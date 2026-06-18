"""FMP /stable migration: stock list uses /stable/company-screener.

fetch_stock_list() used v3 /stock-screener (403 for keys issued after
2025-08-31). It now calls /stable/company-screener first with a v3 fallback;
both take the same params and return the same fields.
"""

from unittest.mock import MagicMock, patch

import analyze_downtrends


def _resp(status_code, payload):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    return resp


@patch("analyze_downtrends.requests.get")
def test_uses_stable_company_screener_first(mock_get):
    mock_get.return_value = _resp(
        200, [{"symbol": "XOM", "sector": "Energy", "marketCap": 500_000_000_000}]
    )
    stocks = analyze_downtrends.fetch_stock_list("key", sector="Energy")

    assert stocks[0]["symbol"] == "XOM"
    call = mock_get.call_args_list[0]
    assert call[0][0].endswith("/stable/company-screener")
    assert call[1]["params"]["sector"] == "Energy"
    assert call[1]["params"]["isActivelyTrading"] == "true"
    assert call[1]["params"]["limit"] == 500


@patch("analyze_downtrends.requests.get")
def test_falls_back_to_v3_stock_screener(mock_get):
    def fake_get(url, params=None, timeout=None):
        if url.endswith("/stable/company-screener"):
            return _resp(403, {})  # legacy/stable failure -> fallback
        return _resp(200, [{"symbol": "AAPL", "sector": "Technology"}])

    mock_get.side_effect = fake_get
    stocks = analyze_downtrends.fetch_stock_list("key")
    assert stocks[0]["symbol"] == "AAPL"
    urls = [c[0][0] for c in mock_get.call_args_list]
    assert any(u.endswith("/api/v3/stock-screener") for u in urls)


@patch("analyze_downtrends.requests.get")
def test_returns_empty_when_all_fail(mock_get):
    mock_get.return_value = _resp(403, {})
    assert analyze_downtrends.fetch_stock_list("key") == []
