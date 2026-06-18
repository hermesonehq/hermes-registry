"""FMP /stable migration: sector screener uses /stable/company-screener.

fetch_sector_stocks() used v3 /stock-screener (403 for keys issued after
2025-08-31). It now calls /stable/company-screener first with a v3 fallback;
both take the same params and field names, so extraction is unchanged.
"""

from unittest.mock import MagicMock, patch

import pytest

# find_pairs imports statsmodels at module load (used elsewhere in the module,
# not by fetch_sector_stocks). statsmodels is not a declared project dependency,
# so skip cleanly when it's unavailable rather than failing collection.
pytest.importorskip("statsmodels")

import find_pairs  # noqa: E402


def _resp(status_code, payload):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    return resp


@patch("find_pairs.requests.get")
def test_uses_stable_company_screener_first(mock_get):
    mock_get.return_value = _resp(
        200,
        [
            {
                "symbol": "NVDA",
                "companyName": "NVIDIA Corporation",
                "marketCap": 5_343_290_069_887,
                "sector": "Technology",
                "exchangeShortName": "NASDAQ",
                "isActivelyTrading": True,
            }
        ],
    )
    stocks = find_pairs.fetch_sector_stocks("Technology", "key")

    assert stocks[0]["symbol"] == "NVDA"
    assert stocks[0]["name"] == "NVIDIA Corporation"
    assert stocks[0]["exchange"] == "NASDAQ"
    assert stocks[0]["marketCap"] == 5_343_290_069_887

    call = mock_get.call_args_list[0]
    assert call[0][0].endswith("/stable/company-screener")
    assert call[1]["params"]["sector"] == "Technology"
    assert call[1]["params"]["marketCapMoreThan"] == 2_000_000_000


@patch("find_pairs.requests.get")
def test_falls_back_to_v3_stock_screener(mock_get):
    def fake_get(url, params=None, headers=None, timeout=None):
        if url.endswith("/stable/company-screener"):
            return _resp(403, {})  # legacy/stable failure -> fallback
        return _resp(
            200,
            [{"symbol": "AAPL", "companyName": "Apple", "isActivelyTrading": True}],
        )

    mock_get.side_effect = fake_get
    stocks = find_pairs.fetch_sector_stocks("Technology", "key")
    assert stocks[0]["symbol"] == "AAPL"
    urls = [c[0][0] for c in mock_get.call_args_list]
    assert any(u.endswith("/api/v3/stock-screener") for u in urls)


@patch("find_pairs.requests.get")
def test_filters_inactive_symbols(mock_get):
    mock_get.return_value = _resp(
        200,
        [
            {"symbol": "ACTIVE", "isActivelyTrading": True},
            {"symbol": "DELISTED", "isActivelyTrading": False},
        ],
    )
    stocks = find_pairs.fetch_sector_stocks("Technology", "key")
    assert [s["symbol"] for s in stocks] == ["ACTIVE"]
