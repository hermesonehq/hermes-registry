"""Tests for exposure_policy (TQQQ vs QQQ differentiation)."""

from exposure_policy import generate_portfolio_action


class TestTQQQPolicy:
    def test_normal_keeps_full_exposure(self):
        action = generate_portfolio_action(
            risk_level="NORMAL",
            instrument="TQQQ",
            current_exposure_pct=100,
            base_trailing_stop_pct=10,
        )
        assert action.recommended_action == "HOLD_OR_FOLLOW_BASE_STRATEGY"
        assert action.target_exposure_pct == 100
        assert action.trailing_stop_pct == 10
        assert action.exposure_delta_pct == 0

    def test_caution_avoids_new_adds_75(self):
        action = generate_portfolio_action("CAUTION", "TQQQ", 100, 10)
        assert action.recommended_action == "AVOID_NEW_ADDS"
        assert action.target_exposure_pct == 75
        assert action.exposure_delta_pct == -25
        assert action.trailing_stop_pct == 7

    def test_high_reduces_to_50(self):
        action = generate_portfolio_action("HIGH", "TQQQ", 100, 10)
        assert action.recommended_action == "REDUCE_EXPOSURE"
        assert action.target_exposure_pct == 50
        assert action.exposure_delta_pct == -50
        assert action.trailing_stop_pct == 5

    def test_severe_closes_or_hedges_to_25(self):
        action = generate_portfolio_action("SEVERE", "TQQQ", 100, 10)
        assert action.recommended_action == "CLOSE_TQQQ_OR_HEDGE"
        assert action.target_exposure_pct == 25
        assert action.exposure_delta_pct == -75
        assert action.trailing_stop_pct == 3

    def test_trailing_stop_does_not_increase(self):
        # If base trailing is already tighter than the policy cap, keep it.
        action = generate_portfolio_action("HIGH", "TQQQ", 100, 4)
        assert action.trailing_stop_pct == 4  # min(4, 5) = 4


class TestQQQPolicyLessAggressive:
    def test_qqq_high_keeps_75_not_50(self):
        action = generate_portfolio_action("HIGH", "QQQ", 100, 10)
        assert action.target_exposure_pct == 75

    def test_qqq_severe_keeps_50_not_25(self):
        action = generate_portfolio_action("SEVERE", "QQQ", 100, 10)
        assert action.target_exposure_pct == 50

    def test_qqq_caution_stays_at_100(self):
        # Differs from TQQQ (which drops to 75)
        action = generate_portfolio_action("CAUTION", "QQQ", 100, 10)
        assert action.target_exposure_pct == 100
