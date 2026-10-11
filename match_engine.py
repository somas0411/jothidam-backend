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

TABLE_SOURCES = [
    ('Checked against one or more published pages, which agree',
     'Dinam counts; Mahendram counts; Stree Deergham limits; the stars of each gana, yoni, rajju and nadi; '
     'the vedhai pairs; the same-star lists; the 27th-star rule; the 4th pada of the 22nd star; varna of the '
     'rasis; tara; Graha Maitri points; Bhakoot; the Nadi, Bhakoot and Gana exceptions.'),
    ('Published sources disagree; the variant used is named in the rule',
     'Gana points (two pages print the table with bride and groom exchanged); Vashya points (three cells '
     'differ between pages); Yoni points (two different 14 x 14 tables are in circulation); Vriksha (two '
     'pages print the milk and non-milk groups the opposite way round); the Tamil Rasi porutham rule for '
     'the counts 3, 4, 5, 9, 10 and 11.'),
    ('Written from memory of B.V. Raman, Muhurtha; not checked against the printed book',
     'The Tamil Vasiyam list.'),
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

def match(boy, girl):
    """
    Compare two people.

    boy, girl: each a result of astro_engine.compute(), or a star-only record
    {nakshatra, pada, rasi, name}. Raises InputError for a record that cannot
    be read.
    """
    boy, girl = as_person(boy, 'boy'), as_person(girl, 'girl')
    pair = Pair(boy, girl)
    _group_a(pair)
    _group_b(pair)
    _group_c(pair)
    full = bool(boy['res'] and girl['res'])
    return {
        'schema': SCHEMA, 'label': LABEL, 'mode': 'full' if full else 'star',
        'persons': {'boy': person_facts(boy), 'girl': person_facts(girl)},
        'counts': {'boy_star_from_girl_star': pair.n, 'girl_star_from_boy_star': pair.m,
                   'boy_rasi_from_girl_rasi': pair.r},
        'groups': dict(GROUPS),
        'rows': pair.rows,
        'summary': summarise(pair.rows),
        'rules': [{'name': name, 'rule': rule} for name, rule in MATCH_RULES],
        'table_sources': [{'status': status, 'tables': tables} for status, tables in TABLE_SOURCES],
        'not_included': list(NOT_INCLUDED),
    }
