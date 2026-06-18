"""Tests for prepare_effective_history (C1 / H5 / L11 / L12)."""

import pytest
from helpers import make_history
from history_utils import prepare_effective_history


class TestPrepareEffectiveHistory:
    def test_no_as_of_returns_history_as_is(self):
        history = make_history([100, 99, 98, 97, 96])
        effective, audit = prepare_effective_history(history, as_of=None, required_min_sessions=3)
        assert effective == history
        assert audit["as_of_resolved"] == history[0]["date"]
        assert audit["sessions_available"] == 5
        assert "insufficient_lookback" not in audit["audit_flags"]

    def test_as_of_rebases_history_to_index_zero(self):
        history = make_history([100, 99, 98, 97, 96])
        # history[2] = "2026-04-28" if start=2026-04-30
        target_date = history[2]["date"]
        effective, audit = prepare_effective_history(
            history, as_of=target_date, required_min_sessions=2
        )
        # effective[0] must be the as_of session
        assert effective[0]["date"] == target_date
        # downstream slice = history[2:] which is 3 sessions
        assert len(effective) == 3
        assert audit["as_of_resolved"] == target_date
        assert audit["sessions_available"] == 3

    def test_as_of_insufficient_lookback_adds_audit_flag(self):
        history = make_history([100, 99, 98, 97, 96])
        target_date = history[3]["date"]  # only 2 sessions remain after slice
        effective, audit = prepare_effective_history(
            history, as_of=target_date, required_min_sessions=10
        )
        assert len(effective) == 2
        assert "insufficient_lookback" in audit["audit_flags"]

    def test_as_of_not_found_raises(self):
        history = make_history([100, 99, 98])
        with pytest.raises(ValueError, match="not found"):
            prepare_effective_history(history, as_of="1999-01-01", required_min_sessions=2)

    def test_empty_history_raises(self):
        with pytest.raises(ValueError, match="empty"):
            prepare_effective_history([], as_of=None, required_min_sessions=2)
