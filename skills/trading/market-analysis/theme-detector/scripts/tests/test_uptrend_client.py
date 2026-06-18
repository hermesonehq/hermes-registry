"""Tests for uptrend_client.is_data_stale (business day logic)."""

from datetime import datetime
from unittest.mock import patch

from uptrend_client import is_data_stale


class TestIsDataStale:
    """is_data_stale should count business days, not calendar days."""

    def _mock_now(self, year, month, day, hour=12):
        return datetime(year, month, day, hour, 0, 0)

    def test_friday_to_sunday_not_stale(self):
        """Friday data checked on Sunday: 0 business days -> not stale."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 15)  # Sunday
            assert is_data_stale("2026-02-13") is False  # Friday

    def test_friday_to_monday_not_stale(self):
        """Friday data checked on Monday: 1 business day -> not stale (threshold=2)."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 16)  # Monday
            assert is_data_stale("2026-02-13") is False  # Friday

    def test_friday_to_tuesday_not_stale(self):
        """Friday data checked on Tuesday: 2 business days -> not stale (threshold=2)."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 17)  # Tuesday
            assert is_data_stale("2026-02-13") is False  # Friday

    def test_friday_to_wednesday_stale(self):
        """Friday data checked on Wednesday: 3 business days -> stale (threshold=2)."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 18)  # Wednesday
            assert is_data_stale("2026-02-13") is True  # Friday

    def test_monday_to_wednesday_not_stale(self):
        """Monday data checked on Wednesday: 2 business days -> not stale."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 18)  # Wednesday
            assert is_data_stale("2026-02-16") is False  # Monday

    def test_monday_to_thursday_stale(self):
        """Monday data checked on Thursday: 3 business days -> stale."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 19)  # Thursday
            assert is_data_stale("2026-02-16") is True  # Monday

    def test_same_day_not_stale(self):
        """Same day data -> 0 business days -> not stale."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 16)  # Monday
            assert is_data_stale("2026-02-16") is False

    def test_invalid_date_returns_true(self):
        """Invalid date string -> stale (safe default)."""
        assert is_data_stale("not-a-date") is True

    def test_custom_threshold(self):
        """Custom threshold_bdays works correctly."""
        with patch("uptrend_client.datetime") as mock_dt:
            mock_dt.strptime = datetime.strptime
            mock_dt.now.return_value = self._mock_now(2026, 2, 17)  # Tuesday
            # Friday to Tuesday = 2 bdays, threshold=1 -> stale
            assert is_data_stale("2026-02-13", threshold_bdays=1) is True
