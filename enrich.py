"""
enrich.py — derived facts for AI readers.

compute() in astro_engine.py returns the positions. enrich(res) adds what an
astrologer works out from them — lordships, aspects, dignity, strength,
Ashtakavarga, yogas, deeper dasa levels, transits — as flat tables, so that
an AI given the Excel "AI_" sheets or the JSON file can read every fact
directly and derive nothing.

enrich() is a separate step: compute() is unchanged and the web page does
not pay for it. Every table is a list of rows (dicts) whose keys are the
column names; the Excel sheets and the JSON file are written from the same
rows, so they cannot disagree.

Conventions
  * Names are always English: astro_engine.RASIS, NAKS and PLANETS.
  * Houses are whole sign from the lagna unless a column says otherwise.
  * Angles are decimal degrees rounded to 6 places.
  * "*_local" moments are clock time at the birth place, using the UTC
    offset in force at birth; "*_utc" moments are UTC.
  * None means "does not apply" or "could not be computed" (an empty cell).
  * Nothing here concerns death or length of life.

The rules and the variant chosen for each are in RULES and are printed on
the Notes sheet and in AI_ReadMe.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from itertools import combinations

import swisseph as swe

import astro_engine as A
from astro_engine import (COMBUST_ORB, DASA_ORDER, DASA_YRS, EXALT_SIGN, NAKS, OWN_SIGNS, PLANETS,
                          RASIS, SIGN_LORDS, VARGAS, VARGA_KEYS, YEAR_DAYS, angle_diff, norm,
                          varga_part, varga_sign)

SCHEMA = 'horoscopegen-ai/1'

SEVEN = PLANETS[:7]                       # Sun ... Saturn: the planets that own signs
NODES = ('Rahu', 'Ketu')

# ── RULE TABLES ───────────────────────────────────────────────────────────────

# Graha drishti: signs aspected, counted from the planet's own sign (1 = own).
ASPECTS = {'Sun': (7,), 'Moon': (7,), 'Mars': (4, 7, 8), 'Mercury': (7,), 'Jupiter': (5, 7, 9),
           'Venus': (7,), 'Saturn': (3, 7, 10), 'Rahu': (7,), 'Ketu': (7,)}

DEEP_EXALT_DEG = {'Sun': 10, 'Moon': 3, 'Mars': 28, 'Mercury': 15, 'Jupiter': 5, 'Venus': 27, 'Saturn': 20}

# Moolatrikona (D1 only): sign, from degree (inclusive), to degree (exclusive)
MOOLATRIKONA = {'Sun': (4, 0, 20), 'Moon': (1, 3, 30), 'Mars': (0, 0, 12), 'Mercury': (5, 15, 20),
                'Jupiter': (8, 0, 10), 'Venus': (6, 0, 15), 'Saturn': (10, 0, 20)}
# Where the exaltation sign is shared with moolatrikona or own sign, the part
# of it that counts as exaltation in D1 (degrees, upper limit exclusive).
EXALT_PART_D1 = {'Moon': 3, 'Mercury': 15}

# Natural friendship (BPHS): friends, neutrals, enemies
NATURAL = {
    'Sun':     (('Moon', 'Mars', 'Jupiter'), ('Mercury',), ('Venus', 'Saturn')),
    'Moon':    (('Sun', 'Mercury'), ('Mars', 'Jupiter', 'Venus', 'Saturn'), ()),
    'Mars':    (('Sun', 'Moon', 'Jupiter'), ('Venus', 'Saturn'), ('Mercury',)),
    'Mercury': (('Sun', 'Venus'), ('Mars', 'Jupiter', 'Saturn'), ('Moon',)),
    'Jupiter': (('Sun', 'Moon', 'Mars'), ('Saturn',), ('Mercury', 'Venus')),
    'Venus':   (('Mercury', 'Saturn'), ('Mars', 'Jupiter'), ('Sun', 'Moon')),
    'Saturn':  (('Mercury', 'Venus'), ('Jupiter',), ('Sun', 'Moon', 'Mars')),
}
TEMP_FRIEND_PLACES = (2, 3, 4, 10, 11, 12)
COMPOUND = {('Friend', 'Friend'): 'Great friend', ('Neutral', 'Friend'): 'Friend',
            ('Enemy', 'Friend'): 'Neutral', ('Friend', 'Enemy'): 'Neutral',
            ('Neutral', 'Enemy'): 'Enemy', ('Enemy', 'Enemy'): 'Great enemy'}

VIMSOPAKA_POINTS = {'Exalted': 20, 'Moolatrikona': 20, 'Own sign': 20, 'Great friend': 18,
                    'Friend': 15, 'Neutral': 10, 'Enemy': 7, 'Great enemy': 5}
VIMSOPAKA_WEIGHTS = {
    'shodasavarga': {'D1': 3.5, 'D2': 1, 'D3': 1, 'D4': 0.5, 'D7': 0.5, 'D9': 3, 'D10': 0.5, 'D12': 0.5,
                     'D16': 2, 'D20': 0.5, 'D24': 0.5, 'D27': 0.5, 'D30': 1, 'D40': 0.5, 'D45': 0.5, 'D60': 4},
    'dasavarga': {'D1': 3, 'D60': 5, 'D2': 1.5, 'D3': 1.5, 'D7': 1.5, 'D9': 1.5, 'D10': 1.5, 'D12': 1.5,
                  'D16': 1.5, 'D30': 1.5},
    'saptavarga': {'D1': 5, 'D2': 2, 'D3': 3, 'D7': 2.5, 'D9': 4.5, 'D12': 2, 'D30': 1},
    'shadvarga': {'D1': 6, 'D2': 2, 'D3': 4, 'D9': 5, 'D12': 2, 'D30': 1},
}

# Ashtakavarga (Parashara): benefic places counted from each donor.
BAV_PLACES = {
    'Sun': {'Sun': (1, 2, 4, 7, 8, 9, 10, 11), 'Moon': (3, 6, 10, 11), 'Mars': (1, 2, 4, 7, 8, 9, 10, 11),
            'Mercury': (3, 5, 6, 9, 10, 11, 12), 'Jupiter': (5, 6, 9, 11), 'Venus': (6, 7, 12),
            'Saturn': (1, 2, 4, 7, 8, 9, 10, 11), 'Lagna': (3, 4, 6, 10, 11, 12)},
    'Moon': {'Sun': (3, 6, 7, 8, 10, 11), 'Moon': (1, 3, 6, 7, 10, 11), 'Mars': (2, 3, 5, 6, 9, 10, 11),
             'Mercury': (1, 3, 4, 5, 7, 8, 10, 11), 'Jupiter': (1, 4, 7, 8, 10, 11, 12),
             'Venus': (3, 4, 5, 7, 9, 10, 11), 'Saturn': (3, 5, 6, 11), 'Lagna': (3, 6, 10, 11)},
    'Mars': {'Sun': (3, 5, 6, 10, 11), 'Moon': (3, 6, 11), 'Mars': (1, 2, 4, 7, 8, 10, 11),
             'Mercury': (3, 5, 6, 11), 'Jupiter': (6, 10, 11, 12), 'Venus': (6, 8, 11, 12),
             'Saturn': (1, 4, 7, 8, 9, 10, 11), 'Lagna': (1, 3, 6, 10, 11)},
    'Mercury': {'Sun': (5, 6, 9, 11, 12), 'Moon': (2, 4, 6, 8, 10, 11), 'Mars': (1, 2, 4, 7, 8, 9, 10, 11),
                'Mercury': (1, 3, 5, 6, 9, 10, 11, 12), 'Jupiter': (6, 8, 11, 12),
                'Venus': (1, 2, 3, 4, 5, 8, 9, 11), 'Saturn': (1, 2, 4, 7, 8, 9, 10, 11),
                'Lagna': (1, 2, 4, 6, 8, 10, 11)},
    'Jupiter': {'Sun': (1, 2, 3, 4, 7, 8, 9, 10, 11), 'Moon': (2, 5, 7, 9, 11),
                'Mars': (1, 2, 4, 7, 8, 10, 11), 'Mercury': (1, 2, 4, 5, 6, 9, 10, 11),
                'Jupiter': (1, 2, 3, 4, 7, 8, 10, 11), 'Venus': (2, 5, 6, 9, 10, 11),
                'Saturn': (3, 5, 6, 12), 'Lagna': (1, 2, 4, 5, 6, 7, 9, 10, 11)},
    'Venus': {'Sun': (8, 11, 12), 'Moon': (1, 2, 3, 4, 5, 8, 9, 11, 12), 'Mars': (3, 5, 6, 9, 11, 12),
              'Mercury': (3, 5, 6, 9, 11), 'Jupiter': (5, 8, 9, 10, 11),
              'Venus': (1, 2, 3, 4, 5, 8, 9, 10, 11), 'Saturn': (3, 4, 5, 8, 9, 10, 11),
              'Lagna': (1, 2, 3, 4, 5, 8, 9, 11)},
    'Saturn': {'Sun': (1, 2, 4, 7, 8, 10, 11), 'Moon': (3, 6, 11), 'Mars': (3, 5, 6, 10, 11, 12),
               'Mercury': (6, 8, 9, 10, 11, 12), 'Jupiter': (5, 6, 11, 12), 'Venus': (6, 11, 12),
               'Saturn': (3, 5, 6, 11), 'Lagna': (1, 3, 4, 6, 10, 11)},
}
BAV_TOTALS = {'Sun': 48, 'Moon': 49, 'Mars': 39, 'Mercury': 54, 'Jupiter': 56, 'Venus': 52, 'Saturn': 39}
SAV_TOTAL = 337

KENDRA = (1, 4, 7, 10)
TRIKONA = (1, 5, 9)
DUSTHANA = (6, 8, 12)
UPACHAYA = (3, 6, 10, 11)
MAHAPURUSHA = (('Ruchaka', 'Mars'), ('Bhadra', 'Mercury'), ('Hamsa', 'Jupiter'),
               ('Malavya', 'Venus'), ('Sasa', 'Saturn'))
STAR_PLANETS = ('Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')     # the five tara grahas
NATURAL_BENEFICS = ('Mercury', 'Jupiter', 'Venus')

# Transit results counted from the natal Moon (classical gochara)
TRANSIT_GOOD_FROM_MOON = {'Saturn': (3, 6, 11), 'Jupiter': (2, 5, 7, 9, 11),
                          'Rahu': (3, 6, 11), 'Ketu': (3, 6, 11)}
SATURN_FROM_MOON = {12: 'sade sati - 1st phase', 1: 'sade sati - 2nd phase', 2: 'sade sati - 3rd phase',
                    8: 'ashtama', 4: 'ardhashtama', 7: 'kantaka', 10: 'kantaka'}

# Largest daily motion in degrees, with a margin: how far a body can get in a day.
_VMAX = {'Saturn': 0.16, 'Jupiter': 0.28, 'mean': 0.07, 'true': 0.45}
TRANSIT_MIN_STEP = 1.0          # days
TRANSIT_TOL = 0.5 / 86400.0     # days: entries are bisected to half a second
TRANSIT_YEARS_AHEAD = 10
PRATYANTAR_YEARS_BACK = 1
PRATYANTAR_YEARS_AHEAD = 5
LAGNA_STEP = 10                 # seconds between lagna samples
LAGNA_LIMIT = 6 * 3600          # seconds searched each way
LAGNA_UNCERTAIN = 120           # seconds

# topic, D1 houses, significators, divisional charts, KP houses
TOPICS = [
    ('Job and career', (10, 6, 2, 11), ('Sun', 'Saturn', 'Mercury'), ('D10',), (2, 6, 10, 11)),
    ('Business', (7, 10, 11, 2), ('Mercury',), ('D10',), (2, 7, 10, 11)),
    ('Marriage', (7, 2, 11), ('Venus',), ('D9',), (2, 7, 11)),
    ('Children', (5, 9, 2), ('Jupiter',), ('D7',), (2, 5, 11)),
    ('Abroad / onsite', (12, 9, 7, 3), ('Rahu', 'Moon'), ('D9', 'D10'), (3, 9, 12)),
    ('Education', (4, 5, 2, 9), ('Mercury', 'Jupiter'), ('D24',), (4, 9, 11)),
    ('Home and vehicle', (4,), ('Mars', 'Moon', 'Venus'), ('D4', 'D16'), (4, 11, 12)),
    ('Money', (2, 11, 5, 9), ('Jupiter',), ('D2',), (2, 6, 11)),
    ('Strain (general)', (6, 8, 12), ('Saturn',), ('D30',), (6, 8, 12)),
    ('Parents', (4, 9), ('Moon', 'Sun'), ('D12',), ()),
    ('Siblings', (3, 11), ('Mars',), ('D3',), ()),
    ('Spiritual life', (9, 12, 5), ('Jupiter', 'Ketu'), ('D20',), ()),
]
MARRIAGE_EXTRA_FOR_WOMAN = 'Jupiter'

RULES = [
    ('Houses and lordship', 'Whole sign from the lagna. Sign lords: Mesha and Vrischika Mars, Rishabha and Thula '
     'Venus, Mithuna and Kanya Mercury, Kataka Moon, Simha Sun, Dhanu and Meena Jupiter, Makara and Kumbha '
     'Saturn. Rahu and Ketu own no sign.'),
    ('Functional nature', 'Simple BPHS rule, applied in this order: (1) owns a kendra (4, 7, 10) and a trikona '
     '(5, 9): Yogakaraka; (2) owns a trikona (1, 5, 9): Benefic; (3) owns 3, 6 or 11, or owns 8 (the Sun and '
     'the Moon are exempt from the 8th lord rule): Malefic; (4) otherwise (only 2, 12 or kendras): Neutral. '
     'The houses owned are given beside the label so another scheme can be applied.'),
    ('Badhaka', '11th house for a movable lagna, 9th for a fixed lagna, 7th for a dual lagna.'),
    ('Aspects', 'Graha drishti, full aspects only, by whole sign: every planet aspects the 7th sign from itself; '
     'Mars also the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th. Rahu and Ketu: the 7th '
     'only (the 5th and 9th aspects of the nodes are a variant that is not used). Rasi (Jaimini) aspects '
     'are not used.'),
    ('Conjunction', 'Two planets in the same sign. The separation in degrees is given for every pair.'),
    ('Combustion', 'Orbs from the Sun: Moon 12°, Mars 17°, Mercury 14° (12° retrograde), Jupiter 11°, Venus 10° '
     '(8° retrograde), Saturn 15°. The distance from the Sun is given.'),
    ('Planetary war', 'Two of Mars, Mercury, Jupiter, Venus and Saturn within 1° of longitude. The pair is '
     'flagged; no winner is named because the rules for the winner differ between authors.'),
    ('Exaltation and debilitation', 'Exaltation signs: Sun Mesha, Moon Rishabha, Mars Makara, Mercury Kanya, '
     'Jupiter Kataka, Venus Meena, Saturn Thula; debilitation is the opposite sign. Deep exaltation: Sun 10°, '
     'Moon 3°, Mars 28°, Mercury 15°, Jupiter 5°, Venus 27°, Saturn 20°.'),
    ('Moolatrikona', 'Rasi chart (D1) only, because it needs degrees: Sun Simha 0-20°; Moon Rishabha 3-30° '
     '(0-3° is exaltation); Mars Mesha 0-12°; Mercury Kanya 15-20° (0-15° exaltation, 20-30° own sign); '
     'Jupiter Dhanu 0-10°; Venus Thula 0-15°; Saturn Kumbha 0-20°. The Vedic sheet of the workbook marks '
     'exaltation and own sign by sign alone, so it can say Exalted or Own sign where the AI sheets say '
     'Moolatrikona.'),
    ('Friendship', 'Natural friendship as in BPHS. Temporary friendship from the Rasi chart: planets in the 2nd, '
     '3rd, 4th, 10th, 11th and 12th sign from a planet are its friends, the rest its enemies. Compound: '
     'friend + friend = great friend; friend + neutral = friend; friend + enemy = neutral; neutral + enemy '
     '= enemy; enemy + enemy = great enemy. The same compound relationship (from the Rasi chart) is used '
     'in every divisional chart.'),
    ('Dignity label', 'In every chart: Exalted, Moolatrikona (D1 only), Own sign, or the compound relationship '
     'with the lord of the sign occupied (Great friend, Friend, Neutral, Enemy, Great enemy). Debilitation '
     'is a separate yes / no flag, and a debilitated planet carries the relationship label of its sign '
     'lord. Rahu, Ketu, the lagna and Mandi get no dignity.'),
    ('Vimsopaka strength', 'Out of 20. Points: Exalted, Moolatrikona or Own sign 20; Great friend 18; Friend 15; '
     'Neutral 10; Enemy 7; Great enemy 5; a debilitated planet is scored by its relationship with the sign '
     'lord. Weights - Shodasavarga: D1 3.5, D2 1, D3 1, D4 0.5, D7 0.5, D9 3, D10 0.5, D12 0.5, D16 2, '
     'D20 0.5, D24 0.5, D27 0.5, D30 1, D40 0.5, D45 0.5, D60 4. Dasavarga: D1 3, D60 5, and 1.5 each for '
     'D2, D3, D7, D9, D10, D12, D16, D30. Saptavarga: D1 5, D2 2, D3 3, D7 2.5, D9 4.5, D12 2, D30 1. '
     'Shadvarga: D1 6, D2 2, D3 4, D9 5, D12 2, D30 1. Figure = sum of weight x points / 20.'),
    ('Degree in a divisional chart', '(Offset of the point inside its part / size of the part) x 30. The same '
     'formula is used for the unequal parts of Trimsamsa (D30). House = whole sign from that chart\'s lagna.'),
    ('Lagna sensitivity', 'For each divisional chart, the number of seconds the birth could be earlier or later '
     'with that chart\'s lagna staying in the same sign, found by recomputing the real lagna every 10 seconds '
     'and refining to the second (no average rate). Searched for 6 hours each way; an empty cell means no '
     'change in that time. lagna_uncertain = yes when either margin is under 120 seconds.'),
    ('Ashtakavarga', 'Parashara\'s benefic places with eight donors (the seven planets and the lagna). '
     'Bhinnashtakavarga totals are always Sun 48, Moon 49, Mars 39, Mercury 54, Jupiter 56, Venus 52, '
     'Saturn 39; Sarvashtakavarga is their sum, 337, and so includes the bindus given by the lagna. '
     'No reductions (trikona or ekadhipatya sodhana) are applied. Sources differ on four lists; this file '
     'follows BPHS chapter 66 as usually printed - Moon\'s chart: from the Moon 1, 3, 6, 7, 10, 11; from Mars '
     '2, 3, 5, 6, 9, 10, 11; from Jupiter 1, 4, 7, 8, 10, 11, 12; Venus\'s chart: from Mars 3, 5, 6, 9, 11, 12. '
     'The other version seen (PyJHora library) has Moon 1, 3, 6, 7, 9, 10, 11; Mars 2, 3, 5, 6, 10, 11; Jupiter '
     '1, 2, 4, 7, 8, 10, 11; and for Venus\'s chart Mars 3, 4, 6, 9, 11, 12. The totals are the same in both.'),
    ('Pancha Mahapurusha yoga', 'Mars (Ruchaka), Mercury (Bhadra), Jupiter (Hamsa), Venus (Malavya) or Saturn '
     '(Sasa) in its own or exaltation sign and in a kendra from the lagna. The same test counted from the '
     'Moon is reported on a separate row as a variant.'),
    ('Gajakesari, Budha-Aditya, Chandra-Mangala, Guru-Chandala', 'Gajakesari: Jupiter in a kendra (1, 4, 7, 10) '
     'from the Moon. Budha-Aditya: Sun and Mercury in one sign. Chandra-Mangala: Moon and Mars in one sign. '
     'Guru-Chandala: Jupiter in one sign with Rahu or Ketu.'),
    ('Neecha bhanga', 'For a planet debilitated in the Rasi chart, one row for each condition met: (a) the lord '
     'of the debilitation sign is in a kendra from the lagna or the Moon; (b) the planet that is exalted in '
     'that sign is in a kendra from the lagna or the Moon; (c) the debilitated planet is exalted in D9. '
     'No planet is exalted in Vrischika, so (b) cannot apply to a debilitated Moon.'),
    ('Raja yoga and Dhana yoga', 'Raja yoga: a lord of a kendra (1, 4, 7, 10) and a lord of a trikona (1, 5, 9), '
     'two different planets, joined by conjunction (same sign), mutual aspect or exchange of signs. Dhana '
     'yoga: the same three links between two different lords of houses 1, 2, 5, 9 and 11. One row per pair. '
     'A single planet that owns both a kendra and a trikona is shown as Yogakaraka under functional nature.'),
    ('Viparita raja yoga', 'The lord of the 6th (Harsha), the 8th (Sarala) or the 12th (Vimala) placed in the '
     '6th, 8th or 12th house. A stricter variant, not used here, wants each lord in its own house.'),
    ('Parivartana', 'Exchange of signs: each of two planets sits in a sign owned by the other.'),
    ('Yogas from the Moon', 'Counting only Mars, Mercury, Jupiter, Venus and Saturn (the Sun, Rahu and Ketu are '
     'ignored). Sunapha: a planet in the 2nd from the Moon and none in the 12th. Anapha: in the 12th and '
     'none in the 2nd. Durudhara: in both. Kemadruma: none in the 2nd or 12th and none with the Moon; it is '
     'cancelled when one of those five planets is in a kendra from the lagna or from the Moon. Status '
     '"cancelled" means formed and cancelled.'),
    ('Yogas from the Sun', 'Counting only Mars, Mercury, Jupiter, Venus and Saturn (the Moon, Rahu and Ketu are '
     'ignored). Vesi: a planet in the 2nd from the Sun and none in the 12th. Vasi: in the 12th and none in '
     'the 2nd. Ubhayachari: in both.'),
    ('Adhi yoga and Amala', 'Adhi yoga: Mercury, Jupiter and Venus in the 6th, 7th or 8th from the Moon; found '
     'when at least one is there, and the note says how many of the three (all three is the complete yoga). '
     'Amala: Mercury, Jupiter or Venus in the 10th from the lagna or from the Moon (the Moon itself is not '
     'counted as a benefic here).'),
    ('Kuja dosha', 'Mars in the 1st, 2nd, 4th, 7th, 8th or 12th, counted from the lagna, from the Moon and from '
     'Venus, as three separate rows. No exceptions, severity or remedies are applied.'),
    ('Kala Sarpa', 'Popular, not in BPHS: all seven planets on one side of the Rahu-Ketu axis, judged by '
     'longitude. Software that judges by sign also counts planets that share a sign with a node but lie '
     'beyond it, and so reports this yoga more often.'),
    ('Dasa levels', 'Vimshottari from the Moon with the chosen Vedic ayanamsha, year of 365.25 days. The bhukti '
     'table has one row per bhukti. Pratyantar (4th level): inside an antaram the order starts with the '
     'antaram lord and each part = antaram length x lord\'s years / 120; listed from 1 year before the '
     'report date to 5 years after.'),
    ('Transits', 'Saturn, Jupiter, Rahu and Ketu with the chart\'s ayanamsha and node setting; Ketu is opposite '
     'Rahu. Sign entries from birth to 10 years after the report date, every retrograde re-entry included, '
     'found by stepping through time (never more than the body can travel towards a sign boundary, at most '
     'one day near a boundary) and bisecting; each moment is cut down to the minute it falls in.'),
    ('Transit results from the Moon', 'Classical gochara counted from the natal Moon sign: Saturn favourable in '
     '3, 6, 11; Jupiter in 2, 5, 7, 9, 11; Rahu and Ketu in 3, 6, 11; other places unfavourable. Vedha '
     '(obstruction) points are not applied. Saturn from the Moon: 12th, 1st and 2nd = sade sati phases 1, 2 '
     'and 3; 8th = ashtama; 4th = ardhashtama; 7th or 10th = kantaka.'),
    ('Double transit', 'Modern method, not classical: a house is marked while both Jupiter and Saturn occupy it '
     'or aspect it (Jupiter 5th, 7th, 9th; Saturn 3rd, 7th, 10th) by transit. Every span that touches the '
     '10 years after the report date is listed with its real start and end.'),
    ('Topic map and scores', 'A fixed table of houses, significators, divisional chart and KP houses for each '
     'common question. Score per bhukti and topic = "rule-based relevance, not a prediction". For the '
     'bhukti lord add 1 for each: (a) owns a key house; (b) sits in a key house; (c) aspects a key house; '
     '(d) is a significator; (e) is in a kendra, trikona or the 11th, or in its own or exaltation sign, in '
     'a topic chart; (f) signifies one of the topic\'s KP houses on the KP sheet. Add half of the dasa '
     'lord\'s count of (a) to (f). Subtract 1 if the bhukti lord has Shodasavarga Vimsopaka under 10, or is '
     'combust, or is debilitated in D1 with no neecha bhanga condition met. For marriage Jupiter is a '
     'significator only when the gender is female.'),
]

NOT_IN_FILE = [
    'Shadbala and Bhava bala', 'Planet latitude, declination and retrograde station dates',
    'Chara karakas, Karakamsa and arudha padas', 'Special lagnas (Bhava, Hora, Ghati, Indu)',
    'Gulika and the other upagrahas (Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu)',
    'Avasthas, Tara bala, Pushkara and gandanta flags', 'Yogini dasa and any dasa other than Vimshottari',
    'Sookshma dasa (5th level) and deeper', 'Ashtakavarga reductions (sodhana) and kakshya transits',
    'Transits of the Sun, Moon, Mars, Mercury and Venus through the signs (only their positions on the '
    'report date are given)', 'Rasi (Jaimini) aspects and 5th / 9th aspects of Rahu and Ketu',
    'The winner of a planetary war', 'Remedies, gem or ritual advice',
    'Length of life: left out on purpose; this file gives no figure and no analysis of it',
    'Predictions: every table states facts or rule-based labels, not outcomes',
]

# ── SMALL HELPERS ─────────────────────────────────────────────────────────────


def _yes(flag):
    return 'yes' if flag else 'no'


def _join(items):
    """List -> 'a, b'; an empty list -> 'none' (so it cannot be mistaken for a missing value)."""
    items = list(items)
    return ', '.join(str(i) for i in items) if items else 'none'


def _r6(x):
    return None if x is None else round(float(x), 6)


def _sec(dt):
    """Round a datetime to the whole second."""
    if dt is None:
        return None
    return (dt + timedelta(microseconds=500000)).replace(microsecond=0)


def _minute(dt):
    """Cut a datetime down to the minute it falls in."""
    return dt.replace(second=0, microsecond=0)


def fmt_deg(deg):
    """Degrees inside a sign as text, rounded to the second but never reaching 30°."""
    total = min(int(round(deg * 3600)), 30 * 3600 - 1)
    d, rem = divmod(max(total, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{d:02d}°{m:02d}'{s:02d}\""


def house_from(sign, ref_sign):
    """Place of a sign counted from a reference sign (1 = the same sign)."""
    return (sign - ref_sign) % 12 + 1


def aspected_signs(planet, sign):
    return {(sign + k - 1) % 12 for k in ASPECTS[planet]}


def natural_relation(a, b):
    """How planet a regards planet b: Friend, Neutral or Enemy."""
    friends, neutrals, _ = NATURAL[a]
    return 'Friend' if b in friends else ('Neutral' if b in neutrals else 'Enemy')


def temporary_relation(sign_a, sign_b):
    return 'Friend' if house_from(sign_b, sign_a) in TEMP_FRIEND_PLACES else 'Enemy'


def compound_relation(a, b, sign_a, sign_b):
    return COMPOUND[(natural_relation(a, b), temporary_relation(sign_a, sign_b))]


def varga_degree(lon, key):
    """
    Degree (0 <= d < 30) of a longitude inside its divisional chart sign:
    the offset inside its part, stretched to 30 degrees.
    """
    lon = norm(lon)
    if key == 'D30':
        sign = A.get_rasi(lon)
        deg = lon - 30.0 * sign
        table = A._TRIMSAMSA_ODD if sign % 2 == 0 else A._TRIMSAMSA_EVEN
        part = varga_part(lon, key)
        low = table[part - 1][0] if part else 0
        d = (deg - low) / (table[part][0] - low) * 30.0
    else:
        # same arithmetic as varga_part (multiply first), so a point exactly on
        # an edge is at 0 degrees of the next part
        d = (lon * A._VARGA_DIV[key]) % 30.0
    return min(max(d, 0.0), 30.0 - 1e-9)


def dignity_in(planet, sign, key, deg, compound):
    """
    (label, debilitated) of one of the seven planets in one chart.
    deg is the degree in the Rasi sign and is used for D1 only.
    """
    debilitated = sign == (EXALT_SIGN[planet] + 6) % 12
    if key == 'D1':
        mt_sign, lo, hi = MOOLATRIKONA[planet]
        if sign == mt_sign and lo <= deg < hi:
            return 'Moolatrikona', False
        if sign == EXALT_SIGN[planet] and deg >= EXALT_PART_D1.get(planet, 30):
            return 'Own sign', False               # Mercury in Kanya from 20 degrees
    if sign == EXALT_SIGN[planet]:
        return 'Exalted', False
    if sign in OWN_SIGNS[planet]:
        return 'Own sign', False
    return compound[planet][SIGN_LORDS[sign]], debilitated


def functional_nature(owned):
    owned = set(owned)
    if owned & {4, 7, 10} and owned & {5, 9}:
        return 'Yogakaraka'
    if owned & {1, 5, 9}:
        return 'Benefic'
    return None


# ── CONTEXT: everything derived once ──────────────────────────────────────────

class Ctx:
    """Derived facts about one chart, shared by the table builders."""

    def __init__(self, res, now=None):
        m, v = res['meta'], res['vedic']
        self.res, self.meta, self.v, self.kp = res, m, v, res['kp']
        self.now = now or m['generated_at']
        self.birth = m['local_dt']
        self.offset = (m['local_dt'] - m['ut_dt']).total_seconds() / 3600.0
        self.lat, self.lon = m['lat'], m['lon']
        self.sid_mode = A.AYANAMSHAS[m['ayanamsha_key']][1]
        self.node = m['node']
        self.gender = (m.get('gender') or '').strip().lower()
        self.female = self.gender in ('female', 'f', 'woman', 'girl')

        self.mandi = v.get('mandi')
        self.points = {p['name']: p for p in v['planets']}
        if self.mandi:
            self.points['Mandi'] = self.mandi
        self.names = ['Lagna'] + PLANETS + ['Mandi']
        self.sign = {n: p['sign'] for n, p in self.points.items()}
        self.lagna_sign = v['lagna_sign']
        self.moon_sign = self.sign['Moon']
        self.sun_sign = self.sign['Sun']
        self.house = {n: house_from(s, self.lagna_sign) for n, s in self.sign.items()}

        self.house_sign = {h: (self.lagna_sign + h - 1) % 12 for h in range(1, 13)}
        self.house_lord = {h: SIGN_LORDS[s] for h, s in self.house_sign.items()}
        self.owned = {p: [h for h in range(1, 13) if self.house_lord[h] == p] for p in PLANETS}

        self.asp_signs = {p: aspected_signs(p, self.sign[p]) for p in PLANETS}
        self.asp_houses = {p: sorted(house_from(s, self.lagna_sign) for s in self.asp_signs[p]) for p in PLANETS}
        self.aspecting = {s: [p for p in PLANETS if s in self.asp_signs[p]] for s in range(12)}
        self.in_sign = {s: [p for p in PLANETS if self.sign[p] == s] for s in range(12)}

        self.compound = {a: {b: compound_relation(a, b, self.sign[a], self.sign[b])
                             for b in SEVEN if b != a} for a in SEVEN}

        self.vargas = {vg['key']: vg for vg in v['vargas']}
        self.dignity = {}                # key -> planet -> (label, debilitated)
        for key in VARGA_KEYS:
            signs = self.vargas[key]['signs']
            self.dignity[key] = {p: dignity_in(p, signs[p], key, self.points[p]['deg'], self.compound)
                                 for p in SEVEN}
        self.points_grid = {p: {k: VIMSOPAKA_POINTS[self.dignity[k][p][0]] for k in VARGA_KEYS} for p in SEVEN}
        self.vimsopaka = {p: {scheme: round(sum(w * self.points_grid[p][k] for k, w in weights.items()) / 20.0, 3)
                              for scheme, weights in VIMSOPAKA_WEIGHTS.items()} for p in SEVEN}

        self.bav, self.sav = ashtakavarga(self.sign)
        self.kp_house = {p['name']: p['house'] for p in self.kp['planets']}
        self.kp_signifies = {s['planet']: set(s['all']) for s in self.kp['planet_significators']}

        self.nature = {}
        for p in SEVEN:
            owned = set(self.owned[p])
            label = functional_nature(owned)
            if label is None:
                eighth = 8 in owned and p not in ('Sun', 'Moon')
                label = 'Malefic' if (owned & {3, 6, 11} or eighth) else 'Neutral'
            self.nature[p] = label

        quality = self.lagna_sign % 3          # 0 movable, 1 fixed, 2 dual
        self.badhaka_house = (11, 9, 7)[quality]

    # -- shared tests --------------------------------------------------------
    def combust(self, p):
        return bool(self.points[p].get('combust')) if p in COMBUST_ORB else False

    def debilitated(self, p):
        return p in SEVEN and self.dignity['D1'][p][1]

    def mutual_aspect(self, a, b):
        return self.sign[b] in self.asp_signs[a] and self.sign[a] in self.asp_signs[b]

    def exchange(self, a, b):
        return (a in SEVEN and b in SEVEN and a != b
                and SIGN_LORDS[self.sign[a]] == b and SIGN_LORDS[self.sign[b]] == a)

    def links(self, a, b):
        out = []
        if self.sign[a] == self.sign[b]:
            out.append('conjunction')
        if self.mutual_aspect(a, b):
            out.append('mutual aspect')
        if self.exchange(a, b):
            out.append('exchange of signs')
        return out


def ashtakavarga(sign):
    """
    Bhinnashtakavarga of the seven planets and the Sarvashtakavarga.
    sign: {name: sign index} for the seven planets and 'Lagna'.
    Returns (bav, sav): bav[planet] is a list of 12 bindu counts by sign.
    """
    bav = {}
    for planet, donors in BAV_PLACES.items():
        row = [0] * 12
        for donor, places in donors.items():
            for place in places:
                row[(sign[donor] + place - 1) % 12] += 1
        bav[planet] = row
    sav = [sum(bav[p][s] for p in SEVEN) for s in range(12)]
    return bav, sav


# ── TABLES: natal ─────────────────────────────────────────────────────────────

def _facts(c):
    m, v, pc = c.meta, c.v, c.v['panchangam']
    lagna, moon = c.points['Lagna'], c.points['Moon']
    bal = v['dasa']['balance']
    off = c.offset
    now_utc = c.now - timedelta(hours=off)
    age = (c.now - c.birth).total_seconds() / 86400.0 / YEAR_DAYS
    frame = None
    if pc.get('sunrise') and pc.get('sunset'):
        frame = 'day' if pc['sunrise'] <= c.birth < pc['sunset'] else 'night'
    rows = [
        ('name', m['name'], ''),
        ('gender', m.get('gender') or None, 'as entered; empty when not given'),
        ('birth_date', c.birth.date(), 'civil date at the birth place'),
        ('birth_time', c.birth.strftime('%H:%M:%S'), 'clock time at the birth place, 24-hour, as text'),
        ('birth_datetime_local', _sec(c.birth), 'clock time at the birth place'),
        ('birth_place', m['pob'], ''),
        ('latitude_deg', m['lat'], 'north positive'),
        ('longitude_deg', m['lon'], 'east positive'),
        ('time_zone', m['tz'], ''),
        ('utc_offset_hours', round(off, 6), 'offset in force at birth; used for every *_local moment in the AI sheets'),
        ('utc_offset_text', m['utc_offset_str'], ''),
        ('birth_datetime_utc', _sec(m['ut_dt']), 'UT moment of birth'),
        ('julian_day_ut', m['jd_ut'], ''),
        ('ayanamsha_name', m['ayanamsha_name'], 'used for every AI sheet except the columns labelled KP'),
        ('ayanamsha_deg', _r6(v['ayanamsha']), 'at birth'),
        ('ayanamsha_text', v['ayanamsha_dms'], ''),
        ('kp_ayanamsha_deg', _r6(c.kp['ayanamsha']), 'Krishnamurti; used only by the KP sheet and the kp_ columns'),
        ('node_type', 'true node' if m['node'] == 'true' else 'mean node', 'Rahu; Ketu is exactly opposite'),
        ('default_house_system', 'whole sign from the lagna', 'use this unless a question names Sripati bhava or KP'),
        ('default_dasa_table', 'AI_Dasa (Vimshottari, Vedic ayanamsha)', 'the KP sheet has its own dasa dates; do not mix them'),
        ('lagna_sign_no', lagna['sign'] + 1, '1 = Mesha ... 12 = Meena'),
        ('lagna_sign', RASIS[lagna['sign']], ''),
        ('lagna_deg_in_sign', _r6(lagna['deg']), ''),
        ('lagna_lord', SIGN_LORDS[lagna['sign']], ''),
        ('moon_sign_no', moon['sign'] + 1, ''),
        ('moon_sign', RASIS[moon['sign']], 'janma rasi'),
        ('moon_nakshatra_no', moon['nak'] + 1, '1 = Ashwini ... 27 = Revati'),
        ('moon_nakshatra', NAKS[moon['nak']], 'janma nakshatra'),
        ('moon_pada', moon['pada'], ''),
        ('moon_nakshatra_lord', v['dasa']['birth_star_lord'], ''),
        ('sun_sign', RASIS[c.sun_sign], 'sidereal'),
        ('paksha', pc['paksha'], 'Shukla = waxing, Krishna = waning'),
        ('tithi_no', pc['tithi_num'], '1-30, counted from the new moon'),
        ('tithi', pc['tithi'], ''),
        ('nitya_yoga', pc['yoga'], 'the panchangam yoga (Sun + Moon); not a planetary yoga'),
        ('karana', pc['karana'], ''),
        ('weekday', pc['vara'], 'Vedic weekday, sunrise to sunrise'),
        ('weekday_lord', pc['vara_lord'], ''),
        ('sunrise_local', _sec(pc['sunrise']), 'on the civil date of birth; visible upper limb'),
        ('sunset_local', _sec(pc['sunset']), 'on the civil date of birth'),
        ('birth_by_day_or_night', frame, 'day = between that sunrise and sunset'),
        ('dasa_balance_lord', bal['lord'], 'Vimshottari dasa running at birth'),
        ('dasa_balance_years', bal['years'], 'years of that dasa left at birth'),
        ('dasa_balance_text', f"{bal['y']} y {bal['m']} m {bal['d']} d", 'on a 360-day basis, as printed on the Vedic sheet'),
        ('dasa_year_days', m['year_days'], 'length of a dasa year'),
        ('badhaka_house', c.badhaka_house, 'house of obstruction for this lagna'),
        ('badhaka_sign', RASIS[c.house_sign[c.badhaka_house]], ''),
        ('badhaka_lord', c.house_lord[c.badhaka_house], ''),
        ('report_datetime_local', _sec(c.now), 'when this file was generated; "now" for transits and periods'),
        ('report_datetime_utc', _sec(now_utc), ''),
        ('age_at_report_years', round(age, 3), 'in years of 365.25 days'),
        ('engine', m['engine'], ''),
        ('ai_schema', SCHEMA, 'version of the AI sheets'),
    ]
    return [{'key': k, 'value': val, 'note': note or None} for k, val, note in rows]


def _planets(c):
    d9 = c.vargas['D9']['signs']
    rows = []
    for n in c.names:
        p = c.points.get(n)
        if p is None:                              # Mandi where the Sun does not rise or set
            row = {'point': n}
            rows.append(row)
            continue
        s = p['sign']
        seven, planet = n in SEVEN, n in PLANETS
        orb = None
        if n in COMBUST_ORB:
            orb = COMBUST_ORB[n][1 if p['speed'] < 0 else 0]
        label, debil = c.dignity['D1'][n] if seven else (None, None)
        row = {
            'point': n,
            'longitude_deg': _r6(p['lon']),
            'sign_no': s + 1,
            'sign': RASIS[s],
            'deg_in_sign': _r6(p['deg']),
            'deg_in_sign_text': p['dms'],
            'nakshatra_no': p['nak'] + 1,
            'nakshatra': NAKS[p['nak']],
            'pada': p['pada'],
            'sign_lord': p['sign_lord'],
            'star_lord': p['star_lord'],
            'house_whole_sign': c.house[n],
            'bhava_sripati': p['bhava'],
            'kp_house_placidus': 1 if n == 'Lagna' else c.kp_house.get(n),
            'house_from_moon': house_from(s, c.moon_sign),
            'house_from_sun': house_from(s, c.sun_sign),
            'retrograde': _yes(p['retro']) if seven else None,
            'speed_deg_per_day': _r6(p['speed']) if planet else None,
            'combust': _yes(p['combust']) if n in COMBUST_ORB else None,
            'distance_from_sun_deg': None if n == 'Sun' else _r6(angle_diff(p['lon'], c.points['Sun']['lon'])),
            'combust_orb_deg': orb,
            'dignity': label,
            'moolatrikona': _yes(label == 'Moolatrikona') if seven else None,
            'debilitated': _yes(debil) if seven else None,
            'debilitation_cancelled_by': _join(c.neecha_bhanga.get(n, [])) if debil else None,
            'distance_from_deep_exaltation_deg': (
                _r6(angle_diff(p['lon'], EXALT_SIGN[n] * 30 + DEEP_EXALT_DEG[n])) if seven else None),
            'houses_owned': _join(c.owned[n]) if planet else None,
            'functional_nature': c.nature.get(n),
            'houses_aspected': _join(c.asp_houses[n]) if planet else None,
            'planets_aspected': _join(q for q in PLANETS if q != n and c.sign[q] in c.asp_signs[n]) if planet else None,
            'aspected_by': _join(q for q in c.aspecting[s] if q != n),
            'conjunct_with': _join(q for q in c.in_sign[s] if q != n),
            'd9_sign': RASIS[d9[n]],
            'vargottama': _yes(d9[n] == s),
            'vimsopaka_shodasavarga': c.vimsopaka[n]['shodasavarga'] if seven else None,
            'vimsopaka_dasavarga': c.vimsopaka[n]['dasavarga'] if seven else None,
            'vimsopaka_saptavarga': c.vimsopaka[n]['saptavarga'] if seven else None,
            'vimsopaka_shadvarga': c.vimsopaka[n]['shadvarga'] if seven else None,
            'own_bav_bindus_in_sign_occupied': c.bav[n][s] if seven else None,
            'sav_bindus_in_sign_occupied': c.sav[s],
        }
        rows.append(row)
    return rows


def _house_groups(h):
    groups = [name for name, hs in (('kendra', KENDRA), ('trikona', TRIKONA), ('dusthana', DUSTHANA),
                                    ('upachaya', UPACHAYA)) if h in hs]
    return _join(groups)


def _houses(c):
    cusps = {x['house']: x for x in c.kp['cusps']}
    all_points = PLANETS + (['Mandi'] if c.mandi else [])
    rows = []
    for h in range(1, 13):
        s = c.house_sign[h]
        lord = c.house_lord[h]
        cusp = cusps[h]
        rows.append({
            'house': h,
            'sign_no': s + 1,
            'sign': RASIS[s],
            'house_groups': _house_groups(h),
            'lord': lord,
            'lord_sign': RASIS[c.sign[lord]],
            'lord_house': c.house[lord],
            'lord_dignity': c.dignity['D1'][lord][0],
            'lord_debilitated': _yes(c.dignity['D1'][lord][1]),
            'occupants_whole_sign': _join(n for n in all_points if c.sign[n] == s),
            'occupants_bhava_sripati': _join(n for n in all_points if c.points[n]['bhava'] == h),
            'aspected_by': _join(c.aspecting[s]),
            'sav_bindus': c.sav[s],
            'house_from_moon': house_from(s, c.moon_sign),
            'kp_cusp_longitude_deg': _r6(cusp['lon']),
            'kp_cusp_sign': RASIS[cusp['sign']],
            'kp_cusp_star_lord': cusp['star_lord'],
            'kp_cusp_sub_lord': cusp['sub_lord'],
            'kp_occupants': _join(p for p in PLANETS if c.kp_house[p] == h),
        })
    return rows


def _pairs(c):
    rows = []
    for a, b in combinations(PLANETS, 2):
        pa, pb = c.points[a], c.points[b]
        both = a in SEVEN and b in SEVEN
        sep = angle_diff(pa['lon'], pb['lon'])
        war = a in STAR_PLANETS and b in STAR_PLANETS and sep <= 1.0
        rows.append({
            'planet_a': a,
            'planet_b': b,
            'same_sign': _yes(c.sign[a] == c.sign[b]),
            'separation_deg': _r6(sep),
            'b_counted_from_a': house_from(c.sign[b], c.sign[a]),
            'a_aspects_b': _yes(c.sign[b] in c.asp_signs[a]),
            'b_aspects_a': _yes(c.sign[a] in c.asp_signs[b]),
            'mutual_aspect': _yes(c.mutual_aspect(a, b)),
            'exchange_of_signs': _yes(c.exchange(a, b)),
            'natural_a_to_b': natural_relation(a, b) if both else None,
            'natural_b_to_a': natural_relation(b, a) if both else None,
            'temporary_a_to_b': temporary_relation(c.sign[a], c.sign[b]) if both else None,
            'temporary_b_to_a': temporary_relation(c.sign[b], c.sign[a]) if both else None,
            'compound_a_to_b': c.compound[a][b] if both else None,
            'compound_b_to_a': c.compound[b][a] if both else None,
            'planetary_war': _yes(war),
        })
    return rows


def _vargas(c):
    names = {v[0]: v[2] for v in VARGAS}
    rows = []
    for key in VARGA_KEYS:
        vg = c.vargas[key]
        for n in c.names:
            p = c.points.get(n)
            if p is None:
                rows.append({'chart': key, 'chart_name': names[key], 'point': n})
                continue
            s = vg['signs'][n]
            deg = varga_degree(p['lon'], key)
            label, debil = c.dignity[key][n] if n in SEVEN else (None, None)
            rows.append({
                'chart': key,
                'chart_name': names[key],
                'point': n,
                'sign_no': s + 1,
                'sign': RASIS[s],
                'deg_in_chart': _r6(deg),
                'deg_in_chart_text': fmt_deg(deg),
                'house': house_from(s, vg['lagna_sign']),
                'sign_lord': SIGN_LORDS[s],
                'dignity': label,
                'debilitated': _yes(debil) if n in SEVEN else None,
            })
    return rows


def lagna_margins(c):
    """
    For each divisional chart: (seconds earlier, lagna beyond, seconds later,
    lagna beyond). A margin is the largest whole number of seconds the birth
    can move that way with that chart's lagna still in the same sign; one
    second more and it is in the sign given. None when it does not change
    within LAGNA_LIMIT. The real lagna is recomputed; no average rate is used.
    """
    current = {k: c.vargas[k]['lagna_sign'] for k in VARGA_KEYS}
    cache = {}

    def lagna(offset_s):
        if offset_s not in cache:
            cache[offset_s] = A._lagna_at(c.birth + timedelta(seconds=offset_s), c.offset, c.lat, c.lon, c.sid_mode)
        return cache[offset_s]

    out = {k: {} for k in VARGA_KEYS}
    for direction in (-1, 1):
        pending = set(VARGA_KEYS)
        s = 0
        while pending and s < LAGNA_LIMIT:
            s2 = s + LAGNA_STEP
            lon = lagna(direction * s2)
            for k in [k for k in VARGA_KEYS if k in pending]:
                if varga_sign(lon, k) == current[k]:
                    continue
                lo, hi = s, s2                      # same sign at lo, another sign at hi
                while hi - lo > 1:
                    mid = (lo + hi) // 2
                    if varga_sign(lagna(direction * mid), k) == current[k]:
                        lo = mid
                    else:
                        hi = mid
                out[k][direction] = (hi - 1, varga_sign(lagna(direction * hi), k))
                pending.discard(k)
            s = s2
        for k in pending:
            out[k][direction] = (None, None)
    return out


def _varga_lagnas(c):
    names = {v[0]: v[2] for v in VARGAS}
    lagna_lon = c.points['Lagna']['lon']
    rows = []
    for key in VARGA_KEYS:
        vg = c.vargas[key]
        s = vg['lagna_sign']
        lord = SIGN_LORDS[s]
        lord_sign = vg['signs'][lord]
        (sec_e, sign_e), (sec_l, sign_l) = c.margins[key][-1], c.margins[key][1]
        small = [x for x in (sec_e, sec_l) if x is not None]
        deg = varga_degree(lagna_lon, key)
        rows.append({
            'chart': key,
            'chart_name': names[key],
            'lagna_sign_no': s + 1,
            'lagna_sign': RASIS[s],
            'lagna_deg_in_chart': _r6(deg),
            'lagna_lord': lord,
            'lagna_lord_sign': RASIS[lord_sign],
            'lagna_lord_house': house_from(lord_sign, s),
            'lagna_lord_dignity': c.dignity[key][lord][0],
            'lagna_lord_debilitated': _yes(c.dignity[key][lord][1]),
            'seconds_earlier': sec_e,
            'lagna_if_earlier': RASIS[sign_e] if sign_e is not None else None,
            'seconds_later': sec_l,
            'lagna_if_later': RASIS[sign_l] if sign_l is not None else None,
            'lagna_uncertain': _yes(bool(small) and min(small) < LAGNA_UNCERTAIN),
        })
    return rows


def _strength(c):
    rows = []
    for p in SEVEN:
        row = {'planet': p}
        for scheme in VIMSOPAKA_WEIGHTS:
            row[f'vimsopaka_{scheme}'] = c.vimsopaka[p][scheme]
        for k in VARGA_KEYS:
            row[f'points_{k}'] = c.points_grid[p][k]
        row['debilitated_in'] = _join(k for k in VARGA_KEYS if c.dignity[k][p][1])
        rows.append(row)
    return rows


def _ashtakavarga(c):
    rows = []
    for planet in SEVEN + ['Sarvashtakavarga']:
        data = c.sav if planet == 'Sarvashtakavarga' else c.bav[planet]
        for s in range(12):
            rows.append({'planet': planet, 'row_type': 'sign', 'sign_no': s + 1, 'sign': RASIS[s],
                         'house': house_from(s, c.lagna_sign), 'bindus': data[s]})
        rows.append({'planet': planet, 'row_type': 'total', 'sign_no': None, 'sign': 'Total',
                     'house': None, 'bindus': sum(data)})
    return rows


# ── YOGAS ─────────────────────────────────────────────────────────────────────

def _yogas(c):
    rows = []
    sign, house = c.sign, c.house
    moon = c.moon_sign

    def add(name, status, rule, planets=(), houses=(), note=''):
        rows.append({'yoga': name, 'status': status, 'rule': rule, 'planets': _join(planets),
                     'houses': _join(houses), 'note': note or None})

    def from_moon(p):
        return house_from(sign[p], moon)

    # Pancha Mahapurusha
    for name, p in MAHAPURUSHA:
        strong = sign[p] == EXALT_SIGN[p] or sign[p] in OWN_SIGNS[p]
        state = ('exalted' if sign[p] == EXALT_SIGN[p] else 'in its own sign') if strong else 'not in its own or exaltation sign'
        rule = f'{p} in its own or exaltation sign and in a kendra from the lagna'
        add(f'{name} yoga', 'found' if strong and house[p] in KENDRA else 'not found', rule, [p], [house[p]],
            f'{p} is {state}, in house {house[p]} from the lagna')
        add(f'{name} yoga - counted from the Moon (variant)',
            'found' if strong and from_moon(p) in KENDRA else 'not found',
            f'{p} in its own or exaltation sign and in a kendra from the Moon', [p], [house[p]],
            f'{p} is {state}, in place {from_moon(p)} from the Moon')

    add('Gajakesari yoga', 'found' if from_moon('Jupiter') in KENDRA else 'not found',
        'Jupiter in a kendra (1, 4, 7, 10) from the Moon', ['Jupiter', 'Moon'], [house['Jupiter'], house['Moon']],
        f"Jupiter is in place {from_moon('Jupiter')} from the Moon")
    for name, a, b in (('Budha-Aditya yoga', 'Sun', 'Mercury'), ('Chandra-Mangala yoga', 'Moon', 'Mars')):
        same = sign[a] == sign[b]
        add(name, 'found' if same else 'not found', f'{a} and {b} in one sign', [a, b], [house[a], house[b]],
            f'{a} in {RASIS[sign[a]]}, {b} in {RASIS[sign[b]]}')
    with_node = [n for n in NODES if sign[n] == sign['Jupiter']]
    add('Guru-Chandala yoga', 'found' if with_node else 'not found', 'Jupiter in one sign with Rahu or Ketu',
        ['Jupiter'] + with_node, [house['Jupiter']],
        f"Jupiter in {RASIS[sign['Jupiter']]}, Rahu in {RASIS[sign['Rahu']]}, Ketu in {RASIS[sign['Ketu']]}")

    # Neecha bhanga
    c.neecha_bhanga = {}
    debilitated = [p for p in SEVEN if c.debilitated(p)]
    if not debilitated:
        add('Neecha bhanga', 'not found', 'Cancellation of debilitation: conditions (a), (b), (c)',
            note='No planet is debilitated in the Rasi chart')
    exalted_in = {s: p for p, s in EXALT_SIGN.items()}

    def kendra_refs(p):
        refs = []
        if house[p] in KENDRA:
            refs.append(f'the lagna (house {house[p]})')
        if from_moon(p) in KENDRA:
            refs.append(f'the Moon (place {from_moon(p)})')
        return refs

    for p in debilitated:
        met = []
        s = sign[p]
        lord = SIGN_LORDS[s]
        refs = kendra_refs(lord)
        if refs:
            met.append('a')
            add(f'Neecha bhanga of {p} - condition (a)', 'found',
                'The lord of the debilitation sign is in a kendra from the lagna or the Moon', [p, lord],
                [house[p], house[lord]],
                f"The debilitation of {p} in {RASIS[s]} is cancelled: its lord {lord} is in a kendra from "
                f"{' and from '.join(refs)}")
        ex = exalted_in.get(s)
        if ex:
            refs = kendra_refs(ex)
            if refs:
                met.append('b')
                add(f'Neecha bhanga of {p} - condition (b)', 'found',
                    'The planet that is exalted in the debilitation sign is in a kendra from the lagna or the Moon',
                    [p, ex], [house[p], house[ex]],
                    f"The debilitation of {p} in {RASIS[s]} is cancelled: {ex}, which is exalted in {RASIS[s]}, "
                    f"is in a kendra from {' and from '.join(refs)}")
        d9 = c.vargas['D9']['signs'][p]
        if d9 == EXALT_SIGN[p]:
            met.append('c')
            add(f'Neecha bhanga of {p} - condition (c)', 'found', 'The debilitated planet is exalted in D9',
                [p], [house[p]], f'The debilitation of {p} in {RASIS[s]} is cancelled: {p} is in {RASIS[d9]} in D9')
        c.neecha_bhanga[p] = met
        if not met:
            add(f'Neecha bhanga of {p}', 'not found', 'Cancellation of debilitation: conditions (a), (b), (c)',
                [p], [house[p]], f'{p} is debilitated in {RASIS[s]} and none of the three conditions is met')

    # Raja yoga, Dhana yoga
    def lords_of(houses):
        return {p: [h for h in c.owned[p] if h in houses] for p in SEVEN if set(c.owned[p]) & set(houses)}

    def pair_rows(name, rule, qualifies):
        found = False
        for a, b in combinations(SEVEN, 2):
            if not qualifies(a, b):
                continue
            links = c.links(a, b)
            if not links:
                continue
            found = True
            add(name, 'found', rule, [a, b], sorted({house[a], house[b]}),
                f"{a} (lord of {_join(c.owned[a])}) in house {house[a]}; {b} (lord of {_join(c.owned[b])}) "
                f"in house {house[b]}; link: {', '.join(links)}")
        if not found:
            add(name, 'not found', rule, note='No qualifying pair of lords is joined')

    kendra_lords, trikona_lords = lords_of(KENDRA), lords_of(TRIKONA)
    pair_rows('Raja yoga', 'A kendra lord and a trikona lord joined by conjunction, mutual aspect or exchange of signs',
              lambda a, b: (a in kendra_lords and b in trikona_lords) or (b in kendra_lords and a in trikona_lords))
    wealth_lords = lords_of((1, 2, 5, 9, 11))
    pair_rows('Dhana yoga', 'Two lords of houses 1, 2, 5, 9, 11 joined by conjunction, mutual aspect or exchange of signs',
              lambda a, b: a in wealth_lords and b in wealth_lords)

    # Viparita raja yoga
    for name, h in (('Harsha', 6), ('Sarala', 8), ('Vimala', 12)):
        lord = c.house_lord[h]
        add(f'{name} yoga (Viparita raja yoga)', 'found' if house[lord] in DUSTHANA else 'not found',
            f'The lord of the {h}th house placed in the 6th, 8th or 12th', [lord], [house[lord]],
            f'{lord}, lord of {h}, is in house {house[lord]}')

    # Parivartana
    swaps = [(a, b) for a, b in combinations(SEVEN, 2) if c.exchange(a, b)]
    for a, b in swaps:
        add('Parivartana yoga', 'found', 'Two planets each in a sign owned by the other', [a, b],
            sorted({house[a], house[b]}), f'{a} in {RASIS[sign[a]]}, {b} in {RASIS[sign[b]]}')
    if not swaps:
        add('Parivartana yoga', 'not found', 'Two planets each in a sign owned by the other',
            note='No two planets exchange signs')

    # From the Moon
    second = [p for p in STAR_PLANETS if from_moon(p) == 2]
    twelfth = [p for p in STAR_PLANETS if from_moon(p) == 12]
    with_moon = [p for p in STAR_PLANETS if from_moon(p) == 1]
    detail = f'2nd from the Moon: {_join(second)}; 12th from the Moon: {_join(twelfth)}'
    scope = 'counting Mars, Mercury, Jupiter, Venus, Saturn'
    add('Sunapha yoga', 'found' if second and not twelfth else 'not found',
        f'A planet in the 2nd from the Moon and none in the 12th ({scope})', second, [], detail)
    add('Anapha yoga', 'found' if twelfth and not second else 'not found',
        f'A planet in the 12th from the Moon and none in the 2nd ({scope})', twelfth, [], detail)
    add('Durudhara yoga', 'found' if second and twelfth else 'not found',
        f'Planets in both the 2nd and the 12th from the Moon ({scope})', second + twelfth, [], detail)
    formed = not (second or twelfth or with_moon)
    kl = [p for p in STAR_PLANETS if house[p] in KENDRA]
    km = [p for p in STAR_PLANETS if from_moon(p) in KENDRA]
    status = 'not found' if not formed else ('cancelled' if (kl or km) else 'found')
    note = f'Formed: {_yes(formed)} ({detail}; with the Moon: {_join(with_moon)}).'
    if formed:
        note += (f' Cancelled: {_yes(bool(kl or km))} (in a kendra from the lagna: {_join(kl)}; '
                 f'in a kendra from the Moon: {_join(km)}).')
    add('Kemadruma yoga', status,
        f'No planet in the 2nd or 12th from the Moon and no planet with the Moon ({scope}); cancelled when one of them '
        'is in a kendra from the lagna or from the Moon', kl + [p for p in km if p not in kl] if formed else [],
        [], note)

    # From the Sun
    def from_sun(p):
        return house_from(sign[p], c.sun_sign)
    second = [p for p in STAR_PLANETS if from_sun(p) == 2]
    twelfth = [p for p in STAR_PLANETS if from_sun(p) == 12]
    detail = f'2nd from the Sun: {_join(second)}; 12th from the Sun: {_join(twelfth)}'
    add('Vesi yoga', 'found' if second and not twelfth else 'not found',
        f'A planet in the 2nd from the Sun and none in the 12th ({scope})', second, [], detail)
    add('Vasi yoga', 'found' if twelfth and not second else 'not found',
        f'A planet in the 12th from the Sun and none in the 2nd ({scope})', twelfth, [], detail)
    add('Ubhayachari yoga', 'found' if second and twelfth else 'not found',
        f'Planets in both the 2nd and the 12th from the Sun ({scope})', second + twelfth, [], detail)

    # Adhi, Amala
    adhi = [p for p in NATURAL_BENEFICS if from_moon(p) in (6, 7, 8)]
    add('Adhi yoga', 'found' if adhi else 'not found',
        'Mercury, Jupiter and Venus in the 6th, 7th or 8th from the Moon', adhi, [house[p] for p in adhi],
        f'{len(adhi)} of 3 benefics' + (' (complete)' if len(adhi) == 3 else (' (partial)' if adhi else '')))
    am_l = [p for p in NATURAL_BENEFICS if house[p] == 10]
    am_m = [p for p in NATURAL_BENEFICS if from_moon(p) == 10]
    add('Amala yoga', 'found' if (am_l or am_m) else 'not found',
        'Mercury, Jupiter or Venus in the 10th from the lagna or from the Moon', am_l + [p for p in am_m if p not in am_l],
        sorted({house[p] for p in am_l + am_m}),
        f'10th from the lagna: {_join(am_l)}; 10th from the Moon: {_join(am_m)}')

    # Kuja dosha
    for ref, ref_sign in (('the lagna', c.lagna_sign), ('the Moon', moon), ('Venus', sign['Venus'])):
        place = house_from(sign['Mars'], ref_sign)
        add(f'Kuja dosha from {ref}', 'found' if place in (1, 2, 4, 7, 8, 12) else 'not found',
            f'Mars in the 1st, 2nd, 4th, 7th, 8th or 12th from {ref}', ['Mars'], [house['Mars']],
            f'Mars is in place {place} from {ref}')

    # Kala Sarpa
    rahu = c.points['Rahu']['lon']
    arcs = [norm(c.points[p]['lon'] - rahu) for p in SEVEN]
    one_side = all(a < 180 for a in arcs) or all(a > 180 for a in arcs)
    side = 'between Rahu and Ketu' if all(a < 180 for a in arcs) else 'between Ketu and Rahu'
    add('Kala Sarpa yoga (popular, not in BPHS)', 'found' if one_side else 'not found',
        'All seven planets on one side of the Rahu-Ketu axis, by longitude', SEVEN if one_side else [], [],
        f'All seven planets lie {side} (going forward through the zodiac)' if one_side
        else 'Planets lie on both sides of the axis')
    return rows


# ── DASA ──────────────────────────────────────────────────────────────────────

def _lord_cols(c, prefix, lord):
    seven = lord in SEVEN
    return {
        f'{prefix}_houses_owned': _join(c.owned[lord]),
        f'{prefix}_house': c.house[lord],
        f'{prefix}_sign': RASIS[c.sign[lord]],
        f'{prefix}_dignity': c.dignity['D1'][lord][0] if seven else None,
        f'{prefix}_debilitated': _yes(c.dignity['D1'][lord][1]) if seven else None,
        f'{prefix}_vimsopaka_shodasavarga': c.vimsopaka[lord]['shodasavarga'] if seven else None,
    }


def bhuktis(c):
    """(dasa row, bhukti row) for every bhukti in the Vedic dasa tree."""
    return [(d, b) for d in c.v['dasa']['dasas'] for b in d['sub']]


def _dasa(c):
    rows = []
    for d, b in bhuktis(c):
        row = {
            'dasa_lord': d['lord'],
            'bhukti_lord': b['lord'],
            'start_local': _sec(b['start']),
            'end_local': _sec(b['end']),
            'age_at_start_years': round((b['start'] - c.birth).total_seconds() / 86400.0 / YEAR_DAYS, 3),
            'age_at_end_years': round((b['end'] - c.birth).total_seconds() / 86400.0 / YEAR_DAYS, 3),
        }
        row.update(_lord_cols(c, 'dasa_lord', d['lord']))
        row.update(_lord_cols(c, 'bhukti_lord', b['lord']))
        rows.append(row)
    return rows


def pratyantars(antaram, birth):
    """
    The nine pratyantar periods of one antaram row of the dasa tree, as
    (lord, start, end). The order starts with the antaram lord and each part
    is antaram length x lord's years / 120. Parts that ended before birth are
    dropped and the one running at birth starts at birth, as in the engine.
    """
    end = antaram['end']
    start = end - timedelta(days=antaram['years'] * YEAR_DAYS)
    if abs((start - antaram['start']).total_seconds()) < 1.0:
        start = antaram['start']                       # not clipped at birth: use the engine's own start
    span = end - start
    first = DASA_ORDER.index(antaram['lord'])
    out, done = [], 0
    for i in range(9):
        lord = DASA_ORDER[(first + i) % 9]
        s = start + span * (done / 120.0)
        done += DASA_YRS[lord]
        e = start + span * (done / 120.0) if done < 120 else end
        if e > birth:
            out.append((lord, max(s, birth), e))
    return out


def _pratyantar(c):
    lo = c.now - timedelta(days=PRATYANTAR_YEARS_BACK * YEAR_DAYS)
    hi = c.now + timedelta(days=PRATYANTAR_YEARS_AHEAD * YEAR_DAYS)
    rows = []
    for d in c.v['dasa']['dasas']:
        if d['end'] <= lo or d['start'] >= hi:
            continue
        for b in d['sub']:
            if b['end'] <= lo or b['start'] >= hi:
                continue
            for a in b['sub']:
                if a['end'] <= lo or a['start'] >= hi:
                    continue
                for lord, s, e in pratyantars(a, c.birth):
                    if e <= lo or s >= hi:
                        continue
                    rows.append({'dasa_lord': d['lord'], 'bhukti_lord': b['lord'], 'antaram_lord': a['lord'],
                                 'pratyantar_lord': lord, 'start_local': _sec(s), 'end_local': _sec(e),
                                 'days': round((e - s).total_seconds() / 86400.0, 3)})
    return rows


# ── TRANSITS ──────────────────────────────────────────────────────────────────

def _body(body, node):
    """(Swiss Ephemeris id, largest daily motion) for a transit body."""
    if body == 'Rahu':
        return (swe.TRUE_NODE, _VMAX['true']) if node == 'true' else (swe.MEAN_NODE, _VMAX['mean'])
    return A.SWE_IDS[body], _VMAX[body]


def sign_entries(body, jd_start, jd_end, sid_mode, node='mean', min_step=TRANSIT_MIN_STEP):
    """
    Every change of sidereal sign of a body between two Julian days (UT), as
    (jd of entry, sign left, sign entered), in time order.

    The search steps through time and bisects each change found. A step is
    as long as the body needs, at its largest speed, to reach the nearest
    sign boundary - it cannot change sign sooner - and never shorter than
    min_step days, so near a boundary this is a plain search in steps of
    min_step. tests/test_enrich.py checks it against a search that uses
    one-day steps throughout, for 1900-2100.
    """
    pid, vmax = _body(body, node)
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
    out = []
    with A._SWE_LOCK:
        swe.set_sid_mode(sid_mode)

        def lon(jd):
            return norm(swe.calc_ut(jd, pid, flags)[0][0])

        jd = jd_start
        cur = lon(jd)
        sign = int(cur // 30) % 12
        while jd < jd_end:
            in_sign = cur - 30.0 * sign
            step = max(min_step, min(in_sign, 30.0 - in_sign) / vmax)
            nxt = min(jd + step, jd_end)
            cur = lon(nxt)
            if int(cur // 30) % 12 == sign:
                jd = nxt
                continue
            lo, hi = jd, nxt                        # still in the old sign at lo, out of it at hi
            while hi - lo > TRANSIT_TOL:
                mid = (lo + hi) / 2.0
                if int(lon(mid) // 30) % 12 == sign:
                    lo = mid
                else:
                    hi = mid
            cur = lon(hi)
            new_sign = int(cur // 30) % 12
            out.append((hi, sign, new_sign))
            jd, sign = hi, new_sign
    return out


def stays(body, jd_start, jd_end, sid_mode, node='mean'):
    """
    Consecutive stays of a body in a sign between two Julian days:
    dicts {sign, entry, exit, motion}; entry of the first and exit of the last
    are None (unknown: outside the window searched).
    """
    entries = sign_entries(body, jd_start, jd_end, sid_mode, node)
    out = []
    if not entries:
        return out
    out.append({'sign': entries[0][1], 'entry': None, 'exit': entries[0][0], 'motion': None})
    for i, (jd, frm, to) in enumerate(entries):
        nxt = entries[i + 1][0] if i + 1 < len(entries) else None
        out.append({'sign': to, 'entry': jd, 'exit': nxt,
                    'motion': 'direct' if to == (frm + 1) % 12 else 'retrograde'})
    return out


def jd_to_utc(jd):
    y, mo, d, h = swe.revjul(jd)
    return datetime(y, mo, d) + timedelta(hours=h)


def _transit_data(c):
    """Stays of Saturn, Jupiter and Rahu around the life, with moments as datetimes."""
    jd_birth = A.julian_day(c.meta['ut_dt'])
    jd_now = A.julian_day(c.now - timedelta(hours=c.offset))
    jd_end = max(jd_now, jd_birth) + TRANSIT_YEARS_AHEAD * YEAR_DAYS
    off = timedelta(hours=c.offset)
    data = {}
    for body, margin in (('Saturn', 3300), ('Jupiter', 1200), ('Rahu', 1200)):
        rows = stays(body, jd_birth - margin, jd_end + margin, c.sid_mode, c.node)
        for r in rows:
            for k in ('entry', 'exit'):
                utc = _minute(jd_to_utc(r[k])) if r[k] is not None else None
                r[k + '_utc'] = utc
                r[k + '_local'] = utc + off if utc else None
        data[body] = rows
    c.window = (c.birth, jd_to_utc(jd_end) + off)
    c.window_utc = (c.meta['ut_dt'], jd_to_utc(jd_end))
    return data


def _overlaps(row, lo_utc, hi_utc):
    return ((row['entry_utc'] is None or row['entry_utc'] < hi_utc)
            and (row['exit_utc'] is None or row['exit_utc'] > lo_utc))


def _transits(c):
    lo, hi = c.window_utc
    rows = []
    for planet in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
        src = c.transit['Rahu' if planet == 'Ketu' else planet]
        for st in src:
            if not _overlaps(st, lo, hi):
                continue
            s = (st['sign'] + 6) % 12 if planet == 'Ketu' else st['sign']
            fm = house_from(s, c.moon_sign)
            rows.append({
                'planet': planet,
                'sign_no': s + 1,
                'sign': RASIS[s],
                'entry_local': st['entry_local'],
                'entry_utc': st['entry_utc'],
                'exit_local': st['exit_local'],
                'exit_utc': st['exit_utc'],
                'motion_at_entry': st['motion'],
                'house_from_lagna': house_from(s, c.lagna_sign),
                'house_from_moon': fm,
                'sav_bindus': c.sav[s],
                'own_bav_bindus': c.bav[planet][s] if planet in ('Saturn', 'Jupiter') else None,
                'result_from_moon': 'favourable' if fm in TRANSIT_GOOD_FROM_MOON[planet] else 'unfavourable',
                'saturn_from_moon': SATURN_FROM_MOON.get(fm) if planet == 'Saturn' else None,
            })
    return rows


def _transit_now(c):
    now_utc = c.now - timedelta(hours=c.offset)
    pos = A._positions(A.julian_day(now_utc), c.lat, c.lon, c.sid_mode, c.node)
    rows = []
    for p in PLANETS:
        lon, speed = pos['pts'][p]
        s = A.get_rasi(lon)
        rows.append({
            'planet': p,
            'as_of_local': _sec(c.now),
            'as_of_utc': _sec(now_utc),
            'longitude_deg': _r6(lon),
            'sign_no': s + 1,
            'sign': RASIS[s],
            'deg_in_sign': _r6(norm(lon) % 30),
            'deg_in_sign_text': A.fmt_sign_dms(lon),
            'retrograde': _yes(speed < 0) if p in SEVEN else None,
            'speed_deg_per_day': _r6(speed),
            'house_from_lagna': house_from(s, c.lagna_sign),
            'house_from_moon': house_from(s, c.moon_sign),
        })
    return rows


def sade_sati_cycles(saturn_stays, moon_sign):
    """
    Sade sati cycles from Saturn's stays: Saturn in the 12th, 1st or 2nd sign
    from the Moon, merged across the short breaks made by retrograde motion.
    Returns a list of cycles, each a list of stays (breaks included, marked
    with phase None).
    """
    phase = {11: 1, 0: 2, 1: 3}
    cycles, cur, gap = [], [], []
    for st in saturn_stays:
        ph = phase.get((st['sign'] - moon_sign) % 12)
        if ph:
            if cur and gap:
                long_gap = (gap[0]['entry_utc'] is None or gap[-1]['exit_utc'] is None
                            or (gap[-1]['exit_utc'] - gap[0]['entry_utc']).days > 730)
                if long_gap:
                    cycles.append(cur)
                    cur = []
                else:
                    cur.extend(dict(g, phase=None) for g in gap)
            gap = []
            cur.append(dict(st, phase=ph))
        elif cur:
            gap.append(st)
    if cur:
        cycles.append(cur)
    return cycles


def _sade_sati(c):
    lo, hi = c.window_utc
    rows = []
    number = 0
    for cyc in sade_sati_cycles(c.transit['Saturn'], c.moon_sign):
        start, end = cyc[0]['entry_utc'], cyc[-1]['exit_utc']
        if (start is not None and start >= hi) or (end is not None and end <= lo):
            continue
        number += 1

        def emit(label, members, breaks):
            signs = []
            for st in members:
                if RASIS[st['sign']] not in signs:
                    signs.append(RASIS[st['sign']])
            rows.append({'cycle': number, 'phase': label, 'row_type': 'span',
                         'start_local': members[0]['entry_local'], 'end_local': members[-1]['exit_local'],
                         'start_utc': members[0]['entry_utc'], 'end_utc': members[-1]['exit_utc'],
                         'saturn_sign': ', '.join(signs), 'break_count': len(breaks)})
            for st in breaks:
                rows.append({'cycle': number, 'phase': label, 'row_type': 'break',
                             'start_local': st['entry_local'], 'end_local': st['exit_local'],
                             'start_utc': st['entry_utc'], 'end_utc': st['exit_utc'],
                             'saturn_sign': RASIS[st['sign']], 'break_count': None})

        emit('sade sati - whole', [s for s in cyc if s['phase']], [s for s in cyc if s['phase'] is None])
        for ph, label in ((1, 'sade sati - 1st phase'), (2, 'sade sati - 2nd phase'), (3, 'sade sati - 3rd phase')):
            idx = [i for i, s in enumerate(cyc) if s['phase'] == ph]
            if not idx:
                continue
            members = [cyc[i] for i in idx]
            breaks = [s for s in cyc[idx[0]:idx[-1] + 1] if s['phase'] != ph]
            emit(label, members, breaks)
    return rows


def _double_transit(c):
    off = timedelta(hours=c.offset)
    lo = c.now - off                                    # spans that touch the 10 years after the report date,
    hi = lo + timedelta(days=TRANSIT_YEARS_AHEAD * YEAR_DAYS)   # each with its real start and end
    reach_j = {0: 'occupies', 4: 'aspects (5th)', 6: 'aspects (7th)', 8: 'aspects (9th)'}
    reach_s = {0: 'occupies', 2: 'aspects (3rd)', 6: 'aspects (7th)', 9: 'aspects (10th)'}
    rows = []
    for j in c.transit['Jupiter']:
        if not _overlaps(j, lo, hi):
            continue
        for s in c.transit['Saturn']:
            if not _overlaps(s, lo, hi):
                continue
            if None in (j['entry_utc'], s['entry_utc'], j['exit_utc'], s['exit_utc']):
                continue                                # cannot happen inside the window searched
            start = max(j['entry_utc'], s['entry_utc'])
            end = min(j['exit_utc'], s['exit_utc'])
            if start >= end or start >= hi or end <= lo:
                continue
            for dj, how_j in reach_j.items():
                target = (j['sign'] + dj) % 12
                ds = (target - s['sign']) % 12
                if ds not in reach_s:
                    continue
                rows.append({
                    'house': house_from(target, c.lagna_sign),
                    'sign': RASIS[target],
                    'start_local': start + off,
                    'end_local': end + off,
                    'start_utc': start,
                    'end_utc': end,
                    'jupiter_sign': RASIS[j['sign']],
                    'jupiter_reaches_by': how_j,
                    'saturn_sign': RASIS[s['sign']],
                    'saturn_reaches_by': reach_s[ds],
                    'method': 'modern method',
                })
    rows.sort(key=lambda r: (r['house'], r['start_utc']))
    return rows


# ── TOPICS ────────────────────────────────────────────────────────────────────

def topic_significators(c, topic, significators):
    sig = list(significators)
    if topic == 'Marriage' and c.female:
        sig.append(MARRIAGE_EXTRA_FOR_WOMAN)
    return sig


def _topic_map(c):
    rows = []
    for topic, houses, sig, vargas, kp in TOPICS:
        fixed = _join(sig)
        if topic == 'Marriage':
            fixed += f'; {MARRIAGE_EXTRA_FOR_WOMAN} also for a woman'
        rows.append({'topic': topic, 'd1_houses': _join(houses), 'significators': fixed,
                     'significators_for_this_chart': _join(topic_significators(c, topic, sig)),
                     'divisional_charts': _join(vargas), 'kp_houses': _join(kp)})
    return rows


def _topic_facts(c):
    rows = []
    cusps = {x['house']: x for x in c.kp['cusps']}
    all_points = PLANETS + (['Mandi'] if c.mandi else [])

    def add(topic, subject, factor, value):
        rows.append({'topic': topic, 'subject': subject, 'factor': factor, 'value': value})

    for topic, houses, sig, vargas, kp in TOPICS:
        for h in houses:
            s, lord = c.house_sign[h], c.house_lord[h]
            sub = f'house {h}'
            add(topic, sub, 'sign', RASIS[s])
            add(topic, sub, 'lord', lord)
            add(topic, sub, 'lord_house', c.house[lord])
            add(topic, sub, 'lord_sign', RASIS[c.sign[lord]])
            add(topic, sub, 'lord_dignity', c.dignity['D1'][lord][0])
            add(topic, sub, 'lord_debilitated', _yes(c.dignity['D1'][lord][1]))
            add(topic, sub, 'occupants', _join(n for n in all_points if c.sign[n] == s))
            add(topic, sub, 'aspected_by', _join(c.aspecting[s]))
            add(topic, sub, 'sav_bindus', c.sav[s])
        for p in topic_significators(c, topic, sig):
            sub = f'significator {p}'
            add(topic, sub, 'sign', RASIS[c.sign[p]])
            add(topic, sub, 'house', c.house[p])
            if p in SEVEN:
                add(topic, sub, 'dignity', c.dignity['D1'][p][0])
                add(topic, sub, 'debilitated', _yes(c.dignity['D1'][p][1]))
                add(topic, sub, 'retrograde', _yes(c.points[p]['retro']))
                if p in COMBUST_ORB:
                    add(topic, sub, 'combust', _yes(c.points[p]['combust']))
                add(topic, sub, 'vimsopaka_shodasavarga', c.vimsopaka[p]['shodasavarga'])
            else:
                add(topic, sub, 'sign_lord', SIGN_LORDS[c.sign[p]])
            add(topic, sub, 'aspected_by', _join(q for q in c.aspecting[c.sign[p]] if q != p))
            add(topic, sub, 'conjunct_with', _join(q for q in c.in_sign[c.sign[p]] if q != p))
        for key in vargas:
            vg = c.vargas[key]
            s = vg['lagna_sign']
            lord = SIGN_LORDS[s]
            sub = f'chart {key}'
            sec_e, sec_l = c.margins[key][-1][0], c.margins[key][1][0]
            small = [x for x in (sec_e, sec_l) if x is not None]
            add(topic, sub, 'lagna_sign', RASIS[s])
            add(topic, sub, 'lagna_lord', lord)
            add(topic, sub, 'lagna_lord_house_in_chart', house_from(vg['signs'][lord], s))
            add(topic, sub, 'lagna_lord_dignity_in_chart', c.dignity[key][lord][0])
            add(topic, sub, 'lagna_uncertain', _yes(bool(small) and min(small) < LAGNA_UNCERTAIN))
            add(topic, sub, 'seconds_earlier', sec_e)
            add(topic, sub, 'seconds_later', sec_l)
            for p in topic_significators(c, topic, sig):
                add(topic, sub, f'{p}_house_in_chart', house_from(vg['signs'][p], s))
                if p in SEVEN:
                    add(topic, sub, f'{p}_dignity_in_chart', c.dignity[key][p][0])
        for h in kp:
            sub = f'KP house {h}'
            add(topic, sub, 'cusp_sign', RASIS[cusps[h]['sign']])
            add(topic, sub, 'cusp_sub_lord', cusps[h]['sub_lord'])
            add(topic, sub, 'planets_signifying', _join(p for p in PLANETS if h in c.kp_signifies.get(p, ())))
    return rows


def topic_letters(c, lord, topic, houses, sig, vargas, kp):
    """The letters (a) to (f) of the topic-score rule that fire for one dasa or bhukti lord."""
    letters = ''
    key_signs = {c.house_sign[h] for h in houses}
    if set(c.owned[lord]) & set(houses):
        letters += 'a'
    if c.house[lord] in houses:
        letters += 'b'
    if c.asp_signs[lord] & key_signs:
        letters += 'c'
    if lord in topic_significators(c, topic, sig):
        letters += 'd'
    for key in vargas:
        vg = c.vargas[key]
        place = house_from(vg['signs'][lord], vg['lagna_sign'])
        strong = lord in SEVEN and c.dignity[key][lord][0] in ('Exalted', 'Own sign', 'Moolatrikona')
        if place in (1, 4, 7, 10, 5, 9, 11) or strong:
            letters += 'e'
            break
    if c.kp_signifies.get(lord, set()) & set(kp):
        letters += 'f'
    return letters


def penalty(c, lord):
    """Reasons for the one-point deduction of the topic-score rule."""
    reasons = []
    if lord in SEVEN and c.vimsopaka[lord]['shodasavarga'] < 10:
        reasons.append('vimsopaka under 10')
    if c.combust(lord):
        reasons.append('combust')
    if c.debilitated(lord) and not c.neecha_bhanga.get(lord):
        reasons.append('debilitated, not cancelled')
    return reasons


def _topic_scores(c):
    letters = {(lord, t[0]): topic_letters(c, lord, *t) for lord in PLANETS for t in TOPICS}
    penalties = {lord: penalty(c, lord) for lord in PLANETS}
    rows = []
    for d, b in bhuktis(c):
        for t in TOPICS:
            lb, ld = letters[(b['lord'], t[0])], letters[(d['lord'], t[0])]
            pen = penalties[b['lord']]
            rows.append({
                'dasa_lord': d['lord'],
                'bhukti_lord': b['lord'],
                'start_local': _sec(b['start']),
                'end_local': _sec(b['end']),
                'topic': t[0],
                'relevance_score_not_a_prediction': len(lb) + len(ld) / 2.0 - (1 if pen else 0),
                'bhukti_lord_letters': lb or 'none',
                'dasa_lord_letters': ld or 'none',
                'deduction': _join(pen),
            })
    return rows


# ── COLUMN DICTIONARY ─────────────────────────────────────────────────────────

_LOCAL = 'clock time at the birth place (fixed UTC offset in force at birth)'
COLUMNS = {
    'AI_ReadMe': [('section', 'Group of lines'), ('item', 'What the line is about'), ('text', 'The line itself')],
    'AI_Facts': [('key', 'Name of the fact'), ('value', 'Its value: text, number, date or time'),
                 ('note', 'What the value means')],
    'AI_Planets': [
        ('point', 'Lagna, the nine planets, then Mandi'),
        ('longitude_deg', 'Sidereal longitude, 0-360'),
        ('sign_no', '1 = Mesha ... 12 = Meena'), ('sign', 'Sign (rasi) occupied'),
        ('deg_in_sign', 'Degrees inside the sign, 0-30'), ('deg_in_sign_text', 'The same as degrees, minutes, seconds'),
        ('nakshatra_no', '1 = Ashwini ... 27 = Revati'), ('nakshatra', 'Nakshatra occupied'), ('pada', 'Quarter, 1-4'),
        ('sign_lord', 'Lord of the sign occupied'), ('star_lord', 'Lord of the nakshatra occupied'),
        ('house_whole_sign', 'House counted by whole sign from the lagna (the default house)'),
        ('bhava_sripati', 'Bhava by the Sripati system (unequal, lagna degree at the centre of bhava 1)'),
        ('kp_house_placidus', 'KP house: Placidus cusps and KP ayanamsha; empty for Mandi'),
        ('house_from_moon', 'Place counted from the Moon sign'), ('house_from_sun', 'Place counted from the Sun sign'),
        ('retrograde', 'yes / no for the seven planets; empty for the lagna, Rahu, Ketu and Mandi '
                       '(the nodes move backward by nature and are not flagged)'),
        ('speed_deg_per_day', 'Daily motion in longitude; negative = moving backward'),
        ('combust', 'yes / no for Moon to Saturn; empty where combustion does not apply'),
        ('distance_from_sun_deg', 'Angular distance from the Sun, 0-180'),
        ('combust_orb_deg', 'Orb that applies to this planet (smaller when retrograde)'),
        ('dignity', 'Exalted, Moolatrikona, Own sign, Great friend, Friend, Neutral, Enemy or Great enemy in D1. '
                    'A debilitated planet shows its relationship with its sign lord here: always read the '
                    'debilitated column as well'),
        ('moolatrikona', 'yes / no'), ('debilitated', 'yes / no; separate from the dignity label'),
        ('debilitation_cancelled_by', 'For a debilitated planet: the neecha bhanga conditions met (a, b, c; see AI_Yogas), '
                                      'or none when the debilitation is not cancelled. Empty when the planet is not debilitated'),
        ('distance_from_deep_exaltation_deg', 'Angular distance from the deep exaltation point, 0-180'),
        ('houses_owned', 'Houses whose sign the planet owns; none for Rahu and Ketu'),
        ('functional_nature', 'Yogakaraka, Benefic, Malefic or Neutral for this lagna'),
        ('houses_aspected', 'Houses receiving its full aspect'), ('planets_aspected', 'Planets in those houses'),
        ('aspected_by', 'Planets whose full aspect falls on the sign of this point'),
        ('conjunct_with', 'Planets in the same sign'),
        ('d9_sign', 'Sign in the Navamsa'), ('vargottama', 'yes when the D1 and D9 signs are the same'),
        ('vimsopaka_shodasavarga', 'Strength out of 20 over 16 charts'),
        ('vimsopaka_dasavarga', 'Strength out of 20 over 10 charts'),
        ('vimsopaka_saptavarga', 'Strength out of 20 over 7 charts'),
        ('vimsopaka_shadvarga', 'Strength out of 20 over 6 charts'),
        ('own_bav_bindus_in_sign_occupied', 'Bindus in the planet\'s own Bhinnashtakavarga for the sign it occupies (0-8)'),
        ('sav_bindus_in_sign_occupied', 'Sarvashtakavarga bindus of the sign occupied'),
    ],
    'AI_Houses': [
        ('house', 'House number by whole sign from the lagna'), ('sign_no', '1 = Mesha ... 12 = Meena'),
        ('sign', 'Sign of the house'),
        ('house_groups', 'kendra (1, 4, 7, 10), trikona (1, 5, 9), dusthana (6, 8, 12), upachaya (3, 6, 10, 11)'),
        ('lord', 'Lord of the sign'), ('lord_sign', 'Sign the lord occupies'), ('lord_house', 'House the lord occupies'),
        ('lord_dignity', 'Dignity of the lord in D1'), ('lord_debilitated', 'yes / no'),
        ('occupants_whole_sign', 'Planets and Mandi in the sign of this house (the default)'),
        ('occupants_bhava_sripati', 'Planets and Mandi in this bhava by the Sripati system'),
        ('aspected_by', 'Planets whose full aspect falls on this house'),
        ('sav_bindus', 'Sarvashtakavarga bindus of the sign'),
        ('house_from_moon', 'Number of this house counted from the Moon sign'),
        ('kp_cusp_longitude_deg', 'KP: longitude of the Placidus cusp (KP ayanamsha)'),
        ('kp_cusp_sign', 'KP: sign of the cusp'), ('kp_cusp_star_lord', 'KP: star lord of the cusp'),
        ('kp_cusp_sub_lord', 'KP: sub lord of the cusp'), ('kp_occupants', 'KP: planets in this Placidus house'),
    ],
    'AI_Pairs': [
        ('planet_a', 'First planet'), ('planet_b', 'Second planet'), ('same_sign', 'yes = conjunction'),
        ('separation_deg', 'Angular distance between the two, 0-180'),
        ('b_counted_from_a', 'Place of planet_b counted from the sign of planet_a (1 = same sign)'),
        ('a_aspects_b', 'yes / no, full aspect by sign'), ('b_aspects_a', 'yes / no, full aspect by sign'),
        ('mutual_aspect', 'yes when each aspects the other'),
        ('exchange_of_signs', 'yes when each is in a sign owned by the other (parivartana)'),
        ('natural_a_to_b', 'Natural relationship: how planet_a regards planet_b'), ('natural_b_to_a', 'The reverse'),
        ('temporary_a_to_b', 'Temporary relationship from D1'), ('temporary_b_to_a', 'The reverse'),
        ('compound_a_to_b', 'Compound relationship'), ('compound_b_to_a', 'The reverse'),
        ('planetary_war', 'yes when both are among Mars, Mercury, Jupiter, Venus, Saturn and within 1°'),
    ],
    'AI_Vargas': [
        ('chart', 'D1 ... D60'), ('chart_name', 'Name of the divisional chart'), ('point', 'Lagna, planet or Mandi'),
        ('sign_no', '1 = Mesha ... 12 = Meena'), ('sign', 'Sign in that chart'),
        ('deg_in_chart', 'Degrees inside that sign of the divisional chart, 0-30'),
        ('deg_in_chart_text', 'The same as degrees, minutes, seconds'),
        ('house', 'House by whole sign from that chart\'s own lagna'), ('sign_lord', 'Lord of the sign'),
        ('dignity', 'Dignity of the planet in that chart'), ('debilitated', 'yes / no'),
    ],
    'AI_VargaLagnas': [
        ('chart', 'D1 ... D60'), ('chart_name', 'Name of the divisional chart'),
        ('lagna_sign_no', '1 = Mesha ... 12 = Meena'), ('lagna_sign', 'Lagna of that chart'),
        ('lagna_deg_in_chart', 'Degrees of the lagna inside that sign, 0-30'), ('lagna_lord', 'Lord of that lagna'),
        ('lagna_lord_sign', 'Sign of the lord in that chart'), ('lagna_lord_house', 'House of the lord in that chart'),
        ('lagna_lord_dignity', 'Dignity of the lord in that chart'), ('lagna_lord_debilitated', 'yes / no'),
        ('seconds_earlier', 'Largest whole number of seconds the birth can be earlier with the lagna of this chart '
                            'unchanged; at one second more it is the sign in lagna_if_earlier'),
        ('lagna_if_earlier', 'The lagna of this chart for a birth earlier than that'),
        ('seconds_later', 'Largest whole number of seconds the birth can be later with the lagna of this chart '
                          'unchanged; at one second more it is the sign in lagna_if_later'),
        ('lagna_if_later', 'The lagna of this chart for a birth later than that'),
        ('lagna_uncertain', 'yes when either margin is under 120 seconds: read this chart with caution'),
    ],
    'AI_Strength': (
        [('planet', 'Sun to Saturn')]
        + [(f'vimsopaka_{s}', f'Vimsopaka strength out of 20, {s} weights') for s in VIMSOPAKA_WEIGHTS]
        + [(f'points_{k}', f'Dignity points in {k} (20, 18, 15, 10, 7 or 5)') for k in VARGA_KEYS]
        + [('debilitated_in', 'Charts in which the planet is debilitated')]),
    'AI_Ashtakavarga': [
        ('planet', 'Sun to Saturn = that planet\'s Bhinnashtakavarga; Sarvashtakavarga = the sum of the seven'),
        ('row_type', 'sign = bindus of one sign; total = the sum over the 12 signs'),
        ('sign_no', '1 = Mesha ... 12 = Meena; empty on total rows'), ('sign', 'Sign, or Total'),
        ('house', 'House of that sign from the lagna; empty on total rows'), ('bindus', 'Number of bindus'),
    ],
    'AI_Yogas': [
        ('yoga', 'Name of the yoga or dosha checked'),
        ('status', 'found, not found, or cancelled = the yoga on this row is formed but cancelled (Kemadruma). '
                   'A Neecha bhanga row with status found means that a debilitation is cancelled'),
        ('rule', 'The rule as applied'),
        ('planets', 'Planets involved'),
        ('houses', 'Houses those planets occupy, always counted from the lagna, also on rows that test from the '
                   'Moon, the Sun or Venus (the place from that point is in the note)'),
        ('note', 'What was found in this chart'),
    ],
    'AI_Dasa': [
        ('dasa_lord', 'Lord of the dasa (1st level)'), ('bhukti_lord', 'Lord of the bhukti (2nd level)'),
        ('start_local', f'Start of the bhukti, {_LOCAL}'), ('end_local', f'End of the bhukti, {_LOCAL}'),
        ('age_at_start_years', 'Age when it starts'), ('age_at_end_years', 'Age when it ends'),
        ('dasa_lord_houses_owned', 'Houses the dasa lord owns'), ('dasa_lord_house', 'House it occupies'),
        ('dasa_lord_sign', 'Sign it occupies'), ('dasa_lord_dignity', 'Its dignity in D1'),
        ('dasa_lord_debilitated', 'yes / no'), ('dasa_lord_vimsopaka_shodasavarga', 'Its strength out of 20'),
        ('bhukti_lord_houses_owned', 'Houses the bhukti lord owns'), ('bhukti_lord_house', 'House it occupies'),
        ('bhukti_lord_sign', 'Sign it occupies'), ('bhukti_lord_dignity', 'Its dignity in D1'),
        ('bhukti_lord_debilitated', 'yes / no'), ('bhukti_lord_vimsopaka_shodasavarga', 'Its strength out of 20'),
    ],
    'AI_Pratyantar': [
        ('dasa_lord', '1st level'), ('bhukti_lord', '2nd level'), ('antaram_lord', '3rd level'),
        ('pratyantar_lord', '4th level'), ('start_local', f'Start, {_LOCAL}'), ('end_local', f'End, {_LOCAL}'),
        ('days', 'Length in days'),
    ],
    'AI_Transits': [
        ('planet', 'Saturn, Jupiter, Rahu or Ketu; rows are in time order for each planet, and a sign appears again '
                   'on every later entry (retrograde re-entry, or the next round of the zodiac)'),
        ('sign_no', '1 = Mesha ... 12 = Meena'), ('sign', 'Sidereal sign entered'),
        ('entry_local', f'Moment of entry, {_LOCAL}. The first row of each planet is the stay that was running '
                        'at birth, so its entry is before the birth'),
        ('entry_utc', 'Moment of entry, UTC'), ('exit_local', f'Moment it leaves the sign, {_LOCAL}'),
        ('exit_utc', 'Moment it leaves the sign, UTC'),
        ('motion_at_entry', 'direct = entered moving forward; retrograde = entered moving backward '
                            '(the usual direction for Rahu and Ketu)'),
        ('house_from_lagna', 'House of that sign from the natal lagna'),
        ('house_from_moon', 'Place of that sign from the natal Moon'),
        ('sav_bindus', 'Natal Sarvashtakavarga bindus of the sign'),
        ('own_bav_bindus', 'Bindus of the sign in the natal Bhinnashtakavarga of Saturn or Jupiter'),
        ('result_from_moon', 'Classical gochara label by place from the Moon: favourable or unfavourable'),
        ('saturn_from_moon', 'Saturn rows only: sade sati phase, ashtama, ardhashtama or kantaka; else empty'),
    ],
    'AI_TransitNow': [
        ('planet', 'The nine planets'), ('as_of_local', f'The report moment, {_LOCAL}'), ('as_of_utc', 'The report moment, UTC'),
        ('longitude_deg', 'Sidereal longitude at that moment'), ('sign_no', '1 = Mesha ... 12 = Meena'),
        ('sign', 'Sign occupied'), ('deg_in_sign', 'Degrees inside the sign'),
        ('deg_in_sign_text', 'The same as degrees, minutes, seconds'), ('retrograde', 'yes / no; empty for Rahu and Ketu'),
        ('speed_deg_per_day', 'Daily motion; negative = backward'),
        ('house_from_lagna', 'House from the natal lagna'), ('house_from_moon', 'Place from the natal Moon'),
    ],
    'AI_SadeSati': [
        ('cycle', 'Number of the sade sati cycle within the period covered'),
        ('phase', 'whole = the complete sade sati; 1st phase (Saturn 12th from the Moon), 2nd phase (in the Moon '
                  'sign) or 3rd phase (2nd from the Moon). Because Saturn moves back and forth, the spans of two '
                  'phases can overlap; the phase running on a date is the one whose span holds the date outside '
                  'its breaks (or read saturn_from_moon in AI_Transits)'),
        ('row_type', 'span = first entry to last exit. break = a time inside that span when Saturn was in another '
                     'sign: on a "whole" row Saturn had left the sade sati signs; on a phase row it was in the '
                     'sign of a neighbouring phase or outside'),
        ('start_local', f'Start, {_LOCAL}'), ('end_local', f'End, {_LOCAL}'), ('start_utc', 'Start, UTC'),
        ('end_utc', 'End, UTC'), ('saturn_sign', 'Sign or signs of Saturn during the row'),
        ('break_count', 'Number of breaks inside a span; empty on break rows'),
    ],
    'AI_DoubleTransit': [
        ('house', 'Natal house reached by both Jupiter and Saturn; rows are sorted by house, then by start'),
        ('sign', 'Its sign'),
        ('start_local', f'Real start of the span, which can be before the report date; {_LOCAL}'),
        ('end_local', f'Real end of the span, which can be more than 10 years ahead; {_LOCAL}'),
        ('start_utc', 'Start, UTC'), ('end_utc', 'End, UTC'), ('jupiter_sign', 'Sign Jupiter transits'),
        ('jupiter_reaches_by', 'occupies, or the aspect it uses'), ('saturn_sign', 'Sign Saturn transits'),
        ('saturn_reaches_by', 'occupies, or the aspect it uses'), ('method', 'Always "modern method": not a classical rule'),
    ],
    'AI_TopicMap': [
        ('topic', 'Common question'), ('d1_houses', 'Key houses in the Rasi chart'),
        ('significators', 'Significator planets (fixed table)'),
        ('significators_for_this_chart', 'Significators used here (Jupiter is added for marriage when the gender is female)'),
        ('divisional_charts', 'Chart to read with D1'), ('kp_houses', 'Houses judged in KP; none where not listed'),
    ],
    'AI_TopicFacts': [
        ('topic', 'Common question'), ('subject', 'A key house, a significator, a divisional chart or a KP house'),
        ('factor', 'Which fact about the subject'), ('value', 'The fact'),
    ],
    'AI_TopicScores': [
        ('dasa_lord', 'Lord of the dasa'), ('bhukti_lord', 'Lord of the bhukti'),
        ('start_local', f'Start of the bhukti, {_LOCAL}'), ('end_local', f'End of the bhukti, {_LOCAL}'),
        ('topic', 'Common question'),
        ('relevance_score_not_a_prediction', 'Rule-based relevance, not a prediction: letters of the bhukti lord '
                                             '+ half the letters of the dasa lord - 1 if a deduction applies'),
        ('bhukti_lord_letters', 'Which of the conditions (a) to (f) the bhukti lord meets'),
        ('dasa_lord_letters', 'Which of the conditions (a) to (f) the dasa lord meets'),
        ('deduction', 'Reason for the one-point deduction, or none'),
    ],
}
SHEETS = list(COLUMNS)


def _readme(c, tables):
    m = c.meta
    lines = []

    def add(section, item, text):
        lines.append({'section': section, 'item': item, 'text': text})

    off = m['utc_offset_str']
    add('About', 'what this is', 'The AI_ sheets hold every fact of this horoscope as flat tables: one table per '
        'sheet, header in row 1, one fact per cell, values only. They repeat what the other sheets of the '
        'workbook (Summary, Vedic, Divisional Charts, KP, ALP, Dasa, Notes) show as chart pictures and add '
        'what an astrologer derives from it. Read facts from the AI_ sheets; do not parse the chart pictures.')
    add('About', 'generated', f"{c.now.strftime('%Y-%m-%d %H:%M:%S')} at the birth place ({off}). "
        'This is the "report date" used for transits and for the range of the pratyantar table.')
    add('About', 'language', 'Always English, whatever language the rest of the report uses. Names follow the '
        'engine: signs Mesha ... Meena, nakshatras Ashwini ... Revati, planets Sun ... Ketu.')
    add('About', 'schema', SCHEMA)
    add('Defaults', 'house system', 'Whole sign from the lagna: every "house" column means this unless its name '
        'says bhava_sripati or kp_.')
    add('Defaults', 'dasa table', f"AI_Dasa and AI_Pratyantar: Vimshottari from the Moon with the Vedic ayanamsha "
        f"({m['ayanamsha_name']}). Use these dates.")
    add('Defaults', 'ayanamsha', f"{m['ayanamsha_name']} for everything except the columns that begin with kp_.")
    add('Warnings', 'KP', 'The KP sheet of the workbook (the "kp" part of the JSON file) and the kp_ columns here '
        'use the Krishnamurti ayanamsha, Placidus houses and their own dasa dates, which differ by weeks from '
        'AI_Dasa. Do not mix KP houses or KP dasa dates with the whole-sign houses and the dates of AI_Dasa.')
    add('Warnings', 'three house systems', 'AI_Planets and AI_Houses show whole-sign, Sripati and KP placements side '
        'by side and they can differ for the same planet. Answer with the whole-sign column and name the system '
        'whenever another one is used.')
    add('Warnings', 'current periods', 'Labels such as "Current" on the other sheets were true on the day the file '
        'was generated and go stale. The AI sheets carry no status column: compare the start and end dates '
        'with today\'s date to find the running dasa, bhukti, pratyantar or transit.')
    add('Warnings', 'divisional charts', 'A divisional chart whose row in AI_VargaLagnas has lagna_uncertain = yes '
        'changes its lagna if the birth time is wrong by under two minutes; treat its houses with caution.')
    add('Warnings', 'scores', 'AI_TopicScores is rule-based relevance, not a prediction. AI_DoubleTransit is a '
        'modern method. Kala Sarpa is popular and not in BPHS.')
    add('Conventions', 'times', f"Columns ending in _local are clock time at the birth place with the fixed offset "
        f"{off} (the offset in force at birth). Columns ending in _utc are UTC. Transit moments are given "
        'to the minute, dasa moments to the second.')
    add('Conventions', 'angles', 'Columns ending in _deg are decimal degrees (6 places); the matching _text column '
        'gives degrees, minutes and seconds.')
    add('Conventions', 'yes / no', 'Flags are the words yes and no. Lists are separated by a comma and a space; '
        'an empty list is the word none.')
    add('Conventions', 'empty cells', 'An empty cell means the value does not apply to that row or could not be '
        'computed. It never means zero or no.')
    add('Conventions', 'house numbers', 'Houses and places are numbered 1 to 12; signs 1 = Mesha to 12 = Meena.')
    missing = []
    if not c.mandi:
        missing.append('Mandi: the Sun does not rise or set at this place on this date, so Mandi has no value '
                       'and its cells are empty.')
    pc = c.v['panchangam']
    if not pc.get('sunrise') or not pc.get('sunset'):
        missing.append('Sunrise or sunset: the Sun does not rise or set at this place on this date.')
    if any(x[0] is None for mg in c.margins.values() for x in mg.values()):
        missing.append('Lagna sensitivity: a divisional lagna did not change within 6 hours, so that margin is empty.')
    if c.kp['house_system'] != 'Placidus':
        missing.append('KP houses: Placidus is undefined at this latitude; Porphyry cusps were used instead.')
    for i, text in enumerate(missing or ['Nothing: every value could be computed for this chart.'], start=1):
        add('Not computed for this chart', str(i), text)
    for i, text in enumerate(NOT_IN_FILE, start=1):
        add('Not in this file', str(i), text)
    for name, text in RULES:
        add('Rules', name, text)
    for sheet in SHEETS:
        rows = len(tables[sheet]) if sheet in tables else None
        add('Sheets', sheet, SHEET_ABOUT[sheet] + (f' ({rows} rows)' if rows is not None else ''))
    for sheet in SHEETS:
        for col, meaning in COLUMNS[sheet]:
            add('Columns', f'{sheet}.{col}', meaning)
    return lines


SHEET_ABOUT = {
    'AI_ReadMe': 'This sheet: what the AI sheets are, warnings, rules and the meaning of every column.',
    'AI_Facts': 'Birth details and settings, one value per row.',
    'AI_Planets': 'One row for the lagna, each planet and Mandi: position, houses, dignity, aspects, strength.',
    'AI_Houses': 'One row per house: sign, lord, occupants, aspects, bindus, KP cusp.',
    'AI_Pairs': 'One row per pair of planets: conjunction, aspect, exchange, friendship.',
    'AI_Vargas': 'One row per point and divisional chart: sign, degree, house, dignity.',
    'AI_VargaLagnas': 'One row per divisional chart: its lagna, the lagna lord and how sensitive it is to birth time.',
    'AI_Strength': 'Vimsopaka strength of the seven planets and the points behind it.',
    'AI_Ashtakavarga': 'Bindus by sign and house for each planet and for the Sarvashtakavarga.',
    'AI_Yogas': 'Every yoga checked, with found, cancelled or not found.',
    'AI_Dasa': 'One row per Vimshottari bhukti from birth, with the state of both lords.',
    'AI_Pratyantar': 'The 4th dasa level from 1 year before the report date to 5 years after.',
    'AI_Transits': 'Sign entries of Saturn, Jupiter, Rahu and Ketu from birth to 10 years after the report date; '
                   'each planet starts with the stay running at birth.',
    'AI_TransitNow': 'Positions of the nine planets on the report date.',
    'AI_SadeSati': 'Sade sati spans and their phases, with retrograde breaks.',
    'AI_DoubleTransit': 'Houses reached by both Jupiter and Saturn in the 10 years after the report date, '
                        'sorted by house.',
    'AI_TopicMap': 'Where to look for each common question.',
    'AI_TopicFacts': 'The facts of this chart for each common question.',
    'AI_TopicScores': 'Rule-based relevance of every bhukti to each common question.',
}


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def enrich(res, now=None):
    """
    Build the AI block from compute() output.

    now: the report moment (naive clock time at the birth place); defaults to
    the moment the horoscope was generated.
    Returns {'schema', 'report_datetime_local', 'sheets', 'columns', 'tables',
    'rules'}; tables[sheet] is a list of rows keyed by column name.
    """
    c = Ctx(res, now)
    c.margins = lagna_margins(c)
    c.transit = _transit_data(c)
    tables = {}
    yoga_rows = _yogas(c)                           # first: it also finds which debilitations are cancelled
    tables['AI_Facts'] = _facts(c)
    tables['AI_Planets'] = _planets(c)
    tables['AI_Houses'] = _houses(c)
    tables['AI_Pairs'] = _pairs(c)
    tables['AI_Vargas'] = _vargas(c)
    tables['AI_VargaLagnas'] = _varga_lagnas(c)
    tables['AI_Strength'] = _strength(c)
    tables['AI_Ashtakavarga'] = _ashtakavarga(c)
    tables['AI_Yogas'] = yoga_rows
    tables['AI_Dasa'] = _dasa(c)
    tables['AI_Pratyantar'] = _pratyantar(c)
    tables['AI_Transits'] = _transits(c)
    tables['AI_TransitNow'] = _transit_now(c)
    tables['AI_SadeSati'] = _sade_sati(c)
    tables['AI_DoubleTransit'] = _double_transit(c)
    tables['AI_TopicMap'] = _topic_map(c)
    tables['AI_TopicFacts'] = _topic_facts(c)
    tables['AI_TopicScores'] = _topic_scores(c)
    tables['AI_ReadMe'] = _readme(c, tables)

    # every row carries every column of its sheet, in the declared order
    ordered = {}
    for sheet in SHEETS:
        cols = [name for name, _ in COLUMNS[sheet]]
        ordered[sheet] = [{k: row.get(k) for k in cols} for row in tables[sheet]]
        for row in tables[sheet]:
            extra = set(row) - set(cols)
            if extra:
                raise KeyError(f'{sheet}: undeclared column(s) {sorted(extra)}')
    return {
        'schema': SCHEMA,
        'report_datetime_local': _sec(c.now),
        'utc_offset_hours': round(c.offset, 6),
        'sheets': SHEETS,
        'columns': {s: [{'name': n, 'meaning': t} for n, t in COLUMNS[s]] for s in SHEETS},
        'tables': ordered,
        'rules': [{'rule': n, 'variant': t} for n, t in RULES],
    }
