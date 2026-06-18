"""Tests for fetch_breadth_csv.py -- CSV-based breadth data fetcher."""

import json
import os
import sys
import unittest

# Add scripts directory to path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "scripts"),
)

from fetch_breadth_csv import (
    BREADTH_8MA_THRESHOLDS,
    BREADTH_200MA_THRESHOLDS,
    # Constants
    BREADTH_CSV_URL,
    SECTOR_CSV_URL,
    UPTREND_CSV_URL,
    UPTREND_THRESHOLDS,
    AnalysisResult,
    # Data classes
    BreadthData,
    SectorData,
    UptrendData,
    _float_or_none,
    # Analysis
    analyze,
    classify_breadth_8ma,
    # Classification functions
    classify_breadth_200ma,
    classify_uptrend,
    # Output formatting
    format_human,
    format_json,
    is_dead_cross,
    uptrend_color,
)


class TestConstants(unittest.TestCase):
    """Test URL constants and threshold definitions."""

    def test_breadth_csv_url(self):
        self.assertIn("market_breadth_data.csv", BREADTH_CSV_URL)
        self.assertTrue(BREADTH_CSV_URL.startswith("https://"))

    def test_uptrend_csv_url(self):
        self.assertIn("uptrend_ratio_timeseries.csv", UPTREND_CSV_URL)
        self.assertTrue(UPTREND_CSV_URL.startswith("https://"))

    def test_sector_csv_url(self):
        self.assertIn("sector_summary.csv", SECTOR_CSV_URL)
        self.assertTrue(SECTOR_CSV_URL.startswith("https://"))

    def test_threshold_lists_are_descending(self):
        for thresholds in [
            BREADTH_200MA_THRESHOLDS,
            BREADTH_8MA_THRESHOLDS,
            UPTREND_THRESHOLDS,
        ]:
            values = [t[0] for t in thresholds]
            self.assertEqual(values, sorted(values, reverse=True))


class TestDataClasses(unittest.TestCase):
    """Test data class instantiation."""

    def test_breadth_data(self):
        b = BreadthData(
            date="2026-02-13",
            sp500_price=6000.0,
            breadth_raw=0.65,
            breadth_200ma=0.6226,
            breadth_8ma=0.6756,
            trend="UPTREND",
        )
        self.assertEqual(b.date, "2026-02-13")
        self.assertAlmostEqual(b.breadth_200ma, 0.6226)

    def test_uptrend_data(self):
        u = UptrendData(
            date="2026-02-13",
            ratio=0.3303,
            ma_10=0.3265,
            slope=0.0055,
            trend="up",
        )
        self.assertEqual(u.date, "2026-02-13")
        self.assertAlmostEqual(u.ratio, 0.3303)

    def test_sector_data(self):
        s = SectorData(
            sector="Energy",
            ratio=0.606,
            ma_10=0.55,
            trend="up",
            slope=0.01,
            status="overbought",
        )
        self.assertEqual(s.sector, "Energy")


class TestClassification(unittest.TestCase):
    """Test threshold classification logic."""

    # --- Breadth 200MA ---

    def test_200ma_healthy(self):
        self.assertEqual(classify_breadth_200ma(62.26), "healthy")
        self.assertEqual(classify_breadth_200ma(60.0), "healthy")
        self.assertEqual(classify_breadth_200ma(75.0), "healthy")

    def test_200ma_narrow_rally(self):
        self.assertEqual(classify_breadth_200ma(55.0), "narrow_rally")
        self.assertEqual(classify_breadth_200ma(50.0), "narrow_rally")

    def test_200ma_caution(self):
        self.assertEqual(classify_breadth_200ma(45.0), "caution")
        self.assertEqual(classify_breadth_200ma(40.0), "caution")

    def test_200ma_fragile(self):
        self.assertEqual(classify_breadth_200ma(35.0), "fragile")
        self.assertEqual(classify_breadth_200ma(10.0), "fragile")

    # --- Breadth 8MA ---

    def test_8ma_overbought(self):
        self.assertEqual(classify_breadth_8ma(75.0), "overbought")
        self.assertEqual(classify_breadth_8ma(73.0), "overbought")

    def test_8ma_healthy_bullish(self):
        self.assertEqual(classify_breadth_8ma(67.56), "healthy_bullish")
        self.assertEqual(classify_breadth_8ma(60.0), "healthy_bullish")

    def test_8ma_neutral(self):
        self.assertEqual(classify_breadth_8ma(50.0), "neutral")
        self.assertEqual(classify_breadth_8ma(40.0), "neutral")

    def test_8ma_bearish(self):
        self.assertEqual(classify_breadth_8ma(30.0), "bearish")
        self.assertEqual(classify_breadth_8ma(23.0), "bearish")

    def test_8ma_oversold(self):
        self.assertEqual(classify_breadth_8ma(20.0), "oversold")
        self.assertEqual(classify_breadth_8ma(10.0), "oversold")

    # --- Uptrend Ratio ---

    def test_uptrend_overbought(self):
        self.assertEqual(classify_uptrend(40.0), "overbought")
        self.assertEqual(classify_uptrend(37.0), "overbought")

    def test_uptrend_neutral_bullish(self):
        self.assertEqual(classify_uptrend(33.03), "neutral_bullish")
        self.assertEqual(classify_uptrend(30.0), "neutral_bullish")

    def test_uptrend_neutral(self):
        self.assertEqual(classify_uptrend(25.0), "neutral")
        self.assertEqual(classify_uptrend(20.0), "neutral")

    def test_uptrend_neutral_bearish(self):
        self.assertEqual(classify_uptrend(18.0), "neutral_bearish")
        self.assertEqual(classify_uptrend(15.0), "neutral_bearish")

    def test_uptrend_bearish(self):
        self.assertEqual(classify_uptrend(10.0), "bearish")
        self.assertEqual(classify_uptrend(5.0), "bearish")


class TestDeadCross(unittest.TestCase):
    """Test dead cross / golden cross detection."""

    def test_dead_cross_true(self):
        # 8MA below 200MA
        self.assertTrue(is_dead_cross(58.0, 60.0))

    def test_dead_cross_false(self):
        # 8MA above 200MA (golden cross)
        self.assertFalse(is_dead_cross(67.56, 62.26))

    def test_dead_cross_equal(self):
        # Equal values -- not a dead cross
        self.assertFalse(is_dead_cross(60.0, 60.0))

    def test_actual_data_no_dead_cross(self):
        """The actual 2/16 data: 8MA 67.56% >> 200MA 62.26%, NO dead cross."""
        self.assertFalse(is_dead_cross(67.56, 62.26))

    def test_opencv_error_was_dead_cross(self):
        """The erroneous OpenCV reading: 8MA 60.0% < 200MA 60.7%, false dead cross."""
        self.assertTrue(is_dead_cross(60.0, 60.7))


class TestUptrendColor(unittest.TestCase):
    """Test trend-to-color conversion."""

    def test_up_to_green(self):
        self.assertEqual(uptrend_color("up"), "GREEN")
        self.assertEqual(uptrend_color("UP"), "GREEN")
        self.assertEqual(uptrend_color("uptrend"), "GREEN")

    def test_down_to_red(self):
        self.assertEqual(uptrend_color("down"), "RED")
        self.assertEqual(uptrend_color("DOWN"), "RED")
        self.assertEqual(uptrend_color("downtrend"), "RED")

    def test_none_to_unknown(self):
        self.assertEqual(uptrend_color(None), "UNKNOWN")

    def test_empty_to_unknown(self):
        self.assertEqual(uptrend_color(""), "UNKNOWN")

    def test_other_to_unknown(self):
        self.assertEqual(uptrend_color("sideways"), "UNKNOWN")


class TestFloatOrNone(unittest.TestCase):
    """Test float parsing helper."""

    def test_valid_float(self):
        self.assertAlmostEqual(_float_or_none("0.6226"), 0.6226)
        self.assertAlmostEqual(_float_or_none("62.26"), 62.26)

    def test_none(self):
        self.assertIsNone(_float_or_none(None))

    def test_empty(self):
        self.assertIsNone(_float_or_none(""))
        self.assertIsNone(_float_or_none("  "))

    def test_na_values(self):
        self.assertIsNone(_float_or_none("NA"))
        self.assertIsNone(_float_or_none("nan"))
        self.assertIsNone(_float_or_none("None"))
        self.assertIsNone(_float_or_none("null"))


class TestAnalyze(unittest.TestCase):
    """Test the analyze function with mock data."""

    def _make_breadth(self, b200=0.6226, b8=0.6756):
        return [
            BreadthData(
                date="2026-02-13",
                sp500_price=6828.3,
                breadth_raw=0.65,
                breadth_200ma=b200,
                breadth_8ma=b8,
                trend="UPTREND",
            )
        ]

    def _make_uptrend(self, ratio=0.3303, slope=0.0055, trend="up"):
        return [
            UptrendData(
                date="2026-02-13",
                ratio=ratio,
                ma_10=0.3265,
                slope=slope,
                trend=trend,
            )
        ]

    def _make_sectors(self):
        return [
            SectorData("Energy", 0.606, 0.55, "up", 0.01, "overbought"),
            SectorData("Technology", 0.35, 0.40, "down", -0.005, None),
        ]

    def test_basic_analysis(self):
        result = analyze(
            self._make_breadth(),
            self._make_uptrend(),
            self._make_sectors(),
        )
        self.assertAlmostEqual(result.breadth_200ma, 62.26)
        self.assertAlmostEqual(result.breadth_8ma, 67.56)
        self.assertFalse(result.dead_cross)
        self.assertGreater(result.cross_diff, 0)  # 8MA > 200MA
        self.assertEqual(result.breadth_200ma_class, "healthy")
        self.assertEqual(result.breadth_8ma_class, "healthy_bullish")

    def test_uptrend_analysis(self):
        result = analyze(
            self._make_breadth(),
            self._make_uptrend(),
            self._make_sectors(),
        )
        self.assertAlmostEqual(result.uptrend_ratio, 33.03)
        self.assertEqual(result.uptrend_color, "GREEN")
        self.assertEqual(result.uptrend_class, "neutral_bullish")
        self.assertAlmostEqual(result.uptrend_slope, 0.0055)

    def test_dead_cross_scenario(self):
        result = analyze(
            self._make_breadth(b200=0.60, b8=0.58),
            self._make_uptrend(),
            self._make_sectors(),
        )
        self.assertTrue(result.dead_cross)
        self.assertLess(result.cross_diff, 0)

    def test_golden_cross_scenario(self):
        result = analyze(
            self._make_breadth(b200=0.60, b8=0.65),
            self._make_uptrend(),
            self._make_sectors(),
        )
        self.assertFalse(result.dead_cross)
        self.assertGreater(result.cross_diff, 0)

    def test_downtrend_uptrend_ratio(self):
        result = analyze(
            self._make_breadth(),
            self._make_uptrend(ratio=0.18, trend="down"),
            self._make_sectors(),
        )
        self.assertEqual(result.uptrend_color, "RED")
        self.assertEqual(result.uptrend_class, "neutral_bearish")

    def test_empty_breadth_raises(self):
        with self.assertRaises(ValueError):
            analyze([], self._make_uptrend(), self._make_sectors())

    def test_empty_uptrend_raises(self):
        with self.assertRaises(ValueError):
            analyze(self._make_breadth(), [], self._make_sectors())

    def test_sectors_in_result(self):
        result = analyze(
            self._make_breadth(),
            self._make_uptrend(),
            self._make_sectors(),
        )
        self.assertEqual(len(result.sectors), 2)
        self.assertEqual(result.sectors[0]["sector"], "Energy")
        self.assertAlmostEqual(result.sectors[0]["ratio"], 60.6)

    def test_percentage_values_already_in_percent(self):
        """Test that values > 1.0 are treated as already-percent."""
        breadth = [
            BreadthData(
                date="2026-02-13",
                sp500_price=6828.3,
                breadth_raw=65.0,
                breadth_200ma=62.26,
                breadth_8ma=67.56,
                trend="UPTREND",
            )
        ]
        uptrend = [
            UptrendData(
                date="2026-02-13",
                ratio=33.03,
                ma_10=32.65,
                slope=0.0055,
                trend="up",
            )
        ]
        result = analyze(breadth, uptrend, [])
        self.assertAlmostEqual(result.breadth_200ma, 62.26)
        self.assertAlmostEqual(result.uptrend_ratio, 33.03)


class TestFormatHuman(unittest.TestCase):
    """Test human-readable output formatting."""

    def _make_result(self, dead_cross=False):
        return AnalysisResult(
            breadth_date="2026-02-13",
            breadth_200ma=62.26,
            breadth_200ma_class="healthy",
            breadth_8ma=67.56,
            breadth_8ma_class="healthy_bullish",
            dead_cross=dead_cross,
            cross_diff=5.30 if not dead_cross else -2.0,
            breadth_trend="UPTREND",
            uptrend_date="2026-02-13",
            uptrend_ratio=33.03,
            uptrend_color="GREEN",
            uptrend_class="neutral_bullish",
            uptrend_ma10=32.65,
            uptrend_slope=0.0055,
            uptrend_trend="up",
            sectors=[
                {"sector": "Energy", "ratio": 60.6, "trend": "up", "status": "overbought"},
            ],
        )

    def test_contains_breadth_values(self):
        output = format_human(self._make_result())
        self.assertIn("62.26%", output)
        self.assertIn("67.56%", output)

    def test_contains_no_dead_cross(self):
        output = format_human(self._make_result(dead_cross=False))
        self.assertIn("NO dead cross", output)
        self.assertIn("+5.30pt", output)

    def test_contains_dead_cross(self):
        output = format_human(self._make_result(dead_cross=True))
        self.assertIn("DEAD CROSS", output)

    def test_contains_uptrend_values(self):
        output = format_human(self._make_result())
        self.assertIn("33.03%", output)
        self.assertIn("GREEN", output)
        self.assertIn("+0.0055", output)

    def test_contains_sector_summary(self):
        output = format_human(self._make_result())
        self.assertIn("Energy", output)
        self.assertIn("Overbought", output)


class TestFormatJson(unittest.TestCase):
    """Test JSON output formatting."""

    def test_valid_json(self):
        result = AnalysisResult(
            breadth_date="2026-02-13",
            breadth_200ma=62.26,
            breadth_200ma_class="healthy",
            breadth_8ma=67.56,
            breadth_8ma_class="healthy_bullish",
            dead_cross=False,
            cross_diff=5.30,
            breadth_trend="UPTREND",
            uptrend_date="2026-02-13",
            uptrend_ratio=33.03,
            uptrend_color="GREEN",
            uptrend_class="neutral_bullish",
            uptrend_ma10=32.65,
            uptrend_slope=0.0055,
            uptrend_trend="up",
            sectors=[],
        )
        output = format_json(result)
        data = json.loads(output)
        self.assertEqual(data["breadth_200ma"], 62.26)
        self.assertFalse(data["dead_cross"])
        self.assertEqual(data["uptrend_color"], "GREEN")


if __name__ == "__main__":
    unittest.main()
