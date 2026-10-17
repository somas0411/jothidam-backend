"""
notify.py — booking e-mails, sent from a database outbox by a background thread.

Why an outbox: gunicorn runs one worker (gunicorn.conf.py). A booking writes
its messages to the outbox table in the same transaction as the booking
itself, so a message cannot be lost if the server restarts before sending,
and the HTTP answer never waits for an e-mail provider. A daemon thread in
the worker sends what is due, makes up to 3 attempts (retrying after 1 and then 4
minutes) and records the outcome per recipient in
bookings.notification_status. No Redis or Celery is needed. Rows are claimed
with SELECT ... FOR UPDATE SKIP LOCKED, so it stays correct if more workers
are ever added.

E-mail providers (first one configured wins):
  BREVO_API_KEY                          Brevo transactional API (free tier: 300 e-mails a day)
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD    any SMTP server
  neither                                the message is logged (masked) and marked "logged": local development
EMAIL_FROM is the sender, e.g. "HoroscopeGen <bookings@horoscopegen.in>".

WhatsApp is not sent by the server. The confirmation page gives the user
wa.me buttons (to the astrologer, and to themselves) with whatsapp_summary()
prefilled; see SETUP_BOOKINGS.md for adding the WhatsApp Business Cloud API later.

The same thread wipes personal data RETENTION_DAYS after an appointment.
"""
import base64
import logging
import os
import smtplib
import threading
from datetime import timedelta
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

import requests
from sqlalchemy import and_, insert, select, update

import booking_core as C
import booking_db as D

log = logging.getLogger('horoscopegen.notify')

MAX_ATTEMPTS = 3
BATCH = 10
# The worker does not poll: it touches the database only when woken by a
# booking or cancellation, when a retry falls due, and once every few hours
# for the retention purge. This lets a free Neon database pause when idle
# (Neon counts compute-hours while it is awake).
IDLE_SECONDS = 6 * 3600
MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024

_render_pdf = None
_manage_url = None
_wake = threading.Event()
_worker = None


def configure(render_pdf, booking_view_fn=None, manage_url_fn=None):
    global _render_pdf, _manage_url
    _render_pdf = render_pdf
    _manage_url = manage_url_fn


def enqueue(conn, booking_id, event, now):
    """Queue the e-mails of a booking event ('confirmed' or 'cancelled') inside the caller's transaction."""
    for recipient in ('user', 'astrologer'):
        conn.execute(insert(D.outbox).values(booking_id=booking_id, event=event, channel='email',
                                             recipient=recipient, status='pending', attempts=0,
                                             next_attempt_at=now, created_at=now))


def wake():
    _wake.set()


def _status_key(event, recipient):
    return f'{"cancel_" if event == "cancelled" else ""}email_{recipient}'


# ── TEXT ──────────────────────────────────────────────────────────────────────

T = {
    'en': {
        'confirmed_subject': 'Appointment confirmed: {astro} on {when} (Booking #{short})',
        'cancelled_subject': 'Appointment cancelled: {astro} on {when} (Booking #{short})',
        'hello': 'Hello {name},',
        'confirmed_user': 'Your astrology consultation is booked.',
        'confirmed_astro': 'A consultation has been booked with you on HoroscopeGen.',
        'cancelled_user': 'Your consultation has been cancelled. The slot is free again.',
        'cancelled_astro': 'This consultation has been cancelled by {by}. The slot is free again.',
        'booking_id': 'Booking ID', 'astrologer': 'Astrologer', 'when': 'Date and time',
        'client': 'Client', 'email': 'E-mail', 'whatsapp': 'WhatsApp', 'fee': 'Consultation fee',
        'questions': 'Questions',
        'pay_title': 'Payment is made directly to the astrologer (offline).',
        'pay_1': 'Pay the consultation fee of ₹{fee} to the astrologer (UPI or bank transfer) using the contact details shared with you.',
        'pay_2': 'Send the payment screenshot to the astrologer on WhatsApp ({phone}) before your consultation time, quoting Booking ID {id}.',
        'pay_3': 'HoroscopeGen does not collect or hold any payment and is not responsible for payment disputes.',
        'pay_astro': 'Payment screenshot expected from the user before the session. Please confirm receipt to the user.',
        'horoscope': 'The horoscope is attached as a PDF.',
        'horoscope_link': 'Download the horoscope (PDF)',
        'gcal': 'Add to Google Calendar', 'ics': 'A calendar file (.ics) is attached for Apple Calendar and Outlook.',
        'manage': 'View or cancel this booking', 'wa_astro': 'Message the astrologer on WhatsApp',
        'disclaimer': 'Astrology consultations are for guidance and entertainment only, not medical, legal or financial advice.',
        'by_user': 'the client', 'by_admin': 'HoroscopeGen',
    },
    'ta': {
        'confirmed_subject': 'சந்திப்பு உறுதி: {astro}, {when} (முன்பதிவு #{short})',
        'cancelled_subject': 'சந்திப்பு ரத்து: {astro}, {when} (முன்பதிவு #{short})',
        'hello': 'வணக்கம் {name},',
        'confirmed_user': 'உங்கள் ஜோதிட ஆலோசனை முன்பதிவு செய்யப்பட்டது.',
        'cancelled_user': 'உங்கள் ஆலோசனை ரத்து செய்யப்பட்டது. அந்த நேரம் மீண்டும் காலியாக உள்ளது.',
        'booking_id': 'முன்பதிவு எண்', 'astrologer': 'ஜோதிடர்', 'when': 'தேதி மற்றும் நேரம்',
        'fee': 'ஆலோசனைக் கட்டணம்', 'questions': 'கேள்விகள்',
        'pay_title': 'கட்டணம் நேரடியாக ஜோதிடருக்குச் செலுத்தப்படும் (ஆஃப்லைன்).',
        'pay_1': 'ஆலோசனைக் கட்டணம் ₹{fee}-ஐ ஜோதிடருக்கு (UPI அல்லது வங்கிப் பரிமாற்றம்) பகிரப்பட்ட தொடர்பு விவரங்களைப் பயன்படுத்திச் செலுத்துங்கள்.',
        'pay_2': 'கட்டணம் செலுத்திய ஸ்கிரீன்ஷாட்டை உங்கள் ஆலோசனை நேரத்திற்கு முன் ஜோதிடருக்கு WhatsApp-இல் ({phone}) முன்பதிவு எண் {id}-உடன் அனுப்புங்கள்.',
        'pay_3': 'HoroscopeGen எந்தக் கட்டணத்தையும் வசூலிப்பதோ வைத்திருப்பதோ இல்லை; கட்டணச் சர்ச்சைகளுக்குப் பொறுப்பல்ல.',
        'horoscope': 'ஜாதகம் PDF ஆக இணைக்கப்பட்டுள்ளது.',
        'horoscope_link': 'ஜாதகத்தைப் பதிவிறக்கவும் (PDF)',
        'gcal': 'Google Calendar-இல் சேர்க்கவும்',
        'ics': 'Apple Calendar, Outlook-க்கான நாட்காட்டிக் கோப்பு (.ics) இணைக்கப்பட்டுள்ளது.',
        'manage': 'முன்பதிவைப் பார்க்க அல்லது ரத்து செய்ய', 'wa_astro': 'ஜோதிடருக்கு WhatsApp-இல் செய்தி அனுப்புங்கள்',
        'disclaimer': 'ஜோதிட ஆலோசனைகள் வழிகாட்டுதல் மற்றும் பொழுதுபோக்கிற்கு மட்டுமே; மருத்துவ, சட்ட அல்லது நிதி ஆலோசனை அல்ல.',
    },
}


def _t(lang, key, **kw):
    text = T.get(lang, {}).get(key) or T['en'][key]
    return text.format(**kw) if kw else text


def whatsapp_summary(row, astro):
    """The text the user's wa.me buttons prefill: booking, questions and the payment reminder."""
    when = C.ist_label(D.as_utc(row.slot_start_utc))
    lines = [f'🔮 *HoroscopeGen booking {row.id[:8]}*', f'Booking ID: {row.id}', f'Astrologer: {astro.name}',
             f'Time: {when}', f'Client: {row.user_name} ({row.user_whatsapp})', '', '*Questions*']
    lines += [f'{i}. {q}' for i, q in enumerate(row.questions or [], 1)]
    lines += ['', f'Fee: ₹{astro.fee_inr}, paid directly to the astrologer (offline).',
              'I will send the payment screenshot here before the consultation.']
    return '\n'.join(lines)


def _payment_lines(lang, row, astro, recipient):
    if recipient == 'astrologer':
        return [_t('en', 'pay_title'), _t('en', 'pay_astro')]
    return [_t(lang, 'pay_title'), '1. ' + _t(lang, 'pay_1', fee=astro.fee_inr),
            '2. ' + _t(lang, 'pay_2', phone=astro.phone_e164, id=row.id), '3. ' + _t(lang, 'pay_3')]


def build_email(event, recipient, row, astro):
    """
    One e-mail as a dict: to, to_name, reply_to, subject, text, html,
    attachments [(filename, bytes, mime)]. The astrologer's copy is in
    English and carries the client's contact details; the user's copy is in
    the language they booked in.
    """
    lang = row.lang if recipient == 'user' else 'en'
    start, end = D.as_utc(row.slot_start_utc), D.as_utc(row.slot_end_utc)
    when = C.ist_label(start)
    token = C.make_token(row.id)
    manage = _manage_url(row.id, token) if _manage_url else ''
    is_user = recipient == 'user'
    to, to_name = (row.user_email, row.user_name) if is_user else (astro.email, astro.name)
    reply_to = (astro.email, astro.name) if is_user else (row.user_email, row.user_name)
    subject = _t(lang, f'{event}_subject', astro=astro.name, when=when, short=row.id[:8])
    subject = subject.replace('\r', ' ').replace('\n', ' ')[:200]

    if event == 'confirmed':
        lead = _t(lang, 'confirmed_user') if is_user else _t('en', 'confirmed_astro')
    else:
        by = _t('en', 'by_admin' if row.cancelled_by == 'admin' else 'by_user')
        lead = _t(lang, 'cancelled_user') if is_user else _t('en', 'cancelled_astro', by=by)

    facts = [(_t(lang, 'booking_id'), row.id), (_t(lang, 'astrologer'), f'{astro.name} ({astro.phone_e164})'),
             (_t(lang, 'when'), f'{when} – {end.astimezone(C.IST):%H:%M} IST'),
             (_t(lang, 'fee'), f'₹{astro.fee_inr}')]
    if not is_user:
        facts[1:1] = [(_t('en', 'client'), row.user_name), (_t('en', 'email'), row.user_email),
                      (_t('en', 'whatsapp'), row.user_whatsapp)]
    questions = list(row.questions or [])
    pay = _payment_lines(lang, row, astro, recipient) if event == 'confirmed' else []
    gcal = C.google_calendar_link(row.id, astro.name, astro.fee_inr, astro.phone_e164, start, end,
                                  manage if is_user else None)
    wa_astro = C.wa_link(astro.phone_e164, whatsapp_summary(row, astro))

    attachments = []
    pdf_note = ''
    if event == 'confirmed' and not row.purged_at and _render_pdf:
        pdf = _render_pdf(row.horoscope_input, row.lang)
        if len(pdf) <= MAX_ATTACHMENT_BYTES:
            attachments.append((f'Horoscope_{row.id[:8]}.pdf', pdf, 'application/pdf'))
            pdf_note = _t(lang, 'horoscope')
    attachments.append((f'Consultation_{row.id[:8]}.ics',
                        C.ics(row.id, astro.name, astro.fee_inr, astro.phone_e164, start, end, D.utcnow(),
                              cancelled=event == 'cancelled', cancel_url=manage if is_user else None),
                        'text/calendar'))

    # Plain text
    text = [_t(lang, 'hello', name=to_name), '', lead, '']
    text += [f'{k}: {v}' for k, v in facts]
    if questions and (event == 'confirmed' or not is_user):
        text += ['', _t(lang, 'questions') + ':'] + [f'{i}. {q}' for i, q in enumerate(questions, 1)]
    if pay:
        text += [''] + pay
    if event == 'confirmed':
        text += ['', pdf_note or (f'{_t(lang, "horoscope_link")}: ' + manage if is_user else ''),
                 f'{_t(lang, "gcal")}: {gcal}', _t(lang, 'ics')]
        if is_user:
            text += [f'{_t(lang, "wa_astro")}: {wa_astro}']
    if is_user:
        text += [f'{_t(lang, "manage")}: {manage}']
    text += ['', _t(lang, 'disclaimer'), '', 'HoroscopeGen · horoscopegen.in']

    # HTML: every piece of user text is escaped.
    e = C.esc
    rows = ''.join(f'<tr><td style="padding:4px 12px 4px 0;color:#7a5a20">{e(k)}</td>'
                   f'<td style="padding:4px 0"><b>{e(v)}</b></td></tr>' for k, v in facts)
    qs = ''
    if questions and (event == 'confirmed' or not is_user):
        qs = (f'<h3 style="margin:20px 0 6px">{e(_t(lang, "questions"))}</h3><ol>'
              + ''.join(f'<li style="margin:0 0 8px;white-space:pre-wrap">{e(q)}</li>' for q in questions)
              + '</ol>')
    pay_html = ''
    if pay:
        pay_html = ('<div style="background:#fff6e5;border:1px solid #e8b860;border-radius:8px;padding:12px 16px;'
                    f'margin:18px 0"><b>{e(pay[0])}</b><br>' + '<br>'.join(e(p) for p in pay[1:]) + '</div>')
    button = ('<a href="{href}" style="display:inline-block;background:#B86010;color:#fff;text-decoration:none;'
              'padding:10px 16px;border-radius:8px;margin:4px 8px 4px 0">{label}</a>')
    buttons = ''
    if event == 'confirmed':
        buttons += button.format(href=e(gcal), label=e(_t(lang, 'gcal')))
        if is_user:
            buttons += button.format(href=e(wa_astro), label=e(_t(lang, 'wa_astro')))
    if is_user:
        buttons += button.format(href=e(manage), label=e(_t(lang, 'manage')))
    notes = ' '.join(e(n) for n in (pdf_note, _t(lang, 'ics') if event == 'confirmed' else '') if n)
    html = (f'<div style="font-family:Arial,sans-serif;max-width:600px;color:#2a1600;line-height:1.5">'
            f'<h2 style="color:#B86010;margin:0 0 12px">HoroscopeGen</h2>'
            f'<p>{e(_t(lang, "hello", name=to_name))}</p><p>{e(lead)}</p>'
            f'<table style="border-collapse:collapse">{rows}</table>{qs}{pay_html}'
            f'<p>{buttons}</p><p style="color:#7a5a20;font-size:13px">{notes}</p>'
            f'<p style="color:#7a5a20;font-size:12px">{e(_t(lang, "disclaimer"))}</p></div>')
    return {'to': to, 'to_name': to_name, 'reply_to': reply_to, 'subject': subject,
            'text': '\n'.join(text), 'html': html, 'attachments': attachments}


# ── SENDING ───────────────────────────────────────────────────────────────────

def _sender():
    name, addr = parseaddr(os.environ.get('EMAIL_FROM', 'HoroscopeGen <bookings@horoscopegen.in>'))
    return name or 'HoroscopeGen', addr


def send_email(msg):
    """Send one message. Returns 'sent' or 'logged'; raises on a provider error."""
    name, addr = _sender()
    if os.environ.get('BREVO_API_KEY'):
        body = {'sender': {'name': name, 'email': addr}, 'to': [{'email': msg['to'], 'name': msg['to_name']}],
                'replyTo': {'email': msg['reply_to'][0], 'name': msg['reply_to'][1]},
                'subject': msg['subject'], 'htmlContent': msg['html'], 'textContent': msg['text'],
                'attachment': [{'name': f, 'content': base64.b64encode(b).decode()}
                               for f, b, _ in msg['attachments']]}
        r = requests.post('https://api.brevo.com/v3/smtp/email', json=body, timeout=30,
                          headers={'api-key': os.environ['BREVO_API_KEY'], 'accept': 'application/json'})
        if r.status_code >= 300:
            raise RuntimeError(f'Brevo answered {r.status_code}')
        return 'sent'
    if os.environ.get('SMTP_HOST'):
        em = EmailMessage()
        em['From'] = formataddr((name, addr))
        em['To'] = formataddr((msg['to_name'], msg['to']))
        em['Reply-To'] = formataddr((msg['reply_to'][1], msg['reply_to'][0]))
        em['Subject'] = msg['subject']
        em.set_content(msg['text'])
        em.add_alternative(msg['html'], subtype='html')
        for filename, data, mime in msg['attachments']:
            main, sub = mime.split('/', 1)
            em.add_attachment(data, maintype=main, subtype=sub, filename=filename)
        port = int(os.environ.get('SMTP_PORT', 587))
        cls = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
        with cls(os.environ['SMTP_HOST'], port, timeout=30) as s:
            if port != 465:
                s.starttls()
            if os.environ.get('SMTP_USER'):
                s.login(os.environ['SMTP_USER'], os.environ.get('SMTP_PASSWORD', ''))
            s.send_message(em)
        return 'sent'
    log.info('E-mail not sent (no provider configured): to %s, subject %r, %d attachment(s)',
             C.mask_email(msg['to']), msg['subject'], len(msg['attachments']))
    return 'logged'


def _set_status(conn, booking_id, key, value):
    row = conn.execute(select(D.bookings.c.notification_status).where(D.bookings.c.id == booking_id)
                       .with_for_update()).first()
    if row is None:
        return
    status = dict(row.notification_status or {})
    status[key] = value
    conn.execute(update(D.bookings).where(D.bookings.c.id == booking_id).values(notification_status=status))


def process_outbox_once(now=None, send=None):
    """Send what is due. Returns the number of messages handled. send defaults to send_email (tests pass a fake)."""
    send = send or send_email
    now = now or D.utcnow()
    eng = D.engine()
    with eng.begin() as conn:
        due = conn.execute(select(D.outbox).where(and_(D.outbox.c.status == 'pending',
                                                       D.outbox.c.next_attempt_at <= now))
                           .order_by(D.outbox.c.id).limit(BATCH).with_for_update(skip_locked=True)).all()
        # Claim them for five minutes, so a crash mid-send leads to a retry rather than a loss.
        for item in due:
            conn.execute(update(D.outbox).where(D.outbox.c.id == item.id).values(
                attempts=item.attempts + 1, next_attempt_at=now + timedelta(minutes=5)))
    for item in due:
        attempt = item.attempts + 1
        key = _status_key(item.event, item.recipient)
        try:
            with eng.connect() as conn:
                row = conn.execute(select(D.bookings).where(D.bookings.c.id == item.booking_id)).first()
                astro = conn.execute(select(D.astrologers).where(D.astrologers.c.id == row.astrologer_id)).first()
            if row.purged_at:
                outcome = 'skipped'
            else:
                outcome = send(build_email(item.event, item.recipient, row, astro))
            with eng.begin() as conn:
                conn.execute(update(D.outbox).where(D.outbox.c.id == item.id).values(
                    status='sent' if outcome != 'skipped' else 'skipped', sent_at=D.utcnow(), last_error=None))
                _set_status(conn, item.booking_id, key, outcome)
        except Exception as e:
            log.warning('E-mail %s for booking %s failed (attempt %d): %s', key, item.booking_id, attempt,
                        type(e).__name__)
            final = attempt >= MAX_ATTEMPTS
            with eng.begin() as conn:
                conn.execute(update(D.outbox).where(D.outbox.c.id == item.id).values(
                    status='failed' if final else 'pending', last_error=f'{type(e).__name__}: {e}'[:300],
                    next_attempt_at=now + timedelta(minutes=4 ** (attempt - 1))))
                _set_status(conn, item.booking_id, key, 'failed' if final else 'retrying')
    return len(due)


def purge_personal_data(now=None):
    """
    Wipe the user's personal data from bookings whose appointment ended more
    than RETENTION_DAYS ago. The row stays (with no personal data) so the
    slot history is kept. Returns the number of bookings wiped.
    """
    now = now or D.utcnow()
    cutoff = now - timedelta(days=C.retention_days())
    with D.engine().begin() as conn:
        result = conn.execute(update(D.bookings).where(and_(D.bookings.c.slot_end_utc < cutoff,
                                                            D.bookings.c.purged_at.is_(None))).values(
            user_name='[deleted]', user_email='deleted@invalid', user_whatsapp='+0', questions=[],
            horoscope_input={}, idempotency_key=None, purged_at=now))
        count = result.rowcount or 0
    if count:
        log.info('Wiped personal data from %d past booking(s)', count)
    return count


def forget_booking(booking_id, now=None):
    """Wipe one booking's personal data now (a deletion request). Cancels it first if still upcoming."""
    now = now or D.utcnow()
    with D.engine().begin() as conn:
        result = conn.execute(update(D.bookings).where(D.bookings.c.id == booking_id).values(
            user_name='[deleted]', user_email='deleted@invalid', user_whatsapp='+0', questions=[],
            horoscope_input={}, idempotency_key=None, purged_at=now))
        conn.execute(update(D.bookings).where(and_(D.bookings.c.id == booking_id, D.bookings.c.status == 'confirmed',
                                                   D.bookings.c.slot_start_utc > now))
                     .values(status='cancelled', cancelled_at=now, cancelled_by='admin'))
        conn.execute(update(D.outbox).where(and_(D.outbox.c.booking_id == booking_id, D.outbox.c.status == 'pending'))
                     .values(status='skipped'))
    return bool(result.rowcount)


def next_due(now=None):
    """Seconds until the earliest pending message is due (0 if one is due now), or None if none is waiting."""
    now = now or D.utcnow()
    with D.engine().connect() as conn:
        due = conn.execute(select(D.outbox.c.next_attempt_at).where(D.outbox.c.status == 'pending')
                           .order_by(D.outbox.c.next_attempt_at).limit(1)).scalar()
    if due is None:
        return None
    return max((D.as_utc(due) - now).total_seconds(), 0)


def _loop():
    last_purge = None
    while True:
        wait = IDLE_SECONDS
        try:
            while process_outbox_once():
                pass
            now = D.utcnow()
            if last_purge is None or (now - last_purge).total_seconds() >= IDLE_SECONDS:
                purge_personal_data(now)
                last_purge = now
            pending = next_due(now)
            if pending is not None:
                wait = min(wait, pending + 1)
        except Exception:
            log.exception('Notification worker error')
            wait = 60
        _wake.wait(wait)
        _wake.clear()


def start_worker():
    """Start the background sender once per process."""
    global _worker
    if _worker and _worker.is_alive():
        return
    _worker = threading.Thread(target=_loop, name='booking-notify', daemon=True)
    _worker.start()
