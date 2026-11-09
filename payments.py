"""
payments.py — paid reports through Razorpay. Built and tested, OFF by default.

Switch: PAYMENTS_ENABLED (features.py). While it is false:
  * POST /api/orders answers 503 and every download stays free, as before;
  * nothing here touches Razorpay or the database.
When it is true:
  * the free download routes answer 402 (see app.py);
  * a visitor buys one product, pays in Razorpay Checkout, and downloads the
    files from /api/orders/<id>/download/<pdf|excel>?token=...

Products and prices (paise, set in the environment, never by the browser):
  basic  PRICE_BASIC_PAISE  20000  ₹200  horoscope without Notes / Predictions
  full   PRICE_FULL_PAISE   50000  ₹500  horoscope with Notes (குறிப்புகள்) and Predictions (பலன்கள்)
  match  PRICE_MATCH_PAISE  20000  ₹200  marriage matching report
  family PRICE_FAMILY_PAISE 50000  ₹500  family reading report
INR only.

Settings: RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET,
PAYMENT_SECRET (signs download links), PAYMENT_LINK_HOURS (default 72).
Razorpay is called with plain HTTPS (requests); no SDK is needed.

Flow
  1. POST /api/orders {product, email, phone?, lang, request:{...}}
     The request is checked by building the report once (so a bad birth date
     fails before payment), the order is created at Razorpay with the amount
     from the settings, and a row is stored with status 'created'.
  2. Checkout runs in the browser.
  3. POST /api/orders/<id>/verify {razorpay_payment_id, razorpay_order_id,
     razorpay_signature}: HMAC-SHA256(order_id|payment_id, key secret).
     On success the order is 'paid' and a download token is returned.
  4. POST /api/payments/webhook: Razorpay's own call, signed with the webhook
     secret over the raw body. payment.captured / order.paid mark the order
     paid even if the browser closed before step 3; payment.failed and
     refund.processed set those states. Repeated events change nothing.
"""
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import timedelta

import requests
from flask import jsonify, request
from sqlalchemy import insert, select, update
from sqlalchemy.exc import OperationalError

import booking_core as C
import booking_db as D
import features
import pay_i18n
from astro_engine import InputError

log = logging.getLogger('horoscopegen.payments')

LIMIT_ORDER = '10 per hour'
LIMIT_VERIFY = '20 per hour'
LIMIT_DOWNLOAD = '30 per hour'
LIMIT_STATUS = '60 per hour'
LIMIT_WEBHOOK = '300 per minute'

RAZORPAY_API = 'https://api.razorpay.com/v1'

_render = None          # set by register(): render(product, payload, fmt, lang) -> (bytes, filename, mime)


class PaymentError(Exception):
    def __init__(self, status, message, code):
        super().__init__(message)
        self.status, self.code = status, code


# ── SETTINGS ──────────────────────────────────────────────────────────────────

def key_id():
    return os.environ.get('RAZORPAY_KEY_ID', '').strip()


def key_secret():
    return os.environ.get('RAZORPAY_KEY_SECRET', '').strip()


def webhook_secret():
    return os.environ.get('RAZORPAY_WEBHOOK_SECRET', '').strip()


def link_hours():
    try:
        return max(1, min(int(os.environ.get('PAYMENT_LINK_HOURS', 72)), 24 * 30))
    except ValueError:
        return 72


def ready():
    """Payments are switched on and every setting they need is present."""
    return (features.payments_enabled() and bool(key_id()) and bool(key_secret())
            and bool(os.environ.get('PAYMENT_SECRET', '').strip()) and D.configured())


def products(lang='en'):
    return [{'code': p, 'price_paise': features.price_paise(p), 'currency': 'INR',
             'name': pay_i18n.T(f'product.{p}', lang), 'includes': pay_i18n.T(f'includes.{p}', lang)}
            for p in features.PRODUCTS]


def options_block(lang='en'):
    """What /api/options adds for the website."""
    return {'payments_enabled': ready(), 'currency': 'INR', 'products': products(lang),
            'support_email': pay_i18n._support_address(), 'link_hours': link_hours()}


# ── SIGNATURES AND TOKENS ─────────────────────────────────────────────────────

def _hmac(secret, message):
    return hmac.new(secret.encode(), message.encode() if isinstance(message, str) else message,
                    hashlib.sha256).hexdigest()


def checkout_signature_ok(razorpay_order_id, razorpay_payment_id, signature, secret=None):
    expected = _hmac(secret or key_secret(), f'{razorpay_order_id}|{razorpay_payment_id}')
    return hmac.compare_digest(expected, str(signature or ''))


def webhook_signature_ok(raw_body, signature, secret=None):
    secret = secret or webhook_secret()
    if not secret:
        return False
    return hmac.compare_digest(_hmac(secret, raw_body), str(signature or ''))


def download_token(order_id):
    return _hmac(os.environ.get('PAYMENT_SECRET', ''), f'download:{order_id}')


def token_ok(order_id, token):
    secret = os.environ.get('PAYMENT_SECRET', '')
    return bool(secret) and hmac.compare_digest(download_token(order_id), str(token or ''))


# ── RAZORPAY ──────────────────────────────────────────────────────────────────

def razorpay_create_order(amount_paise, receipt, notes):
    """Create an order at Razorpay. Returns its id (order_...)."""
    r = requests.post(f'{RAZORPAY_API}/orders', auth=(key_id(), key_secret()), timeout=20,
                      json={'amount': amount_paise, 'currency': 'INR', 'receipt': receipt[:40],
                            'notes': notes, 'payment_capture': 1})
    if r.status_code >= 300:
        log.error('Razorpay order create answered %s', r.status_code)
        raise PaymentError(502, 'The payment service did not answer. Please try again.', 'gateway_error')
    return r.json()['id']


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _err(status, message, code):
    return jsonify({'error': message, 'code': code}), status


def _guard(fn):
    def run(*args, **kwargs):
        if not ready():
            return _err(503, 'Payments are not switched on yet.', 'payments_off')
        try:
            resp = fn(*args, **kwargs)
        except PaymentError as e:
            return _err(e.status, str(e), e.code)
        except C.ValidationError as e:
            return _err(422, str(e), 'invalid')
        except InputError as e:
            return _err(400, str(e), 'invalid_details')
        except OperationalError:
            log.exception('Database unreachable in %s', request.path)
            return _err(503, 'The payment service is busy. Please try again in a minute.', 'db_unavailable')
        if isinstance(resp, tuple):
            resp[0].headers['Cache-Control'] = 'no-store'
        else:
            resp.headers['Cache-Control'] = 'no-store'
        return resp
    run.__name__ = fn.__name__
    return run


def _body():
    b = request.get_json(force=True, silent=True)
    return b if isinstance(b, dict) else {}


def _load(conn, order_id):
    return conn.execute(select(D.orders).where(D.orders.c.id == str(order_id))).first()


def _view(row):
    return {'order_id': row.id, 'product': row.product, 'amount_paise': row.amount_paise,
            'currency': row.currency, 'status': row.status, 'razorpay_order_id': row.razorpay_order_id,
            'razorpay_payment_id': row.razorpay_payment_id,
            'paid_at': row.paid_at and D.as_utc(row.paid_at).isoformat(),
            'expires_at': row.paid_at and (D.as_utc(row.paid_at) + timedelta(hours=link_hours())).isoformat(),
            'files_available': _files_available(row)}


def _files_available(row):
    if row.status != 'paid' or row.purged_at or not row.request_payload or not row.paid_at:
        return False
    return D.utcnow() < D.as_utc(row.paid_at) + timedelta(hours=link_hours())


def links(row):
    from booking_api import api_url, site_url
    token = download_token(row.id)
    return {'pdf': f'{api_url()}/api/orders/{row.id}/download/pdf?token={token}',
            'excel': f'{api_url()}/api/orders/{row.id}/download/excel?token={token}',
            'page': f'{site_url()}/payment-success.html?order={row.id}&token={token}'}


def mark_paid(conn, row, payment_id):
    """Set the order paid once; send the receipt once. Returns the fresh row."""
    now = D.utcnow()
    if row.status != 'paid':
        conn.execute(update(D.orders).where(D.orders.c.id == row.id)
                     .values(status='paid', razorpay_payment_id=payment_id, paid_at=now))
    row = _load(conn, row.id)
    if not row.receipt_sent_at and row.email:
        try:
            import notify
            notify.send_email(pay_i18n.receipt_email(row, links(row), link_hours()))
            conn.execute(update(D.orders).where(D.orders.c.id == row.id).values(receipt_sent_at=now))
        except Exception:
            log.exception('Receipt e-mail failed for order %s', row.id)
    return _load(conn, row.id)


# ── ROUTES ────────────────────────────────────────────────────────────────────

def create_order():
    b = _body()
    product = str(b.get('product', '')).strip()
    if product not in features.PRODUCTS:
        raise PaymentError(422, 'Unknown product.', 'invalid_product')
    email = C.clean_email(b.get('email'))
    if not email:
        raise PaymentError(422, 'A valid e-mail address is required.', 'invalid_email')
    phone = C.clean_phone(b.get('phone')) if b.get('phone') else None
    if b.get('phone') and not phone:
        raise PaymentError(422, 'The phone number is not valid. Use the form +91 98765 43210.', 'invalid_phone')
    if not b.get('consent'):
        raise PaymentError(422, 'Please accept the Terms and the Refund policy.', 'consent_required')
    lang = str(b.get('lang') or 'en')
    payload = b.get('request')
    if not isinstance(payload, dict) or len(json.dumps(payload)) > 60000:
        raise PaymentError(422, 'The report details are missing.', 'invalid_request')
    payload = dict(payload, lang=lang)
    _render(product, payload, 'check', lang)        # raises InputError (400 in app) on bad details
    oid = str(uuid.uuid4())
    amount = features.price_paise(product)
    rzp_id = razorpay_create_order(amount, oid, {'product': product, 'order': oid})
    with D.engine().begin() as conn:
        conn.execute(insert(D.orders).values(
            id=oid, product=product, amount_paise=amount, currency='INR', razorpay_order_id=rzp_id,
            status='created', email=email, phone_e164=phone, lang=lang, request_payload=payload,
            created_at=D.utcnow()))
    return jsonify({'order_id': oid, 'razorpay_order_id': rzp_id, 'key_id': key_id(), 'amount': amount,
                    'currency': 'INR', 'name': 'HoroscopeGen',
                    'description': pay_i18n.T(f'product.{product}', lang),
                    'prefill': {'email': email, 'contact': phone or ''}}), 201


def verify_order(order_id):
    b = _body()
    with D.engine().begin() as conn:
        row = _load(conn, order_id)
        if not row:
            raise PaymentError(404, 'Order not found.', 'not_found')
        if str(b.get('razorpay_order_id')) != row.razorpay_order_id or not checkout_signature_ok(
                row.razorpay_order_id, b.get('razorpay_payment_id'), b.get('razorpay_signature')):
            raise PaymentError(400, 'The payment could not be verified.', 'bad_signature')
        row = mark_paid(conn, row, str(b.get('razorpay_payment_id')))
    return jsonify(dict(_view(row), token=download_token(row.id), links=links(row)))


def order_status(order_id):
    if not token_ok(order_id, request.args.get('token')):
        raise PaymentError(404, 'Order not found.', 'not_found')
    with D.engine().connect() as conn:
        row = _load(conn, order_id)
    if not row:
        raise PaymentError(404, 'Order not found.', 'not_found')
    return jsonify(dict(_view(row), links=links(row) if row.status == 'paid' else None))


def download(order_id, fmt):
    if fmt not in ('pdf', 'excel') or not token_ok(order_id, request.args.get('token')):
        raise PaymentError(404, 'Not found.', 'not_found')
    with D.engine().begin() as conn:
        row = _load(conn, order_id)
        if not row or row.status != 'paid':
            raise PaymentError(402, 'This order is not paid.', 'not_paid')
        if not _files_available(row):
            raise PaymentError(410, 'The download link has expired. Please raise a support ticket.', 'expired')
        conn.execute(update(D.orders).where(D.orders.c.id == row.id)
                     .values(download_count=D.orders.c.download_count + 1))
        payload, product, lang = row.request_payload, row.product, row.lang
    data, filename, mime = _render(product, payload, fmt, lang)
    from flask import make_response
    resp = make_response(data)
    resp.headers['Content-Type'] = mime
    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def webhook():
    """Razorpay's server calls this. Answers 200 for every valid event so Razorpay stops retrying."""
    raw = request.get_data()
    if not webhook_signature_ok(raw, request.headers.get('X-Razorpay-Signature')):
        return _err(400, 'Bad signature.', 'bad_signature')
    try:
        event = json.loads(raw)
    except ValueError:
        return _err(400, 'Bad body.', 'bad_body')
    kind = event.get('event', '')
    pl = event.get('payload', {})
    pay = (pl.get('payment') or {}).get('entity') or {}
    refund = (pl.get('refund') or {}).get('entity') or {}
    rzp_order = pay.get('order_id') or ((pl.get('order') or {}).get('entity') or {}).get('id')
    with D.engine().begin() as conn:
        row = None
        if rzp_order:
            row = conn.execute(select(D.orders).where(D.orders.c.razorpay_order_id == rzp_order)).first()
        elif refund.get('payment_id'):
            row = conn.execute(select(D.orders).where(
                D.orders.c.razorpay_payment_id == refund['payment_id'])).first()
        if not row:
            log.warning('Webhook %s for an unknown order', kind)
            return jsonify({'status': 'ignored'})
        if kind in ('payment.captured', 'order.paid'):
            if pay.get('amount') not in (None, row.amount_paise):
                log.error('Webhook amount %s differs from order %s', pay.get('amount'), row.id)
                return jsonify({'status': 'amount_mismatch'})
            mark_paid(conn, row, pay.get('id') or row.razorpay_payment_id)
        elif kind == 'payment.failed' and row.status == 'created':
            conn.execute(update(D.orders).where(D.orders.c.id == row.id).values(status='failed'))
        elif kind == 'refund.processed' and row.status != 'refunded':
            conn.execute(update(D.orders).where(D.orders.c.id == row.id)
                         .values(status='refunded', refunded_at=D.utcnow()))
    return jsonify({'status': 'ok'})


def purge(now=None):
    """Wipe the stored request, e-mail and phone RETENTION_DAYS after payment (or creation)."""
    now = now or D.utcnow()
    cutoff = now - timedelta(days=C.retention_days())
    with D.engine().begin() as conn:
        res = conn.execute(update(D.orders).where(D.orders.c.purged_at.is_(None),
                                                  D.orders.c.created_at < cutoff)
                           .values(request_payload=None, email=None, phone_e164=None, purged_at=now))
    return res.rowcount


def register(app, limiter, render):
    """render(product, payload, fmt, lang): fmt 'check' validates only; 'pdf'/'excel' return (bytes, filename, mime)."""
    global _render
    _render = render

    def add(rule, fn, limit, methods=('GET',)):
        app.add_url_rule(rule, f'pay_{fn.__name__}', limiter.limit(limit)(_guard(fn)), methods=list(methods))

    add('/api/orders', create_order, LIMIT_ORDER, ('POST',))
    add('/api/orders/<order_id>/verify', verify_order, LIMIT_VERIFY, ('POST',))
    add('/api/orders/<order_id>', order_status, LIMIT_STATUS)
    add('/api/orders/<order_id>/download/<fmt>', download, LIMIT_DOWNLOAD)
    add('/api/payments/webhook', webhook, LIMIT_WEBHOOK, ('POST',))
