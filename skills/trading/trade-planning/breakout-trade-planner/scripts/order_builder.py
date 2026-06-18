"""Alpaca order template builder for breakout trade planner.

Generates stop-limit bracket templates (pre_place) and limit bracket
templates (post_confirm) for Pre-breakout candidates. Breakout candidates
get revalidation advisories only (no order template).
"""

from __future__ import annotations


def build_pre_place_template(
    symbol: str,
    qty: int,
    signal_entry: float,
    worst_entry: float,
    stop_loss: float,
    take_profit: float,
    time_in_force: str = "day",
) -> dict:
    """Build a stop-limit bracket order template for pre-placement.

    This template is placed on the market and auto-triggers when price
    reaches signal_entry (buy stop). Limit at worst_entry prevents chasing.

    Raises:
        ValueError: On invalid inputs.
    """
    _validate_order_params(qty, signal_entry, worst_entry, stop_loss, take_profit)

    return {
        "execution_mode": "pre_place",
        "requires_monitor_confirmation": False,
        "symbol": symbol,
        "qty": qty,
        "side": "buy",
        "type": "stop_limit",
        "stop_price": signal_entry,
        "limit_price": worst_entry,
        "time_in_force": time_in_force,
        "order_class": "bracket",
        "take_profit": {"limit_price": take_profit},
        "stop_loss": {"stop_price": stop_loss},
    }


def build_post_confirm_template(
    symbol: str,
    qty: int,
    worst_entry: float,
    stop_loss: float,
    take_profit: float,
    entry_condition: dict,
    time_in_force: str = "day",
) -> dict:
    """Build a limit bracket order template for post-confirmation mode.

    This template is sent after the breakout-monitor confirms 5-min candle
    conditions (close > pivot, close_loc >= 0.60, RVOL >= 1.5).

    Raises:
        ValueError: On invalid inputs.
    """
    if qty <= 0:
        raise ValueError(f"qty must be positive, got {qty}")
    if (worst_entry - stop_loss) < 0.01:
        raise ValueError(
            f"stop_loss ({stop_loss}) must be >= $0.01 below worst_entry ({worst_entry})"
        )
    if take_profit <= worst_entry:
        raise ValueError(f"take_profit ({take_profit}) must be above worst_entry ({worst_entry})")

    return {
        "execution_mode": "post_confirm",
        "requires_monitor_confirmation": True,
        "entry_condition": entry_condition,
        "symbol": symbol,
        "qty": qty,
        "side": "buy",
        "type": "limit",
        "limit_price": worst_entry,
        "time_in_force": time_in_force,
        "order_class": "bracket",
        "take_profit": {"limit_price": take_profit},
        "stop_loss": {"stop_price": stop_loss},
    }


def build_revalidation_advisory(
    symbol: str,
    pivot: float,
    current_price: float,
    worst_entry: float,
) -> dict:
    """Build an advisory for Breakout-state candidates (no order template).

    These candidates already crossed the pivot and need live revalidation
    before any order can be placed.
    """
    return {
        "symbol": symbol,
        "plan_type": "late_breakout_revalidation",
        "next_action": "revalidate live price/5min confirmation before any order",
        "pivot": pivot,
        "current_price": current_price,
        "max_entry_price": worst_entry,
    }


def build_entry_condition(
    pivot: float,
    close_loc_min: float = 0.60,
    rvol_threshold: float = 1.5,
    max_chase_pct: float = 2.0,
) -> dict:
    """Build a machine-readable entry condition for the post_confirm template."""
    return {
        "bar_interval": "5min",
        "trigger": {"field": "close", "op": ">", "value": pivot},
        "checks": [
            {"field": "close_loc", "op": ">=", "value": close_loc_min},
            {"field": "tod_rvol", "op": ">=", "value": rvol_threshold},
            {"field": "price_vs_pivot_pct", "op": "<=", "value": max_chase_pct},
        ],
    }


def _validate_order_params(
    qty: int,
    signal_entry: float,
    worst_entry: float,
    stop_loss: float,
    take_profit: float,
) -> None:
    """Shared validation for order templates."""
    if qty <= 0:
        raise ValueError(f"qty must be positive, got {qty}")
    if (signal_entry - stop_loss) < 0.01:
        raise ValueError(
            f"stop_loss ({stop_loss}) must be >= $0.01 below signal_entry ({signal_entry})"
        )
    if take_profit <= worst_entry:
        raise ValueError(f"take_profit ({take_profit}) must be above worst_entry ({worst_entry})")
