"""Tests for risk_classifier (M11 / M12)."""

import pytest
from models import IndexResult, RiskThresholds
from risk_classifier import classify_risk, combine_index_risks


def _idx(symbol: str, level: str):
    return IndexResult(
        symbol=symbol,
        benchmark_name=f"{symbol} Proxy",
        is_distribution_day_today=False,
        today={},
        d5_count=0,
        d15_count=0,
        d25_count=0,
        active_distribution_days=[],
        removed_distribution_days=[],
        risk_level=level,
        cluster_state={},
        trend_filters={},
        explanation="",
    )


class TestClassifyRisk:
    @pytest.fixture
    def t(self):
        return RiskThresholds()

    def test_normal_when_d25_2(self, t):
        assert classify_risk(0, 0, 2, False, t) == "NORMAL"

    def test_caution_when_d25_3(self, t):
        assert classify_risk(0, 0, 3, False, t) == "CAUTION"

    def test_high_when_d25_5(self, t):
        assert classify_risk(0, 0, 5, False, t) == "HIGH"

    def test_high_when_d15_3(self, t):
        assert classify_risk(0, 3, 3, False, t) == "HIGH"

    def test_high_when_d5_2(self, t):
        assert classify_risk(2, 2, 3, False, t) == "HIGH"

    def test_severe_when_d25_6(self, t):
        assert classify_risk(0, 0, 6, False, t) == "SEVERE"

    def test_severe_when_d15_4(self, t):
        assert classify_risk(0, 4, 5, False, t) == "SEVERE"

    def test_severe_when_market_below_ma_and_d25_5(self, t):
        assert classify_risk(0, 0, 5, True, t) == "SEVERE"

    def test_market_below_ma_none_does_not_force_severe(self, t):
        # None must not be treated as True
        assert classify_risk(0, 0, 5, None, t) == "HIGH"


class TestCombineIndexRisks:
    def test_severe_takes_precedence(self):
        results = [_idx("QQQ", "NORMAL"), _idx("SPY", "SEVERE")]
        assert combine_index_risks(results) == "SEVERE"

    def test_qqq_high_returns_high(self):
        results = [_idx("QQQ", "HIGH"), _idx("SPY", "NORMAL")]
        assert combine_index_risks(results) == "HIGH"

    def test_qqq_caution_spy_high_returns_high(self):
        results = [_idx("QQQ", "CAUTION"), _idx("SPY", "HIGH")]
        assert combine_index_risks(results) == "HIGH"

    def test_qqq_caution_spy_caution_returns_high(self):
        results = [_idx("QQQ", "CAUTION"), _idx("SPY", "CAUTION")]
        assert combine_index_risks(results) == "HIGH"

    def test_qqq_normal_spy_high_returns_high(self):
        # M12: broad-market degradation can spill into TQQQ
        results = [_idx("QQQ", "NORMAL"), _idx("SPY", "HIGH")]
        assert combine_index_risks(results) == "HIGH"

    def test_max_fallback_when_no_special_case(self):
        results = [_idx("QQQ", "NORMAL"), _idx("SPY", "CAUTION")]
        assert combine_index_risks(results) == "CAUTION"

    def test_all_normal_returns_normal(self):
        results = [_idx("QQQ", "NORMAL"), _idx("SPY", "NORMAL")]
        assert combine_index_risks(results) == "NORMAL"
