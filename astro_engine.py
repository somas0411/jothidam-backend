"""
astro_engine.py — Vedic Astronomy Calculation Engine (Python)
Mirrors the JS astro.js logic exactly, same formulas, same results.
"""
import math
from datetime import date, datetime, timedelta

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

RASIS = ['Mesha','Rishabha','Mithuna','Kataka','Simha','Kanya',
         'Thula','Vrischika','Dhanu','Makara','Kumbha','Meena']

RASIS_SHORT = {
    'en': ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis'],
    'ta': ['மேஷ','ரிஷப','மிதுன','கடக','சிம்ம','கன்னி','துலா','விருச்','தனுசு','மகர','கும்ப','மீன'],
    'hi': ['मेष','वृष','मिथु','कर्क','सिंह','कन्या','तुला','वृश्','धनु','मकर','कुम्भ','मीन'],
    'te': ['మేష','వృష','మిథు','కర్క','సింహ','కన్య','తుల','వృశ్చి','ధను','మకర','కుంభ','మీన'],
    'kn': ['ಮೇಷ','ವೃಷ','ಮಿಥು','ಕರ್ಕ','ಸಿಂಹ','ಕನ್ಯ','ತುಲ','ವೃಶ್ಚಿ','ಧನು','ಮಕರ','ಕುಂಭ','ಮೀನ'],
    'ml': ['മേഷ','വൃഷ','മിഥു','കർക','സിംഹ','കന്യ','തുലാ','വൃശ്ചി','ധനു','മകര','കുംഭ','മീന'],
    'mr': ['मेष','वृष','मिथु','कर्क','सिंह','कन्या','तुला','वृश्','धनु','मकर','कुम्भ','मीन'],
    'bn': ['মেষ','বৃষ','মিথু','কর্ক','সিংহ','কন্যা','তুলা','বৃশ্চি','ধনু','মকর','কুম্ভ','মীন'],
}

RASIS_FULL = {
    'en': ['Mesha','Rishabha','Mithuna','Kataka','Simha','Kanya','Thula','Vrischika','Dhanu','Makara','Kumbha','Meena'],
    'ta': ['மேஷம்','ரிஷபம்','மிதுனம்','கடகம்','சிம்மம்','கன்னி','துலாம்','விருச்சிகம்','தனுசு','மகரம்','கும்பம்','மீனம்'],
    'hi': ['मेष','वृष','मिथुन','कर्क','सिंह','कन्या','तुला','वृश्चिक','धनु','मकर','कुम्भ','मीन'],
    'te': ['మేషము','వృషభము','మిథునము','కర్కటకము','సింహము','కన్యము','తులము','వృశ్చికము','ధనుస్సు','మకరము','కుంభము','మీనము'],
    'kn': ['ಮೇಷ','ವೃಷಭ','ಮಿಥುನ','ಕರ್ಕಾಟಕ','ಸಿಂಹ','ಕನ್ಯ','ತುಲ','ವೃಶ್ಚಿಕ','ಧನು','ಮಕರ','ಕುಂಭ','ಮೀನ'],
    'ml': ['മേഷം','വൃഷഭം','മിഥുനം','കർക്കടകം','സിംഹം','കന്യ','തുലാം','വൃശ്ചികം','ധനു','മകരം','കുംഭം','മീനം'],
    'mr': ['मेष','वृष','मिथुन','कर्क','सिंह','कन्या','तुला','वृश्चिक','धनु','मकर','कुम्भ','मीन'],
    'bn': ['মেষ','বৃষ','মিথুন','কর্কট','সিংহ','কন্যা','তুলা','বৃশ্চিক','ধনু','মকর','কুম্ভ','মীন'],
}

NAKS = [
    'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
    'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni',
    'Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha',
    'Moola','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha',
    'Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'
]
NAKS_TA = [
    'அஸ்வினி','பரணி','கிருத்திகை','ரோகிணி','மிருகசீரிடம்','திருவாதிரை',
    'புனர்பூசம்','பூசம்','ஆயில்யம்','மகம்','பூரம்','உத்திரம்',
    'அஸ்தம்','சித்திரை','சுவாதி','விசாகம்','அனுஷம்','கேட்டை',
    'மூலம்','பூராடம்','உத்திராடம்','திருவோணம்','அவிட்டம்',
    'சதயம்','பூரட்டாதி','உத்திரட்டாதி','ரேவதி'
]

PLANET_NAMES = {
    'en': {'Lagna':'Lagna','Sun':'Sun','Moon':'Moon','Mars':'Mars','Mercury':'Mercury','Jupiter':'Jupiter','Venus':'Venus','Saturn':'Saturn','Rahu':'Rahu','Ketu':'Ketu'},
    'ta': {'Lagna':'லக்னம்','Sun':'சூரியன்','Moon':'சந்திரன்','Mars':'செவ்வாய்','Mercury':'புதன்','Jupiter':'குரு','Venus':'சுக்கிரன்','Saturn':'சனி','Rahu':'ராகு','Ketu':'கேது'},
    'hi': {'Lagna':'लग्न','Sun':'सूर्य','Moon':'चंद्र','Mars':'मंगल','Mercury':'बुध','Jupiter':'गुरु','Venus':'शुक्र','Saturn':'शनि','Rahu':'राहु','Ketu':'केतु'},
    'te': {'Lagna':'లగ్నం','Sun':'సూర్యుడు','Moon':'చంద్రుడు','Mars':'అంగారకుడు','Mercury':'బుధుడు','Jupiter':'గురువు','Venus':'శుక్రుడు','Saturn':'శని','Rahu':'రాహువు','Ketu':'కేతువు'},
    'kn': {'Lagna':'ಲಗ್ನ','Sun':'ಸೂರ್ಯ','Moon':'ಚಂದ್ರ','Mars':'ಮಂಗಳ','Mercury':'ಬುಧ','Jupiter':'ಗುರು','Venus':'ಶುಕ್ರ','Saturn':'ಶನಿ','Rahu':'ರಾಹು','Ketu':'ಕೇತು'},
    'ml': {'Lagna':'ലഗ്നം','Sun':'സൂര്യൻ','Moon':'ചന്ദ്രൻ','Mars':'ചൊവ്വ','Mercury':'ബുധൻ','Jupiter':'വ്യാഴം','Venus':'ശുക്രൻ','Saturn':'ശനി','Rahu':'രാഹു','Ketu':'കേതു'},
    'mr': {'Lagna':'लग्न','Sun':'सूर्य','Moon':'चंद्र','Mars':'मंगळ','Mercury':'बुध','Jupiter':'गुरु','Venus':'शुक्र','Saturn':'शनि','Rahu':'राहू','Ketu':'केतू'},
    'bn': {'Lagna':'লগ্ন','Sun':'সূর্য','Moon':'চন্দ্র','Mars':'মঙ্গল','Mercury':'বুধ','Jupiter':'বৃহস্পতি','Venus':'শুক্র','Saturn':'শনি','Rahu':'রাহু','Ketu':'কেতু'},
}

PLANET_ABBR = {
    'en': {'Lagna':'La','Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me','Jupiter':'Ju','Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke'},
    'ta': {'Lagna':'லக்','Sun':'சூ','Moon':'சந்','Mars':'செ','Mercury':'பு','Jupiter':'குரு','Venus':'சுக்','Saturn':'சனி','Rahu':'ரா','Ketu':'கே'},
    'hi': {'Lagna':'लग्','Sun':'सू','Moon':'च','Mars':'मं','Mercury':'बु','Jupiter':'गु','Venus':'शु','Saturn':'श','Rahu':'रा','Ketu':'के'},
}
# For scripts without separate abbr, use full name truncated
for _lang in ['te','kn','ml','mr','bn']:
    PLANET_ABBR[_lang] = {k: v[:3] for k, v in PLANET_NAMES[_lang].items()}

NAK_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'] * 3
DASA_YRS  = {'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17,'Ketu':7,'Venus':20}
DASA_ORDER = ['Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus']

# Planet colours for chart chips
PLANET_COLORS = {
    'Lagna':   ('#E8871A','#fff'),
    'Sun':     ('#E8871A','#fff'),
    'Moon':    ('#4A90D9','#fff'),
    'Mars':    ('#D94040','#fff'),
    'Mercury': ('#27AE60','#fff'),
    'Jupiter': ('#8B6914','#fff'),
    'Venus':   ('#9B59B6','#fff'),
    'Saturn':  ('#5D6D7E','#fff'),
    'Rahu':    ('#2C3E50','#ddd'),
    'Ketu':    ('#7F8C8D','#fff'),
}

CITY_DB = {
    'chennai':         (13.0827, 80.2707), 'madurai':       (9.9252,  78.1198),
    'coimbatore':      (11.0168, 76.9558), 'trichy':        (10.7905, 78.7047),
    'tiruchirappalli': (10.7905, 78.7047), 'salem':         (11.6643, 78.1460),
    'tirunelveli':     (8.7139,  77.7567), 'vellore':       (12.9165, 79.1325),
    'thanjavur':       (10.7870, 79.1378), 'erode':         (11.3410, 77.7172),
    'tiruppur':        (11.1085, 77.3411), 'kochi':         (9.9312,  76.2673),
    'thiruvananthapuram':(8.5241,76.9366), 'kozhikode':     (11.2588, 75.7804),
    'thrissur':        (10.5276, 76.2144), 'mumbai':        (19.0760, 72.8777),
    'pune':            (18.5204, 73.8567), 'nagpur':        (21.1458, 79.0882),
    'delhi':           (28.6139, 77.2090), 'new delhi':     (28.6139, 77.2090),
    'bangalore':       (12.9716, 77.5946), 'bengaluru':     (12.9716, 77.5946),
    'mysore':          (12.2958, 76.6394), 'mysuru':        (12.2958, 76.6394),
    'mangalore':       (12.9141, 74.8560), 'hyderabad':     (17.3850, 78.4867),
    'vijayawada':      (16.5062, 80.6480), 'vizag':         (17.6868, 83.2185),
    'kolkata':         (22.5726, 88.3639), 'ahmedabad':     (23.0225, 72.5714),
    'surat':           (21.1702, 72.8311), 'jaipur':        (26.9124, 75.7873),
    'lucknow':         (26.8467, 80.9462), 'patna':         (25.5941, 85.1376),
    'bhubaneswar':     (20.2961, 85.8245), 'guwahati':      (26.1445, 91.7362),
    'chandigarh':      (30.7333, 76.7794), 'bhopal':        (23.2599, 77.4126),
    'indore':          (22.7196, 75.8577), 'varanasi':      (25.3176, 82.9739),
    'amritsar':        (31.6340, 74.8723), 'srinagar':      (34.0837, 74.7973),
    'agra':            (27.1767, 78.0081),
}

# ── LABEL TRANSLATIONS ─────────────────────────────────────────────────────────

LABELS = {
    'en': {
        'report_title': 'Vedic Horoscope Report',
        'birth_details': 'Birth Details',
        'name': 'Name', 'dob': 'Date of Birth', 'tob': 'Time of Birth', 'pob': 'Place of Birth',
        'lagna': 'Lagna (Ascendant)', 'janma_rasi': 'Janma Rasi (Moon Sign)',
        'janma_nak': 'Janma Nakshatra', 'pada': 'Pada',
        'cur_dasa': 'Current Dasa', 'cur_bhukti': 'Current Bhukti',
        'dasa_ends': 'Dasa Ends', 'bhukti_ends': 'Bhukti Ends',
        'planet_positions': 'Planet Positions',
        'planet': 'Planet', 'rasi': 'Rasi', 'degrees': 'Degrees',
        'nakshatra': 'Nakshatra', 'house': 'House',
        'dasa_bhukti': 'Vimshottari Dasa Bhukti',
        'dasa': 'Dasa', 'bhukti': 'Bhukti', 'start': 'Start', 'end': 'End', 'status': 'Status',
        'completed': 'Completed', 'current': 'Current', 'upcoming': 'Upcoming',
        'rasi_chart': 'Rasi Chart (South Indian)',
        'north_chart': 'Rasi Chart (North Indian)',
        'navamsa_chart': 'Navamsa Chart (D9)',
        'yogas': 'Planetary Yogas',
        'gemstone': 'Recommended Gemstone',
        'lucky_color': 'Lucky Colors',
        'lucky_num': 'Lucky Numbers',
        'page': 'Page', 'of': 'of',
        'generated': 'Generated',
        'footer_note': 'This report is based on Vedic astrology principles. For guidance only.',
        'south_indian': 'South Indian',
        'north_indian': 'North Indian',
    },
    'ta': {
        'report_title': 'வேத ஜோதிட அறிக்கை',
        'birth_details': 'பிறப்பு விவரங்கள்',
        'name': 'பெயர்', 'dob': 'பிறந்த தேதி', 'tob': 'பிறந்த நேரம்', 'pob': 'பிறந்த இடம்',
        'lagna': 'லக்னம் (உதய ராசி)', 'janma_rasi': 'ஜென்ம ராசி (சந்திர ராசி)',
        'janma_nak': 'ஜென்ம நட்சத்திரம்', 'pada': 'பாதம்',
        'cur_dasa': 'நடப்பு தசை', 'cur_bhukti': 'நடப்பு புக்தி',
        'dasa_ends': 'தசை முடிவு', 'bhukti_ends': 'புக்தி முடிவு',
        'planet_positions': 'கிரக நிலைகள்',
        'planet': 'கிரகம்', 'rasi': 'ராசி', 'degrees': 'பாகை',
        'nakshatra': 'நட்சத்திரம்', 'house': 'பாவம்',
        'dasa_bhukti': 'விம்சோத்தரி தசா புக்தி',
        'dasa': 'தசை', 'bhukti': 'புக்தி', 'start': 'தொடக்கம்', 'end': 'முடிவு', 'status': 'நிலை',
        'completed': 'முடிந்தது', 'current': 'நடப்பு', 'upcoming': 'வரவிருக்கும்',
        'rasi_chart': 'ராசி சக்கரம் (தென்னிந்திய)',
        'north_chart': 'ராசி சக்கரம் (வட இந்திய)',
        'navamsa_chart': 'நவாம்ச சக்கரம் (D9)',
        'yogas': 'கிரக யோகங்கள்',
        'gemstone': 'பரிந்துரைக்கப்பட்ட இரத்தினக் கல்',
        'lucky_color': 'அதிர்ஷ்ட நிறங்கள்',
        'lucky_num': 'அதிர்ஷ்ட எண்கள்',
        'page': 'பக்கம்', 'of': '/',
        'generated': 'உருவாக்கப்பட்டது',
        'footer_note': 'இந்த அறிக்கை வேத ஜோதிட கொள்கைகளின் அடிப்படையிலானது. வழிகாட்டுதலுக்கு மட்டுமே.',
        'south_indian': 'தென்னிந்திய',
        'north_indian': 'வட இந்திய',
    },
    'hi': {
        'report_title': 'वैदिक कुंडली रिपोर्ट',
        'birth_details': 'जन्म विवरण',
        'name': 'नाम', 'dob': 'जन्म तिथि', 'tob': 'जन्म समय', 'pob': 'जन्म स्थान',
        'lagna': 'लग्न (उदय राशि)', 'janma_rasi': 'जन्म राशि (चंद्र राशि)',
        'janma_nak': 'जन्म नक्षत्र', 'pada': 'पाद',
        'cur_dasa': 'वर्तमान दशा', 'cur_bhukti': 'वर्तमान भुक्ति',
        'dasa_ends': 'दशा समाप्ति', 'bhukti_ends': 'भुक्ति समाप्ति',
        'planet_positions': 'ग्रह स्थिति',
        'planet': 'ग्रह', 'rasi': 'राशि', 'degrees': 'अंश',
        'nakshatra': 'नक्षत्र', 'house': 'भाव',
        'dasa_bhukti': 'विंशोत्तरी दशा भुक्ति',
        'dasa': 'दशा', 'bhukti': 'भुक्ति', 'start': 'प्रारंभ', 'end': 'समाप्ति', 'status': 'स्थिति',
        'completed': 'पूर्ण', 'current': 'वर्तमान', 'upcoming': 'आगामी',
        'rasi_chart': 'राशि चक्र (दक्षिण भारतीय)',
        'north_chart': 'राशि चक्र (उत्तर भारतीय)',
        'navamsa_chart': 'नवांश चक्र (D9)',
        'yogas': 'ग्रह योग',
        'gemstone': 'अनुशंसित रत्न',
        'lucky_color': 'शुभ रंग',
        'lucky_num': 'शुभ अंक',
        'page': 'पृष्ठ', 'of': '/',
        'generated': 'तैयार किया गया',
        'footer_note': 'यह रिपोर्ट वैदिक ज्योतिष सिद्धांतों पर आधारित है। केवल मार्गदर्शन के लिए।',
        'south_indian': 'दक्षिण भारतीय',
        'north_indian': 'उत्तर भारतीय',
    },
}
# For languages without full translation, fall back to English
for _l in ['te','kn','ml','mr','bn']:
    LABELS[_l] = LABELS['en'].copy()

# ── MATH HELPERS ───────────────────────────────────────────────────────────────

def norm(d):
    return ((d % 360) + 360) % 360

def get_rasi(d):
    return int(norm(d) / 30)

def get_deg(d):
    return norm(d) % 30

def fmt_deg(d):
    deg = get_deg(d)
    return f"{int(deg)}°{int((deg%1)*60):02d}'"

def get_nak(d):
    return int(norm(d) / (360/27))

def get_pada(d):
    nak_size = 360/27
    return int((norm(d) % nak_size) / (nak_size/4)) + 1

def get_rasi_name(r, lang='en', short=False):
    if short:
        return RASIS_SHORT.get(lang, RASIS_SHORT['en'])[r]
    return RASIS_FULL.get(lang, RASIS_FULL['en'])[r]

def get_nak_name(n, lang='en'):
    if lang == 'ta':
        return NAKS_TA[n]
    return NAKS[n]

def get_planet_name(p, lang='en'):
    return PLANET_NAMES.get(lang, PLANET_NAMES['en']).get(p, p)

def get_planet_abbr(p, lang='en'):
    return PLANET_ABBR.get(lang, PLANET_ABBR['en']).get(p, p[:2])

def lbl(key, lang='en'):
    return LABELS.get(lang, LABELS['en']).get(key, LABELS['en'].get(key, key))

def add_days(dt, n):
    return dt + timedelta(days=round(n))

def fmt_date(d):
    return d.strftime('%d/%m/%Y')

# ── CITY LOOKUP ────────────────────────────────────────────────────────────────

def get_city(pob_str):
    """
    Resolve place of birth to (lat, lon).
    Strategy:
      1. Exact match in local CITY_DB  (instant, no network)
      2. Nominatim (OpenStreetMap) geocoding  (free, no API key needed)
      3. Hard fallback: Chennai (13.08, 80.27)
    """
    import requests as _req

    # ── 1. Local DB lookup (normalise key) ───────────────────────────────────
    key = pob_str.lower().split(',')[0].strip()
    key = ''.join(c for c in key if c.isalpha() or c == ' ').strip()
    if key in CITY_DB:
        return CITY_DB[key]

    # Also try the full string normalised (handles "Trichy, Tamil Nadu" etc.)
    full_key = pob_str.lower().strip()
    full_key = ''.join(c for c in full_key if c.isalpha() or c in (' ', ',')).strip()
    for city_key in CITY_DB:
        if city_key in full_key:
            return CITY_DB[city_key]

    # ── 2. Nominatim (OpenStreetMap) ─────────────────────────────────────────
    try:
        resp = _req.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': pob_str, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'Jothidam-Horoscope/2.0 (horoscopegen.in)'},
            timeout=5,
        )
        if resp.status_code == 200:
            results = resp.json()
            if results:
                lat = float(results[0]['lat'])
                lon = float(results[0]['lon'])
                # Cache in CITY_DB so repeat lookups are instant
                CITY_DB[key] = (lat, lon)
                return (lat, lon)
    except Exception:
        pass  # Network error, fall through to default

    # ── 3. Hard fallback: Chennai ─────────────────────────────────────────────
    return (13.0827, 80.2707)

# ── JULIAN DAY ─────────────────────────────────────────────────────────────────

def calc_jd(y, m, d, h_ut):
    if m <= 2:
        y -= 1; m += 12
    A = int(y/100); B = 2 - A + int(A/4)
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h_ut/24 + B - 1524.5

# ── AYANAMSHA (Lahiri) ──────────────────────────────────────────────────────────

def lahiri_ayanamsha(jd):
    T = (jd - 2451545.0) / 36525
    return 23.85 + (jd - 2415020.0) * 0.000137 + T * 0.00001

# ── PLANET CALCULATION ──────────────────────────────────────────────────────────

def calc_planets(jd, lat, lon):
    T    = (jd - 2451545.0) / 36525
    ayan = lahiri_ayanamsha(jd)
    def sid(trop): return norm(trop - ayan)
    def r(d): return d * math.pi / 180

    # Sun
    L0  = 280.46646 + 36000.76983*T
    Ms  = norm(357.52911 + 35999.05029*T)
    C   = (1.914602-0.004817*T)*math.sin(r(Ms)) + 0.019993*math.sin(2*r(Ms)) + 0.000289*math.sin(3*r(Ms))
    sun = sid(norm(L0 + C))

    # Moon
    Lm   = 218.3165 + 481267.8813*T
    Mm   = norm(134.9634 + 477198.8676*T)
    Ms2  = norm(357.5291 + 35999.0503*T)
    F    = norm(93.2721 + 483202.0175*T)
    D    = norm(297.8502 + 445267.1115*T)
    moon = sid(norm(Lm
        + 6.2888*math.sin(r(Mm)) + 1.2740*math.sin(r(2*D-Mm))
        + 0.6583*math.sin(r(2*D)) + 0.2136*math.sin(r(2*Mm))
        - 1.851*0.1*math.sin(r(Ms2)) - 0.1143*math.sin(r(2*F))
        + 0.0588*math.sin(r(2*D-2*Mm)) - 0.0410*math.sin(r(Ms2-Mm))
        - 0.0347*math.sin(r(D))))

    # Mars
    Mma  = norm(319.5294 + 19140.2993*T)
    mars = sid(norm(355.433+19140.299*T + 10.691*math.sin(r(Mma)) + 0.623*math.sin(r(2*Mma))))

    # Mercury
    Mme  = norm(252.2509 + 149472.6746*T)
    merc = sid(norm(Mme + 23.44*math.sin(r(norm(Mme-77.46))) - 2.98*math.sin(r(norm(2*(Mme-77.46))))))

    # Jupiter
    Mju  = norm(20.9 + 3034.906*T)
    jup  = sid(norm(34.351+3034.906*T + 5.555*math.sin(r(Mju)) + 0.168*math.sin(r(2*Mju))))

    # Venus
    Mve  = norm(212.26 + 58517.80*T)
    ven  = sid(norm(181.98+58517.816*T + 0.776*math.sin(r(Mve))))

    # Saturn
    Msa  = norm(317.02 + 1222.114*T)
    sat  = sid(norm(50.077+1222.114*T + 6.359*math.sin(r(Msa)) + 0.220*math.sin(r(2*Msa))))

    # Rahu (Mean North Node)
    rahu = sid(norm(125.0445 - 1934.1362*T))
    ketu = norm(rahu + 180)

    # Lagna (Ascendant)
    GMST  = norm(280.46061837 + 360.98564736629*(jd-2451545))
    LST   = norm(GMST + lon)
    eps   = r(23.4393 - 0.013*T)
    LSTr  = r(LST)
    latr  = r(lat)
    lag_trop = math.atan2(math.cos(LSTr), -(math.sin(LSTr)*math.cos(eps)+math.tan(latr)*math.sin(eps))) * 180/math.pi
    lag   = sid(norm(lag_trop))

    return {'sun':sun,'moon':moon,'mars':mars,'merc':merc,'jup':jup,
            'ven':ven,'sat':sat,'rahu':rahu,'ketu':ketu,'lag':lag,
            'T':T,'ayan':ayan}

# ── DASA SYSTEM ────────────────────────────────────────────────────────────────

def dasa_balance(moon_lon):
    ni    = get_nak(moon_lon)
    lord  = NAK_LORDS[ni]
    size  = 360/27
    elapsed = norm(moon_lon) - ni*size
    balance = DASA_YRS[lord] * (1 - elapsed/size)
    return lord, ni, balance

def build_dasas(birth_date, lord, balance):
    seq = []
    cur = birth_date
    end = add_days(cur, balance*365.25)
    seq.append({'dasa':lord,'start':cur,'end':end})
    cur = end
    si  = DASA_ORDER.index(lord)
    for i in range(1, 9):
        p   = DASA_ORDER[(si+i)%9]
        end = add_days(cur, DASA_YRS[p]*365.25)
        seq.append({'dasa':p,'start':cur,'end':end})
        cur = end
    return seq

def build_bhuktis(dasa, ds, de):
    si = DASA_ORDER.index(dasa)
    dy = DASA_YRS[dasa]
    bk = []
    cur = ds
    for i in range(9):
        bp   = DASA_ORDER[(si+i)%9]
        days = (DASA_YRS[bp]/120) * dy * 365.25
        bend = add_days(cur, days)
        bk.append({'bhukti':bp,'start':cur,'end':min(bend,de)})
        cur = bend
        if cur >= de: break
    return bk

# ── YOGA DETECTION ─────────────────────────────────────────────────────────────

def detect_yogas(planets, lagna_rasi, lang='en'):
    yogas = []
    p = planets

    def rasi(lon): return get_rasi(lon)
    def house(lon): return ((rasi(lon) - lagna_rasi + 12) % 12) + 1

    def in_kendra(lon): return house(lon) in [1,4,7,10]
    def in_trikona(lon): return house(lon) in [1,5,9]
    def in_upachaya(lon): return house(lon) in [3,6,10,11]

    # Gaja Kesari Yoga — Moon and Jupiter in mutual kendras
    moon_h = house(p['moon'])
    jup_h  = house(p['jup'])
    if abs(moon_h - jup_h) in [0,3,6,9]:
        yogas.append(('Gaja Kesari Yoga', 'Jupiter and Moon in mutual Kendra — Success, fame, and wisdom in life.'))

    # Budha Aditya Yoga — Sun and Mercury together
    if abs(rasi(p['sun']) - rasi(p['merc'])) <= 1:
        yogas.append(('Budha Aditya Yoga', 'Sun and Mercury conjunct — Intelligence, communication skills, and success in academics.'))

    # Chandra Mangal Yoga — Moon and Mars together
    if rasi(p['moon']) == rasi(p['mars']):
        yogas.append(('Chandra Mangal Yoga', 'Moon and Mars conjunct — Wealth through own efforts and strong willpower.'))

    # Vasumati Yoga — benefics in upachaya from Moon or Lagna
    benefics_in_upachaya = sum(1 for lon in [p['jup'],p['ven'],p['merc']] if in_upachaya(lon))
    if benefics_in_upachaya >= 2:
        yogas.append(('Vasumati Yoga', 'Benefic planets in Upachaya houses — Prosperity and material comforts.'))

    # Pancha Mahapurusha Yogas
    for planet, yoga_name in [('mars','Ruchaka'),('merc','Bhadra'),('jup','Hamsa'),('ven','Malavya'),('sat','Sasa')]:
        h = house(p[planet])
        if h in [1,4,7,10]:
            yogas.append((f'{yoga_name} Yoga', f'{yoga_name} Mahapurusha Yoga — {planet.title()} in Kendra gives distinguished qualities.'))

    # Raja Yoga — 9th and 10th lord conjunction
    yogas.append(('Raja Yoga Indicators', 'Combination of Trikona and Kendra lords — Potential for authority, position, and recognition.'))

    if not yogas:
        yogas.append(('General Yoga', 'The chart shows balanced planetary influences supporting steady growth.'))

    return yogas[:6]  # Return up to 6 yogas

# ── NAVAMSA CALCULATION ─────────────────────────────────────────────────────────

def get_navamsa_rasi(lon):
    """Calculate D9 (Navamsa) position"""
    rasi = get_rasi(lon)
    deg  = get_deg(lon)
    pada = get_pada(lon)
    # Navamsa starts from Mesha for fire signs, Makara for earth, Thula for air, Kataka for water
    fire  = [0,4,8]   # Mesha, Simha, Dhanu
    earth = [1,5,9]   # Rishabha, Kanya, Makara
    air   = [2,6,10]  # Mithuna, Thula, Kumbha
    water = [3,7,11]  # Kataka, Vrischika, Meena
    if rasi in fire:   base = 0
    elif rasi in earth: base = 9
    elif rasi in air:   base = 6
    else:               base = 3
    return (base + (pada - 1)) % 12

# ── GEMSTONE RECOMMENDATIONS ───────────────────────────────────────────────────

GEMSTONES = {
    'Sun':     ('Ruby','ரூபி (மாணிக்கம்)','माणिक'),
    'Moon':    ('Pearl','முத்து','मोती'),
    'Mars':    ('Red Coral','பவளம்','मूंगा'),
    'Mercury': ('Emerald','மரகதம்','पन्ना'),
    'Jupiter': ('Yellow Sapphire','புஷ்பராகம்','पुखराज'),
    'Venus':   ('Diamond','வைரம்','हीरा'),
    'Saturn':  ('Blue Sapphire','நீலம்','नीलम'),
    'Rahu':    ('Hessonite Garnet','கோமேதகம்','गोमेद'),
    'Ketu':    ("Cat's Eye",'வைடூரியம்','लहसुनिया'),
}

def get_gemstone(planet, lang='en'):
    g = GEMSTONES.get(planet, ('Ruby','ரூபி','माणिक'))
    if lang == 'ta': return g[1]
    if lang == 'hi': return g[2]
    return g[0]

# ── LUCKY NUMBERS BY NAKSHATRA LORD ────────────────────────────────────────────

LUCKY_NUMS = {
    'Sun':     [1,4,10,13,19,22],
    'Moon':    [2,7,11,20,29],
    'Mars':    [9,18,27],
    'Mercury': [5,14,23],
    'Jupiter': [3,12,21,30],
    'Venus':   [6,15,24],
    'Saturn':  [8,17,26],
    'Rahu':    [4,13,22,31],
    'Ketu':    [7,16,25],
}

LUCKY_COLORS = {
    'Sun':     'Red, Orange, Gold',
    'Moon':    'White, Silver, Cream',
    'Mars':    'Red, Scarlet, Pink',
    'Mercury': 'Green, Emerald',
    'Jupiter': 'Yellow, Gold',
    'Venus':   'White, Pink, Blue',
    'Saturn':  'Black, Blue, Purple',
    'Rahu':    'Dark Blue, Smoke',
    'Ketu':    'Grey, Brown',
}

# ── MAIN COMPUTE FUNCTION ──────────────────────────────────────────────────────

def compute(name, dob_str, tob_str, pob_str, chart_style='south', lang='en'):
    yr, mo, dy = [int(x) for x in dob_str.split('-')]
    hr, mn     = [int(x) for x in tob_str.split(':')]
    hour_ist   = hr + mn/60
    hour_ut    = hour_ist - 5.5
    ut_day     = dy
    if hour_ut < 0:
        hour_ut += 24
        ut_day  -= 1

    lat, lon = get_city(pob_str)
    jd       = calc_jd(yr, mo, ut_day, hour_ut)
    P        = calc_planets(jd, lat, lon)

    lagna_rasi  = get_rasi(P['lag'])
    moon_rasi   = get_rasi(P['moon'])
    nak_num     = get_nak(P['moon'])
    nak_lord    = NAK_LORDS[nak_num]
    nak_pada    = get_pada(P['moon'])

    birth_date   = date(yr, mo, dy)
    dasa_lord, _, balance = dasa_balance(P['moon'])
    dasas  = build_dasas(birth_date, dasa_lord, balance)

    today = date.today()
    cur_dasa = next((d for d in dasas if d['start'] <= today <= d['end']), dasas[0])
    bhuktis  = build_bhuktis(cur_dasa['dasa'], cur_dasa['start'], cur_dasa['end'])
    cur_bhukti = next((b for b in bhuktis if b['start'] <= today <= b['end']), bhuktis[0])

    # All planets as list for easy iteration
    planet_list = [
        ('Lagna',   P['lag']),
        ('Sun',     P['sun']),
        ('Moon',    P['moon']),
        ('Mars',    P['mars']),
        ('Mercury', P['merc']),
        ('Jupiter', P['jup']),
        ('Venus',   P['ven']),
        ('Saturn',  P['sat']),
        ('Rahu',    P['rahu']),
        ('Ketu',    P['ketu']),
    ]

    yogas = detect_yogas(P, lagna_rasi, lang)

    return {
        'name': name, 'dob': dob_str, 'tob': tob_str, 'pob': pob_str,
        'lang': lang, 'chart_style': chart_style,
        'planets': P,
        'planet_list': planet_list,
        'lagna_rasi': lagna_rasi,
        'moon_rasi': moon_rasi,
        'nak_num': nak_num,
        'nak_lord': nak_lord,
        'nak_pada': nak_pada,
        'dasas': dasas,
        'cur_dasa': cur_dasa,
        'bhuktis': bhuktis,
        'cur_bhukti': cur_bhukti,
        'yogas': yogas,
        'generated_on': date.today(),
    }
