"""Tests for report_generator.py"""

import json

from report_generator import generate_json_report, generate_markdown_report


def _build_analysis(
    score=65,
    zone="High Conviction",
    zone_color="light_green",
    pattern="policy_pivot_anticipation",
    match_strength=75,
    include_optional=True,
):
    """Build a minimal but complete analysis dict for report generation."""
    component_scores = {
        "market_structure": {
            "score": 70,
            "weight": 0.18,
            "effective_weight": 0.18,
            "available": True,
            "weighted_contribution": 12.6,
            "label": "Market Structure (Breadth + Uptrend)",
        },
        "distribution_risk": {
            "score": 60,
            "weight": 0.18,
            "effective_weight": 0.18,
            "available": True,
            "weighted_contribution": 10.8,
            "label": "Distribution Risk (Market Top, inverted)",
        },
        "bottom_confirmation": {
            "score": 80,
            "weight": 0.12,
            "effective_weight": 0.12,
            "available": True,
            "weighted_contribution": 9.6,
            "label": "Bottom Confirmation (FTD Detector)",
        },
        "macro_alignment": {
            "score": 75,
            "weight": 0.18,
            "effective_weight": 0.18,
            "available": True,
            "weighted_contribution": 13.5,
            "label": "Macro Alignment (Regime)",
        },
        "theme_quality": {
            "score": 50 if include_optional else 50,
            "weight": 0.12,
            "effective_weight": 0.12 if include_optional else 0.0,
            "available": include_optional,
            "weighted_contribution": 6.0 if include_optional else 0.0,
            "label": "Theme Quality (Theme Detector)",
        },
        "setup_availability": {
            "score": 55 if include_optional else 50,
            "weight": 0.10,
            "effective_weight": 0.10 if include_optional else 0.0,
            "available": include_optional,
            "weighted_contribution": 5.5 if include_optional else 0.0,
            "label": "Setup Availability (VCP + CANSLIM)",
        },
        "signal_convergence": {
            "score": 72,
            "weight": 0.12,
            "effective_weight": 0.12,
            "available": True,
            "weighted_contribution": 8.6,
            "label": "Signal Convergence (Cross-Skill Agreement)",
        },
    }

    input_summary = {
        "market_breadth": {"composite_score": 65, "zone": "Healthy"},
        "uptrend_analysis": {"composite_score": 70, "zone": "Bull"},
        "market_top": {"composite_score": 40, "zone": "Yellow"},
        "macro_regime": {
            "composite_score": 60,
            "regime": "broadening",
            "confidence": "medium",
        },
        "ftd_detector": {"state": "FTD_CONFIRMED", "quality_score": 80},
    }
    if include_optional:
        input_summary["vcp_screener"] = {
            "derived_score": 55,
            "textbook_count": 1,
            "strong_count": 2,
        }
        input_summary["theme_detector"] = {
            "derived_score": 50,
            "hot_count": 3,
            "exhaustion_count": 1,
        }
        input_summary["canslim_screener"] = {
            "derived_score": 60,
            "m_score": 80,
            "exceptional_count": 2,
        }

    return {
        "metadata": {
            "generated_at": "2026-02-19 12:00:00",
            "reports_dir": "reports/",
            "max_age_hours": 72,
            "skills_loaded": 8 if include_optional else 5,
            "required_count": 5,
            "optional_count": 3 if include_optional else 0,
            "skills_list": list(input_summary.keys()),
        },
        "conviction": {
            "conviction_score": score,
            "zone": zone,
            "zone_color": zone_color,
            "exposure_range": "70-90%",
            "guidance": "Multiple signals confirm.",
            "actions": [
                "Above-average equity allocation (70-90%)",
                "New entries on quality setups",
            ],
            "strongest_component": {
                "component": "bottom_confirmation",
                "label": "Bottom Confirmation (FTD Detector)",
                "score": 80,
            },
            "weakest_component": {
                "component": "theme_quality",
                "label": "Theme Quality (Theme Detector)",
                "score": 50,
            },
            "data_quality": {"available_count": 7, "total_components": 7},
            "component_scores": component_scores,
        },
        "pattern": {
            "pattern": pattern,
            "label": "Policy Pivot Anticipation",
            "description": "Central bank policy at inflection point.",
            "match_strength": match_strength,
            "all_pattern_scores": {
                "policy_pivot_anticipation": match_strength,
                "unsustainable_distortion": 20,
                "extreme_sentiment_contrarian": 15,
                "wait_and_observe": 40,
            },
        },
        "allocation": {
            "target": {"equity": 75, "bonds": 5, "alternatives": 5, "cash": 15},
            "regime": "broadening",
            "pattern": pattern,
            "zone": zone,
        },
        "position_sizing": {
            "max_single_position": 15,
            "daily_vol_target": 0.3,
            "max_positions": 12,
        },
        "input_summary": input_summary,
    }


class TestJsonReport:
    """Test JSON report generation."""

    def test_json_output_valid(self, tmp_path):
        """Generated JSON must be parseable."""
        analysis = _build_analysis()
        out = str(tmp_path / "report.json")
        generate_json_report(analysis, out)
        with open(out) as f:
            data = json.load(f)
        assert data["conviction"]["conviction_score"] == 65

    def test_json_has_all_top_keys(self, tmp_path):
        """JSON must contain all top-level sections."""
        analysis = _build_analysis()
        out = str(tmp_path / "report.json")
        generate_json_report(analysis, out)
        with open(out) as f:
            data = json.load(f)
        for key in [
            "metadata",
            "conviction",
            "pattern",
            "allocation",
            "position_sizing",
            "input_summary",
        ]:
            assert key in data, f"Missing top-level key: {key}"

    def test_json_empty_input(self, tmp_path):
        """Empty analysis should still produce valid JSON."""
        out = str(tmp_path / "empty.json")
        generate_json_report({}, out)
        with open(out) as f:
            data = json.load(f)
        assert isinstance(data, dict)


class TestMarkdownReport:
    """Test Markdown report generation."""

    def _generate_md(self, tmp_path, **kwargs):
        """Helper to generate and read markdown."""
        analysis = _build_analysis(**kwargs)
        out = str(tmp_path / "report.md")
        generate_markdown_report(analysis, out)
        with open(out) as f:
            return f.read()

    def test_all_sections_present(self, tmp_path):
        """All 8 sections must appear in the markdown."""
        md = self._generate_md(tmp_path)
        expected_sections = [
            "## 1. Conviction Dashboard",
            "## 2. Pattern Classification",
            "## 3. Component Scores",
            "## 4. Input Skills Summary",
            "## 5. Target Allocation",
            "## 6. Position Sizing & Risk",
            "## 7. Druckenmiller Principle",
            "## Methodology",
        ]
        for section in expected_sections:
            assert section in md, f"Missing section: {section}"

    def test_conviction_score_embedded(self, tmp_path):
        """Conviction score must appear in the dashboard."""
        md = self._generate_md(tmp_path, score=72)
        assert "72/100" in md

    def test_pattern_displayed(self, tmp_path):
        """Detected pattern must appear."""
        md = self._generate_md(tmp_path)
        assert "Policy Pivot Anticipation" in md

    def test_allocation_table(self, tmp_path):
        """Allocation table must show all 4 asset classes."""
        md = self._generate_md(tmp_path)
        for asset in ["Equity", "Bonds", "Alternatives", "Cash"]:
            assert asset in md

    def test_disclaimer_present(self, tmp_path):
        """Disclaimer must appear at the end."""
        md = self._generate_md(tmp_path)
        assert "Disclaimer" in md
        assert "educational and informational purposes" in md

    def test_optional_skills_not_available(self, tmp_path):
        """Optional skills without data should show 'Not available'."""
        md = self._generate_md(tmp_path, include_optional=False)
        assert "Not available" in md

    def test_component_effective_weight_column(self, tmp_path):
        """Component table must include Eff. Weight column."""
        md = self._generate_md(tmp_path)
        assert "Eff. Weight" in md

    def test_unavailable_component_marked_na(self, tmp_path):
        """Unavailable components should show (N/A) marker."""
        md = self._generate_md(tmp_path, include_optional=False)
        assert "(N/A)" in md

    def test_pattern_scores_table(self, tmp_path):
        """All 4 pattern scores should appear."""
        md = self._generate_md(tmp_path)
        for pattern_name in [
            "Policy Pivot Anticipation",
            "Unsustainable Distortion",
            "Extreme Sentiment Contrarian",
            "Wait And Observe",
        ]:
            assert pattern_name in md

    def test_druckenmiller_quote(self, tmp_path):
        """A Druckenmiller quote should appear in section 7."""
        md = self._generate_md(tmp_path)
        assert "Stanley Druckenmiller" in md
