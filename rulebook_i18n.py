"""
rulebook_i18n.py — the rule-book findings in the report language.

rulebook.py builds each finding as an English sentence (that is what the
AI_RuleBook sheet and /api/predictions keep). For the reader-facing reports,
translate(finding, rule_id, lang, planet) turns it into the report language:

  * a finding made of lines from the rule data files (K12, 2L, 12L) is split
    at '; ' and every line is looked up in 'lines' of the language file;
  * any other finding is matched against the English patterns of
    data/rulebook/i18n/catalog.json; the slots it holds (planets, houses,
    dates, a few fixed phrases) are carried over in the report language.

Returns None when the finding has no translation (a new rule or a changed
sentence), so the caller can fall back to English and a test can catch it.
filter_lines() drops the lines a report must not show (health, banned words).
"""
import json
import os
import re

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'rulebook', 'i18n')

PLANET_SLOTS = ('p', 'n', 'st', 'd')
LIST_SLOTS = ('names', 'hidden')
KEEP_SLOTS = ('h', 'houses', 'start', 'end')
PHRASE_SLOTS = {'areas': 'areas.', 'quick': 'quick', 'extra_jup': 'extra_jup', 'extra_node': 'extra_node',
                'why': 'why.', 'fields': 'fields.', 'dig': 'dig.'}
OPTIONAL = ('quick', 'extra_jup', 'extra_node')          # phrases that may be empty
SLOT = re.compile(r'\{(\w+)\}')

_CACHE = {}


def _load(name):
    if name not in _CACHE:
        path = os.path.join(DIR, f'{name}.json')
        if not os.path.exists(path):
            _CACHE[name] = None
        else:
            with open(path, encoding='utf-8') as f:
                _CACHE[name] = json.load(f)
    return _CACHE[name]


def catalog():
    return _load('catalog')


def languages():
    return sorted(n[:-5] for n in os.listdir(DIR) if n.endswith('.json') and n != 'catalog.json')


def _phrase_values(slot):
    """The English values a phrase slot can take: {english text: phrase key}."""
    prefix = PHRASE_SLOTS[slot]
    out = {}
    for key, text in catalog()['phrases'].items():
        if key == prefix or (prefix.endswith('.') and key.startswith(prefix)):
            out[text] = key
    return out


_COMPILED = None


def _compiled():
    """[(id, regex)] for every pattern, most specific (longest) first."""
    global _COMPILED
    if _COMPILED is None:
        items = []
        for pid, pattern in catalog()['patterns'].items():
            seen, parts, pos = set(), [], 0
            for m in SLOT.finditer(pattern):
                parts.append(re.escape(pattern[pos:m.start()]))
                slot = m.group(1)
                if slot in seen:
                    parts.append(f'(?P={slot})')
                elif slot in PHRASE_SLOTS:
                    alts = sorted(_phrase_values(slot), key=len, reverse=True)
                    alts = [re.escape(a) for a in alts] + ([''] if slot in OPTIONAL else [])
                    parts.append(f'(?P<{slot}>' + '|'.join(alts) + ')')
                else:
                    parts.append(f'(?P<{slot}>.+?)')
                seen.add(slot)
                pos = m.end()
            parts.append(re.escape(pattern[pos:]))
            items.append((pid, re.compile('^' + ''.join(parts) + '$', re.S), len(pattern)))
        items.sort(key=lambda x: -x[2])
        _COMPILED = [(pid, rx) for pid, rx, _ in items]
    return _COMPILED


def match(finding):
    """(pattern id, slot values) of an English finding, or (None, None)."""
    for pid, rx in _compiled():
        m = rx.match(finding)
        if m:
            return pid, m.groupdict()
    return None, None


def is_line_rule(rule_id):
    return rule_id in catalog()['line_rules']


def _known_lines():
    """The English data-file lines (a line may itself hold '; ')."""
    if '_lines' not in _CACHE:
        known = set()
        for lang in languages():
            known.update((_load(lang) or {}).get('lines', {}))
        _CACHE['_lines'] = known
    return _CACHE['_lines']


def split_lines(finding):
    """The data-file lines a finding is made of: parts split at '; ', joined back
    greedily (longest first) where several parts form one known line."""
    text = finding[:-1] if finding.endswith('.') else finding
    parts = [x.strip() for x in text.split('; ') if x.strip()]
    known = _known_lines()
    out, i = [], 0
    while i < len(parts):
        for j in range(len(parts), i, -1):
            cand = '; '.join(parts[i:j])
            if cand in known or j == i + 1:
                out.append(cand)
                i = j
                break
    return out


def filter_lines(lines, *patterns):
    """Lines that none of the regexes match."""
    return [x for x in lines if not any(p.search(x) for p in patterns)]


def _slot(slot, value, data, planet):
    if slot in PLANET_SLOTS:
        return planet(value)
    if slot in LIST_SLOTS:
        return ', '.join(planet(x.strip()) for x in value.split(','))
    if slot in KEEP_SLOTS:
        return value
    if slot == 'exc':
        out = []
        for part in value.split('; '):
            m = re.match(r'^(\w+) is retrograde$', part)
            if m:
                out.append(data['phrases']['exc.retro'].format(p=planet(m.group(1))))
            elif part == catalog()['phrases']['exc.dispositor']:
                out.append(data['phrases']['exc.dispositor'])
            else:
                return None
        return '; '.join(out)
    if slot in PHRASE_SLOTS:
        if value == '':
            return ''
        key = _phrase_values(slot).get(value)
        return data['phrases'].get(key) if key else None
    return None


def translate(finding, rule_id, lang, planet, drop=()):
    """
    The finding in language lang, or None when there is no translation.
    planet: function giving a planet's name in the report language.
    drop: regexes; data-file lines matching any are left out (in every language).
    """
    if is_line_rule(rule_id):
        lines = filter_lines(split_lines(finding), *drop)
        if not lines:
            return ''
        if lang == 'en':
            return '; '.join(lines) + '.'
        data = _load(lang)
        if not data:
            return None
        out = [data['lines'].get(x) for x in lines]
        if any(x is None for x in out):
            return None
        return '; '.join(out) + data.get('stop', '.')
    if lang == 'en':
        return finding
    data = _load(lang)
    pid, slots = match(finding)
    if not data or pid is None or pid not in data['patterns']:
        return None
    values = {}
    for slot, value in slots.items():
        v = _slot(slot, value, data, planet)
        if v is None:
            return None
        values[slot] = v
    return data['patterns'][pid].format(**values)
