"""
astro_engine.py — HoroscopeGen calculation engine.

One function, compute(), returns everything the web page, the Excel workbook
and the PDF need, so the three can never disagree.

Astronomy comes from the Swiss Ephemeris (pyswisseph, built-in Moshier mode,
no data files required). Three systems are produced from one birth moment:

  * Vedic (Parashari): D1 Rasi, D9 Navamsa, Sripati Bhava, panchangam,
    Vimshottari dasa / bhukti / antaram.
  * KP (Krishnamurti Paddhati): KP ayanamsha, Placidus cusps, star / sub /
    sub-sub lords, 4-level significators, ruling planets, Vimshottari.
  * ALP (Akshaya Lagna Paddhati): birth lagna progressed at 30 degrees per
    10 years (one nakshatra pada = 1 year 1 month 10 days).

All names in the returned dict are English keys; i18n.py localises them.
"""
from __future__ import annotations

import threading
from datetime import date, datetime, timedelta, timezone

import swisseph as swe

try:  # Python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

# ── CONSTANTS ─────────────────────────────────────────────────────────────────

RASIS = ['Mesha', 'Rishabha', 'Mithuna', 'Kataka', 'Simha', 'Kanya',
         'Thula', 'Vrischika', 'Dhanu', 'Makara', 'Kumbha', 'Meena']

NAKS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Moola', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha',
    'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati',
]

PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

SIGN_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury',
              'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']

# Vimshottari: order starts at Ketu (lord of Ashwini)
DASA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASA_YRS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
            'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}
NAK_LORDS = DASA_ORDER * 3

YEAR_DAYS = 365.25            # length of a dasa / ALP year
NAK_SIZE = 360.0 / 27         # 13 deg 20 min
PADA_SIZE = NAK_SIZE / 4      # 3 deg 20 min
ALP_DEG_PER_YEAR = 3.0        # 30 degrees per 10 years

EXALT_SIGN = {'Sun': 0, 'Moon': 1, 'Mars': 9, 'Mercury': 5, 'Jupiter': 3, 'Venus': 11, 'Saturn': 6}
OWN_SIGNS = {'Sun': [4], 'Moon': [3], 'Mars': [0, 7], 'Mercury': [2, 5],
             'Jupiter': [8, 11], 'Venus': [1, 6], 'Saturn': [9, 10]}
# Combustion orbs in degrees from the Sun: (direct, retrograde)
COMBUST_ORB = {'Moon': (12, 12), 'Mars': (17, 17), 'Mercury': (14, 12),
               'Jupiter': (11, 11), 'Venus': (10, 8), 'Saturn': (15, 15)}

TITHIS = ['Prathama', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami', 'Shashthi',
          'Saptami', 'Ashtami', 'Navami', 'Dashami', 'Ekadashi', 'Dwadashi',
          'Trayodashi', 'Chaturdashi']
YOGAS = ['Vishkambha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana', 'Atiganda',
         'Sukarma', 'Dhriti', 'Shoola', 'Ganda', 'Vriddhi', 'Dhruva', 'Vyaghata',
         'Harshana', 'Vajra', 'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva',
         'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma', 'Indra', 'Vaidhriti']
KARANAS_MOVABLE = ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti']
WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
WEEKDAY_LORDS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']

AYANAMSHAS = {
    'lahiri':     ('Lahiri (Chitrapaksha)', swe.SIDM_LAHIRI),
    'kp':         ('Krishnamurti (KP)',     swe.SIDM_KRISHNAMURTI),
    'raman':      ('B.V. Raman',            swe.SIDM_RAMAN),
    'yukteshwar': ('Sri Yukteshwar',        swe.SIDM_YUKTESHWAR),
}

SWE_IDS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 'Mercury': swe.MERCURY,
           'Jupiter': swe.JUPITER, 'Venus': swe.VENUS, 'Saturn': swe.SATURN}

# Swiss Ephemeris keeps the sidereal mode in global state: serialise access.
_SWE_LOCK = threading.Lock()
_EPH = swe.FLG_MOSEPH | swe.FLG_SPEED

# Offline fallback for place search when the geocoder cannot be reached.
CITY_DB = {
    'chennai': (13.0827, 80.2707), 'madurai': (9.9252, 78.1198),
    'coimbatore': (11.0168, 76.9558), 'trichy': (10.7905, 78.7047),
    'tiruchirappalli': (10.7905, 78.7047), 'salem': (11.6643, 78.1460),
    'tirunelveli': (8.7139, 77.7567), 'vellore': (12.9165, 79.1325),
    'thanjavur': (10.7870, 79.1378), 'erode': (11.3410, 77.7172),
    'tiruppur': (11.1085, 77.3411), 'kochi': (9.9312, 76.2673),
    'thiruvananthapuram': (8.5241, 76.9366), 'kozhikode': (11.2588, 75.7804),
    'thrissur': (10.5276, 76.2144), 'mumbai': (19.0760, 72.8777),
    'pune': (18.5204, 73.8567), 'nagpur': (21.1458, 79.0882),
    'delhi': (28.6139, 77.2090), 'new delhi': (28.6139, 77.2090),
    'bangalore': (12.9716, 77.5946), 'bengaluru': (12.9716, 77.5946),
    'mysore': (12.2958, 76.6394), 'mysuru': (12.2958, 76.6394),
    'mangalore': (12.9141, 74.8560), 'hyderabad': (17.3850, 78.4867),
    'vijayawada': (16.5062, 80.6480), 'vizag': (17.6868, 83.2185),
    'visakhapatnam': (17.6868, 83.2185), 'kolkata': (22.5726, 88.3639),
    'ahmedabad': (23.0225, 72.5714), 'surat': (21.1702, 72.8311),
    'jaipur': (26.9124, 75.7873), 'lucknow': (26.8467, 80.9462),
    'patna': (25.5941, 85.1376), 'bhubaneswar': (20.2961, 85.8245),
    'guwahati': (26.1445, 91.7362), 'chandigarh': (30.7333, 76.7794),
    'bhopal': (23.2599, 77.4126), 'indore': (22.7196, 75.8577),
    'varanasi': (25.3176, 82.9739), 'amritsar': (31.6340, 74.8723),
    'srinagar': (34.0837, 74.7973), 'agra': (27.1767, 78.0081),
}


class InputError(ValueError):
    """Raised for bad or unresolvable birth details (HTTP 400)."""


# ── SMALL HELPERS ─────────────────────────────────────────────────────────────

def norm(d):
    return d % 360.0


def get_rasi(lon):
    return int(norm(lon) // 30) % 12


def get_nak(lon):
    # Multiply before dividing so exact boundaries (13°20', 26°40' ...) land correctly.
    return int(norm(lon) * 27 // 360) % 27


def get_pada(lon):
    return int(norm(lon) * 108 // 360) % 4 + 1


def dms(deg):
    """Degrees -> (d, m, s) with seconds rounded and carried correctly."""
    total = int(round(abs(deg) * 3600))
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return d, m, s


def fmt_dms(deg):
    d, m, s = dms(deg)
    return f"{d:02d}°{m:02d}'{s:02d}\""


def fmt_sign_dms(lon):
    """Position inside its sign, e.g. 25°58'12\"."""
    total = int(round(norm(lon) * 3600)) % (360 * 3600)
    in_sign = total % (30 * 3600)
    d, rem = divmod(in_sign, 3600)
    m, s = divmod(rem, 60)
    return f"{d:02d}°{m:02d}'{s:02d}\""


def navamsa_sign(lon):
    return int(norm(lon) * 9 // 30) % 12


def angle_diff(a, b):
    """Smallest absolute difference between two longitudes."""
    d = abs(norm(a) - norm(b))
    return min(d, 360 - d)


def in_arc(lon, start, end):
    """True when lon lies in the arc [start, end) going forward through 360."""
    lon, start, end = norm(lon), norm(start), norm(end)
    if start <= end:
        return start <= lon < end
    return lon >= start or lon < end


def midpoint(a, b):
    """Midpoint of the forward arc from a to b."""
    return norm(a + (norm(b - a)) / 2.0)


def ymd_from_years(years):
    """Split a span in years into (years, months, days) on a 360-day basis."""
    total_days = int(round(years * 360))
    y, rem = divmod(total_days, 360)
    m, d = divmod(rem, 30)
    return y, m, d


# ── TIME ZONE AND PLACE ───────────────────────────────────────────────────────

_TF = None


def timezone_for(lat, lon):
    """IANA time zone name for coordinates, or None when it cannot be found."""
    global _TF
    try:
        if _TF is None:
            from timezonefinder import TimezoneFinder
            _TF = TimezoneFinder()
        return _TF.timezone_at(lat=lat, lng=lon)
    except Exception:
        # Library missing or failed: India is a single zone, so answer for it.
        if 6.0 <= lat <= 37.5 and 68.0 <= lon <= 97.5:
            return 'Asia/Kolkata'
        return None


def geocode(query, limit=5):
    """
    Search for a place. Returns a list of
    {name, lat, lon, tz} candidates, best first. Uses OpenStreetMap Nominatim,
    falling back to the small built-in city list when it cannot be reached.
    """
    query = (query or '').strip()
    if not query:
        return []
    out = []
    try:
        import requests
        resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': query, 'format': 'json', 'limit': limit, 'accept-language': 'en'},
            headers={'User-Agent': 'HoroscopeGen/3.0 (horoscopegen.in)'},
            timeout=6,
        )
        if resp.status_code == 200:
            for r in resp.json():
                lat, lon = float(r['lat']), float(r['lon'])
                out.append({'name': r.get('display_name', query), 'lat': round(lat, 4),
                            'lon': round(lon, 4), 'tz': timezone_for(lat, lon)})
    except Exception:
        out = []
    if not out:
        key = ''.join(c for c in query.lower().split(',')[0] if c.isalpha() or c == ' ').strip()
        if key in CITY_DB:
            lat, lon = CITY_DB[key]
            out.append({'name': query, 'lat': lat, 'lon': lon, 'tz': timezone_for(lat, lon)})
    return out


def resolve_place(pob, lat=None, lon=None):
    """Coordinates for the birth place. Never guesses: raises InputError instead."""
    if lat is not None and lon is not None:
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise InputError('Latitude must be between -90 and 90 and longitude between -180 and 180.')
        return lat, lon, pob
    hits = geocode(pob, limit=1)
    if not hits:
        raise InputError(f'Could not find the place "{pob}". Search for it and pick a result, '
                         'or enter the latitude and longitude.')
    return hits[0]['lat'], hits[0]['lon'], hits[0]['name']


def resolve_utc_offset(local_dt, lat, lon, tz_name=None, utc_offset=None):
    """
    UTC offset (hours) in force at the birth moment.
    Priority: explicit numeric offset > named time zone > zone found from the
    coordinates. Named zones use the historical rules in the tz database.
    """
    if utc_offset not in (None, ''):
        off = float(utc_offset)
        if not -14 <= off <= 14:
            raise InputError('UTC offset must be between -14 and +14 hours.')
        return off, 'Manual offset'
    name = tz_name or timezone_for(lat, lon)
    if name and ZoneInfo is not None:
        try:
            aware = local_dt.replace(tzinfo=ZoneInfo(name))
            return aware.utcoffset().total_seconds() / 3600.0, name
        except Exception:
            pass
    raise InputError('Could not determine the time zone for this place. Enter the UTC offset.')


def fmt_offset(hours):
    sign = '+' if hours >= 0 else '-'
    total = int(round(abs(hours) * 3600))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"UTC{sign}{h:02d}:{m:02d}" + (f":{s:02d}" if s else '')


def julian_day(ut_dt):
    h = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0 + ut_dt.microsecond / 3.6e9
    return swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, h)


def jd_to_local(jd, offset_hours):
    y, m, d, h = swe.revjul(jd)
    base = datetime(y, m, d) + timedelta(hours=h)
    return base + timedelta(hours=offset_hours)


# ── POSITIONS ─────────────────────────────────────────────────────────────────

def _positions(jd, lat, lon, sid_mode, node='mean', hsys=b'P'):
    """Sidereal longitudes, speeds, cusps and angles for one ayanamsha."""
    with _SWE_LOCK:
        swe.set_sid_mode(sid_mode)
        ayan = swe.get_ayanamsa_ut(jd)
        flags = _EPH | swe.FLG_SIDEREAL
        pts = {}
        for name, pid in SWE_IDS.items():
            xx = swe.calc_ut(jd, pid, flags)[0]
            pts[name] = (norm(xx[0]), xx[3])
        node_id = swe.TRUE_NODE if node == 'true' else swe.MEAN_NODE
        xx = swe.calc_ut(jd, node_id, flags)[0]
        pts['Rahu'] = (norm(xx[0]), xx[3])
        pts['Ketu'] = (norm(xx[0] + 180), xx[3])
        used = hsys
        try:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, hsys, swe.FLG_SIDEREAL)
        except Exception:
            # Placidus is undefined near the poles: fall back to Porphyry.
            used = b'O'
            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', swe.FLG_SIDEREAL)
        porph, _ = swe.houses_ex(jd, lat, lon, b'O', swe.FLG_SIDEREAL)
    return {'ayan': ayan, 'pts': pts, 'cusps': [norm(c) for c in cusps[:12]],
            'porph': [norm(c) for c in porph[:12]], 'asc': norm(ascmc[0]),
            'mc': norm(ascmc[1]), 'hsys': used}


def dignity_of(planet, sign):
    if planet not in EXALT_SIGN:
        return ''
    if sign == EXALT_SIGN[planet]:
        return 'Exalted'
    if sign == (EXALT_SIGN[planet] + 6) % 12:
        return 'Debilitated'
    if sign in OWN_SIGNS[planet]:
        return 'Own sign'
    return ''


def is_combust(planet, lon, speed, sun_lon):
    if planet not in COMBUST_ORB:
        return False
    direct, retro = COMBUST_ORB[planet]
    return angle_diff(lon, sun_lon) <= (retro if speed < 0 else direct)


def kp_lords(lon):
    """(sign lord, star lord, sub lord, sub-sub lord) for a longitude."""
    lon = norm(lon)
    star = NAK_LORDS[get_nak(lon)]
    pos = lon % NAK_SIZE
    start = DASA_ORDER.index(star)

    def split(position, span, first_idx):
        acc = 0.0
        for i in range(9):
            lord = DASA_ORDER[(first_idx + i) % 9]
            width = span * DASA_YRS[lord] / 120.0
            if position < acc + width or i == 8:
                return lord, position - acc, width
            acc += width

    sub, pos_in_sub, sub_width = split(pos, NAK_SIZE, start)
    subsub, _, _ = split(pos_in_sub, sub_width, DASA_ORDER.index(sub))
    return SIGN_LORDS[get_rasi(lon)], star, sub, subsub


def _point(name, lon, speed=0.0):
    sign = get_rasi(lon)
    nak = get_nak(lon)
    sign_lord, star_lord, sub_lord, subsub_lord = kp_lords(lon)
    return {
        'name': name, 'lon': round(lon, 6), 'sign': sign, 'deg': round(norm(lon) % 30, 6),
        'dms': fmt_sign_dms(lon), 'nak': nak, 'pada': get_pada(lon),
        'sign_lord': sign_lord, 'star_lord': star_lord,
        'sub_lord': sub_lord, 'subsub_lord': subsub_lord,
        'retro': bool(speed < 0) and name not in ('Rahu', 'Ketu', 'Lagna'),
        'speed': round(speed, 6),
    }


def house_from_cusps(lon, cusps):
    for i in range(12):
        if in_arc(lon, cusps[i], cusps[(i + 1) % 12]):
            return i + 1
    return 1


# ── VIMSHOTTARI ───────────────────────────────────────────────────────────────

def vimshottari(moon_lon, birth_dt, now=None, levels=3):
    """
    Vimshottari dasa tree from the Moon's longitude.
    Periods that ended before birth are dropped; the one running at birth is
    clipped to start at birth (so the first dasa lists only the bhuktis left).
    """
    now = now or datetime.now()
    nak = get_nak(moon_lon)
    lord = NAK_LORDS[nak]
    elapsed_frac = (norm(moon_lon) % NAK_SIZE) / NAK_SIZE
    balance_years = DASA_YRS[lord] * (1 - elapsed_frac)
    cycle_start = birth_dt - timedelta(days=DASA_YRS[lord] * elapsed_frac * YEAR_DAYS)

    def children(parent_lord, start, span_years, depth):
        rows, cur = [], start
        first = DASA_ORDER.index(parent_lord)
        for i in range(9):
            sub = DASA_ORDER[(first + i) % 9]
            yrs = span_years * DASA_YRS[sub] / 120.0
            end = cur + timedelta(days=yrs * YEAR_DAYS)
            if end > birth_dt:
                row = {'lord': sub, 'start': max(cur, birth_dt), 'end': end,
                       'years': yrs, 'current': max(cur, birth_dt) <= now < end}
                if depth > 1:
                    row['sub'] = children(sub, cur, yrs, depth - 1)
                rows.append(row)
            cur = end
        return rows

    dasas, cur = [], cycle_start
    first = DASA_ORDER.index(lord)
    for i in range(9):
        d_lord = DASA_ORDER[(first + i) % 9]
        yrs = DASA_YRS[d_lord]
        end = cur + timedelta(days=yrs * YEAR_DAYS)
        row = {'lord': d_lord, 'start': max(cur, birth_dt), 'end': end, 'years': yrs,
               'current': max(cur, birth_dt) <= now < end}
        if levels > 1:
            row['sub'] = children(d_lord, cur, yrs, levels - 1)
        dasas.append(row)
        cur = end

    current = {}
    cd = next((d for d in dasas if d['current']), None)
    if cd:
        current['dasa'] = {'lord': cd['lord'], 'start': cd['start'], 'end': cd['end']}
        cb = next((b for b in cd.get('sub', []) if b['current']), None)
        if cb:
            current['bhukti'] = {'lord': cb['lord'], 'start': cb['start'], 'end': cb['end']}
            ca = next((a for a in cb.get('sub', []) if a['current']), None)
            if ca:
                current['antara'] = {'lord': ca['lord'], 'start': ca['start'], 'end': ca['end']}

    y, m, d = ymd_from_years(balance_years)
    return {
        'birth_star_lord': lord,
        'balance': {'lord': lord, 'years': round(balance_years, 4), 'y': y, 'm': m, 'd': d},
        'dasas': dasas,
        'current': current,
    }


# ── PANCHANGAM ────────────────────────────────────────────────────────────────

def _sun_event(jd_start, lat, lon, rise=True):
    flag = swe.CALC_RISE if rise else swe.CALC_SET
    try:
        with _SWE_LOCK:
            res, tret = swe.rise_trans(jd_start, swe.SUN, flag, (lon, lat, 0.0), 1013.25, 15.0, swe.FLG_MOSEPH)
        return tret[0] if res == 0 else None
    except Exception:
        return None


def panchangam(sun_lon, moon_lon, local_dt, offset_hours, lat, lon):
    elong = norm(moon_lon - sun_lon)
    t = int(elong // 12)                       # 0..29
    paksha = 'Shukla' if t < 15 else 'Krishna'
    if t == 14:
        tithi = 'Purnima'
    elif t == 29:
        tithi = 'Amavasya'
    else:
        tithi = TITHIS[t % 15]

    k = int(elong // 6)                        # 0..59
    if k == 0:
        karana = 'Kimstughna'
    elif k >= 57:
        karana = ['Shakuni', 'Chatushpada', 'Naga'][k - 57]
    else:
        karana = KARANAS_MOVABLE[(k - 1) % 7]

    yoga = YOGAS[int(norm(sun_lon + moon_lon) // NAK_SIZE) % 27]

    # Sunrise and sunset on the civil date of birth (visible upper limb).
    midnight_local = datetime(local_dt.year, local_dt.month, local_dt.day)
    jd0 = julian_day(midnight_local - timedelta(hours=offset_hours))
    jd_rise = _sun_event(jd0, lat, lon, True)
    jd_set = _sun_event(jd_rise if jd_rise else jd0, lat, lon, False)
    sunrise = jd_to_local(jd_rise, offset_hours) if jd_rise else None
    sunset = jd_to_local(jd_set, offset_hours) if jd_set else None

    # The Vedic day runs sunrise to sunrise.
    vara_date = local_dt.date()
    if sunrise and local_dt < sunrise:
        vara_date = vara_date - timedelta(days=1)
    wd = vara_date.weekday()

    return {
        'tithi': tithi, 'tithi_num': t + 1, 'paksha': paksha,
        'vara': WEEKDAYS[wd], 'vara_lord': WEEKDAY_LORDS[wd],
        'nak': get_nak(moon_lon), 'pada': get_pada(moon_lon),
        'yoga': yoga, 'karana': karana,
        'sunrise': sunrise, 'sunset': sunset,
    }


# ── SYSTEM BUILDERS ───────────────────────────────────────────────────────────

def _build_vedic(pos, local_dt, offset_hours, lat, lon, now):
    sun_lon = pos['pts']['Sun'][0]
    lagna = _point('Lagna', pos['asc'])
    lagna_sign = lagna['sign']

    # Sripati bhava: Porphyry cusps are the bhava centres (madhya);
    # each bhava starts midway between its centre and the previous one.
    madhya = pos['porph']
    starts = [midpoint(madhya[(i - 1) % 12], madhya[i]) for i in range(12)]
    bhavas = [{'house': i + 1, 'start': round(starts[i], 6), 'madhya': round(madhya[i], 6),
               'end': round(starts[(i + 1) % 12], 6),
               'start_sign': get_rasi(starts[i]), 'start_dms': fmt_sign_dms(starts[i]),
               'madhya_sign': get_rasi(madhya[i]), 'madhya_dms': fmt_sign_dms(madhya[i])}
              for i in range(12)]

    def enrich(p, lon_, speed):
        p['house'] = ((p['sign'] - lagna_sign) % 12) + 1
        p['bhava'] = house_from_cusps(lon_, starts)
        p['navamsa'] = navamsa_sign(lon_)
        p['dignity'] = dignity_of(p['name'], p['sign'])
        p['combust'] = is_combust(p['name'], lon_, speed, sun_lon)
        return p

    lagna = enrich(lagna, pos['asc'], 0.0)
    planets = [lagna]
    for name in PLANETS:
        lon_, speed = pos['pts'][name]
        planets.append(enrich(_point(name, lon_, speed), lon_, speed))

    moon = next(p for p in planets if p['name'] == 'Moon')
    return {
        'ayanamsha': round(pos['ayan'], 6),
        'ayanamsha_dms': fmt_dms(pos['ayan']),
        'planets': planets,
        'lagna_sign': lagna_sign,
        'moon_sign': moon['sign'], 'moon_nak': moon['nak'], 'moon_pada': moon['pada'],
        'bhavas': bhavas,
        'panchangam': panchangam(sun_lon, pos['pts']['Moon'][0], local_dt, offset_hours, lat, lon),
        'dasa': vimshottari(pos['pts']['Moon'][0], local_dt, now, levels=3),
    }


def _build_kp(pos, local_dt, vara_lord, now):
    cusps = pos['cusps']
    cusp_rows = []
    for i, c in enumerate(cusps):
        row = _point(f'Cusp {i + 1}', c)
        row['house'] = i + 1
        cusp_rows.append(row)

    planets = []
    for name in PLANETS:
        lon_, speed = pos['pts'][name]
        p = _point(name, lon_, speed)
        p['house'] = house_from_cusps(lon_, cusps)
        planets.append(p)
    by_name = {p['name']: p for p in planets}

    occupants = {h: [p['name'] for p in planets if p['house'] == h] for h in range(1, 13)}
    owned = {pl: [r['house'] for r in cusp_rows if r['sign_lord'] == pl] for pl in PLANETS}

    # Planet significators (4 levels, strongest first)
    planet_sig = []
    for p in planets:
        star = by_name[p['star_lord']]
        l1, l2 = [star['house']], [p['house']]
        l3, l4 = owned[p['star_lord']], owned[p['name']]
        allh = sorted(set(l1 + l2 + l3 + l4))
        planet_sig.append({'planet': p['name'], 'star_lord': p['star_lord'], 'sub_lord': p['sub_lord'],
                           'l1': l1, 'l2': l2, 'l3': l3, 'l4': l4, 'all': allh})

    # House significators (A strongest ... D weakest)
    house_sig = []
    for h in range(1, 13):
        occ = occupants[h]
        owner = cusp_rows[h - 1]['sign_lord']
        a = [p['name'] for p in planets if p['star_lord'] in occ]
        c = [p['name'] for p in planets if p['star_lord'] == owner]
        house_sig.append({'house': h, 'a': a, 'b': occ, 'c': c, 'd': [owner]})

    # Rahu and Ketu act for their sign lord and for planets in the same sign.
    agents = []
    for node_name in ('Rahu', 'Ketu'):
        n = by_name[node_name]
        conj = [p['name'] for p in planets if p['sign'] == n['sign'] and p['name'] != node_name]
        agents.append({'node': node_name, 'sign_lord': n['sign_lord'], 'star_lord': n['star_lord'],
                       'conjoined': conj})

    asc = cusp_rows[0]
    moon = by_name['Moon']
    ruling = {
        'day_lord': vara_lord,
        'moon_sign_lord': moon['sign_lord'], 'moon_star_lord': moon['star_lord'],
        'moon_sub_lord': moon['sub_lord'],
        'lagna_sign_lord': asc['sign_lord'], 'lagna_star_lord': asc['star_lord'],
        'lagna_sub_lord': asc['sub_lord'],
    }

    return {
        'ayanamsha': round(pos['ayan'], 6), 'ayanamsha_dms': fmt_dms(pos['ayan']),
        'house_system': 'Placidus' if pos['hsys'] == b'P' else 'Porphyry',
        'cusps': cusp_rows, 'planets': planets,
        'lagna_sign': asc['sign'],
        'planet_significators': planet_sig, 'house_significators': house_sig,
        'node_agents': agents, 'ruling_planets': ruling,
        'dasa': vimshottari(moon['lon'], local_dt, now, levels=2),
    }


def _build_alp(lagna_lon, local_dt, now, years=120):
    """Akshaya Lagna: birth lagna advancing 3 degrees a year."""
    def at(dt):
        yrs = (dt - local_dt).total_seconds() / 86400.0 / YEAR_DAYS
        return norm(lagna_lon + ALP_DEG_PER_YEAR * yrs)

    age_years = max((now - local_dt).total_seconds() / 86400.0 / YEAR_DAYS, 0.0)
    cur = _point('ALP Lagna', at(now) if now > local_dt else lagna_lon)

    def when(deg_travelled):
        return local_dt + timedelta(days=deg_travelled / ALP_DEG_PER_YEAR * YEAR_DAYS)

    total = ALP_DEG_PER_YEAR * years
    # Pada-level periods
    padas, travelled = [], 0.0
    to_boundary = PADA_SIZE - (norm(lagna_lon) % PADA_SIZE)
    step = to_boundary if to_boundary > 1e-9 else PADA_SIZE
    while travelled < total - 1e-9:
        span = min(step, total - travelled)
        lon_mid = norm(lagna_lon + travelled + span / 2.0)
        start, end = when(travelled), when(travelled + span)
        sign = get_rasi(lon_mid)
        nak = get_nak(lon_mid)
        padas.append({'start': start, 'end': end, 'sign': sign, 'nak': nak, 'pada': get_pada(lon_mid),
                      'sign_lord': SIGN_LORDS[sign], 'star_lord': NAK_LORDS[nak],
                      'age_from': round(travelled / ALP_DEG_PER_YEAR, 2),
                      'age_to': round((travelled + span) / ALP_DEG_PER_YEAR, 2),
                      'current': start <= now < end})
        travelled += span
        step = PADA_SIZE

    # Sign-level periods (10 years each)
    signs, travelled = [], 0.0
    to_boundary = 30.0 - (norm(lagna_lon) % 30.0)
    step = to_boundary if to_boundary > 1e-9 else 30.0
    while travelled < total - 1e-9:
        span = min(step, total - travelled)
        lon_mid = norm(lagna_lon + travelled + span / 2.0)
        start, end = when(travelled), when(travelled + span)
        sign = get_rasi(lon_mid)
        signs.append({'start': start, 'end': end, 'sign': sign, 'sign_lord': SIGN_LORDS[sign],
                      'age_from': round(travelled / ALP_DEG_PER_YEAR, 2),
                      'age_to': round((travelled + span) / ALP_DEG_PER_YEAR, 2),
                      'current': start <= now < end})
        travelled += span
        step = 30.0

    return {
        'birth_lagna_lon': round(lagna_lon, 6),
        'as_of': now, 'age_years': round(age_years, 2),
        'lagna': cur, 'lagna_sign': cur['sign'],
        'rate': '30° per 10 years (3° per year; one pada = 1 year 1 month 10 days)',
        'pada_periods': padas, 'sign_periods': signs,
    }


# ── MAIN ENTRY POINT ──────────────────────────────────────────────────────────

def compute(name, dob, tob, pob, lat=None, lon=None, tz=None, utc_offset=None,
            ayanamsha='lahiri', node='mean', gender='', lang='en', chart_style='south',
            now=None):
    """
    Build the complete horoscope.

    name, dob (YYYY-MM-DD), tob (HH:MM or HH:MM:SS, local clock time), pob.
    lat / lon: decimal degrees; when omitted the place name is looked up.
    tz: IANA zone name; utc_offset: hours, overrides tz when given.
    now: reference moment for "current" periods (naive local time of the
         birth zone); defaults to the present.
    """
    try:
        y, m, d = [int(x) for x in str(dob).split('-')]
        parts = [int(x) for x in str(tob).split(':')]
        hh, mm = parts[0], parts[1]
        ss = parts[2] if len(parts) > 2 else 0
        local_dt = datetime(y, m, d, hh, mm, ss)
    except Exception:
        raise InputError('Date must be YYYY-MM-DD and time HH:MM (24-hour).')

    ayanamsha = (ayanamsha or 'lahiri').lower()
    if ayanamsha not in AYANAMSHAS:
        raise InputError(f'Unknown ayanamsha "{ayanamsha}".')
    node = 'true' if str(node).lower() == 'true' else 'mean'
    chart_style = 'north' if str(chart_style).lower() == 'north' else 'south'

    lat, lon, place_resolved = resolve_place(pob, lat, lon)
    offset_hours, tz_label = resolve_utc_offset(local_dt, lat, lon, tz, utc_offset)
    ut_dt = local_dt - timedelta(hours=offset_hours)
    jd = julian_day(ut_dt)

    if now is None:
        now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=offset_hours)

    ayan_name, sid_mode = AYANAMSHAS[ayanamsha]
    pos_vedic = _positions(jd, lat, lon, sid_mode, node, b'P')
    pos_kp = _positions(jd, lat, lon, swe.SIDM_KRISHNAMURTI, node, b'P')

    vedic = _build_vedic(pos_vedic, local_dt, offset_hours, lat, lon, now)
    kp = _build_kp(pos_kp, local_dt, vedic['panchangam']['vara_lord'], now)
    alp = _build_alp(pos_vedic['asc'], local_dt, now)
    alp['planets'] = [dict(p, house=((p['sign'] - alp['lagna_sign']) % 12) + 1)
                      for p in vedic['planets'] if p['name'] != 'Lagna']

    return {
        'meta': {
            'name': name, 'gender': gender or '', 'dob': dob, 'tob': tob, 'pob': pob,
            'place_resolved': place_resolved,
            'lat': round(lat, 4), 'lon': round(lon, 4),
            'tz': tz_label, 'utc_offset': round(offset_hours, 4),
            'utc_offset_str': fmt_offset(offset_hours),
            'local_dt': local_dt, 'ut_dt': ut_dt, 'jd_ut': round(jd, 6),
            'ayanamsha_key': ayanamsha, 'ayanamsha_name': ayan_name,
            'node': node, 'lang': lang, 'chart_style': chart_style,
            'generated_at': now, 'year_days': YEAR_DAYS,
            'engine': f'Swiss Ephemeris {swe.version} (Moshier)',
        },
        'vedic': vedic,
        'kp': kp,
        'alp': alp,
    }


def to_jsonable(obj):
    """Recursively convert datetimes so the result can be sent as JSON."""
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    if isinstance(obj, date):
        return obj.isoformat()
    return obj
