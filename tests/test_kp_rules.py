"""Tests for kp_rules.py: the KP cuspal sub lord rule book and its report output."""

import io
import re
from datetime import datetime

import openpyxl
import pytest

import astro_engine as A
import excel_generator as X
import i18n
import kp_rules as KR
import pdf_generator as PG

NOW = datetime(2026, 11, 5, 11, 40)
ADULT = dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707)
MINOR = dict(name='Child', dob='2016-06-01', tob='09:15', pob='Chennai', lat=13.0827, lon=80.2707)
BANNED = re.compile(r'death|longevity|lifespan|maraka|surgery|hospital|accident|disease|illness|'
                    r'divorce|prison|channel|youtube|murali|masterclass', re.I)


@pytest.fixture(scope='module')
def adult():
    return A.compute(now=NOW, **ADULT)


def test_every_rule_has_all_languages():
    langs = [l for l in i18n.LANGS if l != 'bi']
    for r in KR.BOOK['rules']:
        assert set(langs) <= set(r['name']), r['id']
        assert not set(r['favourable']) & set(r['negating']), r['id']
        assert 1 <= r['cusp'] <= 12
    for k, v in KR.BOOK['labels'].items():
        assert set(langs) <= set(v), k


def test_no_banned_words_in_rule_book():
    for r in KR.BOOK['rules']:
        assert not BANNED.search(r['name']['en']), r['id']
    for v in KR.BOOK['labels'].values():
        assert not BANNED.search(v['en'])


def test_adult_rows_and_known_cusp(adult):
    rows = KR.evaluate(adult, NOW)
    assert len(rows) == len(KR.BOOK['rules'])
    assert {r['verdict'] for r in rows} <= {'strong', 'promised', 'mixed', 'weak'}
    tenth = next(r for r in rows if r['id'] == 'KP-10')
    assert tenth['csl'] == adult['kp']['cusps'][9]['sub_lord']
    for r in rows:
        if r['verdict'] == 'weak':
            assert r['window'] is None


def test_deterministic(adult):
    assert KR.evaluate(adult, NOW) == KR.evaluate(A.compute(now=NOW, **ADULT), NOW)


def test_minor_sees_only_education():
    rows = KR.evaluate(A.compute(now=NOW, **MINOR), NOW)
    assert rows and {r['topic'] for r in rows} == {'education'}


@pytest.mark.parametrize('lang', i18n.LANGS)
def test_table_rows_every_language(adult, lang):
    rows = KR.table_rows(adult, lang, NOW)
    assert rows and all(len(r) == 7 for r in rows)
    assert KR.label('section', lang)


def test_excel_full_has_section_basic_does_not(adult):
    def kp_text(product):
        wb = openpyxl.load_workbook(io.BytesIO(X.generate_excel(adult, lang='en', product=product)))
        ws = wb[X._sheet_name('kp', 'en')]
        return ' '.join(str(c.value) for row in ws.iter_rows() for c in row if c.value is not None)
    full = kp_text('full')
    assert KR.label('section', 'en') in full and 'Salaried job' in full
    assert not BANNED.search(full.replace('Kalyani', ''))
    assert KR.label('section', 'en') not in kp_text('basic')


@pytest.mark.parametrize('lang', ['en', 'ta', 'bi'])
def test_pdf_builds(adult, lang):
    full = PG.generate_pdf(adult, lang=lang, product='full')
    basic = PG.generate_pdf(adult, lang=lang, product='basic')
    assert full[:4] == b'%PDF' and len(full) > len(basic)
