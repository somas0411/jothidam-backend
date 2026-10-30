"""
Rule book: chart rules evaluated against one horoscope, with the period that
switches each rule on.

    rows = evaluate(res)          # res: astro_engine.compute() output

Every row is one rule that applies to the chart. A rule only describes what the
chart shows; the 'status' column says whether the dasa or bhukti that carries
it is running, still to come, already over, or outside the useful years of
life ("dormant"). The rule texts live in data/rulebook/*.json (paraphrased
rules, no source or author fields) and in the RULES table below.

Kept out on purpose: anything about death, length of life or the manner of
passing (the site does not show such results), and the rules marked for
astrologer reference only (intimacy, conduct, health diagnoses, second
marriage counts). The rule book is a separate step: compute() and the existing
report sheets are unchanged.
"""

import json
import os
import re
from datetime import datetime

import astro_engine as A
import enrich as E
from astro_engine import PLANETS, RASIS, SIGN_LORDS

SEVEN = PLANETS[:7]
NODES = ('Rahu', 'Ketu')
KENDRA, TRIKONA, DUSTHANA = (1, 4, 7, 10), (1, 5, 9), (6, 8, 12)
GOOD_RELATION = (1, 4, 5, 7, 9, 10)          # kendra / trikona from each other
SIX_EIGHT = (6, 8)
DUAL_LAGNAS = (2, 5, 8, 11)                  # Mithuna, Kanya, Dhanus, Meena
LIFE_WINDOW = (0, 75)                        # a period starting after 75 is treated as too late to use
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'rulebook')

# Words the output must never carry (site policy and attribution policy).
BANNED = re.compile(r'channel|youtube|death|passing|longevity|lifespan|life span|long life|'
                    r'ayush|ayul|maraka|\bdie\b|last birth', re.I)

TOPICS = ('career', 'wealth', 'property', 'marriage', 'family', 'children', 'education', 'foreign',
          'spiritual', 'personality', 'general')

COLUMNS = [
    ('rule_id', 'Identifier of the rule in data/rulebook'),
    ('ruleset', 'Group the rule belongs to'),
    ('topic', 'Life area: ' + ', '.join(TOPICS)),
    ('rule', 'Short name of the rule'),
    ('tone', 'favourable, mixed or challenging: how the rule reads for this chart'),
    ('finding', 'What the rule says for this chart'),
    ('basis', 'The chart facts that make the rule apply'),
    ('period_lords', 'Planets whose dasa or bhukti switches the rule on; empty when the rule is not tied to a period'),
    ('status', 'running now / upcoming / past / dormant (its periods fall outside the useful years) / always'),
    ('window', 'The running or next period that carries the rule, with dates and age; or the last one if all are past'),
]


# ── loading the rule texts ───────────────────────────────────────────────────

_DATA = None


def data():
    """All rule files, keyed by file name without .json."""
    global _DATA
    if _DATA is None:
        _DATA = {}
        for name in sorted(os.listdir(DATA_DIR)):
            if name.endswith('.json'):
                with open(os.path.join(DATA_DIR, name), encoding='utf-8') as fh:
                    _DATA[name[:-5]] = json.load(fh)
    return _DATA


def _find(obj, rule_id):
    if isinstance(obj, dict):
        if obj.get('id') == rule_id:
            return obj
        for v in obj.values():
            hit = _find(v, rule_id)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = _find(v, rule_id)
            if hit is not None:
                return hit
    return None


def rule_text(fileset, rule_id):
    """The 'results' list of a placement rule in a data file, cleaned."""
    r = _find(data().get(fileset, {}), rule_id) or {}
    lines = r.get('results') or []
    return [s for s in lines if isinstance(s, str) and s and not BANNED.search(s)]


# ── chart context ────────────────────────────────────────────────────────────

class Chart:
    """Facts the rules ask for, built on enrich.Ctx."""

    def __init__(self, res, now=None):
        self.c = c = E.Ctx(res, now)
        E._yogas(c)                       # fills c.neecha_bhanga
        self.res, self.now, self.birth = res, c.now, c.birth
        self.lagna = c.lagna_sign
        self.pt = c.points
        self.sign, self.house = c.sign, c.house
        self.lord = c.house_lord           # house -> lord
        self.owned = c.owned               # planet -> houses
        self.dasas = res['vedic']['dasa']['dasas']

    # dignity
    def dig(self, p):
        if p not in SEVEN:
            return ''
        label, debil = self.c.dignity['D1'][p]
        if debil:
            return 'debilitated'
        if label == 'Exalted':
            return 'exalted'
        if label in ('Own sign', 'Moolatrikona'):
            return 'own'
        return ''

    def own_or_exalted(self, p):
        return self.dig(p) in ('own', 'exalted')

    def nb(self, p):
        return bool(self.c.neecha_bhanga.get(p))

    def retro(self, p):
        return bool(self.pt[p].get('retro'))

    def combust(self, p):
        return self.c.combust(p)

    def star_lord(self, p):
        return self.pt[p]['star_lord']

    def dispositor(self, p):
        return SIGN_LORDS[self.sign[p]]

    def strong(self, p):
        """Own sign, exalted, or debilitated with the debilitation cancelled; nodes by their dispositor."""
        if p in NODES:
            return self.strong(self.dispositor(p))
        d = self.dig(p)
        return d in ('own', 'exalted') or (d == 'debilitated' and self.nb(p))

    def weak(self, p):
        if p in NODES:
            return self.house[p] in DUSTHANA and not self.strong(self.dispositor(p))
        d = self.dig(p)
        return ((d == 'debilitated' and not self.nb(p)) or self.combust(p)
                or (self.house[p] in DUSTHANA and not self.own_or_exalted(p)))

    # relations
    def together(self, a, b):
        return a != b and self.sign[a] == self.sign[b]

    def aspects(self, a, b):
        """a casts a sign aspect on b."""
        return self.sign[b] in self.c.asp_signs.get(a, set())

    def jupiter_on(self, p):
        return p != 'Jupiter' and (self.together('Jupiter', p) or self.aspects('Jupiter', p))

    def node_on(self, p):
        """Rahu or Ketu with p, aspecting p, or p in a node's star."""
        if p in NODES:
            return False
        return any(self.together(n, p) or self.star_lord(p) == n for n in NODES)

    def linked(self, a, b):
        if a == b:
            return True
        return (self.together(a, b) or self.aspects(a, b) or self.aspects(b, a)
                or self.star_lord(a) == b or self.star_lord(b) == a
                or (a in SEVEN and b in SEVEN and self.c.exchange(a, b)))

    def rel(self, a, b):
        """Place of b counted from a (1-12)."""
        return E.house_from(self.sign[b], self.sign[a])

    def mutual(self, a, b):
        """Houses of a and b from each other as an unordered pair, e.g. (6, 8)."""
        x = self.rel(a, b)
        return tuple(sorted((x, (14 - x) % 12 or 12)))

    def with_planets(self, p):
        return [q for q in PLANETS if q != p and self.together(q, p)]

    def in_house(self, h):
        return [p for p in PLANETS if self.house[p] == h]

    def name(self, p):
        return f"{p} ({RASIS[self.sign[p]]}, house {self.house[p]})"

    # periods
    def age(self, dt):
        return round((dt - self.birth).days / A.YEAR_DAYS, 1)

    def periods(self, lords):
        """Every dasa of these lords, and every bhukti of these lords inside other dasas."""
        out = []
        for d in self.dasas:
            if d['lord'] in lords:
                out.append(('dasa', d['lord'], None, d['start'], d['end']))
            for b in d.get('sub', []):
                if b['lord'] in lords and d['lord'] not in lords:
                    out.append(('bhukti', d['lord'], b['lord'], b['start'], b['end']))
        return sorted(out, key=lambda r: r[3])


def _fmt(dt):
    return dt.strftime('%Y-%m-%d')


def timing(ch, lords, dasa_only=False, ages=None):
    """(status, window) for the periods of these lords."""
    if not lords:
        return 'always', ''
    lo, hi = ages or LIFE_WINDOW
    rows = [r for r in ch.periods(lords) if not (dasa_only and r[0] != 'dasa')]
    if not rows:
        return 'dormant', 'no period of ' + ', '.join(lords) + ' in this lifetime'

    def label(r):
        kind, d, b, s, e = r
        what = f'{d} dasa' if kind == 'dasa' else f'{b} bhukti in {d} dasa'
        return f'{what}, {_fmt(s)} to {_fmt(e)} (age {ch.age(s):g} to {ch.age(e):g})'

    usable = [r for r in rows if ch.age(r[3]) < hi and ch.age(r[4]) > lo]
    now = ch.now
    running = [r for r in usable if r[3] <= now < r[4]]
    if running:
        # a dasa outranks a bhukti when both run
        running.sort(key=lambda r: r[0] != 'dasa')
        return 'running now', label(running[0])
    later = [r for r in usable if r[3] > now]
    if later:
        return 'upcoming', label(later[0])
    if usable:
        return 'past', label(usable[-1])
    return 'dormant', 'its periods fall outside the useful years (' + label(rows[0]) + ')'


# ── the rules ────────────────────────────────────────────────────────────────

RULES = []


def rule(rule_id, ruleset, topic, title, dasa_only=False, ages=None):
    def deco(fn):
        RULES.append((rule_id, ruleset, topic, title, dasa_only, ages, fn))
        return fn
    return deco


def hit(finding, basis, lords=(), tone='favourable'):
    return {'finding': finding, 'basis': basis, 'lords': list(dict.fromkeys(lords)), 'tone': tone}


# -- Rahu / Ketu ---------------------------------------------------------------

def _node_authorities(ch, n):
    sl, st = ch.dispositor(n), ch.star_lord(n)
    if sl == st:
        return sl, st, 'same planet', True
    pair = ch.mutual(sl, st)
    good = (pair[0] in GOOD_RELATION and pair[1] in GOOD_RELATION) or ch.together(sl, st) \
        or (sl in SEVEN and st in SEVEN and ch.c.mutual_aspect(sl, st)) or pair == (3, 11)
    return sl, st, f'{pair[0]}/{pair[1]} from each other', good


@rule('RAHU-DA-01', 'rahu_love_marriage', 'general', 'Rahu dasa decided by its sign lord and star lord', dasa_only=True)
def r_rahu_da(ch):
    sl, st, how, good = _node_authorities(ch, 'Rahu')
    basis = f'Rahu in house {ch.house["Rahu"]}; sign lord {ch.name(sl)}; star lord {ch.name(st)}; {how}'
    if good:
        hidden = [p for p in {sl, st} if ch.house[p] in DUSTHANA]
        if hidden:
            return hit('Rahu dasa is good overall, with one area of strain tied to the house of '
                       + ', '.join(hidden) + '.', basis, ['Rahu'], 'mixed')
        return hit('Rahu dasa gives the results of its sign lord and star lord, which support each other: '
                   'a productive Rahu dasa whatever house Rahu occupies.', basis, ['Rahu'])
    return hit('Rahu\'s sign lord and star lord are at odds (6/8 or 2/12): Rahu dasa needs care - '
               'gains come with setbacks.', basis, ['Rahu'], 'challenging')


@rule('KETU-DA-01', 'raja_yoga_activation', 'general', 'Ketu dasa decided by its sign lord and star lord', dasa_only=True)
def r_ketu_da(ch):
    sl, st, how, good = _node_authorities(ch, 'Ketu')
    basis = f'Ketu in house {ch.house["Ketu"]}; sign lord {ch.name(sl)}; star lord {ch.name(st)}; {how}'
    if good and (ch.strong(sl) or ch.strong(st)):
        return hit('Ketu dasa can bring sudden, lasting gains: its deciding planets are strong and support each other.',
                   basis, ['Ketu'])
    if good:
        return hit('Ketu dasa works well: its sign lord and star lord support each other.', basis, ['Ketu'])
    return hit('Ketu\'s deciding planets are 6/8 or 2/12 from each other: Ketu dasa is harder than the house alone suggests.',
               basis, ['Ketu'], 'challenging')


@rule('RY-02', 'raja_yoga_activation', 'general', 'Rahu or Ketu with a strong or retrograde planet')
def r_node_boost(ch):
    out = []
    for n in NODES:
        for p in ch.with_planets(n):
            if p in NODES:
                continue
            if ch.own_or_exalted(p) or ch.retro(p):
                same_pada = ch.pt[p]['nak'] == ch.pt[n]['nak'] and ch.pt[p]['pada'] == ch.pt[n]['pada']
                why = 'own sign' if ch.dig(p) == 'own' else ('exalted' if ch.dig(p) == 'exalted' else 'retrograde')
                if same_pada:
                    out.append(hit(f'{n} and {p} share the same nakshatra pada: instead of a boost this pairing tends to fail '
                                   f'in their periods.', f'{n} with {p} ({why}) in {RASIS[ch.sign[p]]}, same pada',
                                   [n, p], 'challenging'))
                else:
                    out.append(hit(f'{n} amplifies {p} ({why}): a yoga, not a dosha; the periods of both are strengthened.',
                                   f'{n} with {p} in {RASIS[ch.sign[p]]}', [n, p]))
            elif ch.dig(p) == 'debilitated' and not ch.nb(p):
                out.append(hit(f'{n} with a debilitated {p}: the weakness is magnified in their periods; avoid big risks then.',
                               f'{n} with {p} debilitated in {RASIS[ch.sign[p]]}, no cancellation', [n, p], 'challenging'))
    return out


@rule('KETU-GEN-02', 'ketu_12th', 'general', 'Ketu holds back the next sign it moves into')
def r_ketu_next(ch):
    h = (ch.house['Ketu'] - 2) % 12 + 1
    areas = {1: 'self and health', 2: 'family and savings', 3: 'courage and siblings', 4: 'home and property',
             5: 'children and studies', 6: 'job and debts', 7: 'marriage and partnerships', 8: 'sudden events',
             9: 'fortune and father', 10: 'career', 11: 'gains', 12: 'expenses and travel'}
    return hit(f'Matters of house {h} ({areas[h]}) tend to come late at first and are delivered later.',
               f'Ketu in house {ch.house["Ketu"]}; the 12th sign from Ketu is house {h}', [], 'mixed')


@rule('K12', 'ketu_12th', 'personality', 'Planets in the 12th sign from Ketu')
def r_k12(ch):
    twelfth = (ch.sign['Ketu'] - 1) % 12
    out = []
    for p in SEVEN:
        how = []
        if ch.sign[p] == twelfth:
            how.append(f'{p} occupies the 12th sign from Ketu')
        if SIGN_LORDS[twelfth] == p:
            how.append(f'the 12th sign from Ketu ({RASIS[twelfth]}) is owned by {p}')
        if not how:
            continue
        lines = rule_text('ketu_12th', f'K12-{p.upper()}')
        if lines:
            out.append(hit('; '.join(lines[:3]) + '.', '; '.join(how), [], 'mixed' if not ch.strong(p) else 'favourable'))
    return out


# -- retrograde planets --------------------------------------------------------

@rule('VAK-01', 'retrograde_planet', 'general', 'Retrograde planet: results reverse')
def r_retro(ch):
    out = []
    for p in ('Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'):
        if not ch.retro(p):
            continue
        nat = ch.c.nature.get(p, 'Neutral')
        basis = f'{ch.name(p)} retrograde; functional {nat.lower()} for this lagna'
        if ch.jupiter_on(p):
            out.append(hit(f'{p} is retrograde but Jupiter aspects or joins it: the reversal is neutralised; '
                           f'judge {p} normally.', basis, [p]))
        elif ch.node_on(p):
            out.append(hit(f'Retrograde {p} is linked to Rahu/Ketu: its period turns into a yoga.', basis, [p]))
        elif ch.dig(p) == 'debilitated':
            out.append(hit(f'{p} is debilitated and retrograde: it gives the results of an exalted planet in its period.',
                           basis, [p]))
        elif ch.own_or_exalted(p):
            out.append(hit(f'{p} is {ch.dig(p) if ch.dig(p) != "own" else "in own sign"} but retrograde: it loses its '
                           f'positional strength; its period gives less than its dignity promises.', basis, [p], 'challenging'))
        elif nat in ('Benefic', 'Yogakaraka'):
            out.append(hit(f'{p} is a benefic for this lagna but retrograde: expect delays or reversals in the matters '
                           f'of houses {", ".join(map(str, ch.owned[p]))} during its period.', basis, [p], 'challenging'))
        else:
            out.append(hit(f'{p} is not a benefic for this lagna and is retrograde: its harm is reduced and it can '
                           f'even help in its period.', basis, [p]))
    return out


@rule('VAK-04', 'retrograde_planet', 'general', 'Back-to-back retrograde dasas')
def r_retro_run(ch):
    seq = [d for d in ch.dasas if ch.age(d['start']) < 75]
    best, cur = [], []
    for d in seq:
        if d['lord'] in SEVEN and ch.retro(d['lord']):
            cur.append(d)
            if len(cur) > len(best):
                best = list(cur)
        else:
            cur = []
    if len(best) >= 2:
        names = ', '.join(d['lord'] for d in best)
        return hit(f'Dasas of retrograde planets follow one another ({names}): a long stretch where results come in '
                   f'reverse order - patience pays, gains come late.',
                   f'{names}: all retrograde, consecutive dasas', [d['lord'] for d in best], 'mixed')


@rule('VAK-06', 'retrograde_planet', 'marriage', 'Retrograde 5th lord')
def r_retro5(ch):
    l5 = ch.lord[5]
    if ch.retro(l5):
        return hit('The 5th lord is retrograde: a self-chosen (love) marriage is more likely than an arranged one.',
                   f'5th lord {ch.name(l5)} retrograde', [l5], 'mixed')


@rule('ED-01', 'education_choice', 'education', 'Retrograde bhukti lord slows studies', ages=(5, 25))
def r_study_delay(ch):
    out = []
    for d in ch.dasas:
        for b in d.get('sub', []):
            p = b['lord']
            if p in SEVEN and ch.retro(p) and ch.age(b['start']) < 25 and ch.age(b['end']) > 5:
                out.append(hit(f'Studies may slow down in {p} bhukti ({_fmt(b["start"])} to {_fmt(b["end"])}); '
                               f'they pick up again when it ends.', f'{p} retrograde', [], 'mixed'))
    return out[:3]


@rule('CX-06', 'complex_chart_techniques', 'education', 'Retrograde Mercury with Ketu')
def r_merc_research(ch):
    if ch.retro('Mercury') and (ch.together('Mercury', 'Ketu') or ch.star_lord('Mercury') in NODES):
        return hit('Retrograde Mercury linked to a node: research ability - a PhD or a lasting invention is possible.',
                   f'{ch.name("Mercury")} retrograde, with Ketu or in a node\'s star', ['Mercury'])


@rule('OS-15', 'own_sign_failure', 'personality', 'Lone retrograde Mercury')
def r_merc_alone(ch):
    if ch.retro('Mercury') and not ch.with_planets('Mercury'):
        return hit('Mercury alone and retrograde: bold to the point of acting against all advice - '
                   'decisions should be checked with someone trusted.', ch.name('Mercury'), [], 'mixed')


# -- own sign / exalted planets ------------------------------------------------

def _trigger_set(ch, p):
    return [p] + [q for q in PLANETS if q != p and (ch.star_lord(q) == p or ch.together(q, p))]


@rule('OE-01', 'own_exalted_dasa', 'career', 'Own-sign or exalted planet in the 6th or 10th: career change')
def r_oe01(ch):
    out = []
    for p in SEVEN:
        if ch.house[p] in (6, 10) and ch.own_or_exalted(p):
            exc = []
            if ch.retro(p):
                exc.append(f'{p} is retrograde')
            if ch.dig(ch.dispositor(p)) == 'debilitated':
                exc.append('its dispositor is debilitated')
            basis = f'{ch.name(p)} {ch.dig(p)}'
            if exc:
                out.append(hit(f'A career shift is indicated but may not happen ({"; ".join(exc)}).', basis,
                               _trigger_set(ch, p), 'mixed'))
            else:
                out.append(hit('When these periods begin, a job or business change is close to certain - and it moves '
                               'the native up (better role, income, or an own venture). Some turbulence until the '
                               'planet\'s own bhukti ends.', basis, _trigger_set(ch, p)))
    return out


@rule('OE-02', 'own_exalted_dasa', 'personality', 'Own-sign or exalted planet in the lagna', dasa_only=True)
def r_oe02(ch):
    out = []
    for p in SEVEN:
        if ch.house[p] == 1 and ch.own_or_exalted(p):
            extra = ' (strongest with Jupiter)' if p == 'Jupiter' else ''
            out.append(hit(f'Strong self-respect and sense of status{extra}; may leave a job over lack of recognition. '
                           'Flexibility at work serves better than pride in this period.', ch.name(p), [p], 'mixed'))
    return out


@rule('OS-01', 'own_sign_failure', 'career', 'Dasa lord and bhukti lord both own sign or exalted')
def r_os01(ch):
    out = []
    for d in ch.dasas:
        if not (d['lord'] in SEVEN and ch.own_or_exalted(d['lord'])):
            continue
        for b in d.get('sub', []):
            p = b['lord']
            if p != d['lord'] and p in SEVEN and ch.own_or_exalted(p) and b['end'] > ch.now \
                    and ch.age(b['start']) < 65:
                out.append(hit(f'{d["lord"]} dasa, {p} bhukti ({_fmt(b["start"])} to {_fmt(b["end"])}): pressure or a push '
                               'out of the current job; business owners should avoid over-investing (stock, machinery). '
                               'Most people end up better placed after it.',
                               f'{d["lord"]} {ch.dig(d["lord"])}, {p} {ch.dig(p)}', [], 'mixed'))
    return out[:3]


@rule('JT-01', 'job_timing', 'career', 'Dasa lord tied to own-sign/exalted planets', dasa_only=True, ages=(18, 45))
def r_jt01(ch):
    out = []
    for d in ch.dasas:
        p = d['lord']
        if ch.age(d['end']) < 18 or ch.age(d['start']) > 45:
            continue
        ties = [q for q in SEVEN if q != p and ch.own_or_exalted(q)
                and (ch.together(p, q) or ch.star_lord(p) == q)]
        if ties and not ch.own_or_exalted(p):
            out.append(hit(f'In {p} dasa the job is hard to settle or below expectation (may need to relocate or take a '
                           'smaller role; an own business is not advised then). The second half eases.',
                           f'{p} linked to {", ".join(ties)} (own sign/exalted)', [p], 'mixed'))
    return out


@rule('OS-04', 'own_sign_failure', 'career', 'Job or business: 6th lord against 10th lord')
def r_os04(ch):
    def score(p):
        s = 0
        s += 2 if ch.own_or_exalted(p) else 0
        s += 1 if ch.house[p] in KENDRA + TRIKONA else 0
        s -= 2 if ch.weak(p) and not ch.own_or_exalted(p) else 0
        s += 1 if ch.jupiter_on(p) else 0
        return s
    l6, l10 = ch.lord[6], ch.lord[10]
    s6, s10 = score(l6), score(l10)
    basis = f'6th lord {ch.name(l6)} score {s6}; 10th lord {ch.name(l10)} score {s10}'
    if l6 == l10:
        return None
    if s6 > s10 + 1:
        return hit('Employment suits better than running a business.', basis, [], 'mixed')
    if s6 > s10:
        return hit('A job plus a side business suits this chart.', basis)
    if s10 > s6 + 1:
        return hit('Business suits this chart: when a period hurts the 6th house, the native tends to leave the job '
                   'for an own venture.', basis)
    return hit('Job and business are balanced; the running dasa decides which way it goes.', basis, [], 'mixed')


@rule('OS-03', 'own_sign_failure', 'career', 'Business courage test')
def r_os03(ch):
    fails = []
    if ch.house[ch.lord[3]] == 12:
        fails.append(f'3rd lord {ch.lord[3]} in the 12th (courage for big jobs, not for own finances)')
    if ch.house[ch.lord[5]] == 12:
        fails.append(f'5th lord {ch.lord[5]} in the 12th')
    l2 = ch.lord[2]
    if ch.dig(l2) == 'debilitated':
        fails.append(f'2nd lord {l2} debilitated (earns by working rather than owning)')
    if ch.together('Sun', 'Saturn') and ch.house['Sun'] == 12:
        fails.append('Sun and Saturn together in the 12th (their trade yoga does not work there)')
    if len(fails) >= 2:
        return hit('Own business is not advised; the native does best in employment.', '; '.join(fails), [], 'mixed')


@rule('CX-05', 'complex_chart_techniques', 'career', 'Retrograde 10th lord', dasa_only=True)
def r_retro10(ch):
    l10 = ch.lord[10]
    if ch.retro(l10):
        quick = ' and fast' if ch.node_on(l10) or ch.strong(ch.dispositor(l10)) else ''
        return hit(f'In employment the native rises to top positions{quick}; an own business struggles.',
                   f'10th lord {ch.name(l10)} retrograde', [l10])


@rule('RY-04', 'raja_yoga_activation', 'career', 'Exalted 10th lord', dasa_only=True)
def r_ex10(ch):
    l10 = ch.lord[10]
    if ch.dig(l10) == 'exalted':
        if ch.retro(l10):
            return hit('Big career yoga through employment, possibly top management.', ch.name(l10), [l10])
        return hit('Big career yoga; own business suits.', ch.name(l10), [l10])


@rule('DU-03', 'dusthana_planets', 'career', '6th lord in the 6th', dasa_only=True)
def r_du03(ch):
    l6 = ch.lord[6]
    if ch.house[l6] == 6 and ch.own_or_exalted(l6):
        if ch.retro(l6):
            return hit('Employment in a top-priority role (not business).', ch.name(l6), [l6])
        return hit('Strong in competition; an own business can do very well (pioneer, few rivals).', ch.name(l6), [l6])


@rule('DU-02', 'dusthana_planets', 'foreign', 'Planet in the 6th and work abroad', dasa_only=True)
def r_du02(ch):
    six = [p for p in ch.in_house(6)]
    if not six:
        return None
    l6 = ch.lord[6]
    basis = f'planets in the 6th: {", ".join(six)}; 6th lord {ch.name(l6)}'
    if ch.own_or_exalted(l6):
        return hit('Work abroad brings hardship in these periods; staying in the home country is better.', basis, six, 'mixed')
    if ch.house[l6] in DUSTHANA:
        return hit('Goes abroad for work in these periods and lives comfortably there.', basis, six)
    if ch.retro(l6):
        return hit('Goes abroad for work in these periods.', basis, six)


@rule('SAT-13', 'saturn_raja_yoga', 'career', 'Several planets in the 10th')
def r_stellium10(ch):
    ten = ch.in_house(10)
    if len(ten) >= 4:
        return hit('Four or more planets in the 10th: a detached, renunciate streak may show; career needs a closer look.',
                   ', '.join(ten), ten, 'mixed')
    if len(ten) == 3 and ch.lord[10] in ten and ch.own_or_exalted(ch.lord[10]):
        return hit('Three planets in the 10th with its own-sign lord: wealth through career.', ', '.join(ten), ten)


@rule('ED-14', 'education_choice', 'career', 'Jupiter, Mars and Venus alone in kendras')
def r_govt(ch):
    if all(ch.house[p] in KENDRA and not [q for q in ch.with_planets(p) if q in SEVEN] for p in ('Jupiter', 'Mars', 'Venus')):
        return hit('A high-status government position is indicated.', ', '.join(ch.name(p) for p in ('Jupiter', 'Mars', 'Venus')))


# -- wealth --------------------------------------------------------------------

@rule('RY-01', 'raja_yoga_activation', 'wealth', '2nd and 11th lords exchange signs', dasa_only=True)
def r_ry01(ch):
    l2, l11 = ch.lord[2], ch.lord[11]
    if l2 != l11 and ch.c.exchange(l2, l11):
        return hit('Major wealth yoga - delivered in the dasas of these two planets.', f'{l2} and {l11} exchange signs', [l2, l11])


@rule('JT-05', 'job_timing', 'wealth', '2nd and 11th lords both in own sign', dasa_only=True)
def r_jt05(ch):
    l2, l11 = ch.lord[2], ch.lord[11]
    if ch.dig(l2) == 'own' and ch.dig(l11) == 'own':
        return hit('Lasting wealth.', f'{ch.name(l2)}, {ch.name(l11)}', [l2, l11])


@rule('RY-03', 'raja_yoga_activation', 'wealth', '2nd and 11th lords in mutual kendra', dasa_only=True)
def r_ry03(ch):
    l2, l11 = ch.lord[2], ch.lord[11]
    if l2 != l11 and ch.rel(l2, l11) in KENDRA:
        return hit('Wealth lords support each other: a dhana yoga chart.', f'{ch.name(l2)}, {ch.name(l11)}', [l2, l11])


@rule('2L', 'second_lord_placement', 'wealth', 'Where the 2nd lord sits', dasa_only=True)
def r_2l(ch):
    l2 = ch.lord[2]
    h = ch.house[l2]
    lines = rule_text('second_lord_placement', f'2L-H{h}')
    if lines:
        return hit('; '.join(lines[:4]) + '.', f'2nd lord {ch.name(l2)}', [l2],
                   'favourable' if h in (1, 2, 4, 9, 11) else 'mixed')


@rule('12L', 'twelfth_lord_placement', 'wealth', 'Where the 12th lord sits', dasa_only=True)
def r_12l(ch):
    l12 = ch.lord[12]
    out = []
    if ch.own_or_exalted(l12):
        lines = rule_text('twelfth_lord_placement', '12L-STRONG')
        if lines:
            out.append(hit('; '.join(lines) + '.', f'12th lord {ch.name(l12)} {ch.dig(l12)}', [l12]))
    lines = rule_text('twelfth_lord_placement', f'12L-H{ch.house[l12]}')
    if lines:
        out.append(hit('; '.join(lines[:3]) + '.', f'12th lord {ch.name(l12)}', [l12], 'mixed'))
    return out


@rule('H12-01', 'twelfth_house_significations', 'wealth', '12th lord dasa: spending that turns into wealth', dasa_only=True)
def r_h12_01(ch):
    l12 = ch.lord[12]
    basis = f'12th lord {ch.name(l12)}'
    if ch.retro(l12) and not ch.node_on(l12):
        return hit('In the 12th lord\'s dasa debts can build up and commitments get hard; keep savings, especially for '
                   'retirement, well guarded.', basis + ' retrograde, no Rahu/Ketu link', [l12], 'challenging')
    if ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA or ch.house[l12] in (3, 6, 8) or ch.jupiter_on(l12):
        return hit('Spending in this dasa turns into assets - house, land, vehicle, a business, deposits; investment '
                   'rather than salary builds the wealth.', basis + ' strong', [l12])


@rule('H12-21', 'twelfth_house_significations', 'wealth', 'Income that lasts')
def r_h12_21(ch):
    l12 = ch.lord[12]
    if ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA or ch.jupiter_on(l12):
        return hit('Money keeps coming in through later life; no need to hoard anxiously for retirement.',
                   f'12th lord {ch.name(l12)}')


@rule('H12-22', 'twelfth_house_significations', 'wealth', 'Investments beat business')
def r_h12_22(ch):
    l5 = ch.lord[5]
    lords = [d['lord'] for d in ch.dasas if d['lord'] != l5 and ch.linked(l5, d['lord'])
             and ch.age(d['start']) < 70]
    if lords:
        return hit('In these dasas income from investing (funds, shares, deposits, property) beats running a business.',
                   f'5th lord {l5} linked to the dasa lord', lords)


@rule('VEN-S', 'venus_7th_house', 'wealth', 'Venus and financial comfort')
def r_venus_s(ch):
    d = ch.dig('Venus')
    if d in ('own', 'exalted'):
        return hit('Financially well above self-sufficiency.', ch.name('Venus') + ' ' + d, ['Venus'])
    if not ch.with_planets('Venus') and ch.dig(ch.dispositor('Venus')) == 'exalted':
        return hit('Financial success, through its sign lord\'s strength.', ch.name('Venus'), ['Venus'])
    if ch.retro('Venus'):
        return hit('Success comes late, after many challenges.', ch.name('Venus') + ' retrograde', ['Venus'], 'mixed')
    if d == 'debilitated' and not ch.nb('Venus'):
        return hit('Still succeeds financially; strongly goal-driven.', ch.name('Venus') + ' debilitated', ['Venus'], 'mixed')


@rule('YP-02', 'yoga_period_timing', 'wealth', '2nd lord in the 9th with a strong dispositor', dasa_only=True)
def r_yp02(ch):
    l2 = ch.lord[2]
    disp = ch.dispositor(l2)
    if ch.house[l2] == 9 and ch.dig(disp) == 'own' and ch.rel(l2, disp) == 8:
        return hit('A strong wealth period.', f'2nd lord {ch.name(l2)}; its dispositor {ch.name(disp)} in own sign', [l2, disp])


@rule('DU-06', 'dusthana_planets', 'wealth', '12th lord dasa - prosperity or strain', dasa_only=True)
def r_du06(ch):
    l12 = ch.lord[12]
    if ch.own_or_exalted(l12) or (ch.house[l12] in DUSTHANA and ch.dig(l12) == 'own'):
        return hit('A prosperous dasa: household goods, vehicles, property.', f'12th lord {ch.name(l12)}', [l12])
    if (ch.retro(l12) or (ch.dig(l12) == 'debilitated' and not ch.nb(l12))) and not ch.node_on(l12):
        return hit('Financial strain in this dasa; avoid promises that are hard to keep.', f'12th lord {ch.name(l12)}',
                   [l12], 'challenging')


@rule('DU-12', 'dusthana_planets', 'wealth', '5th lord dasa and money', dasa_only=True)
def r_du12(ch):
    l5 = ch.lord[5]
    if ch.retro(l5):
        return hit('Good earnings in the 5th lord\'s dasa.', f'5th lord {ch.name(l5)} retrograde', [l5])
    if not ch.strong(l5):
        return hit('Borrowing is likely in the 5th lord\'s dasa; keep debt in check.', f'5th lord {ch.name(l5)}', [l5], 'mixed')


# -- property ------------------------------------------------------------------

@rule('YP-07', 'yoga_period_timing', 'property', 'Strong 4th lord', dasa_only=True)
def r_yp07(ch):
    l4 = ch.lord[4]
    if ch.house[l4] == 4 or ch.own_or_exalted(l4) or ch.house[l4] in KENDRA + TRIKONA:
        return hit('Property, a good house and vehicles.', f'4th lord {ch.name(l4)}', [l4])


@rule('YP-06', 'yoga_period_timing', 'property', 'Mars in the 4th')
def r_yp06(ch):
    if ch.house['Mars'] == 4:
        return hit('An own home tends to come late.', ch.name('Mars'), ['Mars'], 'mixed')


@rule('PROP-01', 'property_spouse_name', 'property', '4th house afflicted')
def r_prop01(ch):
    l4 = ch.lord[4]
    bad_lords = {ch.lord[6], ch.lord[8], ch.lord[12]}
    why = []
    if ch.dig(l4) == 'debilitated' and not ch.nb(l4):
        why.append('4th lord debilitated')
    if ch.retro(l4):
        why.append('4th lord retrograde')
    if ch.combust(l4):
        why.append('4th lord combust')
    if ch.house[l4] in DUSTHANA:
        why.append(f'4th lord in house {ch.house[l4]}')
    if [q for q in ch.with_planets(l4) if q in bad_lords]:
        why.append('4th lord with a 6th/8th/12th lord')
    if why:
        return hit('Own property may come late; registering property in the spouse\'s name (if the spouse\'s 4th lord '
                   'is stronger) is a common remedy.', '; '.join(why), [l4], 'mixed')


@rule('PROP-09', 'property_spouse_name', 'property', '4th and 11th lords connected', dasa_only=True)
def r_prop09(ch):
    l4, l11 = ch.lord[4], ch.lord[11]
    if l4 == l11 or ch.linked(l4, l11):
        return hit('Property brings gains; good for buying property.', f'4th lord {l4}, 11th lord {l11}', [l4, l11])


@rule('H12-04', 'twelfth_house_significations', 'property', '4th lord in the 12th', dasa_only=True)
def r_h12_04(ch):
    l4 = ch.lord[4]
    if ch.house[l4] != 12:
        return None
    l12 = ch.lord[12]
    if not ch.retro(l4) and (ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA):
        return hit('Buys land and a house; property grows in this dasa.', f'4th lord {ch.name(l4)}; 12th lord {ch.name(l12)}', [l4])
    return hit('Plans to buy property may end in selling; keep property papers and loans in order in this dasa.',
               f'4th lord {ch.name(l4)}', [l4], 'challenging')


@rule('DU-13', 'dusthana_planets', 'property', 'Mars-Rahu connection and property', dasa_only=True)
def r_du13(ch):
    if not ch.linked('Mars', 'Rahu'):
        return None
    basis = f'{ch.name("Mars")} linked to Rahu'
    if ch.retro('Mars') or ch.own_or_exalted('Mars'):
        return hit('Top-grade property yoga.', basis, ['Mars', 'Rahu'])
    if ch.jupiter_on('Mars'):
        return hit('Good property yoga.', basis, ['Mars', 'Rahu'])
    if not ch.strong(ch.dispositor('Mars')):
        return hit('Property purchases can turn into a burden; check finances first.', basis, ['Mars', 'Rahu'], 'challenging')
    return hit('Moderate property yoga.', basis, ['Mars', 'Rahu'], 'mixed')


# -- marriage and family -------------------------------------------------------

@rule('MS-01', 'marriage_chart_selection', 'marriage', 'Strong 7th lord for a dual lagna - timing check', dasa_only=True)
def r_ms01(ch):
    l7 = ch.lord[7]
    if ch.lagna in DUAL_LAGNAS and ch.own_or_exalted(l7):
        return hit('The 7th lord is strong for a dual lagna, which is often labelled a marriage dosha; it acts only in '
                   'the 7th lord\'s dasa. If that dasa is over or comes late, ignore it when matching.',
                   f'7th lord {ch.name(l7)} {ch.dig(l7)}', [l7], 'mixed')


@rule('CX-08', 'complex_chart_techniques', 'marriage', '6th lord in the 7th', dasa_only=True)
def r_cx08(ch):
    l6 = ch.lord[6]
    if ch.house[l6] != 7:
        return None
    if (ch.lagna == 7 and l6 == 'Mars') or (ch.lagna == 1 and l6 == 'Venus'):
        return None
    basis = f'6th lord {ch.name(l6)}'
    if ch.retro(l6) or ch.jupiter_on(l6):
        return hit('The usual strain on married life from this placement is neutralised.', basis, [l6])
    return hit('Distance between spouses (living apart, separate finances) is possible in this dasa; give the '
               'relationship extra care then. Not a reason on its own to reject a match.', basis, [l6], 'challenging')


@rule('MS-03', 'marriage_chart_selection', 'family', '2nd lord hidden', dasa_only=True)
def r_ms03(ch):
    l2 = ch.lord[2]
    if ch.house[l2] in (3, 6, 8, 12) and not ch.own_or_exalted(l2):
        return hit('Family life needs care in the 2nd lord\'s dasa; harmless if that dasa is over or comes late.',
                   f'2nd lord {ch.name(l2)}', [l2], 'mixed')


@rule('MH-05', 'marital_harmony', 'marriage', 'Venus own sign in the 7th')
def r_mh05(ch):
    if ch.house['Venus'] == 7 and ch.dig('Venus') == 'own':
        return hit('The usual worry about Venus in the 7th does not apply: Venus in own sign gives a supportive spouse.',
                   ch.name('Venus'), ['Venus'])


@rule('SAT-11', 'saturn_raja_yoga', 'marriage', 'Exalted 7th lord Saturn in the 4th')
def r_sat11(ch):
    if ch.lord[7] == 'Saturn' and ch.house['Saturn'] == 4 and ch.dig('Saturn') == 'exalted':
        return hit('Marriage is assured, even in Saturn dasa.', ch.name('Saturn'), ['Saturn'])


@rule('RAHU-8-MARRIAGE', 'rahu_love_marriage', 'marriage', 'Rahu in the 8th', dasa_only=True)
def r_rahu8(ch):
    if ch.house['Rahu'] == 8 and _node_authorities(ch, 'Rahu')[3]:
        return hit('Rahu in the 8th is not a marriage dosha here: its deciding planets are well placed; marriage can '
                   'happen even in Rahu dasa.', f'Rahu in house 8; {_node_authorities(ch, "Rahu")[2]}', ['Rahu'])


@rule('CX-04', 'complex_chart_techniques', 'family', 'Retrograde 2nd lord in own or exalted sign', dasa_only=True)
def r_cx04(ch):
    l2 = ch.lord[2]
    if ch.retro(l2) and ch.own_or_exalted(l2):
        if ch.node_on(l2):
            return hit('Family life is fine: the node link rescues the retrograde 2nd lord.', f'2nd lord {ch.name(l2)}', [l2])
        return hit('The 2nd lord gives a family, then turbulence within it in its dasa; patience and space help.',
                   f'2nd lord {ch.name(l2)} retrograde', [l2], 'challenging')


@rule('H12-13', 'twelfth_house_significations', 'family', '2nd lord in the 12th', dasa_only=True)
def r_h12_13(ch):
    l2, l12 = ch.lord[2], ch.lord[12]
    if ch.house[l2] == 12 and (ch.retro(l2) or ch.weak(l2)) and not ch.own_or_exalted(l12):
        return hit('Family members may live apart for a while in this dasa (often for work); it lasts only for the period.',
                   f'2nd lord {ch.name(l2)}; 12th lord {ch.name(l12)}', [l2], 'mixed')


@rule('DU-14', 'dusthana_planets', 'marriage', 'Sun with Mars')
def r_du14(ch):
    if ch.together('Sun', 'Mars') and (ch.own_or_exalted('Sun') or ch.own_or_exalted('Mars')):
        return hit('Sun with Mars is often called a marital dosha; with one of them strong, it does not apply.',
                   f'Sun and Mars in {RASIS[ch.sign["Sun"]]}')


@rule('MH-06', 'marital_harmony', 'marriage', 'Lagna lord or 6th lord in the 8th with a strong dispositor')
def r_mh06(ch):
    out = []
    for h in (1, 6):
        p = ch.lord[h]
        d = ch.dispositor(p)
        if ch.house[p] == 8 and (ch.house[d] in TRIKONA or ch.jupiter_on(d) or ch.own_or_exalted(d)):
            out.append(hit('No marital dosha from this placement: its dispositor is strong.',
                           f'{"lagna" if h == 1 else "6th"} lord {ch.name(p)}; dispositor {ch.name(d)}', []))
    return out


# -- children and education ----------------------------------------------------

@rule('ED-02', 'education_choice', 'education', 'Jupiter in the 12th')
def r_ed02(ch):
    if ch.house['Jupiter'] == 12:
        return hit('A research path later in life; finish the main degree first.', ch.name('Jupiter'), ['Jupiter'])


@rule('ED-MAP', 'education_choice', 'education', 'Field of study from the dasa of the study years', ages=(15, 25))
def r_ed_map(ch):
    fields = {'Jupiter': 'HR, administration, finance, marketing, banking, insurance, logistics',
              'Mercury': 'IT (with Rahu: AI; with Moon: creative AI; with Saturn: accounts; with Sun: science and technology)',
              'Rahu': 'electrical, electronics, computer science, mechatronics, foreign trade',
              'Ketu': 'research, PhD'}
    out = []
    for d in ch.dasas:
        if d['lord'] in fields and ch.age(d['start']) < 25 and ch.age(d['end']) > 15:
            out.append(hit(f'{d["lord"]} dasa runs in the study years: suited fields include {fields[d["lord"]]}. '
                           'Combine with marks, interest and affordability.', f'{d["lord"]} dasa', [d['lord']], 'mixed'))
    return out


@rule('ED-15', 'education_choice', 'education', 'Strong 1st and 5th lords')
def r_ed15(ch):
    if ch.strong(ch.lord[1]) and ch.strong(ch.lord[5]):
        return hit('Good for higher education (an engineering stream suits).', f'lagna lord {ch.lord[1]}, 5th lord {ch.lord[5]}')


# -- foreign and relocation ----------------------------------------------------

@rule('H12-15', 'twelfth_house_significations', 'foreign', 'Long stay abroad')
def r_h12_15(ch):
    l7, l12, l5 = ch.lord[7], ch.lord[12], ch.lord[5]
    strong12 = ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA
    why = []
    if ch.house[l7] == 12 or (l7 != l12 and ch.linked(l7, l12)):
        why.append(f'7th lord {l7} linked to the 12th')
    if (ch.house[l5] == 12 or (l5 != l12 and ch.together(l5, l12))) and strong12:
        why.append(f'5th lord {l5} with the 12th and a strong 12th lord')
    if why:
        return hit('A long stay abroad is indicated (permanent residence abroad is possible).', '; '.join(why), [l7, l5])


@rule('H12-16', 'twelfth_house_significations', 'foreign', 'Relocation periods', dasa_only=True)
def r_h12_16(ch):
    l4, l7, l12 = ch.lord[4], ch.lord[7], ch.lord[12]
    lords = []
    if ch.house[l12] in (4, 7):
        lords.append(l12)
    if ch.house[l4] == 12:
        lords.append(l4)
    if ch.house[l7] == 12:
        lords.append(l7)
    if lords:
        return hit('A change of job, business or residence is close to certain in these dasas (short stints abroad '
                   'in the bhuktis).', ', '.join(ch.name(p) for p in lords), lords, 'mixed')


# -- 12th house and spirituality -----------------------------------------------

@rule('P12-01', 'planets_in_12th', 'spiritual', 'Several planets in the 12th', dasa_only=True)
def r_p12_01(ch):
    tw = ch.in_house(12)
    if len(tw) < 2:
        return None
    l12 = ch.lord[12]
    if ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA or ch.linked(l12, ch.lord[1]):
        return hit('Each of these planets\' dasas becomes productive (foreign links, investments).', ', '.join(tw), tw)
    return hit('These dasas bring 12th-house expenses and losses; plan spending.', ', '.join(tw), tw, 'challenging')


@rule('P12-11', 'planets_in_12th', 'career', 'Saturn in the 12th', dasa_only=True)
def r_p12_11(ch):
    if ch.house['Saturn'] != 12:
        return None
    if ch.retro('Saturn'):
        if ch.lagna in (8, 9):
            return hit('Retrograde Saturn in the 12th for this lagna strains family, finances or health in its dasa.',
                       ch.name('Saturn'), ['Saturn'], 'challenging')
        extra = ' - even bigger with the Rahu/Ketu link' if ch.node_on('Saturn') else ''
        return hit(f'A major yoga: career and financial rise, own business success{extra}.', ch.name('Saturn') + ' retrograde', ['Saturn'])
    if ch.dig(ch.lord[12]) == 'own':
        return hit('Own business succeeds; large earnings and investment gains.', ch.name('Saturn'), ['Saturn'])
    return hit('Generally good; may bring job changes and moves for work.', ch.name('Saturn'), ['Saturn'], 'mixed')


@rule('H12-11', 'twelfth_house_significations', 'personality', 'Love of solitude')
def r_h12_11(ch):
    who = [n for n, p in (('lagna lord', ch.lord[1]), ('5th lord', ch.lord[5]), ('9th lord', ch.lord[9]), ('Moon', 'Moon'))
           if ch.house[p] == 12]
    if who:
        return hit('Enjoys time alone; meditation and quiet suit.', ', '.join(who) + ' in the 12th', [], 'mixed')


@rule('H12-SPIRIT', 'twelfth_house_significations', 'spiritual', 'Jupiter or Ketu in the 12th', dasa_only=True)
def r_h12_spirit(ch):
    who = [p for p in ('Jupiter', 'Ketu') if ch.house[p] == 12]
    if who:
        return hit('Spiritual depth, pilgrimages and quiet charity; intuition through dreams.', ', '.join(who) + ' in the 12th', who)


@rule('H12-06', 'twelfth_house_significations', 'personality', 'Sleep')
def r_h12_06(ch):
    l12 = ch.lord[12]
    if ch.own_or_exalted(l12) or ch.house[l12] in KENDRA + TRIKONA:
        return hit('Sound sleep and peace of mind, whatever the bank balance.', f'12th lord {ch.name(l12)}')


# -- dusthana dasas ------------------------------------------------------------

@rule('DU-01', 'dusthana_planets', 'general', 'Dasa of a planet in the 6th, 8th or 12th', dasa_only=True)
def r_du01(ch):
    out = []
    for p in PLANETS:
        h = ch.house[p]
        if h not in DUSTHANA:
            continue
        lord = ch.lord[h]
        if ch.own_or_exalted(lord) or ch.jupiter_on(p) or ch.sign[p] in ch.c.asp_signs['Jupiter']:
            out.append(hit(f'{p} sits in a hidden house but its dasa still succeeds (the house lord is strong or Jupiter helps).',
                           f'{ch.name(p)}; house lord {ch.name(lord)}', [p]))
        else:
            out.append(hit(f'{p} dasa may be difficult (in house {h} without support).', f'{ch.name(p)}; house lord {ch.name(lord)}',
                           [p], 'challenging'))
    return out


@rule('DU-04', 'dusthana_planets', 'wealth', '8th lord in the 8th', dasa_only=True)
def r_du04(ch):
    l8 = ch.lord[8]
    if ch.house[l8] == 8 and ch.dig(l8) == 'own':
        if ch.retro(l8):
            return hit('Hardship in its dasa (finances when young, family strain in a child).', ch.name(l8), [l8], 'challenging')
        return hit('A yoga: lends money to others rather than borrowing.', ch.name(l8), [l8])


@rule('DU-05', 'dusthana_planets', 'general', '8th lord in a kendra or trikona', dasa_only=True)
def r_du05(ch):
    l8 = ch.lord[8]
    if ch.house[l8] in KENDRA + TRIKONA and l8 != ch.lord[1]:
        if ch.retro(l8):
            return hit('Turns into a yoga (e.g. in the 4th: property and vehicles).', ch.name(l8) + ' retrograde', [l8])
        return hit('Losses or domestic strain in its dasa.', ch.name(l8), [l8], 'challenging')


@rule('DU-09', 'dusthana_planets', 'general', 'Adhi yoga')
def r_adhi(ch):
    places = {6, 7, 8}
    ben = [p for p in ('Mercury', 'Jupiter', 'Venus') if E.house_from(ch.sign[p], ch.sign['Moon']) in places]
    if len({E.house_from(ch.sign[p], ch.sign['Moon']) for p in ben}) >= 2:
        return hit('Adhi yoga: prosperity, comforts, success over opponents.', ', '.join(ben) + ' in the 6th/7th/8th from the Moon', ben)


@rule('J8-04', 'jupiter_8th_dasa', 'general', 'Dasa lord in friction with its star lord', dasa_only=True)
def r_j804(ch):
    out = []
    for d in ch.dasas:
        p = d['lord']
        st = ch.star_lord(p)
        if st != p and ch.mutual(p, st) == SIX_EIGHT and ch.age(d['start']) < 70 and d['end'] > ch.now:
            out.append(hit(f'{p} dasa has friction from its star lord {st}: expected gains may not fully come.',
                           f'{p} and {st} are 6/8 from each other', [p], 'mixed'))
    return out


@rule('J8-01', 'jupiter_8th_dasa', 'general', 'Exalted lagna lord in the 8th', dasa_only=True)
def r_j801(ch):
    l1 = ch.lord[1]
    if ch.house[l1] == 8 and ch.dig(l1) == 'exalted':
        return hit('Not a hidden or weak placement: a strong yoga.', ch.name(l1), [l1])


# -- Saturn ---------------------------------------------------------------------

@rule('SAT-GEN', 'saturn_raja_yoga', 'career', 'Saturn: yoga or dosha', dasa_only=True)
def r_sat(ch):
    p = 'Saturn'
    basis = ch.name(p) + (' retrograde' if ch.retro(p) else '')
    rescued = ch.jupiter_on(p) or ch.node_on(p)
    d = ch.dig(p)
    if d == 'debilitated':
        if ch.retro(p) or ch.nb(p) or rescued:
            return hit('Debilitated Saturn is rescued (retrograde, cancellation, Jupiter or a node): Saturn dasa turns favourable.',
                       basis, [p])
        return hit('Debilitated Saturn without rescue: Saturn dasa needs care; harmless if it falls in childhood or very late.',
                   basis, [p], 'challenging')
    if d in ('own', 'exalted'):
        if ch.retro(p) and not rescued:
            return hit('Saturn is dignified but retrograde with no rescue: its dasa gives less than expected.', basis, [p], 'challenging')
        return hit('Saturn has positional strength: its dasa is a yoga period (career and assets).', basis, [p])
    if rescued:
        return hit('Saturn is linked to Jupiter or a node: its dasa turns favourable.', basis, [p])


@rule('SAT-15', 'saturn_raja_yoga', 'personality', 'Aptitude for astrology')
def r_sat15(ch):
    why = []
    if ch.house['Mercury'] in KENDRA + TRIKONA:
        why.append('Mercury in a kendra/trikona')
    if ch.house['Jupiter'] == 1 or ch.lagna in ch.c.asp_signs['Jupiter']:
        why.append('Jupiter in or aspecting the lagna')
    if any(ch.house[p] == 2 for p in ('Saturn', 'Rahu', 'Ketu')):
        why.append('Saturn or a node in the 2nd')
    if len(why) >= 2:
        return hit('Interest and aptitude for astrology.', '; '.join(why))


# -- eclipse ---------------------------------------------------------------------

@rule('ECL', 'eclipse_grahana', 'general', 'Moon with Rahu or Ketu')
def r_ecl(ch):
    for n in NODES:
        if ch.together('Moon', n):
            if ch.sign['Moon'] in (1, 3):
                return hit(f'Moon with {n} in the Moon\'s own or exaltation sign: no eclipse dosha; the node boosts the Moon.',
                           f'Moon and {n} in {RASIS[ch.sign["Moon"]]}', ['Moon', n])
            if ch.jupiter_on('Moon') or ch.strong(ch.dispositor('Moon')):
                return hit(f'Moon with {n} is neutralised by Jupiter or a strong sign lord.', f'Moon and {n} in {RASIS[ch.sign["Moon"]]}',
                           ['Moon', n], 'mixed')
            return hit(f'Moon with {n}: worry and restlessness in their periods; routine and rest help.',
                       f'Moon and {n} in {RASIS[ch.sign["Moon"]]}', ['Moon', n], 'challenging')
    if ch.together('Sun', 'Moon'):
        return hit('Sun with Moon (new-Moon birth): strong will; the house they occupy gets a mixed start that improves.',
                   f'Sun and Moon in {RASIS[ch.sign["Sun"]]}', ['Sun', 'Moon'], 'mixed')


# -- whole-chart tests ---------------------------------------------------------

@rule('CX-12', 'complex_chart_techniques', 'general', 'Karma test of the 1st, 5th and 9th lords')
def r_cx12(ch):
    marks = {}
    for h in (1, 5, 9):
        p = ch.lord[h]
        marks[h] = (p, not ch.weak(p) or ch.strong(p))
    good = [h for h, (_, ok) in marks.items() if ok]
    basis = '; '.join(f'{h}th lord {p} {"strong" if ok else "weak"}' for h, (p, ok) in marks.items()).replace('1th', '1st').replace('5th', '5th')
    if len(good) == 3:
        return hit('All three dharma lords hold up: life tends to flow and efforts pay.', basis)
    if len(good) == 2:
        return hit('Two of the three dharma lords hold up: steady progress with one weak area.', basis, [], 'mixed')
    return hit('Most dharma lords are weak: settling takes persistent effort; gains come later.', basis, [], 'challenging')


@rule('CX-13', 'complex_chart_techniques', 'general', 'Dasa sequence audit (age 15 to 50)')
def r_cx13(ch):
    weak = []
    for d in ch.dasas:
        a0, a1 = ch.age(d['start']), ch.age(d['end'])
        if a1 < 15 or a0 > 50:
            continue
        p = d['lord']
        if p in NODES:
            bad = ch.house[ch.dispositor(p)] in DUSTHANA and ch.house[ch.star_lord(p)] in DUSTHANA
        else:
            bad = ch.weak(p) and not ch.strong(p)
        weak.append((p, bad))
    if not weak:
        return None
    run = best = 0
    for _, bad in weak:
        run = run + 1 if bad else 0
        best = max(best, run)
    seq = ', '.join(f'{p}{" (weak)" if bad else ""}' for p, bad in weak)
    if best >= 3:
        return hit('A long run of weak dasas between 15 and 50: progress is slow despite the yogas in the chart; '
                   'expect results later and plan for them.', seq, [], 'challenging')
    good = sum(1 for _, b in weak if not b)
    if good == len(weak):
        return hit('Every dasa between 15 and 50 is supportive: a good working life.', seq)
    return hit('A mix of supportive and weak dasas between 15 and 50.', seq, [], 'mixed')


# -- nakshatra traits (data/rulebook/nakshatra_traits.json) ----------------------
# Traits read from the nakshatra (and pada) a point sits in. They describe the
# chart and are not tied to a period, so every row reads 'always'.

NK_SET = 'nakshatra_traits'
NK_POINTS = ('Lagna',) + tuple(PLANETS)
WHO_ORDER = ((1, 'self'), (7, 'spouse'), (5, 'children'), (9, 'father'), (4, 'mother'), (3, 'siblings'))
WHO_TEXT = {'self': 'you', 'spouse': 'the spouse', 'children': 'the children', 'father': 'the father',
            'mother': 'the mother', 'siblings': 'the siblings'}


def nak_of(ch, p):
    return A.NAKS[ch.pt[p]['nak']]


def pada_of(ch, p):
    return ch.pt[p]['pada']


def who(ch, p):
    """Whose life a point's theme shows in, by the houses the planet rules."""
    if p in ('Lagna', 'Moon') or p in NODES:
        return WHO_TEXT['self']
    owned = ch.owned.get(p, [])
    for h, key in WHO_ORDER:
        if h in owned:
            return WHO_TEXT[key]
    return WHO_TEXT['self']


def _in(ch, points, *naks):
    return [p for p in points if nak_of(ch, p) in naks]


def _nk(finding, ch, p, tone='favourable'):
    return hit(finding, f'{p} in {nak_of(ch, p)} pada {pada_of(ch, p)}', [], tone)


@rule('NK-01', NK_SET, 'personality', 'Mrigashira: the seeker')
def r_nk01(ch):
    return [_nk(f'{p} in Mrigashira: a seeker who keeps chasing the next goal; enjoys travel, speed and fragrances.', ch, p)
            for p in _in(ch, ('Lagna', 'Moon'), 'Mrigashira')]


NK02_TEXT = {
    1: 'Moon in the first pada of Mrigashira: the search centres on creativity, romance and studies.',
    2: 'Moon in the second pada of Mrigashira: the search turns analytical - checking, reviewing and measuring.',
    3: 'Moon in the third pada of Mrigashira: the search is for beauty, comfort and money.',
    4: 'Moon in the fourth pada of Mrigashira: the search turns inward - occult subjects, spirituality and hidden knowledge.',
}


@rule('NK-02', NK_SET, 'personality', 'Mrigashira Moon by pada')
def r_nk02(ch):
    if nak_of(ch, 'Moon') == 'Mrigashira':
        return _nk(NK02_TEXT[pada_of(ch, 'Moon')], ch, 'Moon')


@rule('NK-03', NK_SET, 'general', 'Punarvasu: things return')
def r_nk03(ch):
    return [_nk(f'{p} in Punarvasu: events repeat for {who(ch, p)} - returning to a place, a job or a person after a gap.', ch, p)
            for p in _in(ch, NK_POINTS, 'Punarvasu')]


@rule('NK-04', NK_SET, 'personality', 'Mercury in Punarvasu: the name')
def r_nk04(ch):
    if nak_of(ch, 'Mercury') == 'Punarvasu':
        return _nk(f'Mercury in Punarvasu: a name change, or a name with repeated letters, is likely for {who(ch, "Mercury")}.',
                   ch, 'Mercury')


@rule('NK-05', NK_SET, 'marriage', '7th lord in Vishakha')
def r_nk05(ch):
    p = ch.lord[7]
    if nak_of(ch, p) == 'Vishakha':
        return _nk(f'The 7th lord {p} is in Vishakha: married life can see phases of distance; conscious effort keeps it together.',
                   ch, p, 'mixed')


@rule('NK-06', NK_SET, 'family', '4th lord in Vishakha')
def r_nk06(ch):
    p = ch.lord[4]
    if nak_of(ch, p) == 'Vishakha':
        return _nk(f'The 4th lord {p} is in Vishakha: likely to live away from the family home at some stage.', ch, p, 'mixed')


@rule('NK-07', NK_SET, 'personality', 'Anuradha: the lotus')
def r_nk07(ch):
    return [_nk(f'{p} in Anuradha: rises from modest beginnings and gathers loyal supporters; a devotional nature.', ch, p)
            for p in _in(ch, ('Lagna', 'Moon'), 'Anuradha')]


@rule('NK-08', NK_SET, 'spiritual', 'Rahu in Rohini')
def r_nk08(ch):
    if nak_of(ch, 'Rahu') == 'Rohini':
        return _nk('Rahu in Rohini: devotion to Krishna; pilgrimages such as Khatu Shyam may appeal.', ch, 'Rahu')


@rule('NK-09', NK_SET, 'personality', 'Ketu in Rohini')
def r_nk09(ch):
    if nak_of(ch, 'Ketu') == 'Rohini':
        return _nk(f'Ketu in Rohini: a liking for the flute or other wind instruments for {who(ch, "Ketu")}.', ch, 'Ketu')


@rule('NK-10', NK_SET, 'marriage', 'Musical spouse')
def r_nk10(ch):
    return [_nk(f'{p} in Dhanishtha in the 7th house: the spouse is likely to be musical, with a feel for rhythm.', ch, p)
            for p in _in(ch, ('Mars', 'Venus'), 'Dhanishtha') if ch.house[p] == 7]


@rule('NK-11', NK_SET, 'marriage', '7th lord in a late-marriage nakshatra')
def r_nk11(ch):
    p = ch.lord[7]
    if nak_of(ch, p) in ('Dhanishtha', 'Uttara Ashadha'):
        return _nk(f'The 7th lord {p} is in a nakshatra linked with late marriage: marriage may come later, '
                   f'or one may choose to stay single.', ch, p, 'mixed')


@rule('NK-12', NK_SET, 'wealth', 'Wealth lord in Dhanishtha')
def r_nk12(ch):
    lords = list(dict.fromkeys((ch.lord[2], ch.lord[11])))
    return [_nk(f'{p}, a lord of wealth, is in Dhanishtha: unearned money such as inheritance or family property is likely.', ch, p)
            for p in _in(ch, lords, 'Dhanishtha')]


@rule('NK-13', NK_SET, 'children', 'Twins')
def r_nk13(ch):
    pts = list(dict.fromkeys((ch.lord[5], 'Jupiter')))
    return [_nk(f'{p} in the Gemini pada of Ashwini: a possibility of twins in the family.', ch, p)
            for p in _in(ch, pts, 'Ashwini') if pada_of(ch, p) == 3]


@rule('NK-14', NK_SET, 'personality', 'Ashwini: speed and care')
def r_nk14(ch):
    return [_nk(f'{p} in Ashwini: quick and active; loves vehicles and speed; caring towards animals.', ch, p)
            for p in _in(ch, ('Lagna', 'Moon'), 'Ashwini')]


@rule('NK-15', NK_SET, 'personality', 'Ashlesha: the strategist')
def r_nk15(ch):
    return [_nk(f'{p} in Ashlesha: a strategic mind suited to chess, mathematics or research; '
                f'attachments run deep for {who(ch, p)}.', ch, p)
            for p in _in(ch, NK_POINTS, 'Ashlesha')]


@rule('NK-16', NK_SET, 'career', 'Krittika: the cut')
def r_nk16(ch):
    return [_nk(f'{p} in Krittika: a talent for cooking, or for work that involves cutting and editing such as film.', ch, p)
            for p in _in(ch, NK_POINTS, 'Krittika')]


@rule('NK-17', NK_SET, 'marriage', '7th lord in Purva Ashadha')
def r_nk17(ch):
    p = ch.lord[7]
    if nak_of(ch, p) == 'Purva Ashadha':
        return _nk(f'The 7th lord {p} is in Purva Ashadha: marriage tends to come early.', ch, p)


@rule('NK-18', NK_SET, 'education', 'Shravana: the listener')
def r_nk18(ch):
    return [_nk(f'{p} in Shravana: learns best by listening; drawn to the sky and the stars.', ch, p)
            for p in _in(ch, NK_POINTS, 'Shravana')]


@rule('NK-19', NK_SET, 'personality', 'Hasta: the hand')
def r_nk19(ch):
    return [_nk(f'{p} in Hasta: a distinctive smile and a good sense of humour; likes rings, watches and hand adornments.', ch, p)
            for p in _in(ch, ('Lagna', 'Moon'), 'Hasta')]


@rule('NK-20', NK_SET, 'career', 'Magha: the throne')
def r_nk20(ch):
    return [_nk(f'{p} in Magha: a pull towards leadership and public standing; fond of grand furniture and ancestral traditions.',
                ch, p)
            for p in _in(ch, ('Lagna', 'Moon', 'Sun'), 'Magha')]


@rule('NK-21', NK_SET, 'career', 'Saturn in Ardra')
def r_nk21(ch):
    if nak_of(ch, 'Saturn') == 'Ardra':
        return _nk('Saturn in Ardra: work that lifts up the neglected, people or stray animals; '
                   'struggles come first and recognition late.', ch, 'Saturn', 'mixed')


@rule('NK-22', NK_SET, 'personality', 'Node in Ardra or Moola: dogs')
def r_nk22(ch):
    return [_nk(f'{p} in Ardra or Moola: likely to keep dogs or care for strays.', ch, p)
            for p in _in(ch, NODES, 'Ardra', 'Moola')]


@rule('NK-23', NK_SET, 'family', 'Phalguni: left hand')
def r_nk23(ch):
    pts = list(dict.fromkeys((ch.lord[1], ch.lord[3])))
    return [_nk(f'{p} in a Phalguni nakshatra: left-handedness may show up for {who(ch, p)}.', ch, p)
            for p in _in(ch, pts, 'Purva Phalguni', 'Uttara Phalguni')]


@rule('NK-24', NK_SET, 'personality', 'Uttara Ashadha: undefeated')
def r_nk24(ch):
    return [_nk(f'{p} in Uttara Ashadha: does not accept defeat; keeps returning until the goal is won.', ch, p)
            for p in _in(ch, NK_POINTS, 'Uttara Ashadha')]


@rule('NK-25', NK_SET, 'general', 'Benefic in Pushya')
def r_nk25(ch):
    return [_nk(f'{p} in Pushya: steady growth and nourishment for {who(ch, p)}.', ch, p)
            for p in _in(ch, ('Moon', 'Mercury', 'Jupiter', 'Venus'), 'Pushya') if ch.dig(p) != 'debilitated']


@rule('NK-26', NK_SET, 'wealth', 'Wealth star (Sampat tara) remedy')
def r_nk26(ch):
    star = A.NAKS[(ch.pt['Moon']['nak'] + 1) % 27]
    sym = data()[NK_SET]['rules'][-1]['symbols'][star]
    return hit(f'Wealth star (Sampat tara) is {star}: keeping its symbol, {sym}, nearby as a picture or wallpaper '
               f'is a simple remedy that costs nothing.', f'Moon in {nak_of(ch, "Moon")}; next star {star}')


# ── evaluation ───────────────────────────────────────────────────────────────

def evaluate(res, now=None):
    """Rows of the rules that apply to this chart, most relevant first."""
    ch = Chart(res, now)
    rows = []
    for rule_id, ruleset, topic, title, dasa_only, ages, fn in RULES:
        found = fn(ch)
        if not found:
            continue
        for h in (found if isinstance(found, list) else [found]):
            status, window = timing(ch, h['lords'], dasa_only, ages)
            row = {
                'rule_id': rule_id, 'ruleset': ruleset, 'topic': topic, 'rule': title,
                'tone': h['tone'], 'finding': h['finding'], 'basis': h['basis'],
                'period_lords': ', '.join(h['lords']), 'status': status, 'window': window,
            }
            for k, v in row.items():
                if isinstance(v, str) and BANNED.search(v):
                    raise ValueError(f'rule {rule_id}: banned wording in {k}')
            rows.append(row)
    order = {'running now': 0, 'upcoming': 1, 'always': 2, 'past': 3, 'dormant': 4}
    rows.sort(key=lambda r: (order.get(r['status'], 5), TOPICS.index(r['topic'])))
    return rows


def summary(rows):
    """Short text grouped by topic, for an AI reader or a report."""
    lines = []
    for topic in TOPICS:
        mine = [r for r in rows if r['topic'] == topic and r['status'] in ('running now', 'upcoming', 'always')]
        if not mine:
            continue
        lines.append(f'{topic.upper()}:')
        for r in mine:
            when = f' [{r["status"]}: {r["window"]}]' if r['window'] else ''
            lines.append(f'- {r["finding"]}{when}')
    return '\n'.join(lines)
