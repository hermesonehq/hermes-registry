"""Tests for risk_calculator module."""

import pytest
from risk_calculator import (
    calculate_position_size,
    calculate_r_multiples,
    calculate_risks,
    derive_trade_prices,
    get_rating_band,
    get_sizing_multiplier,
    round_price,
)


class TestRoundPrice:
    def test_above_1_dollar_rounds_to_2_decimals(self):
        assert round_price(150.123) == 150.12

    def test_above_1_dollar_rounds_up(self):
        assert round_price(150.126) == 150.13

    def test_below_1_dollar_rounds_to_4_decimals(self):
        assert round_price(0.12345) == 0.1235

    def test_exactly_1_dollar(self):
        assert round_price(1.0) == 1.0

    def test_boundary_just_below_1(self):
        assert round_price(0.9999) == 0.9999


class TestDeriveTradePrices:
    def test_default_params(self):
        # pivot=100, last_low=95, defaults: buf=0.1%, chase=2.0%, stop_buf=1.0%
        signal, worst, stop = derive_trade_prices(100.0, 95.0)
        assert signal == 100.10  # 100 * 1.001
        assert worst == 102.00  # 100 * 1.02
        assert stop == 94.05  # 95 * 0.99

    def test_custom_params(self):
        signal, worst, stop = derive_trade_prices(
            200.0, 190.0, pivot_buffer_pct=0.2, max_chase_pct=3.0, stop_buffer_pct=2.0
        )
        assert signal == 200.40  # 200 * 1.002
        assert worst == 206.00  # 200 * 1.03
        assert stop == 186.20  # 190 * 0.98

    def test_zero_pivot_raises(self):
        with pytest.raises(ValueError, match="pivot must be positive"):
            derive_trade_prices(0, 95.0)

    def test_zero_low_raises(self):
        with pytest.raises(ValueError, match="last_contraction_low must be positive"):
            derive_trade_prices(100.0, 0)

    def test_stop_above_entry_raises(self):
        # pivot=10, last_low=15 → stop=14.85, signal=10.01 → stop > signal
        with pytest.raises(ValueError, match="stop_loss.*must be below"):
            derive_trade_prices(10.0, 15.0)


class TestCalculateRisks:
    def test_basic_risk_calculation(self):
        signal_risk, worst_risk = calculate_risks(100.10, 102.00, 94.05)
        assert signal_risk == 6.04  # (100.10 - 94.05) / 100.10 * 100
        assert worst_risk == 7.79  # (102.00 - 94.05) / 102.00 * 100

    def test_worst_is_always_larger(self):
        signal_risk, worst_risk = calculate_risks(50.05, 51.00, 47.00)
        assert worst_risk > signal_risk

    def test_both_pass_gate_but_worst_is_tighter(self):
        # last_low=95 -> signal=100.10, worst=102.00, stop=94.05
        # signal_risk=6.04%, worst_risk=7.79% -> both < 8%
        signal, worst, stop = derive_trade_prices(100.0, 95.0)
        signal_risk, worst_risk = calculate_risks(signal, worst, stop)
        assert signal_risk < 8.0
        assert worst_risk < 8.0
        assert worst_risk > signal_risk

    def test_worst_risk_fails_gate(self):
        # pivot=100, last_low=91 -> stop=90.09, worst=102 -> risk=11.68%
        signal, worst, stop = derive_trade_prices(100.0, 91.0)
        _, worst_risk = calculate_risks(signal, worst, stop)
        assert worst_risk > 8.0


class TestCalculateRMultiples:
    def test_default_multiples(self):
        result = calculate_r_multiples(100.0, 95.0)
        # R = 5.0
        assert result["1.0R"] == 105.0
        assert result["2.0R"] == 110.0
        assert result["3.0R"] == 115.0

    def test_custom_multiples(self):
        result = calculate_r_multiples(100.0, 95.0, multiples=(0.5, 1.5))
        assert result["0.5R"] == 102.5
        assert result["1.5R"] == 107.5

    def test_worst_entry_multiples_larger_targets(self):
        # Worst entry is higher, so R is larger, targets are further
        signal_r = calculate_r_multiples(100.10, 94.05)
        worst_r = calculate_r_multiples(102.00, 94.05)
        assert worst_r["2.0R"] > signal_r["2.0R"]


class TestGetRatingBand:
    def test_textbook(self):
        assert get_rating_band(92.5) == "textbook"
        assert get_rating_band(90.0) == "textbook"

    def test_strong(self):
        assert get_rating_band(85.0) == "strong"
        assert get_rating_band(80.0) == "strong"

    def test_good(self):
        assert get_rating_band(75.0) == "good"
        assert get_rating_band(70.0) == "good"

    def test_developing(self):
        assert get_rating_band(65.0) == "developing"
        assert get_rating_band(60.0) == "developing"

    def test_weak(self):
        assert get_rating_band(50.0) == "weak"
        assert get_rating_band(0.0) == "weak"


class TestGetSizingMultiplier:
    def test_textbook_175(self):
        assert get_sizing_multiplier("textbook") == 1.75

    def test_strong_100(self):
        assert get_sizing_multiplier("strong") == 1.0

    def test_good_075(self):
        assert get_sizing_multiplier("good") == 0.75

    def test_developing_zero(self):
        assert get_sizing_multiplier("developing") == 0.0

    def test_unknown_zero(self):
        assert get_sizing_multiplier("unknown") == 0.0


class TestCalculatePositionSize:
    def test_basic_sizing(self):
        result = calculate_position_size(
            worst_entry=102.00,
            stop_loss=94.05,
            account_size=100_000,
            base_risk_pct=0.5,
            sizing_multiplier=1.0,
        )
        # effective_risk = 0.5%, dollar_risk = 500, risk_per_share = 7.95
        # shares = int(500 / 7.95) = 62
        assert result["shares"] == 62
        assert result["effective_risk_pct"] == 0.5
        assert result["risk_dollars"] > 0
        assert result["position_value"] > 0

    def test_sizing_multiplier_applied(self):
        base = calculate_position_size(
            worst_entry=100.0,
            stop_loss=95.0,
            account_size=100_000,
            base_risk_pct=0.5,
            sizing_multiplier=1.0,
            max_position_pct=100.0,
        )
        textbook = calculate_position_size(
            worst_entry=100.0,
            stop_loss=95.0,
            account_size=100_000,
            base_risk_pct=0.5,
            sizing_multiplier=1.75,
            max_position_pct=100.0,
        )
        assert textbook["shares"] > base["shares"]

    def test_zero_multiplier_returns_zero_shares(self):
        result = calculate_position_size(
            worst_entry=100.0,
            stop_loss=95.0,
            account_size=100_000,
            base_risk_pct=0.5,
            sizing_multiplier=0.0,
        )
        assert result["shares"] == 0
        assert result["binding_constraint"] == "sizing_multiplier_zero"

    def test_sector_constraint_limits_shares(self):
        unconstrained = calculate_position_size(
            worst_entry=100.0,
            stop_loss=95.0,
            account_size=100_000,
            base_risk_pct=1.0,
            sizing_multiplier=1.0,
        )
        constrained = calculate_position_size(
            worst_entry=100.0,
            stop_loss=95.0,
            account_size=100_000,
            base_risk_pct=1.0,
            sizing_multiplier=1.0,
            max_sector_pct=5.0,
            current_sector_exposure=4.5,
        )
        assert constrained["shares"] < unconstrained["shares"]
