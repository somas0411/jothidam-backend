"""
Shared test setup.

The suite calls the routes far more often than a visitor may, so the request
limits are switched off for every test. tests/test_protection.py switches them
on again for the tests that are about the limits.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def _request_limits_off():
    import app as app_module
    before = app_module.limiter.enabled
    app_module.limiter.enabled = False
    yield
    app_module.limiter.enabled = before



# The AI_ sheets are off by default (AI_TABS_ENABLED, features.py). These
# modules test that kept code path, so they run with the switch on (set for
# the whole module, as their module-scoped fixtures build workbooks). The
# default (off) is tested in tests/test_ai_off.py.
AI_ON_MODULES = {'test_enrich', 'test_reader', 'test_match', 'test_family', 'test_family_relations',
                 'test_predictions', 'test_protection'}


@pytest.fixture(scope='module', autouse=True)
def _ai_tabs_for_ai_tests(request):
    import os
    on = request.module.__name__.split('.')[-1] in AI_ON_MODULES
    before = os.environ.get('AI_TABS_ENABLED')
    os.environ['AI_TABS_ENABLED'] = 'true' if on else 'false'
    os.environ.pop('PAYMENTS_ENABLED', None)
    yield
    if before is None:
        os.environ.pop('AI_TABS_ENABLED', None)
    else:
        os.environ['AI_TABS_ENABLED'] = before
