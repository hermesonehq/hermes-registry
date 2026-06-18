#!/usr/bin/env python3
"""
Execution State Engine - Determines whether a VCP candidate is actionable now.

Separates "strong pattern" from "buy-able now":
- Structure Quality (composite_score): How good is the VCP pattern?
- Execution State: Can I actually enter at this price?

States (highest to lowest precedence):
  Invalid      - Price below SMA50 and SMA200 (not in Stage 2)
  Damaged      - Price below stop level or SMA50 violated
  Overextended - Too far from pivot or SMA200 (chase risk)
  Extended     - 5-10% above pivot (elevated risk)
  Early-post-breakout - 3-5% above pivot
  Breakout     - Within 3% of pivot with volume confirmation
  Pre-breakout - Within or below pivot (ideal entry zone)
"""

from typing import Optional


def compute_execution_state(
    distance_from_pivot_pct: Optional[float],
    price: float,
    sma50: Optional[float],
    sma200: Optional[float],
    sma200_distance_pct: Optional[float],
    last_contraction_low: Optional[float],
    breakout_volume: bool,
    max_sma200_extension: float = 50.0,
) -> dict:
    """
    Determine execution state from pre-calculated data.

    Decision tree evaluated top-to-bottom (first match wins):
    1. price < sma50 < sma200            → Invalid
    2. price < last_contraction_low      → Damaged
    3. price < sma50                     → Damaged
    4. sma200_distance > max_sma200_ext  → Overextended
    5. pivot_distance > 10%              → Overextended
    6. pivot_distance 5-10%              → Extended
    7. pivot_distance 3-5%              → Early-post-breakout
    8. pivot_distance 0-3% + volume      → Breakout
    9. pivot_distance 0-3%              → Early-post-breakout (volume unconfirmed)
    10. pivot_distance < 0%              → Pre-breakout

    Args:
        distance_from_pivot_pct: % distance from pivot (positive = above, negative = below)
        price: Current stock price
        sma50: 50-day simple moving average
        sma200: 200-day simple moving average
        sma200_distance_pct: % above SMA200 (positive = above)
        last_contraction_low: Low of the last VCP contraction (stop level)
        breakout_volume: True if today's volume confirms a breakout (1.5x+ avg)
        max_sma200_extension: Max % above SMA200 before Overextended (default 50.0)

    Returns:
        dict with "state" (str) and "reasons" (list[str])
    """
    reasons = []

    # Rule 1: Invalid - not in Stage 2 (price below both moving averages)
    if sma50 is not None and sma200 is not None:
        if price < sma50 and sma50 < sma200:
            reasons.append(f"Price ${price:.2f} < SMA50 ${sma50:.2f} < SMA200 ${sma200:.2f}")
            return {"state": "Invalid", "reasons": reasons}

    # Rule 2: Damaged - stop level violated
    if last_contraction_low is not None and last_contraction_low > 0:
        if price < last_contraction_low:
            reasons.append(
                f"Price ${price:.2f} below last contraction low ${last_contraction_low:.2f}"
            )
            return {"state": "Damaged", "reasons": reasons}

    # Rule 3: Damaged - price below SMA50 (Stage 2 violation)
    if sma50 is not None and price < sma50:
        reasons.append(f"Price ${price:.2f} below SMA50 ${sma50:.2f}")
        return {"state": "Damaged", "reasons": reasons}

    # Rule 4: Overextended - too far above SMA200
    if sma200_distance_pct is not None and sma200_distance_pct > max_sma200_extension:
        reasons.append(
            f"SMA200 distance {sma200_distance_pct:.1f}% > max {max_sma200_extension:.0f}%"
        )
        return {"state": "Overextended", "reasons": reasons}

    # Rules 5-10 require pivot distance
    if distance_from_pivot_pct is None:
        reasons.append("No pivot available")
        return {"state": "Pre-breakout", "reasons": reasons}

    # Rule 5: Overextended - more than 10% above pivot
    if distance_from_pivot_pct > 10.0:
        reasons.append(f"+{distance_from_pivot_pct:.1f}% above pivot (> 10%)")
        return {"state": "Overextended", "reasons": reasons}

    # Rule 6: Extended - 5-10% above pivot
    if distance_from_pivot_pct > 5.0:
        reasons.append(f"+{distance_from_pivot_pct:.1f}% above pivot (5-10% zone)")
        return {"state": "Extended", "reasons": reasons}

    # Rule 7: Early-post-breakout - 3-5% above pivot
    if distance_from_pivot_pct > 3.0:
        reasons.append(f"+{distance_from_pivot_pct:.1f}% above pivot (3-5% zone)")
        return {"state": "Early-post-breakout", "reasons": reasons}

    # Rules 8-9: Within 3% of pivot (or below)
    if distance_from_pivot_pct >= 0.0:
        if breakout_volume:
            reasons.append(f"+{distance_from_pivot_pct:.1f}% above pivot with volume confirmation")
            return {"state": "Breakout", "reasons": reasons}
        else:
            reasons.append(f"+{distance_from_pivot_pct:.1f}% above pivot (volume unconfirmed)")
            return {"state": "Early-post-breakout", "reasons": reasons}

    # Rule 10: Below pivot
    reasons.append(f"{distance_from_pivot_pct:.1f}% below pivot (forming pattern)")
    return {"state": "Pre-breakout", "reasons": reasons}


# State ordering for cap enforcement (lower index = more restrictive)
STATE_ORDER = [
    "Invalid",
    "Damaged",
    "Overextended",
    "Extended",
    "Early-post-breakout",
    "Breakout",
    "Pre-breakout",
]

# Maximum rating allowed per execution state
STATE_MAX_RATING = {
    "Invalid": "No VCP",
    "Damaged": "No VCP",
    "Overextended": "Weak VCP",
    "Extended": "Developing VCP",
    "Early-post-breakout": "Strong VCP",  # Cap: breakout in progress, not yet confirmed
    "Breakout": None,  # No cap
    "Pre-breakout": None,  # No cap
}

# Rating hierarchy (higher index = higher rating)
RATING_ORDER = [
    "No VCP",
    "Weak VCP",
    "Developing VCP",
    "Good VCP",
    "Strong VCP",
    "Textbook VCP",
]


def apply_state_cap(rating: str, execution_state: str) -> tuple[str, bool]:
    """
    Apply the State Cap: if execution state restricts the maximum allowed rating,
    downgrade the rating accordingly.

    Args:
        rating: Current rating string
        execution_state: Execution state string

    Returns:
        (capped_rating: str, cap_applied: bool)
    """
    max_rating = STATE_MAX_RATING.get(execution_state)
    if max_rating is None:
        return rating, False  # No cap for this state

    current_idx = RATING_ORDER.index(rating) if rating in RATING_ORDER else 0
    max_idx = RATING_ORDER.index(max_rating) if max_rating in RATING_ORDER else 0

    if current_idx > max_idx:
        return max_rating, True

    return rating, False
