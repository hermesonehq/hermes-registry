"""FMP /stable migration for canslim-screener.

Keys issued after 2025-08-31 lose v3 access (403). Three FMP calls are migrated
(stable-first, v3 fallback):
- get_income_statement: /income-statement/{sym} -> /stable/income-statement?symbol=&period=
- get_profile: /profile/{sym} -> /stable/profile?symbol= (+ mktCap alias)
- get_institutional_holders: /institutional-holder/{sym} (full list) ->
  /stable institutional-ownership summary (count + ownership%) + top-holders
  page (superinvestor names), returned as an aggregate dict.
"""

import os
from datetime import date
from unittest.mock import MagicMock, patch


def _make_client():
    with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):  # pragma: allowlist secret
        from fmp_client import FMPClient

        client = FMPClient(api_key="test_key")
    client.RATE_LIMIT_DELAY = 0  # no sleep in tests
    return client


def _resp(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.text = ""
    return resp


class TestIncomeStatementProfile:
    def test_income_statement_uses_stable_query(self):
        client = _make_client()
        captured = {}

        def fake_get(url, params=None, timeout=30):
            captured["url"], captured["params"] = url, params
            return _resp(200, [{"symbol": "AAPL", "period": "Q2", "eps": 2.0}])

        client.session.get = fake_get
        client.get_income_statement("AAPL", period="quarter", limit=8)
        assert captured["url"].endswith("/stable/income-statement")
        assert captured["params"]["symbol"] == "AAPL"
        assert captured["params"]["period"] == "quarter"

    def test_profile_stable_with_mktcap_alias(self):
        client = _make_client()
        # /stable/profile returns marketCap, not mktCap.
        client.session.get = lambda *a, **k: _resp(
            200, [{"symbol": "AAPL", "companyName": "Apple", "marketCap": 4_000_000_000_000}]
        )
        profile = client.get_profile("AAPL")
        assert profile[0]["mktCap"] == 4_000_000_000_000  # aliased for downstream


class TestInstitutionalHolders:
    def test_summary_plus_top_holders(self):
        def fake_get(url, params=None, timeout=30):
            if "symbol-positions-summary" in url:
                return _resp(200, [{"investorsHolding": 6170, "ownershipPercent": 61.6}])
            if "extract-analytics/holder" in url:
                return _resp(
                    200,
                    [
                        {
                            "investorName": "VANGUARD GROUP INC",
                            "sharesNumber": 100,
                            "changeInSharesNumber": 5,
                        },
                        {
                            "investorName": "BLACKROCK, INC.",
                            "sharesNumber": 90,
                            "changeInSharesNumber": -2,
                        },
                    ],
                )
            raise AssertionError(f"unexpected {url}")

        client = _make_client()
        client.session.get = fake_get
        result = client.get_institutional_holders("AAPL")
        assert result["num_holders"] == 6170
        assert result["ownership_pct"] == 61.6
        assert result["top_holders"][0] == {
            "holder": "VANGUARD GROUP INC",
            "shares": 100,
            "change": 5,
        }

    def test_v3_fallback_when_stable_empty(self):
        def fake_get(url, params=None, timeout=30):
            if "/stable/" in url:
                return _resp(200, [])  # no stable 13F data for any quarter
            # v3 institutional-holder full list
            return _resp(200, [{"holder": "Vanguard", "shares": 100, "change": 1}] * 75)

        client = _make_client()
        client.session.get = fake_get
        result = client.get_institutional_holders("AAPL")
        assert result["num_holders"] == 75  # len of the v3 list
        assert result["ownership_pct"] is None  # calculator derives it

    def test_recent_13f_quarters_walk_back(self):
        from fmp_client import FMPClient

        # May 2026 -> most recent completed quarter is Q1 2026, then walk back.
        quarters = list(FMPClient._recent_13f_quarters(as_of=date(2026, 5, 20), count=3))
        assert quarters == [(2026, 1), (2025, 4), (2025, 3)]


class TestInstitutionalCalculatorDictShape:
    def test_uses_aggregate_count_and_ownership(self):
        from calculators.institutional_calculator import calculate_institutional_sponsorship

        agg = {
            "num_holders": 6170,
            "ownership_pct": 61.6,
            # SUPERINVESTORS are famous active managers (Berkshire, Baupost, ...),
            # not passive index funds, so this name triggers the bonus.
            "top_holders": [
                {"holder": "BLACKROCK, INC.", "shares": 90, "change": 1},
                {"holder": "BERKSHIRE HATHAWAY INC", "shares": 50, "change": 0},
            ],
        }
        result = calculate_institutional_sponsorship(agg, profile={}, use_finviz_fallback=False)
        assert result["num_holders"] == 6170
        assert result["ownership_pct"] == 61.6
        assert result["superinvestor_present"] is True  # matched Berkshire
        assert result["score"] > 0
