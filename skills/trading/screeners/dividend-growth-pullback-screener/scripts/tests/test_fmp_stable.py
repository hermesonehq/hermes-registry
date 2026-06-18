"""FMP /stable migration for dividend-growth-pullback-screener.

Keys issued after 2025-08-31 lose v3 access (403). FMPClient._get now routes
the legacy v3 path-style endpoints to their /stable query-style equivalents
(with a v3 fallback) and normalizes responses to the v3 shapes callers expect:

- historical-price-full/stock_dividend/{sym} -> dividends?symbol= (flat list
  wrapped as {"historical": [...]})
- key-metrics: roe <- returnOnEquity
- cash-flow-statement: dividendsPaid <- netDividendsPaid

get_historical_prices is also fixed to /stable/historical-price-eod/full
(flat-list parsing + from/to bounding) so RSI has data again.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock  # noqa: E402

import screen_dividend_growth_rsi as mod  # noqa: E402
from screen_dividend_growth_rsi import FMPClient  # noqa: E402


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(mod.time, "sleep", lambda *_a, **_k: None)


def _resp(status_code, payload):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    return resp


def _client(router):
    client = FMPClient("test_key")
    session = MagicMock()
    session.get.side_effect = router
    client.session = session
    return client, session


class TestGetRouting:
    def test_statement_path_to_stable_query(self):
        client, session = _client(lambda *a, **k: _resp(200, [{"symbol": "AAPL", "revenue": 1}]))
        client.get_income_statement("AAPL", limit=5)
        call = session.get.call_args_list[0]
        assert call[0][0].endswith("/stable/income-statement")
        assert call[1]["params"]["symbol"] == "AAPL"
        assert call[1]["params"]["limit"] == 5

    def test_screener_to_company_screener(self):
        client, session = _client(lambda *a, **k: _resp(200, [{"symbol": "X"}]))
        client.screen_stocks(min_market_cap=2_000_000_000)
        assert session.get.call_args_list[0][0][0].endswith("/stable/company-screener")

    def test_dividends_normalized_to_historical(self):
        flat = [{"symbol": "KO", "date": "2026-05-11", "dividend": 0.53}]
        client, _ = _client(lambda *a, **k: _resp(200, flat))
        result = client.get_dividend_history("KO")
        assert isinstance(result, dict) and result["historical"] == flat

    def test_key_metrics_roe_alias(self):
        client, _ = _client(lambda *a, **k: _resp(200, [{"returnOnEquity": 1.2}]))
        assert client.get_key_metrics("AAPL", limit=1)[0]["roe"] == 1.2

    def test_cashflow_dividends_paid_alias(self):
        client, _ = _client(lambda *a, **k: _resp(200, [{"netDividendsPaid": -8_000_000}]))
        assert client.get_cash_flow("AAPL", limit=1)[0]["dividendsPaid"] == -8_000_000

    def test_v3_fallback_when_stable_fails(self):
        def router(url, params=None, timeout=None):
            if "/stable/" in url:
                return _resp(403, {})
            return _resp(200, [{"symbol": "AAPL", "sector": "Tech"}])

        client, session = _client(router)
        assert client.get_company_profile("AAPL")["sector"] == "Tech"
        urls = [c[0][0] for c in session.get.call_args_list]
        assert any(u.endswith("/api/v3/profile/AAPL") for u in urls)


class TestHistoricalPrices:
    def test_stable_flat_list_with_from_to(self):
        bars = [{"date": "2026-05-19", "close": 100.0}, {"date": "2026-05-18", "close": 99.0}]

        def router(url, params=None, timeout=None):
            assert url.endswith("/stable/historical-price-eod/full")
            assert "from" in (params or {}) and "to" in (params or {})
            return _resp(200, bars)

        client, _ = _client(router)
        assert client.get_historical_prices("AAPL", days=30) == bars  # flat list, close intact
