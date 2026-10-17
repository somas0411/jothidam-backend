"""
app.py — HoroscopeGen backend API (Flask).

Endpoints
  GET  /health, /api/ping      health checks
  GET  /api/geocode?q=         place search -> name, latitude, longitude, time zone
  POST /api/horoscope          full horoscope as JSON (Vedic, KP, ALP, charts)
  POST /api/download/excel     Excel workbook
  POST /api/download/pdf       PDF report
  POST /api/download/json      the horoscope plus the AI block, as a JSON file
  POST /api/match              marriage matching (porutham) of two people as JSON
  POST /api/download/match/excel, /pdf   the same match as a workbook or a PDF
  /api/astrologers..., /api/bookings..., /api/admin...   astrologer consultations (booking_api.py)

The two single-horoscope downloads also take "partner" (birth details of a
partner): the workbook then gains a Marriage sheet and the PDF a Marriage
section.

All horoscope endpoints take the same JSON body and call the same
compute() function, so the page, the Excel, the PDF and the JSON file always
agree. The Excel and JSON downloads also call enrich(), which adds flat
tables of derived facts for AI readers; /api/horoscope adds them only when
the body has "ai": true.

The horoscope endpoints store nothing: birth details are used for the
calculation and discarded. The one exception is an astrologer consultation
the user books with their consent (booking_api.py): the booking, the user's
contact details, questions and birth details are kept in the database until
RETENTION_DAYS (default 90) after the appointment, then wiped (notify.py).

The API is public (the website calls it from the visitor's browser), so it is
protected by limits rather than by secrecy: a cap on the request body size and
a cap on requests per visitor (see "PROTECTION" below and the README).

Deploy (Render): build `pip install -r requirements.txt`, start `gunicorn app:app`.
"""
import ipaddress
import json
import logging
import os
import re

import swisseph as swe
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_limiter import Limiter
from limits import parse as parse_limit
from werkzeug.exceptions import HTTPException, TooManyRequests

import booking_api
import charts
import i18n
from astro_engine import AYANAMSHAS, InputError, compute, geocode, to_jsonable
from enrich import enrich
from excel_generator import generate_excel, generate_match_excel
from match_engine import match, tables as match_tables
from pdf_generator import generate_match_pdf, generate_pdf

app = Flask(__name__)
app.json.ensure_ascii = False

ALLOWED_ORIGINS = [
    'https://horoscopegen.in',
    'https://www.horoscopegen.in',
    'https://horoscopesgen.netlify.app',
    'android-app://com.jothidam.horoscopegen',
    'http://localhost:5500', 'http://127.0.0.1:5500',
    'http://localhost:8000', 'http://127.0.0.1:8000',
]
# CORS only tells browsers which websites may read the answers. It does not
# stop a script from calling the API directly; the limits below do that.
# Only the admin routes (booking_api.py) take PUT and DELETE.
CORS(app, origins=ALLOWED_ORIGINS + [o for o in os.environ.get('EXTRA_ORIGINS', '').split(',') if o],
     resources={r'/api/admin/*': {'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']},
                r'/*': {'methods': ['GET', 'POST', 'OPTIONS']}},
     expose_headers=['Content-Disposition', 'Retry-After'], max_age=600, always_send=False)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('horoscopegen')


# ── PROTECTION ────────────────────────────────────────────────────────────────

# A real request body (birth details and the optional "life" inputs) is a few
# hundred bytes. Anything larger is refused before it is read.
MAX_BODY_BYTES = 64 * 1024
app.config['MAX_CONTENT_LENGTH'] = MAX_BODY_BYTES

# Requests allowed per visitor. Several people can share one address (an
# office, a mobile network), so these are well above what one person needs.
LIMIT_DEFAULT = '120 per minute'
LIMIT_HOROSCOPE = '30 per minute; 300 per hour'
LIMIT_MATCH = '15 per minute; 150 per hour'         # one match computes two horoscopes
LIMIT_DOWNLOAD = '10 per minute; 100 per hour'      # all the downloads together
LIMIT_GEOCODE = '20 per minute; 200 per hour'
# Place look-ups go to OpenStreetMap Nominatim, which allows one request a
# second from this server in total, whoever asked.
LIMIT_NOMINATIM_ALL_VISITORS = '60 per minute'

# The header in which the hosting platform passes on the visitor's address.
# On Render, requests arrive through Cloudflare, which sets CF-Connecting-IP
# and overwrites anything the visitor sent under that name.
CLIENT_IP_HEADER = os.environ.get('CLIENT_IP_HEADER', 'CF-Connecting-IP').strip()


def _client_key():
    """
    The visitor's address, used only to count requests in memory; it is not
    logged or stored. IPv6 visitors are counted by their /64 network, because
    one connection owns a whole /64 and could otherwise change address at will.
    """
    raw = request.headers.get(CLIENT_IP_HEADER, '') if CLIENT_IP_HEADER else ''
    if not raw:
        raw = request.headers.get('X-Forwarded-For', '').split(',')[0]
    raw = raw.strip() or request.remote_addr or ''
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError:
        return 'unknown'
    if ip.version == 6:
        if ip.ipv4_mapped:
            return str(ip.ipv4_mapped)
        return str(ipaddress.ip_network((ip, 64), strict=False))
    return str(ip)


def _limits_enabled():
    """RATE_LIMIT_ENABLED=false switches the request limits off without a code change."""
    return os.environ.get('RATE_LIMIT_ENABLED', 'true').strip().lower() not in ('0', 'false', 'no', 'off')


app.config['RATELIMIT_ENABLED'] = _limits_enabled()
app.config['RATELIMIT_HEADERS_ENABLED'] = True
# Counters are kept in this process's memory: nothing to set up, and correct
# while gunicorn runs one worker (see gunicorn.conf.py). With more workers
# each one would count separately.
limiter = Limiter(key_func=_client_key, app=app, default_limits=[LIMIT_DEFAULT],
                  storage_uri='memory://', strategy='fixed-window')


@limiter.request_filter
def _never_limit_preflight():
    """A browser's CORS preflight (OPTIONS) is not a request for work."""
    return request.method == 'OPTIONS'


download_limit = limiter.shared_limit(LIMIT_DOWNLOAD, scope='download')

_NOMINATIM_LIMIT = parse_limit(LIMIT_NOMINATIM_ALL_VISITORS)


def _spend_nominatim_budget():
    """
    Call just before a place look-up. It is counted here, after the visitor's
    own limit has let the request through, so that requests already refused
    cannot use up the budget everyone shares.
    """
    if limiter.enabled and not limiter.limiter.hit(_NOMINATIM_LIMIT, 'nominatim', 'all-visitors'):
        raise TooManyRequests(retry_after=60)


@app.errorhandler(HTTPException)
def _http_error(e):
    """Every error leaves as {"error": "..."}, the shape the website already shows."""
    messages = {
        404: 'Not found.',
        405: 'This address does not accept that kind of request.',
        413: 'The request is too large.',
        429: 'Too many requests. Please wait a minute and try again.',
    }
    resp = jsonify({'error': messages.get(e.code, e.name)})
    resp.status_code = e.code or 500
    for name, value in (e.get_headers() or []):
        if name.lower() not in ('content-type', 'content-length'):
            resp.headers[name] = value
    return resp


@app.after_request
def _response_headers(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    if request.method == 'POST':
        # Answers hold birth details: no proxy or browser cache should keep them.
        resp.headers.setdefault('Cache-Control', 'no-store')
    return resp


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _num(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise InputError(f'"{value}" is not a number.')


def _body():
    """The JSON body as a dict. Raises InputError when it is some other JSON value."""
    body = request.get_json(force=True, silent=True)
    if body is None:
        return {}
    if not isinstance(body, dict):
        raise InputError('The request body must be a JSON object.')
    return body


def _lang(body):
    lang = body.get('lang', 'en')
    return lang if lang in i18n.LANGS else 'en'


def _compute(details, settings, who=None):
    """
    Run the engine for one person. details holds the birth details; settings
    holds what is common to a request (ayanamsha, node, language, chart
    style). For a single horoscope the two are the same JSON body. who names
    the person in a matching request ('boy' or 'girl'), where the name may be
    left out. Raises InputError on bad input.
    """
    name = str(details.get('name', '')).strip()
    dob = str(details.get('dob', '')).strip()
    tob = str(details.get('tob', '')).strip()
    pob = str(details.get('pob', '')).strip()
    if who:
        if not all([dob, tob, pob]):
            raise InputError(f'Date, time and place of birth are required for the {who}.')
        name = name or who.capitalize()
    elif not all([name, dob, tob, pob]):
        raise InputError('Name, date, time and place of birth are required.')
    lat, lon = _num(details.get('lat')), _num(details.get('lon'))
    if lat is None or lon is None:
        _spend_nominatim_budget()       # compute() will look the place up
    gender = {'boy': 'male', 'girl': 'female'}.get(who) or str(details.get('gender', ''))[:20]
    return compute(
        name=name[:80], dob=dob, tob=tob, pob=pob[:120],
        lat=lat, lon=lon,
        tz=(details.get('tz') or None), utc_offset=_num(details.get('utcOffset')),
        ayanamsha=str(settings.get('ayanamsha') or 'lahiri'), node=settings.get('node', 'mean'),
        gender=gender, lang=_lang(settings),
        chart_style=settings.get('chartStyle', 'south'),
    )


def _compute_from_request():
    """Read the JSON body and run the engine. Raises InputError on bad input."""
    body = _body()
    return _compute(body, body), _lang(body)


def _match_options(body):
    return {'kuja_houses': body.get('kujaHouses'), 'sandhi_months': body.get('sandhiMonths')}


def _match_from_request():
    """
    Read a matching request and run the two people through the engine.

    Body: {"boy": {...}, "girl": {...}, "mode": "full" | "star"} plus the
    settings of a horoscope request (ayanamsha, node, lang, chartStyle).
    "full": each person holds birth details as for /api/horoscope (the name
    may be left out). "star": each holds {"nakshatra", "pada", "rasi"}.
    "kujaHouses": "south" (the default), "north" or "all".
    "sandhiMonths": 1 to 36 (default 12), for the dasa sandhi row.
    Returns (match result, the two compute() results or None, language).
    """
    body = _body()
    mode = str(body.get('mode') or 'full').strip().lower()
    if mode not in ('full', 'star'):
        raise InputError('"mode" must be "full" or "star".')
    people = {}
    for role in ('boy', 'girl'):
        details = body.get(role)
        if not isinstance(details, dict) or not details:
            raise InputError(f'The details of the {role} are required.')
        people[role] = details if mode == 'star' else _compute(details, body, role)
    result = match(people['boy'], people['girl'], _match_options(body))
    return result, (people if mode == 'full' else None), _lang(body)


def _partner_match(res):
    """
    For the single-horoscope downloads: when the body holds "partner" (the
    birth details of a partner), the match of the two and both compute()
    results; otherwise (None, None). The person's own "gender" decides who is
    the boy and who is the girl, so it must then be male or female.
    """
    body = _body()
    partner = body.get('partner')
    if partner in (None, '', {}):
        return None, None
    if not isinstance(partner, dict):
        raise InputError('"partner" must hold the birth details of the partner.')
    gender = str(body.get('gender', '')).strip().lower()
    if gender not in ('male', 'female'):
        raise InputError('Set "gender" to male or female to add a marriage match with a partner.')
    own, other = ('boy', 'girl') if gender == 'male' else ('girl', 'boy')
    people = {own: res, other: _compute(partner, body, other)}
    return match(people['boy'], people['girl'], _match_options(body)), people


def _ai_mode():
    """
    What the request body asks for under "ai": 'full' for true, 'brief' for
    "brief" (the short AI_Brief table only), None otherwise.
    """
    body = _body()
    text = str(body.get('ai', '')).strip().lower()
    if body.get('ai') is True or text == 'true':
        return 'full'
    return 'brief' if text == 'brief' else None


def _wants_ai():
    """True when the request body asks for the full AI block ("ai": true)."""
    return _ai_mode() == 'full'


def _extras():
    """
    Optional inputs for the AI block, read from the request body:
    "tobUncertaintyMin" (how many minutes the birth time may be off) and
    "life" (facts and past events only the user knows). enrich() checks them
    and raises InputError on a bad value. Nothing is stored.
    """
    body = _body()
    given = body.get('lat') not in (None, '') and body.get('lon') not in (None, '')
    return {'tob_uncertainty_min': body.get('tobUncertaintyMin'),
            'coordinates_source': 'entered' if given else 'looked up',
            'life': body.get('life')}


def _brief_block(res):
    """The short form for an assistant that cannot load the full tables: meta and AI_Brief."""
    ai = enrich(res, extras=_extras())
    return {'meta': to_jsonable(res['meta']),
            'ai': {'schema': ai['schema'], 'report_datetime_local': to_jsonable(ai['report_datetime_local']),
                   'utc_offset_hours': ai['utc_offset_hours'], 'columns': ai['columns']['AI_Brief'],
                   'brief': to_jsonable(ai['tables']['AI_Brief'])}}


def _filename(name, ext):
    safe = re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_') or 'Report'
    return f'HoroscopeGen_{safe}.{ext}'


def _file_response(data, filename, mime):
    resp = make_response(data)
    resp.headers['Content-Type'] = mime
    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    resp.headers['Content-Length'] = len(data)
    return resp


def _guard(fn):
    """Uniform error handling: 400 for bad input, 500 otherwise."""
    try:
        return fn()
    except InputError as e:
        return jsonify({'error': str(e)}), 400
    except HTTPException:
        raise               # e.g. 413 for an oversized body: answered by _http_error
    except (OverflowError, swe.Error):
        # A date beyond what Python's calendar or the ephemeris covers.
        log.warning('Date out of range in %s', request.path)
        return jsonify({'error': 'That date is outside the range this service can calculate.'}), 400
    except Exception:
        log.exception('Unhandled error in %s', request.path)
        return jsonify({'error': 'The report could not be generated. Please try again.'}), 500


def _legacy_fields(res):
    """
    Top-level fields in the shape the previous website expected, so a cached
    copy of the old page keeps working until it refreshes. Safe to remove once
    the new website has been live for a while.
    """
    v = res['vedic']
    cur = v['dasa']['current']
    iso = lambda d: d.strftime('%Y-%m-%d')
    rows = [{'dasa': d['lord'], 'bhukti': b['lord'], 'start': iso(b['start']), 'end': iso(b['end']),
             'status': 'current' if b['current'] else 'upcoming'}
            for d in v['dasa']['dasas'] for b in d['sub']]
    first = v['dasa']['dasas'][0]
    cd = cur.get('dasa') or {'lord': first['lord'], 'start': first['start'], 'end': first['end']}
    cb = cur.get('bhukti') or dict(first['sub'][0])
    return {
        'planets': [{'planet': p['name'], 'longitude': p['lon']} for p in v['planets']],
        'lagnaRasi': v['lagna_sign'], 'moonRasi': v['moon_sign'], 'nakNum': v['moon_nak'],
        'nakPada': v['moon_pada'], 'nakLord': v['dasa']['birth_star_lord'],
        'curDasa': {'dasa': cd['lord'], 'end': iso(cd['end'])},
        'curBhukti': {'bhukti': cb['lord'], 'start': iso(cb['start']), 'end': iso(cb['end'])},
        'dasas': rows, 'yogas': [],
    }


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/health')
@limiter.exempt
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/ping')
@limiter.exempt
def ping():
    return jsonify({'status': 'ok', 'service': 'HoroscopeGen API', 'version': '3.0'})


@app.route('/api/options')
def options():
    return jsonify({'ayanamshas': {k: v[0] for k, v in AYANAMSHAS.items()},
                    'languages': i18n.LANGS, 'chartStyles': ['south', 'north'],
                    'nodes': ['mean', 'true']})


@app.route('/api/geocode')
@limiter.limit(LIMIT_GEOCODE)
def geocode_route():
    """Place search. Called only when the user presses Search (no type-ahead)."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'results': []})
    _spend_nominatim_budget()
    return _guard(lambda: jsonify({'results': geocode(q[:120], limit=5)}))


@app.route('/api/horoscope', methods=['POST'])
@limiter.limit(LIMIT_HOROSCOPE)
def horoscope():
    def run():
        res, lang = _compute_from_request()
        if _ai_mode() == 'brief':
            return jsonify(_brief_block(res))
        out = to_jsonable(res)
        out['charts'] = charts.build_specs(res, lang)
        out['varga_charts'] = charts.build_varga_specs(res, lang)
        keys, rows = charts.varga_table(res, lang)
        out['varga_table'] = {'keys': keys, 'rows': rows}
        out['names'] = i18n.bundle(lang)
        out.update(_legacy_fields(res))
        if _wants_ai():
            out['ai'] = to_jsonable(enrich(res, extras=_extras()))
        return jsonify(out)
    return _guard(run)


@app.route('/api/match', methods=['POST'])
@limiter.limit(LIMIT_MATCH)
def match_route():
    """Marriage matching of two people. Nothing is stored."""
    def run():
        result, people, lang = _match_from_request()
        out = to_jsonable(result)
        if people:
            # The two rasi and navamsa charts, for the page to draw side by side.
            out['charts'] = {role: {k: v for k, v in charts.build_specs(res, lang).items() if k in ('d1', 'd9')}
                             for role, res in people.items()}
        if _wants_ai():
            out['ai'] = to_jsonable(match_tables(result))
        return jsonify(out)
    return _guard(run)


def _match_filename(result, ext):
    people = result['persons']
    return _filename(f"Match_{people['boy']['name']}_{people['girl']['name']}", ext)


@app.route('/api/download/match/excel', methods=['POST'])
@download_limit
def download_match_excel():
    """The match as a workbook: the Marriage sheet, then the AI_Match sheets."""
    def run():
        result, people, lang = _match_from_request()
        return _file_response(generate_match_excel(result, people, lang), _match_filename(result, 'xlsx'),
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return _guard(run)


@app.route('/api/download/match/pdf', methods=['POST'])
@download_limit
def download_match_pdf():
    """The match as a PDF: the Marriage section alone."""
    def run():
        result, people, lang = _match_from_request()
        return _file_response(generate_match_pdf(result, people, lang), _match_filename(result, 'pdf'),
                              'application/pdf')
    return _guard(run)


@app.route('/api/download/excel', methods=['POST'])
@download_limit
def download_excel():
    def run():
        res, lang = _compute_from_request()
        result, people = _partner_match(res)
        return _file_response(generate_excel(res, lang, ai=enrich(res, extras=_extras()), match=result,
                                             people=people),
                              _filename(res['meta']['name'], 'xlsx'),
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return _guard(run)


@app.route('/api/download/pdf', methods=['POST'])
@download_limit
def download_pdf():
    def run():
        res, lang = _compute_from_request()
        result, people = _partner_match(res)
        return _file_response(generate_pdf(res, lang, match=result, people=people),
                              _filename(res['meta']['name'], 'pdf'), 'application/pdf')
    return _guard(run)


@app.route('/api/download/json', methods=['POST'])
@download_limit
def download_json():
    """
    The full result of compute() plus the AI block, for giving to an AI assistant.
    With "ai": "brief" the file holds meta and the short AI_Brief table only.
    """
    def run():
        res, _ = _compute_from_request()
        if _ai_mode() == 'brief':
            out = _brief_block(res)
        else:
            out = to_jsonable(res)
            out['ai'] = to_jsonable(enrich(res, extras=_extras()))
        data = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        return _file_response(data, _filename(res['meta']['name'], 'json'), 'application/json; charset=utf-8')
    return _guard(run)


# ── ASTROLOGER CONSULTATIONS ──────────────────────────────────────────────────

def _booking_compute(birth, lang):
    """compute() for the birth details stored with a booking (they always hold coordinates)."""
    return _compute(birth, dict(birth, lang=lang))


def _booking_pdf(birth, lang):
    """The same PDF as /api/download/pdf, for a booking's stored birth details."""
    return generate_pdf(_booking_compute(birth, lang), lang)


booking_api.register(app, limiter, check_birth=_booking_compute, render_pdf=_booking_pdf)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
