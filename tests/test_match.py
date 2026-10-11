"""
Tests for marriage matching (match_engine.py and POST /api/match).

Reference values that do not come from match_engine.py:
  * The star tables below (gana, rajju, nadi, yoni, vedha, same-star lists)
    are typed here in a different form from the engine's: one letter or word
    per star in star order, or as star numbers, taken from the published
    pages named in match_engine.TABLE_SOURCES.
  * `Reference` is a second statement of every rule of groups A to C, written
    with star and rasi numbers from 1. Every pair of the 108 padas with every
    other (11,664 pairs) is run through both. No published table of all
    pairs was found to compare with, so this catches a slip in the code, not
    a rule that was read wrongly from its source.
  * The pairs worked by hand, with the counting written out beside them.
  * A fact that follows from the rules alone: the same star, rasi and pada
    scores 28 of 36 (every Ashtakoota row in full except Nadi).
  * The request limit of the route is written here as a plain figure:
    15 matches a minute for one visitor.

No test here reaches the network.
"""
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import astro_engine as A          # noqa: E402
import match_engine as M          # noqa: E402

NOW = datetime(2026, 10, 3, 20, 0)
STARS = ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
         'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha',
         'Jyeshtha', 'Moola', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
         'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati']
SIGNS = ['Mesha', 'Rishabha', 'Mithuna', 'Kataka', 'Simha', 'Kanya', 'Thula', 'Vrischika', 'Dhanu', 'Makara',
         'Kumbha', 'Meena']

# One letter per star, Ashwini first. D deva, M manushya, R rakshasa.
GANA = 'DMRMDMDDRRMMDRDRDRRMMDRRMMD'
# P pada, K kati, N nabhi, C kantha, S siro: up the body and down again, three times.
RAJJU = 'PKNCSCNKP' * 3
# A aadi, M madhya, Z antya.
NADI = 'AMZZMA' * 4 + 'AMZ'
YONI = ['Horse', 'Elephant', 'Sheep', 'Serpent', 'Serpent', 'Dog', 'Cat', 'Sheep', 'Cat', 'Rat', 'Rat', 'Cow',
        'Buffalo', 'Tiger', 'Buffalo', 'Tiger', 'Deer', 'Deer', 'Dog', 'Monkey', 'Mongoose', 'Monkey', 'Lion',
        'Horse', 'Lion', 'Cow', 'Elephant']
ENEMIES = ['Cow Tiger', 'Elephant Lion', 'Horse Buffalo', 'Dog Deer', 'Cat Rat', 'Serpent Mongoose',
           'Sheep Monkey']
# Vedha, by star number: twelve pairs and one set of three.
VEDHA = [(1, 18), (2, 17), (3, 16), (4, 15), (6, 22), (7, 21), (8, 20), (9, 19), (10, 27), (11, 26), (12, 25),
         (13, 24), (5, 14, 23)]
# The same star for both: + matched, o medium, - not matched.
SAME_STAR = 'o-o+o+oo-+oo+o-+o--oo+---++'
# A milk tree: y, or not: n (grouping of horoscope.hosuronline.com).
PAAL = 'nnyynnnyyyyyynnnnyyyyynnyny'
SIGN_LORD = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
             'Saturn', 'Jupiter']
# Natural friendship: friends and enemies of each planet; the rest are neutral.
FRIENDS = {'Sun': 'Moon Mars Jupiter', 'Moon': 'Sun Mercury', 'Mars': 'Sun Moon Jupiter', 'Mercury': 'Sun Venus',
           'Jupiter': 'Sun Moon Mars', 'Venus': 'Mercury Saturn', 'Saturn': 'Mercury Venus'}
FOES = {'Sun': 'Venus Saturn', 'Moon': '', 'Mars': 'Mercury', 'Mercury': 'Moon', 'Jupiter': 'Mercury Venus',
        'Venus': 'Sun Moon', 'Saturn': 'Sun Moon Mars'}
VASYA = {1: (5, 8), 2: (4, 7), 3: (6,), 4: (8, 9), 5: (7,), 6: (12, 3), 7: (10, 6), 8: (4,), 9: (12,),
         10: (1, 11), 11: (1,), 12: (10,)}
# Varna by rasi number, 4 the highest.
VARNA_RANK = {4: 4, 8: 4, 12: 4, 1: 3, 5: 3, 9: 3, 2: 2, 6: 2, 10: 2, 3: 1, 7: 1, 11: 1}
VASHYA_ORDER = ['Chatushpada', 'Manava', 'Jalachara', 'Vanachara', 'Keeta']
# Rows the girl, columns the boy, in VASHYA_ORDER (vedicmarga.com).
VASHYA_TABLE = [[2, 1, 1, 0.5, 1], [1, 2, 0.5, 0, 1], [1, 0.5, 2, 1, 1], [0, 0, 0, 2, 0], [1, 1, 1, 0, 2]]
# Rows the girl, columns the boy: deva, manushya, rakshasa (vedicmarga.com).
GANA_TABLE = {'D': {'D': 6, 'M': 5, 'R': 1}, 'M': {'D': 6, 'M': 6, 'R': 0}, 'R': {'D': 0, 'M': 0, 'R': 6}}


def person(pada_index, name=None):
    """Star-only record for one of the 108 padas (0 = Ashwini pada 1)."""
    record = {'nakshatra': pada_index // 4 + 1, 'pada': pada_index % 4 + 1}
    if name:
        record['name'] = name
    return record


def star(name, pada=None, rasi=None):
    record = {'nakshatra': name}
    if pada:
        record['pada'] = pada
    if rasi:
        record['rasi'] = rasi
    return record


def rows(boy, girl):
    return {r['key']: r for r in M.match(boy, girl)['rows']}


def results(boy, girl):
    return {k: r['result'] for k, r in rows(boy, girl).items()}


# ── the tables ────────────────────────────────────────────────────────────────

def test_engine_names_are_the_ones_the_tables_use():
    assert A.NAKS == STARS and A.RASIS == SIGNS and A.SIGN_LORDS == SIGN_LORD


def test_star_tables_match_the_published_lists():
    assert len(GANA) == len(RAJJU) == len(NADI) == len(SAME_STAR) == len(PAAL) == len(YONI) == 27
    assert [g[0] for g in M.GANA] == list(GANA)
    assert [{'Pada': 'P', 'Kati': 'K', 'Nabhi': 'N', 'Kantha': 'C', 'Siro': 'S'}[r] for r in M.RAJJU] == list(RAJJU)
    assert [{'Aadi': 'A', 'Madhya': 'M', 'Antya': 'Z'}[n] for n in M.NADI] == list(NADI)
    assert M.YONI == YONI
    assert [{M.MATCHED: '+', M.MEDIUM: 'o', M.NOT_MATCHED: '-'}[s] for s in M.SAME_STAR] == list(SAME_STAR)
    assert ['y' if p else 'n' for p in M.PAAL] == list(PAAL)


def test_group_sizes():
    assert sorted(GANA.count(c) for c in 'DMR') == [9, 9, 9]
    assert [RAJJU.count(c) for c in 'PKNCS'] == [6, 6, 6, 6, 3]
    assert [NADI.count(c) for c in 'AMZ'] == [9, 9, 9]
    assert sorted(YONI.count(a) for a in set(YONI)) == [1] + [2] * 13      # the mongoose has one star
    assert [SAME_STAR.count(c) for c in '+o-'] == [8, 11, 8]
    assert PAAL.count('y') == 15


def test_vedha_sets():
    engine = sorted(sorted(i + 1 for i, v in enumerate(M.VEDHA) if v == g) for g in set(M.VEDHA))
    assert engine == sorted(sorted(s) for s in VEDHA)
    assert sorted(n for s in VEDHA for n in s) == list(range(1, 28))        # every star once
    # The pairs mirror each other inside three runs of the zodiac.
    assert {a + b for a, b in VEDHA[:4]} == {19} and {a + b for a, b in VEDHA[4:8]} == {28}
    assert {a + b for a, b in VEDHA[8:12]} == {37}


def test_yoni_points_table():
    table, order = M.YONI_POINTS, M.YONI_ORDER
    assert len(table) == 14 and all(len(row) == 14 for row in table) and set(order) == set(YONI)
    for i, a in enumerate(order):
        assert table[i][i] == 4
        for j, b in enumerate(order):
            assert table[i][j] == table[j][i], (a, b)
            enemies = f'{a} {b}' in ENEMIES or f'{b} {a}' in ENEMIES
            assert (table[i][j] == 0) == enemies, (a, b)
    # Cells quoted from the published table (saravali.github.io).
    quoted = {('Horse', 'Serpent'): 3, ('Horse', 'Cow'): 1, ('Elephant', 'Sheep'): 3, ('Elephant', 'Tiger'): 1,
              ('Dog', 'Monkey'): 2, ('Cat', 'Deer'): 3, ('Cow', 'Buffalo'): 3, ('Tiger', 'Lion'): 1,
              ('Monkey', 'Mongoose'): 3, ('Rat', 'Lion'): 2}
    for (a, b), points in quoted.items():
        assert M.yoni_points(a, b) == M.yoni_points(b, a) == points


def test_points_tables():
    assert [[M.VASHYA_POINTS[g][b] for b in VASHYA_ORDER] for g in VASHYA_ORDER] == VASHYA_TABLE
    full = {'D': 'Deva', 'M': 'Manushya', 'R': 'Rakshasa'}
    assert {g: {b: M.GANA_POINTS[full[g]][full[b]] for b in 'DMR'} for g in 'DMR'} == GANA_TABLE
    assert {SIGNS.index(s) + 1: 4 - M.VARNA_ORDER.index(v) for s, v in M.VARNA.items()} == VARNA_RANK
    assert {SIGNS.index(s) + 1: tuple(SIGNS.index(x) + 1 for x in v) for s, v in M.VASYA.items()} == VASYA
    assert M.DINAM_COUNTS == (2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26)
    assert M.MAHENDRAM_COUNTS == (4, 7, 10, 13, 16, 19, 22, 25)


def test_every_check_has_a_rule_and_every_rule_is_listed():
    out = M.match(person(13), person(52))
    assert {r['key'] for r in out['rows']} == set(M.CHECKS)
    names = [r['name'] for r in out['rules']]
    assert len(names) == len(set(names))
    for group, name, rule, variant in M.CHECKS.values():
        listed = next(r['rule'] for r in out['rules'] if r['name'].endswith(': ' + name))
        assert rule in listed and variant in listed
    for r in out['rows']:
        assert r['rule_applied'] == M.CHECKS[r['key']][2] and r['result'] in M.RESULTS
        assert set(r) == {'key', 'group', 'name', 'boy_value', 'girl_value', 'result', 'points', 'max_points',
                          'rule_applied', 'exception_applied', 'note'}


# ── a second statement of the rules, with numbers from 1 ──────────────────────

def relation(a, b):
    return 'F' if b in FRIENDS[a].split() else ('E' if b in FOES[a].split() else 'N')


class Reference:
    """Groups A to C for a pair of padas (0 to 107), written apart from the engine."""

    def __init__(self, boy, girl):
        self.bs, self.gs = boy // 4 + 1, girl // 4 + 1              # stars, 1 to 27
        self.bp = boy % 4 + 1                                       # boy's pada
        self.gp = girl % 4 + 1
        self.br, self.gr = boy // 9 + 1, girl // 9 + 1              # rasis, 1 to 12
        n = self.bs - self.gs + 1
        self.n = n if n >= 1 else n + 27                            # boy's star from the girl's
        m = self.gs - self.bs + 1
        self.m = m if m >= 1 else m + 27
        r = self.br - self.gr + 1
        self.r = r if r >= 1 else r + 12
        bl, gl = SIGN_LORD[self.br - 1], SIGN_LORD[self.gr - 1]
        self.same_lord = bl == gl
        self.rel = '' if self.same_lord else ''.join(sorted(relation(bl, gl) + relation(gl, bl)))
        self.friends = self.same_lord or self.rel == 'FF'
        self.boy_deg = (boy % 9) * 10 / 3                            # start of his pada inside the rasi
        self.girl_deg = (girl % 9) * 10 / 3

    def vashya(self, rasi, deg):
        if rasi in (9, 10):
            if deg < 15 < deg + 10 / 3:
                return None                                         # the pada lies across 15 degrees
            first = deg + 10 / 3 <= 15
            return ('Manava' if first else 'Chatushpada') if rasi == 9 else ('Chatushpada' if first else 'Jalachara')
        return {1: 'Chatushpada', 2: 'Chatushpada', 3: 'Manava', 4: 'Jalachara', 5: 'Vanachara', 6: 'Manava',
                7: 'Manava', 8: 'Keeta', 11: 'Manava', 12: 'Jalachara'}[rasi]

    def nadi_exception(self):
        if self.br == self.gr and self.bs != self.gs:
            return 'The same rasi with different stars'
        if self.bs == self.gs and self.br != self.gr:
            return 'The same star with different rasis'
        if self.bs == self.gs and self.bp != self.gp:
            return 'The same star with different padas'
        return None

    def expected(self):
        yes, mid, no, na = 'matched', 'medium', 'not matched', 'not applicable'
        same_star = {'+': yes, 'o': mid, '-': no}[SAME_STAR[self.bs - 1]]
        out, points, exc = {}, {}, {}
        n, m, r = self.n, self.m, self.r
        bs, gs = self.bs - 1, self.gs - 1

        if n == 1:
            out['dinam'] = same_star
        elif n == 27:
            out['dinam'] = yes if self.br == self.gr else no
        else:
            out['dinam'] = yes if n in (2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26) else no
        gana = GANA_TABLE[GANA[gs]][GANA[bs]]
        out['ganam'] = {6: yes, 5: mid}.get(gana, no)
        out['mahendram'] = yes if n % 3 == 1 and n > 1 else no
        out['stree_deergham'] = yes if n >= 14 else (mid if n >= 8 else no)
        hostile = f'{YONI[bs]} {YONI[gs]}' in ENEMIES or f'{YONI[gs]} {YONI[bs]}' in ENEMIES
        out['yoni'] = yes if YONI[bs] == YONI[gs] else (no if hostile else mid)
        if r == 7 and {self.br, self.gr} in ({5, 11}, {4, 10}):
            out['rasi'] = no
        else:
            out['rasi'] = yes if r in (1, 7) else (no if r in (2, 6, 8, 12) else mid)
        out['rasi_adhipathi'] = yes if self.friends else (no if 'E' in self.rel else mid)
        out['vasiyam'] = yes if self.br in VASYA[self.gr] else (mid if self.gr in VASYA[self.br] else no)
        out['rajju'] = no if RAJJU[bs] == RAJJU[gs] else yes
        vedha = any(self.bs in s and self.gs in s for s in VEDHA) and self.bs != self.gs
        out['vedhai'] = no if vedha else yes
        out['nadi'] = no if NADI[bs] == NADI[gs] else yes
        out['vriksha'] = yes if 'y' in (PAAL[bs], PAAL[gs]) else no

        def tara(k):
            t = k % 9
            return no if t in (3, 5, 7) else (mid if t == 1 else yes)
        out['tara_boy'], out['tara_girl'] = tara(n), tara(m)
        out['vadha'] = no if n == 7 else yes
        out['vainasika'] = no if n == 22 else yes
        out['vainasika_pada'] = no if n == 22 and self.bp == 4 else yes
        out['star_27'] = (yes if self.br == self.gr else no) if n == 27 else na
        out['eka_nakshatra'] = same_star if n == 1 else na
        if self.br != self.gr or n == 1:
            out['eka_rasi'] = na
        else:
            out['eka_rasi'] = yes if self.bs < self.gs else mid

        points['ak_varna'] = 1 if VARNA_RANK[self.br] >= VARNA_RANK[self.gr] else 0
        bv, gv = self.vashya(self.br, self.boy_deg), self.vashya(self.gr, self.girl_deg)
        points['ak_vashya'] = (None if None in (bv, gv) else
                               VASHYA_TABLE[VASHYA_ORDER.index(gv)][VASHYA_ORDER.index(bv)])
        points['ak_tara'] = 1.5 * ((n % 9 not in (3, 5, 7)) + (m % 9 not in (3, 5, 7)))
        points['ak_yoni'] = M.YONI_POINTS[M.YONI_ORDER.index(YONI[gs])][M.YONI_ORDER.index(YONI[bs])]
        points['ak_graha_maitri'] = 5 if self.same_lord else {'FF': 5, 'FN': 4, 'NN': 3, 'EF': 1, 'EN': 0.5,
                                                              'EE': 0}[self.rel]
        points['ak_gana'] = gana
        points['ak_bhakoot'] = 0 if r in (2, 12, 5, 9, 6, 8) else 7
        points['ak_nadi'] = 0 if NADI[bs] == NADI[gs] else 8
        top = {'ak_varna': 1, 'ak_vashya': 2, 'ak_tara': 3, 'ak_yoni': 4, 'ak_graha_maitri': 5, 'ak_gana': 6,
               'ak_bhakoot': 7, 'ak_nadi': 8}
        for key, p in points.items():
            out[key] = na if p is None else (yes if p == top[key] else (no if p == 0 else mid))

        lords = self.friends
        exc['rasi'] = (out['rasi'] == no) and (lords or r == 7)
        exc['ak_gana'] = gana < 6 and lords
        exc['ak_bhakoot'] = points['ak_bhakoot'] == 0 and lords
        exc['nadi'] = exc['ak_nadi'] = NADI[bs] == NADI[gs] and self.nadi_exception() is not None
        exc['dinam'] = n in (1, 27)
        return out, points, exc


def test_every_pair_of_padas_against_the_second_statement_of_the_rules():
    people = [M.star_person(person(i), 'boy') for i in range(108)]
    wrong = []
    for b in range(108):
        for g in range(108):
            pair = M.Pair(dict(people[b], role='boy'), dict(people[g], role='girl'))
            M._group_a(pair)
            M._group_b(pair)
            M._group_c(pair)
            got = {r['key']: r for r in pair.rows}
            out, points, exc = Reference(b, g).expected()
            assert set(got) == set(out)
            for key, result in out.items():
                row = got[key]
                if row['result'] != result or (key in points and row['points'] != points[key]):
                    wrong.append((b, g, key, row['result'], result, row['points'], points.get(key)))
                elif key in exc and bool(row['exception_applied']) != exc[key]:
                    wrong.append((b, g, key, 'exception', row['exception_applied'], exc[key]))
    assert not wrong, wrong[:10]


def test_the_grid_reaches_every_result_of_every_row():
    """A rule that could never fail, or never pass, would pass the grid test unnoticed."""
    seen = {}
    for b in range(108):
        for g in range(108):
            out, _, _ = Reference(b, g).expected()
            for key, result in out.items():
                seen.setdefault(key, set()).add(result)
    yes, mid, no, na = 'matched', 'medium', 'not matched', 'not applicable'
    two = {yes, no}
    want = {key: {yes, mid, no} for key in seen}
    want.update({key: two for key in ('rajju', 'vedhai', 'nadi', 'vriksha', 'mahendram', 'vadha', 'vainasika',
                                      'vainasika_pada', 'ak_varna', 'ak_bhakoot', 'ak_nadi')})
    want.update({'star_27': {yes, no, na}, 'eka_nakshatra': {yes, mid, no, na}, 'eka_rasi': {yes, mid, na},
                 'ak_vashya': {yes, mid, no, na},
                 # The two counts add up to 29, so both cannot leave a remainder of 3, 5 or 7 by 9.
                 'ak_tara': {yes, mid}})
    assert seen == want


# ── pairs worked by hand ──────────────────────────────────────────────────────

def test_rohini_boy_and_chitra_girl():
    """
    Girl Chitra (14th star, pada 1: Kanya), boy Rohini (4th star: Rishabha).
    Chitra to Revati is 14 stars, then Ashwini to Rohini 4 more: the 18th.
    Kanya to Meena is 7 rasis, then Mesha, Rishabha: the 9th.
    """
    got = rows(star('Rohini', 2), star('Chitra', 1))
    assert got['dinam']['note'] == "The boy's star is the 18th from the girl's star"
    assert got['rasi']['note'] == "The boy's rasi is the 9th from the girl's rasi"
    want = {'dinam': 'matched',            # 18 is on the list
            'ganam': 'not matched',        # girl rakshasa, boy manushya
            'mahendram': 'not matched',    # 18 is not 4, 7, 10 ...
            'stree_deergham': 'matched',   # more than 13
            'yoni': 'medium',              # serpent and tiger: different, not enemies
            'rasi': 'medium',              # the 9th
            'rasi_adhipathi': 'matched',   # Venus and Mercury are friends
            'vasiyam': 'not matched',      # Kanya: Meena, Mithuna; Rishabha: Kataka, Thula
            'rajju': 'matched',            # kantha and siro
            'vedhai': 'matched', 'nadi': 'matched',      # antya and madhya
            'vriksha': 'matched',          # Rohini has a milk tree
            'tara_boy': 'matched',         # 18 = 9 + 9: the 9th tara, Parama Mitra
            'tara_girl': 'matched',        # the 11th: 2nd tara, Sampat
            'vadha': 'matched', 'vainasika': 'matched', 'vainasika_pada': 'matched',
            'star_27': 'not applicable', 'eka_nakshatra': 'not applicable', 'eka_rasi': 'not applicable'}
    assert {k: got[k]['result'] for k in want} == want
    points = {k: got[k]['points'] for k in got if k.startswith('ak_')}
    # varna 1 (both Vaishya), vashya 1 (girl manava, boy chatushpada), tara 3, yoni 2, maitri 5,
    # gana 0, bhakoot 0 (5/9), nadi 8
    assert points == {'ak_varna': 1, 'ak_vashya': 1, 'ak_tara': 3, 'ak_yoni': 2, 'ak_graha_maitri': 5,
                      'ak_gana': 0, 'ak_bhakoot': 0, 'ak_nadi': 8}
    summary = M.match(star('Rohini', 2), star('Chitra', 1))['summary']
    assert summary['ashtakoota'] == {'points': 20, 'max_points': 36, 'rows_scored': 8, 'rows': 8}
    assert summary['ten_poruthams'] == {'matched': 5, 'medium': 2, 'not_matched': 3, 'not_applicable': 0,
                                        'information': 0, 'of': 10}
    assert summary['key_poruthams_not_matched'] == ['Ganam']
    assert summary['label'] == 'rule-based, not a prediction'
    assert got['ak_bhakoot']['exception_applied'] == 'The rasi lords are friends to each other (Venus, Mercury)'


def test_the_seventh_and_the_twenty_second_star_are_one_pair_seen_from_each_side():
    # Ashwini 1, Punarvasu 7.
    got = rows(star('Punarvasu', 4), star('Ashwini'))
    assert (got['vadha']['result'], got['vainasika']['result']) == ('not matched', 'matched')
    assert got['tara_boy']['boy_value'] == 'Vadha' and got['tara_boy']['result'] == 'not matched'
    back = rows(star('Ashwini', 2), star('Punarvasu', 4))
    assert back['dinam']['note'] == "The boy's star is the 22nd from the girl's star"
    assert (back['vadha']['result'], back['vainasika']['result']) == ('matched', 'not matched')
    assert back['dinam']['result'] == 'not matched'          # 22 is not on the Tamil list
    assert back['mahendram']['result'] == 'matched'           # 22 is on the Mahendram list
    for n in range(2, 28):
        assert n + (29 - n) == 29                             # boy's count + girl's count is 29 when stars differ
    for b in range(27):
        for g in range(27):
            if b != g:
                assert M.count(g, b) + M.count(b, g) == 29


@pytest.mark.parametrize('pada,result', [(1, 'matched'), (2, 'matched'), (3, 'matched'), (4, 'not matched'),
                                         (None, 'not applicable')])
def test_vainasika_pada_is_the_fourth_pada_of_the_22nd_star(pada, result):
    # Girl Bharani (2nd star); the 22nd from it is Dhanishtha (23rd). Pada 4 of Dhanishtha is in Kumbha.
    boy = star('Dhanishtha', pada, None if pada else 'Kumbha')
    got = rows(boy, star('Bharani'))
    assert got['vainasika']['result'] == 'not matched' and got['vainasika_pada']['result'] == result
    # The 88th pada counted from the first pada of the girl's star: 21 stars of 4 padas, then 4.
    assert 21 * 4 + 4 == 88


def test_the_27th_star():
    one_rasi = rows(star('Ashwini'), star('Bharani'))                 # both in Mesha
    assert one_rasi['star_27']['result'] == 'matched' and one_rasi['dinam']['result'] == 'matched'
    assert one_rasi['dinam']['exception_applied'] == 'The 27th star: judged by the 27th-star rule'
    two_rasis = rows(star('Revati'), star('Ashwini'))                 # Meena and Mesha
    assert two_rasis['star_27']['result'] == 'not matched' and two_rasis['dinam']['result'] == 'not matched'
    assert two_rasis['rasi']['note'] == "The boy's rasi is the 12th from the girl's rasi"
    # Krittika lies in two rasis: the 27th star from Rohini is in the same rasi only from pada 2.
    assert rows(star('Krittika', 2), star('Rohini'))['star_27']['result'] == 'matched'
    assert rows(star('Krittika', 1), star('Rohini'))['star_27']['result'] == 'not matched'


def test_the_same_star():
    for i, name in enumerate(STARS):
        got = rows(star(name, 1), star(name, 1))
        want = {'+': 'matched', 'o': 'medium', '-': 'not matched'}[SAME_STAR[i]]
        assert got['eka_nakshatra']['result'] == got['dinam']['result'] == want
        assert got['eka_nakshatra']['note'] == 'The padas are the same'
        assert got['eka_rasi']['result'] == 'not applicable'
        assert got['vedhai']['result'] == 'matched'
        assert got['rajju']['result'] == got['nadi']['result'] == 'not matched'
    assert rows(star('Rohini', 1), star('Rohini', 3))['eka_nakshatra']['note'] == 'The padas are different'
    assert rows(star('Rohini'), star('Rohini', 3))['eka_nakshatra']['note'] == 'A pada was not given'


def test_the_same_star_rasi_and_pada_scores_28():
    """Every Ashtakoota row in full except Nadi: 1 + 2 + 3 + 4 + 5 + 6 + 7 = 28."""
    for i in range(108):
        summary = M.match(person(i), person(i))['summary']['ashtakoota']
        if summary['rows_scored'] == 8:
            assert summary['points'] == 28
        else:                       # the pada lies across 15 degrees of Dhanu or Makara: Vashya is not scored
            assert i in (19 * 4, 21 * 4 + 1) and summary == {'points': 26, 'max_points': 36, 'rows_scored': 7,
                                                             'rows': 8}


def test_the_same_rasi():
    # Mesha holds Ashwini, Bharani and the first pada of Krittika, in that order.
    assert results(star('Ashwini'), star('Krittika', 1))['eka_rasi'] == 'matched'
    assert results(star('Krittika', 1), star('Bharani'))['eka_rasi'] == 'medium'
    assert results(star('Krittika', 2), star('Bharani'))['eka_rasi'] == 'not applicable'


def test_rasi_rule():
    def rasi(boy, girl):
        r = rows(star(boy), star(girl))['rasi']
        return r['result'], r['exception_applied']
    # Stars that lie wholly in one rasi: Ashwini Mesha, Rohini Rishabha, Ardra Mithuna, Pushya Kataka,
    # Magha Simha, Hasta Kanya, Swati Thula, Anuradha Vrischika, Moola Dhanu, Shravana Makara,
    # Shatabhisha Kumbha, Revati Meena.
    assert rasi('Ashwini', 'Ashwini') == ('matched', None)
    assert rasi('Swati', 'Ashwini') == ('matched', None)                                  # the 7th
    assert rasi('Shatabhisha', 'Magha') == ('not matched', 'The 7th is not accepted for Simha with Kumbha')
    assert rasi('Pushya', 'Shravana') == ('not matched', 'The 7th is not accepted for Makara with Kataka')
    assert rasi('Rohini', 'Ashwini') == ('not matched', None)                             # 2nd: Mars, Venus
    assert rasi('Anuradha', 'Ashwini') == ('not matched', 'One lord for both rasis (Mars)')    # the 8th
    assert rasi('Ashwini', 'Anuradha') == ('not matched', 'One lord for both rasis (Mars)')    # the 6th
    assert rasi('Shatabhisha', 'Shravana') == ('not matched', 'One lord for both rasis (Saturn)')
    assert rasi('Magha', 'Pushya') == ('not matched',
                                       'The rasi lords are friends to each other (Sun, Moon)')  # the 2nd
    assert rasi('Ardra', 'Ashwini')[0] == rasi('Magha', 'Ashwini')[0] == 'medium'         # 3rd, 5th


def test_ganam_follows_who_is_the_girl():
    # Ashwini deva, Bharani manushya, Krittika rakshasa.
    assert results(star('Ashwini'), star('Bharani'))['ganam'] == 'matched'       # girl manushya, boy deva
    assert results(star('Bharani'), star('Ashwini'))['ganam'] == 'medium'        # girl deva, boy manushya
    assert results(star('Krittika', 1), star('Ashwini'))['ganam'] == 'not matched'
    assert results(star('Ashwini'), star('Krittika', 1))['ganam'] == 'not matched'
    assert rows(star('Krittika', 1), star('Ashwini'))['ak_gana']['points'] == 1
    assert rows(star('Ashwini'), star('Krittika', 1))['ak_gana']['points'] == 0


def test_vasiyam_follows_who_is_the_girl():
    # For Mesha, Simha and Vrischika are vasya.
    assert results(star('Magha'), star('Ashwini'))['vasiyam'] == 'matched'       # boy Simha, girl Mesha
    assert results(star('Ashwini'), star('Magha'))['vasiyam'] == 'medium'
    assert results(star('Rohini'), star('Ashwini'))['vasiyam'] == 'not matched'


def test_nadi_exceptions_are_named_and_do_not_change_the_result():
    # Ashwini and Ardra are both aadi, in different rasis: no exception.
    got = rows(star('Ashwini'), star('Ardra'))
    assert (got['nadi']['result'], got['nadi']['exception_applied']) == ('not matched', None)
    assert (got['ak_nadi']['points'], got['ak_nadi']['exception_applied']) == (0, None)
    # Punarvasu and Ardra are both aadi; Punarvasu 1 to 3 is in Mithuna with Ardra.
    got = rows(star('Punarvasu', 1), star('Ardra'))
    assert got['nadi']['exception_applied'] == got['ak_nadi']['exception_applied'] == \
        'The same rasi with different stars'
    assert got['ak_nadi']['points'] == 0 and got['nadi']['result'] == 'not matched'
    got = rows(star('Punarvasu', 1), star('Punarvasu', 4))
    assert got['ak_nadi']['exception_applied'] == 'The same star with different rasis'
    got = rows(star('Punarvasu', 1), star('Punarvasu', 2))
    assert got['ak_nadi']['exception_applied'] == 'The same star with different padas'
    assert rows(star('Punarvasu', 1), star('Punarvasu', 1))['ak_nadi']['exception_applied'] is None


# ── direction ─────────────────────────────────────────────────────────────────

def test_rajju_vedhai_yoni_and_nadi_do_not_depend_on_who_is_the_boy():
    for b in range(0, 108, 2):
        for g in range(1, 108, 3):
            one, other = results(person(b), person(g)), results(person(g), person(b))
            for key in ('rajju', 'vedhai', 'yoni', 'nadi', 'vriksha', 'rasi_adhipathi', 'ak_yoni',
                        'ak_graha_maitri', 'ak_bhakoot', 'ak_nadi', 'ak_tara'):
                assert one[key] == other[key], (b, g, key)


def test_dinam_and_stree_deergham_depend_on_who_is_the_boy():
    # Girl Ashwini, boy Rohini: the 4th. The other way round, Rohini to Revati is 24 stars and Ashwini
    # one more: the 25th.
    one, other = results(star('Rohini'), star('Ashwini')), results(star('Ashwini'), star('Rohini'))
    assert (one['dinam'], other['dinam']) == ('matched', 'not matched')              # 4 is listed, 25 is not
    assert (one['stree_deergham'], other['stree_deergham']) == ('not matched', 'matched')
    # Girl Ashwini, boy Krittika: the 3rd; the other way round the 26th.
    one, other = results(star('Krittika', 1), star('Ashwini')), results(star('Ashwini'), star('Krittika', 1))
    assert (one['dinam'], other['dinam']) == ('not matched', 'matched')
    # Girl Ashwini, boy Mrigashira: the 5th; the other way round the 24th.
    one, other = results(star('Mrigashira', 1), star('Ashwini')), results(star('Ashwini'), star('Mrigashira', 1))
    assert (one['dinam'], other['dinam']) == ('not matched', 'matched')
    differs = {key: sum(results(person(b), person(g))[key] != results(person(g), person(b))[key]
                        for b in range(0, 108, 4) for g in range(0, 108, 4))
               for key in ('dinam', 'stree_deergham', 'ganam', 'vasiyam', 'tara_boy', 'vadha', 'vainasika')}
    assert all(differs.values()), differs


def test_mahendram_is_counted_from_the_girl_but_comes_out_the_same_both_ways():
    """
    The list 4, 7, 10 ... 25 is every count that leaves 1 when divided by 3.
    The two counts add up to 29, which leaves 2, so when one count is on the
    list the other is too: 4 and 25, 7 and 22, 10 and 19, 13 and 16.
    """
    assert [n for n in range(2, 28) if n % 3 == 1] == list(M.MAHENDRAM_COUNTS)
    assert all((29 - n) in M.MAHENDRAM_COUNTS for n in M.MAHENDRAM_COUNTS)
    for b in range(0, 108, 4):
        for g in range(0, 108, 4):
            assert results(person(b), person(g))['mahendram'] == results(person(g), person(b))['mahendram']
    assert results(star('Rohini'), star('Ashwini'))['mahendram'] == 'matched'          # the 4th


# ── star-only records ─────────────────────────────────────────────────────────

def test_a_star_given_by_number_or_by_name_is_the_same_person():
    by_name = M.star_person({'nakshatra': 'purva phalguni', 'pada': '3', 'rasi': 'SIMHA', 'name': ' Kumar '}, 'boy')
    by_number = M.star_person({'nakshatra': 11, 'pada': 3, 'rasi': 5, 'name': 'Kumar'}, 'boy')
    assert by_name == by_number and by_name['name'] == 'Kumar'
    assert M.star_person({'nakshatra': '11'}, 'girl')['rasi'] == 4 and M.star_person({'nakshatra': 11}, 'girl')['name'] == 'Girl'


def test_the_rasi_of_every_pada():
    # 9 padas to a rasi: Ashwini 1-4, Bharani 1-4, Krittika 1 are Mesha, and so on round the zodiac.
    for i in range(108):
        p = M.star_person(person(i), 'boy')
        assert (p['nak'], p['pada'], p['rasi']) == (i // 4, i % 4 + 1, i // 9)
    split = [s for s in range(27) if (s * 4) // 9 != (s * 4 + 3) // 9]
    assert [STARS[s] for s in split] == ['Krittika', 'Mrigashira', 'Punarvasu', 'Uttara Phalguni', 'Chitra',
                                         'Vishakha', 'Uttara Ashadha', 'Dhanishtha', 'Purva Bhadrapada']
    # A star in two rasis with the rasi given and no pada.
    assert M.star_person({'nakshatra': 'Krittika', 'rasi': 'Rishabha'}, 'boy')['pada'] is None


@pytest.mark.parametrize('record,message', [
    ({}, "The boy's nakshatra is required."),
    ({'nakshatra': 0}, "The boy's nakshatra must be a whole number from 1 to 27."),
    ({'nakshatra': 28}, "The boy's nakshatra must be a whole number from 1 to 27."),
    ({'nakshatra': 3.5}, "The boy's nakshatra must be a whole number from 1 to 27."),
    ({'nakshatra': True}, "The boy's nakshatra is required."),
    ({'nakshatra': 'Abhijit'}, '"Abhijit" is not a boy\'s nakshatra this service knows.'),
    ({'nakshatra': 'Rohini', 'pada': 5}, "The boy's pada must be 1, 2, 3 or 4."),
    ({'nakshatra': 'Rohini', 'pada': 'x'}, "The boy's pada must be 1, 2, 3 or 4."),
    ({'nakshatra': 'Rohini', 'rasi': 13}, "The boy's rasi must be a whole number from 1 to 12."),
    ({'nakshatra': 'Rohini', 'rasi': 'Mesha'}, 'Rohini is in Rishabha, not in Mesha.'),
    ({'nakshatra': 'Krittika'}, "Krittika lies in Mesha and Rishabha: give the boy's pada or rasi."),
    ({'nakshatra': 'Krittika', 'rasi': 'Mithuna'}, 'Krittika is in Mesha or Rishabha, not in Mithuna.'),
    ({'nakshatra': 'Krittika', 'pada': 1, 'rasi': 'Rishabha'}, 'Krittika pada 1 is in Mesha, not in Rishabha.'),
    ('Rohini', 'The details of the boy must be a JSON object.'),
])
def test_a_star_record_that_cannot_be_read(record, message):
    with pytest.raises(A.InputError) as e:
        M.star_person(record, 'boy')
    assert str(e.value) == message


def test_vashya_needs_the_degree_only_across_15_degrees_of_dhanu_and_makara():
    # Dhanu: Moola 1-4 (0 to 13°20'), Purva Ashadha 1 (13°20' to 16°40') ... ; Makara: Uttara Ashadha 2-4,
    # Shravana 1 (10° to 13°20'), Shravana 2 (13°20' to 16°40') ...
    def group(name, pada):
        return M.vashya_group(M.star_person(star(name, pada), 'boy'))
    assert group('Moola', 4) == 'Manava' and group('Purva Ashadha', 1) is None
    assert group('Purva Ashadha', 2) == 'Chatushpada' and group('Uttara Ashadha', 1) == 'Chatushpada'
    assert group('Uttara Ashadha', 2) == 'Chatushpada' and group('Shravana', 1) == 'Chatushpada'
    assert group('Shravana', 2) is None and group('Shravana', 3) == 'Jalachara'
    assert M.vashya_group(M.star_person(star('Krittika', None, 'Mesha'), 'boy')) == 'Chatushpada'
    got = rows(star('Purva Ashadha', 1), star('Rohini'))['ak_vashya']
    assert (got['result'], got['points'], got['max_points']) == ('not applicable', None, 2)
    # With birth details the degree is known.
    for lon, want in ((254.9, 'Manava'), (255.0, 'Chatushpada'), (284.9, 'Chatushpada'), (285.0, 'Jalachara')):
        assert M.vashya_group({'rasi': int(lon // 30), 'moon_lon': lon, 'nak': 0, 'pada': 1}) == want


# ── two horoscopes ────────────────────────────────────────────────────────────

BOY = dict(name='Sample Native', dob='1998-03-06', tob='01:37', pob='Delhi', lat=28.6139, lon=77.2090)
GIRL = dict(name='Sample Bride', dob='2000-07-15', tob='14:20', pob='Chennai', lat=13.0827, lon=80.2707)


@pytest.fixture(scope='module')
def charts():
    return (A.compute(**BOY, gender='male', now=NOW), A.compute(**GIRL, gender='female', now=NOW))


def test_two_horoscopes_give_the_rows_of_their_moon_stars(charts):
    boy, girl = charts
    out = M.match(boy, girl)
    assert out['schema'] == 'horoscopegen-match/1' and out['mode'] == 'full'
    people = out['persons']
    # The sample chart of tests/test_engine.py: Moon in Mrigashira pada 2, Rishabha.
    assert (people['boy']['nakshatra'], people['boy']['pada'], people['boy']['rasi']) == ('Mrigashira', 2, 'Rishabha')
    moon = next(p for p in girl['vedic']['planets'] if p['name'] == 'Moon')
    assert (people['girl']['nakshatra'], people['girl']['pada'], people['girl']['rasi']) == \
        (STARS[moon['nak']], moon['pada'], SIGNS[moon['sign']])
    assert people['boy']['source'] == people['girl']['source'] == 'birth details'
    assert people['boy']['dob'] == '1998-03-06' and people['girl']['pob'] == 'Chennai'
    star_only = M.match({'nakshatra': people['boy']['nakshatra'], 'pada': people['boy']['pada']},
                        {'nakshatra': people['girl']['nakshatra'], 'pada': people['girl']['pada']})
    assert star_only['mode'] == 'star'
    scored = {r['key']: (r['result'], r['points']) for r in out['rows'] if r['group'] in 'ABC'}
    again = {r['key']: (r['result'], r['points']) for r in star_only['rows']}
    again['ak_vashya'] = scored['ak_vashya']          # the girl's Moon is in Dhanu: its degree decides
    assert scored == again


def test_match_leaves_the_horoscopes_alone(charts):
    import copy
    boy, girl = charts
    before = copy.deepcopy((boy, girl))
    M.match(boy, girl)
    assert (boy, girl) == before


def test_nothing_about_length_of_life():
    banned = ('marak', 'ayur', 'longevity', 'lifespan', 'life span', 'death', 'mrityu', 'alpayu', 'alive', 'died',
              'widow', 'kill', 'fatal', 'surviv')
    allowed = ('Ayul porutham, and anything about length of life: left out on purpose',
               'Ayul porutham and the rules about particular stars and the in-laws.')

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

    seen = 0
    for b in range(0, 108, 5):
        for g in range(0, 108, 7):
            for text in texts(M.match(person(b), person(g))):
                seen += 1
                if text not in allowed:
                    low = text.lower()
                    assert not any(word in low for word in banned), text
                    assert 'length of life' not in low and 'remedy' not in low.replace('no remedy', ''), text
    assert seen > 1000
    assert allowed[0] in M.NOT_INCLUDED


# ── the route ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(monkeypatch):
    import app as app_module

    def no_network(*args, **kwargs):
        raise AssertionError('a test tried to look a place up')

    monkeypatch.setattr(app_module, 'geocode', no_network)
    monkeypatch.setattr(A, 'geocode', no_network)
    return app_module.app.test_client()


def test_route_with_birth_details(client, charts):
    rv = client.post('/api/match', json={'boy': BOY, 'girl': GIRL, 'lang': 'ta'})
    assert rv.status_code == 200 and rv.headers['Cache-Control'] == 'no-store'
    out = rv.get_json()
    want = M.match(*charts)
    assert out['mode'] == 'full' and out['schema'] == 'horoscopegen-match/1'
    assert [(r['key'], r['result'], r['points']) for r in out['rows'] if r['group'] in 'ABC'] == \
        [(r['key'], r['result'], r['points']) for r in want['rows'] if r['group'] in 'ABC']
    assert set(out['charts']) == {'boy', 'girl'} and set(out['charts']['boy']) == {'d1', 'd9'}
    assert len(out['charts']['girl']['d1']['signs']) == 12


def test_route_with_stars_only(client):
    rv = client.post('/api/match', json={'mode': 'star', 'boy': {'nakshatra': 'Rohini', 'pada': 2},
                                         'girl': {'nakshatra': 14, 'pada': 1, 'name': 'Meena'}})
    out = rv.get_json()
    assert rv.status_code == 200 and out['mode'] == 'star' and 'charts' not in out
    assert out['persons']['girl']['name'] == 'Meena' and out['persons']['boy']['name'] == 'Boy'
    assert out['summary']['ashtakoota']['points'] == 20
    assert out['persons']['boy']['source'] == 'star only' and 'dob' not in out['persons']['boy']


def test_the_name_may_be_left_out(client):
    nameless = {k: v for k, v in GIRL.items() if k != 'name'}
    out = client.post('/api/match', json={'boy': BOY, 'girl': nameless}).get_json()
    assert out['persons']['girl']['name'] == 'Girl' and out['persons']['boy']['name'] == 'Sample Native'


@pytest.mark.parametrize('body,message', [
    ({}, 'The details of the boy are required.'),
    ({'boy': BOY}, 'The details of the girl are required.'),
    ({'boy': BOY, 'girl': 'Rohini'}, 'The details of the girl are required.'),
    ({'boy': BOY, 'girl': {}}, 'The details of the girl are required.'),
    ({'boy': BOY, 'girl': GIRL, 'mode': 'quick'}, '"mode" must be "full" or "star".'),
    ({'boy': BOY, 'girl': {'name': 'x', 'dob': '2000-07-15'}},
     'Date, time and place of birth are required for the girl.'),
    ({'boy': dict(BOY, dob='15-07-2000'), 'girl': GIRL}, 'Date must be YYYY-MM-DD and time HH:MM (24-hour).'),
    ({'boy': dict(BOY, lat='north'), 'girl': GIRL}, '"north" is not a number.'),
    ({'boy': BOY, 'girl': GIRL, 'ayanamsha': 'tropical'}, 'Unknown ayanamsha "tropical".'),
    ({'mode': 'star', 'boy': {'nakshatra': 'Rohini'}, 'girl': {'nakshatra': 3}},
     "Krittika lies in Mesha and Rishabha: give the girl's pada or rasi."),
    ({'mode': 'star', 'boy': {'nakshatra': 40}, 'girl': {'nakshatra': 3}},
     "The boy's nakshatra must be a whole number from 1 to 27."),
    ({'mode': 'star', 'boy': BOY, 'girl': GIRL}, "The boy's nakshatra is required."),
    ([1, 2], 'The request body must be a JSON object.'),
])
def test_bad_input_is_a_400_with_a_message(client, body, message):
    rv = client.post('/api/match', json=body)
    assert rv.status_code == 400 and rv.get_json() == {'error': message}


def test_the_settings_of_the_request_apply_to_both_people(client):
    out = client.post('/api/match', json={'boy': BOY, 'girl': GIRL, 'ayanamsha': 'raman'}).get_json()
    assert out['persons']['boy']['ayanamsha'] == out['persons']['girl']['ayanamsha'] == 'B.V. Raman'


def test_a_person_without_coordinates_is_one_place_lookup(monkeypatch):
    import app as app_module
    asked = []

    def fake(query, limit=5):
        asked.append(query)
        return [{'name': query, 'lat': 13.0827, 'lon': 80.2707, 'tz': 'Asia/Kolkata'}]

    monkeypatch.setattr(app_module, 'geocode', fake)
    monkeypatch.setattr(A, 'geocode', fake)
    girl = {k: v for k, v in GIRL.items() if k not in ('lat', 'lon')}
    rv = app_module.app.test_client().post('/api/match', json={'boy': BOY, 'girl': girl})
    assert rv.status_code == 200 and asked == ['Chennai']


def test_matching_is_limited_to_15_a_minute_for_one_visitor(client):
    import app as app_module
    app_module.limiter.enabled = True
    app_module.limiter.reset()
    try:
        body = {'mode': 'star', 'boy': {'nakshatra': 1}, 'girl': {'nakshatra': 2}}
        headers = {'CF-Connecting-IP': '203.0.113.9'}
        got = [client.post('/api/match', json=body, headers=headers).status_code for _ in range(17)]
        assert got == [200] * 15 + [429, 429]
        assert client.post('/api/match', json=body, headers={'CF-Connecting-IP': '203.0.113.10'}).status_code == 200
        # Matching has its own count: the horoscope route is still open to the first visitor.
        assert client.post('/api/horoscope', json=BOY, headers=headers).status_code == 200
    finally:
        app_module.limiter.reset()


def test_the_single_horoscope_route_still_needs_a_name(client):
    rv = client.post('/api/horoscope', json={k: v for k, v in BOY.items() if k != 'name'})
    assert rv.status_code == 400
    assert rv.get_json() == {'error': 'Name, date, time and place of birth are required.'}
