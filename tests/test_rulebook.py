"""
Tests for rulebook.py (rule-book readings with their periods) and the
/api/predictions route.

Reference cases are worked by hand from the rule texts in data/rulebook:
  * Kataka lagna, Jupiter and Mars in Dhanus (6th): Jupiter is the 6th lord in
    its own sign in the 6th, so OE-01 (career change in the periods of
    Jupiter and of the planets with it or in its star) and DU-03 apply.
  * Kataka lagna, Saturn exalted in Thula (4th) is the 7th lord: SAT-11.
  * Mesha lagna, Saturn (10th lord) exalted in Thula: RY-04, own business
    when direct, employment when retrograde.
"""
import json
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import astro_engine as A          # noqa: E402
import rulebook as RB             # noqa: E402
from test_enrich import NOW, S, chart   # noqa: E402

FORBIDDEN = ('channel', 'youtube', '"source"')
POLICY = RB.BANNED


def with_dasa(res, now=NOW):
    moon = next(p for p in res['vedic']['planets'] if p['name'] == 'Moon')
    res['vedic']['dasa'] = A.vimshottari(moon['lon'], res['meta']['local_dt'], now, levels=3)
    return res


def rows_of(lagna, retro=(), **signs):
    res = with_dasa(chart(lagna, **signs))
    for p in res['vedic']['planets']:
        if p['name'] in retro:
            p['retro'] = True
    return RB.evaluate(res, NOW)


def ids(rows):
    return {r['rule_id'] for r in rows}


# ── the rule texts ────────────────────────────────────────────────────────────

def test_rule_files_carry_no_source_or_author():
    files = sorted(Path(RB.DATA_DIR).glob('*.json'))
    assert len(files) == 23
    for f in files:
        text = f.read_text(encoding='utf-8')
        low = text.lower()
        assert not any(w in low for w in FORBIDDEN), f.name
        data = json.loads(text)
        assert 'source' not in data, f.name
        assert not POLICY.search(text), f.name        # nothing about death or length of life


def test_rule_ids_are_unique_and_known():
    seen = [r[0] for r in RB.RULES]
    assert len(seen) == len(set(seen))
    assert all(r[2] in RB.TOPICS for r in RB.RULES)


# ── hand-worked cases ─────────────────────────────────────────────────────────

def test_own_sign_6th_lord_in_6th_brings_career_change():
    rows = rows_of('Kataka', Jupiter='Dhanu', Mars='Dhanu', Moon='Kumbha', Saturn='Thula', Sun='Thula',
                   Mercury='Vrischika', Venus='Vrischika', Rahu='Rishabha', Ketu='Vrischika')
    oe = [r for r in rows if r['rule_id'] == 'OE-01']
    assert len(oe) == 1 and oe[0]['tone'] == 'favourable'
    assert set(oe[0]['period_lords'].split(', ')) >= {'Jupiter', 'Mars'}
    assert 'DU-03' in ids(rows)
    os4 = next(r for r in rows if r['rule_id'] == 'OS-04')
    assert 'Employment' in os4['finding']        # 6th lord own sign, 10th lord Mars weak in the 6th


def test_exalted_7th_lord_saturn_in_4th_for_kataka():
    rows = rows_of('Kataka', Saturn='Thula')
    assert 'SAT-11' in ids(rows)


def test_exalted_10th_lord_direct_and_retrograde():
    direct = next(r for r in rows_of('Mesha', Saturn='Thula') if r['rule_id'] == 'RY-04')
    retro = next(r for r in rows_of('Mesha', retro=('Saturn',), Saturn='Thula') if r['rule_id'] == 'RY-04')
    assert 'own business' in direct['finding'] and 'employment' in retro['finding']


def test_retrograde_debilitated_planet_gives_exalted_result():
    rows = rows_of('Mesha', retro=('Saturn',), Saturn='Mesha', Jupiter='Kanya')
    vak = [r for r in rows if r['rule_id'] == 'VAK-01' and r['basis'].startswith('Saturn')]
    assert vak and 'exalted' in vak[0]['finding']


def test_jupiter_aspect_neutralises_retrogression():
    rows = rows_of('Mesha', retro=('Venus',), Venus='Thula', Jupiter='Mesha')     # Jupiter aspects the 7th from it
    vak = next(r for r in rows if r['rule_id'] == 'VAK-01' and r['basis'].startswith('Venus'))
    assert 'neutralised' in vak['finding']


# ── timing ────────────────────────────────────────────────────────────────────

def test_status_follows_the_periods():
    res = with_dasa(A.compute(now=NOW, **S))
    ch = RB.Chart(res, NOW)
    current = res['vedic']['dasa']['current']['dasa']['lord']
    assert RB.timing(ch, [current], dasa_only=True)[0] == 'running now'
    assert RB.timing(ch, [])[0] == 'always'
    late = [d['lord'] for d in res['vedic']['dasa']['dasas'] if ch.age(d['start']) >= 75]
    if late:
        assert RB.timing(ch, [late[-1]], dasa_only=True)[0] == 'dormant'


def test_random_charts_evaluate_cleanly():
    rnd = random.Random(2026)
    statuses = {'running now', 'upcoming', 'past', 'dormant', 'always'}
    for _ in range(25):
        dob = f'{rnd.randint(1950, 2020)}-{rnd.randint(1, 12):02d}-{rnd.randint(1, 28):02d}'
        tob = f'{rnd.randint(0, 23):02d}:{rnd.randint(0, 59):02d}'
        rows = RB.evaluate(A.compute('X', dob, tob, 'Chennai', lat=13.08, lon=80.27, tz='Asia/Kolkata', now=NOW), NOW)
        assert rows
        for r in rows:
            assert list(r) == [c for c, _ in RB.COLUMNS]
            assert r['status'] in statuses and r['tone'] in ('favourable', 'mixed', 'challenging')
            text = json.dumps(r).lower()
            assert not any(w in text for w in FORBIDDEN) and not POLICY.search(text)


# ── AI block and route ────────────────────────────────────────────────────────

def test_ai_block_has_the_rule_book():
    import enrich as E
    ai = E.enrich(A.compute(now=NOW, **S), extras={'coordinates_source': 'entered'})
    rb = ai['tables']['AI_RuleBook']
    assert rb and 'status_at_report_date' in rb[0]
    assert all(v != '' for r in rb for v in r.values())          # an empty cell is None in the AI sheets


def test_predictions_route():
    import app as app_module
    body = dict(S, tz='Asia/Kolkata')
    resp = app_module.app.test_client().post('/api/predictions', json=body)
    assert resp.status_code == 200
    out = resp.get_json()
    assert out['predictions'] and out['summary'] and [c['name'] for c in out['columns']] == [c for c, _ in RB.COLUMNS]
    text = resp.get_data(as_text=True).lower()
    assert not any(w in text for w in FORBIDDEN)


def test_predictions_route_rejects_bad_input():
    import app as app_module
    resp = app_module.app.test_client().post('/api/predictions', json={'dob': 'x', 'tob': '10:00', 'pob': 'Chennai',
                                                                         'lat': 13, 'lon': 80})
    assert resp.status_code == 400


# ── nakshatra traits (NK-*) ───────────────────────────────────────────────────

def _nk(rows):
    return {r['rule_id']: r for r in rows if r['rule_id'].startswith('NK-')}


def test_mrigashira_moon_pada_and_wealth_star():
    # Moon at Rishabha 25 deg = Mrigashira pada 1 (Leo navamsa); next star Ardra
    nk = _nk(rows_of('Mesha', Moon=('Rishabha', 25.0)))
    assert 'Mrigashira' in nk['NK-01']['finding']
    assert nk['NK-02']['finding'].startswith('Moon in the first pada of Mrigashira')
    assert 'Ardra' in nk['NK-26']['finding'] and 'a diamond' in nk['NK-26']['finding']
    assert all(r['status'] == 'always' for r in nk.values())


def test_seventh_lord_in_vishakha():
    # Mesha lagna: Venus rules the 7th; Thula 25 deg is Vishakha
    nk = _nk(rows_of('Mesha', Venus=('Thula', 25.0)))
    assert nk['NK-05']['tone'] == 'mixed' and 'Venus' in nk['NK-05']['finding']


def test_theme_routed_to_the_house_the_planet_rules():
    # Kataka lagna: Saturn rules the 7th (and 8th); Mithuna 25 deg is Punarvasu
    nk = _nk(rows_of('Kataka', Saturn=('Mithuna', 25.0)))
    assert 'for the spouse' in nk['NK-03']['finding']


def test_nakshatra_findings_translate_everywhere():
    import i18n
    import rulebook_i18n as RI
    rows = rows_of('Kataka', Moon=('Rishabha', 25.0), Saturn=('Mithuna', 25.0), Venus=('Thula', 25.0))
    nk = [r for r in rows if r['rule_id'].startswith('NK-')]
    assert len(nk) >= 4
    for r in nk:
        for lang in ('ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn'):
            out = RI.translate(r['finding'], r['rule_id'], lang, lambda p: i18n.planet(p, lang))
            assert out and '{' not in out, (lang, r['finding'])
