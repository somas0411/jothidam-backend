"""
Tests for what protects the public API: the request limits, the cap on the
body size, the CORS answers and the handling of input no visitor would send.

The expected numbers are written here as plain figures, not read from app.py,
so a change to a limit has to be made in both places on purpose:

  place search      20 a minute for one visitor
  horoscope         30 a minute for one visitor
  downloads         10 a minute for one visitor, the three routes together
  everything else  120 a minute for one visitor
  place look-ups    60 a minute for all visitors together
  request body      64 KB

No test here reaches the network: the place look-up is replaced by a stub
that counts its calls.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import astro_engine as A          # noqa: E402

SITE = 'https://www.horoscopegen.in'
BODY = {'name': 'Sample Native', 'dob': '1998-03-06', 'tob': '01:37', 'pob': 'Delhi',
        'lat': 28.6139, 'lon': 77.2090, 'tz': 'Asia/Kolkata'}
NO_COORDINATES = {k: v for k, v in BODY.items() if k not in ('lat', 'lon')}
TOO_MANY = {'error': 'Too many requests. Please wait a minute and try again.'}


def visitor(ip):
    """Headers as the hosting platform sends them for a visitor at this address."""
    return {'CF-Connecting-IP': ip}


@pytest.fixture()
def lookups(monkeypatch):
    """Stand-in for the Nominatim look-up; the list holds every query it was asked."""
    import app as app_module
    asked = []

    def fake(query, limit=5):
        asked.append(query)
        return [{'name': query, 'lat': 13.0827, 'lon': 80.2707, 'tz': 'Asia/Kolkata'}]

    monkeypatch.setattr(app_module, 'geocode', fake)
    monkeypatch.setattr(A, 'geocode', fake)
    return asked


@pytest.fixture()
def api(lookups):
    """A client with the request limits on and every counter at zero."""
    import app as app_module
    app_module.limiter.enabled = True
    app_module.limiter.reset()
    yield app_module.app.test_client()
    app_module.limiter.reset()


def statuses(responses):
    return [r.status_code for r in responses]


# ── LIMITS FOR ONE VISITOR ────────────────────────────────────────────────────

def test_place_search_is_limited_to_20_a_minute(api):
    got = [api.get('/api/geocode?q=Chennai', headers=visitor('203.0.113.7')) for _ in range(22)]
    assert statuses(got) == [200] * 20 + [429, 429]
    refused = got[20]
    assert refused.get_json() == TOO_MANY
    assert int(refused.headers['Retry-After']) > 0


def test_horoscope_is_limited_to_30_a_minute(api):
    # An empty body is answered with 400 at once, and still counts as a request.
    got = [api.post('/api/horoscope', json={}, headers=visitor('203.0.113.7')) for _ in range(31)]
    assert statuses(got) == [400] * 30 + [429]
    assert got[30].get_json() == TOO_MANY


def test_the_three_downloads_share_10_a_minute(api):
    routes = ['/api/download/excel', '/api/download/pdf', '/api/download/json']
    got = [api.post(routes[i % 3], json={}, headers=visitor('203.0.113.7')) for i in range(10)]
    assert statuses(got) == [400] * 10
    for route in routes:
        assert api.post(route, json={}, headers=visitor('203.0.113.7')).status_code == 429
    # The download limit is separate from the horoscope limit.
    assert api.post('/api/horoscope', json=BODY, headers=visitor('203.0.113.7')).status_code == 200


def test_other_routes_are_limited_to_120_a_minute(api):
    got = [api.get('/api/options', headers=visitor('203.0.113.7')) for _ in range(121)]
    assert statuses(got) == [200] * 120 + [429]


def test_health_checks_are_never_limited(api):
    for route in ('/health', '/api/ping'):
        assert statuses([api.get(route, headers=visitor('203.0.113.7')) for _ in range(300)]) == [200] * 300


def test_a_refused_request_does_no_work(api, lookups):
    for _ in range(25):
        api.get('/api/geocode?q=Chennai', headers=visitor('203.0.113.7'))
    assert len(lookups) == 20


# ── WHO COUNTS AS ONE VISITOR ─────────────────────────────────────────────────

def use_up_place_search(api, headers, environ=None):
    environ = environ or {}
    for _ in range(20):
        assert api.get('/api/geocode?q=Chennai', headers=headers, environ_base=environ).status_code == 200
    assert api.get('/api/geocode?q=Chennai', headers=headers, environ_base=environ).status_code == 429


def test_each_visitor_is_counted_separately(api):
    use_up_place_search(api, visitor('203.0.113.7'))
    assert api.get('/api/geocode?q=Chennai', headers=visitor('203.0.113.8')).status_code == 200


def test_a_made_up_forwarded_address_does_not_reset_the_count(api):
    use_up_place_search(api, visitor('203.0.113.7'))
    for fake in ('1.2.3.4', '5.6.7.8, 9.9.9.9'):
        headers = dict(visitor('203.0.113.7'), **{'X-Forwarded-For': fake})
        assert api.get('/api/geocode?q=Chennai', headers=headers).status_code == 429


def test_without_the_platform_header_the_forwarded_address_is_used(api):
    use_up_place_search(api, {'X-Forwarded-For': '203.0.113.7, 10.0.0.1'})
    assert api.get('/api/geocode?q=Chennai', headers={'X-Forwarded-For': '203.0.113.7'}).status_code == 429
    assert api.get('/api/geocode?q=Chennai', headers={'X-Forwarded-For': '203.0.113.8, 10.0.0.1'}).status_code == 200


def test_with_no_headers_the_connecting_address_is_used(api):
    use_up_place_search(api, {}, environ={'REMOTE_ADDR': '203.0.113.7'})
    assert api.get('/api/geocode?q=Chennai', environ_base={'REMOTE_ADDR': '203.0.113.8'}).status_code == 200


def test_ipv6_visitors_are_counted_by_their_64_network(api):
    use_up_place_search(api, visitor('2001:db8:1:2::1'))
    # Same /64, another address in it: the same visitor.
    assert api.get('/api/geocode?q=Chennai', headers=visitor('2001:db8:1:2:aaaa:bbbb:cccc:dddd')).status_code == 429
    # The next /64: someone else.
    assert api.get('/api/geocode?q=Chennai', headers=visitor('2001:db8:1:3::1')).status_code == 200


def test_an_ipv4_address_written_as_ipv6_is_the_same_visitor(api):
    use_up_place_search(api, visitor('203.0.113.7'))
    assert api.get('/api/geocode?q=Chennai', headers=visitor('::ffff:203.0.113.7')).status_code == 429


def test_text_that_is_not_an_address_is_one_visitor(api):
    use_up_place_search(api, visitor('not-an-address'))
    assert api.get('/api/geocode?q=Chennai', headers=visitor('something else')).status_code == 429
    assert api.get('/api/geocode?q=Chennai', headers=visitor('203.0.113.8')).status_code == 200


# ── PLACE LOOK-UPS, ALL VISITORS TOGETHER ─────────────────────────────────────

def test_all_visitors_together_get_60_place_lookups_a_minute(api, lookups):
    # 4 visitors, 15 searches each: every one within the visitor's own 20.
    for n in range(4):
        got = [api.get('/api/geocode?q=Madurai', headers=visitor(f'198.51.100.{n}')) for _ in range(15)]
        assert statuses(got) == [200] * 15
    assert len(lookups) == 60
    late = api.get('/api/geocode?q=Madurai', headers=visitor('198.51.100.200'))
    assert late.status_code == 429 and late.get_json() == TOO_MANY and late.headers['Retry-After'] == '60'
    assert len(lookups) == 60


def test_one_visitor_cannot_use_up_the_place_lookups_of_the_others(api, lookups):
    got = [api.get('/api/geocode?q=Madurai', headers=visitor('203.0.113.7')) for _ in range(200)]
    assert statuses(got).count(200) == 20
    # 20 of the 60 are gone, so 40 are left for everyone else.
    others = [api.get('/api/geocode?q=Madurai', headers=visitor(f'198.51.100.{n}')) for n in range(41)]
    assert statuses(others) == [200] * 40 + [429]
    assert len(lookups) == 60


def test_a_horoscope_without_coordinates_counts_as_a_place_lookup(api, lookups):
    for n in range(3):
        for _ in range(20):
            api.get('/api/geocode?q=Madurai', headers=visitor(f'198.51.100.{n}'))
    assert len(lookups) == 60
    someone = visitor('192.0.2.1')
    for route in ('/api/horoscope', '/api/download/pdf', '/api/download/excel', '/api/download/json'):
        assert api.post(route, json=NO_COORDINATES, headers=someone).status_code == 429
    assert len(lookups) == 60
    # With coordinates no look-up is needed, so the shared budget does not apply.
    assert api.post('/api/horoscope', json=BODY, headers=someone).status_code == 200


def test_a_horoscope_without_coordinates_looks_the_place_up_once(api, lookups):
    rv = api.post('/api/horoscope', json=NO_COORDINATES, headers=visitor('192.0.2.1'))
    assert rv.status_code == 200 and lookups == ['Delhi']
    assert rv.get_json()['meta']['lat'] == 13.0827      # the stub's answer


def test_a_search_too_short_to_look_up_spends_nothing(api, lookups):
    assert api.get('/api/geocode?q=C', headers=visitor('192.0.2.1')).get_json() == {'results': []}
    assert lookups == []


# ── SWITCHING THE LIMITS OFF ──────────────────────────────────────────────────

def test_with_the_limits_off_nothing_is_refused(api, lookups):
    import app as app_module
    app_module.limiter.enabled = False
    got = [api.get('/api/geocode?q=Chennai', headers=visitor('203.0.113.7')) for _ in range(80)]
    assert statuses(got) == [200] * 80 and len(lookups) == 80


@pytest.mark.parametrize('value,on', [(None, True), ('true', True), ('1', True), ('', True), ('anything', True),
                                      ('false', False), ('False', False), (' off ', False), ('0', False), ('no', False)])
def test_rate_limit_enabled_setting(monkeypatch, value, on):
    import app as app_module
    if value is None:
        monkeypatch.delenv('RATE_LIMIT_ENABLED', raising=False)
    else:
        monkeypatch.setenv('RATE_LIMIT_ENABLED', value)
    assert app_module._limits_enabled() is on


# ── CORS ──────────────────────────────────────────────────────────────────────

def preflight(api, origin, method='POST'):
    return api.options('/api/horoscope', headers={
        'Origin': origin, 'Access-Control-Request-Method': method,
        'Access-Control-Request-Headers': 'content-type'})


@pytest.mark.parametrize('origin', ['https://horoscopegen.in', SITE, 'https://horoscopesgen.netlify.app'])
def test_the_website_may_read_the_answers(api, origin):
    rv = api.post('/api/horoscope', json=BODY, headers={'Origin': origin})
    assert rv.status_code == 200
    assert rv.headers['Access-Control-Allow-Origin'] == origin
    assert 'Origin' in rv.headers['Vary']
    exposed = [h.strip() for h in rv.headers['Access-Control-Expose-Headers'].split(',')]
    assert set(exposed) == {'Content-Disposition', 'Retry-After'}


@pytest.mark.parametrize('origin', ['https://evil.example', 'http://horoscopegen.in', 'https://horoscopegen.in.evil.example',
                                    'https://www.horoscopegen.in.evil.example', 'null'])
def test_another_website_is_given_no_permission(api, origin):
    rv = api.post('/api/horoscope', json=BODY, headers={'Origin': origin})
    assert 'Access-Control-Allow-Origin' not in rv.headers
    assert 'Access-Control-Allow-Origin' not in preflight(api, origin).headers


def test_a_request_with_no_origin_gets_no_cors_headers(api):
    rv = api.get('/api/ping')
    assert rv.status_code == 200
    assert not [name for name, _ in rv.headers if name.startswith('Access-Control-')]


def test_preflight_answer(api):
    rv = preflight(api, SITE)
    assert rv.status_code == 200
    assert rv.headers['Access-Control-Allow-Origin'] == SITE
    assert {m.strip() for m in rv.headers['Access-Control-Allow-Methods'].split(',')} == {'GET', 'POST', 'OPTIONS'}
    assert rv.headers['Access-Control-Allow-Headers'].lower() == 'content-type'
    assert rv.headers['Access-Control-Max-Age'] == '600'


def test_preflights_are_not_counted(api):
    asking = dict(visitor('203.0.113.7'), **{'Origin': SITE, 'Access-Control-Request-Method': 'GET'})
    # A route with a limit of its own (20) and one under the general limit (120).
    for route, times in (('/api/geocode', 50), ('/api/options', 150)):
        assert statuses([api.options(route, headers=asking) for _ in range(times)]) == [200] * times
    assert statuses([api.get('/api/options', headers=visitor('203.0.113.7')) for _ in range(120)]) == [200] * 120
    use_up_place_search(api, visitor('203.0.113.7'))


def test_the_website_can_read_a_refusal(api):
    """A 429 or 413 without the CORS header would reach the page as a bare network error."""
    headers = dict(visitor('203.0.113.7'), Origin=SITE)
    for _ in range(30):
        api.post('/api/horoscope', json={}, headers=headers)
    refused = api.post('/api/horoscope', json=BODY, headers=headers)
    assert refused.status_code == 429 and refused.headers['Access-Control-Allow-Origin'] == SITE
    big = api.post('/api/download/pdf', data=json.dumps(dict(BODY, pad='x' * 70_000)),
                   content_type='application/json', headers={'Origin': SITE})
    assert big.status_code == 413 and big.headers['Access-Control-Allow-Origin'] == SITE


# ── BODY SIZE ─────────────────────────────────────────────────────────────────

def padded(size):
    """A valid body made exactly `size` bytes long with an ignored field."""
    base = len(json.dumps(dict(BODY, pad='')))
    data = json.dumps(dict(BODY, pad='x' * (size - base)))
    assert len(data.encode()) == size
    return data


@pytest.mark.parametrize('route', ['/api/horoscope', '/api/download/excel', '/api/download/pdf', '/api/download/json'])
def test_a_body_over_64_kb_is_refused(api, route):
    rv = api.post(route, data=padded(64 * 1024 + 1), content_type='application/json')
    assert rv.status_code == 413
    assert rv.get_json() == {'error': 'The request is too large.'}


def test_a_body_of_exactly_64_kb_is_accepted(api):
    rv = api.post('/api/horoscope', data=padded(64 * 1024), content_type='application/json')
    assert rv.status_code == 200 and rv.get_json()['meta']['name'] == 'Sample Native'


def test_the_largest_real_body_is_far_below_the_cap():
    """Every field at its longest, every optional input given, the most events allowed."""
    import enrich as E
    events = [{'type': max(E.EVENT_TOPIC, key=len), 'year': 2020}] * E.MAX_EVENTS
    life = {'marital_status': max(E.MARITAL_STATUS, key=len), 'marriage_year': 2012, 'children_count': E.MAX_COUNT,
            'first_child_birth_year': 2014, 'elder_siblings': E.MAX_COUNT, 'younger_siblings': E.MAX_COUNT,
            'work_type': max(E.WORK_TYPES, key=len), 'lives_abroad': False, 'events': events}
    body = dict(BODY, name='அ' * 80, pob='அ' * 120, gender='x' * 20, utcOffset=-12.75, ayanamsha='yukteshwar',
                node='mean', lang='bi', chartStyle='north', ai='brief', tobUncertaintyMin=E.MAX_TOB_UNCERTAINTY_MIN,
                life=life)
    assert len(json.dumps(body).encode()) < 64 * 1024 / 4


# ── INPUT NO VISITOR WOULD SEND ───────────────────────────────────────────────

@pytest.mark.parametrize('body,message', [
    ([1, 2], 'The request body must be a JSON object.'),
    ('text', 'The request body must be a JSON object.'),
    (5, 'The request body must be a JSON object.'),
    (dict(BODY, dob='0001-01-01'), 'That date is outside the range this service can calculate.'),
    (dict(BODY, dob='9999-12-31'), 'That date is outside the range this service can calculate.'),
    (dict(BODY, ayanamsha=[1]), 'Unknown ayanamsha "[1]".'),
    (dict(BODY, ayanamsha={'a': 1}), 'Unknown ayanamsha "{\'a\': 1}".'),
])
@pytest.mark.parametrize('route', ['/api/horoscope', '/api/download/pdf'])
def test_bad_input_is_a_400_with_a_message_not_a_500(api, route, body, message):
    rv = api.post(route, json=body)
    assert rv.status_code == 400 and rv.get_json() == {'error': message}


def test_a_date_the_tables_cannot_reach_is_a_400(api):
    """Born in 2990: the birth chart can be drawn, the tables of later years cannot."""
    for route in ('/api/download/excel', '/api/download/json'):
        rv = api.post(route, json=dict(BODY, dob='2990-01-01'))
        assert rv.status_code == 400
        assert rv.get_json() == {'error': 'That date is outside the range this service can calculate.'}


def test_no_body_and_empty_body_ask_for_the_birth_details(api):
    for kwargs in ({}, {'json': {}}, {'data': 'not json', 'content_type': 'application/json'}):
        rv = api.post('/api/horoscope', **kwargs)
        assert rv.status_code == 400
        assert rv.get_json() == {'error': 'Name, date, time and place of birth are required.'}


def test_ayanamsha_left_out_or_empty_is_lahiri(api):
    for body in (BODY, dict(BODY, ayanamsha=None), dict(BODY, ayanamsha='')):
        assert api.post('/api/horoscope', json=body).get_json()['meta']['ayanamsha_key'] == 'lahiri'
    assert api.post('/api/horoscope', json=dict(BODY, ayanamsha='KP')).get_json()['meta']['ayanamsha_key'] == 'kp'


# ── ERRORS AND HEADERS ────────────────────────────────────────────────────────

def test_unknown_address_and_wrong_method_answer_in_json(api):
    missing = api.get('/no-such-page')
    assert missing.status_code == 404 and missing.get_json() == {'error': 'Not found.'}
    wrong = api.get('/api/horoscope')
    assert wrong.status_code == 405
    assert wrong.get_json() == {'error': 'This address does not accept that kind of request.'}
    assert {m.strip() for m in wrong.headers['Allow'].split(',')} == {'POST', 'OPTIONS'}


def test_every_answer_says_nosniff(api):
    answers = [api.get('/health'), api.get('/api/ping'), api.get('/api/options'), api.get('/api/geocode?q=Chennai'),
               api.post('/api/horoscope', json=BODY), api.post('/api/horoscope', json={}),
               api.post('/api/download/pdf', json=BODY), api.get('/no-such-page')]
    assert [a.headers.get('X-Content-Type-Options') for a in answers] == ['nosniff'] * len(answers)


def test_answers_holding_birth_details_are_not_to_be_cached(api):
    for route in ('/api/horoscope', '/api/download/pdf', '/api/download/json'):
        assert api.post(route, json=BODY).headers['Cache-Control'] == 'no-store'
    assert 'Cache-Control' not in api.get('/api/ping').headers


def test_a_download_is_still_a_download(api):
    rv = api.post('/api/download/pdf', json=BODY, headers={'Origin': SITE})
    assert rv.status_code == 200 and rv.data[:5] == b'%PDF-'
    assert rv.headers['Content-Type'] == 'application/pdf'
    assert rv.headers['Content-Disposition'] == 'attachment; filename="HoroscopeGen_Sample_Native.pdf"'
    assert int(rv.headers['Content-Length']) == len(rv.data)


# ── HOURLY LIMITS ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize('route,per_minute,per_hour', [
    ('/api/horoscope', 30, 300), ('/api/download/pdf', 10, 100), ('/api/geocode?q=Chennai', 20, 200)])
def test_the_hourly_limit_holds_when_the_minute_limit_is_respected(api, monkeypatch, route, per_minute, per_hour):
    """Send the full allowance of each minute, minute after minute, on a clock moved by hand."""
    import time
    clock = [time.time()]
    monkeypatch.setattr(time, 'time', lambda: clock[0])
    send = (lambda: api.get(route, headers=visitor('203.0.113.7'))) if 'geocode' in route else \
           (lambda: api.post(route, json={}, headers=visitor('203.0.113.7')))
    allowed = 0
    for minute in range(per_hour // per_minute):
        got = statuses([send() for _ in range(per_minute)])
        assert 429 not in got, f'refused in minute {minute + 1}'
        allowed += len(got)
        clock[0] += 61
    assert allowed == per_hour
    assert send().status_code == 429            # a new minute, but the hour is used up
    clock[0] += 3600
    assert send().status_code != 429            # an hour later
