#!/usr/bin/env python3
"""
Pivot Proximity Calculator - Breakout Distance & Risk Analysis

Calculates how close the current price is to the VCP pivot (breakout) point
and computes the risk profile for a potential trade.

Distance-priority scoring (Minervini: do not chase >5% above pivot):
- 0-3% above pivot:  90 (+ volume bonus 10 = 100 BREAKOUT CONFIRMED)
- 3-5% above:        65 (+ volume bonus 10 = 75)
- 5-10% above:       50 (no volume bonus)
- 10-20% above:      35 (no volume bonus)
- >20% above:        20 (no volume bonus)
- 0 to -2% below:    90 (AT PIVOT)
- -2% to -5%:        75 (NEAR PIVOT)
- -5% to -8%:        60 (APPROACHING)
- -8% to -10%:       45 (DEVELOPING)
- -10% to -15%:      30 (EARLY)
- < -15%:            10 (FAR FROM PIVOT)

Also calculates:
- Stop-loss price (below last contraction low)
- Risk % per share (entry to stop distance)
"""

from typing import Optional


def calculate_pivot_proximity(
    current_price: float,
    pivot_price: Optional[float],
    last_contraction_low: Optional[float] = None,
    breakout_volume: bool = False,
) -> dict:
    """
    Calculate proximity to pivot point and risk metrics.

    Args:
        current_price: Current stock price
        pivot_price: The pivot (breakout) price from VCP pattern
        last_contraction_low: Low of the last contraction (for stop-loss)
        breakout_volume: Whether current volume is 1.5x+ above average

    Returns:
        Dict with score (0-100), distance_pct, stop_loss, risk_pct
    """
    if not pivot_price or pivot_price <= 0:
        return {
            "score": 0,
            "distance_from_pivot_pct": None,
            "stop_loss_price": None,
            "risk_pct": None,
            "trade_status": "NO PIVOT",
            "error": "No valid pivot price",
        }

    if current_price <= 0:
        return {
            "score": 0,
            "distance_from_pivot_pct": None,
            "stop_loss_price": None,
            "risk_pct": None,
            "trade_status": "INVALID PRICE",
            "error": "Invalid current price",
        }

    # Distance from pivot (negative = below pivot)
    distance_pct = (current_price - pivot_price) / pivot_price * 100

    # Determine trade status and score (distance-priority)
    if distance_pct > 20:
        score = 20
        trade_status = "OVEREXTENDED - Do not chase"
    elif distance_pct > 10:
        score = 35
        trade_status = "EXTENDED - Very high chase risk"
    elif distance_pct > 5:
        score = 50
        trade_status = "EXTENDED - High chase risk"
    elif distance_pct > 3:
        score = 65
        trade_status = "EXTENDED - Moderate chase risk"
    elif distance_pct > 0:
        score = 90
        trade_status = "ABOVE PIVOT (within 3%)"
    elif distance_pct >= -2:
        score = 90
        trade_status = "AT PIVOT (within 2%)"
    elif distance_pct >= -5:
        score = 75
        trade_status = "NEAR PIVOT (2-5% below)"
    elif distance_pct >= -8:
        score = 60
        trade_status = "APPROACHING (5-8% below)"
    elif distance_pct >= -10:
        score = 45
        trade_status = "DEVELOPING (8-10% below)"
    elif distance_pct >= -15:
        score = 30
        trade_status = "EARLY (10-15% below)"
    else:
        score = 10
        trade_status = "FAR FROM PIVOT (>15% below)"

    # Volume confirmation bonus (only for 0-5% above pivot)
    if breakout_volume and distance_pct > 0:
        if distance_pct <= 3:
            score += 10
            trade_status = "BREAKOUT CONFIRMED"
        elif distance_pct <= 5:
            score += 10
            trade_status += " (vol confirmed)"

    # Calculate stop-loss and risk
    stop_loss_price = None
    risk_pct = None

    if last_contraction_low and last_contraction_low > 0:
        # Stop-loss is 1-2% below the last contraction low
        stop_loss_price = round(last_contraction_low * 0.99, 2)

        # Risk per share from current price to stop
        if current_price > stop_loss_price:
            risk_pct = round((current_price - stop_loss_price) / current_price * 100, 2)
        else:
            # Price already below stop level — setup is invalidated
            risk_pct = None
            trade_status = "BELOW STOP LEVEL"
            score = 0

    return {
        "score": score,
        "distance_from_pivot_pct": round(distance_pct, 2),
        "pivot_price": round(pivot_price, 2),
        "stop_loss_price": stop_loss_price,
        "risk_pct": risk_pct,
        "trade_status": trade_status,
        "error": None,
    }
