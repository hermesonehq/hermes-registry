"""Risk-level -> portfolio action mapping for TQQQ and QQQ.

TQQQ is more aggressive (3x daily leverage), so its exposure cuts faster.
"""

from __future__ import annotations

from models import PortfolioAction

_TQQQ_POLICY = {
    "NORMAL": ("HOLD_OR_FOLLOW_BASE_STRATEGY", 100, None),
    "CAUTION": ("AVOID_NEW_ADDS", 75, 7),
    "HIGH": ("REDUCE_EXPOSURE", 50, 5),
    "SEVERE": ("CLOSE_TQQQ_OR_HEDGE", 25, 3),
}

_QQQ_POLICY = {
    "NORMAL": ("HOLD_OR_FOLLOW_BASE_STRATEGY", 100, None),
    "CAUTION": ("AVOID_NEW_ADDS", 100, 8),  # don't reduce, just stop adding
    "HIGH": ("REDUCE_EXPOSURE", 75, 6),
    "SEVERE": ("REDUCE_EXPOSURE_OR_HEDGE", 50, 5),
}

_RATIONALE = {
    "TQQQ": (
        "TQQQ targets 3x daily Nasdaq returns. Distribution Day clusters "
        "amplify drawdown risk via daily compounding, so exposure is cut "
        "faster than for unleveraged QQQ."
    ),
    "QQQ": (
        "QQQ tracks Nasdaq-100 1x. Exposure cuts are smaller than TQQQ but "
        "still respond to clustered distribution."
    ),
}

_ALTERNATIVES_TQQQ = {
    "HIGH": "SWITCH_PARTIAL_TO_QQQ",
    "SEVERE": "SWITCH_TO_QQQ_OR_CASH",
}


def generate_portfolio_action(
    risk_level: str,
    instrument: str,
    current_exposure_pct: int,
    base_trailing_stop_pct: int,
) -> PortfolioAction:
    """Return the recommended portfolio action for the given risk level."""
    instrument_upper = instrument.upper()
    policy = _TQQQ_POLICY if instrument_upper == "TQQQ" else _QQQ_POLICY
    if risk_level not in policy:
        raise ValueError(f"Unknown risk_level: {risk_level}")

    action, target, cap = policy[risk_level]
    if cap is None:
        trailing_stop = base_trailing_stop_pct
    else:
        trailing_stop = min(base_trailing_stop_pct, cap)

    alternative = _ALTERNATIVES_TQQQ.get(risk_level) if instrument_upper == "TQQQ" else None

    return PortfolioAction(
        instrument=instrument_upper,
        recommended_action=action,
        current_exposure_pct=current_exposure_pct,
        target_exposure_pct=target,
        exposure_delta_pct=target - current_exposure_pct,
        trailing_stop_pct=trailing_stop,
        alternative_action=alternative,
        rationale=_RATIONALE.get(instrument_upper, ""),
    )
