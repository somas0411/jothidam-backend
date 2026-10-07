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

Schema horoscopegen-ai/2 only adds to schema 1: new sheets, and new columns
at the end of old sheets. It adds what a reader had to work out before: the
dasa and antaram levels as tables, what a transiting planet touches, the
faster planets and stations, one row of facts per period (AI_PeriodFacts),
what supports and weakens each topic (AI_TopicPromise), where dasa and transit
overlap (AI_TopicWindows), a short copy for a reader who cannot load every
sheet (AI_Brief), and what only the user knows, when they choose to give it
(clean_extras: birth-time uncertainty, life facts and past events).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from itertools import combinations

import swisseph as swe

import astro_engine as A
from astro_engine import (COMBUST_ORB, DASA_ORDER, DASA_YRS, EXALT_SIGN, NAKS, OWN_SIGNS, PLANETS,
                          RASIS, SIGN_LORDS, VARGAS, VARGA_KEYS, YEAR_DAYS, angle_diff, norm,
                          varga_part, varga_sign)

SCHEMA = 'horoscopegen-ai/2'

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
                          'Rahu': (3, 6, 11), 'Ketu': (3, 6, 11),
                          'Sun': (3, 6, 10, 11), 'Mars': (3, 6, 11), 'Mercury': (2, 4, 6, 8, 10, 11),
                          'Venus': (1, 2, 3, 4, 5, 8, 9, 11, 12)}
SATURN_FROM_MOON = {12: 'sade sati - 1st phase', 1: 'sade sati - 2nd phase', 2: 'sade sati - 3rd phase',
                    8: 'ashtama', 4: 'ardhashtama', 7: 'kantaka', 10: 'kantaka'}

# Largest daily motion in degrees, with a margin: how far a body can get in a day.
_VMAX = {'Saturn': 0.16, 'Jupiter': 0.28, 'mean': 0.07, 'true': 0.45,
         'Mars': 0.9, 'Sun': 1.15, 'Mercury': 2.5, 'Venus': 1.45}
TRANSIT_MIN_STEP = 1.0          # days
TRANSIT_TOL = 0.5 / 86400.0     # days: entries are bisected to half a second
TRANSIT_YEARS_AHEAD = 10
PRATYANTAR_YEARS_BACK = 1
PRATYANTAR_YEARS_AHEAD = 10
ANTARAM_FACTS_YEARS_BACK = 1    # antaram rows of AI_PeriodFacts: from this many years before the report date
# Faster bodies in AI_TransitsFast: body, years before the report date, years after, search margin in days
# (longer than the longest stay of that body in one sign, so every listed stay has both its ends).
FAST_BODIES = (('Mars', 2, 10, 400), ('Sun', 1, 2, 45), ('Mercury', 1, 2, 120), ('Venus', 1, 2, 200))
STATION_BODIES = ('Mars', 'Jupiter', 'Saturn')
STATION_YEARS_BACK = 1
STATION_STEP = 5.0              # days: the daily motion keeps its sign for far longer than this
STATION_TOL = 20.0 / 86400.0    # days: stations are bisected to 20 seconds
WINDOW_MIN_BINDUS = 4           # own bindus a transit sign needs to count as a layer in AI_TopicWindows
WINDOW_MIN_LAYERS = 2           # rows of AI_TopicWindows have at least this many layers
BRIEF_WINDOWS = 3               # windows per topic repeated in AI_Brief
SAV_STRONG, SAV_WEAK = 30, 24   # bindus of a house: supports from 30, weakens up to 24
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
    ('Mother', (4,), ('Moon',), ('D12',), ()),
    ('Father', (9,), ('Sun',), ('D12',), ()),
]
NO_PROMISE = ('Strain (general)',)      # topics left out of AI_TopicPromise

# The nine taras, counted from the janma nakshatra, and their classical labels
TARA_NAMES = ('Janma', 'Sampat', 'Vipat', 'Kshema', 'Pratyari', 'Sadhaka', 'Vadha', 'Mitra', 'Parama Mitra')
TARA_LABELS = ('mixed', 'favourable', 'unfavourable', 'favourable', 'unfavourable', 'favourable',
               'unfavourable', 'favourable', 'favourable')

NATURAL_MALEFICS = ('Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu')
GOOD_DIGNITY = ('Exalted', 'Moolatrikona', 'Own sign', 'Great friend', 'Friend')
OWN_DIGNITY = ('Exalted', 'Moolatrikona', 'Own sign')

# Optional facts only the user knows (request field "life"). Nothing here is computed.
MARITAL_STATUS = ('single', 'married', 'other')
WORK_TYPES = ('employed', 'self-employed', 'business', 'student', 'homemaker', 'retired', 'not working')
EVENT_TOPIC = {'marriage': 'Marriage', 'child born': 'Children', 'job change': 'Job and career',
               'own business started': 'Business', 'moved abroad': 'Abroad / onsite',
               'returned from abroad': 'Abroad / onsite', 'home bought': 'Home and vehicle',
               'higher study': 'Education'}
MAX_EVENTS = 10
MAX_COUNT = 20
MAX_TOB_UNCERTAINTY_MIN = 120
LIFE_FIELDS = (
    ('marital_status', 'one of: ' + ', '.join(MARITAL_STATUS)),
    ('marriage_year', 'calendar year'),
    ('children_count', 'number of children'),
    ('first_child_birth_year', 'calendar year'),
    ('elder_siblings', 'number of elder brothers and sisters'),
    ('younger_siblings', 'number of younger brothers and sisters'),
    ('work_type', 'one of: ' + ', '.join(WORK_TYPES)),
    ('lives_abroad', 'yes / no: lives outside the country of birth'),
)
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
     'report date to 10 years after, so that it ends with the transit tables. AI_DasaPeriods has one row '
     'per dasa and AI_Antaram one row per antaram (3rd level) for the whole life.'),
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
     'significator only when the gender is female. rank_in_topic: 1 for the highest score of that topic '
     'over all bhuktis, 2 for the next different score, and so on. in_top_quarter: yes when fewer than a '
     'quarter of all bhuktis have a higher score for that topic.'),
    ('Dharma-Karmadhipati yoga', 'The lord of the 9th and the lord of the 10th joined by conjunction, mutual '
     'aspect or exchange of signs. When one planet owns both houses the row says so and is marked found.'),
    ('Weakening factors of a yoga', 'For a yoga that is found, the facts about its planets that tradition reads '
     'as reducing it: combust; debilitated (with "cancelled" when a neecha bhanga condition is met); placed '
     'in house 6, 8 or 12 (not listed for the Viparita yogas, which need that placement); in the sign of an '
     'enemy or great enemy. Empty for doshas, Kemadruma, Guru-Chandala, Kala Sarpa and neecha bhanga rows.'),
    ('Tara', 'Nine taras counted from the janma nakshatra and repeated three times: 1 Janma, 2 Sampat, 3 Vipat, '
     '4 Kshema, 5 Pratyari, 6 Sadhaka, 7 Vadha, 8 Mitra, 9 Parama Mitra. Labels: 2, 4, 6, 8, 9 favourable; '
     '3, 5, 7 unfavourable; 1 mixed. Two counts are given for a period lord: tara_of_lordship = the tara '
     'of the nakshatras that planet rules (the order of the dasa lords starting from the lord of the janma '
     'nakshatra); tara_of_position = the tara of the nakshatra that planet occupies.'),
    ('Transits of the faster planets', 'AI_TransitsFast: sign entries of Mars from 2 years before the report date '
     'to 10 years after, and of the Sun, Mercury and Venus from 1 year before to 2 years after, found the '
     'same way as the slow planets. Classical gochara from the natal Moon: Sun favourable in 3, 6, 10, 11; '
     'Mars in 3, 6, 11; Mercury in 2, 4, 6, 8, 10, 11; Venus in 1, 2, 3, 4, 5, 8, 9, 11, 12. Vedha is not '
     'applied. The Moon is not listed.'),
    ('Transit aspects', 'houses_aspected_from_lagna, natal_points_in_sign and natal_points_aspected use the same '
     'full aspects by whole sign as the birth chart (Mars 4, 7, 8; Jupiter 5, 7, 9; Saturn 3, 7, 10; the '
     'others the 7th), counted from the sign the planet transits.'),
    ('Stations', 'AI_Stations: the moments the daily motion in longitude of Mars, Jupiter or Saturn is zero, from '
     '1 year before the report date to 10 years after. retrograde = it turns backward there, direct = it '
     'turns forward. Found by stepping 5 days and bisecting to 20 seconds, then cut to the minute. The '
     'motion changes slowly at a station, so a small difference between ephemerides moves this moment by '
     'many minutes: read it as a date.'),
    ('Period facts', 'AI_PeriodFacts repeats, for the lord of every bhukti (whole life) and of every antaram '
     '(1 year before the report date to 10 years after), what the other sheets say about that planet, on '
     'one row. D9 and D10 dignity are by sign and so do not depend on the lagna of those charts. '
     'lord_tied_topics: the topics for which that planet owns a key house, sits in a key house or is a '
     'significator (conditions a, b, d of the topic scores).'),
    ('Topic promise', 'AI_TopicPromise: a fixed list of tests, the same for every chart; a rule-based count, not a '
     'prediction. For each key house: its lord in a kendra or trikona (1, 4, 5, 7, 9, 10) supports, in 6, '
     '8 or 12 weakens; its lord exalted, in moolatrikona or in its own sign supports; its lord debilitated '
     'with no neecha bhanga, or combust, weakens; Jupiter, Venus or Mercury in the house or aspecting it '
     'supports; the Sun, Mars, Saturn, Rahu or Ketu in the house weakens, but supports when the house is '
     '3, 6 or 11, or when the Sun, Mars or Saturn is there in its own sign, moolatrikona or exaltation; '
     '30 or more bindus support, 24 or fewer weaken. A planet that owns two key houses is tested once as '
     'lord. For each significator that is not the lord of a key house: exalted, '
     'moolatrikona, own sign, great friend or friend and not debilitated supports; in house 6, 8 or 12 '
     'weakens; debilitated with no neecha bhanga, or combust, weakens (dignity, debilitation and '
     'combustion apply to the seven planets only). A Raja, Dhana, Dharma-Karmadhipati or Parivartana yoga '
     'between the lords of two key houses supports. The topic Strain (general) is left out: its houses '
     'are 6, 8 and 12, for which these tests do not fit.'),
    ('Topic windows', 'AI_TopicWindows: rule-based overlap, not a prediction. The 10 years after the report date '
     'are cut at every change of antaram and at every sign change of Jupiter or Saturn. For each piece '
     'and topic four layers are tested: bhukti = the bhukti is in the top quarter of that topic\'s scores; '
     'antaram = the antaram lord owns a key house, sits in one or is a significator; jupiter = Jupiter '
     'transits or aspects a key house from a sign with 4 or more bindus in its own Bhinnashtakavarga; '
     'saturn = the same for Saturn. A piece counts when at least two layers hold; pieces that follow one '
     'another inside one bhukti with the same layers are joined into one window. '
     'key_houses_reached_by_both is the double transit (modern method) restricted to the key houses.'),
    ('Birth-time sensitivity', 'house_if_lagna_earlier and house_if_lagna_later in AI_Vargas count the house of a '
     'point from the lagna that chart would have if the birth were earlier or later than the margins in '
     'AI_VargaLagnas. The point itself is not recomputed, so for the Moon in the finest charts this is an '
     'approximation. dasa_shift_days_per_minute in AI_Facts: every Vimshottari date recomputed for a birth '
     '60 seconds later; negative = the dates move earlier.'),
    ('Life facts', 'AI_LifeFacts and AI_LifeEvents hold what the user chose to enter (request field "life"): they '
     'are not computed and not checked against the chart. AI_EventCheck lists, for each event entered, the '
     'bhuktis that overlap that calendar year with their score for the matching topic, and where Jupiter '
     'and Saturn were. Event to topic: marriage - Marriage; child born - Children; job change - Job and '
     'career; own business started - Business; moved abroad, returned from abroad - Abroad / onsite; home '
     'bought - Home and vehicle; higher study - Education.'),
    ('Brief', 'AI_Brief repeats values of the other AI sheets in a short form; the source column names the sheet. '
     'A value written as "a=1; b=2" holds several cells of one row of that sheet. Lines in the section '
     '"As of the report date" were true at report_datetime_local only. Windows per topic: the first three '
     'by start date among those with three or more layers; when there are fewer, the earliest with two.'),
]

NOT_IN_FILE = [
    'Shadbala and Bhava bala', 'Planet latitude and declination; stations of Mercury and Venus',
    'Chara karakas, Karakamsa and arudha padas', 'Special lagnas (Bhava, Hora, Ghati, Indu)',
    'Gulika and the other upagrahas (Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu)',
    'Avasthas, Pushkara and gandanta flags', 'Yogini dasa and any dasa other than Vimshottari',
    'Sookshma dasa (5th level) and deeper', 'Ashtakavarga reductions (sodhana) and kakshya transits',
    'Transits of the Moon through the signs (only its position on the report date is given); vedha',
    'Rasi (Jaimini) aspects and 5th / 9th aspects of Rahu and Ketu',
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


# ── OPTIONAL INPUT: what only the user knows ──────────────────────────────────

def _whole(value, name, low, high):
    """An optional whole number between low and high, or None."""
    if value in (None, ''):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise A.InputError(f'"{name}" must be a number.')
    if number != int(number) or not low <= number <= high:
        raise A.InputError(f'"{name}" must be a whole number from {low} to {high}.')
    return int(number)


def _choice(value, name, allowed):
    if value in (None, ''):
        return None
    text = str(value).strip().lower()
    if text not in allowed:
        raise A.InputError(f'"{name}" must be one of: {", ".join(allowed)}.')
    return text


def clean_extras(raw=None):
    """
    Check the optional inputs that enrich() takes beside compute()'s result and
    return them in one fixed shape. Raises astro_engine.InputError on a bad value.

    raw: {'tob_uncertainty_min': minutes, 'coordinates_source': text, 'life': {...}}
    (all optional). life holds the LIFE_FIELDS and 'events': [{'type', 'year'}].
    Years are checked against the birth and report dates in enrich().
    """
    raw = raw or {}
    if not isinstance(raw, dict):
        raise A.InputError('The optional inputs must be an object.')
    unc = raw.get('tob_uncertainty_min')
    if unc in (None, ''):
        unc = None
    else:
        try:
            unc = float(unc)
        except (TypeError, ValueError):
            raise A.InputError('"tobUncertaintyMin" must be a number.')
        if not 0 <= unc <= MAX_TOB_UNCERTAINTY_MIN:
            raise A.InputError(f'"tobUncertaintyMin" must be between 0 and {MAX_TOB_UNCERTAINTY_MIN}.')
    source = raw.get('coordinates_source')
    source = str(source)[:40] if source not in (None, '') else None
    life_in = raw.get('life') or {}
    if not isinstance(life_in, dict):
        raise A.InputError('"life" must be an object.')
    yes_no = life_in.get('lives_abroad')
    if isinstance(yes_no, bool):
        yes_no = 'yes' if yes_no else 'no'
    life = {
        'marital_status': _choice(life_in.get('marital_status'), 'marital_status', MARITAL_STATUS),
        'marriage_year': _whole(life_in.get('marriage_year'), 'marriage_year', 1, 9999),
        'children_count': _whole(life_in.get('children_count'), 'children_count', 0, MAX_COUNT),
        'first_child_birth_year': _whole(life_in.get('first_child_birth_year'), 'first_child_birth_year', 1, 9999),
        'elder_siblings': _whole(life_in.get('elder_siblings'), 'elder_siblings', 0, MAX_COUNT),
        'younger_siblings': _whole(life_in.get('younger_siblings'), 'younger_siblings', 0, MAX_COUNT),
        'work_type': _choice(life_in.get('work_type'), 'work_type', WORK_TYPES),
        'lives_abroad': _choice(yes_no, 'lives_abroad', ('yes', 'no')),
    }
    events_in = life_in.get('events') or []
    if not isinstance(events_in, (list, tuple)):
        raise A.InputError('"events" must be a list.')
    if len(events_in) > MAX_EVENTS:
        raise A.InputError(f'At most {MAX_EVENTS} events can be given.')
    events = []
    for item in events_in:
        if not isinstance(item, dict):
            raise A.InputError('Each event must be an object with "type" and "year".')
        kind = _choice(item.get('type'), 'event type', tuple(EVENT_TOPIC))
        year = _whole(item.get('year'), 'event year', 1, 9999)
        if kind is None or year is None:
            raise A.InputError('Each event needs a "type" and a "year".')
        events.append({'type': kind, 'year': year})
    return {'tob_uncertainty_min': unc, 'coordinates_source': source, 'life': life, 'events': events}


def check_years(c):
    """Years the user entered must lie between the birth year and the report year."""
    low, high = c.birth.year, max(c.now.year, c.birth.year)
    years = [(k, v) for k, v in c.extras['life'].items() if k.endswith('_year') and v is not None]
    years += [(f"event \"{e['type']}\"", e['year']) for e in c.extras['events']]
    for name, year in years:
        if not low <= year <= high:
            raise A.InputError(f'The year given for {name} must be between {low} and {high}.')


# ── CONTEXT: everything derived once ──────────────────────────────────────────

class Ctx:
    """Derived facts about one chart, shared by the table builders."""

    def __init__(self, res, now=None, extras=None):
        m, v = res['meta'], res['vedic']
        self.extras = clean_extras(extras)
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
        self.nak = {n: p['nak'] for n, p in self.points.items()}
        self.janma_nak = self.nak['Moon']
        self.janma_lord = A.NAK_LORDS[self.janma_nak]
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

    def tara_of_lordship(self, planet):
        """1-9: the tara of the nakshatras this planet rules, counted from the janma nakshatra."""
        return (DASA_ORDER.index(planet) - DASA_ORDER.index(self.janma_lord)) % 9 + 1

    def tara_of_position(self, point):
        """1-9: the tara of the nakshatra this point occupies, counted from the janma nakshatra."""
        return (self.nak[point] - self.janma_nak) % 9 + 1

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
        ('civil_weekday', A.WEEKDAYS[c.birth.weekday()], 'weekday of the civil date of birth; "weekday" above is '
                                                         'the Vedic day, sunrise to sunrise, and can differ'),
        ('coordinates_source', c.extras['coordinates_source'],
         'entered = latitude and longitude came with the request; looked up = found from the place name; '
         'empty when not known'),
        ('birth_time_uncertainty_minutes', c.extras['tob_uncertainty_min'],
         'how far the birth time may be off, as entered by the user; empty when not given'),
        ('dasa_shift_days_per_minute', dasa_shift(c),
         'days by which every Vimshottari date moves when the birth is one minute later; negative = earlier'),
    ]
    return [{'key': k, 'value': val, 'note': note or None} for k, val, note in rows]


def dasa_shift(c):
    """
    Days by which the Vimshottari dates move for a birth 60 seconds later, by
    recomputing the Moon. None when the Moon changes nakshatra in that minute.
    """
    jd = A.julian_day(c.meta['ut_dt'])
    moon = [A._positions(jd + d, c.lat, c.lon, c.sid_mode, c.node)['pts']['Moon'][0] for d in (0.0, 60.0 / 86400.0)]
    if A.get_nak(moon[0]) != A.get_nak(moon[1]):
        return None
    part = [(norm(x) % A.NAK_SIZE) / A.NAK_SIZE for x in moon]
    years = DASA_YRS[A.NAK_LORDS[A.get_nak(moon[0])]]
    return round(60.0 / 86400.0 - years * (part[1] - part[0]) * YEAR_DAYS, 3)


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
            'combust_margin_deg': (_r6(angle_diff(p['lon'], c.points['Sun']['lon']) - orb)
                                   if orb is not None else None),
            'bhava_differs_from_whole_sign': _yes(p['bhava'] != c.house[n]),
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
            sign_e, sign_l = c.margins[key][-1][1], c.margins[key][1][1]
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
                'house_if_lagna_earlier': house_from(s, sign_e) if sign_e is not None and n != 'Lagna' else None,
                'house_if_lagna_later': house_from(s, sign_l) if sign_l is not None and n != 'Lagna' else None,
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
    unc = c.extras['tob_uncertainty_min']
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
            'lagna_uncertain_for_stated_accuracy': (
                NOT_GIVEN if unc is None else _yes(bool(small) and min(small) < unc * 60.0)),
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

    members = []                                    # planets of each row, in step with rows

    def add(name, status, rule, planets=(), houses=(), note=''):
        rows.append({'yoga': name, 'status': status, 'rule': rule, 'planets': _join(planets),
                     'houses': _join(houses), 'note': note or None})
        members.append(list(planets))

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

    # Dharma-Karmadhipati: lords of the 9th and the 10th
    l9, l10 = c.house_lord[9], c.house_lord[10]
    rule = 'The lord of the 9th and the lord of the 10th joined by conjunction, mutual aspect or exchange of signs'
    if l9 == l10:
        add('Dharma-Karmadhipati yoga', 'found', rule, [l9], [house[l9]],
            f'{l9} owns both the 9th and the 10th house and is in house {house[l9]}')
    else:
        links = c.links(l9, l10)
        add('Dharma-Karmadhipati yoga', 'found' if links else 'not found', rule, [l9, l10],
            sorted({house[l9], house[l10]}),
            f'{l9} (lord of 9) in house {house[l9]}; {l10} (lord of 10) in house {house[l10]}; '
            + (f"link: {', '.join(links)}" if links else 'not joined'))

    # What reduces each yoga that is found, and who takes part in what
    c.yoga_members = []
    for row, planets in zip(rows, members):
        row['weakening_factors'] = None
        if row['status'] != 'found':
            continue
        c.yoga_members.append((row['yoga'], planets))
        name = row['yoga']
        if any(word in name for word in ('dosha', 'Neecha bhanga', 'Kemadruma', 'Guru-Chandala', 'Kala Sarpa')):
            continue
        facts = []
        for p in planets:
            if c.combust(p):
                facts.append(f'{p} combust')
            if c.debilitated(p):
                facts.append(f'{p} debilitated' + (' (cancelled)' if c.neecha_bhanga.get(p) else ''))
            if house[p] in DUSTHANA and 'Viparita' not in name:
                facts.append(f'{p} in house {house[p]}')
            if p in SEVEN and c.dignity['D1'][p][0] in ('Enemy', 'Great enemy'):
                facts.append(f"{p} in an enemy's sign")
        row['weakening_factors'] = _join(facts)
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


def _age(c, moment):
    return round((moment - c.birth).total_seconds() / 86400.0 / YEAR_DAYS, 3)


def _tara_cols(c, prefix, number):
    return {f'{prefix}_no': number, prefix: TARA_NAMES[number - 1], f'{prefix}_label': TARA_LABELS[number - 1]}


def _dasa_periods(c):
    rows = []
    for d in c.v['dasa']['dasas']:
        lord = d['lord']
        row = {'dasa_lord': lord, 'start_local': _sec(d['start']), 'end_local': _sec(d['end']),
               'age_at_start_years': _age(c, d['start']), 'age_at_end_years': _age(c, d['end'])}
        row.update(_lord_cols(c, 'dasa_lord', lord))
        row['dasa_lord_functional_nature'] = c.nature.get(lord)
        row['dasa_lord_star_lord'] = c.points[lord]['star_lord']
        row.update(_tara_cols(c, 'dasa_lord_tara_of_lordship', c.tara_of_lordship(lord)))
        rows.append(row)
    return rows


def antarams(c):
    """(dasa row, bhukti row, antaram row) for every antaram in the Vedic dasa tree."""
    return [(d, b, a) for d in c.v['dasa']['dasas'] for b in d['sub'] for a in b['sub']]


def _antaram(c):
    return [{'dasa_lord': d['lord'], 'bhukti_lord': b['lord'], 'antaram_lord': a['lord'],
             'start_local': _sec(a['start']), 'end_local': _sec(a['end']),
             'days': round((a['end'] - a['start']).total_seconds() / 86400.0, 3)}
            for d, b, a in antarams(c)]


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
    c.fast_window_utc = {}
    for body, back, ahead, margin in FAST_BODIES:
        lo, hi = jd_now - back * YEAR_DAYS, jd_now + ahead * YEAR_DAYS
        rows = stays(body, lo - margin, hi + margin, c.sid_mode, c.node)
        for r in rows:
            for k in ('entry', 'exit'):
                utc = _minute(jd_to_utc(r[k])) if r[k] is not None else None
                r[k + '_utc'] = utc
                r[k + '_local'] = utc + off if utc else None
        data[body] = rows
        c.fast_window_utc[body] = (jd_to_utc(lo), jd_to_utc(hi))
    c.station_window = (jd_now - STATION_YEARS_BACK * YEAR_DAYS, jd_now + TRANSIT_YEARS_AHEAD * YEAR_DAYS)
    return data


def _overlaps(row, lo_utc, hi_utc):
    return ((row['entry_utc'] is None or row['entry_utc'] < hi_utc)
            and (row['exit_utc'] is None or row['exit_utc'] > lo_utc))


def transit_reach(c, planet, s):
    """What a planet touches from sign s: houses it aspects, natal points in s, natal points aspected."""
    asp = aspected_signs(planet, s)
    points = [n for n in c.names if n in c.sign]
    return {
        'houses_aspected_from_lagna': _join(sorted(house_from(x, c.lagna_sign) for x in asp)),
        'natal_points_in_sign': _join(n for n in points if c.sign[n] == s),
        'natal_points_aspected': _join(n for n in points if c.sign[n] in asp),
    }


def _transit_row(c, planet, s, st):
    fm = house_from(s, c.moon_sign)
    row = {
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
        'own_bav_bindus': c.bav[planet][s] if planet in SEVEN else None,
        'result_from_moon': 'favourable' if fm in TRANSIT_GOOD_FROM_MOON[planet] else 'unfavourable',
    }
    row.update(transit_reach(c, planet, s))
    return row


def _transits_fast(c):
    rows = []
    for planet, _, _, _ in FAST_BODIES:
        lo, hi = c.fast_window_utc[planet]
        rows.extend(_transit_row(c, planet, st['sign'], st) for st in c.transit[planet] if _overlaps(st, lo, hi))
    return rows


def stations(body, jd_start, jd_end, sid_mode, step=STATION_STEP):
    """
    Stations of a planet between two Julian days (UT), as (jd, kind, sidereal
    longitude): kind is 'retrograde' where the daily motion turns negative and
    'direct' where it turns positive again. The motion is sampled every `step`
    days and each change of its sign is bisected.
    """
    pid = A.SWE_IDS[body]
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = []
    with A._SWE_LOCK:
        swe.set_sid_mode(sid_mode)

        def state(jd):
            xx = swe.calc_ut(jd, pid, flags)[0]
            return norm(xx[0]), xx[3]

        jd = jd_start
        backward = state(jd)[1] < 0
        while jd < jd_end:
            nxt = min(jd + step, jd_end)
            if (state(nxt)[1] < 0) != backward:
                lo, hi = jd, nxt                    # old direction at lo, new direction at hi
                while hi - lo > STATION_TOL:
                    mid = (lo + hi) / 2.0
                    if (state(mid)[1] < 0) == backward:
                        lo = mid
                    else:
                        hi = mid
                backward = not backward
                out.append((hi, 'retrograde' if backward else 'direct', state(hi)[0]))
            jd = nxt
    return out


def _stations(c):
    off = timedelta(hours=c.offset)
    rows = []
    for planet in STATION_BODIES:
        for jd, kind, lon in stations(planet, c.station_window[0], c.station_window[1], c.sid_mode):
            utc = _minute(jd_to_utc(jd))
            s = A.get_rasi(lon)
            rows.append({
                'planet': planet, 'station': kind, 'moment_local': utc + off, 'moment_utc': utc,
                'longitude_deg': _r6(lon), 'sign_no': s + 1, 'sign': RASIS[s],
                'deg_in_sign_text': A.fmt_sign_dms(lon),
                'house_from_lagna': house_from(s, c.lagna_sign), 'house_from_moon': house_from(s, c.moon_sign),
            })
    return rows


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
            reach = transit_reach(c, planet, s)
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
                **reach,
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


def score_ranks(scores):
    """
    For each score of one topic: (rank, in the top quarter). Rank 1 is the
    highest score, 2 the next different score, and so on. A score is in the
    top quarter when fewer than a quarter of all the scores are higher.
    """
    distinct = sorted(set(scores), reverse=True)
    out = []
    for score in scores:
        higher = sum(1 for x in scores if x > score)
        out.append((distinct.index(score) + 1, higher < len(scores) / 4.0))
    return out


def _topic_scores(c):
    letters = {(lord, t[0]): topic_letters(c, lord, *t) for lord in PLANETS for t in TOPICS}
    c.letters = letters
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
    for topic in {r['topic'] for r in rows}:
        mine = [r for r in rows if r['topic'] == topic]
        for r, (rank, top) in zip(mine, score_ranks([x['relevance_score_not_a_prediction'] for x in mine])):
            r['rank_in_topic'] = rank
            r['in_top_quarter'] = _yes(top)
    c.score_by, c.top_quarter = {}, {}
    for r in rows:
        key = (r['dasa_lord'], r['bhukti_lord'], r['start_local'])
        c.score_by[key + (r['topic'],)] = r
        c.top_quarter.setdefault(key, [])
        if r['in_top_quarter'] == 'yes':
            c.top_quarter[key].append(r['topic'])
    return rows


# ── PERIODS: one row per bhukti and antaram ───────────────────────────────────

def lord_tied_topics(c, lord):
    """Topics for which a planet owns a key house, sits in one or is a significator (letters a, b, d)."""
    return [t[0] for t in TOPICS if set(c.letters[(lord, t[0])]) & set('abd')]


def _relation(c, a, b):
    """Compound relationship of planet a towards planet b; None when either is a node."""
    if a == b:
        return 'same planet'
    if a in SEVEN and b in SEVEN:
        return c.compound[a][b]
    return None


def _period_cols(c, lord, dasa_lord, bhukti_lord=None):
    """Everything the other sheets say about the lord of a period, for one row of AI_PeriodFacts."""
    seven = lord in SEVEN
    p, s = c.points[lord], c.sign[lord]
    label, debil = c.dignity['D1'][lord] if seven else (None, None)
    star = p['star_lord']
    row = {
        'period_lord': lord,
        'houses_owned': _join(c.owned[lord]),
        'house': c.house[lord],
        'sign': RASIS[s],
        'dignity': label,
        'debilitated': _yes(debil) if seven else None,
        'debilitation_cancelled_by': _join(c.neecha_bhanga.get(lord, [])) if debil else None,
        'combust': _yes(p['combust']) if lord in COMBUST_ORB else None,
        'retrograde': _yes(p['retro']) if seven else None,
        'functional_nature': c.nature.get(lord),
        'vimsopaka_shodasavarga': c.vimsopaka[lord]['shodasavarga'] if seven else None,
        'own_bav_bindus_in_sign_occupied': c.bav[lord][s] if seven else None,
    }
    for key in ('D9', 'D10'):
        k = key.lower()
        row[f'{k}_sign'] = RASIS[c.vargas[key]['signs'][lord]]
        row[f'{k}_dignity'] = c.dignity[key][lord][0] if seven else None
        row[f'{k}_debilitated'] = _yes(c.dignity[key][lord][1]) if seven else None
    row.update({
        'sign_lord': SIGN_LORDS[s],
        'sign_lord_house': c.house[SIGN_LORDS[s]],
        'star_lord': star,
        'star_lord_houses_owned': _join(c.owned[star]),
        'star_lord_house': c.house[star],
        'place_from_dasa_lord': house_from(s, c.sign[dasa_lord]),
        'relation_to_dasa_lord': _relation(c, lord, dasa_lord),
        'relation_of_dasa_lord': _relation(c, dasa_lord, lord),
        'place_from_bhukti_lord': house_from(s, c.sign[bhukti_lord]) if bhukti_lord else None,
    })
    row.update(_tara_cols(c, 'tara_of_lordship', c.tara_of_lordship(lord)))
    row.update(_tara_cols(c, 'tara_of_position', c.tara_of_position(lord)))
    row['yogas'] = _join(name for name, planets in c.yoga_members if lord in planets)
    row['lord_tied_topics'] = _join(lord_tied_topics(c, lord))
    return row


def _period_facts(c):
    lo = c.now - timedelta(days=ANTARAM_FACTS_YEARS_BACK * YEAR_DAYS)
    hi = c.now + timedelta(days=TRANSIT_YEARS_AHEAD * YEAR_DAYS)
    rows = []
    for d, b in bhuktis(c):
        top = _join(c.top_quarter[(d['lord'], b['lord'], _sec(b['start']))])
        row = {'level': 'bhukti', 'dasa_lord': d['lord'], 'bhukti_lord': b['lord'], 'antaram_lord': None,
               'start_local': _sec(b['start']), 'end_local': _sec(b['end']),
               'age_at_start_years': _age(c, b['start'])}
        row.update(_period_cols(c, b['lord'], d['lord']))
        row['bhukti_top_quarter_topics'] = top
        rows.append(row)
        for a in b['sub']:
            if a['end'] <= lo or a['start'] >= hi:
                continue
            row = {'level': 'antaram', 'dasa_lord': d['lord'], 'bhukti_lord': b['lord'], 'antaram_lord': a['lord'],
                   'start_local': _sec(a['start']), 'end_local': _sec(a['end']),
                   'age_at_start_years': _age(c, a['start'])}
            row.update(_period_cols(c, a['lord'], d['lord'], b['lord']))
            row['bhukti_top_quarter_topics'] = top
            rows.append(row)
    return rows


# ── TOPIC PROMISE: what supports and what weakens ─────────────────────────────

_DIGNITY_TEXT = {'Exalted': 'exalted', 'Moolatrikona': 'in moolatrikona', 'Own sign': 'in its own sign',
                 'Great friend': "in a great friend's sign", 'Friend': "in a friend's sign"}
PAIR_YOGAS = ('Raja yoga', 'Dhana yoga', 'Dharma-Karmadhipati yoga', 'Parivartana yoga')


def _topic_promise(c):
    rows = []
    for topic, houses, sig, vargas, kp in TOPICS:
        if topic in NO_PROMISE:
            continue
        first = len(rows)

        def add(subject, factor, side, fact):
            rows.append({'topic': topic, 'row_type': 'factor', 'subject': subject, 'factor': factor,
                         'side': side, 'fact': fact, 'supports_count': None, 'weakens_count': None})

        lords = {}
        for h in houses:
            lords.setdefault(c.house_lord[h], []).append(h)
        for lord, owned in lords.items():
            sub = f'lord of house {_join(owned)}'
            lh = c.house[lord]
            if lh in KENDRA or lh in TRIKONA:
                add(sub, 'lord in a kendra or trikona', 'supports', f'{lord} is in house {lh}')
            elif lh in DUSTHANA:
                add(sub, 'lord in house 6, 8 or 12', 'weakens', f'{lord} is in house {lh}')
            label, debil = c.dignity['D1'][lord]
            if label in OWN_DIGNITY:
                add(sub, 'lord exalted, in moolatrikona or in its own sign', 'supports',
                    f'{lord} is {_DIGNITY_TEXT[label]} in {RASIS[c.sign[lord]]}')
            if debil and not c.neecha_bhanga.get(lord):
                add(sub, 'lord debilitated, not cancelled', 'weakens',
                    f'{lord} is debilitated in {RASIS[c.sign[lord]]}')
            if c.combust(lord):
                add(sub, 'lord combust', 'weakens', f'{lord} is combust')
        for h in houses:
            s = c.house_sign[h]
            sub = f'house {h}'
            for p in NATURAL_BENEFICS:
                if c.sign[p] == s:
                    add(sub, 'Jupiter, Venus or Mercury in the house', 'supports', f'{p} is in house {h}')
                elif s in c.asp_signs[p]:
                    add(sub, 'Jupiter, Venus or Mercury aspects the house', 'supports', f'{p} aspects house {h}')
            for p in NATURAL_MALEFICS:
                if c.sign[p] == s:
                    strong = p in SEVEN and c.dignity['D1'][p][0] in OWN_DIGNITY
                    if strong:
                        add(sub, 'Sun, Mars or Saturn in the house in its own or exaltation sign', 'supports',
                            f"{p} is {_DIGNITY_TEXT[c.dignity['D1'][p][0]]} in house {h}")
                    elif h in (3, 6, 11):
                        add(sub, 'Sun, Mars, Saturn, Rahu or Ketu in house 3, 6 or 11', 'supports',
                            f'{p} is in house {h}')
                    else:
                        add(sub, 'Sun, Mars, Saturn, Rahu or Ketu in the house', 'weakens', f'{p} is in house {h}')
            if c.sav[s] >= SAV_STRONG:
                add(sub, f'{SAV_STRONG} or more bindus', 'supports', f'house {h} has {c.sav[s]} bindus')
            elif c.sav[s] <= SAV_WEAK:
                add(sub, f'{SAV_WEAK} or fewer bindus', 'weakens', f'house {h} has {c.sav[s]} bindus')
        for p in topic_significators(c, topic, sig):
            if p in lords:
                continue                            # already tested once, as lord of a key house
            sub = f'significator {p}'
            if p in SEVEN:
                label, debil = c.dignity['D1'][p]
                if label in GOOD_DIGNITY and not debil:
                    add(sub, 'significator in good dignity', 'supports',
                        f'{p} is {_DIGNITY_TEXT[label]} in {RASIS[c.sign[p]]}')
                if debil and not c.neecha_bhanga.get(p):
                    add(sub, 'significator debilitated, not cancelled', 'weakens',
                        f'{p} is debilitated in {RASIS[c.sign[p]]}')
                if c.combust(p):
                    add(sub, 'significator combust', 'weakens', f'{p} is combust')
            if c.house[p] in DUSTHANA:
                add(sub, 'significator in house 6, 8 or 12', 'weakens', f'{p} is in house {c.house[p]}')
        seen = set()
        for name, planets in c.yoga_members:
            if name in PAIR_YOGAS and len(planets) == 2 and all(p in lords for p in planets):
                if (name, tuple(planets)) in seen:
                    continue
                seen.add((name, tuple(planets)))
                add('yoga', 'yoga between lords of key houses', 'supports',
                    f'{name} between {planets[0]} and {planets[1]}')
        mine = rows[first:]
        rows.append({'topic': topic, 'row_type': 'total', 'subject': None, 'factor': None, 'side': None,
                     'fact': None, 'supports_count': sum(1 for r in mine if r['side'] == 'supports'),
                     'weakens_count': sum(1 for r in mine if r['side'] == 'weakens')})
    return rows


# ── TOPIC WINDOWS: where dasa and transit overlap ─────────────────────────────

def _key_houses_reached(c, body, sign, houses):
    """Key houses whose sign a transiting planet occupies or aspects from `sign`."""
    signs = {sign} | aspected_signs(body, sign)
    return sorted(h for h in houses if c.house_sign[h] in signs)


def _known_stays(c, body, lo, hi):
    return [st for st in c.transit[body]
            if st['entry_local'] is not None and st['exit_local'] is not None
            and st['exit_local'] > lo and st['entry_local'] < hi]


def _topic_windows(c):
    lo, hi = _sec(c.now), _sec(c.now + timedelta(days=TRANSIT_YEARS_AHEAD * YEAR_DAYS))
    periods = [(d, b, a) for d, b, a in antarams(c) if a['end'] > lo and a['start'] < hi]
    jupiter, saturn = _known_stays(c, 'Jupiter', lo, hi), _known_stays(c, 'Saturn', lo, hi)
    cuts = {lo, hi}
    for _, _, a in periods:
        cuts.update(_sec(t) for t in (a['start'], a['end']))
    for st in jupiter + saturn:
        cuts.update((st['entry_local'], st['exit_local']))
    cuts = sorted(t for t in cuts if lo <= t <= hi)

    def holder(items, moment, start, end):
        return next((x for x in items if start(x) <= moment < end(x)), None)

    def grow(items, value):
        if not items or items[-1] != value:
            items.append(value)

    open_rows = {}                                  # topic -> the window still growing
    rows = []
    for t0, t1 in zip(cuts, cuts[1:]):
        mid = t0 + (t1 - t0) / 2
        period = holder(periods, mid, lambda x: x[2]['start'], lambda x: x[2]['end'])
        j = holder(jupiter, mid, lambda x: x['entry_local'], lambda x: x['exit_local'])
        s = holder(saturn, mid, lambda x: x['entry_local'], lambda x: x['exit_local'])
        if period is None or j is None or s is None:
            open_rows.clear()                       # beyond the dasa tree or the transit search
            continue
        d, b, a = period
        bhukti_key = (d['lord'], b['lord'], _sec(b['start']))
        for order, (topic, houses, sig, vargas, kp) in enumerate(TOPICS):
            score = c.score_by[bhukti_key + (topic,)]
            jr = _key_houses_reached(c, 'Jupiter', j['sign'], houses)
            sr = _key_houses_reached(c, 'Saturn', s['sign'], houses)
            jb, sb = c.bav['Jupiter'][j['sign']], c.bav['Saturn'][s['sign']]
            layers = []
            if score['in_top_quarter'] == 'yes':
                layers.append('bhukti')
            if set(c.letters[(a['lord'], topic)]) & set('abd'):
                layers.append('antaram')
            if jr and jb >= WINDOW_MIN_BINDUS:
                layers.append('jupiter')
            if sr and sb >= WINDOW_MIN_BINDUS:
                layers.append('saturn')
            if len(layers) < WINDOW_MIN_LAYERS:
                open_rows.pop(topic, None)
                continue
            row = open_rows.get(topic)
            if row is None or row['end_local'] != t0 or row['_layers'] != layers or row['_bhukti'] != bhukti_key:
                row = {'_order': order, '_layers': layers, '_bhukti': bhukti_key, 'topic': topic, 'start_local': t0,
                       'layers_agreeing': len(layers), 'layers': _join(layers),
                       'dasa_lord': d['lord'], 'bhukti_lord': b['lord'],
                       'bhukti_score': score['relevance_score_not_a_prediction'],
                       'bhukti_rank_in_topic': score['rank_in_topic'],
                       '_antaram': [], '_jupiter': [], '_saturn': [], '_jr': set(), '_sr': set(), '_both': set()}
                open_rows[topic] = row
                rows.append(row)
            row['end_local'] = t1
            grow(row['_antaram'], a['lord'])
            grow(row['_jupiter'], (RASIS[j['sign']], jb))
            grow(row['_saturn'], (RASIS[s['sign']], sb))
            row['_jr'].update(jr)
            row['_sr'].update(sr)
            row['_both'].update(set(jr) & set(sr))
    rows.sort(key=lambda r: (r['_order'], r['start_local']))
    out = []
    for r in rows:
        out.append({
            'topic': r['topic'], 'start_local': r['start_local'], 'end_local': r['end_local'],
            'days': round((r['end_local'] - r['start_local']).total_seconds() / 86400.0, 3),
            'layers_agreeing': r['layers_agreeing'], 'layers': r['layers'],
            'dasa_lord': r['dasa_lord'], 'bhukti_lord': r['bhukti_lord'], 'antaram_lords': _join(r['_antaram']),
            'bhukti_score': r['bhukti_score'], 'bhukti_rank_in_topic': r['bhukti_rank_in_topic'],
            'jupiter_signs': _join(x[0] for x in r['_jupiter']),
            'jupiter_own_bindus': _join(x[1] for x in r['_jupiter']),
            'jupiter_key_houses_reached': _join(sorted(r['_jr'])),
            'saturn_signs': _join(x[0] for x in r['_saturn']),
            'saturn_own_bindus': _join(x[1] for x in r['_saturn']),
            'saturn_key_houses_reached': _join(sorted(r['_sr'])),
            'key_houses_reached_by_both': _join(sorted(r['_both'])),
            'label': 'rule-based overlap, not a prediction',
        })
    return out


# ── LIFE FACTS: entered by the user, not computed ─────────────────────────────

def _life_facts(c):
    life = c.extras['life']
    return [{'key': key, 'value': NOT_GIVEN if life[key] is None else life[key], 'note': note}
            for key, note in LIFE_FIELDS]


def _life_events(c):
    return [{'event_type': e['type'], 'year': e['year'], 'topic': EVENT_TOPIC[e['type']],
             'age_that_year': e['year'] - c.birth.year} for e in c.extras['events']]


def _event_check(c):
    topics = {t[0]: t for t in TOPICS}
    rows = []
    for e in c.extras['events']:
        topic, houses = EVENT_TOPIC[e['type']], topics[EVENT_TOPIC[e['type']]][1]
        y0, y1 = datetime(e['year'], 1, 1), datetime(e['year'] + 1, 1, 1)
        for d, b in bhuktis(c):
            start, end = max(b['start'], y0), min(b['end'], y1)
            if start >= end:
                continue
            score = c.score_by[(d['lord'], b['lord'], _sec(b['start']), topic)]
            tied = []
            for a in b['sub']:
                if a['end'] > start and a['start'] < end and set(c.letters[(a['lord'], topic)]) & set('abd'):
                    if a['lord'] not in tied:
                        tied.append(a['lord'])
            row = {
                'event_type': e['type'], 'year': e['year'], 'topic': topic,
                'dasa_lord': d['lord'], 'bhukti_lord': b['lord'],
                'overlap_start_local': _sec(start), 'overlap_end_local': _sec(end),
                'relevance_score_not_a_prediction': score['relevance_score_not_a_prediction'],
                'rank_in_topic': score['rank_in_topic'], 'in_top_quarter': score['in_top_quarter'],
                'antaram_lords_tied_to_topic': _join(tied),
            }
            for body in ('Jupiter', 'Saturn'):
                signs, reached = [], False
                for st in _known_stays(c, body, start, end):
                    text = f"{RASIS[st['sign']]} (house {house_from(st['sign'], c.lagna_sign)})"
                    if text not in signs:
                        signs.append(text)
                    reached = reached or bool(_key_houses_reached(c, body, st['sign'], houses))
                row[f'{body.lower()}_signs'] = _join(signs)
                row[f'{body.lower()}_reaches_key_house'] = _yes(reached)
            rows.append(row)
    return rows


# ── BRIEF: a short copy for a reader who cannot load every sheet ──────────────

def brief_text(value):
    """A cell as text inside a "column=value" line of AI_Brief."""
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def brief_line(row, columns):
    """"column=value; column=value" for the cells of one row that have a value."""
    return '; '.join(f'{col}={brief_text(row[col])}' for col in columns if row.get(col) is not None)


BRIEF_FACTS = (
    'name', 'gender', 'birth_date', 'birth_time', 'birth_place', 'latitude_deg', 'longitude_deg',
    'utc_offset_text', 'ayanamsha_name', 'node_type', 'lagna_sign', 'lagna_deg_in_sign', 'lagna_lord',
    'moon_sign', 'moon_nakshatra', 'moon_pada', 'moon_nakshatra_lord', 'sun_sign', 'paksha', 'tithi',
    'weekday', 'civil_weekday', 'birth_by_day_or_night', 'dasa_balance_lord', 'dasa_balance_years',
    'badhaka_house', 'badhaka_lord', 'birth_time_uncertainty_minutes', 'dasa_shift_days_per_minute',
    'report_datetime_local', 'age_at_report_years', 'ai_schema',
)
BRIEF_PLANET_COLUMNS = (
    'sign', 'deg_in_sign_text', 'nakshatra', 'pada', 'house_whole_sign', 'dignity', 'debilitated',
    'debilitation_cancelled_by', 'combust', 'retrograde', 'vimsopaka_shodasavarga', 'houses_owned',
    'functional_nature', 'conjunct_with', 'aspected_by', 'houses_aspected', 'd9_sign', 'vargottama',
)
BRIEF_HOUSE_COLUMNS = ('sign', 'lord', 'lord_house', 'lord_dignity', 'lord_debilitated', 'occupants_whole_sign',
                       'aspected_by', 'sav_bindus')
BRIEF_TRANSIT_COLUMNS = ('sign', 'entry_local', 'exit_local', 'house_from_lagna', 'house_from_moon',
                         'own_bav_bindus', 'sav_bindus', 'result_from_moon', 'saturn_from_moon',
                         'houses_aspected_from_lagna', 'natal_points_in_sign')
BRIEF_WINDOW_COLUMNS = ('start_local', 'end_local', 'layers_agreeing', 'layers', 'bhukti_lord', 'antaram_lords',
                        'jupiter_signs', 'saturn_signs', 'key_houses_reached_by_both')


def _brief(c, t):
    rows = []
    now = _sec(c.now)

    def add(section, key, value, source):
        rows.append({'section': section, 'key': key, 'value': value, 'source': source})

    def running(sheet, start='start_local', end='end_local'):
        return next((r for r in t[sheet] if r[start] is not None and r[end] is not None
                     and r[start] <= now < r[end]), None)

    add('About', 'how to read', 'A short copy of the other AI sheets, for a reader who cannot load them all. '
        'Every value is repeated from the sheet named under source. "a=1; b=2" holds several cells of one '
        'row of that sheet, under their column names. Counts, scores and windows are rule-based, not '
        'predictions. Go to the full sheets for anything not here.', 'AI_ReadMe')

    facts = {r['key']: r['value'] for r in t['AI_Facts']}
    for key in BRIEF_FACTS:
        if facts.get(key) is not None:
            add('Birth', key, facts[key], 'AI_Facts')

    uncertain = [r['chart'] for r in t['AI_VargaLagnas'] if r['lagna_uncertain'] == 'yes']
    add('Warnings', 'charts with lagna_uncertain = yes', _join(uncertain), 'AI_VargaLagnas')
    stated = [r['chart'] for r in t['AI_VargaLagnas'] if r['lagna_uncertain_for_stated_accuracy'] == 'yes']
    if c.extras['tob_uncertainty_min'] is not None:
        add('Warnings', 'charts with lagna_uncertain_for_stated_accuracy = yes', _join(stated), 'AI_VargaLagnas')
    add('Warnings', 'houses', 'Every house here is whole sign from the lagna. KP houses and KP dasa dates are a '
        'separate system and are not in this sheet.', 'AI_ReadMe')

    for r in t['AI_LifeFacts']:
        if r['value'] != NOT_GIVEN:
            add('Life facts (entered by the user)', r['key'], r['value'], 'AI_LifeFacts')
    for r in t['AI_LifeEvents']:
        add('Life facts (entered by the user)', 'event', brief_line(r, ('event_type', 'year', 'topic')), 'AI_LifeEvents')

    for r in t['AI_Planets']:
        if r.get('sign') is not None:
            add('Planets', r['point'], brief_line(r, BRIEF_PLANET_COLUMNS), 'AI_Planets')
    for r in t['AI_Houses']:
        add('Houses', f"house {r['house']}", brief_line(r, BRIEF_HOUSE_COLUMNS), 'AI_Houses')
    for r in t['AI_Yogas']:
        if r['status'] in ('found', 'cancelled'):
            add('Yogas', r['yoga'], brief_line(r, ('status', 'planets', 'houses', 'weakening_factors')), 'AI_Yogas')

    sec = 'As of the report date'
    add(sec, 'as_of', now, 'AI_Facts')
    add(sec, 'warning', 'The lines of this section were true at the report date only. For any other date compare '
        'the start and end dates in AI_DasaPeriods, AI_Dasa, AI_Antaram, AI_Pratyantar and AI_Transits '
        'with that date.', 'AI_ReadMe')
    bhukti_row = None
    for key, sheet, cols in (
            ('dasa', 'AI_DasaPeriods', ('dasa_lord', 'start_local', 'end_local')),
            ('bhukti', 'AI_Dasa', ('dasa_lord', 'bhukti_lord', 'start_local', 'end_local')),
            ('antaram', 'AI_Antaram', ('dasa_lord', 'bhukti_lord', 'antaram_lord', 'start_local', 'end_local')),
            ('pratyantar', 'AI_Pratyantar', ('dasa_lord', 'bhukti_lord', 'antaram_lord', 'pratyantar_lord',
                                            'start_local', 'end_local'))):
        r = running(sheet)
        if r is not None:
            add(sec, f'running {key}', brief_line(r, cols), sheet)
        if key == 'bhukti':
            bhukti_row = r
    later = [r for r in t['AI_Dasa'] if r['start_local'] > now][:3]
    for i, r in enumerate(later, start=1):
        add(sec, f'next bhukti {i}', brief_line(r, ('dasa_lord', 'bhukti_lord', 'start_local', 'end_local')), 'AI_Dasa')
    for planet in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
        mine = [r for r in t['AI_Transits'] if r['planet'] == planet]
        r = next((x for x in mine if x['entry_local'] is not None and x['exit_local'] is not None
                  and x['entry_local'] <= now < x['exit_local']), None)
        if r is None:
            continue
        add(sec, f'transit {planet}', brief_line(r, BRIEF_TRANSIT_COLUMNS), 'AI_Transits')
        nxt = next((x for x in mine if x['entry_local'] is not None and x['entry_local'] >= r['exit_local']), None)
        if nxt is not None:
            add(sec, f'next sign {planet}', brief_line(nxt, ('sign', 'entry_local', 'exit_local', 'house_from_lagna',
                                                             'house_from_moon', 'own_bav_bindus')), 'AI_Transits')
    spans = [r for r in t['AI_SadeSati'] if r['phase'] == 'sade sati - whole' and r['row_type'] == 'span'
             and r['start_local'] is not None and r['end_local'] is not None]
    span = next((r for r in spans if r['start_local'] <= now < r['end_local']), None)
    cols = ('cycle', 'start_local', 'end_local', 'saturn_sign', 'break_count')
    if span is not None:
        add(sec, 'sade sati span holding the report date', brief_line(span, cols), 'AI_SadeSati')
    else:
        add(sec, 'sade sati span holding the report date', 'none', 'AI_SadeSati')
        nxt = next((r for r in spans if r['start_local'] > now), None)
        if nxt is not None:
            add(sec, 'next sade sati span', brief_line(nxt, cols), 'AI_SadeSati')

    promise = {r['topic']: r for r in t['AI_TopicPromise'] if r['row_type'] == 'total'}
    for m in t['AI_TopicMap']:
        topic = m['topic']
        add('Topics', f'{topic}: where to look',
            brief_line(m, ('d1_houses', 'significators_for_this_chart', 'divisional_charts')), 'AI_TopicMap')
        if topic in promise:
            add('Topics', f'{topic}: promise', brief_line(promise[topic], ('supports_count', 'weakens_count')),
                'AI_TopicPromise')
        if bhukti_row is not None:
            r = next(x for x in t['AI_TopicScores'] if x['topic'] == topic
                     and x['start_local'] == bhukti_row['start_local'] and x['bhukti_lord'] == bhukti_row['bhukti_lord'])
            add('Topics', f'{topic}: running bhukti',
                brief_line(r, ('bhukti_lord', 'relevance_score_not_a_prediction', 'rank_in_topic', 'in_top_quarter',
                               'bhukti_lord_letters', 'dasa_lord_letters', 'deduction')), 'AI_TopicScores')
        mine = [r for r in t['AI_TopicWindows'] if r['topic'] == topic]
        chosen = [r for r in mine if r['layers_agreeing'] >= 3][:BRIEF_WINDOWS]
        if len(chosen) < BRIEF_WINDOWS:
            rest = [r for r in mine if r['layers_agreeing'] < 3][:BRIEF_WINDOWS - len(chosen)]
            chosen = sorted(chosen + rest, key=lambda r: r['start_local'])
        for i, r in enumerate(chosen, start=1):
            add('Topics', f'{topic}: window {i}', brief_line(r, BRIEF_WINDOW_COLUMNS), 'AI_TopicWindows')
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

# Columns added by schema 2 to sheets that already existed: always at the end.
COLUMNS['AI_Planets'] += [
    ('combust_margin_deg', 'Distance from the Sun minus the orb: negative = combust, a small positive value = '
                           'just outside the orb; empty where combustion does not apply'),
    ('bhava_differs_from_whole_sign', 'yes when the Sripati bhava is not the whole-sign house'),
]
COLUMNS['AI_Vargas'] += [
    ('house_if_lagna_earlier', 'House of the point counted from lagna_if_earlier of that chart (AI_VargaLagnas): '
                               'its house if the birth were earlier than the margin; empty on the Lagna row and '
                               'when that lagna does not change within 6 hours'),
    ('house_if_lagna_later', 'The same for lagna_if_later'),
]
COLUMNS['AI_VargaLagnas'] += [
    ('lagna_uncertain_for_stated_accuracy', 'yes when either margin is smaller than birth_time_uncertainty_minutes '
                                            '(AI_Facts); "not given" when the user gave no uncertainty'),
]
COLUMNS['AI_Yogas'] += [
    ('weakening_factors', 'For a yoga that is found: facts about its planets that tradition reads as reducing it '
                          '(combust, debilitated, in house 6, 8 or 12, in an enemy\'s sign), or none. Empty on '
                          'rows that are not found, and on doshas and neecha bhanga rows'),
]
_REACH_COLUMNS = [
    ('houses_aspected_from_lagna', 'Natal houses that receive the full aspect of the planet from this sign'),
    ('natal_points_in_sign', 'Natal planets, Lagna and Mandi in the sign transited'),
    ('natal_points_aspected', 'Natal planets, Lagna and Mandi in the signs aspected from this sign'),
]
COLUMNS['AI_Transits'] += _REACH_COLUMNS
COLUMNS['AI_TopicScores'] += [
    ('rank_in_topic', '1 = the highest score of this topic over all bhuktis, 2 = the next different score, ...'),
    ('in_top_quarter', 'yes when fewer than a quarter of all bhuktis have a higher score for this topic'),
]

_PERIOD_LORD_COLUMNS = [
    ('period_lord', 'The planet whose facts follow: the bhukti lord on a bhukti row, the antaram lord on an antaram row'),
    ('houses_owned', 'Houses it owns; none for Rahu and Ketu'), ('house', 'House it occupies'),
    ('sign', 'Sign it occupies'), ('dignity', 'Its dignity in D1'), ('debilitated', 'yes / no'),
    ('debilitation_cancelled_by', 'Neecha bhanga conditions met, or none; empty when not debilitated'),
    ('combust', 'yes / no'), ('retrograde', 'yes / no'), ('functional_nature', 'Yogakaraka, Benefic, Malefic or Neutral'),
    ('vimsopaka_shodasavarga', 'Its strength out of 20'),
    ('own_bav_bindus_in_sign_occupied', 'Bindus in its own Bhinnashtakavarga for the sign it occupies'),
    ('d9_sign', 'Its sign in the Navamsa'), ('d9_dignity', 'Its dignity there (by sign; no lagna needed)'),
    ('d9_debilitated', 'yes / no'),
    ('d10_sign', 'Its sign in the Dasamsa'), ('d10_dignity', 'Its dignity there (by sign; no lagna needed)'),
    ('d10_debilitated', 'yes / no'),
    ('sign_lord', 'Lord of the sign it occupies'), ('sign_lord_house', 'House that sign lord occupies'),
    ('star_lord', 'Lord of the nakshatra it occupies'), ('star_lord_houses_owned', 'Houses that star lord owns'),
    ('star_lord_house', 'House that star lord occupies'),
    ('place_from_dasa_lord', 'Its place counted from the sign of the dasa lord (1 = same sign)'),
    ('relation_to_dasa_lord', 'Compound relationship: how it regards the dasa lord; "same planet" when it is the '
                              'dasa lord; empty when either is Rahu or Ketu'),
    ('relation_of_dasa_lord', 'The reverse: how the dasa lord regards it'),
    ('place_from_bhukti_lord', 'Antaram rows: its place counted from the sign of the bhukti lord'),
    ('tara_of_lordship_no', '1-9: tara of the nakshatras it rules, counted from the janma nakshatra'),
    ('tara_of_lordship', 'Name of that tara'), ('tara_of_lordship_label', 'favourable, unfavourable or mixed'),
    ('tara_of_position_no', '1-9: tara of the nakshatra it occupies, counted from the janma nakshatra'),
    ('tara_of_position', 'Name of that tara'), ('tara_of_position_label', 'favourable, unfavourable or mixed'),
    ('yogas', 'Yogas found (AI_Yogas) in which it takes part, or none'),
    ('lord_tied_topics', 'Topics for which it owns a key house, sits in one or is a significator'),
]
_NEW_SHEETS = {
    'AI_Brief': [
        ('section', 'Group of lines'), ('key', 'What the line is about'),
        ('value', 'One cell copied from the source sheet, or several cells of one row written as '
                  '"column=value; column=value"'),
        ('source', 'The AI sheet the value is copied from'),
    ],
    'AI_LifeFacts': [('key', 'Name of the fact'), ('value', 'As entered by the user, or "not given"'),
                     ('note', 'What may be entered')],
    'AI_LifeEvents': [('event_type', 'Kind of event, as entered by the user'), ('year', 'Calendar year, as entered'),
                      ('topic', 'The topic of AI_TopicMap this kind of event is checked against'),
                      ('age_that_year', 'Year of the event minus year of birth')],
    'AI_DasaPeriods': [
        ('dasa_lord', 'Lord of the dasa (1st level)'), ('start_local', f'Start of the dasa, {_LOCAL}; the first '
                                                       'dasa starts at birth'),
        ('end_local', f'End of the dasa, {_LOCAL}'), ('age_at_start_years', 'Age when it starts'),
        ('age_at_end_years', 'Age when it ends'),
        ('dasa_lord_houses_owned', 'Houses the dasa lord owns'), ('dasa_lord_house', 'House it occupies'),
        ('dasa_lord_sign', 'Sign it occupies'), ('dasa_lord_dignity', 'Its dignity in D1'),
        ('dasa_lord_debilitated', 'yes / no'), ('dasa_lord_vimsopaka_shodasavarga', 'Its strength out of 20'),
        ('dasa_lord_functional_nature', 'Yogakaraka, Benefic, Malefic or Neutral'),
        ('dasa_lord_star_lord', 'Lord of the nakshatra it occupies'),
        ('dasa_lord_tara_of_lordship_no', '1-9: tara of the nakshatras it rules, counted from the janma nakshatra'),
        ('dasa_lord_tara_of_lordship', 'Name of that tara'),
        ('dasa_lord_tara_of_lordship_label', 'favourable, unfavourable or mixed'),
    ],
    'AI_Antaram': [
        ('dasa_lord', '1st level'), ('bhukti_lord', '2nd level'), ('antaram_lord', '3rd level'),
        ('start_local', f'Start, {_LOCAL}'), ('end_local', f'End, {_LOCAL}'), ('days', 'Length in days'),
    ],
    'AI_PeriodFacts': [
        ('level', 'bhukti or antaram'), ('dasa_lord', '1st level'), ('bhukti_lord', '2nd level'),
        ('antaram_lord', '3rd level; empty on bhukti rows'),
        ('start_local', f'Start of the period, {_LOCAL}'), ('end_local', f'End of the period, {_LOCAL}'),
        ('age_at_start_years', 'Age when it starts'),
    ] + _PERIOD_LORD_COLUMNS + [
        ('bhukti_top_quarter_topics', 'Topics for which the bhukti of this row (the parent bhukti on an antaram '
                                      'row) has in_top_quarter = yes in AI_TopicScores'),
    ],
    'AI_TransitsFast': [col for col in COLUMNS['AI_Transits']
                        if col[0] not in ('planet', 'own_bav_bindus', 'saturn_from_moon')],
    'AI_Stations': [
        ('planet', 'Mars, Jupiter or Saturn'),
        ('station', 'retrograde = the planet turns backward here; direct = it turns forward again'),
        ('moment_local', f'Moment the daily motion is zero, {_LOCAL}; read it as a date'),
        ('moment_utc', 'The same moment, UTC'), ('longitude_deg', 'Sidereal longitude at the station'),
        ('sign_no', '1 = Mesha ... 12 = Meena'), ('sign', 'Sign of the station'),
        ('deg_in_sign_text', 'Degrees, minutes, seconds inside that sign'),
        ('house_from_lagna', 'House of that sign from the natal lagna'),
        ('house_from_moon', 'Place of that sign from the natal Moon'),
    ],
    'AI_TopicPromise': [
        ('topic', 'Common question'), ('row_type', 'factor = one test that fired; total = the two counts of the topic'),
        ('subject', 'What was tested: the lord of key houses, a key house, a significator or a yoga'),
        ('factor', 'The test, from the fixed list in the rule "Topic promise"'),
        ('side', 'supports or weakens'), ('fact', 'What was found in this chart'),
        ('supports_count', 'Total rows only: number of factor rows of the topic with side = supports'),
        ('weakens_count', 'Total rows only: number of factor rows of the topic with side = weakens'),
    ],
    'AI_TopicWindows': [
        ('topic', 'Common question'), ('start_local', f'Start of the piece, {_LOCAL}'),
        ('end_local', f'End of the piece, {_LOCAL}'), ('days', 'Length in days'),
        ('layers_agreeing', 'How many of the four layers hold, 2 to 4'),
        ('layers', 'Which ones: bhukti, antaram, jupiter, saturn'),
        ('dasa_lord', '1st level'), ('bhukti_lord', '2nd level'),
        ('antaram_lords', 'Antaram lords (3rd level) during the window, in time order'),
        ('bhukti_score', 'relevance_score_not_a_prediction of that bhukti for the topic (AI_TopicScores)'),
        ('bhukti_rank_in_topic', 'rank_in_topic of that bhukti'),
        ('jupiter_signs', 'Signs Jupiter transits during the window, in time order'),
        ('jupiter_own_bindus', 'Bindus of those signs in Jupiter\'s own chart, in the same order'),
        ('jupiter_key_houses_reached', 'Key houses of the topic Jupiter occupies or aspects during the window, or none'),
        ('saturn_signs', 'Signs Saturn transits during the window, in time order'),
        ('saturn_own_bindus', 'Bindus of those signs in Saturn\'s own chart, in the same order'),
        ('saturn_key_houses_reached', 'Key houses of the topic Saturn occupies or aspects during the window, or none'),
        ('key_houses_reached_by_both', 'Key houses reached by both at the same time (double transit, modern '
                                       'method), or none'),
        ('label', 'Always "rule-based overlap, not a prediction"'),
    ],
    'AI_EventCheck': [
        ('event_type', 'Kind of event, as entered by the user'), ('year', 'Calendar year, as entered'),
        ('topic', 'Topic the event is checked against'), ('dasa_lord', 'Dasa running in that year'),
        ('bhukti_lord', 'Bhukti running in that year; one row for each bhukti that overlaps the year'),
        ('overlap_start_local', f'Start of the part of that bhukti inside the year, {_LOCAL}'),
        ('overlap_end_local', f'End of that part, {_LOCAL}'),
        ('relevance_score_not_a_prediction', 'Score of that bhukti for the topic (AI_TopicScores)'),
        ('rank_in_topic', 'Its rank_in_topic'), ('in_top_quarter', 'Its in_top_quarter'),
        ('antaram_lords_tied_to_topic', 'Antaram lords inside the overlap that own a key house, sit in one or are '
                                        'a significator, or none'),
        ('jupiter_signs', 'Signs Jupiter was in during the overlap, with the house from the lagna'),
        ('jupiter_reaches_key_house', 'yes when Jupiter occupied or aspected a key house of the topic in that time'),
        ('saturn_signs', 'Signs Saturn was in during the overlap, with the house from the lagna'),
        ('saturn_reaches_key_house', 'yes when Saturn occupied or aspected a key house of the topic in that time'),
    ],
}
_NEW_SHEETS['AI_TransitsFast'] = (
    [('planet', 'Mars, Sun, Mercury or Venus; rows are in time order for each planet')]
    + _NEW_SHEETS['AI_TransitsFast'][:10]
    + [('own_bav_bindus', 'Bindus of the sign in the natal Bhinnashtakavarga of that planet')]
    + _NEW_SHEETS['AI_TransitsFast'][10:])
COLUMNS.update(_NEW_SHEETS)
SHEETS = [
    'AI_ReadMe', 'AI_Brief', 'AI_Facts', 'AI_LifeFacts', 'AI_LifeEvents', 'AI_Planets', 'AI_Houses', 'AI_Pairs',
    'AI_Vargas', 'AI_VargaLagnas', 'AI_Strength', 'AI_Ashtakavarga', 'AI_Yogas', 'AI_DasaPeriods', 'AI_Dasa',
    'AI_Antaram', 'AI_Pratyantar', 'AI_PeriodFacts', 'AI_Transits', 'AI_TransitsFast', 'AI_Stations',
    'AI_TransitNow', 'AI_SadeSati', 'AI_DoubleTransit', 'AI_TopicMap', 'AI_TopicFacts', 'AI_TopicPromise',
    'AI_TopicScores', 'AI_TopicWindows', 'AI_EventCheck',
]
assert set(SHEETS) == set(COLUMNS)
COLUMNS = {sheet: COLUMNS[sheet] for sheet in SHEETS}
# Sheets that are written only when they have rows: they hold what the user entered about past events.
OPTIONAL_SHEETS = ('AI_LifeEvents', 'AI_EventCheck')
NOT_GIVEN = 'not given'


def _readme(c, tables, sheets=None):
    m = c.meta
    sheets = sheets or SHEETS
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
    add('About', 'where to start', 'AI_Brief is a short copy of the main facts and is enough for a first reading. '
        'To judge a period read its row in AI_PeriodFacts; for the promise of a topic read AI_TopicPromise; '
        'for timing read AI_TopicWindows. Every other sheet holds the full detail behind them.')
    add('Defaults', 'house system', 'Whole sign from the lagna: every "house" column means this unless its name '
        'says bhava_sripati or kp_.')
    add('Defaults', 'dasa table', f"AI_Dasa and AI_Pratyantar: Vimshottari from the Moon with the Vedic ayanamsha "
        f"({m['ayanamsha_name']}). Use these dates. AI_DasaPeriods (1st level) and AI_Antaram (3rd level) "
        'belong to the same tree.')
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
    add('Warnings', 'counts and windows', 'AI_TopicPromise counts fixed tests and AI_TopicWindows marks where '
        'fixed layers overlap. Both are rule-based aids, not predictions: a high count or four layers says '
        'that the rules agree, not that an event will happen.')
    add('Warnings', 'D2 Hora', 'By Parashara\'s rule every point of D2 falls in Kataka or Simha. A house number in '
        'D2, and the words Exalted or debilitated there, come from that rule and say nothing about the '
        'planet: do not read them as strength, gain or loss.')
    add('Warnings', 'as-of lines', 'AI_TransitNow and the section "As of the report date" of AI_Brief were true at '
        'the report date only and go stale like the "Current" labels of the other sheets.')
    add('Warnings', 'life facts', 'AI_LifeFacts, AI_LifeEvents and birth_time_uncertainty_minutes are as entered by '
        'the user: not computed and not checked against the chart. AI_LifeEvents and AI_EventCheck are '
        'present only when the user entered past events.')
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
    for sheet in sheets:
        rows = len(tables[sheet]) if sheet in tables else None
        add('Sheets', sheet, SHEET_ABOUT[sheet] + (f' ({rows} rows)' if rows is not None else ''))
    for sheet in sheets:
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
    'AI_Pratyantar': 'The 4th dasa level from 1 year before the report date to 10 years after.',
    'AI_Transits': 'Sign entries of Saturn, Jupiter, Rahu and Ketu from birth to 10 years after the report date; '
                   'each planet starts with the stay running at birth.',
    'AI_TransitNow': 'Positions of the nine planets on the report date.',
    'AI_SadeSati': 'Sade sati spans and their phases, with retrograde breaks.',
    'AI_DoubleTransit': 'Houses reached by both Jupiter and Saturn in the 10 years after the report date, '
                        'sorted by house.',
    'AI_TopicMap': 'Where to look for each common question.',
    'AI_TopicFacts': 'The facts of this chart for each common question.',
    'AI_TopicScores': 'Rule-based relevance of every bhukti to each common question.',
    'AI_Brief': 'Start here: a short copy of the other sheets (birth facts, planets, houses, yogas, the periods and '
                'transits running on the report date, and per topic the promise counts and next windows).',
    'AI_LifeFacts': 'What the user chose to enter about their life; not computed. "not given" where nothing was '
                    'entered.',
    'AI_LifeEvents': 'Past events the user chose to enter (kind and year); not computed. This sheet is present '
                     'only when at least one event was entered.',
    'AI_DasaPeriods': 'One row per Vimshottari dasa (1st level) with its dates and the state of its lord.',
    'AI_Antaram': 'One row per antaram (3rd dasa level) for the whole life.',
    'AI_PeriodFacts': 'One row per bhukti (whole life) and per antaram (1 year before the report date to 10 years '
                      'after) with every fact about the lord of that period.',
    'AI_TransitsFast': 'Sign entries of Mars (2 years before the report date to 10 after) and of the Sun, Mercury '
                       'and Venus (1 year before to 2 after).',
    'AI_Stations': 'Retrograde and direct stations of Mars, Jupiter and Saturn from 1 year before the report date '
                   'to 10 years after.',
    'AI_TopicPromise': 'Per topic, the fixed tests that support or weaken it in this chart, with the two counts. '
                       'Rule-based, not a prediction.',
    'AI_TopicWindows': 'Per topic, the pieces of the 10 years after the report date in which two or more of the '
                       'layers bhukti, antaram, Jupiter and Saturn agree. Rule-based overlap, not a prediction.',
    'AI_EventCheck': 'For each past event the user entered: the bhuktis of that year with their score for the '
                     'matching topic, and where Jupiter and Saturn were. This sheet is present only when at '
                     'least one event was entered.',
}


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def enrich(res, now=None, extras=None):
    """
    Build the AI block from compute() output.

    now: the report moment (naive clock time at the birth place); defaults to
    the moment the horoscope was generated.
    extras: optional facts only the user knows, see clean_extras():
    {'tob_uncertainty_min', 'coordinates_source', 'life'}. A bad value raises
    astro_engine.InputError.
    Returns {'schema', 'report_datetime_local', 'sheets', 'columns', 'tables',
    'rules'}; tables[sheet] is a list of rows keyed by column name. 'sheets' is
    SHEETS without the OPTIONAL_SHEETS that have no rows.
    """
    c = Ctx(res, now, extras)
    check_years(c)
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
    tables['AI_LifeFacts'] = _life_facts(c)
    tables['AI_LifeEvents'] = _life_events(c)
    tables['AI_DasaPeriods'] = _dasa_periods(c)
    tables['AI_Antaram'] = _antaram(c)
    tables['AI_PeriodFacts'] = _period_facts(c)
    tables['AI_TransitsFast'] = _transits_fast(c)
    tables['AI_Stations'] = _stations(c)
    tables['AI_TopicPromise'] = _topic_promise(c)
    tables['AI_TopicWindows'] = _topic_windows(c)
    tables['AI_EventCheck'] = _event_check(c)
    tables['AI_Brief'] = _brief(c, tables)
    sheets = [s for s in SHEETS if tables.get(s) or s not in OPTIONAL_SHEETS]
    tables['AI_ReadMe'] = _readme(c, tables, sheets)

    # every row carries every column of its sheet, in the declared order
    ordered = {}
    for sheet in sheets:
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
        'sheets': sheets,
        'columns': {s: [{'name': n, 'meaning': t} for n, t in COLUMNS[s]] for s in sheets},
        'tables': ordered,
        'rules': [{'rule': n, 'variant': t} for n, t in RULES],
    }
