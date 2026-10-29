"""
family_relations.py — section I of the family reading: relationships over time.

For every pair of members whose relation can be named, each member's chart is
read about the other, and the periods (dasa, bhukti or months) in which that
relationship is supportive or needs care are listed with the counted rule
behind them. Rules (all in FAMILY_RULES of family_engine, printed with the
report):

  I1  karaka period: the member runs the dasa or bhukti of the relative's
      karaka; read by the karaka's strength in the member's chart.
  I2  relation house lord: the member runs the period of the lord of the
      relative's house; read by that lord's strength.
  I3  6th, 8th and 12th counted from the relative's house: their lords' periods
      need care (mixed when the lord also owns the relative's house or a trikona).
  I4  separating planets (Sun, Saturn, Rahu, Ketu): a mahadasa of one that sits
      in, aspects, or is the karaka of the relative's house: distance eases it.
  I5  the member's mahadasa lord against the other's Moon-sign lord, by natural
      relation both ways, confirmed by the other's lagna lord; month windows.
  I6  a 6/8 or 2/12 Moon axis of the pair in months when either member is in a
      difficult period, sade sati or ashtama.
  Σ   an overall row for a period that two or more of I1-I4 read.

Policy (the module's): a line that needs care asks for patience, space or
distance in the relationship; it never makes one member the cause of another's
difficulty, never reads health or length of life, and prints no remedy. Below
ADULT_AGE only parent, child, sibling, grandparent, grandchild and uncle rows
are read.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from itertools import combinations

import enrich as E
import i18n
from astro_engine import RASIS, SIGN_LORDS

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, 'data', 'family', 'relations.json'), encoding='utf-8') as _f:
    TEMPLATES = json.load(_f)

TONES = ('supportive', 'mixed', 'care')
GOOD_STATES = ('Exalted', 'Moolatrikona', 'Own sign', 'Great friend', 'Friend')
TRIK = (6, 8, 12)
TRIKONA = {1, 5, 9}
MALEFIC_COMPANY = ('Saturn', 'Rahu', 'Ketu')
SEPARATING = ('Sun', 'Saturn', 'Rahu', 'Ketu')
ADULT_ROLES = ('spouse', 'father_in_law', 'mother_in_law', 'parent_in_law', 'child_in_law')
AXIS_AREA = {(6, 8): 'understanding', (2, 12): 'money'}
YEAR = 365.25

# ── roles ─────────────────────────────────────────────────────────────────────
# role(A, B): what B is to A. Houses are counted from A's lagna; the karaka is
# read in A's chart.

RELATION_ROLE = {
    'Father': 'father', 'Mother': 'mother', 'Son': 'child', 'Daughter': 'child', 'Spouse': 'spouse',
    'Father-in-law': 'father_in_law', 'Mother-in-law': 'mother_in_law',
    'Daughter-in-law': 'child_in_law', 'Son-in-law': 'child_in_law',
    'Grandfather': 'grandfather', 'Grandmother': 'grandmother',
    'Grandson': 'grandchild', 'Granddaughter': 'grandchild',
    'Maternal uncle': 'maternal_uncle',
}


def houses_of(role, a, b):
    """[(house, karaka, note)] of role in A's chart."""
    if role == 'father':
        return [(9, 'Sun', '9th: father')]
    if role == 'mother':
        return [(4, 'Moon', '4th: mother')]
    if role == 'parent':
        return [(9, 'Sun', '9th: father'), (4, 'Moon', '4th: mother')]
    if role == 'child':
        return [(5, 'Jupiter', '5th: children')]
    if role == 'spouse':
        if a.gender == 'male':
            return [(7, 'Venus', '7th: spouse')]
        if a.gender == 'female':
            return [(7, 'Jupiter', '7th: spouse')]
        return [(7, 'Venus', '7th: spouse'), (7, 'Jupiter', '7th: spouse')]
    if role == 'younger_sibling':
        return [(3, 'Mars', '3rd: younger siblings')]
    if role == 'elder_sibling':
        return [(11, 'Saturn', '11th: elder siblings')]
    if role == 'father_in_law':
        return [(3, 'Sun', '3rd: father-in-law (9th from the 7th)')]
    if role == 'mother_in_law':
        return [(10, 'Moon', '10th: mother-in-law (4th from the 7th)')]
    if role == 'parent_in_law':
        return [(3, 'Sun', '3rd: father-in-law (9th from the 7th)'),
                (10, 'Moon', '10th: mother-in-law (4th from the 7th)')]
    if role == 'child_in_law':
        note = '11th: child-in-law (7th from the 5th)'
        if b.gender == 'female':
            return [(11, 'Venus', note)]
        if b.gender == 'male':
            return [(11, 'Jupiter', note)]
        return [(11, 'Venus', note), (11, 'Jupiter', note)]
    if role == 'grandfather':
        return [(5, 'Sun', '5th: paternal grandfather (9th from the 9th)'),
                (7, 'Sun', '7th: maternal grandfather (4th from the 4th)')]
    if role == 'grandmother':
        return [(12, 'Moon', '12th: grandmother (4th from the 9th; 9th from the 4th)')]
    if role == 'grandchild':
        return [(9, 'Jupiter', '9th: grandchildren (5th from the 5th)')]
    if role == 'maternal_uncle':
        return [(6, 'Mercury', '6th: maternal uncle (3rd from the 4th)')]
    if role == 'sister_child':
        return [(7, 'Jupiter', "7th: younger sister's child (5th from the 3rd)"),
                (3, 'Jupiter', "3rd: elder sister's child (5th from the 11th)")]
    return []


def _sibling(a, b):
    """What b is to a among siblings: born later = younger."""
    return 'younger_sibling' if b.birth_utc > a.birth_utc else 'elder_sibling'


def _parent_by(m):
    return {'male': 'father', 'female': 'mother'}.get(m.gender, 'parent')


def _parent_in_law_by(m):
    return {'male': 'father_in_law', 'female': 'mother_in_law'}.get(m.gender, 'parent_in_law')


def _grandparent_by(m):
    return {'male': 'grandfather', 'female': 'grandmother'}.get(m.gender)


def role_to_anchor(anchor, m):
    """What member m is to the anchor."""
    rel = m.relation
    if rel in ('Brother', 'Sister'):
        return _sibling(anchor, m)
    return RELATION_ROLE.get(rel)


def inverse(role, viewer, other):
    """role is what `viewer` is to `other`; returns what `other` is to `viewer`."""
    if role in ('father', 'mother', 'parent'):
        return 'child'
    if role == 'child':
        return _parent_by(other)
    if role == 'spouse':
        return 'spouse'
    if role in ('younger_sibling', 'elder_sibling'):
        return _sibling(viewer, other)
    if role in ('father_in_law', 'mother_in_law', 'parent_in_law'):
        return 'child_in_law'
    if role == 'child_in_law':
        return _parent_in_law_by(other)
    if role in ('grandfather', 'grandmother'):
        return 'grandchild'
    if role == 'grandchild':
        return _grandparent_by(other)
    if role == 'maternal_uncle':
        return 'sister_child'
    return None


SIBLINGS = ('younger_sibling', 'elder_sibling')
PARENTS = ('father', 'mother')


def derive(x, rx, y, ry):
    """What y is to x when both are named only through the anchor (rx, ry: what each is to the anchor)."""
    if rx == 'spouse':
        if ry in PARENTS:
            return 'father_in_law' if ry == 'father' else 'mother_in_law'
        if ry in ('father_in_law', 'mother_in_law'):
            return 'father' if ry == 'father_in_law' else 'mother'
        if ry in ('child', 'child_in_law', 'grandchild'):
            return ry
    if ry == 'spouse':
        if rx in PARENTS or rx == 'child_in_law':
            return 'child_in_law'
        if rx in ('father_in_law', 'mother_in_law', 'child'):
            return 'child' if rx != 'child' else _parent_by(y)
    if {rx, ry} == {'father', 'mother'} or {rx, ry} == {'father_in_law', 'mother_in_law'}:
        return 'spouse'
    if (rx in SIBLINGS or rx == 'child') and (ry in SIBLINGS or ry == 'child') and (rx == 'child') == (ry == 'child'):
        return _sibling(x, y)
    if rx in SIBLINGS and ry in PARENTS:
        return ry
    if rx in PARENTS and ry in SIBLINGS:
        return 'child'
    if rx == 'child' and ry in PARENTS + ('father_in_law', 'mother_in_law'):
        return 'grandfather' if ry in ('father', 'father_in_law') else 'grandmother'
    if ry == 'child' and rx in PARENTS + ('father_in_law', 'mother_in_law'):
        return 'grandchild'
    if rx == 'mother' and ry == 'maternal_uncle' or rx == 'maternal_uncle' and ry == 'mother':
        return _sibling(x, y)
    if rx in SIBLINGS and ry == 'maternal_uncle':
        return 'maternal_uncle'
    if rx == 'maternal_uncle' and ry in SIBLINGS:
        return 'sister_child'
    return None


def role_between(anchor, a, b):
    """What b is to a, or None when it cannot be named from the relations given."""
    if a is anchor:
        return role_to_anchor(anchor, b)
    if b is anchor:
        r = role_to_anchor(anchor, a)
        return inverse(r, a, b) if r else None
    ra, rb = role_to_anchor(anchor, a), role_to_anchor(anchor, b)
    if not ra or not rb:
        return None
    return derive(a, ra, b, rb)


# ── chart readings ────────────────────────────────────────────────────────────

def strength(m, planet):
    """('supportive' | 'mixed' | 'care', facts) of a planet in member m's chart (rule I1)."""
    c = m.c
    dig = m.dignity(planet)
    house = c.house[planet]
    combust = planet in E.SEVEN and planet != 'Sun' and m.combust(planet)
    company = [p for p in MALEFIC_COMPANY if p != planet and c.sign[p] == c.sign[planet]]
    facts = f"{planet} in {_ord(house)} from lagna ({RASIS[c.sign[planet]]})"
    facts += f", {dig}" if dig else ''
    facts += ', combust' if combust else ''
    facts += f", with {', '.join(company)}" if company else ''
    if dig == 'Debilitated' or combust or house in TRIK or company:
        return 'care', facts
    if dig in GOOD_STATES:
        return 'supportive', facts
    return 'mixed', facts


def trik_lords(m, house):
    """{lord: [counted houses]} of the 6th, 8th and 12th counted from a house."""
    out = {}
    for k in TRIK:
        h = (house + k - 2) % 12 + 1
        out.setdefault(SIGN_LORDS[m.house_sign(h)], []).append((k, h))
    return out


def _through(m, lord):
    return SIGN_LORDS[m.c.sign[lord]] if lord in E.NODES else lord


# ── periods ───────────────────────────────────────────────────────────────────

def periods(m, lo, hi):
    """Dasa and bhukti periods of member m that overlap [lo, hi) local time: (level, lord, start, end)."""
    out = []
    for d in m.res['vedic']['dasa']['dasas']:
        if d['end'] <= lo or d['start'] >= hi:
            continue
        out.append(('dasa', d['lord'], d['start'], d['end'], d['lord']))
        for b in d.get('sub', []):
            if b['end'] <= lo or b['start'] >= hi:
                continue
            out.append(('bhukti', b['lord'], b['start'], b['end'], d['lord']))
    return out


def _ord(n):
    return {1: '1st', 2: '2nd', 3: '3rd'}.get(n, f'{n}th')


def _age(m, dt):
    return round((dt - m.res['meta']['local_dt']).days / YEAR, 1)


def _fmt(dt):
    return dt.strftime('%Y-%m-%d')


# ── the section ───────────────────────────────────────────────────────────────

def _row(a, b, role, level, lord, start, end, rule, tone, key, params, basis, dasa=None):
    what = f"{lord} {level}" + (f" in {dasa} dasa" if level == 'bhukti' and dasa else '')
    return {
        'pair': f'{a.name} - {b.name}', 'member_running': a.name, 'other': b.name, 'relation': role,
        'level': level, 'lord': lord, 'start': start, 'end': end,
        'age_start': _age(a, start) if a else None, 'age_end': _age(a, end) if a else None,
        'rule_id': rule, 'tone': tone, 'key': key, 'params': params,
        'reading': render({'key': key, 'params': params}, 'en'),
        'basis': f"{basis}; {what} {_fmt(start)} to {_fmt(end)}",
    }


def _direction(a, b, role, lo, hi):
    """Rules I1-I4 for A's chart about B."""
    rows = []
    houses = houses_of(role, a, b)
    params = {'b': b.name, 'rel': role}
    for level, lord, start, end, dasa in periods(a, lo, hi):
        for house, karaka, note in houses:
            hsign = a.house_sign(house)
            hlord = SIGN_LORDS[hsign]
            if lord == karaka:                                                   # I1
                tone, facts = strength(a, karaka)
                rows.append(_row(a, b, role, level, lord, start, end, 'I1', tone, f'I1.{tone}',
                                 dict(params, karaka=karaka), f"karaka of the {role.replace('_', ' ')}: {facts}",
                                 dasa))
            if lord == hlord:                                                    # I2
                tone, facts = strength(a, hlord)
                rows.append(_row(a, b, role, level, lord, start, end, 'I2', tone, f'I2.{tone}', params,
                                 f"lord of the {note}: {facts}", dasa))
            trik = trik_lords(a, house)
            if lord in trik:                                                     # I3
                owns = set(a.c.owned[lord])
                tone = 'mixed' if house in owns or owns & TRIKONA else 'care'
                counted = ', '.join(f"{_ord(k)} from the {_ord(house)} = {_ord(h)}" for k, h in trik[lord])
                rows.append(_row(a, b, role, level, lord, start, end, 'I3', tone, f'I3.{tone}', params,
                                 f"{lord} rules {counted} ({note}); owns {sorted(owns)}", dasa))
            if level == 'dasa' and lord in SEPARATING:                           # I4
                psign = a.c.sign[lord]
                link = ('sits in' if psign == hsign else
                        'aspects' if hsign in E.aspected_signs(lord, psign) else
                        'is the karaka of' if lord == karaka else None)
                if link:
                    st, facts = strength(a, lord)
                    tone = 'mixed' if st == 'supportive' else 'care'
                    rows.append(_row(a, b, role, level, lord, start, end, 'I4', tone, f'I4.{tone}', params,
                                     f"separating planet {lord} {link} the {note}: {facts}"))
    return rows


def _months(lo, hi):
    out, y, mo = [], lo.year, lo.month
    while True:
        start = datetime(y, mo, 1)
        if start >= hi:
            return out
        out.append(start)
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1


def _windows(flags):
    """[(start, end, value)] of consecutive months with the same non-None value."""
    out = []
    for start, val in flags:
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        if out and out[-1][2] == val and out[-1][1] == start:
            out[-1] = (out[-1][0], end, val)
        elif val is not None:
            out.append((start, end, val))
    return [w for w in out if w[2] is not None]


def _i5(a, b, role, lo, hi):
    moon_lord = SIGN_LORDS[b.c.moon_sign]
    lagna_lord = SIGN_LORDS[b.c.lagna_sign]
    flags = []
    for start in _months(lo, hi):
        mid = start + timedelta(days=14)
        dasa = None
        for d in a.res['vedic']['dasa']['dasas']:
            if d['start'] <= mid < d['end']:
                dasa = d['lord']
        val = None
        if dasa:
            lord = _through(a, dasa)
            if lord != moon_lord:
                ab, ba = E.natural_relation(lord, moon_lord), E.natural_relation(moon_lord, lord)
                if ab == ba == 'Enemy':
                    val = ('care', dasa)
                elif ab == ba == 'Friend':
                    val = ('supportive', dasa)
                if val and lord != lagna_lord:
                    lb, bl = E.natural_relation(lord, lagna_lord), E.natural_relation(lagna_lord, lord)
                    agree = (lb == bl == 'Enemy') if val[0] == 'care' else (lb == bl == 'Friend')
                    if not agree:
                        val = None
        flags.append((start, val))
    rows = []
    for start, end, (tone, dasa) in _windows(flags):
        rows.append(_row(a, b, role, 'months', dasa, start, end, 'I5', tone, f'I5.{tone}', {'b': b.name, 'rel': role},
                         f"{a.name}'s dasa lord {dasa}{' (via ' + _through(a, dasa) + ')' if dasa in E.NODES else ''} "
                         f"and {b.name}'s Moon-sign lord {moon_lord}: "
                         f"{'enemies' if tone == 'care' else 'friends'} both ways; lagna lord {lagna_lord} agrees"))
    return rows


def _i6(a, b, months_e, lo, hi):
    d = E.house_from(b.c.moon_sign, a.c.moon_sign)
    key = tuple(sorted((d, E.house_from(a.c.moon_sign, b.c.moon_sign))))
    if key not in AXIS_AREA:
        return []
    by_month = {mrow['month']: mrow for mrow in months_e}
    flags = []
    for start in _months(lo, hi):
        mrow = by_month.get(start.strftime('%Y-%m'))
        hard = False
        if mrow:
            for m in (a, b):
                cell = mrow['members'].get(m.idx) or {}
                if cell.get('period') == 'difficult' or cell.get('saturn') in (
                        'sade sati - 1st phase', 'sade sati - 2nd phase', 'sade sati - 3rd phase', 'ashtama'):
                    hard = True
        flags.append((start, 'care' if hard else None))
    rows = []
    axis = f"{key[0]}/{key[1]}"
    for start, end, _ in _windows(flags):
        r = _row(a, b, '', 'months', '', start, end, 'I6', 'care', 'I6.care',
                 {'a': a.name, 'b': b.name, 'area': AXIS_AREA[key]},
                 f"Moon axis {axis}; a difficult period, sade sati or ashtama for {a.name} or {b.name}")
        r['member_running'] = f'{a.name}, {b.name}'
        r['age_start'] = r['age_end'] = None
        rows.append(r)
    return rows


def _summaries(rows):
    """One Σ row for each period read by two or more of the rules I1-I4."""
    groups = {}
    for r in rows:
        if r['rule_id'] in ('I1', 'I2', 'I3', 'I4'):
            groups.setdefault((r['member_running'], r['other'], r['level'], r['lord'], r['start']), []).append(r)
    out = []
    for grp in groups.values():
        if len(grp) < 2:
            continue
        tones = [r['tone'] for r in grp]
        if tones.count('care') >= 2 and 'supportive' not in tones:
            tone = 'care'
        elif tones.count('supportive') >= 2 and 'care' not in tones:
            tone = 'supportive'
        else:
            tone = 'mixed'
        r0 = grp[0]
        s = dict(r0, rule_id='Σ', tone=tone, key=f'sum.{tone}', params={'b': r0['other'], 'rel': r0['relation']},
                 basis=' + '.join(f"{r['rule_id']} {r['tone']}" for r in grp))
        s['reading'] = render(s, 'en')
        out.append(s)
    return out


def section_i(anchor, members, now_utc, years, months_e):
    """Rows of section I for the members (family_engine.Member), sorted by pair and start."""
    rows = []
    for x, y in combinations(members, 2):
        for a, b in ((x, y), (y, x)):
            role = role_between(anchor, a, b)
            if not role:
                continue
            lo = (now_utc + a.offset).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            hi = lo.replace(year=lo.year + years)
            adult = all(_age(m, now_utc + m.offset) >= ADULT_AGE for m in (a, b))
            if role in ADULT_ROLES and not adult:
                continue
            rows += _direction(a, b, role, lo, hi)
            rows += _i5(a, b, role, lo, hi)
        if role_between(anchor, x, y) or role_between(anchor, y, x):
            lo = (now_utc + x.offset).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rows += _i6(x, y, months_e, lo, lo.replace(year=lo.year + years))
    rows += _summaries(rows)
    order = {'Σ': 0, 'I1': 1, 'I2': 2, 'I3': 3, 'I4': 4, 'I5': 5, 'I6': 6}
    rows.sort(key=lambda r: (r['pair'], r['start'], {'dasa': 0, 'months': 1, 'bhukti': 2}[r['level']],
                             order[r['rule_id']]))
    return rows


ADULT_AGE = 18


# ── language ──────────────────────────────────────────────────────────────────

def T(key, lang):
    row = TEMPLATES[key]
    return row.get(lang) or row['en']


def role_label(role, lang='en'):
    return T(f'role.{role}', lang) if role else ''


def render(row, lang='en'):
    """The reading of a row in the report language ('bi' reads English)."""
    lang = lang if lang in TEMPLATES['title'] else 'en'
    p = dict(row['params'])
    if 'rel' in p:
        p['rel'] = role_label(p['rel'], lang)
    if 'karaka' in p:
        p['karaka'] = i18n.planet(p['karaka'], lang)
    if 'area' in p:
        p['area'] = T(f"area.{p['area']}", lang)
    return T(row['key'], lang).format(**p)


def tone_label(tone, lang='en'):
    return T(f'tone.{tone}', lang if lang in TEMPLATES['title'] else 'en')


def level_label(row, lang='en'):
    lang = lang if lang in TEMPLATES['title'] else 'en'
    if row['rule_id'] == 'Σ':
        return T('level.summary', lang)
    return T(f"level.{row['level']}", lang)


def localize(rows, lang):
    """The rows with reading, tone and relation words in the report language (for the API)."""
    out = []
    for r in rows:
        out.append({k: v for k, v in r.items() if k not in ('key', 'params')} | {
            'reading': render(r, lang), 'tone_label': tone_label(r['tone'], lang),
            'relation_label': role_label(r['relation'], lang), 'level_label': level_label(r, lang),
            'lord_label': i18n.planet(r['lord'], lang) if r['lord'] else ''})
    return out
