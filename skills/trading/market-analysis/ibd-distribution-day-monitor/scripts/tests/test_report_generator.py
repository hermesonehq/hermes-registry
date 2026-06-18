"""Tests for report_generator (UTF-8 + redaction H4)."""

import json

from report_generator import REDACTED, _redact, write_json, write_markdown


class TestRedaction:
    def test_redacts_api_key(self):
        out = _redact({"api_key": "sk-12345", "x": 1})  # pragma: allowlist secret
        assert out["api_key"] == REDACTED
        assert out["x"] == 1

    def test_redacts_fmp_api_key_case_insensitive(self):
        # H4: lowercase comparison must catch UPPER and Mixed cases
        out = _redact({"FMP_API_KEY": "real-key", "Fmp_Api_Key": "real-key"})
        assert out["FMP_API_KEY"] == REDACTED
        assert out["Fmp_Api_Key"] == REDACTED

    def test_redacts_token_case_insensitive(self):
        out = _redact({"Access_Token": "abc", "REFRESH_TOKEN": "def"})
        assert out["Access_Token"] == REDACTED
        assert out["REFRESH_TOKEN"] == REDACTED

    def test_redacts_nested_config_api_key(self):
        out = _redact({"data": {"api_key": "secret", "provider": "fmp"}})
        assert out["data"]["api_key"] == REDACTED
        assert out["data"]["provider"] == "fmp"

    def test_passthrough_non_sensitive(self):
        payload = {"market_distribution_state": {"overall_risk_level": "HIGH"}}
        assert _redact(payload) == payload

    def test_redacts_inside_lists(self):
        out = _redact({"items": [{"api_key": "x"}, {"name": "y"}]})
        assert out["items"][0]["api_key"] == REDACTED
        assert out["items"][1]["name"] == "y"


class TestWriteOutputs:
    def test_json_writes_utf8_with_ensure_ascii_false(self, tmp_path):
        path = tmp_path / "out.json"
        payload = {
            "explanation": "QQQは本日Distribution Day。HIGH判定。",
            "data": {"api_key": "sk-secret"},  # pragma: allowlist secret
        }
        write_json(payload, path)
        text = path.read_text(encoding="utf-8")
        # Japanese must be present in raw form (not \u escape)
        assert "QQQは本日" in text
        # API key must be redacted
        assert "sk-secret" not in text
        loaded = json.loads(text)
        assert loaded["data"]["api_key"] == REDACTED

    def test_markdown_writes_utf8(self, tmp_path):
        path = tmp_path / "out.md"
        payload = {
            "market_distribution_state": {
                "as_of": "2026-04-30",
                "overall_risk_level": "HIGH",
                "primary_signal_symbol": "QQQ",
                "index_results": [],
            },
            "portfolio_action": {
                "instrument": "TQQQ",
                "recommended_action": "REDUCE_EXPOSURE",
                "current_exposure_pct": 100,
                "target_exposure_pct": 50,
                "exposure_delta_pct": -50,
                "trailing_stop_pct": 5,
                "alternative_action": None,
                "rationale": "TQQQはレバレッジETF。",
            },
            "audit": {"data_source": "fmp", "audit_flags": []},
        }
        write_markdown(payload, path)
        text = path.read_text(encoding="utf-8")
        assert "TQQQはレバレッジETF" in text
        assert "HIGH" in text
