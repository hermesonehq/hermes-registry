"""Tests for check_live_apis.py — focused on the --fmp-only path
and the missing-Alpaca SKIP behaviour added to address the runbook
gap surfaced during the live smoke run.

Network is mocked at the requests.get level so these stay offline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import check_live_apis as cla


def _fmp_historical_response() -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [
        {
            "date": "2026-05-01",
            "open": 1.0,
            "high": 1.1,
            "low": 0.9,
            "close": 1.0,
            "volume": 1000,
        }
    ]
    resp.raise_for_status = MagicMock()
    return resp


def _fmp_profile_response() -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"symbol": "AAPL", "mktCap": 4_000_000_000_000}]
    resp.raise_for_status = MagicMock()
    return resp


def _fmp_sp500_response() -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = [{"symbol": "AAPL"}, {"symbol": "MSFT"}]
    resp.raise_for_status = MagicMock()
    return resp


def _route_get(url: str, **_kwargs):
    """Dispatch mocked GET responses by URL substring."""
    if "historical-price-eod/full" in url:
        return _fmp_historical_response()
    if "/stable/profile" in url or "/profile/" in url:
        return _fmp_profile_response()
    if "sp500-constituent" in url or "/sp500_constituent" in url:
        return _fmp_sp500_response()
    raise AssertionError(f"Unexpected GET to {url!r} in --fmp-only mode")


@pytest.fixture
def fmp_only_env(monkeypatch):
    monkeypatch.setenv("FMP_API_KEY", "fmp-test-key")  # pragma: allowlist secret
    monkeypatch.delenv("ALPACA_API_KEY", raising=False)
    monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)


@pytest.fixture
def full_env(monkeypatch):
    monkeypatch.setenv("FMP_API_KEY", "fmp-test-key")  # pragma: allowlist secret
    monkeypatch.setenv("ALPACA_API_KEY", "alp-test-key")  # pragma: allowlist secret
    monkeypatch.setenv("ALPACA_SECRET_KEY", "alp-test-secret")  # pragma: allowlist secret
    monkeypatch.setenv("ALPACA_PAPER", "true")


class TestFmpOnlyFlag:
    def test_fmp_only_exits_zero_on_fmp_pass(self, fmp_only_env, capsys):
        with patch("requests.get", side_effect=_route_get):
            rc = cla.main(["--fmp-only"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Mode: --fmp-only" in out
        assert "PASS fmp.historical_price_eod_full" in out
        assert "PASS fmp.profile" in out
        assert "SKIP alpaca.assets_aapl — explicitly skipped via --fmp-only" in out
        assert "SKIP alpaca.assets_404_graceful — explicitly skipped via --fmp-only" in out
        # No raw FAIL setup line — that was the old behaviour.
        assert "FAIL setup" not in out

    def test_fmp_only_does_not_call_alpaca(self, fmp_only_env):
        with patch("requests.get", side_effect=_route_get) as get:
            cla.main(["--fmp-only"])
        called_urls = [c.args[0] for c in get.call_args_list]
        assert all("alpaca.markets" not in u for u in called_urls), called_urls


class TestImplicitFmpOnlyWhenAlpacaMissing:
    """Without --fmp-only and without Alpaca creds, the script should
    still run FMP gates and emit SKIP for Alpaca, plus a hint to add
    --fmp-only or set the env vars. Exit 0 when FMP gates pass."""

    def test_no_alpaca_creds_skips_alpaca_and_passes(self, fmp_only_env, capsys):
        with patch("requests.get", side_effect=_route_get):
            rc = cla.main([])
        assert rc == 0
        out = capsys.readouterr().out
        # FMP runs to completion
        assert "PASS fmp.historical_price_eod_full" in out
        # Alpaca gates marked SKIP with the env-var-missing reason
        assert "SKIP alpaca.assets_aapl — ALPACA_API_KEY" in out
        # Hint nudges the user to choose --fmp-only or configure Alpaca
        assert "--fmp-only" in out


class TestFullModePathStillFails:
    """Sanity: when both keys are set but Alpaca raises, the required
    gate still gates the exit code. Regression test against accidentally
    making Alpaca optional in the full path."""

    def test_full_mode_alpaca_failure_returns_nonzero(self, full_env):
        def router(url: str, **_kwargs):
            if "data.alpaca.markets" in url or "paper-api.alpaca.markets" in url:
                resp = MagicMock()
                resp.status_code = 500
                resp.text = "boom"
                resp.raise_for_status.side_effect = RuntimeError("HTTP 500")
                return resp
            return _route_get(url)

        with patch("requests.get", side_effect=router):
            rc = cla.main([])
        assert rc != 0


class TestMissingFmpStillFails:
    def test_missing_fmp_returns_nonzero(self, monkeypatch, capsys):
        monkeypatch.delenv("FMP_API_KEY", raising=False)
        rc = cla.main([])
        assert rc == 1
        assert "FAIL setup — FMP_API_KEY" in capsys.readouterr().out
