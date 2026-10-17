"""
Tests for astrologer consultations: slots, validation, the booking routes,
double bookings, the calendar file and link, notifications, the admin API
and the retention purge.

The routes run against SQLite in a temporary file unless TEST_DATABASE_URL
names a PostgreSQL database, e.g.
    TEST_DATABASE_URL=postgresql://postgres@localhost/hg_test pytest tests/test_bookings.py
The concurrency test needs PostgreSQL and is skipped without it.

"Now" is fixed at Monday 19 October 2026, 09:30 IST, so every expected time
below is a plain figure worked out by hand:
  09:00 IST = 03:30 UTC     19:30 IST = 14:00 UTC     20:00 IST = 14:30 UTC
"""
import os
import sys
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

os.environ.setdefault('NOTIFY_WORKER', 'false')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import booking_core as C      # noqa: E402
import booking_db as D        # noqa: E402
import notify                 # noqa: E402

UTC = timezone.utc
NOW = datetime(2026, 10, 19, 4, 0, tzinfo=UTC)          # Mon 19 Oct 2026, 09:30 IST
TUESDAY = '2026-10-20'
ADMIN_KEY = 'test-admin-key-0123456789'
BIRTH = {'name': 'Sample Native', 'dob': '1998-03-06', 'tob': '01:37', 'pob': 'Delhi',
         'lat': 28.6139, 'lon': 77.2090, 'tz': 'Asia/Kolkata'}


def body(**over):
    b = {'astrologer_id': 1, 'slot_start': f'{TUESDAY}T09:30', 'name': 'Priya R',
         'email': 'priya@example.com', 'whatsapp': '+91 98765 43210',
         'questions': ['When will I get a job?', 'Is 2027 good for marriage?'],
         'birth': dict(BIRTH), 'lang': 'en', 'consent_share': True, 'consent_messages': True,
         'adult': True, 'website': ''}
    b.update(over)
    return b


# ── SLOTS ─────────────────────────────────────────────────────────────────────

def test_22_slots_from_0900_to_2000_ist():
    slots = C.day_slots(date(2026, 10, 20), NOW)
    assert len(slots) == 22
    assert slots[0]['start'] == '09:00' and slots[0]['start_utc'] == '2026-10-20T03:30:00Z'
    assert slots[-1]['start'] == '19:30' and slots[-1]['end'] == '20:00'
    assert slots[-1]['start_utc'] == '2026-10-20T14:00:00Z' and slots[-1]['end_utc'] == '2026-10-20T14:30:00Z'
    assert all(s['status'] == 'available' for s in slots)


def test_slot_grid_alignment():
    ist = C.IST
    assert C.is_slot_start(datetime(2026, 10, 20, 9, 0, tzinfo=ist))
    assert C.is_slot_start(datetime(2026, 10, 20, 19, 30, tzinfo=ist))
    assert not C.is_slot_start(datetime(2026, 10, 20, 20, 0, tzinfo=ist))     # would end at 20:30
    assert not C.is_slot_start(datetime(2026, 10, 20, 8, 30, tzinfo=ist))
    assert not C.is_slot_start(datetime(2026, 10, 20, 9, 15, tzinfo=ist))
    assert C.is_slot_start(datetime(2026, 10, 20, 4, 0, tzinfo=UTC))           # 09:30 IST


def test_today_respects_the_two_hour_lead_time():
    slots = {s['start']: s['status'] for s in C.day_slots(date(2026, 10, 19), NOW)}
    assert slots['09:00'] == 'past' and slots['11:00'] == 'past'
    assert slots['11:30'] == 'available'           # exactly now + 2 hours


def test_weekly_hours_and_blocks():
    hours = [(1, 9 * 60, 13 * 60)]                 # Tuesdays 09:00-13:00 only
    tue = {s['start']: s['status'] for s in C.day_slots(date(2026, 10, 20), NOW, hours=hours)}
    assert tue['12:30'] == 'available' and tue['13:00'] == 'blocked' and tue['19:30'] == 'blocked'
    wed = C.day_slots(date(2026, 10, 21), NOW, hours=hours)
    assert {s['status'] for s in wed} == {'blocked'}
    block = [(datetime(2026, 10, 20, 4, 30, tzinfo=UTC), datetime(2026, 10, 20, 5, 30, tzinfo=UTC))]
    tue = {s['start']: s['status'] for s in C.day_slots(date(2026, 10, 20), NOW, blocks=block)}
    assert (tue['09:30'], tue['10:00'], tue['10:30'], tue['11:00']) == ('available', 'blocked', 'blocked', 'available')


def test_booked_beats_blocked_and_past_beats_booked():
    booked = {datetime(2026, 10, 20, 4, 0, tzinfo=UTC), datetime(2026, 10, 19, 4, 0, tzinfo=UTC)}
    tue = {s['start']: s['status'] for s in C.day_slots(date(2026, 10, 20), NOW, booked=booked)}
    assert tue['09:30'] == 'booked'
    mon = {s['start']: s['status'] for s in C.day_slots(date(2026, 10, 19), NOW, booked=booked)}
    assert mon['09:30'] == 'past'


def test_slot_sent_from_another_time_zone():
    # A visitor in New York sees the 09:30 IST slot at midnight their time, at the start of the 20th;
    # the slot half an hour earlier (09:00 IST) is 23:30 on the 19th for them.
    start = C.parse_slot('2026-10-20T00:00:00-04:00')
    C.check_slot(start, NOW)
    C.check_slot(C.parse_slot('2026-10-19T23:30:00-04:00'), NOW)
    with pytest.raises(C.ValidationError):
        C.check_slot(C.parse_slot('2026-10-19T23:00:00-04:00'), NOW)      # 08:30 IST
    assert start.astimezone(C.IST).strftime('%Y-%m-%d %H:%M') == '2026-10-20 09:30'
    assert C.parse_slot('2026-10-20T04:00:00Z') == start


def test_booking_window():
    C.check_slot(C.parse_slot('2026-11-18T19:30'), NOW)       # day 30
    with pytest.raises(C.ValidationError):
        C.check_slot(C.parse_slot('2026-11-19T09:00'), NOW)   # day 31
    with pytest.raises(C.ValidationError):
        C.check_slot(C.parse_slot('2026-10-19T10:00'), NOW)   # inside the lead time


# ── VALIDATION ────────────────────────────────────────────────────────────────

def test_valid_booking_is_cleaned():
    out = C.validate_booking(body(questions=['  <b>என் திருமணம்</b> எப்போது? 🙏  ', '', 'Second\r\n\r\n\r\nline']),
                             NOW)
    assert out['whatsapp'] == '+919876543210' and out['email'] == 'priya@example.com'
    assert out['questions'] == ['என் திருமணம் எப்போது? 🙏', 'Second\n\nline']
    assert out['slot_start'] == datetime(2026, 10, 20, 4, 0, tzinfo=UTC)


@pytest.mark.parametrize('over, field', [
    ({'email': 'a@b.com\r\nBcc: x@y.com'}, 'email'),
    ({'email': 'not-an-email'}, 'email'),
    ({'whatsapp': '98765'}, 'whatsapp'),
    ({'whatsapp': '+0123456789'}, 'whatsapp'),
    ({'name': 'A'}, 'name'),
    ({'questions': []}, 'questions'),
    ({'questions': ['', 'second only']}, 'questions'),
    ({'questions': ['q'] * 6}, 'questions'),
    ({'questions': ['x' * 501]}, 'questions'),
    ({'consent_share': False}, 'consent_share'),
    ({'consent_messages': None}, 'consent_messages'),
    ({'adult': False}, 'adult'),
    ({'slot_start': f'{TUESDAY}T09:15'}, 'slot_start'),
    ({'slot_start': f'{TUESDAY}T20:00'}, 'slot_start'),
    ({'birth': {'name': 'x'}}, 'birth'),
    ({'birth': dict(BIRTH, lat=123)}, 'birth'),
    ({'website': 'http://spam'}, 'website'),
])
def test_invalid_booking(over, field):
    with pytest.raises(C.ValidationError) as e:
        C.validate_booking(body(**over), NOW)
    assert field in e.value.fields


def test_500_characters_is_allowed():
    assert len(C.validate_booking(body(questions=['ம' * 500]), NOW)['questions'][0]) == 500


def test_masking():
    assert C.mask_email('priya@example.com') == 'p***@example.com'
    assert C.mask_phone('+919876543210') == '+91********10'


# ── CALENDAR ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('ist, utc_start, utc_end', [
    ('2026-10-20T09:00', '20261020T033000Z', '20261020T040000Z'),
    ('2026-10-20T19:30', '20261020T140000Z', '20261020T143000Z'),
])
def test_ics_and_google_link_times(ist, utc_start, utc_end):
    start = C.parse_slot(ist)
    end = start + timedelta(minutes=30)
    data = C.ics('b-1', 'Astro, "Sample"', 501, '+910000000001', start, end, NOW).decode()
    assert '\r\n' in data and '\n' not in data.replace('\r\n', '')
    assert f'DTSTART:{utc_start}\r\n' in data and f'DTEND:{utc_end}\r\n' in data
    assert 'UID:b-1@horoscopegen.in' in data and 'DTSTAMP:20261019T040000Z' in data
    assert 'TRIGGER:-PT30M' in data and 'TRIGGER:-P1D' in data
    assert 'SUMMARY:Astrology consultation with Astro\\, "Sample"' in data
    assert all(len(line.encode()) <= 75 for line in data.split('\r\n'))
    q = parse_qs(urlparse(C.google_calendar_link('b-1', 'Astro', 501, '+91000', start, end)).query)
    assert q['dates'] == [f'{utc_start}/{utc_end}'] and q['ctz'] == ['Asia/Kolkata']
    assert q['action'] == ['TEMPLATE'] and 'b-1' in q['details'][0] and 'offline' in q['details'][0]


def test_ics_for_an_evening_slot_seen_across_midnight_elsewhere():
    # 19:30 IST is still the same UTC date; a viewer in Auckland (UTC+13) sees it on the next day.
    start = C.parse_slot('2026-10-20T19:30')
    assert start.astimezone(UTC).date() == date(2026, 10, 20)
    from zoneinfo import ZoneInfo
    assert start.astimezone(ZoneInfo('Pacific/Auckland')).strftime('%Y-%m-%d %H:%M') == '2026-10-21 03:00'


def test_cancelled_ics():
    start = C.parse_slot('2026-10-20T09:00')
    data = C.ics('b-1', 'A', 1, '+91', start, start + timedelta(minutes=30), NOW, cancelled=True).decode()
    assert 'METHOD:CANCEL' in data and 'STATUS:CANCELLED' in data and 'VALARM' not in data


def test_tokens():
    t = C.make_token('abc')
    assert t == C.make_token('abc') and t != C.make_token('abd') and len(t) == 40
    assert C.token_matches(t, C.hash_token(t)) and not C.token_matches('x', C.hash_token(t))
    assert not C.token_matches('', C.hash_token(''))


# ── ROUTES ────────────────────────────────────────────────────────────────────

def _test_db_url(tmp_path):
    return os.environ.get('TEST_DATABASE_URL') or f'sqlite:///{tmp_path}/bookings.db'


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', _test_db_url(tmp_path))
    monkeypatch.setenv('ADMIN_API_KEY', ADMIN_KEY)
    monkeypatch.setenv('BOOKING_SECRET', 'test-secret')
    monkeypatch.setattr(D, 'utcnow', lambda: NOW)
    D.reset_engine()
    D.metadata.drop_all(D.engine())
    D.metadata.create_all(D.engine())
    import manage
    manage.seed()                 # ids 1, 2, 3; astrologer 2 works weekday mornings only
    yield D.engine()
    D.metadata.drop_all(D.engine())
    D.reset_engine()


@pytest.fixture()
def client(db):
    import app as app_module
    return app_module.app.test_client()


def admin(headers=None):
    return dict({'X-Admin-Key': ADMIN_KEY}, **(headers or {}))


def slots_of(client, astrologer_id=1, day=TUESDAY):
    r = client.get(f'/api/astrologers/{astrologer_id}/slots?date={day}')
    assert r.status_code == 200, r.get_json()
    return {s['start']: s['status'] for s in r.get_json()['slots']}


def test_password_kept_in_its_own_setting(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://owner@ep-x.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    monkeypatch.setenv('DATABASE_PASSWORD', 'p@ss/word')
    url = D.database_url()
    from sqlalchemy.engine import make_url
    u = make_url(url)
    assert url.startswith('postgresql+psycopg://') and u.password == 'p@ss/word' and u.username == 'owner'
    assert u.query == {'sslmode': 'require', 'channel_binding': 'require'}
    monkeypatch.setenv('DATABASE_URL', 'postgresql://owner:inline@host/db')
    assert make_url(D.database_url()).password == 'inline'          # a password in the URL wins


def test_no_database_means_503(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    D.reset_engine()
    import app as app_module
    r = app_module.app.test_client().get('/api/astrologers')
    assert r.status_code == 503 and r.get_json()['code'] == 'not_configured'


def test_list_shows_active_astrologers_only(client):
    client.put('/api/admin/astrologers/3', json={'is_active': False}, headers=admin())
    r = client.get('/api/astrologers')
    data = r.get_json()['astrologers']
    assert r.status_code == 200 and r.headers['Cache-Control'] == 'no-store'
    assert {a['id'] for a in data} == {1, 2}
    assert set(data[0]) >= {'id', 'name', 'age', 'phone', 'fee_inr'} and 'email' not in data[0]
    assert client.get('/api/astrologers/3').status_code == 404


def test_slots_route(client):
    s = slots_of(client)
    assert len(s) == 22 and set(s.values()) == {'available'}
    assert client.get('/api/astrologers/1/slots?date=2026-13-01').status_code == 422
    assert client.get('/api/astrologers/1/slots?date=2026-12-31').status_code == 422     # past the window
    assert client.get('/api/astrologers/99/slots?date=2026-10-20').status_code == 404
    morning = slots_of(client, 2)
    assert morning['12:30'] == 'available' and morning['13:00'] == 'blocked'


def test_book_then_the_slot_is_red(client):
    r = client.post('/api/bookings', json=body())
    out = r.get_json()
    assert r.status_code == 201, out
    assert out['status'] == 'confirmed' and out['slot_label_ist'] == 'Tue, 20 Oct 2026, 09:30 IST'
    assert out['slot_start_utc'] == '2026-10-20T04:00:00Z' and len(out['token']) == 40
    assert out['questions'] == body()['questions']
    assert out['whatsapp_astrologer_url'].startswith('https://wa.me/910000000001?text=')
    assert 'dates=20261020T040000Z%2F20261020T043000Z' in out['google_calendar_url']
    assert slots_of(client)['09:30'] == 'booked'
    # Nothing secret is stored in clear.
    with D.engine().connect() as conn:
        row = conn.execute(D.bookings.select()).first()
    assert row.cancel_token_hash == C.hash_token(out['token']) and out['token'] not in str(tuple(row))
    assert set(row.horoscope_input) <= set(C.BIRTH_KEYS)


def test_double_booking_is_refused(client):
    assert client.post('/api/bookings', json=body()).status_code == 201
    r = client.post('/api/bookings', json=body(email='other@example.com'))
    assert r.status_code == 409 and r.get_json()['code'] == 'slot_taken'
    # Another astrologer at the same time is fine.
    assert client.post('/api/bookings', json=body(astrologer_id=3)).status_code == 201


def test_unique_index_holds_without_the_application(db):
    from sqlalchemy.exc import IntegrityError
    row = dict(astrologer_id=1, slot_start_utc=NOW + timedelta(days=1), slot_end_utc=NOW + timedelta(days=1, minutes=30),
               status='confirmed', user_name='a', user_email='a@b.c', user_whatsapp='+911234567890', questions=['q'],
               horoscope_input={}, lang='en', cancel_token_hash='x', consent_share_at=NOW, consent_messages_at=NOW,
               adult_confirmed_at=NOW, notification_status={}, created_at=NOW)
    with db.begin() as conn:
        conn.execute(D.bookings.insert().values(id='00000000-0000-0000-0000-000000000001', **row))
    with pytest.raises(IntegrityError):
        with db.begin() as conn:
            conn.execute(D.bookings.insert().values(id='00000000-0000-0000-0000-000000000002', **row))
    with db.begin() as conn:      # a cancelled booking does not hold the slot
        conn.execute(D.bookings.insert().values(id='00000000-0000-0000-0000-000000000003',
                                                **dict(row, status='cancelled')))


@pytest.mark.skipif(not (os.environ.get('TEST_DATABASE_URL') or '').startswith('postgres'),
                    reason='needs TEST_DATABASE_URL pointing at PostgreSQL')
def test_concurrent_requests_for_one_slot(client, monkeypatch):
    import app as app_module
    import booking_api
    # Let every request pass validation first, then race for the insert.
    barrier = threading.Barrier(8)
    real = booking_api._active_astrologer

    def slow_lookup(conn, astrologer_id):
        row = real(conn, astrologer_id)
        try:
            barrier.wait(timeout=10)
        except threading.BrokenBarrierError:
            pass
        return row

    monkeypatch.setattr(booking_api, '_active_astrologer', slow_lookup)
    codes = []

    def book(i):
        with app_module.app.test_client() as c:
            codes.append(c.post('/api/bookings', json=body(email=f'u{i}@example.com')).status_code)

    threads = [threading.Thread(target=book, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(codes) == [201] + [409] * 7


def test_repeated_click_returns_the_same_booking(client):
    key = 'k' * 24
    first = client.post('/api/bookings', json=body(idempotency_key=key))
    again = client.post('/api/bookings', json=body(idempotency_key=key))
    assert first.status_code == 201 and again.status_code == 200
    assert again.get_json()['id'] == first.get_json()['id'] and again.get_json()['token'] == first.get_json()['token']
    other = client.post('/api/bookings', json=body(idempotency_key=key, slot_start=f'{TUESDAY}T10:00'))
    assert other.status_code == 409 and other.get_json()['code'] == 'idempotency_conflict'


def test_booking_refusals(client):
    r = client.post('/api/bookings', json=body(slot_start=f'{TUESDAY}T08:30'))
    assert r.status_code == 422 and 'slot_start' in r.get_json()['fields']
    assert client.post('/api/bookings', data='[1]', content_type='application/json').status_code == 400
    r = client.post('/api/bookings', json=body(astrologer_id=2, slot_start=f'{TUESDAY}T15:00'))
    assert r.status_code == 409 and r.get_json()['code'] == 'slot_unavailable'      # outside his hours
    r = client.post('/api/bookings', json=body(birth=dict(BIRTH, dob='1998-02-30')))
    assert r.status_code == 422 and 'birth' in r.get_json()['fields']


def test_astrologer_deactivated_after_the_page_opened(client):
    assert slots_of(client)['09:30'] == 'available'
    client.put('/api/admin/astrologers/1', json={'is_active': False}, headers=admin())
    r = client.post('/api/bookings', json=body())
    assert r.status_code == 409 and r.get_json()['code'] == 'astrologer_unavailable'


def test_read_and_cancel_need_the_token(client):
    out = client.post('/api/bookings', json=body()).get_json()
    bid, token = out['id'], out['token']
    assert client.get(f'/api/bookings/{bid}?token={token}').status_code == 200
    assert client.get(f'/api/bookings/{bid}?token=wrong').status_code == 404
    assert client.get(f'/api/bookings/{bid}').status_code == 404
    assert client.get('/api/bookings/not-a-uuid?token=x').status_code == 404
    assert client.post(f'/api/bookings/{bid}/cancel', json={'token': 'wrong'}).status_code == 404
    assert client.get(f'/api/bookings/{bid}/ics?token=wrong').status_code == 404

    r = client.get(f'/api/bookings/{bid}/ics?token={token}')
    assert r.status_code == 200 and r.headers['Content-Type'].startswith('text/calendar')
    assert f'UID:{bid}@horoscopegen.in' in r.get_data(as_text=True)

    r = client.post(f'/api/bookings/{bid}/cancel', json={'token': token})
    assert r.status_code == 200 and r.get_json()['status'] == 'cancelled'
    assert slots_of(client)['09:30'] == 'available'            # green again at once
    assert client.post(f'/api/bookings/{bid}/cancel', json={'token': token}).status_code == 200
    assert client.post('/api/bookings', json=body(email='next@example.com')).status_code == 201


def test_booking_pdf_link(client):
    out = client.post('/api/bookings', json=body()).get_json()
    r = client.get(f"/api/bookings/{out['id']}/pdf?token={out['token']}")
    assert r.status_code == 200 and r.get_data()[:5] == b'%PDF-'


def test_booking_rate_limit(client):
    import app as app_module
    app_module.limiter.enabled = True
    app_module.limiter.reset()
    ip = {'CF-Connecting-IP': '203.0.113.9'}
    codes = [client.post('/api/bookings', json=body(slot_start=f'{TUESDAY}T{10 + i}:00'), headers=ip).status_code
             for i in range(6)]
    assert codes == [201] * 5 + [429]
    assert client.post('/api/bookings', json=body(slot_start=f'{TUESDAY}T17:00'),
                       headers={'CF-Connecting-IP': '203.0.113.10'}).status_code == 201
    app_module.limiter.reset()


# ── NOTIFICATIONS ─────────────────────────────────────────────────────────────

@pytest.fixture()
def sent(monkeypatch):
    out = []
    monkeypatch.setattr(notify, '_render_pdf', lambda birth, lang: b'%PDF-1.4 fake')
    return out


def _status(bid):
    with D.engine().connect() as conn:
        return conn.execute(D.bookings.select().where(D.bookings.c.id == bid)).first().notification_status


def test_both_emails_go_out_with_everything_in_them(client, sent):
    out = client.post('/api/bookings', json=body(questions=['Will I go abroad? <b>soon</b> & safe', 'வேலை?'])).get_json()
    assert notify.process_outbox_once(now=NOW, send=lambda m: sent.append(m) or 'sent') == 2
    assert notify.process_outbox_once(now=NOW, send=lambda m: 1 / 0) == 0          # nothing left
    by_to = {m['to']: m for m in sent}
    user, astro = by_to['priya@example.com'], by_to['sample.astrologer1@example.com']
    for m in (user, astro):
        assert out['id'] in m['text'] and 'Tue, 20 Oct 2026, 09:30 IST' in m['text']
        assert '1. Will I go abroad? soon & safe' in m['text'] and '2. வேலை?' in m['text']
        assert 'soon &amp; safe' in m['html'] and '<b>soon' not in m['html']
        assert [a[0][-3:] for a in m['attachments']] == ['pdf', 'ics']
        assert '\n' not in m['subject'] and m['subject'].startswith('Appointment confirmed: ')
    assert 'Pay the consultation fee of ₹501' in user['text'] and 'screenshot' in user['text']
    assert 'Payment screenshot expected from the user' in astro['text']
    assert 'priya@example.com' in astro['text'] and '+919876543210' in astro['text']
    assert user['reply_to'][0] == 'sample.astrologer1@example.com' and astro['reply_to'][0] == 'priya@example.com'
    assert 'calendar.google.com' in user['html'] and out['token'] in user['text']
    assert out['token'] not in astro['text']
    assert _status(out['id']) == {'email_user': 'sent', 'email_astrologer': 'sent', 'whatsapp': 'manual'}


def test_tamil_booking_gets_a_tamil_email(client, sent):
    client.post('/api/bookings', json=body(lang='ta'))
    notify.process_outbox_once(now=NOW, send=lambda m: sent.append(m) or 'sent')
    user = next(m for m in sent if m['to'] == 'priya@example.com')
    astro = next(m for m in sent if m['to'] != 'priya@example.com')
    assert 'சந்திப்பு உறுதி' in user['subject'] and 'ஆஃப்லைன்' in user['text']
    assert astro['subject'].startswith('Appointment confirmed')


def test_partial_failure_is_retried_then_recorded(client, sent):
    bid = client.post('/api/bookings', json=body()).get_json()['id']

    def flaky(m):
        if 'astrologer' in m['to']:
            raise ConnectionError('provider down')
        return 'sent'

    notify.process_outbox_once(now=NOW, send=flaky)
    assert _status(bid)['email_user'] == 'sent' and _status(bid)['email_astrologer'] == 'retrying'
    later = NOW
    for minutes in (1, 4):
        later += timedelta(minutes=minutes)
        assert notify.process_outbox_once(now=later, send=flaky) == 1
    assert _status(bid)['email_astrologer'] == 'failed'
    assert notify.process_outbox_once(now=later + timedelta(days=1), send=flaky) == 0   # 3 attempts only
    # The booking itself stands.
    assert client.get(f'/api/bookings/{bid}?token={C.make_token(bid)}').get_json()['status'] == 'confirmed'


def test_next_due_lets_the_worker_sleep(client, sent):
    assert notify.next_due(NOW) is None                       # nothing queued: no polling needed
    client.post('/api/bookings', json=body())
    assert notify.next_due(NOW) == 0
    notify.process_outbox_once(now=NOW, send=lambda m: (_ for _ in ()).throw(OSError('down')))
    assert notify.next_due(NOW) == 60                          # first retry in a minute
    notify.process_outbox_once(now=NOW + timedelta(minutes=1), send=lambda m: 'sent')
    assert notify.next_due(NOW) is None


def test_cancel_notifies_both(client, sent):
    out = client.post('/api/bookings', json=body()).get_json()
    notify.process_outbox_once(now=NOW, send=lambda m: 'sent')
    client.post(f"/api/bookings/{out['id']}/cancel", json={'token': out['token']})
    notify.process_outbox_once(now=NOW, send=lambda m: sent.append(m) or 'sent')
    assert len(sent) == 2 and all(m['subject'].startswith('Appointment cancelled') for m in sent)
    assert all(m['attachments'][-1][1].decode().count('METHOD:CANCEL') == 1 for m in sent)
    assert _status(out['id'])['cancel_email_astrologer'] == 'sent'


def test_resend_request(monkeypatch):
    calls = []

    class Answer:
        status_code = 200

    monkeypatch.setenv('RESEND_API_KEY', 're_test')
    monkeypatch.setenv('EMAIL_FROM', 'HoroscopeGen <bookings@horoscopegen.in>')
    monkeypatch.setattr(notify.requests, 'post', lambda url, **kw: calls.append((url, kw)) or Answer())
    msg = {'to': 'priya@example.com', 'to_name': 'Priya', 'reply_to': ('astro@example.com', 'Astro'),
           'subject': 'Appointment confirmed', 'text': 'hi', 'html': '<p>hi</p>',
           'attachments': [('h.pdf', b'%PDF', 'application/pdf'), ('c.ics', b'BEGIN', 'text/calendar')]}
    assert notify.send_email(msg) == 'sent'
    url, kw = calls[0]
    assert url == 'https://api.resend.com/emails' and kw['headers']['Authorization'] == 'Bearer re_test'
    b = kw['json']
    assert b['from'] == 'HoroscopeGen <bookings@horoscopegen.in>' and b['to'] == ['priya@example.com']
    assert b['reply_to'] == ['astro@example.com']
    assert [a['filename'] for a in b['attachments']] == ['h.pdf', 'c.ics'] and b['attachments'][0]['content'] == 'JVBERg=='
    Answer.status_code = 403
    with pytest.raises(RuntimeError, match='Resend answered 403'):
        notify.send_email(msg)


def test_no_provider_logs_without_personal_data(client, monkeypatch, caplog):
    for k in ('RESEND_API_KEY', 'BREVO_API_KEY', 'SMTP_HOST'):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(notify, '_render_pdf', lambda b, l: b'%PDF')
    bid = client.post('/api/bookings', json=body()).get_json()['id']
    with caplog.at_level('INFO'):
        notify.process_outbox_once(now=NOW)
    assert _status(bid)['email_user'] == 'logged'
    assert 'priya@example.com' not in caplog.text and '9876543210' not in caplog.text
    assert 'When will I get a job' not in caplog.text


def test_purge_after_retention(client, monkeypatch):
    out = client.post('/api/bookings', json=body()).get_json()
    assert notify.purge_personal_data(NOW + timedelta(days=89)) == 0
    assert notify.purge_personal_data(NOW + timedelta(days=92)) == 1
    with D.engine().connect() as conn:
        row = conn.execute(D.bookings.select()).first()
    assert row.user_email == 'deleted@invalid' and row.questions == [] and row.horoscope_input == {}
    assert client.get(f"/api/bookings/{out['id']}/pdf?token={out['token']}").status_code == 410


def test_forget_one_booking(client):
    out = client.post('/api/bookings', json=body()).get_json()
    assert notify.forget_booking(out['id']) is True
    with D.engine().connect() as conn:
        row = conn.execute(D.bookings.select()).first()
    assert row.status == 'cancelled' and row.user_email == 'deleted@invalid' and row.purged_at
    assert slots_of(client)['09:30'] == 'available'
    assert notify.process_outbox_once(now=NOW, send=lambda m: 1 / 0) == 0      # queued e-mails dropped


# ── ADMIN ─────────────────────────────────────────────────────────────────────

def test_admin_preflight_allows_put_and_delete(client):
    ask = {'Origin': 'https://www.horoscopegen.in', 'Access-Control-Request-Method': 'PUT',
           'Access-Control-Request-Headers': 'content-type, x-admin-key'}
    rv = client.options('/api/admin/astrologers/1', headers=ask)
    assert rv.headers['Access-Control-Allow-Origin'] == 'https://www.horoscopegen.in'
    assert {'PUT', 'DELETE'} <= {m.strip() for m in rv.headers['Access-Control-Allow-Methods'].split(',')}
    assert 'x-admin-key' in rv.headers['Access-Control-Allow-Headers'].lower()
    rv = client.options('/api/bookings', headers=dict(ask, **{'Access-Control-Request-Method': 'POST'}))
    assert 'PUT' not in rv.headers['Access-Control-Allow-Methods']


def test_admin_needs_the_key(client, monkeypatch):
    assert client.get('/api/admin/astrologers').status_code == 401
    assert client.get('/api/admin/astrologers', headers={'X-Admin-Key': 'nope'}).status_code == 401
    monkeypatch.setenv('ADMIN_API_KEY', '')
    assert client.get('/api/admin/astrologers', headers=admin()).status_code == 503


def test_admin_adds_an_astrologer_with_hours(client):
    new = {'name': 'Test Devi', 'age': 40, 'phone': '+91 90000 00009', 'email': 'devi@example.com',
           'fee_inr': 300, 'hours': [{'weekday': 1, 'start': '10:00', 'end': '12:00'}]}
    r = client.post('/api/admin/astrologers', json=new, headers=admin())
    a = r.get_json()
    assert r.status_code == 201 and a['phone'] == '+919000000009' and a['hours'][0]['start'] == '10:00'
    s = slots_of(client, a['id'])
    assert [k for k, v in s.items() if v == 'available'] == ['10:00', '10:30', '11:00', '11:30']
    # Clearing the hours makes every slot green again.
    client.put(f"/api/admin/astrologers/{a['id']}", json={'hours': []}, headers=admin())
    assert set(slots_of(client, a['id']).values()) == {'available'}
    bad = client.post('/api/admin/astrologers', json=dict(new, age=12, phone='123'), headers=admin())
    assert bad.status_code == 422 and {'age', 'phone'} <= set(bad.get_json()['fields'])
    bad = client.put(f"/api/admin/astrologers/{a['id']}", json={'hours': [{'weekday': 1, 'start': '08:00', 'end': '10:00'}]},
                     headers=admin())
    assert bad.status_code == 422


def test_admin_blocks_a_day_and_sees_bookings(client):
    r = client.post('/api/admin/astrologers/1/blocks', json={'from': TUESDAY, 'reason': 'Leave'}, headers=admin())
    assert r.status_code == 201 and r.get_json()['blocks'][0]['to'] == TUESDAY
    assert set(slots_of(client).values()) == {'blocked'}
    assert set(slots_of(client, 1, '2026-10-21').values()) == {'available'}
    client.delete(f"/api/admin/blocks/{r.get_json()['blocks'][0]['id']}", headers=admin())
    bid = client.post('/api/bookings', json=body()).get_json()['id']
    listed = client.get('/api/admin/bookings', headers=admin()).get_json()['bookings']
    assert [b['id'] for b in listed] == [bid] and listed[0]['user_email'] == 'priya@example.com'
    assert client.post(f'/api/admin/bookings/{bid}/cancel', headers=admin()).get_json()['changed'] is True
    assert slots_of(client)['09:30'] == 'available'


def test_admin_deletes_an_astrologer(client, monkeypatch):
    bid = client.post('/api/bookings', json=body()).get_json()['id']
    client.post('/api/admin/astrologers/1/blocks', json={'from': '2026-10-25'}, headers=admin())
    assert client.delete('/api/admin/astrologers/1').status_code == 401              # needs the key
    r = client.delete('/api/admin/astrologers/1', headers=admin())
    assert r.status_code == 409 and r.get_json()['code'] == 'has_bookings'          # upcoming booking
    client.post(f'/api/admin/bookings/{bid}/cancel', headers=admin())
    r = client.delete('/api/admin/astrologers/1', headers=admin())
    assert r.status_code == 200 and r.get_json() == {'deleted': 1, 'bookings_removed': 1}
    assert 1 not in {a['id'] for a in client.get('/api/astrologers').get_json()['astrologers']}
    assert client.get('/api/astrologers/1').status_code == 404
    with D.engine().connect() as conn:
        assert conn.execute(D.bookings.select()).first() is None
        assert conn.execute(D.outbox.select()).first() is None
    assert client.delete('/api/admin/astrologers/1', headers=admin()).status_code == 404


def test_past_bookings_do_not_block_deleting(client, monkeypatch):
    client.post('/api/bookings', json=body())
    monkeypatch.setattr(D, 'utcnow', lambda: NOW + timedelta(days=3))              # the slot is over
    r = client.delete('/api/admin/astrologers/1', headers=admin())
    assert r.status_code == 200 and r.get_json()['bookings_removed'] == 1
