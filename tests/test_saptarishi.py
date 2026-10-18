"""
Saptarishi Samvat year, gotra -> rishi lineage, and the Arundhati note.
"""
from datetime import datetime

import pytest

import i18n
import saptarishi as S

LANGS8 = ['en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn']
BIRTH = dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707)
NOW = datetime(2026, 10, 7, 17, 0)


# ── Saptarishi Samvat ─────────────────────────────────────────────────────────

def _year(local, offset_hours=5.5):
    from datetime import timedelta
    return S.samvat(local, local - timedelta(hours=offset_hours))


def test_kalhana_check_laukika_24_is_shaka_1070():
    # Rajatarangini: Laukika (4)24 = Shaka 1070 = 1148 CE.
    s = _year(datetime(1148, 6, 1, 12, 0))
    assert (s['full'], s['short'], s['display']) == (4224, 24, '24 (4224)')
    assert s['full'] == 1070 + 3154                 # Shaka + 3154


def test_the_year_changes_at_chaitra_shukla_pratipada():
    before, after = _year(datetime(2026, 1, 10, 12)), _year(datetime(2026, 10, 18, 22))
    assert after['full'] - before['full'] == 1
    assert after['display'] == '02 (5102)' and before['display'] == '01 (5101)'


@pytest.mark.parametrize('year, day', [(2023, 21), (2025, 29), (2026, 19)])
def test_chaitra_starts_at_the_new_moon_before_ugadi(year, day):
    # The new moons that began Chaitra (Ugadi is the next day): 21-03-2023, 29-03-2025, 19-03-2026 (UT).
    start = S._jd_to_dt(S.chaitra_start_jd(year))
    assert (start.month, start.day) == (3, day)


def test_either_side_of_the_new_moon_on_19_march_2026():
    # New moon at about 01:23 UT on 19-03-2026.
    assert _year(datetime(2026, 3, 19, 6, 0), 5.5)['full'] == 5101      # 00:30 UT: before
    assert _year(datetime(2026, 3, 19, 7, 30), 5.5)['full'] == 5102     # 02:00 UT: after


def test_today():
    s = _year(datetime(2026, 10, 18, 12))
    assert s['short'] == 2 and s['gregorian_year'] == 2026


def test_compute_carries_the_year():
    import astro_engine as A
    res = A.compute(now=NOW, **BIRTH)
    assert res['saptarishi']['samvat']['display'] == '60 (5060)'
    assert res['saptarishi']['gotra'] is None


# ── Gotra ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('text, key, rishi', [
    ('Kaundinya', 'kaundinya', 'vasishtha'), ('koundinya', 'kaundinya', 'vasishtha'),
    ('Kaundinya Gotra', 'kaundinya', 'vasishtha'), ('Srivatsa', 'srivatsa', 'jamadagni'),
    ('Sreevatsa', 'srivatsa', 'jamadagni'), ('Bharadwaj', 'bharadvaja', 'bharadvaja'),
    ('BHARADVAJA', 'bharadvaja', 'bharadvaja'), ('Shandilya', 'shandilya', 'kashyapa'),
    ('Athreya', 'atreya', 'atri'), ('Agasthya', 'agastya', 'agastya'), ('Vishnu Vriddha', 'vishnuvriddha', 'bharadvaja'),
])
def test_gotra_lookup(text, key, rishi):
    g = S.gotra_info(text)
    assert (g['key'], g['rishi']) == (key, rishi)


def test_stars_only_for_rishis_that_are_stars_of_the_mandala():
    assert S.gotra_info('Kaundinya')['star'] == 'mizar'        # Vasishtha
    assert S.gotra_info('Atreya')['star'] == 'megrez'          # Atri
    for text in ('Kashyapa', 'Kaushika', 'Gautama', 'Srivatsa', 'Bharadvaja', 'Agastya'):
        assert S.gotra_info(text)['star'] is None


def test_every_gotra_and_rishi_has_a_name_in_every_language():
    for lang in LANGS8:
        for key, row in S.GOTRAS.items():
            assert i18n.GOTRA_NAMES[lang][key], (lang, key)
            assert row['rishi'] in i18n.RISHI_NAMES[lang]
        for rishi, meta in S.RISHIS.items():
            assert i18n.RISHI_NAMES[lang][rishi]
            for extra in (meta['line'], meta['star']):
                assert extra is None or i18n.RISHI_NAMES[lang][extra]
        assert set(i18n.SAPTA_LABELS[lang]) == set(i18n.SAPTA_LABELS['en']), lang
        if lang != 'en':
            assert all(v != i18n.SAPTA_LABELS['en'][k] for k, v in i18n.SAPTA_LABELS[lang].items()), lang


@pytest.mark.parametrize('text', [None, '', '   ', 'Other', 'not known', '-'])
def test_no_gotra_means_nothing_is_shown(text):
    assert S.gotra_info(text) is None
    assert S.gotra_rows(None, 'en') == []


def test_an_unknown_gotra_is_kept_as_entered():
    g = S.gotra_info('  Someunknown  ')
    assert g == {'entered': 'Someunknown', 'key': None, 'rishi': None, 'line': None, 'star': None}
    assert S.gotra_rows(g, 'ta') == [('கோத்திரம்', 'Someunknown'), ('மூல ரிஷி', 'பட்டியலில் இல்லை')]


def test_long_input_is_cut():
    assert len(S.gotra_info('x' * 500)['entered']) == S.GOTRA_MAX_LEN


def test_same_gotra():
    k, v, x = S.gotra_info('Koundinya'), S.gotra_info('Vasishtha'), S.gotra_info('kaundinya gotra')
    assert S.same_gotra(k, x) is True and S.same_gotra(k, v) is False
    assert S.same_gotra(k, None) is None and S.same_gotra(None, None) is None
    assert S.same_gotra(S.gotra_info('Abc'), S.gotra_info('ABC')) is True


# ── Views ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize('lang', LANGS8 + ['bi'])
def test_match_view_in_every_language(lang):
    block = S.match_block(S.gotra_info('Bharadwaj'), S.gotra_info('Kaundinya'))
    v = S.match_view(block, lang)
    assert v['arundhati']['title'] == i18n.SL('arundhati_title', lang)
    assert 'Alcor' in v['arundhati']['text'] and 'Mizar' in v['arundhati']['text']
    assert v['gotra']['rows'][-1] == (i18n.SL('same_gotra', lang), i18n.SL('no', lang))
    if lang == 'bi':
        assert v['arundhati']['text'].count('\n') == 1


def test_arundhati_note_is_short_and_positive():
    text = i18n.SL('arundhati_text', 'en')
    assert 60 <= len(text.split()) <= 80
    banned = ('dosha', 'death', 'widow', 'longevity', 'marak', 'ayur', 'bad', 'danger')
    for lang in LANGS8:
        assert not any(w in i18n.SL('arundhati_text', lang).lower() for w in banned)


def test_match_view_without_gotras_has_only_the_note():
    assert S.match_view(None, 'en')['gotra'] is None
    assert S.match_view(S.match_block(None, None), 'en')['gotra'] is None


# ── API and files ─────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    import app as app_module
    return app_module.app.test_client()


BODY = dict(BIRTH, lang='ta', chartStyle='south', ayanamsha='lahiri', gender='male')
GIRL = {'dob': '1988-02-14', 'tob': '06:45', 'pob': 'Madurai', 'lat': 9.9252, 'lon': 78.1198, 'gotra': 'Kaundinya'}


def test_api_horoscope_view(client):
    j = client.post('/api/horoscope', json=dict(BODY, gotra='Srivatsa')).get_json()
    assert j['saptarishi_view']['samvat'] == {'label': 'சப்தரிஷி சம்வத்', 'value': '60 (5060)',
                                              'note': i18n.SL('samvat_note', 'ta')}
    assert j['saptarishi_view']['gotra']['rows'] == [['கோத்திரம்', 'ஸ்ரீவத்ச'], ['மூல ரிஷி', 'ஜமதக்னி (பிருகு மரபு)']]
    assert client.post('/api/horoscope', json=BODY).get_json()['saptarishi_view']['gotra'] is None


def test_gotra_changes_no_matching_result(client):
    plain = client.post('/api/match', json={'mode': 'full', 'lang': 'en', 'boy': BIRTH, 'girl': dict(GIRL, gotra='')})
    same = client.post('/api/match', json={'mode': 'full', 'lang': 'en', 'boy': dict(BIRTH, gotra='Koundinya'),
                                           'girl': GIRL})
    a, b = plain.get_json(), same.get_json()
    assert b['saptarishi']['same'] is True and a['saptarishi']['same'] is None
    for key in ('rows', 'summary'):        # windows start at the moment of the request
        assert a[key] == b[key]


def test_star_mode_takes_a_gotra(client):
    j = client.post('/api/match', json={'mode': 'star', 'lang': 'en',
                                         'boy': {'nakshatra': 4, 'pada': 2, 'rasi': 2, 'gotra': 'Atreya'},
                                         'girl': {'nakshatra': 10, 'rasi': 5}}).get_json()
    assert j['saptarishi']['boy']['rishi'] == 'atri' and j['saptarishi']['girl'] is None
    assert ['Girl: Gotra', 'Not given'] in j['saptarishi_view']['gotra']['rows']


def _texts(data):
    import io
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data))
    return {str(c.value) for ws in wb.worksheets for row in ws.iter_rows() for c in row if c.value is not None}


def test_excel_and_pdf_carry_the_three_additions(client):
    body = dict(BODY, gotra='Koundinya', partner=GIRL)
    texts = _texts(client.post('/api/download/excel', json=body).data)
    assert {'சப்தரிஷி சம்வத்', '60 (5060)', 'கோத்திரம்', 'கௌண்டின்ய', 'மூல ரிஷி', 'வசிஷ்டர்',
            'அருந்ததி தரிசனம்', i18n.SL('arundhati_text', 'ta')} <= texts
    pdf = client.post('/api/download/pdf', json=body)
    assert pdf.status_code == 200 and pdf.data[:4] == b'%PDF'


@pytest.mark.parametrize('lang', LANGS8 + ['bi'])
def test_match_files_in_every_language(client, lang):
    body = {'mode': 'full', 'lang': lang, 'boy': dict(BIRTH, gotra='Bharadwaj'), 'girl': GIRL}
    texts = _texts(client.post('/api/download/match/excel', json=body).data)
    assert i18n.SL('arundhati_title', lang) in texts and i18n.SL('same_gotra', lang) in texts
    pdf = client.post('/api/download/match/pdf', json=body)
    assert pdf.status_code == 200 and pdf.data[:4] == b'%PDF'
