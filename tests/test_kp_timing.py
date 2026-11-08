"""
Tests for kp_timing.py (KP event timing) and its 'kp' section in predictions.py.

  * same chart and report moment, same output
  * ruling planets of a moment come from the KP lagna / Moon and the day lord
  * the verdict follows the cuspal sub lord's star-lord houses
  * every window lies ahead of the report moment, inside the horizon and the
    event's age band, with a fruitful bhukti lord and peak antarams inside it
  * no health / longevity event; below 18 only Education is timed
  * the 'kp' section appears in the predictions block in every language
"""
from datetime import datetime, timedelta

import pytest

import astro_engine as A
import kp_timing as K
import predictions as P
from enrich import enrich

NOW = datetime(2026, 11, 5, 11, 40)
CHARTS = [
    dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707),
    dict(name='Chart B', dob='1998-03-06', tob='01:37', pob='Delhi', lat=28.6139, lon=77.2090),
    dict(name='Chart E', dob='2003-09-21', tob='17:45', pob='Coimbatore', lat=11.0168, lon=76.9558),
]
MINOR = dict(name='Child', dob='2016-06-01', tob='09:15', pob='Chennai', lat=13.0827, lon=80.2707)


@pytest.fixture(scope='module')
def outs():
    return {c['name']: (A.compute(now=NOW, **c), None) for c in CHARTS}


def _out(chart):
    res = A.compute(now=NOW, **chart)
    return res, K.compute(res, NOW)


def test_deterministic():
    assert _out(CHARTS[0])[1] == _out(CHARTS[0])[1]


def test_ruling_planets_parts():
    res, out = _out(CHARTS[0])
    rp = out['ruling_planets']
    jd = A.julian_day(res['meta']['local_dt'] - timedelta(hours=res['meta']['utc_offset']))
    pos = A._positions(jd, res['meta']['lat'], res['meta']['lon'], A.swe.SIDM_KRISHNAMURTI)
    _, star, _, _ = A.kp_lords(pos['cusps'][0])
    assert rp['parts']['lagna_star_lord'] == star
    assert rp['planets'][0] == star
    for k in ('lagna_star_lord', 'lagna_sign_lord', 'moon_star_lord', 'moon_sign_lord', 'day_lord'):
        assert rp['parts'][k] in rp['planets']


def test_verdict_follows_sub_lord():
    for chart in CHARTS:
        res, out = _out(chart)
        for e in out['events']:
            assert e['csl'] == res['kp']['cusps'][e['cusp'] - 1]['sub_lord']
            assert set(e['fav_primary']) <= set(e['fav']) and set(e['neg_primary']) <= set(e['neg'])
            if e['fav_primary'] and not e['neg_primary']:
                assert e['verdict'] == 'strong'
            if not e['fav_primary'] and not e['fav_own']:
                assert e['verdict'] == 'weak' and not e['windows']


def test_windows_are_ahead_and_in_band():
    for chart in CHARTS:
        res, out = _out(chart)
        birth = res['meta']['local_dt']
        horizon = NOW + timedelta(days=K.HORIZON_YEARS * A.YEAR_DAYS)
        for e in out['events']:
            fruitful = {s['planet'] for s in e['significators'] if s['fruitful']}
            assert len(e['windows']) <= K.WINDOWS_PER_EVENT
            for w in e['windows']:
                assert NOW <= w['start'] < w['end'] and w['start'] < horizon
                assert (w['start'] - birth).days / 365.25 <= e['ages'][1]
                assert (w['end'] - birth).days / 365.25 >= e['ages'][0]
                assert w['bhukti'] in fruitful
                assert 1 <= len(w['peaks']) <= K.PEAKS_PER_WINDOW
                for p in w['peaks']:
                    assert w['start'] <= p['start'] < p['end'] <= w['end'] and p['antara'] in fruitful
                for a, b in w['sun']:
                    assert w['start'] - timedelta(days=1) <= a <= b <= w['end']


def test_no_health_event_and_minor_only_education():
    assert not any(k in ('health', 'disease', 'hospital') for k, *_ in K.EVENTS)
    _, out = _out(MINOR)
    assert [e['event'] for e in out['events']] == ['education']


@pytest.mark.parametrize('lang', ['en', 'ta', 'hi', 'bn'])
def test_kp_section_in_predictions(lang):
    res = A.compute(now=NOW, lang=lang, **CHARTS[1])
    block = P.build(res, enrich(res), lang)
    assert any(s['key'] == 'kp' for s in block['sections'])
    rows = [r for r in block['rows'] if r['section'] == 'kp' and r['item'] != 'disclaimer']
    assert any(r['item'] == 'promise' for r in rows) and any(r['item'] == 'ruling planets' for r in rows)
    for r in rows:
        assert '{' not in r['text'] and r['basis']


def test_report_date_does_not_change_the_windows():
    """Ruling planets are those of the birth moment, so a later report date only drops passed periods."""
    a = K.compute(A.compute(now=NOW, **CHARTS[0]), NOW)
    later = NOW + timedelta(days=3)
    b = K.compute(A.compute(now=later, **CHARTS[0]), later)
    assert a['ruling_planets']['planets'] == b['ruling_planets']['planets']
    for ea, eb in zip(a['events'], b['events']):
        assert [(w['dasa'], w['bhukti'], w['end']) for w in ea['windows']] == \
               [(w['dasa'], w['bhukti'], w['end']) for w in eb['windows']]


def test_ruling_planets_are_of_the_birth_moment():
    res = A.compute(now=NOW, **CHARTS[0])
    rp = K.compute(res, NOW)['ruling_planets']
    assert rp['moment'] == res['meta']['local_dt']
    assert rp['parts']['day_lord'] == res['vedic']['panchangam']['vara_lord']


def test_events_do_not_all_share_the_same_windows():
    for chart in CHARTS:
        _, out = _out(chart)
        sets = {tuple((w['dasa'], w['bhukti']) for w in e['windows']) for e in out['events'] if e['windows']}
        assert len(sets) > 1


def test_running_bhukti_is_listed_when_it_qualifies():
    _, out = _out(CHARTS[0])
    job = next(e for e in out['events'] if e['event'] == 'job')
    assert job['windows'][0]['start'] == NOW and job['windows'][0]['bhukti'] == 'Rahu'
