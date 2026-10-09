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
