"""
app.py — Jothidam Backend API Server
Flask backend for horoscopegen.in

Endpoints:
  POST /api/horoscope         — Returns JSON horoscope data
  POST /api/download/pdf      — Returns PDF binary
  POST /api/download/excel    — Returns Excel binary
  POST /api/verify-payment    — Razorpay payment verification

Deploy to Render.com (free tier):
  - Build Command: pip install -r requirements.txt
  - Start Command: gunicorn app:app
"""

import os
import json
import hmac
import hashlib
import logging
from datetime import date
from flask import Flask, request, jsonify, send_file, make_response
import io

# Conditional CORS
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from astro_engine import (
    compute, fmt_date, get_rasi_name, get_nak_name, get_planet_name,
    get_rasi, get_nak, get_pada, fmt_deg, build_bhuktis, lbl,
    LUCKY_NUMS, LUCKY_COLORS, get_gemstone
)
from pdf_generator import generate_pdf
from excel_generator import generate_excel

# ── APP SETUP ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
if HAS_CORS:
    CORS(app, origins=[
        'https://horoscopegen.in',
        'https://www.horoscopegen.in',
        'https://horoscopesgen.netlify.app',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
    ])

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

# ── CORS HEADERS (manual fallback if flask-cors not installed) ─────────────────
def add_cors(response):
    origin = request.headers.get('Origin', '')
    allowed = [
        'https://horoscopegen.in',
        'https://www.horoscopegen.in',
        'https://horoscopesgen.netlify.app',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
    ]
    if origin in allowed or not HAS_CORS:
        response.headers['Access-Control-Allow-Origin'] = origin or '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

@app.after_request
def after_request(response):
    return add_cors(response)

@app.route('/api/ping', methods=['GET','OPTIONS'])
def ping():
    """Health check"""
    if request.method == 'OPTIONS':
        return make_response('', 204)
    return jsonify({'status': 'ok', 'service': 'Jothidam API', 'version': '2.0'})

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok'})

# ── HOROSCOPE DATA ENDPOINT ────────────────────────────────────────────────────
@app.route('/api/horoscope', methods=['POST','OPTIONS'])
def horoscope():
    """Calculate and return full horoscope data as JSON"""
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        body = request.get_json(force=True)
        name        = body.get('name','').strip()
        dob         = body.get('dob','').strip()       # YYYY-MM-DD
        tob         = body.get('tob','').strip()       # HH:MM
        pob         = body.get('pob','').strip()
        lang        = body.get('lang','en')
        chart_style = body.get('chartStyle','south')

        if not all([name, dob, tob, pob]):
            return jsonify({'error': 'Missing required fields'}), 400

        data = compute(name, dob, tob, pob, chart_style, lang)

        # Build JSON-serialisable response
        def d_str(d): return d.isoformat() if isinstance(d, date) else str(d)

        planet_rows = []
        lagna_rasi = data['lagna_rasi']
        for pname, lon in data['planet_list']:
            rn   = get_rasi(lon)
            house = ((rn - lagna_rasi + 12) % 12) + 1
            planet_rows.append({
                'planet':     pname,
                'planetName': get_planet_name(pname, lang),
                'rasi':       get_rasi_name(rn, lang),
                'rasiIndex':  rn,
                'degrees':    fmt_deg(lon),
                'nakshatra':  get_nak_name(get_nak(lon), lang),
                'pada':       get_pada(lon),
                'house':      house,
                'longitude':  round(lon, 4),
            })

        dasa_rows = []
        for drow in data['dasas']:
            bhuktis = build_bhuktis(drow['dasa'], drow['start'], drow['end'])
            today   = date.today()
            for brow in bhuktis:
                is_cur  = brow['start'] <= today <= brow['end']
                is_past = brow['end'] < today
                dasa_rows.append({
                    'dasa':    drow['dasa'],
                    'bhukti':  brow['bhukti'],
                    'start':   d_str(brow['start']),
                    'end':     d_str(brow['end']),
                    'status':  'current' if is_cur else ('completed' if is_past else 'upcoming'),
                })

        yoga_rows = [{'name': yn, 'description': yd} for yn, yd in data['yogas']]

        resp = {
            'name':         data['name'],
            'dob':          data['dob'],
            'tob':          data['tob'],
            'pob':          data['pob'],
            'lang':         lang,
            'lagnaRasi':    data['lagna_rasi'],
            'lagnaName':    get_rasi_name(data['lagna_rasi'], lang),
            'moonRasi':     data['moon_rasi'],
            'moonRasiName': get_rasi_name(data['moon_rasi'], lang),
            'nakNum':       data['nak_num'],
            'nakName':      get_nak_name(data['nak_num'], lang),
            'nakPada':      data['nak_pada'],
            'nakLord':      data['nak_lord'],
            'curDasa':      {'dasa': data['cur_dasa']['dasa'],   'end': d_str(data['cur_dasa']['end'])},
            'curBhukti':    {'bhukti': data['cur_bhukti']['bhukti'], 'end': d_str(data['cur_bhukti']['end'])},
            'planets':      planet_rows,
            'dasas':        dasa_rows,
            'yogas':        yoga_rows,
            'gemstone':     get_gemstone(data['nak_lord'], lang),
            'luckyColors':  LUCKY_COLORS.get(data['nak_lord'],'Gold'),
            'luckyNumbers': LUCKY_NUMS.get(data['nak_lord'],[1,4,7]),
            'generatedOn':  date.today().isoformat(),
        }
        return jsonify(resp)

    except Exception as e:
        log.exception('Error in /api/horoscope')
        return jsonify({'error': str(e)}), 500

# ── PDF DOWNLOAD ENDPOINT ──────────────────────────────────────────────────────
@app.route('/api/download/pdf', methods=['POST','OPTIONS'])
def download_pdf():
    """Generate and return PDF"""
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        body = request.get_json(force=True)
        name        = body.get('name','').strip()
        dob         = body.get('dob','').strip()
        tob         = body.get('tob','').strip()
        pob         = body.get('pob','').strip()
        lang        = body.get('lang','en')
        chart_style = body.get('chartStyle','south')

        if not all([name, dob, tob, pob]):
            return jsonify({'error': 'Missing required fields'}), 400

        data    = compute(name, dob, tob, pob, chart_style, lang)
        pdf_bytes = generate_pdf(data, lang=lang, chart_style=chart_style)

        filename = f"Jothidam_{name.replace(' ','_')}.pdf"
        response = make_response(pdf_bytes)
        response.headers['Content-Type']        = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length']      = len(pdf_bytes)
        return response

    except Exception as e:
        log.exception('Error in /api/download/pdf')
        return jsonify({'error': str(e)}), 500

# ── EXCEL DOWNLOAD ENDPOINT ────────────────────────────────────────────────────
@app.route('/api/download/excel', methods=['POST','OPTIONS'])
def download_excel():
    """Generate and return Excel"""
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        body = request.get_json(force=True)
        name        = body.get('name','').strip()
        dob         = body.get('dob','').strip()
        tob         = body.get('tob','').strip()
        pob         = body.get('pob','').strip()
        lang        = body.get('lang','en')
        chart_style = body.get('chartStyle','south')

        if not all([name, dob, tob, pob]):
            return jsonify({'error': 'Missing required fields'}), 400

        data       = compute(name, dob, tob, pob, chart_style, lang)
        xlsx_bytes = generate_excel(data, lang=lang)

        filename = f"Jothidam_{name.replace(' ','_')}.xlsx"
        response = make_response(xlsx_bytes)
        response.headers['Content-Type']        = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length']      = len(xlsx_bytes)
        return response

    except Exception as e:
        log.exception('Error in /api/download/excel')
        return jsonify({'error': str(e)}), 500

# ── RAZORPAY PAYMENT VERIFICATION ─────────────────────────────────────────────
@app.route('/api/verify-payment', methods=['POST','OPTIONS'])
def verify_payment():
    """
    Verify Razorpay payment signature.
    Frontend sends: razorpay_order_id, razorpay_payment_id, razorpay_signature
    """
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        body = request.get_json(force=True)
        order_id   = body.get('razorpay_order_id','')
        payment_id = body.get('razorpay_payment_id','')
        signature  = body.get('razorpay_signature','')

        if not RAZORPAY_KEY_SECRET:
            # Dev mode — skip verification
            log.warning('RAZORPAY_KEY_SECRET not set — skipping signature check (dev mode)')
            return jsonify({'verified': True, 'dev_mode': True})

        # Compute expected signature
        msg      = f'{order_id}|{payment_id}'.encode('utf-8')
        expected = hmac.new(RAZORPAY_KEY_SECRET.encode('utf-8'), msg, hashlib.sha256).hexdigest()

        if hmac.compare_digest(expected, signature):
            return jsonify({'verified': True})
        else:
            return jsonify({'verified': False, 'error': 'Signature mismatch'}), 400

    except Exception as e:
        log.exception('Error in /api/verify-payment')
        return jsonify({'error': str(e)}), 500

# ── CREATE RAZORPAY ORDER ──────────────────────────────────────────────────────
@app.route('/api/create-order', methods=['POST','OPTIONS'])
def create_order():
    """
    Create Razorpay order.
    Requires: RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET env vars
    """
    if request.method == 'OPTIONS':
        return make_response('', 204)

    try:
        import razorpay
    except ImportError:
        # Dev mode without razorpay installed
        return jsonify({
            'order_id': 'order_dev_mode_test',
            'amount':   4900,
            'currency': 'INR',
            'dev_mode': True
        })

    try:
        body     = request.get_json(force=True)
        amount   = body.get('amount', 4900)  # in paise (₹49 = 4900)
        currency = body.get('currency', 'INR')

        key_id     = os.environ.get('RAZORPAY_KEY_ID','')
        key_secret = os.environ.get('RAZORPAY_KEY_SECRET','')

        if not key_id or not key_secret:
            return jsonify({'order_id': 'order_dev_no_keys', 'amount': amount, 'currency': currency, 'dev_mode': True})

        client = razorpay.Client(auth=(key_id, key_secret))
        order  = client.order.create({
            'amount':   amount,
            'currency': currency,
            'payment_capture': 1,
        })
        return jsonify({'order_id': order['id'], 'amount': amount, 'currency': currency})

    except Exception as e:
        log.exception('Error in /api/create-order')
        return jsonify({'error': str(e)}), 500

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
