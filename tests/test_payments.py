"""
Paid reports (payments.py) and support tickets (tickets.py), with Razorpay
mocked: nothing here reaches the network. SQLite unless TEST_DATABASE_URL.
"""
import hashlib
import hmac
import io
import json
import os
from datetime import datetime, timedelta, timezone

import openpyxl
import pytest

os.environ.setdefault('NOTIFY_WORKER', 'false')

import booking_db as D       # noqa: E402
import payments              # noqa: E402

UTC = timezone.utc
NOW = datetime(2026, 11, 9, 6, 0, tzinfo=UTC)            # 09-11-2026 11:30 IST
KEY_SECRET = 'rzp_test_secret_value'
WEBHOOK_SECRET = 'whsec_test_value'
ADMIN_KEY = 'test-admin-key-0123456789'
S = dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707)


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', os.environ.get('TEST_DATABASE_URL') or f'sqlite:///{tmp_path}/p.db')
    monkeypatch.setenv('PAYMENTS_ENABLED', 'true')
    monkeypatch.setenv('RAZORPAY_KEY_ID', 'rzp_test_key')
    monkeypatch.setenv('RAZORPAY_KEY_SECRET', KEY_SECRET)
    monkeypatch.setenv('RAZORPAY_WEBHOOK_SECRET', WEBHOOK_SECRET)
    monkeypatch.setenv('PAYMENT_SECRET', 'payment-secret')
    monkeypatch.setenv('ADMIN_API_KEY', ADMIN_KEY)
    monkeypatch.setenv('SUPPORT_EMAIL', 'support@example.com')
    monkeypatch.setattr(D, 'utcnow', lambda: NOW)
    D.reset_engine()
    D.metadata.drop_all(D.engine())
    D.metadata.create_all(D.engine())
    created = []
    monkeypatch.setattr(payments, 'razorpay_create_order',
                        lambda amount, receipt, notes: created.append(amount) or f'order_{len(created):014d}')
    sent = []
    import notify
    monkeypatch.setattr(notify, 'send_email', lambda msg: sent.append(msg) or 'sent')
    yield {'created': created, 'sent': sent}
    D.metadata.drop_all(D.engine())
    D.reset_engine()


@pytest.fixture()
def client(env):
    import app as app_module
    return app_module.app.test_client()


def sign(order_id, payment_id):
    return hmac.new(KEY_SECRET.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()


def order(client, product='full', request=None, **over):
    body = {'product': product, 'email': 'Buyer@Example.com', 'lang': 'ta', 'consent': True,
            'request': request or dict(S)}
    body.update(over)
    return client.post('/api/orders', json=body)


def pay(client, o, payment_id='pay_ABCDEFGHIJ1234'):
    return client.post(f"/api/orders/{o['order_id']}/verify", json={
        'razorpay_order_id': o['razorpay_order_id'], 'razorpay_payment_id': payment_id,
        'razorpay_signature': sign(o['razorpay_order_id'], payment_id)})


# ── switch ────────────────────────────────────────────────────────────────────

def test_payments_off_by_default(monkeypatch):
    import app as app_module
    monkeypatch.delenv('PAYMENTS_ENABLED', raising=False)
    c = app_module.app.test_client()
    assert c.post('/api/orders', json={}).status_code == 503
    assert c.get('/api/options').get_json()['payments_enabled'] is False
    r = c.post('/api/horoscope', json=dict(S, lang='en', predictions=True))
    assert 'predictions' in r.get_json() and 'predictions_locked' not in r.get_json()


def test_switch_on_needs_every_setting(env, monkeypatch):
    assert payments.ready()
    monkeypatch.setenv('RAZORPAY_KEY_SECRET', '')
    assert not payments.ready()


def test_with_payments_on_free_downloads_answer_402_and_predictions_are_locked(client):
    for path, body in (('/api/download/excel', dict(S)), ('/api/download/pdf', dict(S)),
                       ('/api/download/match/pdf', {}), ('/api/download/family/excel', {})):
        assert client.post(path, json=body).status_code == 402
    j = client.post('/api/horoscope', json=dict(S, lang='en', predictions=True)).get_json()
    assert j.get('predictions_locked') is True and 'predictions' not in j
    assert client.get('/api/options').get_json()['payments_enabled'] is True


# ── orders ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('product,amount', [('basic', 20000), ('full', 50000)])
def test_amount_comes_from_the_settings(client, env, product, amount):
    r = order(client, product, amount=1)          # an amount from the browser is ignored
    assert r.status_code == 201, r.get_json()
    assert r.get_json()['amount'] == amount and env['created'] == [amount]
    assert r.get_json()['currency'] == 'INR'


def test_price_override_from_env(client, env, monkeypatch):
    monkeypatch.setenv('PRICE_FULL_PAISE', '45000')
    assert order(client).get_json()['amount'] == 45000


def test_order_input_is_checked_before_payment(client, env):
    assert order(client, product='gold').status_code == 422
    assert order(client, email='not-an-email').status_code == 422
    assert order(client, consent=False).status_code == 422
    assert order(client, request=dict(S, dob='1984-13-40')).status_code == 400
    assert env['created'] == []


def test_verify_marks_paid_sends_one_receipt_and_downloads_work(client, env):
    o = order(client).get_json()
    bad = client.post(f"/api/orders/{o['order_id']}/verify", json={
        'razorpay_order_id': o['razorpay_order_id'], 'razorpay_payment_id': 'pay_X',
        'razorpay_signature': 'deadbeef'})
    assert bad.status_code == 400
    r = pay(client, o)
    assert r.status_code == 200
    j = r.get_json()
    assert j['status'] == 'paid' and j['files_available'] and j['razorpay_payment_id'] == 'pay_ABCDEFGHIJ1234'
    assert len(env['sent']) == 1
    msg = env['sent'][0]
    assert msg['to'] == 'buyer@example.com' and 'ரசீது' in msg['subject'] and '₹500' in msg['text']
    assert 'pay_ABCDEFGHIJ1234' in msg['text']
    pay(client, o)                                  # a second verify sends nothing more
    assert len(env['sent']) == 1
    x = client.get(f"/api/orders/{o['order_id']}/download/excel?token={j['token']}")
    assert x.status_code == 200
    names = openpyxl.load_workbook(io.BytesIO(x.data)).sheetnames
    assert 'குறிப்புகள்' in names and 'பலன்கள்' in names and not [n for n in names if n.startswith('AI_')]
    p = client.get(f"/api/orders/{o['order_id']}/download/pdf?token={j['token']}")
    assert p.status_code == 200 and p.data[:4] == b'%PDF'
    assert client.get(f"/api/orders/{o['order_id']}/download/pdf?token=wrong").status_code == 404


def test_basic_order_has_no_notes_or_predictions(client):
    o = order(client, 'basic').get_json()
    tok = pay(client, o).get_json()['token']
    names = openpyxl.load_workbook(io.BytesIO(
        client.get(f"/api/orders/{o['order_id']}/download/excel?token={tok}").data)).sheetnames
    assert 'குறிப்புகள்' not in names and 'பலன்கள்' not in names


def test_unpaid_order_cannot_download(client):
    o = order(client).get_json()
    tok = payments.download_token(o['order_id'])
    assert client.get(f"/api/orders/{o['order_id']}/download/pdf?token={tok}").status_code == 402


def test_links_expire(client, monkeypatch):
    o = order(client).get_json()
    tok = pay(client, o).get_json()['token']
    monkeypatch.setattr(D, 'utcnow', lambda: NOW + timedelta(hours=73))
    assert client.get(f"/api/orders/{o['order_id']}/download/pdf?token={tok}").status_code == 410


def test_match_and_family_products(client, env):
    boy = dict(name='Boy', dob='1990-05-10', tob='06:30', pob='Chennai', lat=13.0827, lon=80.2707)
    girl = dict(name='Girl', dob='1993-08-21', tob='14:10', pob='Madurai', lat=9.9252, lon=78.1198)
    r = order(client, 'match', request={'boy': boy, 'girl': girl})
    assert r.status_code == 201, r.get_json()
    assert r.get_json()['amount'] == 20000
    r = order(client, 'family', request={'members': [dict(boy, relation='Self'), dict(girl, relation='Spouse')]})
    assert r.status_code == 201, r.get_json()
    assert r.get_json()['amount'] == 50000


# ── webhook ───────────────────────────────────────────────────────────────────

def hook(client, event, sig=None):
    raw = json.dumps(event).encode()
    sig = sig or hmac.new(WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return client.post('/api/payments/webhook', data=raw, headers={'X-Razorpay-Signature': sig,
                                                                     'Content-Type': 'application/json'})


def captured(o, amount=50000):
    return {'event': 'payment.captured', 'payload': {'payment': {'entity': {
        'id': 'pay_WEBHOOK0000001', 'order_id': o['razorpay_order_id'], 'amount': amount}}}}


def test_webhook_marks_paid_once_and_checks_signature(client, env):
    o = order(client).get_json()
    assert hook(client, captured(o), sig='bad').status_code == 400
    assert hook(client, captured(o)).status_code == 200
    assert hook(client, captured(o)).status_code == 200            # repeated: no change, no second e-mail
    assert len(env['sent']) == 1
    tok = payments.download_token(o['order_id'])
    st = client.get(f"/api/orders/{o['order_id']}?token={tok}").get_json()
    assert st['status'] == 'paid' and st['razorpay_payment_id'] == 'pay_WEBHOOK0000001'


def test_webhook_amount_mismatch_is_not_paid(client):
    o = order(client).get_json()
    assert hook(client, captured(o, amount=100)).get_json()['status'] == 'amount_mismatch'
    tok = payments.download_token(o['order_id'])
    assert client.get(f"/api/orders/{o['order_id']}?token={tok}").get_json()['status'] == 'created'


def test_webhook_refund(client):
    o = order(client).get_json()
    hook(client, captured(o))
    hook(client, {'event': 'refund.processed', 'payload': {'refund': {'entity': {
        'payment_id': 'pay_WEBHOOK0000001'}}}})
    tok = payments.download_token(o['order_id'])
    assert client.get(f"/api/orders/{o['order_id']}?token={tok}").get_json()['status'] == 'refunded'
    assert client.get(f"/api/orders/{o['order_id']}/download/pdf?token={tok}").status_code == 402


def test_purge_keeps_accounting_fields(client):
    o = order(client).get_json()
    pay(client, o)
    assert payments.purge(NOW + timedelta(days=91)) == 1
    with D.engine().connect() as conn:
        row = conn.execute(D.orders.select()).first()
    assert row.request_payload is None and row.email is None
    assert row.amount_paise == 50000 and row.razorpay_payment_id == 'pay_ABCDEFGHIJ1234'


# ── tickets ───────────────────────────────────────────────────────────────────

def ticket(**over):
    b = {'email': 'user@example.com', 'payment_ref': 'pay_ABCDEFGHIJ1234', 'payment_date': '2026-11-08',
         'issue_type': 'no_report', 'description': 'Money was debited but no file came to me.',
         'consent': True, 'lang': 'ta', 'website': ''}
    b.update(over)
    return b


def test_ticket_is_stored_numbered_and_e_mailed(client, env):
    r = client.post('/api/tickets', json=ticket())
    assert r.status_code == 201, r.get_json()
    assert r.get_json()['ticket_no'] == 'HG-20261109-0001'
    assert client.post('/api/tickets', json=ticket()).get_json()['ticket_no'] == 'HG-20261109-0002'
    to = [m['to'] for m in env['sent']]
    assert to.count('user@example.com') == 2 and to.count('support@example.com') == 2
    assert 'HG-20261109-0001' in env['sent'][0]['subject']


@pytest.mark.parametrize('field,value', [
    ('email', ''), ('email', 'bad'), ('payment_ref', ''), ('payment_ref', 'pay_123'),
    ('payment_ref', 'ABCDEFGHIJ1234'), ('payment_date', ''), ('payment_date', '2026-11-10'),
    ('payment_date', '2026-01-01'), ('issue_type', 'x'), ('description', 'short'), ('consent', False)])
def test_ticket_required_fields(client, field, value):
    r = client.post('/api/tickets', json=ticket(**{field: value}))
    assert r.status_code == 422 and field in r.get_json()['fields']


def test_ticket_not_a_payment_issue(client):
    r = client.post('/api/tickets', json=ticket(payment_ref='', not_payment=True))
    assert r.status_code == 201


def test_ticket_links_to_the_order(client):
    o = order(client).get_json()
    pay(client, o)
    client.post('/api/tickets', json=ticket())
    rows = client.get('/api/admin/tickets', headers={'X-Admin-Key': ADMIN_KEY}).get_json()['tickets']
    assert rows[0]['order_id'] == o['order_id']


def test_ticket_honeypot_stores_nothing(client, env):
    assert client.post('/api/tickets', json=ticket(website='http://spam')).status_code == 201
    assert client.get('/api/admin/tickets', headers={'X-Admin-Key': ADMIN_KEY}).get_json()['tickets'] == []
    assert env['sent'] == []


def test_ticket_admin(client):
    client.post('/api/tickets', json=ticket())
    assert client.get('/api/admin/tickets').status_code == 401
    rows = client.get('/api/admin/tickets', headers={'X-Admin-Key': ADMIN_KEY}).get_json()['tickets']
    tid = rows[0]['id']
    r = client.put(f'/api/admin/tickets/{tid}', json={'status': 'closed', 'admin_note': 'Resent link'},
                   headers={'X-Admin-Key': ADMIN_KEY})
    assert r.get_json()['status'] == 'closed' and r.get_json()['closed_at']
    assert client.get('/api/admin/tickets?status=open', headers={'X-Admin-Key': ADMIN_KEY}).get_json()[
        'tickets'] == []


def test_tickets_without_database(monkeypatch):
    import app as app_module
    monkeypatch.delenv('DATABASE_URL', raising=False)
    D.reset_engine()
    r = app_module.app.test_client().post('/api/tickets', json=ticket())
    assert r.status_code == 503 and r.get_json()['fields']['support_email']
