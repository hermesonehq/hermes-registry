"""Tests for scorer.py"""

from scorer import (
    COMPONENT_WEIGHTS,
    calculate_bottom_confirmation,
    calculate_composite_conviction,
    calculate_distribution_risk,
    calculate_macro_alignment,
    calculate_market_structure,
    calculate_signal_convergence,
    classify_pattern,
)


class TestWeights:
    """Verify component weights sum to 1.0."""

    def test_weights_sum_to_one(self):
        total = sum(COMPONENT_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"


class TestComponentCalculators:
    """Test individual component calculators."""

    def test_market_structure_healthy(self):
        signals = {
            "market_breadth": {"composite_score": 70},
            "uptrend_analysis": {"composite_score": 80},
        }
        score = calculate_market_structure(signals)
        assert 70 <= score <= 80

    def test_market_structure_divergence_penalty(self):
        signals = {
            "market_breadth": {"composite_score": 80},
            "uptrend_analysis": {"composite_score": 30},
        }
        score = calculate_market_structure(signals)
        # Should be below simple average (55) due to divergence penalty
        assert score < 55

    def test_distribution_risk_inverted(self):
        """High top score = low conviction (distribution risk is inverted)."""
        signals = {"market_top": {"composite_score": 80}}
        score = calculate_distribution_risk(signals)
        assert score == 20.0

        signals_low = {"market_top": {"composite_score": 10}}
        score_low = calculate_distribution_risk(signals_low)
        assert score_low == 90.0

    def test_bottom_confirmation_ftd_confirmed(self):
        signals = {
            "ftd_detector": {
                "state": "FTD_CONFIRMED",
                "quality_score": 85,
                "dual_confirmation": True,
                "post_ftd_distribution_count": 0,
            },
        }
        score = calculate_bottom_confirmation(signals)
        assert score >= 80

    def test_bottom_confirmation_rally_failed(self):
        signals = {
            "ftd_detector": {
                "state": "RALLY_FAILED",
                "quality_score": 0,
                "dual_confirmation": False,
                "post_ftd_distribution_count": 0,
            },
        }
        score = calculate_bottom_confirmation(signals)
        assert score <= 15

    def test_macro_alignment_broadening(self):
        signals = {
            "macro_regime": {
                "regime": "broadening",
                "composite_score": 60,
                "confidence": "high",
            },
        }
        score = calculate_macro_alignment(signals)
        assert score >= 75

    def test_macro_alignment_contraction(self):
        signals = {
            "macro_regime": {
                "regime": "contraction",
                "composite_score": 40,
                "confidence": "medium",
            },
        }
        score = calculate_macro_alignment(signals)
        assert score <= 25

    def test_signal_convergence_all_bullish(self):
        signals = {
            "market_breadth": {"composite_score": 70},
            "uptrend_analysis": {"composite_score": 75},
            "market_top": {"composite_score": 20},
            "macro_regime": {"composite_score": 70},
            "ftd_detector": {"quality_score": 80},
        }
        score = calculate_signal_convergence(signals)
        assert score >= 70  # All bullish = high convergence

    def test_signal_convergence_mixed(self):
        signals = {
            "market_breadth": {"composite_score": 80},
            "uptrend_analysis": {"composite_score": 20},
            "market_top": {"composite_score": 70},
            "macro_regime": {"composite_score": 30},
            "ftd_detector": {"quality_score": 90},
        }
        score = calculate_signal_convergence(signals)
        assert score < 60  # Mixed signals = lower convergence

    def test_signal_convergence_all_bearish_reduces_score(self):
        """All bearish convergence should reduce score (not increase it)."""
        bearish = {
            "market_breadth": {"composite_score": 30},
            "uptrend_analysis": {"composite_score": 25},
            "market_top": {"composite_score": 80},  # inverted -> 20
            "macro_regime": {"composite_score": 20},
            "ftd_detector": {"quality_score": 15},
        }
        score = calculate_signal_convergence(bearish)
        # Bearish convergence should NOT produce a high score
        assert score < 80, f"Bearish convergence too high: {score}"

    def test_signal_convergence_bearish_less_than_bullish(self):
        """Bearish convergence score must be lower than bullish convergence."""
        bullish = {
            "market_breadth": {"composite_score": 70},
            "uptrend_analysis": {"composite_score": 75},
            "market_top": {"composite_score": 20},
            "macro_regime": {"composite_score": 70},
            "ftd_detector": {"quality_score": 80},
        }
        bearish = {
            "market_breadth": {"composite_score": 30},
            "uptrend_analysis": {"composite_score": 25},
            "market_top": {"composite_score": 80},
            "macro_regime": {"composite_score": 20},
            "ftd_detector": {"quality_score": 15},
        }
        bullish_score = calculate_signal_convergence(bullish)
        bearish_score = calculate_signal_convergence(bearish)
        assert bearish_score < bullish_score

    def test_signal_convergence_no_adjustment_when_mixed(self):
        """Mixed signals (some bullish, some bearish) get no bonus/penalty."""
        mixed = {
            "market_breadth": {"composite_score": 70},
            "uptrend_analysis": {"composite_score": 30},
            "market_top": {"composite_score": 50},
            "macro_regime": {"composite_score": 60},
            "ftd_detector": {"quality_score": 40},
        }
        score = calculate_signal_convergence(mixed)
        # Neither all > 55 nor all < 45, so no directional adjustment
        # Just a moderate convergence based on std deviation
        assert 20 <= score <= 80


class TestCompositeConviction:
    """Test the full composite scoring pipeline."""

    def _build_signals(
        self,
        breadth=50,
        uptrend=50,
        top=50,
        macro_regime="transitional",
        macro_score=50,
        macro_conf="medium",
        ftd_state="NO_SIGNAL",
        ftd_quality=50,
        theme_derived=50,
        vcp_derived=50,
        canslim_derived=50,
    ):
        """Helper to build a complete signal dict."""
        return {
            "market_breadth": {"composite_score": breadth},
            "uptrend_analysis": {"composite_score": uptrend},
            "market_top": {"composite_score": top},
            "macro_regime": {
                "regime": macro_regime,
                "composite_score": macro_score,
                "confidence": macro_conf,
                "transition_level": "moderate",
            },
            "ftd_detector": {
                "state": ftd_state,
                "quality_score": ftd_quality,
                "dual_confirmation": False,
                "post_ftd_distribution_count": 0,
            },
            "theme_detector": {"derived_score": theme_derived},
            "vcp_screener": {"derived_score": vcp_derived, "textbook_count": 0},
            "canslim_screener": {
                "derived_score": canslim_derived,
                "exceptional_count": 0,
            },
        }

    def test_all_zero_signals(self):
        signals = self._build_signals(
            breadth=0,
            uptrend=0,
            top=100,
            macro_regime="contraction",
            macro_score=0,
            ftd_state="RALLY_FAILED",
            ftd_quality=0,
            theme_derived=0,
            vcp_derived=0,
            canslim_derived=0,
        )
        result = calculate_composite_conviction(signals)
        assert result["conviction_score"] <= 20
        assert result["zone"] == "Capital Preservation"

    def test_all_100_signals(self):
        signals = self._build_signals(
            breadth=100,
            uptrend=100,
            top=0,
            macro_regime="broadening",
            macro_score=100,
            macro_conf="high",
            ftd_state="FTD_CONFIRMED",
            ftd_quality=100,
            theme_derived=100,
            vcp_derived=100,
            canslim_derived=100,
        )
        result = calculate_composite_conviction(signals)
        assert result["conviction_score"] >= 80
        assert result["zone"] == "Maximum Conviction"

    def test_bullish_alignment(self):
        signals = self._build_signals(
            breadth=75,
            uptrend=80,
            top=15,
            macro_regime="broadening",
            macro_score=70,
            macro_conf="high",
            ftd_state="FTD_CONFIRMED",
            ftd_quality=85,
            theme_derived=70,
            vcp_derived=65,
        )
        result = calculate_composite_conviction(signals)
        assert result["conviction_score"] >= 60
        assert "High" in result["zone"] or "Maximum" in result["zone"]

    def test_bearish_alignment(self):
        signals = self._build_signals(
            breadth=25,
            uptrend=20,
            top=80,
            macro_regime="contraction",
            macro_score=20,
            ftd_state="RALLY_FAILED",
            ftd_quality=10,
            theme_derived=20,
            vcp_derived=10,
        )
        result = calculate_composite_conviction(signals)
        assert result["conviction_score"] <= 40

    def test_mixed_signals(self):
        signals = self._build_signals(
            breadth=70,
            uptrend=30,
            top=60,
            macro_regime="transitional",
            macro_score=50,
            ftd_state="RALLY_ATTEMPT",
            ftd_quality=40,
            theme_derived=55,
        )
        result = calculate_composite_conviction(signals)
        assert 30 <= result["conviction_score"] <= 60

    def test_output_structure(self):
        signals = self._build_signals()
        result = calculate_composite_conviction(signals)
        assert "conviction_score" in result
        assert "zone" in result
        assert "exposure_range" in result
        assert "guidance" in result
        assert "actions" in result
        assert "strongest_component" in result
        assert "weakest_component" in result
        assert "component_scores" in result
        assert len(result["component_scores"]) == 7
        # Issue 2: verify new fields exist on each component
        for key, comp in result["component_scores"].items():
            assert "effective_weight" in comp, f"Missing effective_weight on {key}"
            assert "available" in comp, f"Missing available on {key}"

    def test_score_bounded_0_100(self):
        signals = self._build_signals()
        result = calculate_composite_conviction(signals)
        assert 0 <= result["conviction_score"] <= 100


class TestPatternClassification:
    """Test pattern classification logic."""

    def test_policy_pivot_detected(self):
        signals = {
            "macro_regime": {
                "regime": "transitional",
                "composite_score": 60,
                "transition_level": "high",
            },
            "market_top": {"composite_score": 30},
            "ftd_detector": {"state": "NO_SIGNAL", "quality_score": 50},
            "market_breadth": {"composite_score": 60},
        }
        comp_scores = {k: {"score": 60} for k in COMPONENT_WEIGHTS}
        result = classify_pattern(signals, comp_scores, 65)
        assert result["pattern"] == "policy_pivot_anticipation"

    def test_unsustainable_distortion_detected(self):
        signals = {
            "macro_regime": {
                "regime": "contraction",
                "composite_score": 30,
                "transition_level": "low",
            },
            "market_top": {"composite_score": 75},
            "ftd_detector": {"state": "CORRECTION", "quality_score": 20},
            "market_breadth": {"composite_score": 30},
            "theme_detector": {"exhaustion_count": 3},
        }
        comp_scores = {k: {"score": 30} for k in COMPONENT_WEIGHTS}
        result = classify_pattern(signals, comp_scores, 25)
        assert result["pattern"] == "unsustainable_distortion"

    def test_extreme_contrarian_with_ftd(self):
        signals = {
            "macro_regime": {
                "regime": "contraction",
                "composite_score": 20,
                "transition_level": "low",
            },
            "market_top": {"composite_score": 80},
            "ftd_detector": {"state": "FTD_CONFIRMED", "quality_score": 90},
            "market_breadth": {"composite_score": 25},
        }
        comp_scores = {k: {"score": 20} for k in COMPONENT_WEIGHTS}
        result = classify_pattern(signals, comp_scores, 30)
        assert result["pattern"] == "extreme_sentiment_contrarian"

    def test_wait_and_observe_default(self):
        signals = {
            "macro_regime": {
                "regime": "concentration",
                "composite_score": 50,
                "transition_level": "low",
            },
            "market_top": {"composite_score": 50},
            "ftd_detector": {"state": "NO_SIGNAL", "quality_score": 50},
            "market_breadth": {"composite_score": 50},
        }
        comp_scores = {k: {"score": 50} for k in COMPONENT_WEIGHTS}
        result = classify_pattern(signals, comp_scores, 35)
        assert result["pattern"] == "wait_and_observe"

    def test_pattern_has_all_scores(self):
        signals = {
            "macro_regime": {
                "regime": "broadening",
                "composite_score": 70,
                "transition_level": "moderate",
            },
            "market_top": {"composite_score": 30},
            "ftd_detector": {"state": "NO_SIGNAL", "quality_score": 50},
            "market_breadth": {"composite_score": 60},
        }
        comp_scores = {k: {"score": 60} for k in COMPONENT_WEIGHTS}
        result = classify_pattern(signals, comp_scores, 60)
        assert "all_pattern_scores" in result
        assert len(result["all_pattern_scores"]) == 4
        assert "match_strength" in result


class TestWeightRedistribution:
    """Test weight redistribution when optional skills are missing."""

    def _required_only_signals(
        self,
        breadth=70,
        uptrend=70,
        top=30,
        macro_regime="broadening",
        macro_score=70,
        macro_conf="high",
        ftd_state="FTD_CONFIRMED",
        ftd_quality=80,
    ):
        """Build signals with ONLY the 5 required skills (no optionals)."""
        return {
            "market_breadth": {"composite_score": breadth},
            "uptrend_analysis": {"composite_score": uptrend},
            "market_top": {"composite_score": top},
            "macro_regime": {
                "regime": macro_regime,
                "composite_score": macro_score,
                "confidence": macro_conf,
                "transition_level": "moderate",
            },
            "ftd_detector": {
                "state": ftd_state,
                "quality_score": ftd_quality,
                "dual_confirmation": False,
                "post_ftd_distribution_count": 0,
            },
        }

    def test_missing_theme_redistributes_weight(self):
        """theme_detector absent -> theme_quality effective_weight=0."""
        signals = self._required_only_signals()
        result = calculate_composite_conviction(signals)
        cs = result["component_scores"]
        assert cs["theme_quality"]["effective_weight"] == 0.0
        assert cs["theme_quality"]["available"] is False

    def test_missing_all_optional_redistributes(self):
        """No optional skills -> effective_weights of available components sum to 1.0."""
        signals = self._required_only_signals()
        result = calculate_composite_conviction(signals)
        cs = result["component_scores"]
        total_ew = sum(c["effective_weight"] for c in cs.values())
        assert abs(total_ew - 1.0) < 0.001, f"Effective weights sum to {total_ew}"

    def test_all_optional_present_uses_standard_weights(self):
        """All skills present -> effective_weight == base weight."""
        signals = self._required_only_signals()
        signals["theme_detector"] = {"derived_score": 60}
        signals["vcp_screener"] = {"derived_score": 50, "textbook_count": 0}
        signals["canslim_screener"] = {"derived_score": 50, "exceptional_count": 0}
        result = calculate_composite_conviction(signals)
        cs = result["component_scores"]
        for key, comp in cs.items():
            assert abs(comp["effective_weight"] - COMPONENT_WEIGHTS[key]) < 0.001, (
                f"{key}: effective_weight={comp['effective_weight']} != {COMPONENT_WEIGHTS[key]}"
            )
            assert comp["available"] is True

    def test_missing_optional_does_not_inflate_score(self):
        """With optionals missing, neutral-50 defaults must NOT inflate the score."""
        # All required at mediocre 50
        signals_with = {
            "market_breadth": {"composite_score": 50},
            "uptrend_analysis": {"composite_score": 50},
            "market_top": {"composite_score": 50},
            "macro_regime": {
                "regime": "transitional",
                "composite_score": 50,
                "confidence": "medium",
                "transition_level": "moderate",
            },
            "ftd_detector": {
                "state": "NO_SIGNAL",
                "quality_score": 50,
                "dual_confirmation": False,
                "post_ftd_distribution_count": 0,
            },
            "theme_detector": {"derived_score": 50},
            "vcp_screener": {"derived_score": 50, "textbook_count": 0},
            "canslim_screener": {"derived_score": 50, "exceptional_count": 0},
        }
        signals_without = {
            "market_breadth": {"composite_score": 50},
            "uptrend_analysis": {"composite_score": 50},
            "market_top": {"composite_score": 50},
            "macro_regime": {
                "regime": "transitional",
                "composite_score": 50,
                "confidence": "medium",
                "transition_level": "moderate",
            },
            "ftd_detector": {
                "state": "NO_SIGNAL",
                "quality_score": 50,
                "dual_confirmation": False,
                "post_ftd_distribution_count": 0,
            },
        }
        score_with = calculate_composite_conviction(signals_with)["conviction_score"]
        score_without = calculate_composite_conviction(signals_without)["conviction_score"]
        # Removing optional skills that score 50 should not change the composite
        # because redistribution replaces fixed-50 defaults
        assert abs(score_with - score_without) < 5.0, (
            f"Score inflated: with={score_with}, without={score_without}"
        )

    def test_vcp_only_keeps_setup_available(self):
        """VCP alone (no CANSLIM) should keep setup_availability available."""
        signals = self._required_only_signals()
        signals["vcp_screener"] = {"derived_score": 60, "textbook_count": 1}
        result = calculate_composite_conviction(signals)
        cs = result["component_scores"]
        assert cs["setup_availability"]["available"] is True
        assert cs["setup_availability"]["effective_weight"] > 0
