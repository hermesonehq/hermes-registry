"""Tests for math_utils (M10: most-recent-first contract)."""

import pytest
from math_utils import calc_ema, calc_sma


class TestSMA:
    def test_uses_most_recent_n_closes(self):
        # most-recent-first: [100, 90, 80, 70, 60]
        # SMA(3) = mean of [100, 90, 80] = 90
        closes = [100.0, 90.0, 80.0, 70.0, 60.0]
        assert calc_sma(closes, 3) == pytest.approx(90.0)

    def test_partial_fallback_when_period_exceeds_data(self):
        closes = [100.0, 90.0]
        # period > len -> partial mean
        assert calc_sma(closes, 5) == pytest.approx(95.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            calc_sma([], 3)


class TestEMA:
    def test_accepts_most_recent_first_contract(self):
        # Constant series -> EMA = constant
        closes = [100.0] * 30
        assert calc_ema(closes, 21) == pytest.approx(100.0)

    def test_partial_fallback_when_period_exceeds_data(self):
        closes = [100.0, 90.0, 80.0]
        # period > len -> partial mean
        assert calc_ema(closes, 21) == pytest.approx(90.0)
