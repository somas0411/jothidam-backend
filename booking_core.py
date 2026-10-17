"""
booking_core.py — the rules of astrologer consultations, with no web or database code.

  slots        30-minute slots from 09:00 to 20:00 IST: 22 a day, the last one 19:30-20:00
  validation   every field of a booking request is checked here, on the server
  calendar     the .ics file and the Google Calendar link of a booking
  tokens       the secret link that lets the user see or cancel a booking
  masking      phone numbers and e-mail addresses as they may appear in logs

Times are aware datetimes. IST is applied with zoneinfo, never by adding 5:30.
"""
import hashlib
import hmac
import html
import os
import re
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')
UTC = timezone.utc

SLOT_MINUTES = 30
DAY_START_MIN = 9 * 60          # first slot starts at 09:00 IST
DAY_END_MIN = 20 * 60           # last slot ends at 20:00 IST
SLOTS_PER_DAY = (DAY_END_MIN - DAY_START_MIN) // SLOT_MINUTES    # 22

MAX_QUESTIONS = 5
MAX_QUESTION_CHARS = 500
LANGS = ('en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn')


def _env_int(name, default, low, high):
    try:
        value = int(os.environ.get(name, default))
    except ValueError:
        return default
    return min(max(value, low), high)


def lead_hours():
    """How far ahead of now the earliest bookable slot must start (BOOKING_LEAD_HOURS, default 2)."""
    return _env_int('BOOKING_LEAD_HOURS', 2, 0, 72)


def window_days():
    """How many days ahead a slot may be booked (BOOKING_WINDOW_DAYS, default 30)."""
    return _env_int('BOOKING_WINDOW_DAYS', 30, 1, 365)


def retention_days():
    """Days after the appointment when the user's personal data is wiped (RETENTION_DAYS, default 90)."""
    return _env_int('RETENTION_DAYS', 90, 1, 3650)


class ValidationError(Exception):
    """Bad booking input. fields maps a field name to a message for the form."""

    def __init__(self, message, fields=None):
        super().__init__(message)
        self.fields = fields or {}


# ── SLOTS ─────────────────────────────────────────────────────────────────────

def today_ist(now):
    return now.astimezone(IST).date()


def slot_starts(day):
    """The 22 slot starts of an IST calendar date, as aware IST datetimes."""
    midnight = datetime.combine(day, time(0, 0), tzinfo=IST)
    return [midnight + timedelta(minutes=DAY_START_MIN + i * SLOT_MINUTES) for i in range(SLOTS_PER_DAY)]


def is_slot_start(start):
    """True when an aware datetime falls exactly on one of the 22 slot starts of its IST date."""
    local = start.astimezone(IST)
    minutes = local.hour * 60 + local.minute
    return (local.second == 0 and local.microsecond == 0 and DAY_START_MIN <= minutes < DAY_END_MIN
            and (minutes - DAY_START_MIN) % SLOT_MINUTES == 0)


def bookable_dates(now):
    """First and last IST date that may be booked."""
    first = today_ist(now)
    return first, first + timedelta(days=window_days())


def earliest_start(now):
    return now + timedelta(hours=lead_hours())


def _available_by_hours(start_ist, hours):
    """hours: (weekday, start_min, end_min) rows. No rows at all means available all day."""
    if not hours:
        return True
    minutes = start_ist.hour * 60 + start_ist.minute
    return any(w == start_ist.weekday() and s <= minutes and minutes + SLOT_MINUTES <= e for w, s, e in hours)


def _in_block(start, end, blocks):
    return any(b_start < end and start < b_end for b_start, b_end in blocks)


def slot_status(start, now, booked, hours, blocks):
    """
    One slot's state: 'past' (before now plus the lead time), 'booked' (a
    confirmed booking holds it), 'blocked' (outside the astrologer's hours or
    inside a blocked range) or 'available'. start is an aware datetime; booked
    is a set of booked UTC starts.
    """
    end = start + timedelta(minutes=SLOT_MINUTES)
    if start < earliest_start(now):
        return 'past'
    if start.astimezone(UTC) in booked:
        return 'booked'
    if not _available_by_hours(start.astimezone(IST), hours) or _in_block(start, end, blocks):
        return 'blocked'
    return 'available'


def day_slots(day, now, booked=(), hours=(), blocks=()):
    """The 22 slots of an IST date with their state, as JSON-ready dicts."""
    booked = {b.astimezone(UTC) for b in booked}
    out = []
    for start in slot_starts(day):
        end = start + timedelta(minutes=SLOT_MINUTES)
        out.append({'start': start.strftime('%H:%M'), 'end': end.strftime('%H:%M'),
                    'start_utc': iso_utc(start), 'end_utc': iso_utc(end),
                    'status': slot_status(start, now, booked, hours, blocks)})
    return out


def iso_utc(dt):
    return dt.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_day(value):
    try:
        return date.fromisoformat(str(value or '').strip())
    except ValueError:
        raise ValidationError('The date must be given as YYYY-MM-DD.', {'date': 'invalid'})


def parse_slot(value):
    """
    A slot start sent by the page: an ISO time with an offset or Z, or a time
    with no offset, which is read as IST ("2026-10-20T09:30").
    """
    text_value = str(value or '').strip()
    if text_value.endswith('Z'):
        text_value = text_value[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text_value)
    except ValueError:
        raise ValidationError('Please pick a time slot.', {'slot_start': 'invalid'})
    return dt.replace(tzinfo=IST) if dt.tzinfo is None else dt


def check_slot(start, now):
    """Raise ValidationError unless start is a real slot inside the booking window and not too soon."""
    if not is_slot_start(start):
        raise ValidationError('Slots start every 30 minutes from 09:00 to 19:30 IST.', {'slot_start': 'grid'})
    first, last = bookable_dates(now)
    day = start.astimezone(IST).date()
    if day < first or start < earliest_start(now):
        raise ValidationError('That time has passed or is too soon to book. Please pick a later slot.',
                              {'slot_start': 'past'})
    if day > last:
        raise ValidationError(f'Slots can be booked up to {window_days()} days ahead.', {'slot_start': 'window'})


# ── VALIDATION ────────────────────────────────────────────────────────────────

_TAG = re.compile(r'<[^>]*>')
_EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
                    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
_E164 = re.compile(r'^\+[1-9]\d{7,14}$')
_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_TIME = re.compile(r'^\d{2}:\d{2}(:\d{2})?$')


def clean_text(value, multiline=False):
    """
    User text as it may be stored and shown: Unicode-normalised, HTML tags and
    control characters removed (line breaks kept when multiline), spaces
    collapsed. Tamil, Devanagari and emoji pass through unchanged.
    """
    s = unicodedata.normalize('NFC', str(value or ''))
    s = _TAG.sub('', s)
    keep = '\n' if multiline else ''
    s = ''.join(ch for ch in s if ch in keep or unicodedata.category(ch)[0] != 'C' or ch in '\u200c\u200d')
    if multiline:
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in s.replace('\r', '').split('\n')]
        return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()
    return re.sub(r'\s+', ' ', s).strip()


def clean_email(value):
    s = str(value or '').strip()
    if '\r' in s or '\n' in s or len(s) > 254 or not _EMAIL.match(s):
        return None
    return s.lower()


def clean_phone(value):
    """An E.164 number such as +919876543210, or None. Spaces, dashes and brackets are ignored."""
    s = re.sub(r'[\s\-().]', '', str(value or ''))
    return s if _E164.match(s) else None


def _flag(body, key):
    return body.get(key) is True or str(body.get(key, '')).strip().lower() in ('true', '1', 'yes', 'on')


BIRTH_KEYS = ('name', 'dob', 'tob', 'pob', 'lat', 'lon', 'tz', 'utcOffset', 'gender',
              'ayanamsha', 'node', 'chartStyle')


def clean_birth(birth):
    """The birth details kept with a booking: only the keys the horoscope needs."""
    if not isinstance(birth, dict):
        raise ValidationError('Birth details are required for the horoscope.', {'birth': 'required'})
    out = {}
    for key in BIRTH_KEYS:
        value = birth.get(key)
        if value in (None, ''):
            continue
        if key in ('lat', 'lon', 'utcOffset'):
            try:
                value = float(value)
            except (TypeError, ValueError):
                raise ValidationError('The birth place coordinates are not valid.', {'birth': 'coordinates'})
        else:
            value = clean_text(value)[:120]
        out[key] = value
    missing = [k for k in ('name', 'dob', 'tob', 'pob', 'lat', 'lon') if k not in out]
    if missing:
        raise ValidationError('Name, date, time and place of birth (searched on the map) are required.',
                              {'birth': 'missing:' + ','.join(missing)})
    if not _DATE.match(out['dob']) or not _TIME.match(out['tob']):
        raise ValidationError('Date of birth must be YYYY-MM-DD and time HH:MM.', {'birth': 'format'})
    if not (-90 <= out['lat'] <= 90 and -180 <= out['lon'] <= 180):
        raise ValidationError('The birth place coordinates are not valid.', {'birth': 'coordinates'})
    return out


def validate_booking(body, now):
    """
    Check a POST /api/bookings body. Returns the cleaned values; raises
    ValidationError naming every bad field. The honeypot field "website" must
    be empty: a person never sees it, a form-filling bot fills it in.
    """
    if str(body.get('website', '')).strip():
        raise ValidationError('The booking could not be accepted.', {'website': 'bot'})
    fields = {}
    out = {}
    try:
        out['astrologer_id'] = int(body.get('astrologer_id'))
    except (TypeError, ValueError):
        fields['astrologer_id'] = 'required'

    try:
        start = parse_slot(body.get('slot_start'))
        check_slot(start, now)
        out['slot_start'] = start.astimezone(UTC)
    except ValidationError as e:
        fields.update(e.fields)
        out['slot_message'] = str(e)

    name = clean_text(body.get('name'))
    if not 2 <= len(name) <= 80:
        fields['name'] = 'Please enter your name (2 to 80 characters).'
    out['name'] = name[:80]

    email = clean_email(body.get('email'))
    if not email:
        fields['email'] = 'Please enter a valid e-mail address.'
    out['email'] = email

    phone = clean_phone(body.get('whatsapp'))
    if not phone:
        fields['whatsapp'] = 'Please enter a WhatsApp number with its country code, e.g. +91 98765 43210.'
    out['whatsapp'] = phone

    raw = body.get('questions')
    if not isinstance(raw, list) or len(raw) > MAX_QUESTIONS:
        fields['questions'] = f'Up to {MAX_QUESTIONS} questions.'
        raw = []
    questions = [clean_text(q, multiline=True) for q in raw]
    if any(len(q) > MAX_QUESTION_CHARS for q in questions):
        fields['questions'] = f'Each question may be up to {MAX_QUESTION_CHARS} characters.'
    if not questions or not questions[0]:
        fields['questions'] = 'Please write at least your first question.'
    out['questions'] = [q for q in questions if q]

    try:
        out['birth'] = clean_birth(body.get('birth'))
    except ValidationError as e:
        fields.update(e.fields)
        out['birth_message'] = str(e)

    lang = str(body.get('lang') or 'en').strip()
    out['lang'] = lang if lang in LANGS else 'en'

    for key in ('consent_share', 'consent_messages', 'adult'):
        if not _flag(body, key):
            fields[key] = 'required'

    key = str(body.get('idempotency_key') or '').strip()
    out['idempotency_key'] = key if re.fullmatch(r'[A-Za-z0-9_-]{16,64}', key) else None

    if fields:
        first = out.get('slot_message') if 'slot_start' in fields else None
        first = first or out.get('birth_message') if 'birth' in fields else first
        raise ValidationError(first or 'Please correct the highlighted fields.', fields)
    return out


# ── TOKENS ────────────────────────────────────────────────────────────────────

def _secret():
    secret = os.environ.get('BOOKING_SECRET', '')
    if not secret:
        global _DEV_SECRET
        if not _DEV_SECRET:
            _DEV_SECRET = os.urandom(32).hex()
        secret = _DEV_SECRET
    return secret.encode()


_DEV_SECRET = ''


def make_token(booking_id):
    """
    The user's secret for a booking, sent only to them. It is derived from
    BOOKING_SECRET, so a repeated request with the same idempotency key can be
    given the same token again; the database keeps only its SHA-256 hash.
    """
    return hmac.new(_secret(), f'booking:{booking_id}'.encode(), hashlib.sha256).hexdigest()[:40]


def hash_token(token):
    return hashlib.sha256(str(token or '').encode()).hexdigest()


def token_matches(token, stored_hash):
    return bool(token) and hmac.compare_digest(hash_token(token), stored_hash or '')


# ── CALENDAR ──────────────────────────────────────────────────────────────────

def ist_label(dt):
    """'Tue, 20 Oct 2026, 09:30 IST'"""
    return dt.astimezone(IST).strftime('%a, %d %b %Y, %H:%M IST')


def _gcal_stamp(dt):
    return dt.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')


def event_title(astrologer_name):
    return f'Astrology consultation with {astrologer_name}'


def event_details(booking_id, astrologer_name, fee, phone, cancel_url=None):
    lines = [f'Booking ID: {booking_id}', f'Astrologer: {astrologer_name} ({phone})',
             f'Fee: ₹{fee}, paid directly to the astrologer (offline).',
             'Send the payment screenshot to the astrologer on WhatsApp before the consultation.']
    if cancel_url:
        lines.append(f'Manage or cancel: {cancel_url}')
    return '\n'.join(lines)


def google_calendar_link(booking_id, astrologer_name, fee, phone, start, end, cancel_url=None):
    params = {
        'action': 'TEMPLATE',
        'text': event_title(astrologer_name),
        'dates': f'{_gcal_stamp(start)}/{_gcal_stamp(end)}',
        'details': event_details(booking_id, astrologer_name, fee, phone, cancel_url),
        'location': f'Phone / WhatsApp {phone}',
        'ctz': 'Asia/Kolkata',
    }
    return 'https://calendar.google.com/calendar/render?' + urlencode(params, quote_via=quote)


def _ics_escape(s):
    return str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def _fold(line):
    """RFC 5545: lines longer than 75 octets continue on the next line after a space."""
    raw = line.encode('utf-8')
    if len(raw) <= 75:
        return line
    parts, current = [], b''
    for ch in line:
        b = ch.encode('utf-8')
        if len(current) + len(b) > (75 if not parts else 74):
            parts.append(current.decode('utf-8'))
            current = b''
        current += b
    parts.append(current.decode('utf-8'))
    return '\r\n '.join(parts)


def ics(booking_id, astrologer_name, fee, phone, start, end, now, cancelled=False, cancel_url=None):
    """An iCalendar file (bytes) with reminders 1 day and 30 minutes before. Times are UTC."""
    lines = [
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//HoroscopeGen//Astrologer Booking//EN',
        'CALSCALE:GREGORIAN', f'METHOD:{"CANCEL" if cancelled else "PUBLISH"}',
        'BEGIN:VEVENT',
        f'UID:{booking_id}@horoscopegen.in',
        f'DTSTAMP:{_gcal_stamp(now)}',
        f'DTSTART:{_gcal_stamp(start)}',
        f'DTEND:{_gcal_stamp(end)}',
        f'SUMMARY:{_ics_escape(event_title(astrologer_name))}',
        f'DESCRIPTION:{_ics_escape(event_details(booking_id, astrologer_name, fee, phone, cancel_url))}',
        f'LOCATION:{_ics_escape("Phone / WhatsApp " + phone)}',
        f'STATUS:{"CANCELLED" if cancelled else "CONFIRMED"}',
        'SEQUENCE:1' if cancelled else 'SEQUENCE:0',
    ]
    if not cancelled:
        for trigger, label in (('-P1D', 'tomorrow'), ('-PT30M', 'in 30 minutes')):
            lines += ['BEGIN:VALARM', 'ACTION:DISPLAY', f'TRIGGER:{trigger}',
                      f'DESCRIPTION:{_ics_escape("Astrology consultation " + label)}', 'END:VALARM']
    lines += ['END:VEVENT', 'END:VCALENDAR']
    return ('\r\n'.join(_fold(line) for line in lines) + '\r\n').encode('utf-8')


# ── WHATSAPP (click-to-chat) ──────────────────────────────────────────────────

def wa_link(phone, message):
    """A wa.me link that opens WhatsApp with the message ready to send (the user presses Send)."""
    digits = re.sub(r'\D', '', phone or '')
    return f'https://wa.me/{digits}?text={quote(message)}'


# ── MASKING ───────────────────────────────────────────────────────────────────

def mask_email(email):
    if not email or '@' not in email:
        return '***'
    user, domain = email.split('@', 1)
    return f'{user[:1]}***@{domain}'


def mask_phone(phone):
    phone = str(phone or '')
    return phone[:3] + '*' * max(len(phone) - 5, 0) + phone[-2:] if len(phone) > 5 else '***'


def esc(s):
    """HTML-escape user text for e-mails."""
    return html.escape(str(s or ''), quote=True)
