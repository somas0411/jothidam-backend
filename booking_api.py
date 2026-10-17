"""
booking_api.py — routes for astrologer consultations, registered on the app by app.py.

Public
  GET  /api/astrologers                       active astrologers (id, name, age, phone, fee)
  GET  /api/astrologers/<id>                  one active astrologer
  GET  /api/astrologers/<id>/slots?date=      the 22 slots of an IST date and their state
  POST /api/bookings                          book a slot (201; 409 when the slot was just taken)
  GET  /api/bookings/<id>?token=              the booking, for the confirmation page
  POST /api/bookings/<id>/cancel              {"token"}: cancel and free the slot
  GET  /api/bookings/<id>/ics?token=          calendar file
  GET  /api/bookings/<id>/pdf?token=          the horoscope PDF made from the stored birth details

Admin (header X-Admin-Key: the ADMIN_API_KEY environment variable)
  GET  /api/admin/astrologers                 every astrologer, with weekly hours and blocked ranges
  POST /api/admin/astrologers                 add one
  PUT  /api/admin/astrologers/<id>            edit one (weekly hours are replaced when sent)
  POST /api/admin/astrologers/<id>/blocks     block whole IST dates (leave)
  DELETE /api/admin/blocks/<id>               remove a blocked range
  GET  /api/admin/bookings?days=              bookings from today on
  POST /api/admin/bookings/<id>/cancel        cancel for the user

Errors leave as {"error": "...", "code": "...", "fields": {...}} with 400,
401, 404, 409, 410, 422, 429 or 503. Nothing here keeps state in memory:
correctness comes from database transactions and the unique slot index.
"""
import hmac
import logging
import os
import uuid
from datetime import datetime, time, timedelta

from flask import jsonify, request
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, OperationalError

import booking_core as C
import booking_db as D
import notify

log = logging.getLogger('horoscopegen.booking')

LIMIT_ASTROLOGERS = '60 per minute'
LIMIT_SLOTS = '60 per minute'
LIMIT_BOOKING = '5 per hour'                 # POST /api/bookings, per visitor
LIMIT_BOOKING_READ = '30 per minute'
LIMIT_CANCEL = '10 per hour'
LIMIT_ADMIN = '60 per minute'


def site_url():
    return os.environ.get('SITE_URL', 'https://horoscopegen.in').rstrip('/')


def api_url():
    return os.environ.get('PUBLIC_API_URL', 'https://jothidam-backend.onrender.com').rstrip('/')


def manage_url(booking_id, token):
    return f'{site_url()}/astrologers.html#/booking/{booking_id}?token={token}'


def _err(status, message, code=None, fields=None):
    body = {'error': message}
    if code:
        body['code'] = code
    if fields:
        body['fields'] = fields
    return jsonify(body), status


def _no_store(resp):
    resp.headers['Cache-Control'] = 'no-store'
    return resp


def _json_body():
    body = request.get_json(force=True, silent=True)
    return body if isinstance(body, dict) else None


def _db_guard(fn):
    """503 when no database is set up or it cannot be reached; 422 for bad input."""
    def run(*args, **kwargs):
        if not D.configured():
            return _err(503, 'Astrologer booking is not available yet.', 'not_configured')
        try:
            return fn(*args, **kwargs)
        except C.ValidationError as e:
            return _err(422, str(e), 'invalid', e.fields)
        except OperationalError:
            log.exception('Database unreachable in %s', request.path)
            return _err(503, 'The booking service is busy. Please try again in a minute.', 'db_unavailable')
    run.__name__ = fn.__name__
    return run


# ── READING ───────────────────────────────────────────────────────────────────

def _public_astrologer(row):
    return {'id': row.id, 'name': row.name, 'age': row.age, 'phone': row.phone_e164, 'fee_inr': row.fee_inr,
            'languages': row.languages or '', 'bio': row.bio or ''}


def _hours(conn, astrologer_id):
    rows = conn.execute(select(D.availability).where(D.availability.c.astrologer_id == astrologer_id))
    return [(r.weekday, r.start_min, r.end_min) for r in rows]


def _blocks(conn, astrologer_id, start, end):
    rows = conn.execute(select(D.availability_blocks).where(and_(
        D.availability_blocks.c.astrologer_id == astrologer_id,
        D.availability_blocks.c.start_utc < end, D.availability_blocks.c.end_utc > start)))
    return [(D.as_utc(r.start_utc), D.as_utc(r.end_utc)) for r in rows]


def _booked(conn, astrologer_id, start, end):
    rows = conn.execute(select(D.bookings.c.slot_start_utc).where(and_(
        D.bookings.c.astrologer_id == astrologer_id, D.bookings.c.status == 'confirmed',
        D.bookings.c.slot_start_utc >= start, D.bookings.c.slot_start_utc < end)))
    return {D.as_utc(r.slot_start_utc) for r in rows}


def _active_astrologer(conn, astrologer_id):
    return conn.execute(select(D.astrologers).where(and_(
        D.astrologers.c.id == astrologer_id, D.astrologers.c.is_active.is_(True)))).first()


@_db_guard
def list_astrologers():
    with D.engine().connect() as conn:
        rows = conn.execute(select(D.astrologers).where(D.astrologers.c.is_active.is_(True))
                            .order_by(D.astrologers.c.name)).all()
    return _no_store(jsonify({'astrologers': [_public_astrologer(r) for r in rows]}))


@_db_guard
def get_astrologer(astrologer_id):
    with D.engine().connect() as conn:
        row = _active_astrologer(conn, astrologer_id)
    if not row:
        return _err(404, 'This astrologer is not taking bookings.', 'astrologer_unavailable')
    first, last = C.bookable_dates(D.utcnow())
    out = _public_astrologer(row)
    out['booking_window'] = {'first': first.isoformat(), 'last': last.isoformat(),
                             'lead_hours': C.lead_hours()}
    return _no_store(jsonify(out))


def _slots_for(conn, astrologer_id, day, now):
    start = datetime.combine(day, time(0, 0), tzinfo=C.IST)
    end = start + timedelta(days=1)
    return C.day_slots(day, now, booked=_booked(conn, astrologer_id, start, end),
                       hours=_hours(conn, astrologer_id), blocks=_blocks(conn, astrologer_id, start, end))


@_db_guard
def get_slots(astrologer_id):
    day = C.parse_day(request.args.get('date'))
    now = D.utcnow()
    first, last = C.bookable_dates(now)
    if not first <= day <= last:
        raise C.ValidationError(f'Pick a date from {first:%d %b} to {last:%d %b %Y}.', {'date': 'window'})
    with D.engine().connect() as conn:
        if not _active_astrologer(conn, astrologer_id):
            return _err(404, 'This astrologer is not taking bookings.', 'astrologer_unavailable')
        slots = _slots_for(conn, astrologer_id, day, now)
    return _no_store(jsonify({'date': day.isoformat(), 'timezone': 'Asia/Kolkata', 'slots': slots,
                              'server_time_utc': C.iso_utc(now)}))


# ── BOOKING ───────────────────────────────────────────────────────────────────

def booking_view(row, astro, token):
    """What the confirmation page shows. Only for the holder of the booking's token."""
    start, end = D.as_utc(row.slot_start_utc), D.as_utc(row.slot_end_utc)
    manage = manage_url(row.id, token)
    summary = notify.whatsapp_summary(row, astro)
    return {
        'id': row.id, 'status': row.status,
        'astrologer': {'id': astro.id, 'name': astro.name, 'phone': astro.phone_e164, 'fee_inr': astro.fee_inr},
        'slot_start_utc': C.iso_utc(start), 'slot_end_utc': C.iso_utc(end),
        'slot_label_ist': C.ist_label(start), 'date_ist': start.astimezone(C.IST).date().isoformat(),
        'user': {'name': row.user_name, 'email': row.user_email, 'whatsapp': row.user_whatsapp},
        'questions': row.questions, 'lang': row.lang,
        'notification_status': row.notification_status,
        'google_calendar_url': C.google_calendar_link(row.id, astro.name, astro.fee_inr, astro.phone_e164,
                                                      start, end, manage),
        'ics_url': f'{api_url()}/api/bookings/{row.id}/ics?token={token}',
        'pdf_url': f'{api_url()}/api/bookings/{row.id}/pdf?token={token}' if not row.purged_at else None,
        'whatsapp_astrologer_url': C.wa_link(astro.phone_e164, summary),
        'whatsapp_self_url': C.wa_link(row.user_whatsapp, summary),
        'manage_url': manage,
    }


def _existing_by_key(conn, key):
    if not key:
        return None
    return conn.execute(select(D.bookings).where(D.bookings.c.idempotency_key == key)).first()


def make_post_booking(check_birth):
    """check_birth(birth_dict, lang) runs the engine once so a bad birth detail is refused now, not by e-mail."""

    @_db_guard
    def post_booking():
        body = _json_body()
        if body is None:
            return _err(400, 'The request body must be a JSON object.', 'bad_request')
        now = D.utcnow()
        data = C.validate_booking(body, now)
        try:
            check_birth(data['birth'], data['lang'])
        except C.ValidationError:
            raise
        except Exception as e:      # InputError from the engine, or a date it cannot calculate
            raise C.ValidationError(f'Birth details: {e}', {'birth': 'invalid'})

        eng = D.engine()
        with eng.connect() as conn:
            again = _existing_by_key(conn, data['idempotency_key'])
        if again:
            return _repeat(again, data)

        booking_id = str(uuid.uuid4())
        token = C.make_token(booking_id)
        start = data['slot_start']
        end = start + timedelta(minutes=C.SLOT_MINUTES)
        try:
            with eng.begin() as conn:
                astro = _active_astrologer(conn, data['astrologer_id'])
                if not astro:
                    return _err(409, 'This astrologer is no longer taking bookings. Please choose another.',
                                'astrologer_unavailable')
                day_start = datetime.combine(start.astimezone(C.IST).date(), time(0), tzinfo=C.IST)
                status = C.slot_status(start, now, set(), _hours(conn, astro.id),
                                       _blocks(conn, astro.id, day_start, day_start + timedelta(days=1)))
                if status != 'available':
                    return _err(409, 'That slot is not available. Please pick another.', 'slot_unavailable')
                conn.execute(insert(D.bookings).values(
                    id=booking_id, astrologer_id=astro.id, slot_start_utc=start, slot_end_utc=end,
                    status='confirmed', user_name=data['name'], user_email=data['email'],
                    user_whatsapp=data['whatsapp'], questions=data['questions'],
                    horoscope_input=data['birth'], lang=data['lang'], cancel_token_hash=C.hash_token(token),
                    idempotency_key=data['idempotency_key'], consent_share_at=now, consent_messages_at=now,
                    adult_confirmed_at=now, created_at=now,
                    notification_status={'email_user': 'pending', 'email_astrologer': 'pending',
                                         'whatsapp': 'manual'}))
                notify.enqueue(conn, booking_id, 'confirmed', now)
        except IntegrityError:
            with eng.connect() as conn:
                again = _existing_by_key(conn, data['idempotency_key'])
            if again:
                return _repeat(again, data)
            log.info('Slot taken: astrologer %s at %s', data['astrologer_id'], C.iso_utc(start))
            return _err(409, 'Sorry, that slot was just taken. Please pick another.', 'slot_taken')

        notify.wake()
        log.info('Booking %s for astrologer %s at %s (user %s)', booking_id, data['astrologer_id'],
                 C.iso_utc(start), C.mask_email(data['email']))
        with eng.connect() as conn:
            row = conn.execute(select(D.bookings).where(D.bookings.c.id == booking_id)).first()
            astro = conn.execute(select(D.astrologers).where(D.astrologers.c.id == row.astrologer_id)).first()
        out = booking_view(row, astro, token)
        out['token'] = token
        resp = jsonify(out)
        resp.status_code = 201
        return resp

    return post_booking


def _repeat(row, data):
    """The same idempotency key sent again (a retried click): answer with the booking it made."""
    if row.slot_start_utc is None or D.as_utc(row.slot_start_utc) != data['slot_start'] \
            or row.astrologer_id != data['astrologer_id']:
        return _err(409, 'This request was already used for a different booking.', 'idempotency_conflict')
    with D.engine().connect() as conn:
        astro = conn.execute(select(D.astrologers).where(D.astrologers.c.id == row.astrologer_id)).first()
    token = C.make_token(row.id)
    out = booking_view(row, astro, token)
    out['token'] = token
    out['repeated'] = True
    return jsonify(out), 200


def _load_with_token(booking_id, token):
    """(booking, astrologer) when the token fits, else an error response."""
    try:
        uuid.UUID(booking_id)
    except ValueError:
        return None, _err(404, 'Booking not found.', 'not_found')
    with D.engine().connect() as conn:
        row = conn.execute(select(D.bookings).where(D.bookings.c.id == booking_id)).first()
        if not row or not C.token_matches(token, row.cancel_token_hash):
            # The same answer whether the booking is missing or the token is wrong.
            return None, _err(404, 'Booking not found.', 'not_found')
        astro = conn.execute(select(D.astrologers).where(D.astrologers.c.id == row.astrologer_id)).first()
    return (row, astro), None


@_db_guard
def get_booking(booking_id):
    token = request.args.get('token', '')
    found, error = _load_with_token(booking_id, token)
    if error:
        return error
    return _no_store(jsonify(booking_view(*found, token)))


def cancel(booking_id, by):
    """Cancel a confirmed booking and queue the notices. Returns (changed, error message)."""
    now = D.utcnow()
    with D.engine().begin() as conn:
        row = conn.execute(select(D.bookings).where(D.bookings.c.id == booking_id).with_for_update()).first()
        if row.status == 'cancelled':
            return False, None
        if by == 'user' and D.as_utc(row.slot_start_utc) <= now:
            return False, 'This consultation has already started and can no longer be cancelled here.'
        status = dict(row.notification_status or {})
        status.update({'cancel_email_user': 'pending', 'cancel_email_astrologer': 'pending'})
        conn.execute(update(D.bookings).where(D.bookings.c.id == booking_id).values(
            status='cancelled', cancelled_at=now, cancelled_by=by, notification_status=status))
        notify.enqueue(conn, booking_id, 'cancelled', now)
    notify.wake()
    log.info('Booking %s cancelled by %s', booking_id, by)
    return True, None


@_db_guard
def cancel_booking(booking_id):
    body = _json_body() or {}
    token = str(body.get('token') or request.args.get('token') or '')
    found, error = _load_with_token(booking_id, token)
    if error:
        return error
    _, problem = cancel(booking_id, 'user')
    if problem:
        return _err(409, problem, 'too_late')
    found, _ = _load_with_token(booking_id, token)
    return _no_store(jsonify(booking_view(*found, token)))


@_db_guard
def get_ics(booking_id):
    token = request.args.get('token', '')
    found, error = _load_with_token(booking_id, token)
    if error:
        return error
    row, astro = found
    data = C.ics(row.id, astro.name, astro.fee_inr, astro.phone_e164, D.as_utc(row.slot_start_utc),
                 D.as_utc(row.slot_end_utc), D.utcnow(), cancelled=row.status == 'cancelled',
                 cancel_url=manage_url(row.id, token))
    resp = _file(data, f'HoroscopeGen_Booking_{row.id[:8]}.ics', 'text/calendar; charset=utf-8')
    return _no_store(resp)


def make_get_pdf(render_pdf):
    @_db_guard
    def get_pdf(booking_id):
        token = request.args.get('token', '')
        found, error = _load_with_token(booking_id, token)
        if error:
            return error
        row, _ = found
        if row.purged_at:
            return _err(410, 'The birth details of this booking have been deleted.', 'purged')
        data = render_pdf(row.horoscope_input, row.lang)
        return _no_store(_file(data, f'HoroscopeGen_Booking_{row.id[:8]}.pdf', 'application/pdf'))
    return get_pdf


def _file(data, filename, mime):
    from flask import make_response
    resp = make_response(data)
    resp.headers['Content-Type'] = mime
    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


# ── ADMIN ─────────────────────────────────────────────────────────────────────

def _admin(fn):
    """The X-Admin-Key header must equal ADMIN_API_KEY. With no key set, the admin routes are off."""
    def run(*args, **kwargs):
        expected = os.environ.get('ADMIN_API_KEY', '')
        if len(expected) < 16:
            return _err(503, 'The admin API is switched off (ADMIN_API_KEY is not set).', 'admin_off')
        given = request.headers.get('X-Admin-Key', '')
        if not hmac.compare_digest(given.encode(), expected.encode()):
            return _err(401, 'Wrong admin key.', 'unauthorized')
        return fn(*args, **kwargs)
    run.__name__ = fn.__name__
    return run


def _hhmm(value):
    try:
        h, m = str(value).split(':')
        minutes = int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None
    return minutes if 0 <= minutes <= 1440 else None


def _clean_hours(raw):
    """[{"weekday": 0-6, "start": "09:00", "end": "13:00"}] -> rows, on the 30-minute grid inside 09:00-20:00."""
    if not isinstance(raw, list) or len(raw) > 70:
        raise C.ValidationError('Working hours must be a list.', {'hours': 'invalid'})
    out = []
    for item in raw:
        if not isinstance(item, dict):
            raise C.ValidationError('Working hours must be a list.', {'hours': 'invalid'})
        try:
            weekday = int(item.get('weekday'))
        except (TypeError, ValueError):
            weekday = -1
        start, end = _hhmm(item.get('start')), _hhmm(item.get('end'))
        if not 0 <= weekday <= 6 or start is None or end is None or not (
                C.DAY_START_MIN <= start < end <= C.DAY_END_MIN) or start % 30 or end % 30:
            raise C.ValidationError('Each window needs a weekday and a start and end on the half hour '
                                    'between 09:00 and 20:00.', {'hours': 'invalid'})
        out.append((weekday, start, end))
    return out


def _clean_astrologer(body, partial=False):
    out, fields = {}, {}

    def want(key):
        return not partial or key in body

    if want('name'):
        name = C.clean_text(body.get('name'))
        if not 2 <= len(name) <= 80:
            fields['name'] = 'required (2 to 80 characters)'
        out['name'] = name
    if want('age'):
        try:
            out['age'] = int(body.get('age'))
            if not 18 <= out['age'] <= 120:
                raise ValueError
        except (TypeError, ValueError):
            fields['age'] = '18 to 120'
    if want('phone'):
        out['phone_e164'] = C.clean_phone(body.get('phone'))
        if not out['phone_e164']:
            fields['phone'] = 'E.164 with country code, e.g. +919876543210'
    if want('email'):
        out['email'] = C.clean_email(body.get('email'))
        if not out['email']:
            fields['email'] = 'valid e-mail address'
    if want('fee_inr'):
        try:
            out['fee_inr'] = int(body.get('fee_inr'))
            if not 0 <= out['fee_inr'] <= 1000000:
                raise ValueError
        except (TypeError, ValueError):
            fields['fee_inr'] = 'whole rupees, 0 or more'
    if 'is_active' in body or not partial:
        out['is_active'] = body.get('is_active', True) not in (False, 'false', 0, '0')
    for key, size in (('bio', 600), ('languages', 120)):
        if key in body:
            out[key] = C.clean_text(body.get(key), multiline=key == 'bio')[:size] or None
    if fields:
        raise C.ValidationError('Please correct the highlighted fields.', fields)
    return out


def _admin_astrologer(conn, row):
    hours = [{'weekday': w, 'start': f'{s // 60:02d}:{s % 60:02d}', 'end': f'{e // 60:02d}:{e % 60:02d}'}
             for w, s, e in sorted(_hours(conn, row.id))]
    blocks = conn.execute(select(D.availability_blocks).where(and_(
        D.availability_blocks.c.astrologer_id == row.id,
        D.availability_blocks.c.end_utc > D.utcnow())).order_by(D.availability_blocks.c.start_utc)).all()
    return {'id': row.id, 'name': row.name, 'age': row.age, 'phone': row.phone_e164, 'email': row.email,
            'fee_inr': row.fee_inr, 'is_active': row.is_active, 'bio': row.bio or '',
            'languages': row.languages or '', 'hours': hours,
            'blocks': [{'id': b.id, 'from': D.as_utc(b.start_utc).astimezone(C.IST).date().isoformat(),
                        'to': (D.as_utc(b.end_utc).astimezone(C.IST) - timedelta(minutes=1)).date().isoformat(),
                        'reason': b.reason or ''} for b in blocks]}


@_admin
@_db_guard
def admin_list():
    with D.engine().connect() as conn:
        rows = conn.execute(select(D.astrologers).order_by(D.astrologers.c.id)).all()
        return _no_store(jsonify({'astrologers': [_admin_astrologer(conn, r) for r in rows]}))


def _write_hours(conn, astrologer_id, hours):
    conn.execute(delete(D.availability).where(D.availability.c.astrologer_id == astrologer_id))
    for weekday, start, end in hours:
        conn.execute(insert(D.availability).values(astrologer_id=astrologer_id, weekday=weekday,
                                                   start_min=start, end_min=end))


@_admin
@_db_guard
def admin_create():
    body = _json_body() or {}
    values = _clean_astrologer(body)
    hours = _clean_hours(body['hours']) if 'hours' in body else []
    now = D.utcnow()
    with D.engine().begin() as conn:
        new_id = conn.execute(insert(D.astrologers).values(created_at=now, updated_at=now, **values)
                              .returning(D.astrologers.c.id)).scalar_one()
        _write_hours(conn, new_id, hours)
        row = conn.execute(select(D.astrologers).where(D.astrologers.c.id == new_id)).first()
        out = _admin_astrologer(conn, row)
    log.info('Admin added astrologer %s', new_id)
    return jsonify(out), 201


@_admin
@_db_guard
def admin_update(astrologer_id):
    body = _json_body() or {}
    values = _clean_astrologer(body, partial=True)
    hours = _clean_hours(body['hours']) if 'hours' in body else None
    with D.engine().begin() as conn:
        if not conn.execute(select(D.astrologers.c.id).where(D.astrologers.c.id == astrologer_id)).first():
            return _err(404, 'Astrologer not found.', 'not_found')
        if values:
            conn.execute(update(D.astrologers).where(D.astrologers.c.id == astrologer_id)
                         .values(updated_at=D.utcnow(), **values))
        if hours is not None:
            _write_hours(conn, astrologer_id, hours)
        row = conn.execute(select(D.astrologers).where(D.astrologers.c.id == astrologer_id)).first()
        out = _admin_astrologer(conn, row)
    log.info('Admin edited astrologer %s', astrologer_id)
    return jsonify(out)


@_admin
@_db_guard
def admin_add_block(astrologer_id):
    body = _json_body() or {}
    first, last = C.parse_day(body.get('from')), C.parse_day(body.get('to') or body.get('from'))
    if last < first or (last - first).days > 366:
        raise C.ValidationError('"to" must be on or after "from", within a year.', {'to': 'invalid'})
    start = datetime.combine(first, time(0), tzinfo=C.IST)
    end = datetime.combine(last + timedelta(days=1), time(0), tzinfo=C.IST)
    with D.engine().begin() as conn:
        if not conn.execute(select(D.astrologers.c.id).where(D.astrologers.c.id == astrologer_id)).first():
            return _err(404, 'Astrologer not found.', 'not_found')
        conn.execute(insert(D.availability_blocks).values(
            astrologer_id=astrologer_id, start_utc=start.astimezone(C.UTC), end_utc=end.astimezone(C.UTC),
            reason=C.clean_text(body.get('reason'))[:120] or None))
        row = conn.execute(select(D.astrologers).where(D.astrologers.c.id == astrologer_id)).first()
        out = _admin_astrologer(conn, row)
    return jsonify(out), 201


@_admin
@_db_guard
def admin_delete_block(block_id):
    with D.engine().begin() as conn:
        done = conn.execute(delete(D.availability_blocks).where(D.availability_blocks.c.id == block_id)).rowcount
    return (jsonify({'deleted': block_id}), 200) if done else _err(404, 'Not found.', 'not_found')


@_admin
@_db_guard
def admin_bookings():
    try:
        days = min(max(int(request.args.get('days', 30)), 1), 366)
    except ValueError:
        days = 30
    start = datetime.combine(C.today_ist(D.utcnow()), time(0), tzinfo=C.IST)
    with D.engine().connect() as conn:
        rows = conn.execute(select(D.bookings, D.astrologers.c.name.label('astrologer_name'))
                            .join(D.astrologers, D.astrologers.c.id == D.bookings.c.astrologer_id)
                            .where(and_(D.bookings.c.slot_start_utc >= start,
                                        D.bookings.c.slot_start_utc < start + timedelta(days=days)))
                            .order_by(D.bookings.c.slot_start_utc)).all()
    return _no_store(jsonify({'bookings': [{
        'id': r.id, 'status': r.status, 'astrologer_id': r.astrologer_id, 'astrologer_name': r.astrologer_name,
        'slot_label_ist': C.ist_label(D.as_utc(r.slot_start_utc)),
        'slot_start_utc': C.iso_utc(D.as_utc(r.slot_start_utc)),
        'user_name': r.user_name, 'user_email': r.user_email, 'user_whatsapp': r.user_whatsapp,
        'questions': r.questions, 'notification_status': r.notification_status} for r in rows]}))


@_admin
@_db_guard
def admin_cancel(booking_id):
    with D.engine().connect() as conn:
        if not conn.execute(select(D.bookings.c.id).where(D.bookings.c.id == booking_id)).first():
            return _err(404, 'Booking not found.', 'not_found')
    changed, _ = cancel(booking_id, 'admin')
    return jsonify({'id': booking_id, 'status': 'cancelled', 'changed': changed})


# ── REGISTRATION ──────────────────────────────────────────────────────────────

def register(app, limiter, check_birth, render_pdf):
    """Add the booking routes to app, each under its request limit, and start the notification worker."""
    def add(rule, fn, limit, methods=('GET',), endpoint=None):
        app.add_url_rule(rule, endpoint or f'booking_{fn.__name__}', limiter.limit(limit)(fn),
                         methods=list(methods))

    add('/api/astrologers', list_astrologers, LIMIT_ASTROLOGERS)
    add('/api/astrologers/<int:astrologer_id>', get_astrologer, LIMIT_ASTROLOGERS)
    add('/api/astrologers/<int:astrologer_id>/slots', get_slots, LIMIT_SLOTS)
    add('/api/bookings', make_post_booking(check_birth), LIMIT_BOOKING, ('POST',))
    add('/api/bookings/<booking_id>', get_booking, LIMIT_BOOKING_READ)
    add('/api/bookings/<booking_id>/cancel', cancel_booking, LIMIT_CANCEL, ('POST',))
    add('/api/bookings/<booking_id>/ics', get_ics, LIMIT_BOOKING_READ)
    add('/api/bookings/<booking_id>/pdf', make_get_pdf(render_pdf), '10 per minute', endpoint='booking_get_pdf')
    add('/api/admin/astrologers', admin_list, LIMIT_ADMIN)
    add('/api/admin/astrologers', admin_create, LIMIT_ADMIN, ('POST',), 'booking_admin_create')
    add('/api/admin/astrologers/<int:astrologer_id>', admin_update, LIMIT_ADMIN, ('PUT',))
    add('/api/admin/astrologers/<int:astrologer_id>/blocks', admin_add_block, LIMIT_ADMIN, ('POST',))
    add('/api/admin/blocks/<int:block_id>', admin_delete_block, LIMIT_ADMIN, ('DELETE',))
    add('/api/admin/bookings', admin_bookings, LIMIT_ADMIN)
    add('/api/admin/bookings/<booking_id>/cancel', admin_cancel, LIMIT_ADMIN, ('POST',))

    notify.configure(render_pdf, booking_view_fn=booking_view, manage_url_fn=manage_url)
    if D.configured():
        try:
            D.init_db()
        except Exception:
            log.exception('Could not reach the booking database at start; the routes will answer 503 until it is up')
        if os.environ.get('NOTIFY_WORKER', 'true').strip().lower() not in ('0', 'false', 'no', 'off'):
            notify.start_worker()
