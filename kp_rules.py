"""
kp_rules.py — KP (Krishnamurti Paddhati) cuspal sub lord rules, rule-based, no AI model.

    rows = evaluate(res)          # res: astro_engine.compute(); uses res['kp'] and res['meta']
    text = label(key, lang)       # section and column labels in the report language

The rules live in data/kp_rules/kp_cusp_rules.json, separate from the Vedic rule
book (data/rulebook). Each rule names a cusp, its favourable houses and its
negating houses. The cusp's sub lord (CSL) is judged the same way as in
kp_timing.py: the houses its star lord occupies and owns are primary; its own
occupied and owned houses are secondary and only soften a weak verdict.

When a rule has a 'timing_event', the favourable period comes from
kp_timing.compute() for that event (first window ahead).

Site policy: no rule about health, accidents, surgery, confinement, separation,
death or length of life exists in the JSON, and below age 18 only education
rules are shown.
"""

import json
import os

import i18n
import kp_timing

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'kp_rules', 'kp_cusp_rules.json')
ADULT_AGE = 18
MINOR_TOPICS = ('education',)

with open(DATA, encoding='utf-8') as _f:
    BOOK = json.load(_f)


def _text(d, lang):
    if lang == 'bi':
        return i18n._pair(d['en'], d.get('ta'))
    return d.get(lang) or d['en']


def label(key, lang='en'):
    return _text(BOOK['labels'][key], lang)


def evaluate(res, now=None):
    """One row per applicable rule, in cusp order."""
    m, kp = res['meta'], res['kp']
    now = now or m['generated_at']
    age = (now - m['local_dt']).days / 365.25
    houses = kp_timing._signified(kp)
    timing = {e['event']: e for e in kp_timing.compute(res, now)['events']}
    star_of = {p['name']: p['star_lord'] for p in kp['planets']}
    rows = []
    for r in BOOK['rules']:
        if age < ADULT_AGE and r['topic'] not in MINOR_TOPICS:
            continue
        fav, neg = r['favourable'], r['negating']
        csl = kp['cusps'][r['cusp'] - 1]['sub_lord']
        h = houses[csl]
        fav_p = [x for x in h['primary'] if x in fav]
        neg_p = [x for x in h['primary'] if x in neg]
        fav_s = [x for x in h['own'] if x in fav]
        verdict = kp_timing._verdict(fav_p, neg_p, fav_s)
        window = None
        ev = timing.get(r['timing_event'])
        if verdict != 'weak' and ev and ev['windows']:
            window = ev['windows'][0]
        rows.append({'id': r['id'], 'topic': r['topic'], 'cusp': r['cusp'], 'name': r['name'],
                     'favourable': fav, 'negating': neg, 'csl': csl, 'csl_star': star_of[csl],
                     'primary': h['primary'], 'own': h['own'], 'fav_primary': fav_p,
                     'neg_primary': neg_p, 'verdict': verdict, 'window': window,
                     'timed': bool(r['timing_event']) and not (ev and ev['past_band'])})
    return rows


def _d(dt):
    return dt.strftime('%d-%m-%Y')


def table_rows(res, lang, now=None):
    """Rows ready for the KP sheet / KP section: area, cusp, sub lord, houses, result, period."""
    P = lambda n: i18n.planet(n, lang)
    hs = lambda xs: ', '.join(str(x) for x in xs) or '—'
    out = []
    for r in evaluate(res, now):
        w = r['window']
        if w:
            period = f"{P(w['dasa'])} – {P(w['bhukti'])}: {_d(w['start'])} – {_d(w['end'])}"
        elif r['timed'] and r['verdict'] != 'weak':
            period = label('none', lang)
        else:
            period = '—'
        out.append([_text(r['name'], lang), r['cusp'], f"{P(r['csl'])} ({P(r['csl_star'])})",
                    f"{hs(r['primary'])} / {hs(r['own'])}", label('v.' + r['verdict'], lang), period,
                    r['verdict']])
    return out
