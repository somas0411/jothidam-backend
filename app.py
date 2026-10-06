"""
app.py — HoroscopeGen backend API (Flask).

Endpoints
  GET  /health, /api/ping      health checks
  GET  /api/geocode?q=         place search -> name, latitude, longitude, time zone
  POST /api/horoscope          full horoscope as JSON (Vedic, KP, ALP, charts)
  POST /api/download/excel     Excel workbook
  POST /api/download/pdf       PDF report

All three horoscope endpoints take the same JSON body and call the same
compute() function, so the page, the Excel and the PDF always agree.

Nothing is stored: birth details are used for the calculation and discarded.

Deploy (Render): build `pip install -r requirements.txt`, start `gunicorn app:app`.
"""
import logging
import os
import re

from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

import charts
import i18n
from astro_engine import AYANAMSHAS, InputError, compute, geocode, to_jsonable
from excel_generator import generate_excel
from pdf_generator import generate_pdf

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
CORS(app, origins=ALLOWED_ORIGINS + [o for o in os.environ.get('EXTRA_ORIGINS', '').split(',') if o],
     expose_headers=['Content-Disposition'])

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('horoscopegen')


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _num(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise InputError(f'"{value}" is not a number.')


def _compute_from_request():
    """Read the JSON body and run the engine. Raises InputError on bad input."""
    body = request.get_json(force=True, silent=True) or {}
    name = str(body.get('name', '')).strip()
    dob = str(body.get('dob', '')).strip()
    tob = str(body.get('tob', '')).strip()
    pob = str(body.get('pob', '')).strip()
    if not all([name, dob, tob, pob]):
        raise InputError('Name, date, time and place of birth are required.')
    lang = body.get('lang', 'en')
    if lang not in i18n.LANGS:
        lang = 'en'
    res = compute(
        name=name[:80], dob=dob, tob=tob, pob=pob[:120],
        lat=_num(body.get('lat')), lon=_num(body.get('lon')),
        tz=(body.get('tz') or None), utc_offset=_num(body.get('utcOffset')),
        ayanamsha=body.get('ayanamsha', 'lahiri'), node=body.get('node', 'mean'),
        gender=str(body.get('gender', ''))[:20], lang=lang,
        chart_style=body.get('chartStyle', 'south'),
    )
    return res, lang


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
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/ping')
def ping():
    return jsonify({'status': 'ok', 'service': 'HoroscopeGen API', 'version': '3.0'})


@app.route('/api/options')
def options():
    return jsonify({'ayanamshas': {k: v[0] for k, v in AYANAMSHAS.items()},
                    'languages': i18n.LANGS, 'chartStyles': ['south', 'north'],
                    'nodes': ['mean', 'true']})


@app.route('/api/geocode')
def geocode_route():
    """Place search. Called only when the user presses Search (no type-ahead)."""
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'results': []})
    return _guard(lambda: jsonify({'results': geocode(q[:120], limit=5)}))


@app.route('/api/horoscope', methods=['POST'])
def horoscope():
    def run():
        res, lang = _compute_from_request()
        out = to_jsonable(res)
        out['charts'] = charts.build_specs(res, lang)
        out['varga_charts'] = charts.build_varga_specs(res, lang)
        keys, rows = charts.varga_table(res, lang)
        out['varga_table'] = {'keys': keys, 'rows': rows}
        out['names'] = i18n.bundle(lang)
        out.update(_legacy_fields(res))
        return jsonify(out)
    return _guard(run)


@app.route('/api/download/excel', methods=['POST'])
def download_excel():
    def run():
        res, lang = _compute_from_request()
        return _file_response(generate_excel(res, lang), _filename(res['meta']['name'], 'xlsx'),
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return _guard(run)


@app.route('/api/download/pdf', methods=['POST'])
def download_pdf():
    def run():
        res, lang = _compute_from_request()
        return _file_response(generate_pdf(res, lang), _filename(res['meta']['name'], 'pdf'),
                              'application/pdf')
    return _guard(run)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
