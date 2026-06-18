"""Risk calculator for breakout trade planner.

Derives trade prices (signal entry, worst-case entry, stop-loss) from VCP
screener data, calculates risk metrics, R-multiples, rating bands, and
position sizing. Self-contained — no external skill dependencies.
"""

from __future__ import annotations


def round_price(price: float) -> float:
    """Round price to Alpaca tick size.

    >= $1.00: 2 decimal places
    <  $1.00: 4 decimal places
    """
    if price >= 1.0:
        return round(price, 2)
    return round(price, 4)


def derive_trade_prices(
    pivot: float,
    last_contraction_low: float,
    pivot_buffer_pct: float = 0.1,
    max_chase_pct: float = 2.0,
    stop_buffer_pct: float = 1.0,
) -> tuple[float, float, float]:
    """Derive signal entry, worst-case entry, and stop-loss from VCP data.

    Args:
        pivot: Pivot price (high of last contraction).
        last_contraction_low: Low of the last contraction (stop reference).
        pivot_buffer_pct: % above pivot for buy-stop trigger.
        max_chase_pct: % above pivot for buy-limit ceiling.
        stop_buffer_pct: % below contraction low for stop-loss.

    Returns:
        (signal_entry, worst_entry, stop_loss) — all rounded to Alpaca ticks.

    Raises:
        ValueError: If inputs are non-positive or stop >= signal entry.
    """
    if pivot <= 0:
        raise ValueError(f"pivot must be positive, got {pivot}")
    if last_contraction_low <= 0:
        raise ValueError(f"last_contraction_low must be positive, got {last_contraction_low}")
    if pivot_buffer_pct > max_chase_pct:
        raise ValueError(
            f"pivot_buffer_pct ({pivot_buffer_pct}) must be <= max_chase_pct ({max_chase_pct})"
        )

    signal_entry = round_price(pivot * (1 + pivot_buffer_pct / 100))
    worst_entry = round_price(pivot * (1 + max_chase_pct / 100))
    stop_loss = round_price(last_contraction_low * (1 - stop_buffer_pct / 100))

    if stop_loss >= signal_entry:
        raise ValueError(f"stop_loss ({stop_loss}) must be below signal_entry ({signal_entry})")

    return signal_entry, worst_entry, stop_loss


def calculate_risks(
    signal_entry: float,
    worst_entry: float,
    stop_loss: float,
) -> tuple[float, float]:
    """Calculate risk percentages from both entry scenarios.

    Returns:
        (risk_pct_signal, risk_pct_worst)
    """
    risk_pct_signal = (signal_entry - stop_loss) / signal_entry * 100
    risk_pct_worst = (worst_entry - stop_loss) / worst_entry * 100
    return round(risk_pct_signal, 2), round(risk_pct_worst, 2)


def calculate_r_multiples(
    entry: float,
    stop_loss: float,
    multiples: tuple[float, ...] = (1.0, 2.0, 3.0),
) -> dict[str, float]:
    """Calculate R-multiple price targets.

    R = entry - stop_loss.
    nR target = entry + n * R.
    """
    r = entry - stop_loss
    return {f"{m}R": round_price(entry + m * r) for m in multiples}


def get_rating_band(composite_score: float) -> str:
    """Map composite score to rating band (numeric, no string comparison)."""
    if composite_score >= 90:
        return "textbook"
    if composite_score >= 80:
        return "strong"
    if composite_score >= 70:
        return "good"
    if composite_score >= 60:
        return "developing"
    return "weak"


SIZING_MULTIPLIER: dict[str, float] = {
    "textbook": 1.75,
    "strong": 1.0,
    "good": 0.75,
    "developing": 0.0,
    "weak": 0.0,
}


def get_sizing_multiplier(rating_band: str) -> float:
    """Get position sizing multiplier for a rating band."""
    return SIZING_MULTIPLIER.get(rating_band, 0.0)


def calculate_position_size(
    worst_entry: float,
    stop_loss: float,
    account_size: float,
    base_risk_pct: float,
    sizing_multiplier: float,
    max_position_pct: float = 10.0,
    max_sector_pct: float = 30.0,
    current_sector_exposure: float = 0.0,
) -> dict:
    """Calculate position size with portfolio constraints.

    Uses worst_entry as the entry price for conservative sizing.
    Self-contained fixed-fractional sizing with constraint checks.

    Returns:
        Dict with shares, position_value, risk_dollars, binding_constraint.
    """
    effective_risk_pct = base_risk_pct * sizing_multiplier
    if effective_risk_pct <= 0:
        return {
            "shares": 0,
            "position_value": 0.0,
            "risk_dollars": 0.0,
            "effective_risk_pct": 0.0,
            "binding_constraint": "sizing_multiplier_zero",
        }

    # Fixed fractional: shares = dollar_risk / risk_per_share
    risk_per_share = worst_entry - stop_loss
    dollar_risk = account_size * effective_risk_pct / 100
    risk_shares = int(dollar_risk / risk_per_share)

    # Portfolio constraints
    candidates = [risk_shares]
    constraints: list[dict] = []
    binding: str | None = None

    # Max position % constraint
    max_by_pos = int(account_size * max_position_pct / 100 / worst_entry)
    constraints.append(
        {
            "type": "max_position_pct",
            "limit": max_position_pct,
            "max_shares": max_by_pos,
            "binding": False,
        }
    )
    candidates.append(max_by_pos)

    # Max sector % constraint
    remaining_pct = max_sector_pct - current_sector_exposure
    remaining_dollars = max(0.0, remaining_pct / 100 * account_size)
    max_by_sector = max(0, int(remaining_dollars / worst_entry))
    constraints.append(
        {
            "type": "max_sector_pct",
            "limit": max_sector_pct,
            "current": current_sector_exposure,
            "max_shares": max_by_sector,
            "binding": False,
        }
    )
    candidates.append(max_by_sector)

    final_shares = max(0, min(candidates))

    # Identify binding constraint
    for c in constraints:
        if c["max_shares"] == final_shares and final_shares < risk_shares:
            c["binding"] = True
            binding = c["type"]

    position_value = round(final_shares * worst_entry, 2)
    risk_dollars = round(final_shares * risk_per_share, 2)

    return {
        "shares": final_shares,
        "position_value": position_value,
        "risk_dollars": risk_dollars,
        "effective_risk_pct": round(effective_risk_pct, 4),
        "binding_constraint": binding,
        "constraints_applied": constraints,
    }
