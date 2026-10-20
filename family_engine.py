"""
family_engine.py — a family reading from the horoscopes of 2 to 6 members.

family(members) reads the compute() results of the members together and
returns facts in sections. One member is the anchor ("Self"); every other
member carries a relation to the anchor.

Sections
  A  Members: lagna, Moon, star, running dasa and bhukti, Saturn and Jupiter
     from the Moon now.
  B  Relations: the family houses of the anchor (2, 3, 4, 5, 7, 9, 11) in the
     Rasi (D1) and the Dwadasamsa (D12); the house of each relation counted
     from the anchor's lagna, house from house where needed (bhavat bhavam);
     the karaka in D1 and in the varga that concerns the relation; and, read
     back, the house that stands for the anchor in each member's chart.
  C  Pairs: for every pair, the lagna-to-lagna and Moon-to-Moon distance
     both ways and its axis, the relation of the Moon-sign lords, and the
     planets of one member that fall in a sign that matters in the other's
     chart.
  D  Patterns: what repeats across the charts (the same lagna, Moon sign,
     star lord, a planet exalted or debilitated in two or more charts, the
     same ancestral factor), and the Raja, Dhana and Pancha Mahapurusha
     yogas of each member.
  E  Timeline: every member's dasa and bhukti over the years asked for,
     merged month by month with Saturn and Jupiter from each Moon, and each
     month's family status by a counted rule; the windows that result; the
     changes of mahadasa that fall close together for two or more members.
  F  Transits: Saturn, Jupiter, Rahu and Ketu from each Moon now, grouped by
     house, and every change of sign of Saturn and Jupiter over the years.
  G  Family rules: property, children, education, spouse and foreign travel
     read from each member's chart, and where two or more members agree.
  H  Summary.

Rules of this module
  * Facts and counted rules only. Every rule and the variant used is in
    FAMILY_RULES and is printed with the report.
  * Nothing about how long anyone lives, no health reading, and no line that
    makes one member the cause of another's difficulty: a strained link reads
    "needs care in <area>", never that one person harms another.
  * Houses are whole sign from the lagna, as in enrich.py.

Nothing here changes compute(): the module only reads its results.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from itertools import combinations

import astro_engine as A
import enrich as E
from astro_engine import NAKS, PLANETS, RASIS, SIGN_LORDS, InputError

SCHEMA = 'horoscopegen-family/1'
LABEL = 'rule-based, not a prediction'

MIN_MEMBERS, MAX_MEMBERS = 2, 6
YEARS_DEFAULT, YEARS_MIN, YEARS_MAX = 10, 1, 20
SANDHI_DEFAULT, SANDHI_MIN, SANDHI_MAX = 12, 1, 36
MONTH_DAYS = 30.436875

# ── RELATIONS ─────────────────────────────────────────────────────────────────

RELATIONS = ('Self', 'Spouse', 'Father', 'Mother', 'Father-in-law', 'Mother-in-law', 'Son', 'Daughter',
             'Brother', 'Sister', 'Grandfather', 'Grandmother', 'Grandson', 'Granddaughter', 'Other')
RELATION_GENDER = {'Father': 'male', 'Mother': 'female', 'Father-in-law': 'male', 'Mother-in-law': 'female',
                   'Son': 'male', 'Daughter': 'female', 'Brother': 'male', 'Sister': 'female',
                   'Grandfather': 'male', 'Grandmother': 'female', 'Grandson': 'male',
                   'Granddaughter': 'female'}
RELATION_LIMITS = {'Self': 1, 'Spouse': 1, 'Father': 1, 'Mother': 1, 'Father-in-law': 1, 'Mother-in-law': 1,
                   'Grandfather': 2, 'Grandmother': 2}

FAMILY_HOUSES = ((2, 'Kutumba', 'family, speech and the money the family holds'),
                 (3, 'Sahaja', 'younger siblings, courage and talk at home'),
                 (4, 'Matru / Sukha', 'mother, peace at home, land and property'),
                 (5, 'Putra', 'children, the family line and past merit'),
                 (7, 'Kalatra', 'spouse and partnerships'),
                 (9, 'Pitru', 'father, family values and shared fortune'),
                 (11, 'Labha', 'elder siblings and the gains of the family'))

# relation -> [(house from the anchor's lagna, how it is counted, karaka, varga of the karaka)]
# Siblings are placed by age against the anchor; see relation_houses().
GRANDPARENT_ROWS = {
    'Grandfather': [(5, 'paternal grandfather: 9th from the 9th', 'Sun', 'D12'),
                    (7, 'maternal grandfather: 4th from the 4th', 'Sun', 'D12')],
    'Grandmother': [(12, 'paternal grandmother: 4th from the 9th', 'Moon', 'D12'),
                    (12, 'maternal grandmother: 9th from the 4th', 'Moon', 'D12')],
}
RELATION_HOUSES = {
    'Father': [(9, '9th: father', 'Sun', 'D12')],
    'Mother': [(4, '4th: mother', 'Moon', 'D12')],
    'Son': [(5, '5th: children', 'Jupiter', 'D7')],
    'Daughter': [(5, '5th: children', 'Jupiter', 'D7')],
    'Father-in-law': [(3, 'father-in-law: 9th from the 7th', 'Sun', 'D12')],
    'Mother-in-law': [(10, 'mother-in-law: 4th from the 7th', 'Moon', 'D12')],
    'Grandson': [(9, 'grandchildren: 5th from the 5th', 'Jupiter', 'D7')],
    'Granddaughter': [(9, 'grandchildren: 5th from the 5th', 'Jupiter', 'D7')],
    **GRANDPARENT_ROWS,
}
YOUNGER_SIBLING = (3, '3rd: younger siblings', 'Mars', 'D3')
ELDER_SIBLING = (11, '11th: elder siblings', 'Saturn', 'D3')

# ── AXES, OVERLAYS AND PERIODS ────────────────────────────────────────────────

AXIS_NAME = {(1, 1): '1/1 (same sign)', (7, 7): '1/7', (5, 9): '5/9', (3, 11): '3/11', (4, 10): '4/10',
             (6, 8): '6/8 (Shashtashtaka)', (2, 12): '2/12 (Dvirdvadasa)'}
AXIS_CLASS = {(1, 1): 'supportive', (7, 7): 'supportive', (5, 9): 'supportive', (3, 11): 'supportive',
              (4, 10): 'strained', (6, 8): 'strained', (2, 12): 'strained'}
AXIS_CARE = {(4, 10): 'home and shared duties', (6, 8): 'mutual understanding',
             (2, 12): 'shared money and expectations'}

PRESSURE_PLANETS = ('Saturn', 'Rahu', 'Mars')
PRESSURE_POINTS = ('Lagna', 'Moon', 'Sun')
SUPPORT_PLANETS = ('Jupiter', 'Venus')
SUPPORT_HOUSES = (2, 5, 9)

GOOD_HOUSES = (1, 2, 5, 9, 11)
ADULT_AGE = 18              # years; younger members count with MINOR_WEIGHT in the family status
MINOR_WEIGHT = 0.5
MIN_PRESSURE = 1.5          # weighted members needed for a pressured month (two adults, or an adult and a minor)
TRIK_HOUSES = (6, 8, 12)
JUPITER_GOOD_FROM_MOON = E.TRANSIT_GOOD_FROM_MOON['Jupiter']        # 2, 5, 7, 9, 11
SATURN_PRESSURE = {12: 'sade sati - 1st phase', 1: 'sade sati - 2nd phase', 2: 'sade sati - 3rd phase',
                   8: 'ashtama', 4: 'ardhashtama'}
NODE_AXES = {1: '1/7', 7: '1/7', 2: '2/8', 8: '2/8'}
FAMILY_YOGAS = ('Raja yoga', 'Dhana yoga', 'Ruchaka yoga', 'Bhadra yoga', 'Hamsa yoga', 'Malavya yoga',
                'Sasa yoga', 'Dharma-Karmadhipati yoga')

SECTIONS = {
    'A': 'Members',
    'B': 'Relations and family houses',
    'C': 'Pairs',
    'D': 'Shared patterns',
    'E': 'Family timeline',
    'F': 'Transits',
    'G': 'Family rules',
    'H': 'Summary',
}

FAMILY_RULES = [
    ('Members', f'{MIN_MEMBERS} to {MAX_MEMBERS} members, each with full birth details. One is the anchor '
                '("Self"); the others carry their relation to the anchor. At most one each of Spouse, Father, '
                'Mother, Father-in-law and Mother-in-law, and at most two each of Grandfather and Grandmother.'),
    ('Houses', 'Whole sign from the lagna, in the Rasi (D1) and in the Dwadasamsa (D12) with the D12 lagna. '
               'Lords, occupants and graha drishti as in the horoscope workbook (enrich.py).'),
    ('Family houses', 'Read for the anchor: ' + '; '.join(f'{h} {n} ({t})' for h, n, t in FAMILY_HOUSES) + '.'),
    ('Relation houses (bhavat bhavam)', 'From the anchor\'s lagna: spouse 7th; father 9th; mother 4th; '
     'children 5th; younger siblings 3rd and elder siblings 11th (by date of birth against the anchor); '
     'father-in-law 3rd (9th from the 7th); mother-in-law 10th (4th from the 7th); paternal grandfather 5th '
     '(9th from the 9th); maternal grandfather 7th (4th from the 4th); paternal grandmother 12th (4th from '
     'the 9th) and maternal grandmother 12th (9th from the 4th); grandchildren 9th (5th from the 5th). The side '
     'of a grandparent is not asked, so both rows are given.'),
    ('Karakas', 'Spouse: Venus for a male anchor, Jupiter for a female anchor (both shown when the anchor\'s '
                'gender is not given); father and father-in-law Sun; mother and mother-in-law Moon; children '
                'and grandchildren Jupiter; younger siblings Mars; elder siblings Saturn; grandfathers Sun; '
                'grandmothers Moon. Each karaka is also read in the varga for the relation: D9 for the spouse, '
                'D7 for children and grandchildren, D3 for siblings, D12 for parents, in-laws and grandparents.'),
    ('Dignity', 'Exalted, moolatrikona (D1 only), own sign, or the compound relation to the sign lord, with '
                'debilitation; combust in D1 by the orbs of the horoscope workbook.'),
    ('Read back', 'In each member\'s chart, the house that stands for the anchor: for a child, the 9th for '
                  'a father and the 4th for a mother; for a parent, the 5th; for the spouse, the 7th; for a '
                  'sibling, the 3rd when the anchor is younger and the 11th when elder; for a grandparent, '
                  'the 9th; for a grandchild, the 5th (paternal) or 7th (maternal) for a grandfather and the '
                  '12th for a grandmother; for a parent-in-law, the 11th (7th from the 5th).'),
    ('Axes between two charts', 'Distance from one sign to the other, the first counted as 1, both ways. '
     'Supportive: same sign, 1/7, 5/9, 3/11. Strained (needs care): 4/10 (home and shared duties), 6/8 '
     '(mutual understanding), 2/12 (shared money and expectations). Variant: 4/10 is read as strained here; '
     'the rasi porutham of marriage matching counts it differently.'),
    ('Overlays between two charts', 'By sign. Needs care: Saturn, Rahu or Mars of one member in the sign of '
     'another\'s lagna, Moon or Sun. Support: Jupiter or Venus of one member in the sign of another\'s lagna '
     'or Moon, or of the 2nd, 5th or 9th house from the other\'s lagna. Information: any planet of one member '
     'in a kendra (1, 4, 7, 10) from the other\'s lagna.'),
    ('Ancestral factors', 'Read per chart and flagged when two or more members share one: Sun with Rahu, Moon '
     'with Ketu (same sign), the 9th lord or the 2nd lord debilitated, combust, or sharing a sign with Saturn, '
     'Rahu or Ketu. A traditional pattern, reported as a fact only.'),
    ('Period of a lord', 'A dasa or bhukti lord is good when it owns a trikona (1, 5, 9) whatever else it owns, '
     'or owns the 2nd or 11th and none of 6, 8, 12; neutral when it owns the 2nd or 11th together with 6, 8 or '
     '12 and no trikona (the gain house offsets the other); difficult when it owns 6, 8 or 12 with no trikona '
     'and no 2nd or 11th; neutral otherwise. Rahu and Ketu are read through the lord of the sign they '
     'occupy. A member\'s period is good when both the dasa and the bhukti lord are good, difficult when '
     'either is difficult and neither is good, mixed otherwise.'),
    ('Transits from the Moon', 'Sign of the transiting planet counted from the natal Moon sign. Saturn: 12th, '
     '1st, 2nd = sade sati phases 1 to 3; 8th = ashtama; 4th = ardhashtama. Jupiter favourable in the 2nd, 5th, '
     '7th, 9th and 11th. Rahu or Ketu across the 1/7 or 2/8 axis from the Moon is noted.'),
    ('Family status of a month', 'Read at the middle of each month. Every member is weighted: 1 for a member '
     f'aged {ADULT_AGE} or over at that month, {MINOR_WEIGHT} for a younger member, so the periods of the '
     'adults who run the household count for more. Pressured: the weight of members in a difficult period, or in '
     f'sade sati or ashtama while their own period is not good (a good dasa and bhukti offset them), is at least {MIN_PRESSURE} and at least half of the family\'s '
     'weight. Supportive: not pressured, more than half of the weight in a good period, and at least half of '
     'the weight with Jupiter favourable from the Moon. Mixed: otherwise. In a family of two, pressured needs '
     'both. Consecutive months with one status '
     'make a window.'),
    ('Dasa sandhi', 'A change of mahadasa within the set number of months (default 12) of a change of another '
     'member, over the years shown.'),
    ('Family rules', 'Property: 4th lord and Mars. Children: 5th lord and Jupiter. Education: 4th and 5th lords '
     'and Mercury. Spouse: 7th lord and Venus. Foreign travel: Rahu in the 9th or 12th, or the 9th and 12th '
     'lords linked by sign or by exchange. A lord or karaka in an own, exalted, moolatrikona or friendly '
     'sign supports; debilitated or combust needs care. Where two or more members agree on a topic, it is '
     'reported as shared.'),
    ('Language', 'Facts and counted rules only. No verdict on any member, nothing about how long anyone '
                 'lives, no health reading, and no line that makes one member the cause of another\'s '
                 'difficulty.'),
]
NOT_INCLUDED = (
    'Anything about the years of life of any member, or about the end of life',
    'Health readings of any kind',
    'Any statement that blames one member for another\'s difficulty',
    'Remedies',
)


# ── INPUT ─────────────────────────────────────────────────────────────────────

def clean_options(raw=None):
    raw = raw or {}

    def whole(key, default, low, high, name):
        val = raw.get(key)
        if val in (None, ''):
            return default
        try:
            num = int(val)
        except (TypeError, ValueError):
            raise InputError(f'"{name}" must be a whole number from {low} to {high}.')
        if not low <= num <= high:
            raise InputError(f'"{name}" must be a whole number from {low} to {high}.')
        return num

    return {'years': whole('years', YEARS_DEFAULT, YEARS_MIN, YEARS_MAX, 'years'),
            'sandhi_months': whole('sandhi_months', SANDHI_DEFAULT, SANDHI_MIN, SANDHI_MAX, 'sandhiMonths')}


def check_relations(relations):
    """Raise InputError when the list of relations breaks a membership rule."""
    n = len(relations)
    if n < MIN_MEMBERS:
        raise InputError(f'At least {MIN_MEMBERS} family members are needed.')
    if n > MAX_MEMBERS:
        raise InputError(f'At most {MAX_MEMBERS} family members can be read together.')
    for rel in relations:
        if rel not in RELATIONS:
            raise InputError(f'Unknown relation "{rel}". Choose one of: {", ".join(RELATIONS)}.')
    if relations.count('Self') != 1:
        raise InputError('Exactly one member must be "Self" (the person the relations are counted from).')
    for rel, top in RELATION_LIMITS.items():
        if relations.count(rel) > top:
            raise InputError(f'At most {top} member{"s" if top > 1 else ""} can be "{rel}".')


def relation_gender(relation, given=''):
    return RELATION_GENDER.get(relation) or (given if given in ('male', 'female') else '')


# ── CHART HELPERS ─────────────────────────────────────────────────────────────

def _ord(n):
    return {1: '1st', 2: '2nd', 3: '3rd'}.get(n, f'{n}th')


class Member:
    """One member: the compute() result and what the sections read from it."""

    def __init__(self, idx, relation, res):
        self.idx, self.relation, self.res = idx, relation, res
        self.c = E.Ctx(res)
        self.name = res['meta']['name']
        self.label = f'{self.name} ({relation})'
        self.gender = (res['meta'].get('gender') or '').lower()
        self.offset = res['meta']['local_dt'] - res['meta']['ut_dt']
        self.birth_utc = res['meta']['ut_dt']

    # signs of the chart ('D1' or a varga key) -------------------------------
    def signs(self, key='D1'):
        if key == 'D1':
            return dict(self.c.sign)
        return dict(self.c.vargas[key]['signs'])

    def lagna(self, key='D1'):
        return self.signs(key)['Lagna']

    def house_sign(self, h, key='D1'):
        return (self.lagna(key) + h - 1) % 12

    def dignity(self, planet, key='D1'):
        if planet not in E.SEVEN:
            return ''
        label, deb = self.c.dignity[key][planet]
        return 'Debilitated' if deb else label

    def combust(self, planet):
        return self.c.combust(planet)

    def dignity_text(self, planet, key='D1'):
        text = self.dignity(planet, key) or '-'
        if key == 'D1' and self.combust(planet):
            text += ', combust'
        return text

    def house_facts(self, h, key='D1'):
        signs = self.signs(key)
        sign = self.house_sign(h, key)
        lord = SIGN_LORDS[sign]
        occupants = [p for p in PLANETS if signs[p] == sign]
        aspecting = [p for p in PLANETS if sign in E.aspected_signs(p, signs[p])]
        return {
            'chart': key, 'house': h, 'sign': RASIS[sign], 'lord': lord,
            'lord_sign': RASIS[signs[lord]], 'lord_house': E.house_from(signs[lord], self.lagna(key)),
            'lord_dignity': self.dignity_text(lord, key),
            'occupants': ', '.join(occupants) or 'none', 'aspected_by': ', '.join(aspecting) or 'none',
        }

    # periods ------------------------------------------------------------------
    def period_at(self, moment_utc):
        """(dasa lord, bhukti lord, dasa end utc, bhukti end utc) at a UTC moment."""
        for d in self.res['vedic']['dasa']['dasas']:
            if d['start'] - self.offset <= moment_utc < d['end'] - self.offset:
                for b in d.get('sub', []):
                    if b['start'] - self.offset <= moment_utc < b['end'] - self.offset:
                        return d['lord'], b['lord'], d['end'] - self.offset, b['end'] - self.offset
                return d['lord'], None, d['end'] - self.offset, None
        return None, None, None, None

    def lord_quality(self, lord):
        """('good' | 'difficult' | 'neutral', houses owned, read through)."""
        through = lord
        if lord in E.NODES:
            through = SIGN_LORDS[self.c.sign[lord]]
        owned = set(self.c.owned[through])
        trik = owned & set(TRIK_HOUSES)
        gain = owned & {2, 11}
        if owned & {1, 5, 9}:
            q = 'good'
        elif trik and gain:
            q = 'neutral'          # e.g. Saturn ruling the 11th and 12th: the 11th offsets the 12th
        elif trik:
            q = 'difficult'
        elif gain:
            q = 'good'
        else:
            q = 'neutral'
        return q, sorted(owned), through

    def weight_at(self, moment_utc):
        """Weight in the family count: 1 for an adult, MINOR_WEIGHT under ADULT_AGE at that moment."""
        age = (moment_utc - self.birth_utc).days / A.YEAR_DAYS
        return 1.0 if age >= ADULT_AGE else MINOR_WEIGHT

    def period_quality(self, dasa, bhukti):
        qd = self.lord_quality(dasa)[0] if dasa else 'neutral'
        qb = self.lord_quality(bhukti)[0] if bhukti else qd
        if qd == 'good' and qb == 'good':
            return 'good'
        if 'difficult' in (qd, qb) and 'good' not in (qd, qb):
            return 'difficult'
        return 'mixed'

    def mahadasa_changes(self, lo_utc, hi_utc):
        dasas = self.res['vedic']['dasa']['dasas']
        out = []
        for old, new in zip(dasas, dasas[1:]):
            utc = new['start'] - self.offset
            if lo_utc < utc <= hi_utc:
                out.append({'from': old['lord'], 'to': new['lord'], 'utc': utc})
        return out


def relation_houses(anchor, member):
    """Rows (house, rule, karaka, varga) for the member's relation, counted from the anchor."""
    rel = member.relation
    if rel in ('Brother', 'Sister'):
        return [YOUNGER_SIBLING if member.birth_utc > anchor.birth_utc else ELDER_SIBLING]
    if rel == 'Spouse':
        if anchor.gender == 'male':
            return [(7, '7th: spouse', 'Venus', 'D9')]
        if anchor.gender == 'female':
            return [(7, '7th: spouse', 'Jupiter', 'D9')]
        return [(7, '7th: spouse (male anchor)', 'Venus', 'D9'), (7, '7th: spouse (female anchor)', 'Jupiter', 'D9')]
    return RELATION_HOUSES.get(rel, [])


def read_back(anchor, member):
    """Rows (house, rule) in the member's chart that stand for the anchor."""
    rel = member.relation
    if rel in ('Son', 'Daughter'):
        if anchor.gender == 'female':
            return [(4, '4th: mother')]
        if anchor.gender == 'male':
            return [(9, '9th: father')]
        return [(9, '9th: father'), (4, '4th: mother')]
    if rel in ('Father', 'Mother'):
        return [(5, '5th: children')]
    if rel == 'Spouse':
        return [(7, '7th: spouse')]
    if rel in ('Brother', 'Sister'):
        return [(3, '3rd: younger sibling') if anchor.birth_utc > member.birth_utc else (11, '11th: elder sibling')]
    if rel in ('Grandfather', 'Grandmother'):
        return [(9, '9th: grandchildren (5th from the 5th)')]
    if rel in ('Grandson', 'Granddaughter'):
        if anchor.gender == 'female':
            return [(12, '12th: grandmother (either side)')]
        return [(5, '5th: paternal grandfather'), (7, '7th: maternal grandfather')]
    if rel in ('Father-in-law', 'Mother-in-law'):
        return [(11, '11th: child-in-law (7th from the 5th)')]
    return []


# ── TRANSITS ──────────────────────────────────────────────────────────────────

class Sky:
    """Sign stays of the slow planets over the period read."""

    def __init__(self, ref, lo_utc, hi_utc):
        sid = A.AYANAMSHAS[ref['meta']['ayanamsha_key']][1]
        node = ref['meta']['node']
        jd0 = A.julian_day(lo_utc) - 40
        jd1 = A.julian_day(hi_utc) + 40
        self.stays = {}
        for body in ('Saturn', 'Jupiter', 'Rahu'):
            rows = []
            for st in E.stays(body, jd0, jd1, sid, node):
                rows.append({'sign': st['sign'],
                             'entry_utc': E._minute(E.jd_to_utc(st['entry'])) if st['entry'] is not None else None,
                             'exit_utc': E._minute(E.jd_to_utc(st['exit'])) if st['exit'] is not None else None,
                             'motion': st['motion']})
            self.stays[body] = rows

    def sign_at(self, body, moment):
        if body == 'Ketu':
            return (self.sign_at('Rahu', moment) + 6) % 12
        for st in self.stays[body]:
            if (st['entry_utc'] is None or st['entry_utc'] <= moment) and (st['exit_utc'] is None or moment < st['exit_utc']):
                return st['sign']
        return self.stays[body][-1]['sign']


def saturn_state(member, saturn_sign):
    return SATURN_PRESSURE.get(E.house_from(saturn_sign, member.c.moon_sign), 'none')


# ── SECTIONS ──────────────────────────────────────────────────────────────────

def _section_a(members, sky, now):
    rows = []
    for m in members:
        dasa, bhukti, dend, bend = m.period_at(now)
        sat = sky.sign_at('Saturn', now)
        jup = sky.sign_at('Jupiter', now)
        jh = E.house_from(jup, m.c.moon_sign)
        rows.append({
            'member': m.name, 'relation': m.relation, 'gender': m.gender or '-',
            'birth': m.res['meta']['local_dt'], 'place': m.res['meta']['pob'],
            'lagna': RASIS[m.c.lagna_sign], 'moon_sign': RASIS[m.c.moon_sign],
            'star': f"{NAKS[m.c.janma_nak]} pada {m.res['vedic']['moon_pada']}",
            'star_lord': m.c.janma_lord,
            'dasa': dasa, 'dasa_end': dend, 'bhukti': bhukti, 'bhukti_end': bend,
            'saturn_from_moon': f"{_ord(E.house_from(sat, m.c.moon_sign))} ({saturn_state(m, sat)})",
            'jupiter_from_moon': f"{_ord(jh)} ({'favourable' if jh in JUPITER_GOOD_FROM_MOON else 'not favourable'})",
        })
    return rows


def _karaka_cols(m, karaka, varga):
    return {'karaka': karaka, 'karaka_d1': f'{RASIS[m.c.sign[karaka]]}, {m.dignity_text(karaka)}',
            'karaka_varga': varga,
            'karaka_in_varga': f"{RASIS[m.signs(varga)[karaka]]}, {m.dignity(karaka, varga) or '-'}"}


def _section_b(anchor, members):
    houses, relations, back = [], [], []
    for h, name, meaning in FAMILY_HOUSES:
        for key in ('D1', 'D12'):
            houses.append(dict(anchor.house_facts(h, key), name=name, meaning=meaning))
    for m in members:
        if m is anchor:
            continue
        for h, rule, karaka, varga in relation_houses(anchor, m):
            row = {'member': m.name, 'relation': m.relation, 'house': h, 'rule': rule}
            facts = anchor.house_facts(h)
            row.update({k: facts[k] for k in ('sign', 'lord', 'lord_sign', 'lord_house', 'lord_dignity',
                                               'occupants', 'aspected_by')})
            row.update(_karaka_cols(anchor, karaka, varga))
            relations.append(row)
        for h, rule in read_back(anchor, m):
            facts = m.house_facts(h)
            back.append({'member': m.name, 'relation': m.relation, 'house': h, 'rule': rule,
                         **{k: facts[k] for k in ('sign', 'lord', 'lord_house', 'lord_dignity', 'occupants',
                                                  'aspected_by')}})
    return houses, relations, back


def axis_of(sign_a, sign_b):
    d = E.house_from(sign_b, sign_a)
    back = E.house_from(sign_a, sign_b)
    key = tuple(sorted((d, back)))
    return d, back, key


def _axis_cols(prefix, sign_a, sign_b):
    d, back, key = axis_of(sign_a, sign_b)
    cls = AXIS_CLASS[key]
    return {f'{prefix}_count': f'{d} / {back}', f'{prefix}_axis': AXIS_NAME[key], f'{prefix}_reading': cls,
            f'{prefix}_care': f'needs care in {AXIS_CARE[key]}' if cls == 'strained' else ''}


def _section_c(members):
    pairs, overlays = [], []
    for a, b in combinations(members, 2):
        rel = E.natural_relation(SIGN_LORDS[a.c.moon_sign], SIGN_LORDS[b.c.moon_sign]) \
            if SIGN_LORDS[a.c.moon_sign] != SIGN_LORDS[b.c.moon_sign] else 'Same'
        rel_b = E.natural_relation(SIGN_LORDS[b.c.moon_sign], SIGN_LORDS[a.c.moon_sign]) if rel != 'Same' else 'Same'
        row = {'member_a': a.name, 'member_b': b.name}
        row.update(_axis_cols('lagna', a.c.lagna_sign, b.c.lagna_sign))
        row.update(_axis_cols('moon', a.c.moon_sign, b.c.moon_sign))
        row['moon_lords'] = f'{SIGN_LORDS[a.c.moon_sign]} / {SIGN_LORDS[b.c.moon_sign]}'
        row['moon_lords_relation'] = f'{rel} / {rel_b}'
        pairs.append(row)
        for x, y in ((a, b), (b, a)):
            overlays.extend(_overlays(x, y))
    return pairs, overlays


def _overlays(x, y):
    """Planets of member x that fall in a sign that matters in member y's chart."""
    out = []

    def add(planet, point, kind, reading):
        out.append({'from_member': x.name, 'planet': planet, 'to_member': y.name, 'falls_on': point,
                    'sign': RASIS[x.c.sign[planet]], 'kind': kind, 'reading': reading})

    for p in PRESSURE_PLANETS:
        for point in PRESSURE_POINTS:
            if x.c.sign[p] == y.c.sign[point]:
                add(p, f"{y.name}'s {point}", 'needs care', 'needs care in patience and personal space')
    for p in SUPPORT_PLANETS:
        targets = [('Lagna', y.c.lagna_sign), ('Moon', y.c.moon_sign)] + \
                  [(f'{_ord(h)} house', y.house_sign(h)) for h in SUPPORT_HOUSES]
        for point, sign in targets:
            if x.c.sign[p] == sign:
                add(p, f"{y.name}'s {point}", 'support', 'support: relief, guidance and stability')
    for p in PLANETS:
        h = E.house_from(x.c.sign[p], y.c.lagna_sign)
        if h in E.KENDRA:
            add(p, f"{y.name}'s {_ord(h)} house (kendra)", 'information', 'information')
    return out


def ancestral_factors(m):
    s = m.c.sign
    out = []
    if s['Sun'] == s['Rahu']:
        out.append('Sun with Rahu')
    if s['Moon'] == s['Ketu']:
        out.append('Moon with Ketu')
    for h in (9, 2):
        lord = m.c.house_lord[h]
        why = []
        if m.dignity(lord) == 'Debilitated':
            why.append('debilitated')
        if m.combust(lord):
            why.append('combust')
        with_ = [p for p in ('Saturn', 'Rahu', 'Ketu') if p != lord and s[p] == s[lord]]
        if with_:
            why.append('with ' + ', '.join(with_))
        if why:
            out.append(f'{_ord(h)} lord {lord} {" and ".join(why)}')
    return out


def _section_d(members):
    rows = []

    def group(kind, key_fn, note=''):
        groups = {}
        for m in members:
            for k in key_fn(m):
                groups.setdefault(k, []).append(m.name)
        for k, names in groups.items():
            if len(names) >= 2:
                rows.append({'pattern': kind, 'value': k, 'count': len(names), 'members': ', '.join(names),
                             'note': note})

    group('same lagna sign', lambda m: [RASIS[m.c.lagna_sign]])
    group('same Moon sign', lambda m: [RASIS[m.c.moon_sign]])
    group('same star lord', lambda m: [m.c.janma_lord])
    group('planet exalted in two or more charts', lambda m: [p for p in E.SEVEN if m.dignity(p) == 'Exalted'])
    group('planet debilitated in two or more charts', lambda m: [p for p in E.SEVEN if m.dignity(p) == 'Debilitated'])
    group('ancestral factor shared', lambda m: [f.split(' ')[0] + ' ' + f.split(' ', 2)[1] if f.startswith(('9th', '2nd'))
                                                else f for f in ancestral_factors(m)],
          'traditional pattern, reported as a fact only')

    per_member = []
    for m in members:
        found = [y for y in E._yogas(m.c) if y['status'] == 'found' and y['yoga'] in FAMILY_YOGAS]
        per_member.append({'member': m.name, 'relation': m.relation,
                           'yogas': ', '.join(sorted({y['yoga'] for y in found})) or 'none',
                           'ancestral_factors': '; '.join(ancestral_factors(m)) or 'none'})
    return rows, per_member


def _month_starts(lo, hi):
    y, mo = lo.year, lo.month
    out = []
    while True:
        start = datetime(y, mo, 1)
        if start >= hi:
            break
        out.append(start)
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
    return out


def pressure_threshold(total, n):
    """Weight of members needed in a difficult period, sade sati or ashtama for a pressured month."""
    if n <= 2:
        return total
    return max(MIN_PRESSURE, total / 2)


def family_status(states):
    """
    states: per member dicts with 'period', 'saturn', 'jupiter_good' and optional 'weight' (default 1).
    Returns (status, counts); counts are weights, rounded to one decimal.
    """
    n = len(states)
    w = lambda s: s.get('weight', 1.0)
    total = sum(w(s) for s in states)
    good = sum(w(s) for s in states if s['period'] == 'good')
    # Sade sati and ashtama press on a member whose own period is not good; a good dasa and bhukti offset them.
    hard = sum(w(s) for s in states if s['period'] == 'difficult'
               or (s['saturn'] not in ('none', 'ardhashtama') and s['period'] != 'good'))
    jup = sum(w(s) for s in states if s['jupiter_good'])
    if hard >= pressure_threshold(total, n) - 1e-9:
        status = 'pressured'
    elif good * 2 > total and jup * 2 >= total:
        status = 'supportive'
    else:
        status = 'mixed'
    r = lambda x: round(x, 1)
    return status, {'good': r(good), 'pressured': r(hard), 'jupiter_favourable': r(jup), 'weight': r(total)}


def _section_e(members, sky, lo, hi, sandhi_months):
    months = []
    for start in _month_starts(datetime(lo.year, lo.month, 1), hi):
        mid = start + timedelta(days=14)
        sat, jup = sky.sign_at('Saturn', mid), sky.sign_at('Jupiter', mid)
        states, cells = [], {}
        for m in members:
            dasa, bhukti, _, _ = m.period_at(mid)
            period = m.period_quality(dasa, bhukti)
            st = {'period': period, 'saturn': saturn_state(m, sat), 'weight': m.weight_at(mid),
                  'jupiter_good': E.house_from(jup, m.c.moon_sign) in JUPITER_GOOD_FROM_MOON}
            states.append(st)
            cells[m.idx] = {'dasa': dasa, 'bhukti': bhukti, **st,
                            'tag': ('D' if period == 'difficult' else ('G' if period == 'good' else 'M'))
                            + ('S' if st['saturn'].startswith('sade') else ('A' if st['saturn'] == 'ashtama' else ''))
                            + ('J' if st['jupiter_good'] else '')}
        status, counts = family_status(states)
        months.append({'month': start.strftime('%Y-%m'), 'start': start, 'status': status, **counts,
                       'members': cells})

    windows = []
    for mrow in months:
        if windows and windows[-1]['status'] == mrow['status']:
            windows[-1]['to'] = mrow['month']
            windows[-1]['months'] += 1
        else:
            windows.append({'status': mrow['status'], 'from': mrow['month'], 'to': mrow['month'], 'months': 1})

    # periods table: one row per member per bhukti inside the range
    periods = []
    for m in members:
        for d in m.res['vedic']['dasa']['dasas']:
            for b in d.get('sub', []):
                s, e = b['start'] - m.offset, b['end'] - m.offset
                if e <= lo or s >= hi:
                    continue
                qd, owned_d, thr_d = m.lord_quality(d['lord'])
                qb, owned_b, thr_b = m.lord_quality(b['lord'])
                periods.append({'member': m.name, 'dasa': d['lord'], 'bhukti': b['lord'],
                                'start_utc': max(s, lo), 'end_utc': min(e, hi),
                                'dasa_houses': ', '.join(map(str, owned_d)) + ('' if thr_d == d['lord'] else f' (via {thr_d})'),
                                'dasa_quality': qd,
                                'bhukti_houses': ', '.join(map(str, owned_b)) + ('' if thr_b == b['lord'] else f' (via {thr_b})'),
                                'bhukti_quality': qb,
                                'dasa_nature': m.c.nature.get(thr_d, ''),
                                'period': m.period_quality(d['lord'], b['lord'])})

    changes = {m.idx: m.mahadasa_changes(lo, hi) for m in members}
    sandhi = []
    limit = sandhi_months * MONTH_DAYS
    for a, b in combinations(members, 2):
        for ca in changes[a.idx]:
            for cb in changes[b.idx]:
                days = abs((ca['utc'] - cb['utc']).total_seconds()) / 86400.0
                if days <= limit:
                    sandhi.append({'member_a': a.name, 'change_a': f"{ca['from']} to {ca['to']}",
                                   'date_a': ca['utc'], 'member_b': b.name,
                                   'change_b': f"{cb['from']} to {cb['to']}", 'date_b': cb['utc'],
                                   'months_apart': round(days / MONTH_DAYS, 1)})
    sandhi.sort(key=lambda r: min(r['date_a'], r['date_b']))
    all_changes = [{'member': m.name, 'from': c['from'], 'to': c['to'], 'date_utc': c['utc']}
                   for m in members for c in changes[m.idx]]
    all_changes.sort(key=lambda r: r['date_utc'])
    return months, windows, periods, sandhi, all_changes


def _section_f(members, sky, now, lo, hi):
    now_rows = []
    for body in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
        sign = sky.sign_at(body, now)
        groups = {}
        for m in members:
            groups.setdefault(E.house_from(sign, m.c.moon_sign), []).append(m)
        for h in sorted(groups):
            ms = groups[h]
            if body == 'Saturn':
                note = SATURN_PRESSURE.get(h, '')
            elif body == 'Jupiter':
                note = 'favourable' if h in JUPITER_GOOD_FROM_MOON else 'not favourable'
            else:
                note = f'{NODE_AXES[h]} axis from the Moon' if h in NODE_AXES else ''
            now_rows.append({'planet': body, 'sign': RASIS[sign], 'house_from_moon': h,
                             'members': ', '.join(m.name for m in ms), 'count': len(ms), 'note': note,
                             'line': f"{body} {_ord(h)} from the Moon: {', '.join(m.name for m in ms)}"})

    stays = []
    for body in ('Saturn', 'Jupiter', 'Rahu'):
        for st in sky.stays[body]:
            s, e = st['entry_utc'], st['exit_utc']
            if (e is not None and e <= lo) or (s is not None and s >= hi):
                continue
            row = {'planet': body, 'sign': RASIS[st['sign']], 'entry_utc': s, 'exit_utc': e,
                   'motion': st['motion'] or ''}
            parts = []
            for m in members:
                h = E.house_from(st['sign'], m.c.moon_sign)
                tag = ''
                if body == 'Saturn':
                    tag = SATURN_PRESSURE.get(h, '')
                elif body == 'Jupiter':
                    tag = 'favourable' if h in JUPITER_GOOD_FROM_MOON else ''
                else:
                    tag = NODE_AXES.get(h, '') and f'{NODE_AXES[h]} axis'
                parts.append(f"{m.name}: {_ord(h)}" + (f' ({tag})' if tag else ''))
            row['from_each_moon'] = '; '.join(parts)
            stays.append(row)
    return now_rows, stays


GOOD_STATES = ('Exalted', 'Moolatrikona', 'Own sign', 'Great friend', 'Friend')


def _strength(m, planet):
    d = m.dignity(planet)
    if d == 'Debilitated' or m.combust(planet):
        return 'needs care'
    if d in GOOD_STATES:
        return 'supports'
    return 'neutral'


def _topic(m, topic):
    c = m.c
    if topic == 'Property':
        lord = c.house_lord[4]
        items = [(f'4th lord {lord}', _strength(m, lord)), ('Mars', _strength(m, 'Mars'))]
    elif topic == 'Children':
        lord = c.house_lord[5]
        items = [(f'5th lord {lord}', _strength(m, lord)), ('Jupiter', _strength(m, 'Jupiter'))]
    elif topic == 'Education':
        l4, l5 = c.house_lord[4], c.house_lord[5]
        items = [(f'4th lord {l4}', _strength(m, l4)), (f'5th lord {l5}', _strength(m, l5)),
                 ('Mercury', _strength(m, 'Mercury'))]
    elif topic == 'Spouse':
        lord = c.house_lord[7]
        items = [(f'7th lord {lord}', _strength(m, lord)), ('Venus', _strength(m, 'Venus'))]
    else:   # Foreign travel
        l9, l12 = c.house_lord[9], c.house_lord[12]
        linked = l9 != l12 and (c.sign[l9] == c.sign[l12] or c.exchange(l9, l12))
        rahu = c.house['Rahu']
        items = [('Rahu in the 9th or 12th', 'supports' if rahu in (9, 12) else 'neutral'),
                 (f'9th lord {l9} and 12th lord {l12} linked', 'supports' if linked else 'neutral')]
    sup = sum(1 for _, v in items if v == 'supports')
    care = sum(1 for _, v in items if v == 'needs care')
    reading = 'supports' if sup > care else ('needs care' if care > sup else 'neutral')
    return reading, '; '.join(f'{k}: {v}' for k, v in items)


TOPICS = ('Property', 'Children', 'Education', 'Spouse', 'Foreign travel')


def _section_g(members):
    rows, shared = [], []
    for topic in TOPICS:
        by_reading = {}
        for m in members:
            reading, facts = _topic(m, topic)
            rows.append({'topic': topic, 'member': m.name, 'relation': m.relation, 'reading': reading,
                         'facts': facts})
            by_reading.setdefault(reading, []).append(m.name)
        for reading in ('supports', 'needs care'):
            names = by_reading.get(reading, [])
            if len(names) >= 2:
                shared.append({'topic': topic, 'reading': reading, 'count': len(names),
                               'members': ', '.join(names)})
    return rows, shared


def _summary(result):
    s = result['sections']
    months = s['E']['months']
    counts = {k: sum(1 for x in months if x['status'] == k) for k in ('supportive', 'mixed', 'pressured')}
    wins = s['E']['windows']
    best = sorted([w for w in wins if w['status'] == 'supportive'], key=lambda w: -w['months'])[:3]
    worst = sorted([w for w in wins if w['status'] == 'pressured'], key=lambda w: -w['months'])[:3]
    strained = [p for p in s['C']['pairs'] if p['moon_reading'] == 'strained' or p['lagna_reading'] == 'strained']
    lines = [
        ('A', f"{len(result['members'])} members; anchor {result['anchor']}."),
        ('B', f"{len(s['B']['relations'])} relation rows read from the anchor's chart; "
              f"{len(s['B']['read_back'])} read back from the members' charts."),
        ('C', f"{len(s['C']['pairs'])} pairs; {len(strained)} with a strained lagna or Moon axis (needs care); "
              f"{sum(1 for o in s['C']['overlays'] if o['kind'] == 'support')} supportive overlays, "
              f"{sum(1 for o in s['C']['overlays'] if o['kind'] == 'needs care')} needing care."),
        ('D', f"{len(s['D']['patterns'])} shared patterns."),
        ('E', f"Of {len(months)} months: {counts['supportive']} supportive, {counts['mixed']} mixed, "
              f"{counts['pressured']} pressured; {len(s['E']['sandhi'])} pairs of mahadasa changes close together."),
        ('F', '; '.join(r['line'] for r in s['F']['now'] if r['planet'] in ('Saturn', 'Jupiter'))),
        ('G', f"{len(s['G']['shared'])} topics where two or more members agree."),
    ]
    return {
        'lines': [{'section': k, 'title': SECTIONS[k], 'text': t} for k, t in lines],
        'month_counts': counts,
        'supportive_windows': best,
        'pressured_windows': worst,
    }


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def family(members, options=None, now=None):
    """
    Read a family together.

    members: [{'relation': ..., 'res': compute() result}], 2 to 6, exactly one
    'Self'. options: {'years', 'sandhi_months'}. now: the report moment, UTC
    (naive); defaults to the anchor's generated_at converted to UTC.
    Raises InputError when the members break a rule.
    """
    options = clean_options(options)
    check_relations([str(m.get('relation', '')) for m in members])
    ms = [Member(i, m['relation'], m['res']) for i, m in enumerate(members)]
    ms.sort(key=lambda m: (m.relation != 'Self', m.idx))
    for i, m in enumerate(ms):
        m.idx = i
    anchor = ms[0]
    if now is None:
        now = anchor.res['meta']['generated_at'] - anchor.offset
    lo = datetime(now.year, now.month, 1)
    hi = lo.replace(year=lo.year + options['years'])
    sky = Sky(anchor.res, lo - timedelta(days=400), hi)

    houses, relations, back = _section_b(anchor, ms)
    pairs, overlays = _section_c(ms)
    patterns, yogas = _section_d(ms)
    months, windows, periods, sandhi, changes = _section_e(ms, sky, lo, hi, options['sandhi_months'])
    tnow, stays = _section_f(ms, sky, now, lo, hi)
    topics, shared = _section_g(ms)
    result = {
        'schema': SCHEMA, 'label': LABEL, 'generated_utc': now.replace(microsecond=0),
        'anchor': anchor.name,
        'members': [{'idx': m.idx, 'name': m.name, 'relation': m.relation, 'gender': m.gender}
                    for m in ms],
        'settings': {'years': options['years'], 'sandhi_months': options['sandhi_months'],
                     'from': lo.strftime('%Y-%m'), 'to': (hi - timedelta(days=1)).strftime('%Y-%m')},
        'sections': {
            'A': {'members': _section_a(ms, sky, now)},
            'B': {'houses': houses, 'relations': relations, 'read_back': back},
            'C': {'pairs': pairs, 'overlays': overlays},
            'D': {'patterns': patterns, 'per_member': yogas},
            'E': {'months': months, 'windows': windows, 'periods': periods, 'sandhi': sandhi,
                  'changes': changes},
            'F': {'now': tnow, 'stays': stays},
            'G': {'topics': topics, 'shared': shared},
        },
        'titles': dict(SECTIONS),
        'rules': [{'name': n, 'rule': r} for n, r in FAMILY_RULES],
        'not_included': list(NOT_INCLUDED),
    }
    result['summary'] = _summary(result)
    result['_people'] = ms        # for the report builders; removed by public()
    return result


def public(result):
    """The result without the internal objects, ready for JSON."""
    return {k: v for k, v in result.items() if not k.startswith('_')}


# ── FLAT TABLES ───────────────────────────────────────────────────────────────
# One list of rows per sheet, the same rows for the Excel, the PDF and AI readers.

TABLES = [
    # (sheet, section, key inside the section, [(column, meaning)])
    ('AI_FamilyMembers', 'A', 'members', [
        ('member', 'Name'), ('relation', 'Relation to the anchor (Self)'), ('gender', 'male / female / -'),
        ('birth', 'Date and time of birth, clock time at the birth place'), ('place', 'Place of birth'),
        ('lagna', 'Lagna sign (Rasi)'), ('moon_sign', 'Moon sign'), ('star', 'Janma nakshatra and pada'),
        ('star_lord', 'Lord of the janma nakshatra'),
        ('dasa', 'Mahadasa lord at the report moment'), ('dasa_end', 'Its end, UTC'),
        ('bhukti', 'Bhukti lord at the report moment'), ('bhukti_end', 'Its end, UTC'),
        ('saturn_from_moon', 'Transit Saturn counted from the Moon sign now, with its name'),
        ('jupiter_from_moon', 'Transit Jupiter counted from the Moon sign now, favourable in 2, 5, 7, 9, 11')]),
    ('AI_FamilyHouses', 'B', 'houses', [
        ('chart', 'D1 Rasi or D12 Dwadasamsa (houses from that chart\'s lagna)'), ('house', 'House of the anchor'),
        ('name', 'Name of the house'), ('meaning', 'What the house stands for in a family reading'),
        ('sign', 'Sign of the house'), ('lord', 'Lord of the sign'), ('lord_sign', 'Sign the lord occupies'),
        ('lord_house', 'House the lord occupies'), ('lord_dignity', 'Dignity of the lord in that chart'),
        ('occupants', 'Planets in the house'), ('aspected_by', 'Planets aspecting the house (graha drishti)')]),
    ('AI_FamilyRelations', 'B', 'relations', [
        ('member', 'Name'), ('relation', 'Relation to the anchor'), ('house', 'House of the anchor for it'),
        ('rule', 'How the house is counted (bhavat bhavam)'), ('sign', 'Sign of the house'),
        ('lord', 'Lord'), ('lord_sign', 'Sign of the lord'), ('lord_house', 'House of the lord'),
        ('lord_dignity', 'Dignity of the lord in D1'), ('occupants', 'Planets in the house'),
        ('aspected_by', 'Planets aspecting the house'), ('karaka', 'Karaka of the relation'),
        ('karaka_d1', 'Karaka in D1: sign and dignity'), ('karaka_varga', 'Varga read for the relation'),
        ('karaka_in_varga', 'Karaka in that varga: sign and dignity')]),
    ('AI_FamilyReadBack', 'B', 'read_back', [
        ('member', 'Name'), ('relation', 'Relation to the anchor'),
        ('house', 'House in the member\'s own chart that stands for the anchor'), ('rule', 'Why that house'),
        ('sign', 'Sign'), ('lord', 'Lord'), ('lord_house', 'House of the lord'),
        ('lord_dignity', 'Dignity of the lord'), ('occupants', 'Planets in the house'),
        ('aspected_by', 'Planets aspecting the house')]),
    ('AI_FamilyPairs', 'C', 'pairs', [
        ('member_a', 'First member'), ('member_b', 'Second member'),
        ('lagna_count', 'Lagna of B counted from A / A from B'), ('lagna_axis', 'Axis'),
        ('lagna_reading', 'supportive / strained'), ('lagna_care', 'Area that needs care when strained'),
        ('moon_count', 'Moon of B counted from A / A from B'), ('moon_axis', 'Axis'),
        ('moon_reading', 'supportive / strained'), ('moon_care', 'Area that needs care when strained'),
        ('moon_lords', 'Lords of the two Moon signs'),
        ('moon_lords_relation', 'Natural relation of the lords, each way')]),
    ('AI_FamilyOverlays', 'C', 'overlays', [
        ('from_member', 'Member whose planet it is'), ('planet', 'Planet'), ('to_member', 'Other member'),
        ('falls_on', 'What it falls on in the other chart'), ('sign', 'Sign'),
        ('kind', 'support / needs care / information'), ('reading', 'Reading of the overlay')]),
    ('AI_FamilyPatterns', 'D', 'patterns', [
        ('pattern', 'What repeats'), ('value', 'The sign, lord, planet or factor'),
        ('count', 'Members sharing it'), ('members', 'Who'), ('note', 'Note')]),
    ('AI_FamilyYogas', 'D', 'per_member', [
        ('member', 'Name'), ('relation', 'Relation'),
        ('yogas', 'Raja, Dhana, Dharma-Karmadhipati and Pancha Mahapurusha yogas found (rules as in AI_Yogas)'),
        ('ancestral_factors', 'Ancestral factors in this chart')]),
    ('AI_FamilyWindows', 'E', 'windows', [
        ('status', 'supportive / mixed / pressured, by the counted rule'), ('from', 'First month (YYYY-MM)'),
        ('to', 'Last month'), ('months', 'Number of months')]),
    ('AI_FamilyMonths', 'E', 'months', [
        ('month', 'Month (YYYY-MM), read at its middle'), ('status', 'Family status'),
        ('good', 'Weight of members in a good period (adult 1, under 18 0.5)'),
        ('pressured', 'Weight of members in a difficult period, or in sade sati or ashtama outside a good period'),
        ('jupiter_favourable', 'Weight of members with Jupiter favourable from the Moon'),
        ('weight', 'Total weight of the family that month'),
        ('members', 'Per member: dasa/bhukti and tag (G good, M mixed, D difficult; S sade sati, A ashtama; '
                    'J Jupiter favourable)')]),
    ('AI_FamilyPeriods', 'E', 'periods', [
        ('member', 'Name'), ('dasa', 'Mahadasa lord'), ('bhukti', 'Bhukti lord'),
        ('start_utc', 'Start (clipped to the range), UTC'), ('end_utc', 'End (clipped), UTC'),
        ('dasa_houses', 'Houses the dasa lord owns (Rahu/Ketu via their sign lord)'),
        ('dasa_quality', 'good / difficult / neutral'), ('bhukti_houses', 'Houses the bhukti lord owns'),
        ('bhukti_quality', 'good / difficult / neutral'),
        ('dasa_nature', 'Functional nature of the dasa lord (enrich.py rule)'),
        ('period', 'good / mixed / difficult for the member')]),
    ('AI_FamilySandhi', 'E', 'sandhi', [
        ('member_a', 'Member'), ('change_a', 'Change of mahadasa'), ('date_a', 'Date, UTC'),
        ('member_b', 'Other member'), ('change_b', 'Change of mahadasa'), ('date_b', 'Date, UTC'),
        ('months_apart', 'Months between the two')]),
    ('AI_FamilyTransitNow', 'F', 'now', [
        ('planet', 'Planet'), ('sign', 'Its sign now'), ('house_from_moon', 'House from the Moon'),
        ('members', 'Members for whom it is that house'), ('count', 'How many'),
        ('note', 'Sade sati / ashtama / ardhashtama; favourable; node axis'), ('line', 'The same in one line')]),
    ('AI_FamilyTransits', 'F', 'stays', [
        ('planet', 'Planet'), ('sign', 'Sign'), ('entry_utc', 'Entry, UTC (empty: before the range)'),
        ('exit_utc', 'Exit, UTC (empty: after the range)'), ('motion', 'direct / retrograde entry'),
        ('from_each_moon', 'House from each member\'s Moon, with its name')]),
    ('AI_FamilyTopics', 'G', 'topics', [
        ('topic', 'Property, Children, Education, Spouse, Foreign travel'), ('member', 'Name'),
        ('relation', 'Relation'), ('reading', 'supports / neutral / needs care'), ('facts', 'What was read')]),
    ('AI_FamilyShared', 'G', 'shared', [
        ('topic', 'Topic'), ('reading', 'supports / needs care'), ('count', 'Members'), ('members', 'Who')]),
]


def _flat_cell(value):
    if isinstance(value, dict):
        return '; '.join(f'{k}: {v}' for k, v in value.items())
    return value


def tables(result):
    """{'schema', 'sheets', 'columns', 'tables'} in the shape of enrich and match_engine."""
    names = {m['idx']: m['name'] for m in result['members']}
    readme = [
        'Family reading from horoscopegen.in, as flat tables for AI readers.',
        f'Schema {result["schema"]}. Every result is {result["label"]}.',
        f'Anchor (Self): {result["anchor"]}. Members: ' + ', '.join(f"{m['name']} ({m['relation']})"
                                                                for m in result['members']) + '.',
        f"Range: {result['settings']['from']} to {result['settings']['to']}; dasa sandhi within "
        f"{result['settings']['sandhi_months']} months.",
        'AI_FamilyRules holds every rule and the variant used. Houses are whole sign.',
        'An empty cell means "does not apply".',
    ]
    readme += [f'Not included: {x}.' for x in result['not_included']]
    data = {'AI_FamilyReadMe': [{'line': i, 'text': t} for i, t in enumerate(readme, 1)],
            'AI_FamilySummary': [{'section': x['section'], 'title': x['title'], 'text': x['text']}
                                 for x in result['summary']['lines']]}
    columns = {'AI_FamilyReadMe': [('line', 'Line'), ('text', 'What the AI_Family sheets are')],
               'AI_FamilySummary': [('section', 'Section'), ('title', 'Title'), ('text', 'Summary line')]}
    sheets = ['AI_FamilyReadMe', 'AI_FamilySummary']
    for sheet, sec, key, cols in TABLES:
        rows = result['sections'][sec][key]
        if sheet == 'AI_FamilyMonths':
            rows = [dict(r, members='; '.join(
                f"{names[i]}: {c['dasa']}/{c['bhukti']} {c['tag']}" for i, c in r['members'].items())) for r in rows]
        data[sheet] = [{c: _flat_cell(r.get(c)) for c, _ in cols} for r in rows]
        columns[sheet] = cols
        sheets.append(sheet)
    data['AI_FamilyRules'] = [{'name': r['name'], 'rule': r['rule']} for r in result['rules']]
    columns['AI_FamilyRules'] = [('name', 'Rule'), ('rule', 'The rule as applied and the variant used')]
    sheets.append('AI_FamilyRules')
    return {'schema': result['schema'], 'sheets': sheets,
            'columns': {s: [{'name': n, 'meaning': m} for n, m in columns[s]] for s in sheets},
            'tables': data}
