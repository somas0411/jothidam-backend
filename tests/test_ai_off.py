"""
The default build: AI_TABS_ENABLED is off (set by conftest for this module).

No AI_ sheet in any workbook, nothing about AI or AI sheets in the Notes
(குறிப்புகள்) sheet or the PDF in any language, /api/download/json is gone,
the Predictions (பலன்கள்) sheet has no "Chart basis" (ஜாதக அடிப்படை) column,
and the readings themselves are unchanged. Also the basic / full products.
"""
import io
import re
from datetime import datetime

import openpyxl
import pytest

import astro_engine as A
import i18n
import predictions as P
from enrich import enrich
from excel_generator import generate_excel, generate_family_excel, generate_match_excel
from pdf_generator import generate_pdf

NOW = datetime(2026, 10, 7, 17, 0)
S = dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707)
BOY = dict(name='Boy', dob='1990-05-10', tob='06:30', pob='Chennai', lat=13.0827, lon=80.2707)
GIRL = dict(name='Girl', dob='1993-08-21', tob='14:10', pob='Madurai', lat=9.9252, lon=78.1198)
LANGS = list(i18n.LANGS)
AI_WORDS = re.compile(r'\bAI\b|AI_|செயற்கை நுண்ணறிவு|एआई|ఏఐ|ಎಐ|എഐ|কৃত্রিম বুদ্ধিমত্তা|artificial intelligence', re.I)
BASIS = {'Chart basis', 'ஜாதக அடிப்படை', 'कुंडली का आधार', 'జాతక ఆధారం', 'ಜಾತಕದ ಆಧಾರ', 'ജാതകത്തിലെ ആധാരം',
         'कुंडलीचा आधार', 'কোষ্ঠীর ভিত্তি'}


def load(data):
    return openpyxl.load_workbook(io.BytesIO(data))


def texts(ws):
    return [str(v) for row in ws.iter_rows(values_only=True) for v in row if v is not None]


@pytest.fixture(scope='module')
def charts():
    out = {}
    for lang in LANGS:
        res = A.compute(lang=lang, now=NOW, **S)
        out[lang] = (res, enrich(res))
    return out


@pytest.mark.parametrize('lang', LANGS)
def test_no_ai_sheet_and_no_ai_text_in_notes(charts, lang):
    res, ai = charts[lang]
    wb = load(generate_excel(res, lang, ai=ai, predictions=True))
    assert not [n for n in wb.sheetnames if n.startswith('AI_')]
    notes = wb[wb.sheetnames[6]]
    assert notes.title.startswith(i18n.L('notes', lang if lang != 'bi' else 'en')[:10])
    bad = [t for t in texts(notes) if AI_WORDS.search(t)]
    assert not bad, bad


@pytest.mark.parametrize('lang', LANGS)
def test_predictions_sheet_has_no_chart_basis_column(charts, lang):
    res, ai = charts[lang]
    wb = load(generate_excel(res, lang, ai=ai, predictions=True))
    ws = wb[wb.sheetnames[7]]
    cells = set(texts(ws))
    assert not cells & BASIS
    assert ws.max_column <= 6                      # A spacer + topic, text, tone, period, status
    # the readings are the same as the engine builds them
    block = P.build(res, ai, lang)
    for x in block['rows']:
        if x['item'] != 'disclaimer':
            assert x['text'] in cells


def test_readings_unchanged_by_the_switch(charts, monkeypatch):
    res, ai = charts['ta']
    off = P.build(res, ai, 'ta')
    monkeypatch.setenv('AI_TABS_ENABLED', 'true')
    assert P.build(res, ai, 'ta') == off


def test_basic_product_drops_divisional_notes_and_predictions(charts):
    res, ai = charts['ta']
    full = load(generate_excel(res, 'ta', ai=ai, predictions=True, product='full')).sheetnames
    basic = load(generate_excel(res, 'ta', ai=ai, predictions=True, product='basic')).sheetnames
    assert 'குறிப்புகள்' in full and 'பலன்கள்' in full
    assert 'குறிப்புகள்' not in basic and 'பலன்கள்' not in basic
    assert len(basic) == len(full) - 3
    assert set(basic) < set(full)
    pf = generate_pdf(res, 'ta', predictions=P.build(res, ai, 'ta'))
    pb = generate_pdf(res, 'ta', predictions=P.build(res, ai, 'ta'), product='basic')
    assert pb[:4] == b'%PDF' and len(pb) < len(pf)


def test_match_and_family_workbooks_without_ai_sheets():
    import family_engine
    import match_engine
    boy, girl = A.compute(lang='en', now=NOW, **BOY), A.compute(lang='en', now=NOW, **GIRL)
    result = match_engine.match(boy, girl)
    wb = load(generate_match_excel(result, {'boy': boy, 'girl': girl}, 'ta'))
    assert not [n for n in wb.sheetnames if n.startswith('AI_')]
    assert not [t for ws in wb for t in texts(ws) if 'AI_' in t]
    fam = family_engine.family([{'relation': 'Self', 'res': boy}, {'relation': 'Spouse', 'res': girl}], now=NOW)
    wbf = load(generate_family_excel(fam, 'ta'))
    assert not [n for n in wbf.sheetnames if n.startswith('AI_')]


def test_json_download_is_off():
    import app as app_module
    r = app_module.app.test_client().post('/api/download/json', json=dict(S, lang='en'))
    assert r.status_code == 404


def test_options_say_ai_off_and_payments_off():
    import app as app_module
    j = app_module.app.test_client().get('/api/options').get_json()
    assert j['ai_tabs'] is False and j['payments_enabled'] is False
    prices = {p['code']: p['price_paise'] for p in j['products']}
    assert prices == {'basic': 20000, 'full': 50000, 'match': 20000, 'family': 50000}


def test_free_download_still_works_without_ai_sheets():
    import app as app_module
    r = app_module.app.test_client().post('/api/download/excel', json=dict(S, lang='ta'))
    assert r.status_code == 200
    wb = load(r.data)
    assert 'பலன்கள்' in wb.sheetnames and not [n for n in wb.sheetnames if n.startswith('AI_')]
