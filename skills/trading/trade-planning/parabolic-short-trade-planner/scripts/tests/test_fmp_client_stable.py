"""Regression tests for the FMP ``/stable`` endpoint migration (Issue #162).

The v3→/stable sweep routed three ``fmp_client.py`` methods through
``_fmp_compat.v3_to_stable()``, which passes unknown endpoint names through
verbatim. Two endpoints were renamed between v3 and /stable, so the rewritten
URLs 404; a third method dropped the ``mktCap`` alias its consumer still reads.
These tests pin the corrected behaviour:

- ``/stable/sp500-constituent`` (not ``sp500_constituent``)
- ``/stable/earnings-calendar`` (not ``earning_calendar``)
- ``get_company_profile`` re-aliases ``marketCap`` → ``mktCap``

Offline: the network boundary (``_rate_limited_get``) is mocked.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import _fmp_compat  # noqa: E402
from fmp_client import FMPClient  # noqa: E402

_V3 = "https://financialmodelingprep.com/api/v3"


def _call_url_params(mock: MagicMock) -> tuple[str, dict | None]:
    """Extract (url, params) from a _rate_limited_get mock call, tolerating
    both positional and keyword ``params`` call styles."""
    call = mock.call_args
    url = call.args[0]
    if len(call.args) > 1:
        params = call.args[1]
    else:
        params = call.kwargs.get("params")
    return url, params


# --- v3_to_stable URL mapping (pure function) ---------------------------------


def test_v3_to_stable_sp500_constituent_uses_hyphen() -> None:
    url, params = _fmp_compat.v3_to_stable(f"{_V3}/sp500_constituent")
    assert url == "https://financialmodelingprep.com/stable/sp500-constituent"
    assert "sp500_constituent" not in url
    assert params == {}


def test_v3_to_stable_earning_calendar_uses_hyphen_and_preserves_params() -> None:
    url, params = _fmp_compat.v3_to_stable(
        f"{_V3}/earning_calendar", {"from": "2026-05-20", "to": "2026-06-15"}
    )
    assert url == "https://financialmodelingprep.com/stable/earnings-calendar"
    assert "earning_calendar" not in url
    assert params == {"from": "2026-05-20", "to": "2026-06-15"}


# --- Client methods build the corrected URLs ----------------------------------


def test_get_sp500_constituents_requests_hyphenated_url() -> None:
    client = FMPClient(api_key="test-key")
    client._rate_limited_get = MagicMock(return_value=[{"symbol": "AAPL"}])

    client.get_sp500_constituents()

    url, _ = _call_url_params(client._rate_limited_get)
    assert url == "https://financialmodelingprep.com/stable/sp500-constituent"


def test_get_earnings_calendar_requests_hyphenated_url_with_dates() -> None:
    client = FMPClient(api_key="test-key")
    client._rate_limited_get = MagicMock(return_value=[{"symbol": "AAPL"}])

    client.get_earnings_calendar("2026-05-20", "2026-06-15")

    url, params = _call_url_params(client._rate_limited_get)
    assert url == "https://financialmodelingprep.com/stable/earnings-calendar"
    assert params == {"from": "2026-05-20", "to": "2026-06-15"}


# --- Profile alias ------------------------------------------------------------


def test_get_company_profile_aliases_market_cap() -> None:
    client = FMPClient(api_key="test-key")
    # /stable/profile returns ``marketCap`` (no ``mktCap``).
    client._rate_limited_get = MagicMock(
        return_value=[{"symbol": "AAPL", "marketCap": 4_000_000_000_000}]
    )

    profile = client.get_company_profile("AAPL")

    assert profile is not None
    assert profile["mktCap"] == 4_000_000_000_000
    # The original key remains intact.
    assert profile["marketCap"] == 4_000_000_000_000


def test_get_company_profile_keeps_existing_mktcap() -> None:
    client = FMPClient(api_key="test-key")
    # If a row already carries ``mktCap`` it must not be overwritten.
    client._rate_limited_get = MagicMock(
        return_value=[{"symbol": "AAPL", "mktCap": 123, "marketCap": 456}]
    )

    profile = client.get_company_profile("AAPL")

    assert profile is not None
    assert profile["mktCap"] == 123
