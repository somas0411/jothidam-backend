"""
predictions.py — rule-based readings in plain words, without any AI model.

    block = build(res, ai, lang)      # res: compute(); ai: enrich(res)

Every line comes from a fixed template in data/predictions/*.json, picked by
chart facts that enrich() has already worked out (the AI_ tables, including
AI_RuleBook). Nothing is recomputed and nothing is random: the same birth
details and report moment always give the same rows.

Sections, in output order
  summary      P9  6 to 8 lines picked by fixed rules
  personality  P1  lagna, Moon sign, birth star, pada, gana, yoni, nadi,
                   lagna lord, panchangam of the birth moment
  strengths    P2  exalted / own / moolatrikona / debilitated / vargottama
                   planets; the strongest and weakest houses by SAV bindus
  yogas        P3  every yoga found, what it gives and when it is active;
                   Kuja dosha, Kala Sarpa, Kemadruma, Guru-Chandala
  life         P4  13 life areas: promise level, key factors, rule-book rows,
                   timing windows; career fields, job or business, marriage
                   and children periods, partner indications
  period       P5  running dasa, bhukti and antaram, and the next bhuktis
  transit      P6  Saturn, Jupiter, Rahu and Ketu from the Moon, now and for
                   24 months; Sade Sati; Jupiter-Saturn double transit
  calendar     P7  the next 12 months rated by a counted rule (CALENDAR_RULE)
  remedies     P8  generic, optional (SHOW_REMEDIES)

Rules of this module
  * Nothing about death, length of life or the manner of passing, no health
    reading, no gemstones or paid rituals, no fear wording. Every row is
    checked against rulebook.BANNED and HEALTH before it is returned.
  * Below age 18 no career, business, marriage or children rows.
  * 'basis' always names the chart facts used, in English (as in the AI
    sheets), so that every line can be checked.
  * Text is English or Tamil; every other language falls back to English
    text with names (planets, signs, stars) in that language.

TODO (later PR): readings for the family report (family_engine) and the
marriage match (match_engine) are not part of this module yet.
"""

import json
import os
import re
from datetime import datetime, timedelta

import i18n
import match_engine as M
import rulebook_i18n
from astro_engine import NAKS, RASIS, SIGN_LORDS, YOGAS as NITYA_YOGAS
from enrich import TOPICS, SAV_STRONG, SAV_WEAK
from rulebook import BANNED

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'predictions')

SECTIONS = ('summary', 'personality', 'strengths', 'yogas', 'life', 'period', 'transit', 'calendar',
            'remedies')
SEVEN = ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')
NODES = ('Rahu', 'Ketu')
KENDRA_TRIKONA = (1, 4, 5, 7, 9, 10)
DUSTHANA = (6, 8, 12)

# ── thresholds ───────────────────────────────────────────────────────────────
ADULT_AGE = 18                    # below this: no career, business, marriage or children rows
MINOR_TOPICS = ('Job and career', 'Business', 'Marriage', 'Children')
MINOR_RULE_TOPICS = ('career', 'marriage', 'children')
RULE_STATUS_SKIPPED = ('past', 'dormant')   # rule-book rows whose periods are over or too late
STUDY_AGE_MAX = 25                # education rule-book rows are shown up to this age
SUMMARY_TOPICS = ('Job and career', 'Business', 'Marriage', 'Children', 'Abroad / onsite', 'Education',
                  'Home and vehicle', 'Money', 'Spiritual life')   # ranked in the summary
PROMISE_STRONG = 0.65             # supports / (supports + weakens) from here: strong
PROMISE_MODERATE = 0.45           # from here: moderate; below: needs effort
JOB_BUSINESS_MARGIN = 0.10        # ratio difference that makes job or business the lean
SAV_AVERAGE = 28                  # 337 bindus / 12 houses; above: "strongest" wording
SAV_SHOWN = 3                     # strongest and weakest houses listed
MARRIAGE_AGES = (21, 35)
CHILDREN_AGES = (23, 40)
PERIOD_ROWS_MAX = 6               # marriage / children periods listed
WINDOWS_PER_TOPIC = 3
LIFE_LIMIT_AGE = 75               # a period starting later is 'outside the useful years'
TRANSIT_MONTHS = 24
TRANSIT_ROWS_PER_PLANET = 3
SUPPORT_BINDUS = 4                # own bindus of a transit sign that soften a hard transit
DOUBLE_TRANSIT_HOUSES = (2, 4, 5, 7, 9, 10, 11)
DOUBLE_TRANSIT_ROWS = 5
CALENDAR_MONTHS = 12
SHOW_REMEDIES = True

FAVOURABLE_DIGNITY = ('Exalted', 'Moolatrikona', 'Own sign')
WEAK_DIGNITY = ('Enemy', 'Great enemy', 'Debilitated')
GOOD_NATURE = ('Benefic', 'Yogakaraka')

# Fixed tone of each transit, by planet and house from the Moon
_FAV = 'favourable'
_MIX = 'mixed'
_CH = 'challenging'
TRANSIT_TONE = {
    'Jupiter': {1: _MIX, 2: _FAV, 3: _MIX, 4: _CH, 5: _FAV, 6: _CH, 7: _FAV, 8: _CH, 9: _FAV, 10: _MIX, 11: _FAV,
                12: _CH},
    'Saturn': {1: _CH, 2: _CH, 3: _FAV, 4: _CH, 5: _CH, 6: _FAV, 7: _CH, 8: _CH, 9: _MIX, 10: _MIX, 11: _FAV,
               12: _CH},
    'Rahu': {1: _CH, 2: _CH, 3: _FAV, 4: _CH, 5: _CH, 6: _FAV, 7: _CH, 8: _CH, 9: _MIX, 10: _MIX, 11: _FAV,
             12: _MIX},
    'Ketu': {1: _CH, 2: _CH, 3: _FAV, 4: _CH, 5: _CH, 6: _FAV, 7: _CH, 8: _MIX, 9: _MIX, 10: _MIX, 11: _FAV,
             12: _MIX},
}

# P7: the counted rule of the month calendar (also printed with the report)
CAL_JUPITER = {2: 1, 5: 1, 7: 1, 9: 1, 11: 1, 4: -1, 6: -1, 8: -1, 10: -1, 12: -1}
CAL_SATURN = {3: 1, 6: 1, 11: 1, 1: -1, 2: -1, 4: -1, 8: -1, 12: -1}
CAL_TARA = {'favourable': 1, 'unfavourable': -1}
CAL_FAVOURABLE_FROM = 1
CAL_CAREFUL_UPTO = -2

# Yogas: key (template id) by the name enrich gives them; first match wins
YOGA_KEYS = (
    ('Viparita', 'Viparita'), ('Ruchaka', 'Ruchaka'), ('Bhadra', 'Bhadra'), ('Hamsa', 'Hamsa'),
    ('Malavya', 'Malavya'), ('Sasa', 'Sasa'), ('Gajakesari', 'Gajakesari'), ('Budha-Aditya', 'Budha-Aditya'),
    ('Chandra-Mangala', 'Chandra-Mangala'), ('Dharma-Karmadhipati', 'Dharma-Karmadhipati'),
    ('Raja yoga', 'Raja'), ('Dhana yoga', 'Dhana'), ('Parivartana', 'Parivartana'), ('Sunapha', 'Sunapha'),
    ('Anapha', 'Anapha'), ('Durudhara', 'Durudhara'), ('Ubhayachari', 'Ubhayachari'), ('Vasi', 'Vasi'),
    ('Vesi', 'Vesi'), ('Amala', 'Amala'), ('Adhi', 'Adhi'), ('Neecha bhanga', 'Neecha bhanga'),
    ('Kuja dosha', 'Kuja'), ('Kala Sarpa', 'Kala Sarpa'), ('Kemadruma', 'Kemadruma'),
    ('Guru-Chandala', 'Guru-Chandala'),
)
DOSHAS = ('Kuja', 'Kala Sarpa', 'Kemadruma', 'Guru-Chandala')
KEY_YOGA_ORDER = ('Ruchaka', 'Bhadra', 'Hamsa', 'Malavya', 'Sasa', 'Gajakesari', 'Dharma-Karmadhipati', 'Raja',
                  'Dhana', 'Viparita', 'Budha-Aditya', 'Chandra-Mangala', 'Parivartana', 'Adhi', 'Amala',
                  'Neecha bhanga', 'Sunapha', 'Anapha', 'Durudhara', 'Ubhayachari', 'Vasi', 'Vesi')

# P4: which rule-book topics go under each life area; two extra blocks close it
RULE_TOPICS = {
    'Job and career': ('career',), 'Money': ('wealth',), 'Home and vehicle': ('property',),
    'Marriage': ('marriage',), 'Children': ('children',), 'Education': ('education',),
    'Abroad / onsite': ('foreign',), 'Spiritual life': ('spiritual',),
    'Family life': ('family',), 'General': ('general',),
}

# Words a health reading would need; none may appear in the output
HEALTH = re.compile(r'disease|illness|\bill\b|sick|cancer|surgery|surgical|accident|injur|hospital\b|diabet|'
                    r'tumou?r|disorder|infection|fever|chronic|diagnos|மரண|இறப்பு|ஆயுள்|நோய்|விபத்து|'
                    r'அறுவை|மருத்துவமனை', re.I)
# The same policy in the other report scripts: death, length of life, maraka and
# health words. Hindi/Marathi आयु means age and is allowed; words that also mean
# health (आरोग्य) or contain the letters (प्रोग्रामिंग, పురోగతి) are excluded by the look-behinds.
NATIVE_BANNED = re.compile(
    r'मृत्यु|मौत|मरण|दीर्घायु|अल्पायु|आयुष्य|मारक|(?<![\u0900-\u097F])रोग|बीमारी|आजार|दुर्घटना|अपघात|कैंसर|कर्करोग|मधुमेह|शस्त्रक्रिया|सर्जरी|'
    r'మరణ|మృత్యు|ఆయుష్|మారక|వ్యాధి|(?<![\u0C00-\u0C7F])రోగ|శస్త్రచికిత్స|మధుమేహ|'
    r'ಮರಣ|ಸಾವು|ಆಯುಷ್ಯ|ಮಾರಕ|(?<![\u0C80-\u0CFF])ರೋಗ|ಕಾಯಿಲೆ|ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ|ಅಪಘಾತ|ಮಧುಮೇಹ|'
    r'മരണ|ആയുസ്സ|മാരക|(?<![\u0D00-\u0D7F])രോഗ|ശസ്ത്രക്രിയ|പ്രമേഹ|'
    r'মৃত্যু|মরণ|আয়ু|মারক|(?<![\u0980-\u09FF])রোগ|অসুখ|অস্ত্রোপচার|দুর্ঘটনা|ক্যানসার|ডায়াবেটিস')

TEXT_LANGS = ('en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn')   # languages every template is written in

# Gregorian month names for the month calendar, in each report language
MONTHS = {
    'en': ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
    'ta': ('ஜனவரி', 'பிப்ரவரி', 'மார்ச்', 'ஏப்ரல்', 'மே', 'ஜூன்', 'ஜூலை', 'ஆகஸ்ட்', 'செப்டம்பர்',
           'அக்டோபர்', 'நவம்பர்', 'டிசம்பர்'),
    'hi': ('जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर',
           'नवंबर', 'दिसंबर'),
    'te': ('జనవరి', 'ఫిబ్రవరి', 'మార్చి', 'ఏప్రిల్', 'మే', 'జూన్', 'జూలై', 'ఆగస్టు', 'సెప్టెంబర్',
           'అక్టోబర్', 'నవంబర్', 'డిసెంబర్'),
    'kn': ('ಜನವರಿ', 'ಫೆಬ್ರವರಿ', 'ಮಾರ್ಚ್', 'ಏಪ್ರಿಲ್', 'ಮೇ', 'ಜೂನ್', 'ಜುಲೈ', 'ಆಗಸ್ಟ್', 'ಸೆಪ್ಟೆಂಬರ್',
           'ಅಕ್ಟೋಬರ್', 'ನವೆಂಬರ್', 'ಡಿಸೆಂಬರ್'),
    'ml': ('ജനുവരി', 'ഫെബ്രുവരി', 'മാർച്ച്', 'ഏപ്രിൽ', 'മേയ്', 'ജൂൺ', 'ജൂലൈ', 'ഓഗസ്റ്റ്', 'സെപ്റ്റംബർ',
           'ഒക്ടോബർ', 'നവംബർ', 'ഡിസംബർ'),
    'mr': ('जानेवारी', 'फेब्रुवारी', 'मार्च', 'एप्रिल', 'मे', 'जून', 'जुलै', 'ऑगस्ट', 'सप्टेंबर',
           'ऑक्टोबर', 'नोव्हेंबर', 'डिसेंबर'),
    'bn': ('জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর',
           'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'),
}

COLUMNS = [
    ('section', 'Section key: ' + ', '.join(SECTIONS)),
    ('topic', 'Life area or subject of the row, in the report language'),
    ('item', 'What the row is about (template group)'),
    ('tone', 'favourable, mixed, challenging (shown as "needs care") or neutral'),
    ('text', 'The reading, from a fixed template'),
    ('basis', 'The chart facts that chose the template (English)'),
    ('period', 'Dates the row is about, if any'),
    ('status', 'running now / upcoming / past / dormant / always'),
    ('sort_key', 'Fixed order of the rows'),
]


# ── templates ────────────────────────────────────────────────────────────────

_TEXTS = None


def texts():
    """All templates of data/predictions, merged; ids are unique across files."""
    global _TEXTS
    if _TEXTS is None:
        merged = {}
        for name in sorted(os.listdir(DATA_DIR)):
            if name.endswith('.json'):
                with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
                    for key, value in json.load(f).items():
                        if key in merged:
                            raise ValueError(f'template {key} is defined twice')
                        merged[key] = value
        _TEXTS = merged
    return _TEXTS


class _Keep(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def text_lang(lang):
    """Language of the template text: the report language; English for 'bi' and unknown codes."""
    return lang if lang in TEXT_LANGS else 'en'


def T(key, lang, **kw):
    entry = texts()[key]
    value = entry.get(text_lang(lang)) or entry['en']
    return value.format_map(_Keep(kw)) if kw and isinstance(value, str) else value


def has(key):
    return key in texts()


# ── the reader ───────────────────────────────────────────────────────────────

class Reader:
    def __init__(self, res, ai, lang):
        self.res, self.lang = res, lang
        t = ai['tables']
        self.t = t
        self.facts = {r['key']: r['value'] for r in t['AI_Facts']}
        self.now = self.facts['report_datetime_local']
        self.birth = self.facts['birth_datetime_local']
        self.age = self.facts['age_at_report_years']
        self.minor = self.age < ADULT_AGE
        self.p = {r['point']: r for r in t['AI_Planets']}
        self.h = {r['house']: r for r in t['AI_Houses']}
        self.vl = {r['chart']: r for r in t['AI_VargaLagnas']}
        self.rows = []
        self._count = {}
        self.used = set()

    # names and dates in the report language
    def L(self, key, **kw):
        self.used.add(key)
        return T(key, self.lang, **kw)

    def pn(self, planet):
        return i18n.planet(planet, self.lang)

    def pns(self, planets):
        return ', '.join(self.pn(p) for p in planets)

    def sign(self, sign_no):
        return i18n.rasi(sign_no - 1, self.lang)

    def topic(self, name):
        return self.L('topic.' + name)

    def date(self, dt):
        return dt.strftime('%Y-%m-%d')

    def month(self, dt):
        return f'{MONTHS[text_lang(self.lang)][dt.month - 1]} {dt.year}'

    def years(self, dt):
        return (dt - self.birth).days / 365.25

    def span(self, a, b, ages=True):
        if ages:
            return self.L('range_age', a=self.date(a), b=self.date(b), x=f'{self.years(a):.1f}',
                          y=f'{self.years(b):.1f}')
        return self.L('range', a=self.date(a), b=self.date(b))

    def status(self, a, b):
        if a <= self.now < b:
            return 'running now'
        if a > self.now:
            return 'dormant' if self.years(a) > LIFE_LIMIT_AGE else 'upcoming'
        return 'past'

    def meaning(self, house):
        return self.L(f'hm.{house}')

    def owned(self, planet):
        text = self.p[planet].get('houses_owned') or ''
        return [int(x) for x in text.split(',') if x.strip().isdigit()]

    def areas(self, planet):
        """Meanings of the houses a planet rules; for a node, of the house it sits in."""
        houses = self.owned(planet) or [self.p[planet]['house_whole_sign']]
        return '; '.join(self.meaning(h) for h in houses)

    def dignity(self, planet):
        r = self.p[planet]
        if r.get('debilitated') == 'yes':
            return 'Debilitated'
        if r.get('moolatrikona') == 'yes':
            return 'Moolatrikona'
        return r.get('dignity')

    # rows
    def add(self, section, topic, item, tone, text, basis, period='', status='always'):
        n = self._count.get(section, 0)
        self._count[section] = n + 1
        self.rows.append({'section': section, 'topic': topic, 'item': item, 'tone': tone, 'text': text,
                          'basis': basis, 'period': period, 'status': status,
                          'sort_key': f'{SECTIONS.index(section):02d}-{n:04d}'})

    # periods
    def dasa_rows(self):
        return self.t['AI_Dasa']

    def running(self, table):
        for r in self.t[table]:
            if r['start_local'] <= self.now < r['end_local']:
                return r
        return None

    def period_for(self, lords):
        """The running, else the next, dasa or bhukti of one of the lords: (text, status)."""
        lords = set(lords)
        for r in self.t['AI_DasaPeriods']:
            if r['dasa_lord'] in lords and r['start_local'] <= self.now < r['end_local']:
                return (f"{self.pn(r['dasa_lord'])} {self.L('level.dasa')}, "
                        f"{self.span(r['start_local'], r['end_local'])}", 'running now')
        rows = self.dasa_rows()
        for r in rows:
            if r['bhukti_lord'] in lords and r['start_local'] <= self.now < r['end_local']:
                return self._bhukti_text(r), 'running now'
        for r in rows:
            if r['bhukti_lord'] in lords and r['start_local'] > self.now:
                st = self.status(r['start_local'], r['end_local'])
                return self._bhukti_text(r), st
        return '', 'past'

    def _bhukti_text(self, r):
        return (f"{self.pn(r['dasa_lord'])} {self.L('level.dasa')} / {self.pn(r['bhukti_lord'])} "
                f"{self.L('level.bhukti')}, {self.span(r['start_local'], r['end_local'])}")

    def promise(self):
        out = {}
        for r in self.t['AI_TopicPromise']:
            if r['row_type'] == 'total':
                out[r['topic']] = (r['supports_count'] or 0, r['weakens_count'] or 0)
        return out


def _ratio(s, w):
    return s / (s + w) if s + w else 0.5


def _level(s, w):
    r = _ratio(s, w)
    return 'strong' if r >= PROMISE_STRONG else 'moderate' if r >= PROMISE_MODERATE else 'effort'


LEVEL_TONE = {'strong': 'favourable', 'moderate': 'mixed', 'effort': 'challenging'}


def _sign_no(name):
    return RASIS.index(name) + 1


# ── P1 personality ───────────────────────────────────────────────────────────

def _personality(c):
    S = 'personality'
    f = c.facts
    topic = c.topic('Personality')
    lag, moon, nak, pada = f['lagna_sign_no'], f['moon_sign_no'], f['moon_nakshatra_no'], f['moon_pada']
    c.add(S, topic, 'lagna', 'neutral', c.L('lagna_prefix', sign=c.sign(lag)) + c.L(f'lagna.{lag}'),
          f"lagna {RASIS[lag - 1]}")
    c.add(S, topic, 'moon sign', 'neutral', c.L('moon_prefix', sign=c.sign(moon)) + c.L(f'moon.{moon}'),
          f"Moon in {RASIS[moon - 1]}")
    c.add(S, topic, 'birth star', 'neutral',
          c.L('nak_prefix', nak=i18n.nak(nak - 1, c.lang), pada=pada) + c.L(f'nak.{nak}'),
          f"Moon in {NAKS[nak - 1]} pada {pada}")
    d9 = c.p['Moon'].get('d9_sign')
    if d9:
        lord = SIGN_LORDS[_sign_no(d9) - 1]
        c.add(S, topic, 'pada', 'neutral',
              c.L('pada', sign=c.sign(_sign_no(d9)), planet=c.pn(lord), sig=c.L(f'sig.{lord}')),
              f"Moon in navamsa {d9}, ruled by {lord}")
    gana, yoni, nadi = M.GANA[nak - 1], M.YONI[nak - 1], M.NADI[nak - 1]
    c.add(S, topic, 'gana', 'neutral', c.L(f'gana.{gana}'), f"{NAKS[nak - 1]}: {gana} gana")
    c.add(S, topic, 'yoni', 'neutral', c.L('yoni', animal=c.L(f'yoni.{yoni}'), quality=c.L(f'yq.{yoni}')),
          f"{NAKS[nak - 1]}: {yoni} yoni")
    c.add(S, topic, 'nadi', 'neutral', c.L('nadi', nadi=c.L(f'nadi.{nadi}')), f"{NAKS[nak - 1]}: {nadi} nadi")
    ll = f['lagna_lord']
    llh = c.p[ll]['house_whole_sign']
    c.add(S, topic, 'lagna lord', 'neutral', c.L('ll_prefix', planet=c.pn(ll), house=llh) + c.L(f'll.{llh}'),
          f"lagna lord {ll} in house {llh}")
    paksha = f.get('paksha')
    if paksha in ('Shukla', 'Krishna'):
        c.add(S, topic, 'paksha', 'neutral', c.L(f'paksha.{paksha}'), f"{paksha} paksha")
    tno = f.get('tithi_no')
    if tno:
        group = ('nanda', 'bhadra', 'jaya', 'rikta', 'purna')[(tno - 1) % 5]
        c.add(S, topic, 'tithi', 'neutral',
              c.L('tithi_prefix', tithi=i18n.tithi(f['tithi'], c.lang)) + c.L(f'tg.{group}'),
              f"tithi {tno} ({f['tithi']}), {group} group")
    wl = f.get('weekday_lord')
    if wl:
        c.add(S, topic, 'weekday', 'neutral',
              c.L('weekday', weekday=i18n.weekday(f['weekday'], c.lang), planet=c.pn(wl), sig=c.L(f'sig.{wl}')),
              f"born on {f['weekday']}, lord {wl}")
    ny = f.get('nitya_yoga')
    if ny and has(f'nyq.{ny}'):
        quality = c.L(f'nyq.{ny}')
        line = (c.L('nyoga_no', no=NITYA_YOGAS.index(ny) + 1, quality=quality) if BANNED.search(ny)
                else c.L('nyoga', yoga=c.L(f'nyn.{ny}'), quality=quality))
        c.add(S, topic, 'birth yoga', 'neutral', line, f"nitya yoga number {NITYA_YOGAS.index(ny) + 1}")
    kr = f.get('karana')
    if kr and has(f'kq.{kr}'):
        c.add(S, topic, 'karana', 'neutral', c.L('karana', karana=c.L(f'krn.{kr}'), quality=c.L(f'kq.{kr}')), f"karana {kr}")
    _rule_rows(c, S, topic, ('personality',))


# ── P2 strengths ─────────────────────────────────────────────────────────────

def _strengths(c):
    S = 'strengths'
    for planet in SEVEN + NODES:
        r = c.p[planet]
        base = dict(planet=c.pn(planet), sig=c.L(f'sig.{planet}'), areas=c.areas(planet))
        topic = c.pn(planet)
        if r.get('debilitated') == 'yes':
            by = r.get('debilitation_cancelled_by')
            if by:
                c.add(S, topic, 'debilitated, cancelled', 'mixed', c.L('debil_cancel', **base),
                      f"{planet} debilitated in {r['sign']}; neecha bhanga conditions {by} (see AI_Yogas)")
            else:
                c.add(S, topic, 'debilitated', 'challenging', c.L('debil', **base),
                      f"{planet} debilitated in {r['sign']}")
        elif r.get('dignity') == 'Exalted':
            c.add(S, topic, 'exalted', 'favourable', c.L('exalted', **base), f"{planet} exalted in {r['sign']}")
        elif r.get('moolatrikona') == 'yes':
            c.add(S, topic, 'moolatrikona', 'favourable', c.L('moola', **base),
                  f"{planet} in moolatrikona in {r['sign']}")
        elif r.get('dignity') == 'Own sign':
            c.add(S, topic, 'own sign', 'favourable', c.L('own', **base), f"{planet} in own sign {r['sign']}")
        if r.get('vargottama') == 'yes':
            c.add(S, topic, 'vargottama', 'favourable', c.L('vargottama', **base),
                  f"{planet} in {r['sign']} in D1 and D9")
    houses = sorted(c.h.values(), key=lambda r: (-r['sav_bindus'], r['house']))
    for r in houses[:SAV_SHOWN]:
        if r['sav_bindus'] > SAV_AVERAGE:
            c.add(S, c.L('general'), 'strong house', 'favourable',
                  c.L('sav_strong', house=r['house'], bindus=r['sav_bindus'], meaning=c.meaning(r['house'])),
                  f"house {r['house']} ({r['sign']}): {r['sav_bindus']} SAV bindus "
                  f"(strong from {SAV_STRONG})")
    for r in reversed(houses[-SAV_SHOWN:]):
        if r['sav_bindus'] < SAV_AVERAGE:
            c.add(S, c.L('general'), 'weak house', 'challenging',
                  c.L('sav_weak', house=r['house'], bindus=r['sav_bindus'], meaning=c.meaning(r['house'])),
                  f"house {r['house']} ({r['sign']}): {r['sav_bindus']} SAV bindus "
                  f"(weak up to {SAV_WEAK})")


# ── P3 yogas and doshas ──────────────────────────────────────────────────────

def yoga_key(name):
    for needle, key in YOGA_KEYS:
        if needle in name:
            return key
    return None


def found_yogas(c):
    """{key: {'planets': [...], 'notes': [...], 'variant_only': bool, 'refs': [...], 'weak': [...]}} in table order."""
    out = {}
    for r in c.t['AI_Yogas']:
        if r['status'] != 'found':
            continue
        key = yoga_key(r['yoga'])
        if not key:
            continue
        g = out.setdefault(key, {'planets': [], 'notes': [], 'variant_only': True, 'refs': [], 'weak': []})
        variant = 'counted from the Moon' in r['yoga']
        g['variant_only'] = g['variant_only'] and variant
        for p in (r['planets'] or '').split(','):
            p = p.strip()
            if p in SEVEN + NODES and p not in g['planets']:
                g['planets'].append(p)
        if r['note'] and len(g['notes']) < 3:
            g['notes'].append(r['note'])
        if key == 'Kuja':
            g['refs'].append(r['yoga'].replace('Kuja dosha ', ''))
        if r.get('weakening_factors') and r['weakening_factors'] not in g['weak']:
            g['weak'].append(r['weakening_factors'])
    return out


def _yogas(c):
    S = 'yogas'
    yogas = found_yogas(c)
    for key, g in yogas.items():
        if key in DOSHAS:
            continue
        text = c.L(f'y.{key}')
        if g['variant_only']:
            text = text.replace(':', c.L('moon_variant') + ':', 1)
        period, status = c.period_for(g['planets']) if g['planets'] else ('', 'always')
        if period:
            text += c.L('activates', period=period)
        c.add(S, c.L(f'yname.{key}') if has(f'yname.{key}') else key, key, 'favourable', text,
              '; '.join(g['notes']) or key, period, status)
    for key in DOSHAS:
        g = yogas.get(key)
        if not g:
            continue
        if key == 'Kuja':
            refs = ', '.join(c.L(f'kuja.{x}') for x in g['refs'] if has(f'kuja.{x}'))
            text = c.L('d.Kuja', refs=refs)
        else:
            text = c.L(f'd.{key}')
        basis = '; '.join(g['notes']) or key
        if g['weak']:
            text += c.L('cancel')
            basis += '; softening factors: ' + '; '.join(g['weak'])
        text += c.L('consider')
        c.add(S, c.L(f'dname.{key}'), 'dosha', 'mixed', text, basis)


# ── P4 life areas ────────────────────────────────────────────────────────────

_WIN_DASA = re.compile(r'^(\w+) dasa, (\S+) to (\S+) \(age ([\d.]+) to ([\d.]+)\)$')
_WIN_BHUKTI = re.compile(r'^(\w+) bhukti in (\w+) dasa, (\S+) to (\S+) \(age ([\d.]+) to ([\d.]+)\)$')


# Data-file lines of the rule book that a report never shows, in any language:
# banned and health words, and supply to hospitals (a health setting in the
# other scripts).
RULE_LINE_DROP = (BANNED, HEALTH, re.compile(r'hospitals', re.I))


def rule_finding(r, lang):
    """The rule-book finding in the report language; English when no translation exists.
    Lines that a report must not show (health, banned words) are dropped in every language."""
    plan = lambda p: i18n.planet(p, lang)
    text = rulebook_i18n.translate(r['finding'], r['rule_id'], lang, plan, drop=RULE_LINE_DROP)
    if text is None:
        text = rulebook_i18n.translate(r['finding'], r['rule_id'], 'en', plan, drop=RULE_LINE_DROP)
    return text or ''


def rule_window(c, window):
    """A rule window ('X dasa, A to B (age x to y)' or 'B bhukti in D dasa, ...') in the report language."""
    if not window or c.lang == 'en':
        return window or ''
    m = _WIN_DASA.match(window)
    if m:
        d, a, b, x, y = m.groups()
        return f"{c.pn(d)} {c.L('level.dasa')}, {c.L('range_age', a=a, b=b, x=x, y=y)}"
    m = _WIN_BHUKTI.match(window)
    if m:
        bh, d, a, b, x, y = m.groups()
        return (f"{c.pn(d)} {c.L('level.dasa')} / {c.pn(bh)} {c.L('level.bhukti')}, "
                f"{c.L('range_age', a=a, b=b, x=x, y=y)}")
    return window


def _rule_rows(c, section, topic_label, rule_topics):
    for r in c.t['AI_RuleBook']:
        if r['topic'] not in rule_topics:
            continue
        if c.minor and r['topic'] in MINOR_RULE_TOPICS:
            continue
        if r.get('status_at_report_date') in RULE_STATUS_SKIPPED:
            continue
        if r['topic'] == 'education' and c.age > STUDY_AGE_MAX:
            continue
        text = rule_finding(r, c.lang)
        if not text:
            continue
        c.add(section, topic_label, 'rule: ' + r['rule_id'], r['tone'] or 'mixed',
              text, r['basis'] or r['rule'], rule_window(c, r.get('window')),
              r.get('status_at_report_date') or 'always')


def _topic_block(c, name, houses, sig, vargas, promise):
    S = 'life'
    label = c.topic(name)
    s, w = promise.get(name, (0, 0))
    level = _level(s, w)
    c.add(S, label, 'promise', LEVEL_TONE[level],
          c.L(f'level.{level}', topic=label, s=s, w=w, focus=c.L(f'focus.{name}')),
          f"AI_TopicPromise: {s} supports, {w} weakens (ratio {_ratio(s, w):.2f})")
    h = houses[0]
    lord = c.h[h]['lord']
    lh = c.h[h]['lord_house']
    kind = 'good' if lh in KENDRA_TRIKONA else 'dusthana' if lh in DUSTHANA else 'other'
    c.add(S, label, 'house lord', {'good': 'favourable', 'dusthana': 'challenging', 'other': 'mixed'}[kind],
          c.L(f'lord.{kind}', house=h, planet=c.pn(lord), lh=lh, topic=label, meaning=c.meaning(lh)),
          f"lord of house {h} {lord} in house {lh}")
    karaka = sig[0]
    dig = c.dignity(karaka)
    if dig:
        kk = ('strong' if dig in FAVOURABLE_DIGNITY else 'weak' if dig in WEAK_DIGNITY else 'neutral')
        c.add(S, label, 'significator', {'strong': 'favourable', 'weak': 'challenging', 'neutral': 'mixed'}[kk],
              c.L(f'karaka.{kk}', planet=c.pn(karaka), dignity=c.L(f'dig.{dig}'), topic=label),
              f"significator {karaka}: {dig} in {c.p[karaka]['sign']}")
    v = c.vl.get(vargas[0])
    if v:
        vh = v['lagna_lord_house']
        vk = 'good' if vh in KENDRA_TRIKONA else 'weak' if vh in DUSTHANA else 'other'
        c.add(S, label, 'divisional chart', {'good': 'favourable', 'weak': 'challenging', 'other': 'mixed'}[vk],
              c.L(f'varga.{vk}', chart=vargas[0], planet=c.pn(v['lagna_lord']), house=vh, topic=label),
              f"{vargas[0]} lagna {v['lagna_sign']}, lord {v['lagna_lord']} in house {vh}")
    extra = {'Job and career': _career, 'Marriage': _marriage, 'Children': _children}.get(name)
    if extra:
        extra(c, label, promise)
    _rule_rows(c, S, label, RULE_TOPICS.get(name, ()))
    _windows(c, name, label)


def _windows(c, name, label):
    rows = [r for r in c.t['AI_TopicWindows'] if r['topic'] == name and r['end_local'] > c.now]
    rows.sort(key=lambda r: (-r['layers_agreeing'], r['start_local']))
    for r in sorted(rows[:WINDOWS_PER_TOPIC], key=lambda r: r['start_local']):
        a = max(r['start_local'], c.now)
        period = c.span(a, r['end_local'])
        c.add('life', label, 'window', 'favourable',
              c.L('window', period=period, dasa=c.pn(r['dasa_lord']), bhukti=c.pn(r['bhukti_lord']),
                  layers=r['layers_agreeing']),
              f"AI_TopicWindows: layers {r['layers']}", period, c.status(a, r['end_local']))


def _amatyakaraka(c):
    order = sorted(SEVEN, key=lambda p: -c.p[p]['deg_in_sign'])
    return order[1]


def _career(c, label, promise):
    planets = [c.h[10]['lord']]
    occ = [x.strip() for x in (c.h[10]['occupants_whole_sign'] or '').split(',')]
    planets += [x for x in occ if x in SEVEN + NODES]
    if c.vl.get('D10'):
        planets.append(c.vl['D10']['lagna_lord'])
    amk = _amatyakaraka(c)
    planets.append(amk)
    unique = list(dict.fromkeys(planets))
    fields = '; '.join(c.L(f'field.{p}') for p in unique)
    c.add('life', label, 'career fields', 'neutral', c.L('fields', planets=c.pns(unique), fields=fields),
          f"10th lord {c.h[10]['lord']}; in the 10th: {', '.join(x for x in occ if x in SEVEN + NODES) or 'none'}; "
          f"D10 lagna lord {c.vl['D10']['lagna_lord'] if c.vl.get('D10') else '-'}; amatyakaraka {amk}")
    js, jw = promise.get('Job and career', (0, 0))
    bs, bw = promise.get('Business', (0, 0))
    jr, br = _ratio(js, jw), _ratio(bs, bw)
    lean = 'job' if jr - br > JOB_BUSINESS_MARGIN else 'business' if br - jr > JOB_BUSINESS_MARGIN else 'both'
    c.add('life', label, 'job or business', 'neutral',
          c.L(f'job.{lean}', j=f'{js}:{jw}', b=f'{bs}:{bw}'),
          f"supports:weakens - job {js}:{jw} ({jr:.2f}), business {bs}:{bw} ({br:.2f})")


def _lord_periods(c, label, lords, ages, key, basis):
    rows = [r for r in c.dasa_rows() if r['bhukti_lord'] in lords
            and c.years(r['start_local']) < ages[1] and c.years(r['end_local']) > ages[0]]
    for r in rows[:PERIOD_ROWS_MAX]:
        period = c.span(r['start_local'], r['end_local'])
        text = c.L(key, period=f"{c.pn(r['dasa_lord'])} {c.L('level.dasa')} / {c.pn(r['bhukti_lord'])} "
                              f"{c.L('level.bhukti')}, {period}",
                   lords=c.pns([r['bhukti_lord']]))
        c.add('life', label, 'timing', 'favourable', text, basis, period,
              c.status(r['start_local'], r['end_local']))
    return rows


def _marriage(c, label, promise):
    lord7 = c.h[7]['lord']
    lords = list(dict.fromkeys([lord7, 'Venus', 'Rahu']))
    if not _lord_periods(c, label, lords, MARRIAGE_AGES, 'mw',
                         f"bhuktis of the 7th lord {lord7}, Venus or Rahu between ages {MARRIAGE_AGES[0]} "
                         f"and {MARRIAGE_AGES[1]}"):
        c.add('life', label, 'timing', 'neutral', c.L('mw_none'),
              f"no bhukti of {', '.join(lords)} between ages {MARRIAGE_AGES[0]} and {MARRIAGE_AGES[1]}")
    s7 = (c.facts['lagna_sign_no'] + 5) % 12 + 1
    d9 = c.vl.get('D9')
    s9 = (d9['lagna_sign_no'] + 5) % 12 + 1 if d9 else s7
    c.add('life', label, 'partner', 'neutral',
          c.L('spouse', n7=c.L(f'sn.{s7}'), s7=c.sign(s7), pn=c.L(f'pn.{lord7}'), planet=c.pn(lord7),
              n9=c.L(f'sn.{s9}'), s9=c.sign(s9)),
          f"7th sign {RASIS[s7 - 1]}, 7th lord {lord7}, Navamsa 7th {RASIS[s9 - 1]}")


def _children(c, label, promise):
    lord5 = c.h[5]['lord']
    lords = list(dict.fromkeys([lord5, 'Jupiter']))
    _lord_periods(c, label, lords, CHILDREN_AGES, 'cw',
                  f"bhuktis of the 5th lord {lord5} or Jupiter between ages {CHILDREN_AGES[0]} "
                  f"and {CHILDREN_AGES[1]}")


def _life(c):
    promise = c.promise()
    for name, houses, sig, vargas, kp in TOPICS:
        if name == 'Strain (general)' or (c.minor and name in MINOR_TOPICS):
            continue
        _topic_block(c, name, houses, sig, vargas, promise)
    for name in ('Family life', 'General'):
        _rule_rows(c, 'life', c.topic(name), RULE_TOPICS[name])


# ── P5 current period ────────────────────────────────────────────────────────

def _tone_of(c, planet):
    nature = c.p[planet].get('functional_nature')
    dig = c.dignity(planet)
    cancelled = c.p[planet].get('debilitation_cancelled_by')
    if nature == 'Yogakaraka':
        tone, line = 'favourable', c.L('ptone.yogakaraka', planet=c.pn(planet))
    elif nature == 'Benefic':
        tone, line = 'favourable', c.L('ptone.favourable', planet=c.pn(planet))
    elif nature == 'Malefic':
        tone, line = 'challenging', c.L('ptone.challenging', planet=c.pn(planet))
    else:
        tone, line = 'mixed', c.L('ptone.mixed')
    if dig in FAVOURABLE_DIGNITY:
        line += c.L('strong_dignity', dignity=c.L(f'dig.{dig}'))
        tone = 'mixed' if tone == 'challenging' else tone
    elif dig == 'Debilitated' and not cancelled:
        line += c.L('weak_dignity')
        tone = 'mixed' if tone == 'favourable' else tone
    return tone, line


def _owned_text(c, planet):
    houses = c.owned(planet)
    return ', '.join(c.L('owned_one', h=h, meaning=c.meaning(h)) for h in houses)


def _period_line(c, level, planet, a, b):
    period = c.span(a, b)
    r = c.p[planet]
    lvl = c.L(f'level.{level}')
    if c.minor:
        text = c.L('child', level=lvl, planet=c.pn(planet), period=period)
        tone = 'neutral'
    else:
        house = r['house_whole_sign']
        if planet in NODES:
            sl = r['sign_lord']
            text = c.L('period_node', level=lvl, planet=c.pn(planet), period=period, house=house,
                       meaning=c.meaning(house), sl=c.pn(sl), owned=_owned_text(c, sl))
            tone, line = _tone_of(c, sl)
        else:
            text = c.L('period', level=lvl, planet=c.pn(planet), period=period, owned=_owned_text(c, planet),
                       house=house, meaning=c.meaning(house))
            tone, line = _tone_of(c, planet)
        text += line
        st = r['star_lord']
        if st in NODES:
            text += c.L('starlord_node', sl=c.pn(st), house=c.p[st]['house_whole_sign'])
        elif st != planet:
            text += c.L('starlord', sl=c.pn(st), owned=_owned_text(c, st))
    basis = (f"{level} lord {planet}: owns {r.get('houses_owned') or '-'}, in house {r['house_whole_sign']} "
             f"({r['sign']}), {r.get('dignity') or 'no dignity'}, functional {r.get('functional_nature') or '-'}, "
             f"star lord {r['star_lord']}")
    c.add('period', c.L(f'level.{level}'), level, tone, text, basis, period, c.status(a, b))


def _period(c):
    rows = c.dasa_rows()
    cur = c.running('AI_Dasa')
    if not cur:
        return
    dasa = c.running('AI_DasaPeriods')
    if dasa:
        _period_line(c, 'dasa', dasa['dasa_lord'], dasa['start_local'], dasa['end_local'])
    _period_line(c, 'bhukti', cur['bhukti_lord'], cur['start_local'], cur['end_local'])
    ant = c.running('AI_Antaram')
    if ant:
        _period_line(c, 'antaram', ant['antaram_lord'], ant['start_local'], ant['end_local'])
    i = rows.index(cur)
    for r in rows[i + 1:i + 3]:
        period = c.span(r['start_local'], r['end_local'])
        c.add('period', c.L('level.bhukti'), 'next', 'neutral',
              c.L('next', planet=f"{c.pn(r['dasa_lord'])} {c.L('level.dasa')} / {c.pn(r['bhukti_lord'])}",
                  level=c.L('level.bhukti'), period=period),
              f"{r['dasa_lord']} dasa, {r['bhukti_lord']} bhukti", period, c.status(r['start_local'], r['end_local']))


# ── P6 transits ──────────────────────────────────────────────────────────────

def _own_bindus(c, planet, sign_no):
    for r in c.t['AI_Ashtakavarga']:
        if r['planet'] == planet and r['row_type'] == 'sign' and r['sign_no'] == sign_no:
            return r['bindus']
    return None


def _transit_text(c, planet, sign_no, house):
    tone = TRANSIT_TONE[planet][house]
    text = c.L(f'{planet}.{house}')
    bindus = _own_bindus(c, planet, sign_no)
    if tone == 'challenging' and bindus is not None and bindus >= SUPPORT_BINDUS:
        text += c.L('support', bindus=bindus)
        tone = 'mixed'
    return tone, text, bindus


def _add_months(dt, n):
    y, m = divmod(dt.month - 1 + n, 12)
    return datetime(dt.year + y, m + 1, 1)


def _transits(c):
    S = 'transit'
    horizon = _add_months(c.now, TRANSIT_MONTHS)
    for planet in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
        stays = [r for r in c.t['AI_Transits'] if r['planet'] == planet]
        cur = next((r for r in stays if r['entry_local'] <= c.now < r['exit_local']), None)
        if cur:
            tone, text, bindus = _transit_text(c, planet, cur['sign_no'], cur['house_from_moon'])
            c.add(S, c.pn(planet), 'now', tone,
                  c.L('now', planet=c.pn(planet), sign=c.sign(cur['sign_no']), h=cur['house_from_moon'],
                      end=c.date(cur['exit_local']), text=text),
                  f"{planet} in {cur['sign']}, house {cur['house_from_moon']} from the Moon; own bindus {bindus}",
                  c.span(cur['entry_local'], cur['exit_local'], ages=False), 'running now')
        nxt = [r for r in stays if c.now < r['entry_local'] <= horizon][:TRANSIT_ROWS_PER_PLANET]
        for r in nxt:
            tone, text, bindus = _transit_text(c, planet, r['sign_no'], r['house_from_moon'])
            c.add(S, c.pn(planet), 'next', tone,
                  c.L('from', planet=c.pn(planet), start=c.date(r['entry_local']), sign=c.sign(r['sign_no']),
                      h=r['house_from_moon'], text=text),
                  f"{planet} enters {r['sign']} ({r['motion_at_entry']}), house {r['house_from_moon']} from the "
                  f"Moon; own bindus {bindus}",
                  c.span(r['entry_local'], r['exit_local'], ages=False), 'upcoming')
    sade = [r for r in c.t['AI_SadeSati'] if r['row_type'] == 'span' and r['phase'] != 'sade sati - whole'
            and r['end_local'] > c.now and r['start_local'] <= horizon]
    for r in sade:
        period = c.span(r['start_local'], r['end_local'], ages=False)
        c.add(S, c.pn('Saturn'), 'sade sati', 'challenging', c.L(f"sade.{r['phase']}", period=period),
              f"{r['phase']}: Saturn in {r['saturn_sign']}", period, c.status(r['start_local'], r['end_local']))
    if not sade:
        c.add(S, c.pn('Saturn'), 'sade sati', 'neutral', c.L('sade_none'), 'AI_SadeSati: no phase in the window')
    seen = set()
    for r in c.t['AI_DoubleTransit']:
        if len(seen) >= DOUBLE_TRANSIT_ROWS:
            break
        if r['house'] in DOUBLE_TRANSIT_HOUSES and r['house'] not in seen and r['end_local'] > c.now \
                and r['start_local'] <= horizon:
            seen.add(r['house'])
            a = max(r['start_local'], c.now)
            period = c.span(a, r['end_local'], ages=False)
            c.add(S, c.L('general'), 'double transit', 'favourable',
                  c.L('dt', period=period, house=r['house'], meaning=c.meaning(r['house'])),
                  f"house {r['house']} ({r['sign']}): Jupiter in {r['jupiter_sign']} ({r['jupiter_reaches_by']}), "
                  f"Saturn in {r['saturn_sign']} ({r['saturn_reaches_by']})", period, c.status(a, r['end_local']))


# ── P7 month calendar ────────────────────────────────────────────────────────

def _at(rows, moment, start='start_local', end='end_local'):
    for r in rows:
        if r[start] <= moment < r[end]:
            return r
    return None


def _nature_points(c, planet):
    nature = c.p[planet].get('functional_nature')
    return 1 if nature in GOOD_NATURE else -1 if nature == 'Malefic' else 0


def _tara_label(c, planet):
    for r in c.t['AI_PeriodFacts']:
        if r['period_lord'] == planet:
            return r.get('tara_of_position_label')
    return None


def _calendar(c):
    S = 'calendar'
    first = datetime(c.now.year, c.now.month, 1)
    for i in range(CALENDAR_MONTHS):
        start = _add_months(first, i)
        end = _add_months(first, i + 1)
        mid = start + timedelta(days=14)
        b = _at(c.dasa_rows(), mid)
        a = _at(c.t['AI_Antaram'], mid)
        if not b:
            continue
        parts, score = [], 0
        for name, planet in (('bhukti', b['bhukti_lord']), ('antaram', a['antaram_lord'] if a else None)):
            if planet:
                pts = _nature_points(c, planet)
                score += pts
                parts.append(f"{name} {planet} {pts:+d}")
        for planet, table in (('Jupiter', CAL_JUPITER), ('Saturn', CAL_SATURN)):
            stay = _at([r for r in c.t['AI_Transits'] if r['planet'] == planet], mid, 'entry_local', 'exit_local')
            if stay:
                pts = table.get(stay['house_from_moon'], 0)
                score += pts
                parts.append(f"{planet} {stay['house_from_moon']} from Moon {pts:+d}")
        if a:
            label = _tara_label(c, a['antaram_lord'])
            pts = CAL_TARA.get(label, 0)
            score += pts
            parts.append(f"tara {label} {pts:+d}")
        rating = ('favourable' if score >= CAL_FAVOURABLE_FROM else 'careful' if score <= CAL_CAREFUL_UPTO
                  else 'mixed')
        days = {}
        for r in c.t['AI_TopicWindows']:
            if r['topic'] == 'Strain (general)' or (c.minor and r['topic'] in MINOR_TOPICS):
                continue
            lo, hi = max(r['start_local'], start), min(r['end_local'], end)
            if hi > lo:
                days[r['topic']] = days.get(r['topic'], 0) + (hi - lo).total_seconds() / 86400 * r['layers_agreeing']
        top = None
        if days:
            order = [t[0] for t in TOPICS]
            top = max(days, key=lambda k: (round(days[k], 3), -order.index(k)))
        month = c.month(start)
        text = (c.L('month', month=month, rating=c.L(f'rating.{rating}'), topic=c.topic(top)) if top
                else c.L('month_none', month=month, rating=c.L(f'rating.{rating}')))
        tone = {'favourable': 'favourable', 'mixed': 'mixed', 'careful': 'challenging'}[rating]
        c.add(S, month, 'month', tone, text, f"score {score:+d}: " + '; '.join(parts) +
              (f"; main area {top} ({days[top]:.0f} window layer-days)" if top else ''),
              c.span(start, end - timedelta(days=1), ages=False), c.status(start, end))
    c.add(S, c.L('general'), 'rule', 'neutral', c.L('rule'), 'CALENDAR rule in predictions.py')


# ── P8 remedies ──────────────────────────────────────────────────────────────

def _remedies(c):
    S = 'remedies'
    picks = []
    dasa = c.running('AI_DasaPeriods')
    if dasa:
        picks.append((dasa['dasa_lord'], 'dasa'))
    benefics = [p for p in SEVEN if c.p[p].get('functional_nature') in GOOD_NATURE]
    if benefics:
        weakest = min(benefics, key=lambda p: (c.p[p].get('vimsopaka_shodasavarga') or 0, SEVEN.index(p)))
        if weakest not in [p for p, _ in picks]:
            picks.append((weakest, 'weak'))
    for planet, why in picks:
        r = T(f'rem.{planet}', c.lang)
        c.used.add(f'rem.{planet}')
        text = c.L('remedy', planet=c.pn(planet), why=c.L(f'remedy_why.{why}'), **r)
        basis = (f"running dasa lord {planet}" if why == 'dasa' else
                 f"{planet}: functional {c.p[planet].get('functional_nature')}, lowest vimsopaka "
                 f"{c.p[planet].get('vimsopaka_shodasavarga')}")
        c.add(S, c.pn(planet), 'remedy', 'neutral', text, basis)
    if picks:
        c.add(S, c.L('general'), 'note', 'neutral', c.L('remedy_note'), 'site policy')


# ── P9 summary ───────────────────────────────────────────────────────────────

def _summary(c):
    S = 'summary'
    f = c.facts
    label = c.L('section.summary')
    c.add(S, label, 'chart', 'neutral',
          c.L('sum.chart', lagna=c.sign(f['lagna_sign_no']), moon=c.sign(f['moon_sign_no']),
              nak=i18n.nak(f['moon_nakshatra_no'] - 1, c.lang)),
          f"lagna {f['lagna_sign']}, Moon {f['moon_sign']}, {f['moon_nakshatra']}")
    promise = c.promise()
    names = [t[0] for t in TOPICS if t[0] in promise and t[0] in SUMMARY_TOPICS
             and not (c.minor and t[0] in MINOR_TOPICS)]
    ranked = sorted(names, key=lambda n: (-_ratio(*promise[n]), names.index(n)))
    if len(ranked) >= 2:
        c.add(S, label, 'strongest', 'favourable',
              c.L('sum.strong', a=c.topic(ranked[0]), b=c.topic(ranked[1])),
              f"highest supports ratio: {ranked[0]} {_ratio(*promise[ranked[0]]):.2f}, "
              f"{ranked[1]} {_ratio(*promise[ranked[1]]):.2f}")
        c.add(S, label, 'effort', 'challenging', c.L('sum.effort', a=c.topic(ranked[-1])),
              f"lowest supports ratio: {ranked[-1]} {_ratio(*promise[ranked[-1]]):.2f}")
    cur = c.running('AI_Dasa')
    if cur:
        c.add(S, label, 'period', 'neutral',
              c.L('sum.period', dasa=c.pn(cur['dasa_lord']), bhukti=c.pn(cur['bhukti_lord']),
                  end=c.date(cur['end_local'])),
              f"AI_Dasa row running at the report date", c.span(cur['start_local'], cur['end_local']), 'running now')
    wins = [r for r in c.t['AI_TopicWindows'] if r['start_local'] > c.now
            and not (c.minor and r['topic'] in MINOR_TOPICS) and r['topic'] != 'Strain (general)']
    if wins:
        best = max(r['layers_agreeing'] for r in wins)
        r = min((r for r in wins if r['layers_agreeing'] == best), key=lambda r: r['start_local'])
        period = c.span(r['start_local'], r['end_local'])
        c.add(S, label, 'window', 'favourable', c.L('sum.window', topic=c.topic(r['topic']), period=period),
              f"first upcoming AI_TopicWindows row with {best} layers", period, 'upcoming')
    spans = [r for r in c.t['AI_SadeSati'] if r['row_type'] == 'span']
    on = next((r for r in spans if r['phase'] != 'sade sati - whole'
               and r['start_local'] <= c.now < r['end_local']), None)
    if on:
        whole = next((r for r in spans if r['phase'] == 'sade sati - whole'
                      and r['start_local'] <= c.now < r['end_local']), on)
        c.add(S, label, 'sade sati', 'challenging',
              c.L('sum.sade_on', phase=c.L(f"phase.{on['phase']}"), end=c.date(whole['end_local'])),
              f"{on['phase']} running", c.span(whole['start_local'], whole['end_local'], ages=False), 'running now')
    else:
        nxt = next((r for r in spans if r['phase'] == 'sade sati - whole' and r['start_local'] > c.now), None)
        if nxt:
            c.add(S, label, 'sade sati', 'neutral', c.L('sum.sade_next', start=c.date(nxt['start_local'])),
                  'AI_SadeSati: next cycle', c.span(nxt['start_local'], nxt['end_local'], ages=False), 'upcoming')
        else:
            c.add(S, label, 'sade sati', 'neutral', c.L('sum.sade_no'), 'AI_SadeSati: none running')
    yogas = found_yogas(c)
    key = next((k for k in KEY_YOGA_ORDER if k in yogas), None)
    if key:
        c.add(S, label, 'key yoga', 'favourable', c.L('sum.yoga', yoga=c.L(f'yname.{key}')),
              '; '.join(yogas[key]['notes'][:1]) or key)


# ── build ────────────────────────────────────────────────────────────────────

def _clean(rows):
    """Drop any row whose words break site policy (none should; this is the last guard)."""
    keep = []
    for r in rows:
        blob = ' '.join(str(r[k] or '') for k in ('topic', 'item', 'text', 'basis', 'period'))
        if BANNED.search(blob) or HEALTH.search(blob) or NATIVE_BANNED.search(blob):
            continue
        keep.append(r)
    return keep


def build_rows(res, ai, lang='en'):
    """The rows only, in sort_key order. ai: enrich(res) for the same report moment."""
    c = Reader(res, ai, lang)
    _summary(c)
    _personality(c)
    _strengths(c)
    _yogas(c)
    _life(c)
    _period(c)
    _transits(c)
    _calendar(c)
    if SHOW_REMEDIES:
        _remedies(c)
    for s in SECTIONS:
        if c._count.get(s):
            c.add(s, c.L('general'), 'disclaimer', 'neutral', c.L('disclaimer'), 'site policy')
    rows = sorted(_clean(c.rows), key=lambda r: r['sort_key'])
    return rows, c.used


def build(res, ai, lang='en'):
    """
    The predictions block: {'title', 'disclaimer', 'columns', 'sections',
    'labels', 'rows', 'summary', 'rule'}. 'sections' lists the section keys
    with their titles in the report language; 'labels' holds the tone and
    status words; 'summary' repeats the text of the summary rows.
    """
    rows, _ = build_rows(res, ai, lang)
    present = [s for s in SECTIONS if any(r['section'] == s for r in rows)]
    return {
        'title': T('title', lang),
        'disclaimer': T('disclaimer', lang),
        'columns': [{'name': n, 'meaning': m} for n, m in COLUMNS],
        'sections': [{'key': s, 'title': T(f'section.{s}', lang)} for s in present],
        'labels': {'tone': {k: T(f'tone.{k}', lang) for k in ('favourable', 'mixed', 'challenging', 'neutral')},
                   'status': {k: T(f'status.{k}', lang)
                              for k in ('running now', 'upcoming', 'past', 'dormant', 'always')},
                   'columns': {k: T(f'col.{k}', lang)
                               for k in ('section', 'topic', 'text', 'tone', 'period', 'status', 'basis')}},
        'rows': rows,
        'summary': [r['text'] for r in rows if r['section'] == 'summary' and r['item'] != 'disclaimer'],
        'rule': T('rule', lang),
    }
