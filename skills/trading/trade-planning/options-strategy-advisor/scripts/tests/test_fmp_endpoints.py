"""FMP /stable migration: live quote + dividend-yield helpers.

get_current_stock_price and get_dividend_yield used v3 path-style endpoints
(/quote/SYM, /profile/SYM) that 403 for keys issued after 2025-08-31. They now
call the /stable query-style endpoints first, with a v3 fallback. /stable also
renamed the dividend field lastDiv -> lastDividend, which get_dividend_yield
must read or it silently returns 0.
"""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from black_scholes import get_current_stock_price, get_dividend_yield


def _resp(status_code, json_payload):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_payload
    return resp


class TestCurrentStockPrice:
    @patch("black_scholes.requests")
    def test_uses_stable_quote_first(self, mock_requests):
        mock_requests.get.return_value = _resp(200, [{"symbol": "AAPL", "price": 150.0}])
        price = get_current_stock_price("AAPL", "key")
        assert price == 150.0
        call = mock_requests.get.call_args
        assert call[0][0].endswith("/stable/quote")
        assert call[1]["params"] == {"symbol": "AAPL"}

    @patch("black_scholes.requests")
    def test_falls_back_to_v3(self, mock_requests):
        def fake_get(url, headers=None, params=None, timeout=None):
            if url.endswith("/stable/quote"):
                return _resp(403, {})  # legacy/stable failure -> fallback
            return _resp(200, [{"symbol": "AAPL", "price": 150.0}])

        mock_requests.get.side_effect = fake_get
        price = get_current_stock_price("AAPL", "key")
        assert price == 150.0
        urls = [c[0][0] for c in mock_requests.get.call_args_list]
        assert any(u.endswith("/api/v3/quote/AAPL") for u in urls)


class TestDividendYield:
    @patch("black_scholes.requests")
    def test_reads_stable_lastDividend_field(self, mock_requests):
        # /stable/profile uses lastDividend (no lastDiv). Yield = 2.0 / 100.
        mock_requests.get.return_value = _resp(
            200, [{"symbol": "AAPL", "lastDividend": 2.0, "price": 100.0}]
        )
        assert get_dividend_yield("AAPL", "key") == 0.02
        call = mock_requests.get.call_args
        assert call[0][0].endswith("/stable/profile")
        assert call[1]["params"] == {"symbol": "AAPL"}

    @patch("black_scholes.requests")
    def test_v3_lastDiv_still_supported(self, mock_requests):
        def fake_get(url, headers=None, params=None, timeout=None):
            if url.endswith("/stable/profile"):
                return _resp(403, {})
            return _resp(200, [{"symbol": "AAPL", "lastDiv": 4.0, "price": 100.0}])

        mock_requests.get.side_effect = fake_get
        assert get_dividend_yield("AAPL", "key") == 0.04

    @patch("black_scholes.requests")
    def test_zero_when_no_data(self, mock_requests):
        mock_requests.get.return_value = _resp(200, [])
        assert get_dividend_yield("AAPL", "key") == 0
