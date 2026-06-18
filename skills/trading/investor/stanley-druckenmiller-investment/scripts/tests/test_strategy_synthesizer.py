"""E2E tests for the full strategy_synthesizer pipeline."""

from allocation_engine import calculate_position_sizing, generate_allocation
from report_loader import OPTIONAL_SKILLS, REQUIRED_SKILLS, extract_signal, load_all_reports
from scorer import calculate_composite_conviction, classify_pattern


def _run_pipeline(reports_dir, max_age=72):
    """Execute the full synthesizer pipeline and return the analysis dict."""
    reports = load_all_reports(reports_dir, max_age_hours=max_age)

    signals = {}
    for skill_name, report_data in reports.items():
        signals[skill_name] = extract_signal(skill_name, report_data)

    conviction = calculate_composite_conviction(signals)
    score = conviction["conviction_score"]
    zone = conviction["zone"]

    pattern = classify_pattern(signals, conviction["component_scores"], score)

    regime = signals.get("macro_regime", {}).get("regime", "transitional")
    allocation = generate_allocation(
        conviction_score=score,
        zone=zone,
        pattern=pattern["pattern"],
        regime=regime,
    )
    sizing = calculate_position_sizing(conviction_score=score, zone=zone)

    return {
        "reports": reports,
        "signals": signals,
        "conviction": conviction,
        "pattern": pattern,
        "allocation": allocation,
        "sizing": sizing,
    }


class TestFullPipeline:
    """E2E pipeline tests using fixture reports."""

    def test_full_pipeline_all_skills(self, full_reports):
        """8-skill full pipeline: load -> extract -> score -> pattern -> alloc."""
        result = _run_pipeline(full_reports)

        assert len(result["reports"]) == 8
        assert len(result["signals"]) == 8

        conv = result["conviction"]
        assert 0 <= conv["conviction_score"] <= 100
        assert conv["zone"] in [
            "Maximum Conviction",
            "High Conviction",
            "Moderate Conviction",
            "Low Conviction",
            "Capital Preservation",
        ]

        pattern = result["pattern"]
        assert pattern["pattern"] in [
            "policy_pivot_anticipation",
            "unsustainable_distortion",
            "extreme_sentiment_contrarian",
            "wait_and_observe",
        ]
        assert 0 <= pattern["match_strength"] <= 100

    def test_full_pipeline_required_only(self, all_required_reports):
        """5 required skills only: pipeline completes with optional unavailable."""
        result = _run_pipeline(all_required_reports)

        assert len(result["reports"]) == 5
        for req in REQUIRED_SKILLS:
            assert req in result["signals"]

        # Optional skills not in signals
        for opt in OPTIONAL_SKILLS:
            assert opt not in result["signals"]

        # Theme and setup components should be unavailable
        cs = result["conviction"]["component_scores"]
        assert cs["theme_quality"]["available"] is False
        assert cs["setup_availability"]["available"] is False
        assert cs["theme_quality"]["effective_weight"] == 0.0
        assert cs["setup_availability"]["effective_weight"] == 0.0

    def test_conviction_score_consistency(self, full_reports):
        """Same input must produce identical output (deterministic)."""
        r1 = _run_pipeline(full_reports)
        r2 = _run_pipeline(full_reports)
        assert r1["conviction"]["conviction_score"] == r2["conviction"]["conviction_score"]
        assert r1["pattern"]["pattern"] == r2["pattern"]["pattern"]
        assert r1["allocation"] == r2["allocation"]

    def test_allocation_sums_to_100_across_zones(self, full_reports):
        """All 5 zones must produce allocations that sum to 100%."""
        zones = [
            "Maximum Conviction",
            "High Conviction",
            "Moderate Conviction",
            "Low Conviction",
            "Capital Preservation",
        ]
        patterns = [
            "policy_pivot_anticipation",
            "unsustainable_distortion",
            "extreme_sentiment_contrarian",
            "wait_and_observe",
        ]
        for zone in zones:
            for pattern in patterns:
                alloc = generate_allocation(
                    conviction_score=50,
                    zone=zone,
                    pattern=pattern,
                    regime="transitional",
                )
                total = sum(alloc.values())
                assert abs(total - 100) < 0.2, (
                    f"Zone={zone}, Pattern={pattern}: allocation={total}%"
                )
