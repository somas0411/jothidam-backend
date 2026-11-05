"""
kp_timing.py — KP (Krishnamurti Paddhati) event timing, rule-based, no AI model.

    out = compute(res)          # res: astro_engine.compute(); uses res['kp'] and res['meta']

For each life event the classic three KP steps are applied, in this order:

  1. Promise   The sub lord of the event's main cusp (cuspal sub lord, CSL)
               gives the result of the houses its STAR LORD occupies and owns
               ("primary" houses). If those include the event's favourable
               houses and not more negating houses, the event is promised.
               The CSL's own occupied and owned houses are kept as
               "secondary" and only soften a weak verdict to "mixed".
  2. Significators
               Planets linked to the favourable houses at level A (in the star
               of an occupant), B (occupant), C (in the star of the owner) and
               D (owner), scored 4/3/2/1 per house. Rahu and Ketu also carry
               the houses of their sign lord. A planet whose own houses lean
               to the negating group is not "fruitful" for the event.
  3. Timing    Every Vimshottari dasa / bhukti / antaram ahead of the report
               moment (up to HORIZON_YEARS, inside the event's age band) is
               grouped by bhukti: the bhukti lord must be fruitful and the dasa
               lord must not lean clearly to the negating houses; a fruitful
               dasa lord, each dasa/bhukti lord that is also a Ruling Planet of
               the report moment, and the share of fruitful antarams add to the
               score. The best bhuktis are listed with up to two peak antarams
               and the first days of the first peak when the transiting Sun is
               in a sign or star ruled by the bhukti or that antaram lord.
               An event whose age band is already over gets no window.

Site policy (same as predictions.py): no health, disease, death or length of
life event exists in EVENTS, and below age 18 only Education is timed.
Everything is deterministic: same birth details and report moment, same output.
"""

from datetime import timedelta

import swisseph as swe

import astro_engine as A

# event key: main cusp, favourable houses, negating houses, age band (years)
EVENTS = (
    ('marriage',  7,  (2, 7, 11),      (1, 6, 10),  (21, 40)),
    ('job',       10, (2, 6, 10, 11),  (5, 9, 12),  (18, 62)),
    ('business',  7,  (7, 10, 11),     (6, 8, 12),  (21, 70)),
    ('money',     11, (2, 6, 11),      (5, 8, 12),  (18, 75)),
    ('property',  4,  (4, 11, 12),     (3, 5, 10),  (23, 75)),
    ('vehicle',   4,  (4, 11),         (3, 8, 12),  (18, 75)),
    ('abroad',    12, (3, 9, 12),      (4, 11),     (18, 65)),
    ('children',  5,  (2, 5, 11),      (1, 4, 10),  (23, 42)),
    ('education', 4,  (4, 9, 11),      (3, 8, 12),  (4, 30)),
)
MINOR_EVENTS = ('education',)
ADULT_AGE = 18

LEVEL_SCORE = {'a': 4, 'b': 3, 'c': 2, 'd': 1}
HORIZON_YEARS = 15
WINDOWS_PER_EVENT = 3
RP_BONUS = 1.0
W_DASA, W_BHUKTI, W_ANTARA = 1.0, 2.0, 1.5
PEAKS_PER_WINDOW = 2
SUN_DAYS_MAX = 3              # transit date spans listed per window

PLANETS = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu')


# ── ruling planets of a moment ───────────────────────────────────────────────

def ruling_planets_at(local_dt, offset_hours, lat, lon, node='mean'):
    """KP ruling planets for a moment at a place, strongest first, with the raw parts."""
    jd = A.julian_day(local_dt - timedelta(hours=offset_hours))
    pos = A._positions(jd, lat, lon, swe.SIDM_KRISHNAMURTI, node, b'P')
    asc = pos['cusps'][0]
    moon = pos['pts']['Moon'][0]
    pan = A.panchangam(pos['pts']['Sun'][0], moon, local_dt, offset_hours, lat, lon)
    l_sign, l_star, l_sub, _ = A.kp_lords(asc)
    m_sign, m_star, m_sub, _ = A.kp_lords(moon)
    parts = {'lagna_star_lord': l_star, 'lagna_sign_lord': l_sign, 'moon_star_lord': m_star,
             'moon_sign_lord': m_sign, 'day_lord': pan['vara_lord'], 'lagna_sub_lord': l_sub,
             'moon_sub_lord': m_sub}
    order = list(dict.fromkeys(parts[k] for k in ('lagna_star_lord', 'lagna_sign_lord', 'moon_star_lord',
                                                  'moon_sign_lord', 'day_lord')))
    # A node joins the ruling planets when it sits in a sign ruled by one of them.
    for node_name in ('Rahu', 'Ketu'):
        sign_lord = A.SIGN_LORDS[A.get_rasi(pos['pts'][node_name][0])]
        if sign_lord in order and node_name not in order:
            order.append(node_name)
    return {'moment': local_dt, 'parts': parts, 'planets': order}


# ── houses a planet signifies ────────────────────────────────────────────────

def _signified(kp):
    """planet -> {'primary': houses via its star lord, 'own': its own houses, 'all': both}."""
    sig = {r['planet']: r for r in kp['planet_significators']}
    agents = {a['node']: a for a in kp['node_agents']}
    out = {}
    for p in PLANETS:
        r = sig[p]
        primary = set(r['l1']) | set(r['l3'])
        own = set(r['l2']) | set(r['l4'])
        if p in agents:                                    # a node also acts for its sign lord
            sl = sig[agents[p]['sign_lord']]
            own |= set(sl['l2']) | set(sl['l4'])
        out[p] = {'primary': sorted(primary), 'own': sorted(own), 'all': sorted(primary | own)}
    return out


def _house_levels(kp):
    """house -> {planet: strongest level letter}."""
    out = {}
    for r in kp['house_significators']:
        best = {}
        for lvl in ('a', 'b', 'c', 'd'):
            for p in r[lvl]:
                best.setdefault(p, lvl)
        out[r['house']] = best
    return out


# ── promise ──────────────────────────────────────────────────────────────────

def _verdict(fav_p, neg_p, fav_s):
    if fav_p and not neg_p:
        return 'strong'
    if fav_p and len(fav_p) >= len(neg_p):
        return 'promised'
    if fav_p or fav_s:
        return 'mixed'
    return 'weak'


# ── transit refinement ───────────────────────────────────────────────────────

def _sun_lon(local_dt, offset_hours):
    jd = A.julian_day(local_dt - timedelta(hours=offset_hours))
    with A._SWE_LOCK:
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        return A.norm(swe.calc_ut(jd, A.SWE_IDS['Sun'], A._EPH | swe.FLG_SIDEREAL)[0][0])


def sun_spans(start, end, lords, offset_hours, limit=SUN_DAYS_MAX):
    """Date spans inside [start, end) when the Sun is in a sign or star ruled by one of `lords`."""
    lords = set(lords)
    spans, cur, day = [], None, start.replace(hour=12, minute=0, second=0, microsecond=0)
    while day < end and len(spans) < limit:
        s = _sun_lon(day, offset_hours)
        hit = A.SIGN_LORDS[A.get_rasi(s)] in lords or A.NAK_LORDS[A.get_nak(s)] in lords
        if hit and cur is None:
            cur = [day, day]
        elif hit:
            cur[1] = day
        elif cur is not None:
            spans.append(tuple(cur))
            cur = None
        day += timedelta(days=1)
    if cur is not None and len(spans) < limit:
        spans.append(tuple(cur))
    return spans



def _against(p, houses, fav, neg):
    """A dasa lord whose houses lean clearly to the negating group."""
    h = houses[p]['all']
    return len([x for x in h if x in neg]) > len([x for x in h if x in fav]) + 1


def _windows(antaras, now, horizon, birth, ages, fruitful, houses, fav, neg, rp_set, offset):
    """Bhukti windows ahead, best first by score, then listed in date order, each with peak antarams."""
    groups = {}
    for d, b, a, start, end in antaras:
        if end <= now or start >= horizon:
            continue
        groups.setdefault((d, b), []).append((a, start, end))
    out = []
    for (d, b), rows in groups.items():
        start, end = max(rows[0][1], now), rows[-1][2]
        y0, y1 = (start - birth).days / 365.25, (end - birth).days / 365.25
        if y1 < ages[0] or y0 > ages[1] or b not in fruitful or _against(d, houses, fav, neg):
            continue
        peaks = [(a, max(s, now), e) for a, s, e in rows if a in fruitful]
        if not peaks:
            continue
        rp_hits = [x for x in dict.fromkeys((d, b)) if x in rp_set]
        score = (W_BHUKTI + (W_DASA if d in fruitful else 0) + RP_BONUS * len(rp_hits)
                 + W_ANTARA * min(1.0, len(peaks) / 3))
        peaks.sort(key=lambda r: (-(r[0] in rp_set), r[1]))
        peaks = sorted(peaks[:PEAKS_PER_WINDOW], key=lambda r: r[1])
        out.append({'dasa': d, 'bhukti': b, 'start': start, 'end': end, 'score': round(score, 2),
                    'rp_hits': rp_hits,
                    'peaks': [{'antara': a, 'start': s, 'end': e, 'ruling': a in rp_set} for a, s, e in peaks]})
    out.sort(key=lambda w: (-w['score'], w['start']))
    out = sorted(out[:WINDOWS_PER_EVENT], key=lambda w: w['start'])
    for w in out:
        p = w['peaks'][0]
        w['sun'] = sun_spans(p['start'], p['end'], (w['bhukti'], p['antara']), offset)
    return out

# ── main ─────────────────────────────────────────────────────────────────────

def _antaras(kp_moon_lon, birth, now):
    tree = A.vimshottari(kp_moon_lon, birth, now, levels=3)
    for d in tree['dasas']:
        for b in d.get('sub', []):
            for a in b.get('sub', []):
                yield d['lord'], b['lord'], a['lord'], a['start'], a['end']


def compute(res, now=None):
    m, kp = res['meta'], res['kp']
    birth = m['local_dt']
    now = now or m['generated_at']
    offset = m['utc_offset']
    age = (now - birth).days / 365.25
    rp = ruling_planets_at(now, offset, m['lat'], m['lon'], m.get('node', 'mean'))
    rp_set = set(rp['planets'])
    houses = _signified(kp)
    levels = _house_levels(kp)
    cusps = kp['cusps']
    moon_lon = next(p['lon'] for p in kp['planets'] if p['name'] == 'Moon')
    antaras = list(_antaras(moon_lon, birth, now))
    horizon = now + timedelta(days=HORIZON_YEARS * A.YEAR_DAYS)

    events = []
    for key, cusp, fav, neg, ages in EVENTS:
        if age < ADULT_AGE and key not in MINOR_EVENTS:
            continue
        csl = cusps[cusp - 1]['sub_lord']
        star = next(p['star_lord'] for p in kp['planets'] if p['name'] == csl)
        h = houses[csl]
        fav_p = [x for x in h['primary'] if x in fav]
        neg_p = [x for x in h['primary'] if x in neg]
        fav_s = [x for x in h['own'] if x in fav]
        verdict = _verdict(fav_p, neg_p, fav_s)

        # significators of the favourable houses
        score = {}
        for hh in fav:
            for p, lvl in levels[hh].items():
                score[p] = score.get(p, 0) + LEVEL_SCORE[lvl]
        for node_name in ('Rahu', 'Ketu'):                  # a node carries its sign lord's links
            agent = next(a for a in kp['node_agents'] if a['node'] == node_name)
            if agent['sign_lord'] in score:
                score[node_name] = score.get(node_name, 0) + score[agent['sign_lord']] / 2
        sigs = []
        for p, s in sorted(score.items(), key=lambda kv: (-kv[1], PLANETS.index(kv[0]))):
            f = len([x for x in houses[p]['all'] if x in fav])
            n = len([x for x in houses[p]['all'] if x in neg])
            sigs.append({'planet': p, 'score': round(s, 1), 'fav_houses': f, 'neg_houses': n,
                         'fruitful': f > n or (f and f == n and p in rp_set), 'ruling': p in rp_set})
        fruitful = {s['planet']: s for s in sigs if s['fruitful']}

        windows = []
        past_band = (now - birth).days / 365.25 > ages[1]
        if verdict != 'weak' and not past_band:
            windows = _windows(antaras, now, horizon, birth, ages, fruitful, houses, fav, neg, rp_set, offset)
        events.append({'event': key, 'cusp': cusp, 'fav': list(fav), 'neg': list(neg), 'ages': ages,
                       'csl': csl, 'csl_star': star, 'csl_primary': h['primary'], 'csl_own': h['own'],
                       'fav_primary': fav_p, 'neg_primary': neg_p, 'fav_own': fav_s,
                       'verdict': verdict, 'significators': sigs, 'windows': windows,
                       'past_band': past_band})
    return {'ruling_planets': rp, 'age': round(age, 2), 'horizon_years': HORIZON_YEARS, 'events': events}
