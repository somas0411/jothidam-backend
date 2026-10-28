"""
Find English left in a non-English horoscope report.

    python tests/i18n_audit.py            # every language, summary and the first hits
    python tests/i18n_audit.py te -v      # one language, every hit

For one chart in each report language it builds what a visitor sees:
  * web   the /api/horoscope answer with "predictions": true (the labels,
          names and readings the page shows; meta, basis and the AI-only
          fields are skipped)
  * xlsx  the seven report sheets and the Predictions sheet (the AI_ sheets
          are English by design and are skipped; so is the basis column)
  * pdf   the text of the PDF (needs pypdf)
and lists every run of 3 or more English words that is not on the allowed
list below. tests/test_i18n.py runs the same audit as a test.
"""
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CHART = dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707)
LANGS = ('ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn')

# A run of 3 or more words written in Latin letters
RUN = re.compile(r"[A-Za-z][A-Za-z'’.-]*(?:[ ,/&()-]+[A-Za-z][A-Za-z'’.-]*){2,}")

# English that may stay: proper names, codes, the user's own input
ALLOWED = [
    r'Swiss Ephemeris[^,;]*', r'Moshier', r'horoscopegen\.in', r'HoroscopeGen', r'Chart S', r'Chennai',
    r'Asia/[A-Za-z_]+', r'Lahiri[^,;]*', r'Chitrapaksha', r'Krishnamurti', r'Placidus', r'Porphyry', r'Sripati',
    r'Noto Sans[^,;]*', r'UTC[+-]\d', r'BPHS', r'K\.?P\.?', r'ALP', r'D\d+',
]
ALLOWED_RE = re.compile('|'.join(ALLOWED))

# Keys of the /api/horoscope answer that the page does not show as text
WEB_SKIP = {'meta', 'basis', 'columns', 'ai', 'sort_key', 'section', 'item', 'tone', 'status', 'key',
            'style', 'dms', 'id', 'lang', 'charts', 'varga_charts'}


def english_runs(text):
    """The English runs of a text, after removing the allowed English."""
    if not isinstance(text, str) or not text:
        return []
    rest = ALLOWED_RE.sub(' ', text)
    return [m.group(0) for m in RUN.finditer(rest) if len(m.group(0).split()) >= 3]


def _walk(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in WEB_SKIP:
                continue
            yield from _walk(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f'{path}[{i}]')
    elif isinstance(obj, str):
        yield path, obj


def web_hits(lang):
    import app as app_module
    app_module.limiter.enabled = False
    body = dict(CHART, lang=lang, chartStyle='south', ayanamsha='lahiri', predictions=True)
    data = app_module.app.test_client().post('/api/horoscope', json=body).get_json()
    for chart_key in ('charts', 'varga_charts'):                 # chart titles and cell names are shown
        charts = data.get(chart_key) or {}
        items = charts.values() if isinstance(charts, dict) else charts
        for spec in items:
            for path, text in _walk({k: v for k, v in spec.items() if k in ('title', 'purpose', 'subtitle')}):
                for run in english_runs(text):
                    yield f'web.{chart_key}{path}', run
    for path, text in _walk(data):
        for run in english_runs(text):
            yield 'web' + path, run


def xlsx_hits(lang):
    import openpyxl
    import astro_engine as A
    from enrich import enrich
    from excel_generator import generate_excel
    res = A.compute(lang=lang, **CHART)
    wb = openpyxl.load_workbook(io.BytesIO(generate_excel(res, lang, ai=enrich(res), predictions=True)))
    sheets = wb.worksheets[:8]
    for ws in sheets:
        ai_band = None                    # Notes: the AI rules band is English by design
        for row in ws.iter_rows():
            for cell in row:
                if cell.value == 'AI sheets: rules and variants':
                    ai_band = cell.row
                if ai_band and cell.row >= ai_band:
                    continue
                if not isinstance(cell.value, str):
                    continue
                if ws is sheets[7] and cell.column == 7:              # Predictions: basis column (English)
                    continue
                for run in english_runs(cell.value):
                    yield f'xlsx.{ws.title}!{cell.coordinate}', run


def pdf_hits(lang):
    import pypdf
    import astro_engine as A
    import predictions as P
    from enrich import enrich
    from pdf_generator import generate_pdf
    res = A.compute(lang=lang, **CHART)
    data = generate_pdf(res, lang, predictions=P.build(res, enrich(res), lang))
    reader = pypdf.PdfReader(io.BytesIO(data))
    for n, page in enumerate(reader.pages, start=1):
        for line in (page.extract_text() or '').splitlines():
            for run in english_runs(line):
                yield f'pdf.p{n}', run


def audit(lang, parts=('web', 'xlsx', 'pdf')):
    out = []
    for part in parts:
        fn = {'web': web_hits, 'xlsx': xlsx_hits, 'pdf': pdf_hits}[part]
        out.extend(fn(lang))
    return out


def main(argv):
    import logging
    logging.disable(logging.WARNING)
    verbose = '-v' in argv
    langs = [a for a in argv if a in LANGS] or list(LANGS)
    total = 0
    for lang in langs:
        hits = audit(lang)
        total += len(hits)
        by_part = {}
        for where, _ in hits:
            by_part[where.split('.')[0]] = by_part.get(where.split('.')[0], 0) + 1
        print(f'{lang}: {len(hits)} English runs {by_part}')
        shown = hits if verbose else hits[:15]
        for where, run in shown:
            print(f'   {where}: {run[:110]}')
    print('total', total)
    return total


if __name__ == '__main__':
    main(sys.argv[1:])
