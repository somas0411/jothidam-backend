"""
charts.py — chart contents shared by the web page, the Excel workbook and
the PDF. A chart "spec" says what sits in every sign (South Indian layout)
and in every house (North Indian layout); each output only has to draw it.
"""
import i18n

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

# South Indian layout: sign index -> (row, col) on a 4x4 grid. Signs are
# fixed: Meena top-left, then Mesha, Rishabha, Mithuna across the top and
# onwards clockwise.
SOUTH_POS = {11: (0, 0), 0: (0, 1), 1: (0, 2), 2: (0, 3),
             3: (1, 3), 4: (2, 3), 5: (3, 3), 6: (3, 2),
             7: (3, 1), 8: (3, 0), 9: (2, 0), 10: (1, 0)}

# North Indian layout on a unit square (x right, y down). Houses are fixed:
# house 1 is the top-centre diamond and the count runs anticlockwise.
# value = (text anchor x, y, polygon points)
NORTH_HOUSES = {
    1:  (0.50, 0.25, [(0.5, 0.0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.25)]),
    2:  (0.25, 0.09, [(0.0, 0.0), (0.5, 0.0), (0.25, 0.25)]),
    3:  (0.09, 0.25, [(0.0, 0.0), (0.0, 0.5), (0.25, 0.25)]),
    4:  (0.25, 0.50, [(0.0, 0.5), (0.25, 0.25), (0.5, 0.5), (0.25, 0.75)]),
    5:  (0.09, 0.75, [(0.0, 0.5), (0.0, 1.0), (0.25, 0.75)]),
    6:  (0.25, 0.91, [(0.0, 1.0), (0.5, 1.0), (0.25, 0.75)]),
    7:  (0.50, 0.75, [(0.5, 0.5), (0.25, 0.75), (0.5, 1.0), (0.75, 0.75)]),
    8:  (0.75, 0.91, [(0.5, 1.0), (1.0, 1.0), (0.75, 0.75)]),
    9:  (0.91, 0.75, [(1.0, 0.5), (1.0, 1.0), (0.75, 0.75)]),
    10: (0.75, 0.50, [(0.5, 0.5), (0.75, 0.25), (1.0, 0.5), (0.75, 0.75)]),
    11: (0.91, 0.25, [(1.0, 0.0), (1.0, 0.5), (0.75, 0.25)]),
    12: (0.75, 0.09, [(0.5, 0.0), (1.0, 0.0), (0.75, 0.25)]),
}
# Where the sign number sits in each house (towards the inner corner).
NORTH_NUM = {1: (0.50, 0.43), 2: (0.25, 0.19), 3: (0.19, 0.25), 4: (0.43, 0.50),
             5: (0.19, 0.75), 6: (0.25, 0.81), 7: (0.50, 0.57), 8: (0.75, 0.81),
             9: (0.81, 0.75), 10: (0.57, 0.50), 11: (0.81, 0.25), 12: (0.75, 0.19)}
# Lines of the North Indian chart on the unit square.
NORTH_LINES = [((0, 0), (1, 1)), ((1, 0), (0, 1)),
               ((0.5, 0), (1, 0.5)), ((1, 0.5), (0.5, 1)),
               ((0.5, 1), (0, 0.5)), ((0, 0.5), (0.5, 0))]


def _token(p, lang):
    t = i18n.abbr(p['name'], lang)
    return t + i18n.retro_mark(lang) if p.get('retro') else t


def _spec(key, title, lagna_sign, sign_planets, lang, sign_tags=None, house_planets=None,
          house_signs=None, center=None):
    """
    sign_planets:  {sign: [tokens]}  (South layout)
    house_planets: {house: [tokens]} (North layout); derived from signs when omitted
    """
    signs = []
    for s in range(12):
        house = ((s - lagna_sign) % 12) + 1
        signs.append({'sign': s, 'label': i18n.rasi(s, lang, short=True),
                      'tag': (sign_tags or {}).get(s, str(house)),
                      'planets': sign_planets.get(s, []), 'lagna': s == lagna_sign})
    houses = []
    for h in range(1, 13):
        s = (house_signs or {}).get(h, (lagna_sign + h - 1) % 12)
        pl = house_planets[h] if house_planets is not None else sign_planets.get((lagna_sign + h - 1) % 12, [])
        houses.append({'house': h, 'sign_num': s + 1, 'planets': pl})
    return {'key': key, 'title': title, 'lagna_sign': lagna_sign, 'signs': signs,
            'houses': houses, 'center': center or []}


def build_specs(res, lang='en'):
    """All charts for one horoscope: d1, d9, bhava, kp, alp (Mandi in all but kp)."""
    v, kp, alp, meta = res['vedic'], res['kp'], res['alp'], res['meta']
    lagna = v['planets'][0]
    # Chart points: lagna, the nine planets and Mandi (when it could be computed).
    # Mandi appears in the Vedic charts (D1, D9, Bhava) and the ALP chart, which
    # redraws the natal rasi chart; KP has its own ayanamsha and does not use it.
    planets = v['planets'] + ([v['mandi']] if v.get('mandi') else [])
    name = meta['name']

    def group(key_fn, items=planets):
        out = {}
        for p in items:
            out.setdefault(key_fn(p), []).append(_token(p, lang))
        return out

    specs = {}

    # D1 Rasi
    specs['d1'] = _spec('d1', i18n.L('rasi_chart', lang), lagna['sign'], group(lambda p: p['sign']), lang,
                        center=[name, i18n.L('rasi_chart', lang)])

    # D9 Navamsa
    specs['d9'] = _spec('d9', i18n.L('navamsa_chart', lang), lagna['navamsa'], group(lambda p: p['navamsa']), lang,
                        center=[name, i18n.L('navamsa_chart', lang)])

    # Bhava (Sripati): planets grouped by bhava, bhava 1 drawn in the lagna sign
    by_bhava = group(lambda p: p['bhava'])
    specs['bhava'] = _spec(
        'bhava', i18n.L('bhava_chart', lang), lagna['sign'],
        {(lagna['sign'] + b - 1) % 12: toks for b, toks in by_bhava.items()}, lang,
        house_planets={h: by_bhava.get(h, []) for h in range(1, 13)},
        center=[name, i18n.L('bhava_chart', lang)])

    # KP: planets by sign with the cusps that fall in each sign; North layout by cusp
    kp_tags = {}
    for c in kp['cusps']:
        kp_tags.setdefault(c['sign'], []).append(ROMAN[c['house'] - 1])
    kp_by_house = group(lambda p: p['house'], kp['planets'])
    specs['kp'] = _spec(
        'kp', i18n.L('kp_chart', lang), kp['lagna_sign'], group(lambda p: p['sign'], kp['planets']), lang,
        sign_tags={s: ' '.join(kp_tags.get(s, [])) for s in range(12)},
        house_planets={h: kp_by_house.get(h, []) for h in range(1, 13)},
        house_signs={c['house']: c['sign'] for c in kp['cusps']},
        center=[name, i18n.L('kp_chart', lang)])

    # ALP: natal planets, houses counted from today's Akshaya lagna
    alp_signs = group(lambda p: p['sign'])
    alp_signs.setdefault(alp['lagna_sign'], []).insert(0, i18n.abbr('ALP', lang))
    specs['alp'] = _spec('alp', i18n.L('alp_chart', lang), alp['lagna_sign'], alp_signs, lang,
                         center=[name, i18n.L('alp_chart', lang)])
    return specs
