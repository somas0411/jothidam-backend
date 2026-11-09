"""
tickets.py — support tickets from support.html.

POST /api/tickets        a new ticket (201 with its number)
GET  /api/admin/tickets?status=     list (X-Admin-Key)
PUT  /api/admin/tickets/<id>        {"status", "admin_note"} (X-Admin-Key)

Required: email, payment reference, payment date, issue type, description.
The payment reference is a Razorpay payment id (pay_ + 14 letters/digits), a
Razorpay order id (order_ + 14), or "NA" when the visitor ticks "not a payment
issue". The payment date may not be in the future or more than 180 days old.
A filled "website" field (hidden from people) marks a bot: the answer looks
like success and nothing is stored.

Without DATABASE_URL the route answers 503 and the page shows the support
e-mail address instead. Personal data is wiped 180 days after a ticket is
closed (purge()).
"""
import logging
import os
import re
import uuid
from datetime import date, timedelta

from flask import jsonify, request
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError, OperationalError

import booking_core as C
import booking_db as D
import pay_i18n

log = logging.getLogger('horoscopegen.tickets')

LIMIT_TICKET = '5 per hour'
LIMIT_ADMIN = '60 per minute'
ISSUES = ('no_report', 'download', 'wrong_details', 'refund', 'language', 'other')
STATUSES = ('open', 'in_progress', 'closed')
PAY_REF = re.compile(r'^(pay|order)_[A-Za-z0-9]{14}$')
MAX_AGE_DAYS = 180
RETENTION_AFTER_CLOSE_DAYS = 180


def support_email():
    return pay_i18n._support_address()


def today_ist():
    return C.today_ist(D.utcnow())


def validate(b):
    """The cleaned ticket, or C.ValidationError with a message per field."""
    errors = {}
    email = C.clean_email(b.get('email'))
    if not email:
        errors['email'] = 'Enter a valid e-mail address.'
    not_payment = bool(b.get('not_payment'))
    ref = re.sub(r'\s+', '', str(b.get('payment_ref') or ''))
    if not_payment:
        ref = 'NA'
    elif not PAY_REF.match(ref):
        errors['payment_ref'] = 'Enter the Razorpay payment id (pay_ followed by 14 letters or digits).'
    raw_date = str(b.get('payment_date') or '').strip()
    try:
        d = date.fromisoformat(raw_date)
        today = today_ist()
        if d > today:
            errors['payment_date'] = 'The date cannot be in the future.'
        elif d < today - timedelta(days=MAX_AGE_DAYS):
            errors['payment_date'] = f'The date cannot be more than {MAX_AGE_DAYS} days ago.'
    except ValueError:
        errors['payment_date'] = 'Enter the date of payment.'
    issue = str(b.get('issue_type') or '')
    if issue not in ISSUES:
        errors['issue_type'] = 'Choose the kind of issue.'
    desc = C.clean_text(b.get('description'), multiline=True)
    if not 20 <= len(desc) <= 2000:
        errors['description'] = 'Describe the issue in 20 to 2000 characters.'
    if not b.get('consent'):
        errors['consent'] = 'Please agree to us using these details to answer your ticket.'
    phone = None
    if b.get('phone'):
        phone = C.clean_phone(b.get('phone'))
        if not phone:
            errors['phone'] = 'Use the form +91 98765 43210, or leave it empty.'
    if errors:
        raise C.ValidationError('Please correct the marked fields.', errors)
    name = C.clean_text(b.get('name'))[:80] or None
    birth = C.clean_text(b.get('birth_details'), multiline=True)[:500] or None
    lang = str(b.get('lang') or 'en')
    return {'email': email, 'payment_ref': ref, 'payment_date': d.isoformat(), 'issue_type': issue,
            'description': desc, 'phone_e164': phone, 'name': name, 'birth_details': birth,
            'lang': lang if lang in pay_i18n.LANGS + ('bi',) else 'en'}


def _err(status, message, code, fields=None):
    body = {'error': message, 'code': code}
    if fields:
        body['fields'] = fields
    return jsonify(body), status


def _guard(fn):
    def run(*args, **kwargs):
        if not D.configured():
            return _err(503, 'Tickets are not available right now. Please e-mail us.', 'not_configured',
                        {'support_email': support_email()})
        try:
            return fn(*args, **kwargs)
        except C.ValidationError as e:
            return _err(422, str(e), 'invalid', e.fields)
        except OperationalError:
            log.exception('Database unreachable in %s', request.path)
            return _err(503, 'Tickets are busy. Please try again in a minute.', 'db_unavailable')
    run.__name__ = fn.__name__
    return run


def _ticket_no(conn, day):
    prefix = f'HG-{day:%Y%m%d}-'
    n = conn.execute(select(func.count()).select_from(D.tickets)
                     .where(D.tickets.c.ticket_no.like(prefix + '%'))).scalar() or 0
    return f'{prefix}{n + 1:04d}'


def _emails(row):
    import booking_api
    import notify
    lang = row['lang']
    no = row['ticket_no']
    user = {'to': row['email'], 'to_name': row['name'] or row['email'], 'reply_to': (support_email(), 'HoroscopeGen'),
            'subject': pay_i18n.T('t.subject', lang).format(no=no),
            'text': pay_i18n.T('t.body', lang).format(no=no),
            'html': f"<p>{pay_i18n.html.escape(pay_i18n.T('t.body', lang).format(no=no))}</p>", 'attachments': []}
    fields = ['ticket_no', 'issue_type', 'email', 'name', 'phone_e164', 'payment_ref', 'payment_date', 'order_id',
              'lang', 'birth_details', 'description']
    text = '\n'.join(f'{k}: {row.get(k) or "-"}' for k in fields) + f'\n\nAdmin: {booking_api.site_url()}/admin'
    admin = {'to': support_email(), 'to_name': 'HoroscopeGen support', 'reply_to': (row['email'], row['name'] or ''),
             'subject': f'[Ticket {no}] {row["issue_type"]} from {C.mask_email(row["email"])}',
             'text': text, 'html': '<pre>' + pay_i18n.html.escape(text) + '</pre>', 'attachments': []}
    for msg in (user, admin):
        try:
            notify.send_email(msg)
        except Exception:
            log.exception('Ticket e-mail failed for %s', no)


def create_ticket():
    b = request.get_json(force=True, silent=True)
    if not isinstance(b, dict):
        raise C.ValidationError('Bad request.', {})
    if str(b.get('website') or '').strip():          # honeypot
        return jsonify({'ticket_no': 'HG-RECEIVED', 'status': 'open'}), 201
    data = validate(b)
    now = D.utcnow()
    for _ in range(3):
        try:
            with D.engine().begin() as conn:
                order = None
                if data['payment_ref'] != 'NA':
                    col = D.orders.c.razorpay_payment_id if data['payment_ref'].startswith('pay_') \
                        else D.orders.c.razorpay_order_id
                    order = conn.execute(select(D.orders.c.id).where(col == data['payment_ref'])).scalar()
                row = dict(data, id=str(uuid.uuid4()), ticket_no=_ticket_no(conn, today_ist()), status='open',
                           order_id=order, created_at=now, updated_at=now)
                conn.execute(insert(D.tickets).values(**row))
            break
        except IntegrityError:
            continue
    else:
        return _err(503, 'Please try again.', 'busy')
    _emails(row)
    return jsonify({'ticket_no': row['ticket_no'], 'status': 'open'}), 201


def _admin_view(r):
    return {k: (D.as_utc(getattr(r, k)).isoformat() if k.endswith('_at') and getattr(r, k) else getattr(r, k))
            for k in ('id', 'ticket_no', 'status', 'email', 'name', 'phone_e164', 'payment_ref', 'payment_date',
                      'issue_type', 'description', 'birth_details', 'lang', 'order_id', 'admin_note',
                      'created_at', 'updated_at', 'closed_at', 'purged_at')}


def admin_list():
    status = request.args.get('status')
    q = select(D.tickets).order_by(D.tickets.c.created_at.desc()).limit(500)
    if status in STATUSES:
        q = q.where(D.tickets.c.status == status)
    with D.engine().connect() as conn:
        rows = conn.execute(q).fetchall()
    return jsonify({'tickets': [_admin_view(r) for r in rows]})


def admin_update(ticket_id):
    b = request.get_json(force=True, silent=True) or {}
    values = {'updated_at': D.utcnow()}
    if 'status' in b:
        if b['status'] not in STATUSES:
            raise C.ValidationError('Unknown status.', {'status': 'open, in_progress or closed'})
        values['status'] = b['status']
        values['closed_at'] = D.utcnow() if b['status'] == 'closed' else None
    if 'admin_note' in b:
        values['admin_note'] = str(b['admin_note'] or '')[:4000]
    with D.engine().begin() as conn:
        res = conn.execute(update(D.tickets).where(D.tickets.c.id == ticket_id).values(**values))
        if not res.rowcount:
            return _err(404, 'Ticket not found.', 'not_found')
        row = conn.execute(select(D.tickets).where(D.tickets.c.id == ticket_id)).first()
    return jsonify(_admin_view(row))


def purge(now=None):
    now = now or D.utcnow()
    cutoff = now - timedelta(days=RETENTION_AFTER_CLOSE_DAYS)
    with D.engine().begin() as conn:
        res = conn.execute(update(D.tickets).where(
            D.tickets.c.purged_at.is_(None), D.tickets.c.status == 'closed', D.tickets.c.closed_at < cutoff)
            .values(email=None, name=None, phone_e164=None, description=None, birth_details=None, purged_at=now))
    return res.rowcount


def register(app, limiter):
    import booking_api

    def add(rule, fn, limit, methods=('GET',), admin=False):
        view = _guard(fn)
        if admin:
            view = booking_api._admin(view)
        app.add_url_rule(rule, f'ticket_{fn.__name__}', limiter.limit(limit)(view), methods=list(methods))

    add('/api/tickets', create_ticket, LIMIT_TICKET, ('POST',))
    add('/api/admin/tickets', admin_list, LIMIT_ADMIN, admin=True)
    add('/api/admin/tickets/<ticket_id>', admin_update, LIMIT_ADMIN, ('PUT',), admin=True)
