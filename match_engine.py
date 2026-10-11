"""
match_engine.py — marriage matching (porutham) between two horoscopes.

match(boy, girl) compares two people and returns one row per check. Each
person is either a result of astro_engine.compute() (full birth details) or
a star-only record {nakshatra, pada, rasi} for families who know only the
star and the rasi.

Groups of checks
  A  Ten poruthams of the Tamil tradition, plus Nadi and Vriksha.
  B  Star rules: tara both ways, the 7th star (Vadha), the 22nd star and its
     4th pada (Vainasika), the 27th star, the same star, the same rasi.
  C  Ashtakoota, 36 points.
  D  Chart checks, which need the birth details of both: Kuja dosha from
     the lagna, the Moon and Venus with its exceptions; Rahu and Ketu;
     Kalathra facts; Papa samyam; Punarpoo; Kala Sarpa; the lagnas, the 7th
     lords, the navamsa, Venus and Mars, the 5th house.
  E  Timing and KP, which also need the birth details of both: dasa sandhi,
     the dasas running together, the sub lord of the 7th cusp, and the spans
     in which the marriage windows of the two horoscopes overlap.

What every row is
  key, group, name, boy_value, girl_value,
  result (matched / medium / not matched / not applicable / information),
  points, max_points, rule_applied, exception_applied, note.

Rules of this module
  * Direction: every count runs from the girl's star or rasi to the boy's
    unless the rule says otherwise.
  * A row states the rule and the result. It says nothing about what a
    result is believed to bring, nothing about length of life, and gives no
    remedy and no verdict on the marriage.
  * An exception never changes a result or the points: it is named in
    exception_applied so the reader can weigh it.
  * Every rule and the variant used is listed in MATCH_RULES. The tables
    differ between almanacs; TABLE_SOURCES says where each one was checked
    and where the sources disagree.

Nothing here changes compute(): the module only reads its result.
"""
from __future__ import annotations

from datetime import timedelta

import astro_engine as A
import enrich as E
from astro_engine import NAKS, RASIS, SIGN_LORDS, InputError

SCHEMA = 'horoscopegen-match/1'
LABEL = 'rule-based, not a prediction'

MATCHED, MEDIUM, NOT_MATCHED = 'matched', 'medium', 'not matched'
NOT_APPLICABLE, INFORMATION = 'not applicable', 'information'
RESULTS = (MATCHED, MEDIUM, NOT_MATCHED, NOT_APPLICABLE, INFORMATION)

GROUPS = {
    'A': 'Ten poruthams (Tamil tradition), with Nadi and Vriksha',
    'B': 'Star rules',
    'C': 'Ashtakoota (36 points)',
    'D': 'Chart checks (birth details of both)',
    'E': 'Timing and KP (birth details of both)',
}
TAMIL_TEN = ('dinam', 'ganam', 'mahendram', 'stree_deergham', 'yoni', 'rasi', 'rasi_adhipathi',
             'vasiyam', 'rajju', 'vedhai')
KEY_PORUTHAMS = ('rajju', 'dinam', 'ganam', 'yoni', 'rasi')   # named in the summary when not matched


# ── LOOKUP TABLES ─────────────────────────────────────────────────────────────
# Every table is written as "group: the stars in it" and turned into a list
# indexed by star, so a star left out or entered twice stops the import.

def _by_star(groups):
    out = [None] * 27
    for label, stars in groups.items():
        for star in stars:
            i = NAKS.index(star)
            if out[i] is not None:
                raise ValueError(f'{star} is listed twice')
            out[i] = label
    missing = [NAKS[i] for i, v in enumerate(out) if v is None]
    if missing:
        raise ValueError(f'not listed: {missing}')
    return out


# Gana. Checked against vedicmarga.com/guna-milan-explained.
GANA = _by_star({
    'Deva': ['Ashwini', 'Mrigashira', 'Punarvasu', 'Pushya', 'Hasta', 'Swati', 'Anuradha', 'Shravana', 'Revati'],
    'Manushya': ['Bharani', 'Rohini', 'Ardra', 'Purva Phalguni', 'Uttara Phalguni', 'Purva Ashadha',
                 'Uttara Ashadha', 'Purva Bhadrapada', 'Uttara Bhadrapada'],
    'Rakshasa': ['Krittika', 'Ashlesha', 'Magha', 'Chitra', 'Vishakha', 'Jyeshtha', 'Moola', 'Dhanishtha',
                 'Shatabhisha'],
})
# Gana points, GANA_POINTS[girl's gana][boy's gana]. Checked against
# vedicmarga.com; onlinejyotish.com prints the same figures with the bride and
# the groom the other way round (see TABLE_SOURCES).
GANA_POINTS = {
    'Deva':     {'Deva': 6, 'Manushya': 5, 'Rakshasa': 1},
    'Manushya': {'Deva': 6, 'Manushya': 6, 'Rakshasa': 0},
    'Rakshasa': {'Deva': 0, 'Manushya': 0, 'Rakshasa': 6},
}

# Yoni: the animal of each star. Checked against vedicmarga.com,
# saravali.github.io and freehoroscopesonline.in, which agree.
YONI = _by_star({
    'Horse': ['Ashwini', 'Shatabhisha'], 'Elephant': ['Bharani', 'Revati'],
    'Sheep': ['Krittika', 'Pushya'], 'Serpent': ['Rohini', 'Mrigashira'],
    'Dog': ['Ardra', 'Moola'], 'Cat': ['Punarvasu', 'Ashlesha'],
    'Rat': ['Magha', 'Purva Phalguni'], 'Cow': ['Uttara Phalguni', 'Uttara Bhadrapada'],
    'Buffalo': ['Hasta', 'Swati'], 'Tiger': ['Chitra', 'Vishakha'],
    'Deer': ['Anuradha', 'Jyeshtha'], 'Monkey': ['Purva Ashadha', 'Shravana'],
    'Mongoose': ['Uttara Ashadha'], 'Lion': ['Dhanishtha', 'Purva Bhadrapada'],
})
YONI_ENEMIES = (('Cow', 'Tiger'), ('Elephant', 'Lion'), ('Horse', 'Buffalo'), ('Dog', 'Deer'),
                ('Cat', 'Rat'), ('Serpent', 'Mongoose'), ('Sheep', 'Monkey'))
YONI_ORDER = ('Horse', 'Elephant', 'Sheep', 'Serpent', 'Dog', 'Cat', 'Rat', 'Cow', 'Buffalo', 'Tiger',
              'Deer', 'Monkey', 'Mongoose', 'Lion')
# Yoni points (Ashtakoota), rows and columns in YONI_ORDER. The matrix
# published at saravali.github.io (the one the Maitreya software uses). Two of
# its cells do not agree with their mirror cell (Deer-Horse, Lion-Buffalo);
# the value of the earlier row is used for both so the table is symmetric.
YONI_POINTS = (
    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1),   # Horse
    (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),   # Elephant
    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),   # Sheep
    (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),   # Serpent
    (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),   # Dog
    (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),   # Cat
    (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),   # Rat
    (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),   # Cow
    (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),   # Buffalo
    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),   # Tiger
    (3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),   # Deer
    (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),   # Monkey
    (2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),   # Mongoose
    (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),   # Lion
)

# Rajju. Checked against findyourfate.com and hindutone.com, which agree.
RAJJU = _by_star({
    'Pada': ['Ashwini', 'Ashlesha', 'Magha', 'Jyeshtha', 'Moola', 'Revati'],
    'Kati': ['Bharani', 'Pushya', 'Purva Phalguni', 'Anuradha', 'Purva Ashadha', 'Uttara Bhadrapada'],
    'Nabhi': ['Krittika', 'Punarvasu', 'Uttara Phalguni', 'Vishakha', 'Uttara Ashadha', 'Purva Bhadrapada'],
    'Kantha': ['Rohini', 'Ardra', 'Hasta', 'Swati', 'Shravana', 'Shatabhisha'],
    'Siro': ['Mrigashira', 'Chitra', 'Dhanishtha'],
})

# Vedhai: the sets of stars that are vedha to each other. Checked against
# findyourfate.com and hindutone.com, which agree.
VEDHA_SETS = (
    ('Ashwini', 'Jyeshtha'), ('Bharani', 'Anuradha'), ('Krittika', 'Vishakha'), ('Rohini', 'Swati'),
    ('Ardra', 'Shravana'), ('Punarvasu', 'Uttara Ashadha'), ('Pushya', 'Purva Ashadha'),
    ('Ashlesha', 'Moola'), ('Magha', 'Revati'), ('Purva Phalguni', 'Uttara Bhadrapada'),
    ('Uttara Phalguni', 'Purva Bhadrapada'), ('Hasta', 'Shatabhisha'),
    ('Mrigashira', 'Chitra', 'Dhanishtha'),
)
VEDHA = _by_star({i: stars for i, stars in enumerate(VEDHA_SETS)})

# Nadi. Checked against vedicmarga.com.
NADI = _by_star({
    'Aadi': ['Ashwini', 'Ardra', 'Punarvasu', 'Uttara Phalguni', 'Hasta', 'Jyeshtha', 'Moola', 'Shatabhisha',
             'Purva Bhadrapada'],
    'Madhya': ['Bharani', 'Mrigashira', 'Pushya', 'Purva Phalguni', 'Chitra', 'Anuradha', 'Purva Ashadha',
               'Dhanishtha', 'Uttara Bhadrapada'],
    'Antya': ['Krittika', 'Rohini', 'Ashlesha', 'Magha', 'Swati', 'Vishakha', 'Uttara Ashadha', 'Shravana',
              'Revati'],
})

# Vriksha (tree) of each star and whether it is a "paal" (milk) tree. The
# grouping is the one printed at horoscope.hosuronline.com; astroved.com
# prints the same trees with the two groups the other way round.
_PAAL = {'Krittika': 'Athi', 'Rohini': 'Naval', 'Pushya': 'Arasu', 'Ashlesha': 'Punnai', 'Magha': 'Aal',
         'Purva Phalguni': 'Pala', 'Uttara Phalguni': 'Alari', 'Hasta': 'Velam', 'Jyeshtha': 'Pirai',
         'Moola': 'Maa', 'Purva Ashadha': 'Vanji', 'Uttara Ashadha': 'Pala', 'Shravana': 'Erukku',
         'Purva Bhadrapada': 'Thema', 'Revati': 'Iluppai'}
_NOT_PAAL = {'Ashwini': 'Etti', 'Bharani': 'Nelli', 'Mrigashira': 'Karungali', 'Ardra': 'Sengarungali',
             'Punarvasu': 'Moongil', 'Chitra': 'Vilvam', 'Swati': 'Marutham', 'Vishakha': 'Vila',
             'Anuradha': 'Magizh', 'Dhanishtha': 'Vanni', 'Shatabhisha': 'Kadambu',
             'Uttara Bhadrapada': 'Vembu'}
PAAL = _by_star({True: list(_PAAL), False: list(_NOT_PAAL)})
TREE = [{**_PAAL, **_NOT_PAAL}[star] for star in NAKS]

# The same star for both (eka nakshatra). Checked against astroved.com
# (Dina porutham page).
SAME_STAR = _by_star({
    MATCHED: ['Rohini', 'Ardra', 'Magha', 'Hasta', 'Vishakha', 'Shravana', 'Uttara Bhadrapada', 'Revati'],
    MEDIUM: ['Ashwini', 'Krittika', 'Mrigashira', 'Punarvasu', 'Pushya', 'Purva Phalguni', 'Uttara Phalguni',
             'Chitra', 'Anuradha', 'Purva Ashadha', 'Uttara Ashadha'],
    NOT_MATCHED: ['Bharani', 'Ashlesha', 'Swati', 'Jyeshtha', 'Moola', 'Dhanishtha', 'Shatabhisha',
                  'Purva Bhadrapada'],
})

# Dinam: the counts from the girl's star to the boy's that match. Checked
# against astroved.com, findyourfate.com and stevehora.substack.com, which agree.
DINAM_COUNTS = (2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26)
MAHENDRAM_COUNTS = (4, 7, 10, 13, 16, 19, 22, 25)        # checked against hindutone.com
STREE_DEERGHAM_FULL, STREE_DEERGHAM_MEDIUM = 13, 7       # more than 13: matched; more than 7: medium

# Rasi (Tamil): the place of the boy's rasi counted from the girl's. As
# printed at astroved.com (Rasi porutham page).
RASI_MATCHED = (1, 7)
RASI_NOT_MATCHED = (2, 6, 8, 12)
RASI_SEVENTH_NOT_ACCEPTED = (frozenset(('Simha', 'Kumbha')), frozenset(('Kataka', 'Makara')))

# Vasiyam (Tamil): the rasis that are vasya to each rasi. Written from the
# list in B.V. Raman's Muhurtha as remembered; findyourfate.com prints a list
# that agrees where it can be read. Not checked against the printed book.
VASYA = {
    'Mesha': ('Simha', 'Vrischika'), 'Rishabha': ('Kataka', 'Thula'), 'Mithuna': ('Kanya',),
    'Kataka': ('Vrischika', 'Dhanu'), 'Simha': ('Thula',), 'Kanya': ('Meena', 'Mithuna'),
    'Thula': ('Makara', 'Kanya'), 'Vrischika': ('Kataka',), 'Dhanu': ('Meena',),
    'Makara': ('Mesha', 'Kumbha'), 'Kumbha': ('Mesha',), 'Meena': ('Makara',),
}

# Varna of each rasi (Ashtakoota), highest first. Checked against vedicmarga.com.
VARNA_ORDER = ('Brahmin', 'Kshatriya', 'Vaishya', 'Shudra')
VARNA = {'Kataka': 'Brahmin', 'Vrischika': 'Brahmin', 'Meena': 'Brahmin',
         'Mesha': 'Kshatriya', 'Simha': 'Kshatriya', 'Dhanu': 'Kshatriya',
         'Rishabha': 'Vaishya', 'Kanya': 'Vaishya', 'Makara': 'Vaishya',
         'Mithuna': 'Shudra', 'Thula': 'Shudra', 'Kumbha': 'Shudra'}

# Vashya group of each rasi (Ashtakoota). Dhanu and Makara change group at
# 15 degrees. Checked against vedicmarga.com and onlinejyotish.com.
VASHYA_GROUP = {'Mesha': 'Chatushpada', 'Rishabha': 'Chatushpada', 'Mithuna': 'Manava', 'Kataka': 'Jalachara',
                'Simha': 'Vanachara', 'Kanya': 'Manava', 'Thula': 'Manava', 'Vrischika': 'Keeta',
                'Dhanu': ('Manava', 'Chatushpada'), 'Makara': ('Chatushpada', 'Jalachara'),
                'Kumbha': 'Manava', 'Meena': 'Jalachara'}
# Vashya points, VASHYA_POINTS[girl's group][boy's group]. As printed at
# vedicmarga.com; onlinejyotish.com differs in three cells (see TABLE_SOURCES).
VASHYA_POINTS = {
    'Chatushpada': {'Chatushpada': 2, 'Manava': 1, 'Jalachara': 1, 'Vanachara': 0.5, 'Keeta': 1},
    'Manava':      {'Chatushpada': 1, 'Manava': 2, 'Jalachara': 0.5, 'Vanachara': 0, 'Keeta': 1},
    'Jalachara':   {'Chatushpada': 1, 'Manava': 0.5, 'Jalachara': 2, 'Vanachara': 1, 'Keeta': 1},
    'Vanachara':   {'Chatushpada': 0, 'Manava': 0, 'Jalachara': 0, 'Vanachara': 2, 'Keeta': 0},
    'Keeta':       {'Chatushpada': 1, 'Manava': 1, 'Jalachara': 1, 'Vanachara': 0, 'Keeta': 2},
}

# Graha Maitri points by the two relations (how each rasi lord regards the
# other). Checked against vedicmarga.com.
MAITRI_POINTS = {frozenset(('Friend',)): 5, frozenset(('Friend', 'Neutral')): 4, frozenset(('Neutral',)): 3,
                 frozenset(('Friend', 'Enemy')): 1, frozenset(('Neutral', 'Enemy')): 0.5,
                 frozenset(('Enemy',)): 0}
TARA_BAD = (3, 5, 7)                    # Vipat, Pratyari, Vadha
BHAKOOT_BAD = {2: '2/12', 12: '2/12', 5: '5/9', 9: '5/9', 6: '6/8', 8: '6/8'}

# ── CHART CHECKS (GROUP D) ────────────────────────────────────────────────────

# Kuja (Sevvai) dosha: the places of Mars that count. 'south' is the Tamil
# practice (checked against astroved.com); 'all' is the set enrich.py uses in
# AI_Yogas; 'north' leaves out the 2nd.
KUJA_HOUSE_SETS = {'south': (2, 4, 7, 8, 12), 'north': (1, 4, 7, 8, 12), 'all': E.KUJA_HOUSES}
KUJA_DEFAULT = 'south'
# Exceptions, written from B.V. Raman's statement of them as remembered; the
# first five and the sixth are also on the list printed at astroved.com. Not
# checked against the printed book. (key, name, place of Mars or None for any
# place, signs of Mars or None)
KUJA_EXCEPTIONS = (
    ('kuja_x_2nd', 'Mars in the 2nd in Mithuna or Kanya', 2, ('Mithuna', 'Kanya')),
    ('kuja_x_12th', 'Mars in the 12th in Rishabha or Thula', 12, ('Rishabha', 'Thula')),
    ('kuja_x_4th', 'Mars in the 4th in Mesha or Vrischika', 4, ('Mesha', 'Vrischika')),
    ('kuja_x_7th', 'Mars in the 7th in Makara or Kataka', 7, ('Makara', 'Kataka')),
    ('kuja_x_8th', 'Mars in the 8th in Dhanu or Meena', 8, ('Dhanu', 'Meena')),
    ('kuja_x_sign', 'Mars in Simha or Kumbha', None, ('Simha', 'Kumbha')),
    ('kuja_x_joined', 'Mars in one sign with Jupiter or the Moon', None, None),
)
SARPA_HOUSES = (1, 2, 7, 8)                              # Rahu or Ketu from the lagna
# Papa samyam: the planets and places counted (astrologymag.com and
# sreenivasdesabhatla.wordpress.com agree on these), and the weight of each
# reference in the weighted figure (the second page).
PAPA_PLANETS = ('Sun', 'Mars', 'Saturn', 'Rahu')
PAPA_HOUSES = (1, 2, 4, 7, 8, 12)
PAPA_WEIGHTS = (('the lagna', 1.0), ('the Moon', 0.5), ('Venus', 0.25))
SATURN_ASPECTS = {3: '3rd', 7: '7th', 10: '10th'}


# ── TIMING (GROUP E) ──────────────────────────────────────────────────────────

# Dasa sandhi: changes of mahadasa of the two people that fall close together.
# The 12-month convention is the one stated at astrosight.ai; another page
# (sreenivasdesabhatla.wordpress.com) gives 6 months. The request can set it.
SANDHI_MONTHS_DEFAULT = 12
SANDHI_MONTHS_MAX = 36
SANDHI_YEARS_AHEAD = 30                     # changes later than this are not listed
MONTH_DAYS = A.YEAR_DAYS / 12
KP_MARRIAGE_HOUSES = (2, 7, 11)             # the KP houses of the Marriage topic in enrich.TOPICS
WINDOWS_IN_NOTE = 3                         # overlapping spans named in the row; all are in 'windows'

TABLE_SOURCES = [
    ('Checked against one or more published pages, which agree',
     'Dinam counts; Mahendram counts; Stree Deergham limits; the stars of each gana, yoni, rajju and nadi; '
     'the vedhai pairs; the same-star lists; the 27th-star rule; the 4th pada of the 22nd star; varna of the '
     'rasis; tara; Graha Maitri points; Bhakoot; the Nadi, Bhakoot and Gana exceptions.'),
    ('Published sources disagree; the variant used is named in the rule',
     'Gana points (two pages print the table with bride and groom exchanged); Vashya points (three cells '
     'differ between pages); Yoni points (two different 14 x 14 tables are in circulation); Vriksha (two '
     'pages print the milk and non-milk groups the opposite way round); the Tamil Rasi porutham rule for '
     'the counts 3, 4, 5, 9, 10 and 11; the exceptions to Kuja dosha (the lists differ widely); the weights '
     'of Papa samyam (one page counts every placement as 1, another weighs the house, the planet and its '
     'dignity; both figures given here use the plain count, the second weighted by the reference only).'),
    ('Written from memory of B.V. Raman, Muhurtha; not checked against the printed book',
     'The Tamil Vasiyam list; the seven exceptions to Kuja dosha.'),
    ('No single published rule; the rows state facts and give no result',
     'Kalathra dosha, Punarpoo, Kala Sarpa, the lagnas, the 7th lords, the navamsa, Venus and Mars, the 5th '
     'house; the dasas running together (the practice of avoiding one dasa lord for both at the same time '
     'was not found on a published page); the sub lord of the 7th cusp; the overlap of the marriage '
     'windows.'),
    ('Left out because no table could be checked', 'Pakshi and Bhutha porutham.'),
    ('Left out on purpose', 'Ayul porutham and the rules about particular stars and the in-laws.'),
]


# ── CHECKS: name, rule and variant of every row ───────────────────────────────

CHECKS = {
    # key: (group, name, rule, variant and what is not applied)
    'dinam': ('A', 'Dinam', 'The boy\'s star counted from the girl\'s star is 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, '
              '24 or 26.',
              'Tamil list of counts. The same star is judged by the same-star list and the 27th star by the '
              '27th-star rule, and the row says so. The rule "remainder by 9 is 2, 4, 6, 8 or 0" also passes '
              '17, 22 and 27 and is not used.'),
    'ganam': ('A', 'Ganam', 'Both of one gana, or the girl Manushya and the boy Deva: matched. The girl Deva '
              'and the boy Manushya: medium. Any other pair: not matched.',
              'The result follows the Ashtakoota gana points (6 matched, 5 medium, 1 or 0 not matched). '
              'Exceptions by the distance between the stars are not applied.'),
    'mahendram': ('A', 'Mahendram', 'The boy\'s star counted from the girl\'s star is 4, 7, 10, 13, 16, 19, 22 '
                  'or 25.', 'No variant.'),
    'stree_deergham': ('A', 'Stree Deergham', 'The boy\'s star counted from the girl\'s star is more than 13: '
                       'matched. More than 7: medium. Otherwise not matched.',
                       'Some authors take more than 9 as the lower limit; not used.'),
    'yoni': ('A', 'Yoni', 'The same animal: matched. Animals that are enemies (cow and tiger, elephant and lion, '
             'horse and buffalo, dog and deer, cat and rat, serpent and mongoose, sheep and monkey): not '
             'matched. Any other pair: medium.',
             'The male or female nature of the stars is not used.'),
    'rasi': ('A', 'Rasi', 'The boy\'s rasi counted from the girl\'s rasi: 1 or 7 matched; 2, 6, 8 or 12 not '
             'matched; 3, 4, 5, 9, 10 or 11 medium. The 7th is not accepted for Simha with Kumbha or Kataka '
             'with Makara.',
             'Tamil rule as printed at astroved.com. Authors differ on 3, 4, 5, 9, 10 and 11; B.V. Raman '
             'takes 7 to 12 as matched and 2 to 6 as not matched, which is not used. For 2/12 and 6/8 the '
             'exception "one lord for both rasis, or lords who are friends to each other" is named, and the '
             'result stays.'),
    'rasi_adhipathi': ('A', 'Rasi Adhipathi', 'The lords of the two rasis: one planet, or friends to each other: '
                       'matched. Friend and neutral, or both neutral: medium. An enemy on either side: not '
                       'matched.',
                       'Natural friendship as in BPHS, the table already used for the horoscope.'),
    'vasiyam': ('A', 'Vasiyam', 'The boy\'s rasi is vasya to the girl\'s rasi: matched. The girl\'s rasi is '
                'vasya to the boy\'s rasi: medium. Otherwise not matched.',
                'Vasya rasis: Mesha - Simha, Vrischika; Rishabha - Kataka, Thula; Mithuna - Kanya; Kataka - '
                'Vrischika, Dhanu; Simha - Thula; Kanya - Meena, Mithuna; Thula - Makara, Kanya; Vrischika - '
                'Kataka; Dhanu - Meena; Makara - Mesha, Kumbha; Kumbha - Mesha; Meena - Makara. The same '
                'rasi is not on the list.'),
    'rajju': ('A', 'Rajju', 'The two stars are in different rajju groups: matched. The same group: not matched.',
              'Five groups: Pada, Kati, Nabhi, Kantha, Siro. The rising and falling order inside a group is '
              'not used.'),
    'vedhai': ('A', 'Vedhai', 'The two stars are not a vedha pair: matched. A vedha pair: not matched.',
               'Mrigashira, Chitra and Dhanishtha are vedha to one another.'),
    'nadi': ('A', 'Nadi', 'The two stars are in different nadis: matched. The same nadi: not matched.',
             'Three nadis: Aadi, Madhya, Antya. The exceptions are named, and the result stays: the same '
             'rasi with different stars; the same star with different rasis; the same star with different '
             'padas.'),
    'vriksha': ('A', 'Vriksha', 'The tree of either star is a milk (paal) tree: matched. Neither: not matched.',
                'Milk trees are taken as the stars Krittika, Rohini, Pushya, Ashlesha, Magha, Purva Phalguni, '
                'Uttara Phalguni, Hasta, Jyeshtha, Moola, Purva Ashadha, Uttara Ashadha, Shravana, Purva '
                'Bhadrapada and Revati. One published page prints the two groups the other way round.'),
    'tara_boy': ('B', 'Tara of the boy\'s star', 'The tara of the boy\'s star counted from the girl\'s star: '
                 'Sampat, Kshema, Sadhaka, Mitra or Parama Mitra matched; Vipat, Pratyari or Vadha not '
                 'matched; Janma medium.', 'The nine taras repeat three times through the 27 stars.'),
    'tara_girl': ('B', 'Tara of the girl\'s star', 'The tara of the girl\'s star counted from the boy\'s star, '
                  'judged in the same way.', 'The nine taras repeat three times through the 27 stars.'),
    'vadha': ('B', 'Vadha (7th star)', 'The boy\'s star is not the 7th from the girl\'s star: matched. The 7th: '
              'not matched.',
              'When the boy\'s star is the 7th from the girl\'s, the girl\'s is the 22nd from the boy\'s. The '
              '16th and the 25th, which are also Vadha tara, are judged in the tara rows only. The pairs of '
              'stars some texts exempt are not applied.'),
    'vainasika': ('B', 'Vainasika (22nd star)', 'The boy\'s star is not the 22nd from the girl\'s star: matched. '
                  'The 22nd: not matched.',
                  'When the boy\'s star is the 22nd from the girl\'s, the girl\'s is the 7th from the boy\'s. '
                  'The pairs of stars some texts exempt are not applied.'),
    'vainasika_pada': ('B', 'Vainasika pada (88th pada)', 'The boy\'s Moon is not in the 4th pada of the 22nd '
                       'star from the girl\'s star: matched. In that pada: not matched.',
                       'That pada is the 88th counted from the first pada of the girl\'s star. Counting the '
                       '88th from the pada the girl\'s Moon is in is a variant and is not used.'),
    'star_27': ('B', '27th star', 'When the boy\'s star is the 27th from the girl\'s: both in one rasi matched; '
                'in different rasis not matched.', 'Does not arise for any other count.'),
    'eka_nakshatra': ('B', 'Same star', 'When both have one star: Rohini, Ardra, Magha, Hasta, Vishakha, '
                      'Shravana, Uttara Bhadrapada or Revati matched; Ashwini, Krittika, Mrigashira, Punarvasu, '
                      'Pushya, Purva Phalguni, Uttara Phalguni, Chitra, Anuradha, Purva Ashadha or Uttara '
                      'Ashadha medium; the other eight not matched.',
                      'Does not arise when the stars differ. The note says whether the padas are the same.'),
    'eka_rasi': ('B', 'Same rasi', 'When both have one rasi and different stars: the boy\'s star comes before '
                 'the girl\'s: matched; after it: medium.',
                 'Does not arise when the rasis differ; the same star is judged by the same-star row.'),
    'ak_varna': ('C', 'Varna (1)', 'The boy\'s varna is the same as or higher than the girl\'s: 1 point; '
                 'otherwise 0.',
                 'By rasi: Kataka, Vrischika, Meena highest; then Mesha, Simha, Dhanu; then Rishabha, Kanya, '
                 'Makara; then Mithuna, Thula, Kumbha. These are names of four classes of rasis.'),
    'ak_vashya': ('C', 'Vashya (2)', 'Points from the vashya groups of the two rasis, 0 to 2.',
                  'Groups: Chatushpada - Mesha, Rishabha, Dhanu from 15 degrees, Makara up to 15 degrees; '
                  'Manava - Mithuna, Kanya, Thula, Kumbha, Dhanu up to 15 degrees; Jalachara - Kataka, Meena, '
                  'Makara from 15 degrees; Vanachara - Simha; Keeta - Vrischika. Table of points as printed at '
                  'vedicmarga.com; another published table differs in three cells.'),
    'ak_tara': ('C', 'Tara (3)', 'Each way, the star counted from the other, remainder by 9: a remainder of 3, 5 '
                'or 7 scores nothing. Both ways good 3 points, one way 1.5, neither 0.', 'No variant.'),
    'ak_yoni': ('C', 'Yoni (4)', 'Points from the animals of the two stars, 0 to 4.',
                'Table as published at saravali.github.io; another published table differs in many cells.'),
    'ak_graha_maitri': ('C', 'Graha Maitri (5)', 'The lords of the two rasis: one planet or friends both ways 5; '
                        'friend and neutral 4; both neutral 3; friend and enemy 1; neutral and enemy 0.5; '
                        'enemies both ways 0.', 'Natural friendship as in BPHS.'),
    'ak_gana': ('C', 'Gana (6)', 'Points from the two ganas, 0 to 6: one gana 6; girl Manushya and boy Deva 6; '
                'girl Deva and boy Manushya 5; girl Deva and boy Rakshasa 1; every other pair 0.',
                'One published page prints this table with the bride and the groom exchanged. The exception '
                '"one lord for both rasis, or lords who are friends to each other" is named, and the points '
                'stay.'),
    'ak_bhakoot': ('C', 'Bhakoot (7)', 'The two rasis are 2/12, 5/9 or 6/8 from each other: 0 points. Otherwise '
                   '7.',
                   'The exception "one lord for both rasis, or lords who are friends to each other" is named, '
                   'and the points stay.'),
    'ak_nadi': ('C', 'Nadi (8)', 'Different nadis 8 points; the same nadi 0.',
                'The exceptions are named, and the points stay: the same rasi with different stars; the same '
                'star with different rasis; the same star with different padas.'),
    'kuja_lagna': ('D', 'Kuja dosha from the lagna', 'Mars in one of the places that count, from the lagna. '
                   'The row states the place for each; no result.',
                   'Places that count: 2, 4, 7, 8, 12 (Tamil practice) unless the request asks for 1, 4, 7, 8, '
                   '12 or 1, 2, 4, 7, 8, 12. Whole signs.'),
    'kuja_moon': ('D', 'Kuja dosha from the Moon', 'The same, counted from the Moon. No result.', 'As above.'),
    'kuja_venus': ('D', 'Kuja dosha from Venus', 'The same, counted from Venus. No result.', 'As above.'),
    **{key: ('D', f'Kuja exception: {name}', f'{name}. The row says for each chart whether the exception '
             'applies, and from which reference. No result.',
             'One of seven exceptions, as stated by B.V. Raman; other lists exist and are not applied.')
       for key, name, _, _ in KUJA_EXCEPTIONS},
    'kuja_balance': ('D', 'Kuja dosha in both charts', 'Present in both charts or in neither: matched. In one '
                     'only: not matched. Present means from the lagna, the Moon or Venus, before any exception.',
                     'How strong the dosha is, and from which reference, is not weighed.'),
    'kuja_balance_after': ('D', 'Kuja dosha in both charts, after the exceptions', 'The same comparison after '
                           'the seven exceptions: a place of Mars that an exception covers is not counted.',
                           'The exceptions for the 2nd, 12th, 4th, 7th and 8th cover only the reference from '
                           'which Mars is in that place; the other two cover every reference.'),
    'sarpa': ('D', 'Rahu and Ketu', 'Rahu or Ketu in the 1st, 2nd, 7th or 8th from the lagna. In both charts or '
              'in neither: matched. In one only: not matched.', 'Counted from the lagna only, by whole sign.'),
    'kalathra_seventh': ('D', 'Kalathra: planets in the 7th', 'Natural malefics (Sun, Mars, Saturn, Rahu, Ketu) '
                         'in the 7th from the lagna and from the Moon. No result.',
                         'Authors define Kalathra dosha differently; the three Kalathra rows state the facts '
                         'they use.'),
    'kalathra_lord': ('D', 'Kalathra: the 7th lord', 'The lord of the 7th from the lagna: its house, its '
                      'dignity, whether debilitated or combust. No result.', 'Whole-sign houses.'),
    'kalathra_venus': ('D', 'Kalathra: Venus', 'Venus: its house, its dignity, whether debilitated or combust, '
                       'and the natural malefics in its sign. No result.', 'Whole-sign houses.'),
    'papa_count': ('D', 'Papa samyam (count)', 'Sun, Mars, Saturn and Rahu in the 1st, 2nd, 4th, 7th, 8th or '
                   '12th from the lagna, from the Moon and from Venus, each placement counted as 1. The boy\'s '
                   'total equal to or more than the girl\'s: matched. Less: not matched.',
                   'Ketu is not counted. No reduction for dignity.'),
    'papa_weighted': ('D', 'Papa samyam (weighted)', 'The same placements, those from the lagna counted in '
                      'full, from the Moon as a half and from Venus as a quarter. The boy\'s total equal to or '
                      'more than the girl\'s: matched. Less: not matched.',
                      'The fuller scheme that also weighs the house, the planet and its dignity is not used.'),
    'punarpoo': ('D', 'Punarpoo (Saturn and the Moon)', 'Saturn and the Moon in one sign, Saturn aspecting the '
                 'Moon (3rd, 7th or 10th), or the two in each other\'s signs. No result.',
                 'Whole-sign aspects. Links through the stars of the two are not used.'),
    'kala_sarpa': ('D', 'Kala Sarpa', 'All seven planets on one side of the Rahu-Ketu axis, by longitude. No '
                   'result.', 'Popular, not in BPHS; the test used for the horoscope itself.'),
    'lagna_position': ('D', 'The two lagnas', 'The lagna and its lord in each chart; the note gives the place '
                       'of each lagna from the other and how the lords regard each other. No result.',
                       'Natural friendship as in BPHS.'),
    'seventh_lords': ('D', 'The 7th lords', 'The 7th lord of each chart and how it regards the lagna lord of '
                      'the other. No result.', 'Natural friendship as in BPHS.'),
    'navamsa': ('D', 'Navamsa (D9)', 'The navamsa lagna and the navamsa sign of the Moon in each chart; the '
                'note gives their places from each other. No result.', 'No variant.'),
    'venus_mars': ('D', 'Venus and Mars across the charts', 'The signs of Venus and Mars in each chart; the note '
                   'gives the place of each one\'s Mars from the other\'s Venus. No result.', 'No variant.'),
    'fifth_house': ('D', 'The 5th house and Jupiter', 'The 5th house from the lagna: its sign, its lord and the '
                    'lord\'s house and dignity, the planets in it; and Jupiter\'s house and dignity. No result.',
                    'Whole-sign houses.'),
    'dasa_sandhi': ('E', 'Dasa sandhi', 'No change of mahadasa of the boy falls within the set number of months '
                    'of a change of mahadasa of the girl: matched. One or more such pairs: not matched.',
                    'Vimshottari mahadasa only. 12 months unless the request sets another figure (1 to 36). '
                    'Changes from the report date to 30 years ahead are compared. Each row value lists that '
                    'person\'s changes with the date at the birth place.'),
    'eka_dasa': ('E', 'Dasas running together', 'The mahadasa lord of each on the report date, and the spans of '
                 'the next 30 years in which both run the mahadasa of one planet. No result.',
                 'Some families avoid one dasa lord for both at the same time; no published rule was found, '
                 'so the row states the facts.'),
    'kp_seventh': ('E', 'KP: sub lord of the 7th cusp', 'The sub lord of the 7th cusp of each chart, the houses '
                   'it signifies, and whether 2, 7 or 11 is among them. No result.',
                   'KP ayanamsha and Placidus cusps, four-level significators as on the KP sheet. Rahu and '
                   'Ketu also act for their sign lord and the planets with them, which is not added here.'),
    'marriage_windows': ('E', 'Marriage windows of both', 'The spans of the next 10 years in which a Marriage '
                         'window of the boy\'s horoscope and one of the girl\'s overlap. No result.',
                         'A window is a span of AI_TopicWindows for the topic Marriage: two or more of bhukti, '
                         'antaram, Jupiter and Saturn agreeing. Rule-based overlap, not a prediction. The row '
                         'names the first spans; all are in "windows".'),
}

MATCH_RULES = [(f'{GROUPS[group].split(" (")[0]}: {name}', f'{rule} {variant}')
               for group, name, rule, variant in CHECKS.values()]
MATCH_RULES += [
    ('Direction of counting', 'Stars and rasis are counted from the girl\'s to the boy\'s, the starting one '
     'counted as 1, unless the rule names the other direction.'),
    ('Results', 'matched, medium, not matched: the rule as written above. not applicable: the rule does not '
     'arise for this pair, or a fact it needs was not given. information: a fact with no rule of comparison. '
     'Exceptions are named and never change a result or the points.'),
    ('Summary', 'Counts of the results; the ten poruthams counted separately; the Ashtakoota points out of 36; '
     'and which of Rajju, Dinam, Ganam, Yoni and Rasi are not matched. No overall verdict is given.'),
]

NOT_INCLUDED = [
    'Pakshi and Bhutha porutham: no table could be checked',
    'Ayul porutham, and anything about length of life: left out on purpose',
    'Rules about particular stars of the bride and her in-laws: left out on purpose',
    'Remedies; a verdict on whether to marry',
]


# ── PEOPLE ────────────────────────────────────────────────────────────────────

def _index(value, names, what):
    """A number from 1, or an engine name, as a 0-based index."""
    if isinstance(value, bool) or value in (None, ''):
        raise InputError(f'The {what} is required.')
    if isinstance(value, (int, float)) or str(value).strip().lstrip('-').isdigit():
        n = int(value)
        if n != float(value) or not 1 <= n <= len(names):
            raise InputError(f'The {what} must be a whole number from 1 to {len(names)}.')
        return n - 1
    wanted = ''.join(str(value).lower().split())
    for i, name in enumerate(names):
        if ''.join(name.lower().split()) == wanted:
            return i
    raise InputError(f'"{value}" is not a {what} this service knows.')


def star_person(record, role):
    """
    A star-only record {nakshatra, pada, rasi, name} as a person.

    nakshatra: 1 to 27 or its name; pada: 1 to 4, may be left out;
    rasi: 1 to 12 or its name, needed only for a star that lies in two
    rasis when the pada is not given.
    """
    if not isinstance(record, dict):
        raise InputError(f'The details of the {role} must be a JSON object.')
    nak = _index(record.get('nakshatra'), NAKS, f'{role}\'s nakshatra')
    pada = record.get('pada')
    if pada in (None, ''):
        pada = None
    else:
        if isinstance(pada, bool) or not str(pada).strip().isdigit() or not 1 <= int(pada) <= 4:
            raise InputError(f'The {role}\'s pada must be 1, 2, 3 or 4.')
        pada = int(pada)
    possible = sorted({(nak * 4 + p) // 9 for p in range(4)})
    given = record.get('rasi')
    rasi = None if given in (None, '') else _index(given, RASIS, f'{role}\'s rasi')
    if pada is not None:
        own = (nak * 4 + pada - 1) // 9
        if rasi is not None and rasi != own:
            raise InputError(f'{NAKS[nak]} pada {pada} is in {RASIS[own]}, not in {RASIS[rasi]}.')
        rasi = own
    elif rasi is None:
        if len(possible) > 1:
            names = ' and '.join(RASIS[r] for r in possible)
            raise InputError(f'{NAKS[nak]} lies in {names}: give the {role}\'s pada or rasi.')
        rasi = possible[0]
    elif rasi not in possible:
        names = ' or '.join(RASIS[r] for r in possible)
        raise InputError(f'{NAKS[nak]} is in {names}, not in {RASIS[rasi]}.')
    name = str(record.get('name') or '').strip()[:80] or role.capitalize()
    return {'role': role, 'name': name, 'nak': nak, 'pada': pada, 'rasi': rasi, 'moon_lon': None,
            'res': None, 'source': 'star only'}


def chart_person(res, role):
    """A result of compute() as a person."""
    moon = next(p for p in res['vedic']['planets'] if p['name'] == 'Moon')
    return {'role': role, 'name': res['meta']['name'] or role.capitalize(), 'nak': moon['nak'],
            'pada': moon['pada'], 'rasi': moon['sign'], 'moon_lon': moon['lon'], 'res': res,
            'source': 'birth details'}


def as_person(source, role):
    if isinstance(source, dict) and 'vedic' in source and 'meta' in source:
        return chart_person(source, role)
    return star_person(source, role)


def person_facts(p):
    """What the report shows about one person."""
    out = {
        'role': p['role'], 'name': p['name'], 'source': p['source'],
        'nakshatra': NAKS[p['nak']], 'nakshatra_number': p['nak'] + 1, 'pada': p['pada'],
        'rasi': RASIS[p['rasi']], 'rasi_number': p['rasi'] + 1,
        'rasi_lord': SIGN_LORDS[p['rasi']], 'nakshatra_lord': A.NAK_LORDS[p['nak']],
    }
    if p['res']:
        m, v = p['res']['meta'], p['res']['vedic']
        out.update({'dob': m['dob'], 'tob': m['tob'], 'pob': m['pob'], 'utc_offset': m['utc_offset_str'],
                    'lagna': RASIS[v['lagna_sign']], 'lagna_number': v['lagna_sign'] + 1,
                    'ayanamsha': m['ayanamsha_name'], 'node': m['node']})
    return out


# ── SMALL HELPERS ─────────────────────────────────────────────────────────────

def count(start, end, size=27):
    """Places from start to end, the start counted as 1."""
    return (end - start) % size + 1


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        return f'{n}th'
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')


def _star(p):
    return NAKS[p['nak']] + (f' pada {p["pada"]}' if p['pada'] else '')


def _whole(x):
    """36.0 -> 36; 20.5 stays."""
    return int(x) if float(x).is_integer() else x


def lords_relation(lord_a, lord_b):
    """(how a regards b, how b regards a); 'Same' both ways for one planet."""
    if lord_a == lord_b:
        return 'Same', 'Same'
    return E.natural_relation(lord_a, lord_b), E.natural_relation(lord_b, lord_a)


def lords_friendly(lord_a, lord_b):
    """One lord for both, or lords who are friends to each other."""
    return lords_relation(lord_a, lord_b) in (('Same', 'Same'), ('Friend', 'Friend'))


def vashya_group(p):
    """Vashya group of a person's Moon, or None when the degree is needed and not known."""
    group = VASHYA_GROUP[RASIS[p['rasi']]]
    if isinstance(group, str):
        return group
    if p['moon_lon'] is not None:
        return group[0] if A.norm(p['moon_lon']) % 30 < 15 else group[1]
    if p['pada'] is None:
        return None
    start = ((p['nak'] * 4 + p['pada'] - 1) % 9) * A.PADA_SIZE        # where the pada starts in its rasi
    if start + A.PADA_SIZE <= 15:
        return group[0]
    return group[1] if start >= 15 else None


def yoni_points(a, b):
    return YONI_POINTS[YONI_ORDER.index(a)][YONI_ORDER.index(b)]


def yoni_enemies(a, b):
    return (a, b) in YONI_ENEMIES or (b, a) in YONI_ENEMIES


def _by_points(points, top):
    return MATCHED if points == top else (NOT_MATCHED if points == 0 else MEDIUM)


# ── THE CHECKS ────────────────────────────────────────────────────────────────

class Pair:
    """The two people and the counts every rule reads."""

    def __init__(self, boy, girl):
        self.boy, self.girl = boy, girl
        self.n = count(girl['nak'], boy['nak'])              # boy's star from the girl's
        self.m = count(boy['nak'], girl['nak'])              # girl's star from the boy's
        self.r = count(girl['rasi'], boy['rasi'], 12)        # boy's rasi from the girl's
        self.same_star = boy['nak'] == girl['nak']
        self.same_rasi = boy['rasi'] == girl['rasi']
        self.boy_rasi, self.girl_rasi = RASIS[boy['rasi']], RASIS[girl['rasi']]
        self.boy_lord, self.girl_lord = SIGN_LORDS[boy['rasi']], SIGN_LORDS[girl['rasi']]
        self.relation = lords_relation(self.boy_lord, self.girl_lord)
        self.friendly = lords_friendly(self.boy_lord, self.girl_lord)
        self.rows = []

    def add(self, key, boy_value, girl_value, result, points=None, max_points=None, exception='', note=''):
        group, name, rule, _ = CHECKS[key]
        if isinstance(points, float) and points.is_integer():
            points = int(points)
        self.rows.append({
            'key': key, 'group': group, 'name': name, 'boy_value': boy_value, 'girl_value': girl_value,
            'result': result, 'points': points, 'max_points': max_points, 'rule_applied': rule,
            'exception_applied': exception or None, 'note': note or None,
        })

    def lords_exception(self):
        if self.boy_lord == self.girl_lord:
            return f'One lord for both rasis ({self.boy_lord})'
        if self.friendly:
            return f'The rasi lords are friends to each other ({self.boy_lord}, {self.girl_lord})'
        return ''

    def nadi_exception(self):
        boy, girl = self.boy, self.girl
        if self.same_rasi and not self.same_star:
            return 'The same rasi with different stars'
        if self.same_star and not self.same_rasi:
            return 'The same star with different rasis'
        if self.same_star and boy['pada'] and girl['pada'] and boy['pada'] != girl['pada']:
            return 'The same star with different padas'
        return ''


def _count_note(pair):
    return f'The boy\'s star is the {_ordinal(pair.n)} from the girl\'s star'


def _group_a(pair):
    boy, girl, n, r = pair.boy, pair.girl, pair.n, pair.r
    b_star, g_star = _star(boy), _star(girl)

    # Dinam
    exception = ''
    if pair.same_star:
        result = SAME_STAR[boy['nak']]
        exception = 'The same star: judged by the same-star list'
    elif n == 27:
        result = MATCHED if pair.same_rasi else NOT_MATCHED
        exception = 'The 27th star: judged by the 27th-star rule'
    else:
        result = MATCHED if n in DINAM_COUNTS else NOT_MATCHED
    pair.add('dinam', b_star, g_star, result, exception=exception, note=_count_note(pair))

    # Ganam
    b_gana, g_gana = GANA[boy['nak']], GANA[girl['nak']]
    points = GANA_POINTS[g_gana][b_gana]
    pair.add('ganam', b_gana, g_gana, MATCHED if points == 6 else (MEDIUM if points == 5 else NOT_MATCHED))

    pair.add('mahendram', b_star, g_star, MATCHED if n in MAHENDRAM_COUNTS else NOT_MATCHED,
             note=_count_note(pair))

    result = (MATCHED if n > STREE_DEERGHAM_FULL else
              MEDIUM if n > STREE_DEERGHAM_MEDIUM else NOT_MATCHED)
    pair.add('stree_deergham', b_star, g_star, result, note=_count_note(pair))

    # Yoni
    b_yoni, g_yoni = YONI[boy['nak']], YONI[girl['nak']]
    result = MATCHED if b_yoni == g_yoni else (NOT_MATCHED if yoni_enemies(b_yoni, g_yoni) else MEDIUM)
    pair.add('yoni', b_yoni, g_yoni, result)

    # Rasi
    exception = ''
    if r in RASI_MATCHED:
        result = MATCHED
        if r == 7 and frozenset((pair.boy_rasi, pair.girl_rasi)) in RASI_SEVENTH_NOT_ACCEPTED:
            result = NOT_MATCHED
            exception = f'The 7th is not accepted for {pair.girl_rasi} with {pair.boy_rasi}'
    elif r in RASI_NOT_MATCHED:
        result = NOT_MATCHED
        exception = pair.lords_exception()
    else:
        result = MEDIUM
    pair.add('rasi', pair.boy_rasi, pair.girl_rasi, result, exception=exception,
             note=f'The boy\'s rasi is the {_ordinal(r)} from the girl\'s rasi')

    # Rasi Adhipathi
    relation = set(pair.relation)
    if relation <= {'Same', 'Friend'}:
        result = MATCHED
    elif 'Enemy' in relation:
        result = NOT_MATCHED
    else:
        result = MEDIUM
    if pair.boy_lord == pair.girl_lord:
        note = 'One planet rules both rasis'
    else:
        note = (f'{pair.boy_lord} regards {pair.girl_lord} as {pair.relation[0].lower()}; '
                f'{pair.girl_lord} regards {pair.boy_lord} as {pair.relation[1].lower()}')
    pair.add('rasi_adhipathi', pair.boy_lord, pair.girl_lord, result, note=note)

    # Vasiyam
    if pair.boy_rasi in VASYA[pair.girl_rasi]:
        result, note = MATCHED, f'{pair.boy_rasi} is vasya to {pair.girl_rasi}'
    elif pair.girl_rasi in VASYA[pair.boy_rasi]:
        result, note = MEDIUM, f'{pair.girl_rasi} is vasya to {pair.boy_rasi}'
    else:
        result, note = NOT_MATCHED, 'Neither rasi is vasya to the other'
    pair.add('vasiyam', pair.boy_rasi, pair.girl_rasi, result, note=note)

    b_rajju, g_rajju = RAJJU[boy['nak']], RAJJU[girl['nak']]
    pair.add('rajju', b_rajju, g_rajju, NOT_MATCHED if b_rajju == g_rajju else MATCHED)

    vedha = not pair.same_star and VEDHA[boy['nak']] == VEDHA[girl['nak']]
    pair.add('vedhai', b_star, g_star, NOT_MATCHED if vedha else MATCHED,
             note='The two stars are a vedha pair' if vedha else 'The two stars are not a vedha pair')

    b_nadi, g_nadi = NADI[boy['nak']], NADI[girl['nak']]
    same = b_nadi == g_nadi
    pair.add('nadi', b_nadi, g_nadi, NOT_MATCHED if same else MATCHED,
             exception=pair.nadi_exception() if same else '')

    def tree(p):
        return f'{TREE[p["nak"]]} ({"milk tree" if PAAL[p["nak"]] else "not a milk tree"})'
    either = PAAL[boy['nak']] or PAAL[girl['nak']]
    pair.add('vriksha', tree(boy), tree(girl), MATCHED if either else NOT_MATCHED)


def _tara(number):
    """(name, result) of a tara, 1 to 9."""
    label = E.TARA_LABELS[number - 1]
    return E.TARA_NAMES[number - 1], {'favourable': MATCHED, 'unfavourable': NOT_MATCHED}.get(label, MEDIUM)


def _group_b(pair):
    boy, girl, n, m = pair.boy, pair.girl, pair.n, pair.m
    b_star, g_star = _star(boy), _star(girl)

    name, result = _tara((n - 1) % 9 + 1)
    pair.add('tara_boy', name, g_star, result, note=_count_note(pair))
    name, result = _tara((m - 1) % 9 + 1)
    pair.add('tara_girl', b_star, name, result,
             note=f'The girl\'s star is the {_ordinal(m)} from the boy\'s star')

    both = f'{_count_note(pair)}; the girl\'s star is the {_ordinal(m)} from the boy\'s star'
    pair.add('vadha', b_star, g_star, NOT_MATCHED if n == 7 else MATCHED, note=both)
    pair.add('vainasika', b_star, g_star, NOT_MATCHED if n == 22 else MATCHED, note=both)

    if n != 22:
        pair.add('vainasika_pada', b_star, g_star, MATCHED, note=_count_note(pair))
    elif boy['pada'] is None:
        pair.add('vainasika_pada', b_star, g_star, NOT_APPLICABLE,
                 note='The boy\'s star is the 22nd from the girl\'s star and his pada was not given')
    else:
        pair.add('vainasika_pada', b_star, g_star, NOT_MATCHED if boy['pada'] == 4 else MATCHED,
                 note=f'The boy\'s star is the 22nd from the girl\'s star; his Moon is in pada {boy["pada"]}')

    if n == 27:
        pair.add('star_27', pair.boy_rasi, pair.girl_rasi, MATCHED if pair.same_rasi else NOT_MATCHED,
                 note='Both in one rasi' if pair.same_rasi else 'In different rasis')
    else:
        pair.add('star_27', b_star, g_star, NOT_APPLICABLE, note=_count_note(pair))

    if pair.same_star:
        if boy['pada'] and girl['pada']:
            note = 'The padas are the same' if boy['pada'] == girl['pada'] else 'The padas are different'
        else:
            note = 'A pada was not given'
        pair.add('eka_nakshatra', b_star, g_star, SAME_STAR[boy['nak']], note=note)
    else:
        pair.add('eka_nakshatra', b_star, g_star, NOT_APPLICABLE, note='The stars are different')

    if not pair.same_rasi:
        pair.add('eka_rasi', pair.boy_rasi, pair.girl_rasi, NOT_APPLICABLE, note='The rasis are different')
    elif pair.same_star:
        pair.add('eka_rasi', b_star, g_star, NOT_APPLICABLE, note='The same star: see the same-star row')
    else:
        first = boy['nak'] < girl['nak']         # inside one rasi the stars run in order
        pair.add('eka_rasi', b_star, g_star, MATCHED if first else MEDIUM,
                 note=f'The boy\'s star comes {"before" if first else "after"} the girl\'s in {pair.boy_rasi}')


def _group_c(pair):
    boy, girl, n, m = pair.boy, pair.girl, pair.n, pair.m

    b_varna, g_varna = VARNA[pair.boy_rasi], VARNA[pair.girl_rasi]
    points = 1 if VARNA_ORDER.index(b_varna) <= VARNA_ORDER.index(g_varna) else 0
    pair.add('ak_varna', b_varna, g_varna, _by_points(points, 1), points, 1)

    b_group, g_group = vashya_group(boy), vashya_group(girl)
    if b_group and g_group:
        points = VASHYA_POINTS[g_group][b_group]
        pair.add('ak_vashya', b_group, g_group, _by_points(points, 2), points, 2)
    else:
        pair.add('ak_vashya', b_group or pair.boy_rasi, g_group or pair.girl_rasi, NOT_APPLICABLE, None, 2,
                 note='The degree of the Moon is needed: Dhanu and Makara change group at 15 degrees')

    good_boy, good_girl = n % 9 not in TARA_BAD, m % 9 not in TARA_BAD
    points = 1.5 * (good_boy + good_girl)
    pair.add('ak_tara', E.TARA_NAMES[(n - 1) % 9], E.TARA_NAMES[(m - 1) % 9], _by_points(points, 3), points, 3,
             note=f'{_count_note(pair)}; the girl\'s star is the {_ordinal(m)} from the boy\'s star')

    b_yoni, g_yoni = YONI[boy['nak']], YONI[girl['nak']]
    points = yoni_points(g_yoni, b_yoni)
    pair.add('ak_yoni', b_yoni, g_yoni, _by_points(points, 4), points, 4)

    relation = pair.relation
    points = 5 if relation == ('Same', 'Same') else MAITRI_POINTS[frozenset(relation)]
    pair.add('ak_graha_maitri', pair.boy_lord, pair.girl_lord, _by_points(points, 5), points, 5,
             note='One planet rules both rasis' if relation == ('Same', 'Same') else
             f'{pair.boy_lord} regards {pair.girl_lord} as {relation[0].lower()}; '
             f'{pair.girl_lord} regards {pair.boy_lord} as {relation[1].lower()}')

    b_gana, g_gana = GANA[boy['nak']], GANA[girl['nak']]
    points = GANA_POINTS[g_gana][b_gana]
    pair.add('ak_gana', b_gana, g_gana, _by_points(points, 6), points, 6,
             exception=pair.lords_exception() if points < 6 else '')

    kind = BHAKOOT_BAD.get(pair.r)
    points = 0 if kind else 7
    pair.add('ak_bhakoot', pair.boy_rasi, pair.girl_rasi, _by_points(points, 7), points, 7,
             exception=pair.lords_exception() if kind else '',
             note=f'The rasis are {kind} from each other' if kind else
             f'The boy\'s rasi is the {_ordinal(pair.r)} from the girl\'s rasi')

    b_nadi, g_nadi = NADI[boy['nak']], NADI[girl['nak']]
    points = 0 if b_nadi == g_nadi else 8
    pair.add('ak_nadi', b_nadi, g_nadi, _by_points(points, 8), points, 8,
             exception=pair.nadi_exception() if points == 0 else '')


# ── GROUP D: CHART CHECKS ─────────────────────────────────────────────────────

def clean_options(raw=None):
    """
    Settings of a match. Raises InputError.
      kuja_houses:   'south' (the default), 'north' or 'all'
      sandhi_months: 1 to 36, how close two changes of mahadasa must be to count (default 12)
    """
    raw = raw or {}
    if not isinstance(raw, dict):
        raise InputError('The matching options must be a JSON object.')
    kuja = str(raw.get('kuja_houses') or KUJA_DEFAULT).strip().lower()
    if kuja not in KUJA_HOUSE_SETS:
        raise InputError('"kujaHouses" must be "south" (2, 4, 7, 8, 12), "north" (1, 4, 7, 8, 12) or "all" '
                         '(1, 2, 4, 7, 8, 12).')
    months = raw.get('sandhi_months')
    if months in (None, ''):
        months = SANDHI_MONTHS_DEFAULT
    elif (isinstance(months, bool) or not str(months).strip().isdigit()
          or not 1 <= int(months) <= SANDHI_MONTHS_MAX):
        raise InputError(f'"sandhiMonths" must be a whole number from 1 to {SANDHI_MONTHS_MAX}.')
    return {'kuja_houses': kuja, 'sandhi_months': int(months)}


def _house_text(n):
    return f'the {_ordinal(n)}'


def _dignity_text(c, planet):
    label, debilitated = c.dignity['D1'][planet]
    out = label.lower()
    if debilitated:
        out += ', debilitated'
    if c.combust(planet):
        out += ', combust'
    return out


def kuja_state(c, houses):
    """
    Kuja dosha of one chart. present / after: the references from which Mars
    is in a place that counts, before and after the exceptions; exceptions:
    {key: references it covers}.
    """
    mars = RASIS[c.sign['Mars']]
    joined = [p for p in ('Jupiter', 'Moon') if c.sign[p] == c.sign['Mars']]
    places = dict(E.kuja_places(c))
    present = [ref for ref, place in places.items() if place in houses]
    exceptions = {}
    for key, _, place, signs in KUJA_EXCEPTIONS:
        if key == 'kuja_x_joined':
            covered = present if joined else []
        else:
            covered = [ref for ref in present if mars in signs and place in (None, places[ref])]
        exceptions[key] = covered
    cancelled = {ref for refs in exceptions.values() for ref in refs}
    return {'places': places, 'present': present, 'exceptions': exceptions, 'mars': mars, 'joined': joined,
            'after': [ref for ref in present if ref not in cancelled]}


def papa_points(c):
    """Papa samyam of one chart: {reference: [(planet, place)]} for the placements that count."""
    refs = (('the lagna', c.lagna_sign), ('the Moon', c.moon_sign), ('Venus', c.sign['Venus']))
    return {ref: [(p, E.house_from(c.sign[p], ref_sign)) for p in PAPA_PLANETS
                  if E.house_from(c.sign[p], ref_sign) in PAPA_HOUSES] for ref, ref_sign in refs}


def punarpoo(c):
    """The links between Saturn and the Moon in one chart, in words."""
    links = []
    place = E.house_from(c.sign['Moon'], c.sign['Saturn'])
    if place == 1:
        links.append('Saturn and the Moon in one sign')
    elif place in SATURN_ASPECTS:
        links.append(f'Saturn aspects the Moon ({SATURN_ASPECTS[place]} aspect)')
    if c.exchange('Saturn', 'Moon'):
        links.append('Saturn and the Moon in each other\'s signs')
    return links


def _group_d(pair, options):
    boy, girl = pair.boy, pair.girl
    keys = [k for k, v in CHECKS.items() if v[0] == 'D']
    if not (boy['res'] and girl['res']):
        for key in keys:
            pair.add(key, None, None, NOT_APPLICABLE, note='The birth details of both are needed')
        return
    b, g = E.Ctx(boy['res']), E.Ctx(girl['res'])

    def both(key, fn, result=INFORMATION, **kw):
        pair.add(key, fn(b), fn(g), result, **kw)

    # Kuja dosha
    houses = KUJA_HOUSE_SETS[options['kuja_houses']]
    kb, kg = kuja_state(b, houses), kuja_state(g, houses)
    for key, ref in (('kuja_lagna', 'the lagna'), ('kuja_moon', 'the Moon'), ('kuja_venus', 'Venus')):
        def placed(k, ref=ref):
            return (f'Mars in {_house_text(k["places"][ref])} from {ref}: '
                    f'{"present" if ref in k["present"] else "absent"}')
        pair.add(key, placed(kb), placed(kg), INFORMATION,
                 note='Places that count: ' + ', '.join(str(h) for h in houses))
    for key, _, _, _ in KUJA_EXCEPTIONS:
        def applies(k, key=key):
            if not k['present']:
                return 'does not arise: no Kuja dosha'
            covered = k['exceptions'][key]
            return 'applies from ' + ', '.join(covered) if covered else 'does not apply'
        pair.add(key, applies(kb), applies(kg), INFORMATION)

    def state(refs):
        return 'present from ' + ', '.join(refs) if refs else 'absent'
    pair.add('kuja_balance', state(kb['present']), state(kg['present']),
             MATCHED if bool(kb['present']) == bool(kg['present']) else NOT_MATCHED,
             note=f'Mars: the boy\'s in {kb["mars"]}, the girl\'s in {kg["mars"]}')
    used = [name for key, name, _, _ in KUJA_EXCEPTIONS if kb['exceptions'][key] or kg['exceptions'][key]]
    pair.add('kuja_balance_after', state(kb['after']), state(kg['after']),
             MATCHED if bool(kb['after']) == bool(kg['after']) else NOT_MATCHED,
             exception='; '.join(used))

    # Rahu and Ketu
    def nodes(c):
        return [n for n in ('Rahu', 'Ketu') if c.house[n] in SARPA_HOUSES]

    def nodes_text(c):
        where = f'Rahu in {_house_text(c.house["Rahu"])}, Ketu in {_house_text(c.house["Ketu"])} from the lagna'
        return f'{where}: {"present" if nodes(c) else "absent"}'
    both('sarpa', nodes_text, MATCHED if bool(nodes(b)) == bool(nodes(g)) else NOT_MATCHED)

    # Kalathra facts
    def seventh(c):
        lagna = [p for p in E.NATURAL_MALEFICS if c.house[p] == 7]
        moon = [p for p in E.NATURAL_MALEFICS if E.house_from(c.sign[p], c.moon_sign) == 7]
        return f'From the lagna: {", ".join(lagna) or "none"}; from the Moon: {", ".join(moon) or "none"}'
    both('kalathra_seventh', seventh)

    def seventh_lord(c):
        lord = c.house_lord[7]
        return f'{lord} in {_house_text(c.house[lord])} house, {_dignity_text(c, lord)}'
    both('kalathra_lord', seventh_lord)

    def venus(c):
        mates = [p for p in E.NATURAL_MALEFICS if c.sign[p] == c.sign['Venus']]
        return (f'In {_house_text(c.house["Venus"])} house, {_dignity_text(c, "Venus")}; '
                f'malefics in its sign: {", ".join(mates) or "none"}')
    both('kalathra_venus', venus)

    # Papa samyam
    pb, pg = papa_points(b), papa_points(g)

    def tally(points):
        return '; '.join(f'from {ref} {len(found)}' + (' (' + ', '.join(f'{p} {_ordinal(h)}' for p, h in found) + ')'
                                                         if found else '') for ref, found in points.items())

    def total(points, weighted):
        return _whole(sum(len(points[ref]) * (w if weighted else 1) for ref, w in PAPA_WEIGHTS))
    for key, weighted in (('papa_count', False), ('papa_weighted', True)):
        tb, tg = total(pb, weighted), total(pg, weighted)
        pair.add(key, f'{tb}: {tally(pb)}', f'{tg}: {tally(pg)}', MATCHED if tb >= tg else NOT_MATCHED,
                 note=f'The boy\'s total is {tb}, the girl\'s {tg}')

    both('punarpoo', lambda c: 'present: ' + '; '.join(punarpoo(c)) if punarpoo(c) else 'absent')
    both('kala_sarpa', lambda c: 'found' if E.kala_sarpa(c)[0] else 'not found')

    # The lagnas and their lords
    bl, gl = b.house_lord[1], g.house_lord[1]
    rel = lords_relation(bl, gl)
    lords = ('One planet rules both lagnas' if bl == gl else
             f'{bl} regards {gl} as {rel[0].lower()}; {gl} regards {bl} as {rel[1].lower()}')
    pair.add('lagna_position', f'{RASIS[b.lagna_sign]}, lord {bl}', f'{RASIS[g.lagna_sign]}, lord {gl}',
             INFORMATION,
             note=f'The boy\'s lagna is {_house_text(count(g.lagna_sign, b.lagna_sign, 12))} from the girl\'s; '
                  f'the girl\'s is {_house_text(count(b.lagna_sign, g.lagna_sign, 12))} from the boy\'s. {lords}')

    def seventh_to(c, other):
        lord, other_lord = c.house_lord[7], other.house_lord[1]
        if lord == other_lord:
            return f'{lord}: the lagna lord of the other chart'
        return f'{lord}: regards the other\'s lagna lord {other_lord} as {E.natural_relation(lord, other_lord).lower()}'
    pair.add('seventh_lords', seventh_to(b, g), seventh_to(g, b), INFORMATION)

    def d9(c):
        signs = c.vargas['D9']['signs']
        return signs['Lagna'], signs['Moon']
    (b_lagna, b_moon), (g_lagna, g_moon) = d9(b), d9(g)
    pair.add('navamsa', f'D9 lagna {RASIS[b_lagna]}, D9 Moon {RASIS[b_moon]}',
             f'D9 lagna {RASIS[g_lagna]}, D9 Moon {RASIS[g_moon]}', INFORMATION,
             note=f'The boy\'s D9 lagna is {_house_text(count(g_lagna, b_lagna, 12))} from the girl\'s D9 lagna; '
                  f'the boy\'s D9 Moon is {_house_text(count(g_moon, b_moon, 12))} from the girl\'s D9 Moon')

    def venus_mars(c):
        return f'Venus in {RASIS[c.sign["Venus"]]}, Mars in {RASIS[c.sign["Mars"]]}'
    pair.add('venus_mars', venus_mars(b), venus_mars(g), INFORMATION,
             note=f'The girl\'s Mars is {_house_text(count(b.sign["Venus"], g.sign["Mars"], 12))} from the '
                  f'boy\'s Venus; the boy\'s Mars is {_house_text(count(g.sign["Venus"], b.sign["Mars"], 12))} '
                  f'from the girl\'s Venus')

    def fifth(c):
        lord = c.house_lord[5]
        inside = [p for p in E.PLANETS if c.house[p] == 5]
        return (f'{RASIS[c.house_sign[5]]}; lord {lord} in {_house_text(c.house[lord])} house, '
                f'{_dignity_text(c, lord)}; planets in the 5th: {", ".join(inside) or "none"}; '
                f'Jupiter in {_house_text(c.house["Jupiter"])} house, {_dignity_text(c, "Jupiter")}')
    both('fifth_house', fifth)


# ── GROUP E: TIMING AND KP ────────────────────────────────────────────────────

def _offset(res):
    """UTC offset in force at birth, as a timedelta: local = UTC + offset."""
    return res['meta']['local_dt'] - res['meta']['ut_dt']


def _report_utc(res):
    return res['meta']['generated_at'] - _offset(res)


def dasa_changes(res, start_utc, end_utc):
    """Changes of mahadasa after start_utc up to end_utc: [{'from', 'to', 'local', 'utc'}]."""
    dasas = res['vedic']['dasa']['dasas']
    off = _offset(res)
    out = []
    for old, new in zip(dasas, dasas[1:]):
        utc = new['start'] - off
        if start_utc < utc <= end_utc:
            out.append({'from': old['lord'], 'to': new['lord'], 'local': new['start'], 'utc': utc})
    return out


def sandhi_pairs(boy_changes, girl_changes, months):
    """The pairs of changes that fall within the set number of months of each other."""
    limit = months * MONTH_DAYS
    pairs = []
    for bc in boy_changes:
        for gc in girl_changes:
            days = abs((bc['utc'] - gc['utc']).total_seconds()) / 86400.0
            if days <= limit:
                pairs.append({'boy': bc, 'girl': gc, 'months_apart': round(days / MONTH_DAYS, 1)})
    return pairs


def shared_dasa_spans(boy_res, girl_res, start_utc, end_utc):
    """Spans between start_utc and end_utc in which both run the mahadasa of one planet."""
    spans = []
    for bd in boy_res['vedic']['dasa']['dasas']:
        for gd in girl_res['vedic']['dasa']['dasas']:
            if bd['lord'] != gd['lord']:
                continue
            lo = max(bd['start'] - _offset(boy_res), gd['start'] - _offset(girl_res), start_utc)
            hi = min(bd['end'] - _offset(boy_res), gd['end'] - _offset(girl_res), end_utc)
            if lo < hi:
                spans.append({'lord': bd['lord'], 'start_utc': lo, 'end_utc': hi})
    return sorted(spans, key=lambda x: x['start_utc'])


def dasa_lord_at(res, moment_utc):
    off = _offset(res)
    for d in res['vedic']['dasa']['dasas']:
        if d['start'] - off <= moment_utc < d['end'] - off:
            return d['lord']
    return None


def kp_seventh(res):
    """(sub lord of the 7th cusp, houses it signifies)"""
    kp = res['kp']
    sub = next(c for c in kp['cusps'] if c['house'] == 7)['sub_lord']
    houses = next(x for x in kp['planet_significators'] if x['planet'] == sub)['all']
    return sub, list(houses)


def marriage_windows(res):
    """The Marriage rows of AI_TopicWindows of one horoscope, with their moments in UTC."""
    off = _offset(res)
    rows = [r for r in E.enrich(res)['tables']['AI_TopicWindows'] if r['topic'] == 'Marriage']
    return [dict(r, start_utc=r['start_local'] - off, end_utc=r['end_local'] - off) for r in rows]


def window_overlaps(boy_windows, girl_windows):
    """The spans in which a window of the boy and a window of the girl overlap, in time order."""
    out = []
    for bw in boy_windows:
        for gw in girl_windows:
            lo, hi = max(bw['start_utc'], gw['start_utc']), min(bw['end_utc'], gw['end_utc'])
            if lo < hi:
                out.append({
                    'start_utc': lo, 'end_utc': hi, 'days': round((hi - lo).total_seconds() / 86400.0, 3),
                    'boy_layers_agreeing': bw['layers_agreeing'], 'girl_layers_agreeing': gw['layers_agreeing'],
                    'boy_layers': bw['layers'], 'boy_dasa_lord': bw['dasa_lord'],
                    'boy_bhukti_lord': bw['bhukti_lord'],
                    'girl_layers': gw['layers'], 'girl_dasa_lord': gw['dasa_lord'],
                    'girl_bhukti_lord': gw['bhukti_lord'], 'label': 'rule-based overlap, not a prediction',
                })
    return sorted(out, key=lambda x: x['start_utc'])


def _day(moment):
    return moment.strftime('%Y-%m-%d')


def _group_e(pair, options):
    """Adds the rows of group E; returns the overlapping marriage windows (empty without birth details)."""
    boy, girl = pair.boy, pair.girl
    if not (boy['res'] and girl['res']):
        for key in (k for k, v in CHECKS.items() if v[0] == 'E'):
            pair.add(key, None, None, NOT_APPLICABLE, note='The birth details of both are needed')
        return []
    b, g = boy['res'], girl['res']
    start = _report_utc(b)
    end = start + timedelta(days=SANDHI_YEARS_AHEAD * A.YEAR_DAYS)

    # Dasa sandhi
    months = options['sandhi_months']
    bc, gc = dasa_changes(b, start, end), dasa_changes(g, start, end)

    def listed(changes):
        return '; '.join(f'{c["from"]} to {c["to"]} on {_day(c["local"])}' for c in changes) or 'no change'
    pairs = sandhi_pairs(bc, gc, months)
    note = f'Changes within {months} months of each other: ' + (
        '; '.join(f'the boy\'s on {_day(p["boy"]["local"])} and the girl\'s on {_day(p["girl"]["local"])} '
                  f'({p["months_apart"]} months apart)' for p in pairs) if pairs else 'none')
    pair.add('dasa_sandhi', listed(bc), listed(gc), NOT_MATCHED if pairs else MATCHED, note=note)

    # Dasas running together
    b_lord, g_lord = dasa_lord_at(b, start), dasa_lord_at(g, start)
    spans = shared_dasa_spans(b, g, start, end)
    note = ('On the report date both run the mahadasa of one planet. ' if b_lord == g_lord else
            'On the report date the mahadasa lords are different. ')
    note += 'Spans with one lord for both (UTC dates): ' + (
        '; '.join(f'{x["lord"]} {_day(x["start_utc"])} to {_day(x["end_utc"])}' for x in spans) if spans else 'none')
    pair.add('eka_dasa', b_lord, g_lord, INFORMATION, note=note)

    # KP
    def kp_text(res):
        sub, houses = kp_seventh(res)
        linked = [h for h in KP_MARRIAGE_HOUSES if h in houses]
        return (f'{sub}; signifies houses {", ".join(str(h) for h in houses) or "none"}; '
                f'2, 7 or 11 among them: {"yes (" + ", ".join(str(h) for h in linked) + ")" if linked else "no"}')
    pair.add('kp_seventh', kp_text(b), kp_text(g), INFORMATION)

    # Marriage windows
    bw, gw = marriage_windows(b), marriage_windows(g)
    overlaps = window_overlaps(bw, gw)
    first = '; '.join(f'{_day(x["start_utc"])} to {_day(x["end_utc"])}' for x in overlaps[:WINDOWS_IN_NOTE])
    note = (f'{len(overlaps)} spans in which a window of each overlaps (UTC dates). The first: {first}'
            if overlaps else 'No span in which a window of each overlaps')
    pair.add('marriage_windows', f'{len(bw)} windows in the next 10 years',
             f'{len(gw)} windows in the next 10 years', INFORMATION, note=note)
    return overlaps


# ── SUMMARY ───────────────────────────────────────────────────────────────────

def summarise(rows):
    """Counts only: no verdict."""
    def counts(items):
        return {result.replace(' ', '_'): sum(1 for r in items if r['result'] == result) for result in RESULTS}

    by_key = {r['key']: r for r in rows}
    ten = [by_key[k] for k in TAMIL_TEN if k in by_key]
    scored = [r for r in rows if r['group'] == 'C' and r['points'] is not None]
    all_c = [r for r in rows if r['group'] == 'C']
    return {
        'label': LABEL,
        'groups': {g: dict(counts([r for r in rows if r['group'] == g]), title=GROUPS[g])
                   for g in GROUPS if any(r['group'] == g for r in rows)},
        'ten_poruthams': dict(counts(ten), of=len(ten)),
        'ashtakoota': {'points': _whole(sum(r['points'] for r in scored)),
                       'max_points': sum(r['max_points'] for r in all_c),
                       'rows_scored': len(scored), 'rows': len(all_c)},
        'key_poruthams_not_matched': [by_key[k]['name'] for k in KEY_PORUTHAMS
                                      if k in by_key and by_key[k]['result'] == NOT_MATCHED],
    }


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def match(boy, girl, options=None):
    """
    Compare two people.

    boy, girl: each a result of astro_engine.compute(), or a star-only record
    {nakshatra, pada, rasi, name}. options: see clean_options(). Raises
    InputError for a record or an option that cannot be read.

    Groups A to C need only the Moon's star and rasi. Groups D and E need the
    birth details of both: with a star-only record their rows are "not
    applicable". 'windows' lists the spans in which the marriage windows of
    the two horoscopes overlap.
    """
    options = clean_options(options)
    boy, girl = as_person(boy, 'boy'), as_person(girl, 'girl')
    pair = Pair(boy, girl)
    _group_a(pair)
    _group_b(pair)
    _group_c(pair)
    _group_d(pair, options)
    windows = _group_e(pair, options)
    full = bool(boy['res'] and girl['res'])
    return {
        'schema': SCHEMA, 'label': LABEL, 'mode': 'full' if full else 'star',
        'persons': {'boy': person_facts(boy), 'girl': person_facts(girl)},
        'settings': {'kuja_houses': options['kuja_houses'],
                     'kuja_places_that_count': list(KUJA_HOUSE_SETS[options['kuja_houses']]),
                     'sandhi_months': options['sandhi_months'], 'sandhi_years_ahead': SANDHI_YEARS_AHEAD},
        'counts': {'boy_star_from_girl_star': pair.n, 'girl_star_from_boy_star': pair.m,
                   'boy_rasi_from_girl_rasi': pair.r},
        'groups': dict(GROUPS),
        'rows': pair.rows,
        'summary': summarise(pair.rows),
        'windows': windows,
        'rules': [{'name': name, 'rule': rule} for name, rule in MATCH_RULES],
        'table_sources': [{'status': status, 'tables': tables} for status, tables in TABLE_SOURCES],
        'not_included': list(NOT_INCLUDED),
    }
