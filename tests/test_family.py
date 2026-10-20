"""Tests for the family reading: family_engine, the /api/family routes and the reports."""
import io
from datetime import datetime

import openpyxl
import pytest

import astro_engine as A
import family_engine as F
from astro_engine import InputError, compute

PLACE = {'pob': 'Chennai', 'lat': 13.0827, 'lon': 80.2707, 'tz': 'Asia/Kolkata'}
PEOPLE = [
    ('Self', 'Anchor', '1980-06-15', '09:10', 'male'),
    ('Spouse', 'Wife', '1984-02-01', '17:45', 'female'),
    ('Son', 'Boy', '2012-11-20', '05:30', 'male'),
    ('Daughter', 'Girl', '2016-03-03', '23:15', 'female'),
    ('Father', 'Dad', '1950-01-10', '04:00', 'male'),
    ('Mother', 'Mum', '1955-07-07', '12:00', 'female'),
]
NOW = datetime(2026, 10, 20, 12, 0)
BANNED = ('marak', 'ayur', 'longevity', 'lifespan', 'life span', 'death', 'mrityu', 'alpayu', 'alive', 'died',
          'widow', 'kill', 'fatal', 'surviv', 'length of life', 'unlucky for')


def _res(name, dob, tob, gender):
    return compute(name=name, dob=dob, tob=tob, gender=gender, **PLACE)


@pytest.fixture(scope='module')
def six():
    return [{'relation': r, 'res': _res(n, d, t, g)} for r, n, d, t, g in PEOPLE]


@pytest.fixture(scope='module')
def result6(six):
    return F.family(six, now=NOW)


@pytest.fixture(scope='module')
def result2(six):
    return F.family(six[:2], {'years': 3}, now=NOW)


# ── membership rules ──────────────────────────────────────────────────────────

@pytest.mark.parametrize('relations, message', [
    ([], 'At least 2'),
    (['Self'], 'At least 2'),
    (['Self', 'Son', 'Son', 'Son', 'Son', 'Son', 'Son'], 'At most 6'),
    (['Self', 'Self'], 'Exactly one'),
    (['Son', 'Daughter'], 'Exactly one'),
    (['Self', 'Spouse', 'Spouse'], 'Spouse'),
    (['Self', 'Father', 'Father'], 'Father'),
    (['Self', 'Grandfather', 'Grandfather', 'Grandfather'], 'Grandfather'),
    (['Self', 'Cousin'], 'Unknown relation'),
])
def test_bad_membership_is_refused(relations, message):
    with pytest.raises(InputError, match=message):
        F.check_relations(relations)


def test_two_grandfathers_and_six_members_are_allowed():
    F.check_relations(['Self', 'Grandfather', 'Grandfather', 'Grandmother', 'Grandmother', 'Spouse'])


def test_gender_follows_the_relation():
    assert F.relation_gender('Mother') == 'female'
    assert F.relation_gender('Grandson') == 'male'
    assert F.relation_gender('Self', 'female') == 'female'
    assert F.relation_gender('Other', 'x') == ''


def test_options_are_checked():
    assert F.clean_options({}) == {'years': 10, 'sandhi_months': 12}
    with pytest.raises(InputError):
        F.clean_options({'years': 21})
    with pytest.raises(InputError):
        F.clean_options({'sandhi_months': 0})


# ── engine ────────────────────────────────────────────────────────────────────

def test_six_members(result6):
    s = result6['sections']
    assert result6['anchor'] == 'Anchor'
    assert len(s['A']['members']) == 6
    assert len(s['C']['pairs']) == 6 * 5 // 2
    assert len(s['B']['houses']) == 7 * 2                    # 7 family houses in D1 and D12
    assert {h['chart'] for h in s['B']['houses']} == {'D1', 'D12'}
    assert len(s['B']['read_back']) == 5
    assert len(s['E']['months']) == 120


def test_two_members(result2):
    s = result2['sections']
    assert len(s['C']['pairs']) == 1
    assert len(s['E']['months']) == 36
    assert result2['settings']['years'] == 3


def test_anchor_comes_first_whatever_the_order(six):
    res = F.family([six[2], six[0]], now=NOW)
    assert res['members'][0]['relation'] == 'Self'


def test_timeline_months_are_contiguous_and_cover_the_range(result6):
    months = result6['sections']['E']['months']
    assert months[0]['month'] == '2026-10' and months[-1]['month'] == '2036-09'
    for a, b in zip(months, months[1:]):
        ya, ma = map(int, a['month'].split('-'))
        yb, mb = map(int, b['month'].split('-'))
        assert (yb * 12 + mb) - (ya * 12 + ma) == 1
    windows = result6['sections']['E']['windows']
    assert sum(w['months'] for w in windows) == len(months)
    assert windows[0]['from'] == months[0]['month'] and windows[-1]['to'] == months[-1]['month']
    for a, b in zip(windows, windows[1:]):
        assert a['status'] != b['status']
    assert {m['status'] for m in months} <= {'supportive', 'mixed', 'pressured'}


def test_family_status_rule():
    good = {'period': 'good', 'saturn': 'none', 'jupiter_good': True}
    hard = {'period': 'difficult', 'saturn': 'none', 'jupiter_good': False}
    sade = {'period': 'good', 'saturn': 'sade sati - 2nd phase', 'jupiter_good': True}
    ardha = {'period': 'good', 'saturn': 'ardhashtama', 'jupiter_good': True}
    kid = lambda st: dict(st, weight=0.5)
    assert F.family_status([good, good])[0] == 'supportive'
    assert F.family_status([good, hard])[0] == 'mixed'
    assert F.family_status([hard, dict(sade, period='mixed')])[0] == 'pressured'
    assert F.family_status([hard, sade])[0] == 'mixed'                 # a good period offsets sade sati
    assert F.family_status([good, ardha])[0] == 'supportive'           # ardhashtama alone is not pressure
    assert F.family_status([good] * 4 + [hard] * 2)[0] != 'pressured'  # 2 of 6 is under half
    assert F.family_status([good] * 3 + [hard] * 3)[0] == 'pressured'
    # two parents and two young children
    assert F.family_status([good, good, kid(hard), kid(hard)])[0] != 'pressured'   # children alone: weight 1
    assert F.family_status([hard, good, kid(hard), kid(good)])[0] == 'pressured'   # a parent and a child: 1.5
    assert F.family_status([sade, good, kid(good), kid(good)])[0] == 'supportive'   # one parent alone: 1.0
    assert F.family_status([good, good, kid(hard), kid(good)])[0] == 'supportive'
    status, counts = F.family_status([good, good, kid(hard), kid(hard)])
    assert counts == {'good': 2.0, 'pressured': 1.0, 'jupiter_favourable': 2.0, 'weight': 3.0}


def test_eleventh_house_offsets_a_dusthana():
    m = F.Member(0, 'Self', _res('Meena', '2016-12-09', '13:48', 'male'))   # Meena lagna
    assert m.c.lagna_sign == 11
    assert m.lord_quality('Saturn')[0] == 'neutral'                     # owns 11 and 12
    assert m.lord_quality('Venus')[0] == 'difficult'                    # owns 3 and 8
    assert m.lord_quality('Jupiter')[0] == 'good'                       # owns 1 and 10
    assert m.lord_quality('Mars')[0] == 'good'                          # owns 2 and 9


def test_minors_weigh_half(six):
    son = F.Member(0, 'Son', six[2]['res'])                             # born 2012
    assert son.weight_at(datetime(2026, 1, 1)) == F.MINOR_WEIGHT
    assert son.weight_at(datetime(2031, 1, 1)) == 1.0


def test_axes():
    assert F.axis_of(0, 0)[2] == (1, 1)
    assert F.axis_of(0, 6)[2] == (7, 7)
    assert F.axis_of(0, 4)[2] == (5, 9)
    assert F.axis_of(0, 7)[2] == (6, 8)
    assert F.axis_of(0, 1)[2] == (2, 12)
    assert F.axis_of(0, 3)[2] == (4, 10)
    assert F.AXIS_CLASS[(4, 10)] == 'strained'
    assert all(F.AXIS_CLASS[k] for k in F.AXIS_NAME)


@pytest.mark.parametrize('relation, houses', [
    ('Father', [9]), ('Mother', [4]), ('Son', [5]), ('Daughter', [5]), ('Father-in-law', [3]),
    ('Mother-in-law', [10]), ('Grandfather', [5, 7]), ('Grandmother', [12, 12]), ('Grandson', [9]),
    ('Granddaughter', [9]), ('Other', []),
])
def test_relation_houses(six, relation, houses):
    anchor = F.Member(0, 'Self', six[0]['res'])
    other = F.Member(1, relation, six[2]['res'])
    assert [h for h, *_ in F.relation_houses(anchor, other)] == houses


def test_spouse_and_sibling_houses(six):
    anchor = F.Member(0, 'Self', six[0]['res'])                         # male, born 1980
    spouse = F.relation_houses(anchor, F.Member(1, 'Spouse', six[1]['res']))
    assert spouse == [(7, '7th: spouse', 'Venus', 'D9')]
    younger = F.relation_houses(anchor, F.Member(2, 'Brother', six[2]['res']))     # born 2012
    elder = F.relation_houses(anchor, F.Member(3, 'Sister', six[4]['res']))        # born 1950
    assert younger[0][0] == 3 and elder[0][0] == 11


def test_read_back_for_a_child_of_a_male_anchor(result6):
    rows = {r['member']: r for r in result6['sections']['B']['read_back']}
    assert rows['Boy']['house'] == 9
    assert rows['Dad']['house'] == 5
    assert rows['Wife']['house'] == 7


def test_overlays_are_by_sign(result6, six):
    for o in result6['sections']['C']['overlays']:
        assert o['kind'] in ('support', 'needs care', 'information')
        if o['kind'] == 'needs care':
            assert o['planet'] in F.PRESSURE_PLANETS


def test_strained_pairs_read_as_care(result6):
    for p in result6['sections']['C']['pairs']:
        for k in ('lagna', 'moon'):
            if p[f'{k}_reading'] == 'strained':
                assert p[f'{k}_care'].startswith('needs care in ')
            else:
                assert p[f'{k}_care'] == ''


def test_sandhi_pairs_are_within_the_limit(result6):
    for x in result6['sections']['E']['sandhi']:
        assert x['months_apart'] <= 12


def test_flat_tables(result6):
    t = F.tables(result6)
    assert t['sheets'][0] == 'AI_FamilyReadMe' and t['sheets'][-1] == 'AI_FamilyRules'
    for sheet in t['sheets']:
        cols = [c['name'] for c in t['columns'][sheet]]
        for row in t['tables'][sheet]:
            assert list(row) == cols


def test_nothing_about_length_of_life(result6):
    def texts(value):
        if isinstance(value, dict):
            for k, v in value.items():
                yield from texts(k)
                yield from texts(v)
        elif isinstance(value, (list, tuple)):
            for v in value:
                yield from texts(v)
        elif isinstance(value, str):
            yield value
    seen = list(texts(F.public(result6))) + list(texts(F.tables(result6)))
    assert len(seen) > 500
    for text in seen:
        assert not any(word in text.lower() for word in BANNED), text


def test_charts_are_left_alone(six):
    import copy
    before = copy.deepcopy([m['res']['vedic']['planets'] for m in six])
    F.family(six, now=NOW)
    assert [m['res']['vedic']['planets'] for m in six] == before


# ── reports ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('lang', ['en', 'ta', 'bi', 'te'])
def test_excel(result6, lang):
    from excel_generator import generate_family_excel
    wb = openpyxl.load_workbook(io.BytesIO(generate_family_excel(result6, lang)))
    assert wb.sheetnames[:6] == ['Family', 'Relations', 'Pairs', 'Patterns', 'Transits', 'Rules']
    assert 'AI_FamilyMonths' in wb.sheetnames and 'AI_FamilyRules' in wb.sheetnames


@pytest.mark.parametrize('lang', ['en', 'ta'])
def test_pdf(result6, lang):
    from pdf_generator import generate_family_pdf
    data = generate_family_pdf(result6, lang)
    assert data[:5] == b'%PDF-' and len(data) > 20000


# ── routes ────────────────────────────────────────────────────────────────────

def _body(n=3, **extra):
    members = [{'relation': r, 'name': nm, 'dob': d, 'tob': t, 'gender': g, **PLACE}
               for r, nm, d, t, g in PEOPLE[:n]]
    return {'members': members, 'lang': 'en', **extra}


@pytest.fixture()
def client(monkeypatch):
    import app as app_module

    def no_network(*args, **kwargs):
        raise AssertionError('a test tried to look a place up')

    monkeypatch.setattr(app_module, 'geocode', no_network)
    monkeypatch.setattr(A, 'geocode', no_network)
    return app_module.app.test_client()


def test_route_family(client):
    rv = client.post('/api/family', json=_body(3, years=5))
    assert rv.status_code == 200, rv.get_json()
    out = rv.get_json()
    assert out['anchor'] == 'Anchor'
    assert len(out['charts']) == 3 and 'd1' in out['charts'][0]
    assert len(out['sections']['E']['months']) == 60
    assert '_people' not in out


def test_route_family_ai(client):
    rv = client.post('/api/family', json=_body(2, ai=True))
    assert rv.status_code == 200
    assert 'AI_FamilyMonths' in rv.get_json()['ai']['tables']


@pytest.mark.parametrize('body, message', [
    ({'members': 'x'}, 'must be a list'),
    ({'members': []}, 'At least 2'),
])
def test_route_family_bad_input(client, body, message):
    rv = client.post('/api/family', json=body)
    assert rv.status_code == 400 and message in rv.get_json()['error']


def test_route_family_needs_names(client):
    body = _body(2)
    body['members'][1]['name'] = ''
    rv = client.post('/api/family', json=body)
    assert rv.status_code == 400 and 'name of member 2' in rv.get_json()['error']


def test_route_family_too_many(client):
    body = _body(6)
    body['members'].append(dict(body['members'][2], name='Extra'))
    rv = client.post('/api/family', json=body)
    assert rv.status_code == 400 and 'At most 6' in rv.get_json()['error']


def test_route_family_downloads(client):
    rv = client.post('/api/download/family/excel', json=_body(2))
    assert rv.status_code == 200
    assert 'Family_Anchor_' in rv.headers['Content-Disposition']
    openpyxl.load_workbook(io.BytesIO(rv.data))
    rv = client.post('/api/download/family/pdf', json=_body(2))
    assert rv.status_code == 200 and rv.data[:5] == b'%PDF-'
