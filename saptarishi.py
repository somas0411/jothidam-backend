"""
saptarishi.py — Saptarishi Samvat year, gotra -> rishi lineage, Arundhati note.

Three small, informational additions. None of them changes any other figure
of the horoscope or any result of the marriage match.

1. Saptarishi Samvat (Laukika era)
   Full year = Gregorian year + 3076 (= Kali Yuga year - 25 = Shaka year + 3154).
   Check: Kalhana's Rajatarangini equates Laukika 24 with Shaka 1070 (1148 CE):
   1148 + 3076 = 4224, written 24. The year begins at Chaitra Shukla Pratipada,
   taken here as the moment of the new moon that starts the amanta month of
   Chaitra: the new moon at which the Sun is in sidereal Meena (in the
   ayanamsha of the chart). When two new moons fall with the Sun in Meena
   (Adhika Chaitra) the first is used. A birth before that moment belongs to
   the previous year. Shown as the traditional short form (full year mod 100)
   with the full year in brackets, e.g. "02 (5102)". Nothing about where the
   Saptarishis "are" among the nakshatras is computed: there is no
   astronomical basis for it and the sources disagree.

2. Gotra -> root rishi, from data/gotra_rishi.json (a starting table that
   needs review). The gotra is optional; when it is not given nothing is shown.

3. Arundhati Darshan: a fixed cultural note for the marriage pages.

view_* functions give label / value rows already in the report language, so
the web page, the Excel and the PDF show the same thing.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import swisseph as swe

import i18n
from astro_engine import AYANAMSHAS, _EPH, _SWE_LOCK, julian_day, norm

LAUKIKA_OFFSET = 3076          # Laukika year = Gregorian (CE) year + 3076
GOTRA_MAX_LEN = 40

_DATA = json.loads((Path(__file__).parent / 'data' / 'gotra_rishi.json').read_text(encoding='utf-8'))
RISHIS = _DATA['rishis']
GOTRAS = _DATA['gotras']
_ALIASES = {}
for _key, _row in GOTRAS.items():
    for _alias in _row['aliases'] + [_key]:
        _ALIASES[re.sub(r'[^a-z]', '', _alias.lower())] = _key


# ── 1. SAPTARISHI SAMVAT ──────────────────────────────────────────────────────

def _elongation(jd):
    """Moon minus Sun, tropical, 0..360."""
    with _SWE_LOCK:
        sun = swe.calc_ut(jd, swe.SUN, _EPH)[0][0]
        moon = swe.calc_ut(jd, swe.MOON, _EPH)[0][0]
    return norm(moon - sun)


def _sidereal_sun(jd, sid_mode):
    with _SWE_LOCK:
        swe.set_sid_mode(sid_mode)
        return norm(swe.calc_ut(jd, swe.SUN, _EPH | swe.FLG_SIDEREAL)[0][0])


def _new_moons(jd_from, jd_to):
    """Moments (JD UT) of the new moons between two dates, to well under a minute."""
    found = []
    jd, e = jd_from, _elongation(jd_from)
    while jd < jd_to:
        jd2 = jd + 1.0
        e2 = _elongation(jd2)
        if e2 < e:                                  # elongation wrapped through 0: a new moon in (jd, jd2]
            lo, hi = jd, jd2
            for _ in range(40):
                mid = (lo + hi) / 2
                if _elongation(mid) > 180:          # still before conjunction
                    lo = mid
                else:
                    hi = mid
            found.append(hi)
        jd, e = jd2, e2
    return found


@lru_cache(maxsize=512)
def chaitra_start_jd(year, sid_mode=swe.SIDM_LAHIRI):
    """JD UT of Chaitra Shukla Pratipada (start of the amanta month Chaitra) in a Gregorian year."""
    start = swe.julday(year, 1, 15, 0.0)
    end = swe.julday(year, 5, 15, 0.0)
    for jd in _new_moons(start, end):
        if 330.0 <= _sidereal_sun(jd, sid_mode) < 360.0:
            return jd
    raise ValueError(f'No Chaitra new moon found in {year}')    # cannot happen for real dates


def samvat(local_dt, ut_dt, ayanamsha='lahiri'):
    """
    The Saptarishi Samvat year of a moment: local_dt decides the Gregorian
    year, ut_dt is compared with the start of Chaitra.
    """
    sid_mode = AYANAMSHAS.get(ayanamsha, AYANAMSHAS['lahiri'])[1]
    year = local_dt.year
    start = chaitra_start_jd(year, sid_mode)
    if julian_day(ut_dt) < start:
        year -= 1
        start = chaitra_start_jd(year, sid_mode)
    full = year + LAUKIKA_OFFSET
    return {'full': full, 'short': full % 100, 'display': f'{full % 100:02d} ({full})',
            'gregorian_year': year, 'year_start_ut': _jd_to_dt(start)}


def _jd_to_dt(jd):
    y, m, d, h = swe.revjul(jd)
    secs = round(h * 3600)
    return datetime(y, m, d, secs // 3600, (secs % 3600) // 60, secs % 60)


# ── 2. GOTRA ──────────────────────────────────────────────────────────────────

def clean_gotra(text):
    """The gotra as entered, trimmed and kept short; '' when not given."""
    if text is None:
        return ''
    text = re.sub(r'\s+', ' ', str(text)).strip()
    if text.lower() in ('', 'other', 'not known', 'none', 'na', 'n/a', '-'):
        return ''
    return text[:GOTRA_MAX_LEN]


def gotra_key(text):
    """The key of a gotra in data/gotra_rishi.json, or None when it is not in the table."""
    text = clean_gotra(text)
    if not text:
        return None
    word = re.sub(r'[^a-z]', '', text.lower())
    word = re.sub(r'(gotram|gothram|gotra|gothra)$', '', word)    # "Kaundinya gotra" -> "kaundinya"
    return _ALIASES.get(word)


def gotra_info(text):
    """
    None when no gotra is given. Otherwise {'entered', 'key', 'rishi', 'line',
    'star'}: key, rishi, line and star are None when the gotra is not in the table.
    """
    entered = clean_gotra(text)
    if not entered:
        return None
    key = gotra_key(entered)
    rishi = GOTRAS[key]['rishi'] if key else None
    meta = RISHIS.get(rishi, {}) if rishi else {}
    return {'entered': entered, 'key': key, 'rishi': rishi, 'line': meta.get('line'), 'star': meta.get('star')}


def same_gotra(a, b):
    """True / False when both gotras are given, None otherwise. Keys are compared when known."""
    if not a or not b:
        return None
    ka, kb = a.get('key'), b.get('key')
    if ka and kb:
        return ka == kb
    return re.sub(r'[^a-z]', '', a['entered'].lower()) == re.sub(r'[^a-z]', '', b['entered'].lower())


def info(res, gotra=None):
    """The block stored in a compute() result under 'saptarishi'."""
    m = res['meta']
    return {'samvat': samvat(m['local_dt'], m['ut_dt'], m.get('ayanamsha_key', 'lahiri')),
            'gotra': gotra_info(gotra)}


# ── 3. VIEWS (already in the report language) ─────────────────────────────────

def _gotra_value(g, lang):
    return i18n.gotra_name(g['key'], lang) if g['key'] else g['entered']


def _rishi_value(g, lang):
    if not g['rishi']:
        return i18n.SL('not_in_list', lang)
    text = i18n.rishi_name(g['rishi'], lang)
    if g['line']:
        text += f" ({i18n.rishi_name(g['line'], lang)})"
    return text


def gotra_rows(g, lang):
    """Label / value rows of one person's gotra (empty when not given)."""
    if not g:
        return []
    rows = [(i18n.SL('gotra', lang), _gotra_value(g, lang)), (i18n.SL('rishi', lang), _rishi_value(g, lang))]
    if g.get('star'):
        rows.append((i18n.SL('mandala', lang), i18n.rishi_name(g['star'], lang)))
    return rows


def samvat_row(s, lang):
    return (i18n.SL('samvat', lang), s['display'])


def note_text(key, lang):
    """A sentence: bilingual reports put the Tamil on its own line rather than after ' / '."""
    if lang == 'bi':
        return f"{i18n.SL(key, 'en')}\n{i18n.SL(key, 'ta')}"
    return i18n.SL(key, lang)


def view(sp, lang):
    """What the web page shows for one horoscope."""
    return {'samvat': {'label': i18n.SL('samvat', lang), 'value': sp['samvat']['display'],
                       'note': note_text('samvat_note', lang)},
            'gotra': ({'title': i18n.SL('gotra_section', lang), 'rows': gotra_rows(sp['gotra'], lang),
                       'note': note_text('lineage_note', lang)} if sp.get('gotra') else None)}


def match_block(boy_gotra, girl_gotra):
    """The block added to a match result: the two gotras (or None) and whether they are the same."""
    return {'boy': boy_gotra, 'girl': girl_gotra, 'same': same_gotra(boy_gotra, girl_gotra)}


def match_view(block, lang):
    """
    What the Marriage pages show: the gotra section (None when neither gotra
    is given) and the Arundhati note (always).
    """
    gotra = None
    if block and (block.get('boy') or block.get('girl')):
        ML = lambda k: i18n.SL(k, lang)
        rows = []
        for role in ('boy', 'girl'):
            g = block.get(role)
            if g:
                rows += [(f"{ML(role)}: {label}", value) for label, value in gotra_rows(g, lang)]
            else:
                rows.append((f"{ML(role)}: {i18n.SL('gotra', lang)}", i18n.SL('not_given', lang)))
        if block.get('same') is not None:
            rows.append((i18n.SL('same_gotra', lang), i18n.SL('yes' if block['same'] else 'no', lang)))
        gotra = {'title': i18n.SL('gotra_section', lang), 'rows': rows,
                 'note': f"{note_text('info_only', lang)}\n{note_text('lineage_note', lang)}"}
    return {'gotra': gotra,
            'arundhati': {'title': i18n.SL('arundhati_title', lang), 'text': note_text('arundhati_text', lang)}}
