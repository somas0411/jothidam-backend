"""
features.py — on/off switches read from the environment.

AI_TABS_ENABLED (default false)
    false: no AI_ sheet is written to any workbook, the Notes sheet says
           nothing about AI sheets, and /api/download/json answers 404.
    true:  the AI_ sheets come back exactly as before.

Products (used when payments are on, see payments.py):
    basic  ₹200: summary, Vedic, KP, ALP and Dasa (PDF + Excel)
    full   ₹500: basic + divisional charts, Notes (குறிப்புகள்) and
           Predictions (பலன்கள், with KP event timing)
    match  ₹200: the marriage match report
    family ₹500: the family reading report
"""
import os

PRODUCTS = ('basic', 'full', 'match', 'family')
HOROSCOPE_PRODUCTS = ('basic', 'full')


def _flag(name, default=False):
    text = str(os.environ.get(name, '')).strip().lower()
    if text in ('1', 'true', 'yes', 'on'):
        return True
    if text in ('0', 'false', 'no', 'off'):
        return False
    return default


def ai_tabs():
    return _flag('AI_TABS_ENABLED', False)


def payments_enabled():
    return _flag('PAYMENTS_ENABLED', False)


def price_paise(product):
    defaults = {'basic': 20000, 'full': 50000, 'match': 20000, 'family': 50000}
    raw = os.environ.get(f'PRICE_{product.upper()}_PAISE', '')
    try:
        value = int(raw)
        return value if value >= 100 else defaults[product]
    except (TypeError, ValueError):
        return defaults[product]
