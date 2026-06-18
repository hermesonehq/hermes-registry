"""Tests for order_builder module."""

import pytest
from order_builder import (
    build_entry_condition,
    build_post_confirm_template,
    build_pre_place_template,
    build_revalidation_advisory,
)


class TestBuildPrePlaceTemplate:
    def test_stop_limit_bracket_structure(self):
        order = build_pre_place_template(
            symbol="PWR",
            qty=10,
            signal_entry=583.32,
            worst_entry=595.40,
            stop_loss=516.81,
            take_profit=717.57,
        )
        assert order["symbol"] == "PWR"
        assert order["qty"] == 10
        assert order["side"] == "buy"
        assert order["type"] == "stop_limit"
        assert order["stop_price"] == 583.32
        assert order["limit_price"] == 595.40
        assert order["order_class"] == "bracket"
        assert order["take_profit"]["limit_price"] == 717.57
        assert order["stop_loss"]["stop_price"] == 516.81
        assert order["time_in_force"] == "day"

    def test_qty_zero_raises(self):
        with pytest.raises(ValueError, match="qty must be positive"):
            build_pre_place_template(
                symbol="X",
                qty=0,
                signal_entry=100.0,
                worst_entry=102.0,
                stop_loss=95.0,
                take_profit=110.0,
            )

    def test_stop_too_close_to_entry_raises(self):
        # stop must be >= $0.01 below signal_entry
        with pytest.raises(ValueError, match="stop_loss.*must be.*below"):
            build_pre_place_template(
                symbol="X",
                qty=10,
                signal_entry=100.0,
                worst_entry=102.0,
                stop_loss=100.0,
                take_profit=110.0,
            )

    def test_take_profit_below_worst_raises(self):
        with pytest.raises(ValueError, match="take_profit.*must be above"):
            build_pre_place_template(
                symbol="X",
                qty=10,
                signal_entry=100.0,
                worst_entry=102.0,
                stop_loss=95.0,
                take_profit=101.0,
            )


class TestBuildPostConfirmTemplate:
    def test_limit_bracket_structure(self):
        condition = build_entry_condition(pivot=583.73)
        order = build_post_confirm_template(
            symbol="PWR",
            qty=10,
            worst_entry=595.40,
            stop_loss=516.81,
            take_profit=717.57,
            entry_condition=condition,
        )
        assert order["type"] == "limit"
        assert order["limit_price"] == 595.40
        assert order["order_class"] == "bracket"
        assert order["execution_mode"] == "post_confirm"
        assert order["requires_monitor_confirmation"] is True
        assert order["entry_condition"]["bar_interval"] == "5min"
        assert order["take_profit"]["limit_price"] == 717.57
        assert order["stop_loss"]["stop_price"] == 516.81

    def test_qty_zero_raises(self):
        with pytest.raises(ValueError, match="qty must be positive"):
            build_post_confirm_template(
                symbol="X",
                qty=0,
                worst_entry=102.0,
                stop_loss=95.0,
                take_profit=110.0,
                entry_condition={},
            )


class TestBuildRevalidationAdvisory:
    def test_advisory_structure(self):
        advisory = build_revalidation_advisory(
            symbol="ANET",
            pivot=141.77,
            current_price=145.07,
            worst_entry=144.60,
        )
        assert advisory["symbol"] == "ANET"
        assert advisory["plan_type"] == "late_breakout_revalidation"
        assert advisory["next_action"].startswith("revalidate")
        assert advisory["pivot"] == 141.77
        assert advisory["current_price"] == 145.07
        assert advisory["max_entry_price"] == 144.60

    def test_no_alpaca_order_fields(self):
        advisory = build_revalidation_advisory(
            symbol="X",
            pivot=100.0,
            current_price=103.0,
            worst_entry=102.0,
        )
        assert "qty" not in advisory
        assert "type" not in advisory
        assert "order_class" not in advisory


class TestBuildEntryCondition:
    def test_machine_readable_format(self):
        cond = build_entry_condition(pivot=319.52)
        assert cond["bar_interval"] == "5min"
        assert cond["trigger"]["field"] == "close"
        assert cond["trigger"]["op"] == ">"
        assert cond["trigger"]["value"] == 319.52
        assert len(cond["checks"]) == 3

    def test_custom_thresholds(self):
        cond = build_entry_condition(
            pivot=100.0,
            close_loc_min=0.70,
            rvol_threshold=2.0,
            max_chase_pct=1.5,
        )
        close_loc_check = cond["checks"][0]
        assert close_loc_check["value"] == 0.70
        rvol_check = cond["checks"][1]
        assert rvol_check["value"] == 2.0
        chase_check = cond["checks"][2]
        assert chase_check["value"] == 1.5
