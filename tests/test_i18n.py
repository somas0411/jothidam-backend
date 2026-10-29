"""
Tests for the report languages (en, ta, hi, te, kn, ml, mr, bn).

  * every prediction template is written in all 8 languages with the same
    placeholders as English
  * every rule-book language file covers every pattern, phrase and data-file
    line of the catalog, with the same placeholders
  * the name and label tables of i18n.py are complete for every language
  * no template or rule-book text breaks site policy in any script (death,
    length of life, maraka, health words)
  * rule-book findings of sample charts all have a translation
  * the audit (tests/i18n_audit.py) finds no English left in the web answer,
    the Excel workbook or the PDF for ta, hi, te, kn, ml, mr and bn
"""
import json
import os
import re
from datetime import datetime

import pytest

import i18n
import notes_i18n
import predictions as P
import rulebook_i18n as RI
from rulebook import BANNED

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ('en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn')
OTHER = LANGS[1:]
PH = re.compile(r'\{(\w+)\}')


def _templates():
    folder = os.path.join(ROOT, 'data', 'predictions')
    out = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith('.json'):
            with open(os.path.join(folder, name), encoding='utf-8') as f:
                for key, val in json.load(f).items():
                    if isinstance(val, dict) and 'en' in val:
                        out[f'{name}:{key}'] = val
    return out


def test_templates_in_every_language():
    templates = _templates()
    assert len(templates) > 400
    for key, val in templates.items():
        if not isinstance(val['en'], str):
            continue
        want = set(PH.findall(val['en']))
        for lang in LANGS:
            assert val.get(lang), (key, lang)
            assert set(PH.findall(val[lang])) == want, (key, lang)


def test_rulebook_files_complete():
    cat = RI.catalog()
    langs = RI.languages()
    assert set(OTHER) <= set(langs)
    lines = None
    for lang in OTHER:
        with open(os.path.join(RI.DIR, f'{lang}.json'), encoding='utf-8') as f:
            data = json.load(f)
        for table in ('patterns', 'phrases'):
            assert set(data[table]) == set(cat[table]), (lang, table)
            for k, text in data[table].items():
                assert set(PH.findall(text)) == set(PH.findall(cat[table][k])), (lang, k)
        lines = lines or set(data['lines'])
        assert set(data['lines']) == lines, lang
        assert all(data['lines'].values()), lang


def test_name_tables_complete():
    for lang in OTHER:
        assert set(i18n.LABELS[lang]) == set(i18n.LABELS['en']), lang
        assert len(i18n.NAKS[lang]) == 27 and len(i18n.RASIS[lang]) == 12, lang
        assert set(i18n.PLANETS[lang]) == set(i18n.PLANETS['en']), lang
        assert set(i18n.WEEKDAYS[lang]) == set(i18n.WEEKDAYS['en']), lang
        assert set(i18n.TITHIS[lang]) == set(i18n.TITHIS['ta']), lang
        assert set(i18n.VARGA_PURPOSE[lang]) == set(i18n.VARGA_PURPOSE['en']), lang
        assert set(i18n.VARGA_NAMES.get(lang, {})) == set(i18n.VARGA_NAMES['en']), lang
        assert i18n.retro_mark(lang) != '(R)', lang


def test_notes_complete():
    keys = set(notes_i18n.T['hi'])
    for lang in notes_i18n.NOTE_LANGS:
        assert set(notes_i18n.T[lang]) == keys, lang
        for k in keys:
            assert set(PH.findall(notes_i18n.T[lang][k])) == set(PH.findall(notes_i18n.T['hi'][k])), (lang, k)


def _guards(text):
    return BANNED.search(text) or P.HEALTH.search(text) or P.NATIVE_BANNED.search(text)


def test_templates_follow_policy():
    for key, val in _templates().items():
        if key.endswith(':nyn.Ayushman') or not isinstance(val['en'], str):
            continue                                            # the yoga name is never printed (predictions.py)
        for lang in LANGS:
            text = val[lang]
            assert not _guards(text), (key, lang, text)


def test_rulebook_texts_follow_policy():
    cat = RI.catalog()
    english_lines = RI._known_lines()
    shown = {x for x in english_lines if not any(g.search(x) for g in P.RULE_LINE_DROP)}
    for lang in OTHER:
        with open(os.path.join(RI.DIR, f'{lang}.json'), encoding='utf-8') as f:
            data = json.load(f)
        for k, text in list(data['patterns'].items()) + list(data['phrases'].items()):
            assert not _guards(text), (lang, k, text)
        for en, text in data['lines'].items():
            if en in shown:                                     # lines the English filter drops never print
                assert not _guards(text), (lang, en, text)


NOW = datetime(2026, 10, 7, 17, 0)
CHARTS = [
    dict(name='Chart S', dob='1984-11-04', tob='00:20', pob='Chennai', lat=13.0827, lon=80.2707),
    dict(name='Chart B', dob='1998-03-06', tob='01:37', pob='Delhi', lat=28.6139, lon=77.2090),
    dict(name='Chart C', dob='1961-08-15', tob='14:05', pob='Mumbai', lat=19.0760, lon=72.8777),
]


@pytest.mark.parametrize('chart', CHARTS, ids=lambda c: c['name'])
def test_rule_findings_translated(chart):
    import astro_engine as A
    from enrich import enrich
    res = A.compute(lang='en', now=NOW, **chart)
    ai = enrich(res)
    for r in ai['tables']['AI_RuleBook']:
        for lang in OTHER:
            out = RI.translate(r['finding'], r['rule_id'], lang, lambda p: i18n.planet(p, lang),
                               drop=P.RULE_LINE_DROP)
            assert out is not None, (lang, r['rule_id'], r['finding'])


@pytest.mark.parametrize('chart', CHARTS[:1], ids=lambda c: c['name'])
def test_rows_follow_policy_in_every_language(chart):
    import astro_engine as A
    from enrich import enrich
    res = A.compute(lang='en', now=NOW, **chart)
    ai = enrich(res)
    for lang in LANGS:
        for r in P.build(res, ai, lang)['rows']:
            assert r['text'], (lang, r['item'])
            assert not PH.search(r['text']), (lang, r['text'])


@pytest.mark.parametrize('lang', ['ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn'])
def test_no_english_left(lang):
    from tests import i18n_audit
    hits = i18n_audit.audit(lang)
    assert not hits, hits[:10]


def test_marriage_tables_complete():
    for lang in OTHER:
        assert set(i18n.MATCH_LABELS[lang]) == set(i18n.MATCH_LABELS['en']), lang
        assert set(i18n.MATCH_CHECKS[lang]) == set(i18n.MATCH_CHECKS['ta']), lang
        assert set(i18n.MATCH_WORDS[lang]) == set(i18n.MATCH_WORDS['ta']), lang
        for k, v in i18n.MATCH_LABELS[lang].items():
            assert set(PH.findall(v)) == set(PH.findall(i18n.MATCH_LABELS['en'][k])), (lang, k)
