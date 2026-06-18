#!/usr/bin/env python3
"""
MA200 Position Calculator for Earnings Trade Analyzer

Calculates the current price position relative to the 200-day Simple Moving Average.
SMA200 is computed from daily close prices directly.

Scoring (15% weight):
  distance >= 20%:  100
  distance >= 10%:   85
  distance >= 5%:    70
  distance >= 0%:    55
  distance >= -5%:   35
  distance < -5%:    15
"""


def _score_ma200_distance(distance_pct: float) -> float:
    """Score the distance from MA200.

    Args:
        distance_pct: Percentage distance from MA200 (positive = above)

    Returns:
        Score from 0 to 100.
    """
    if distance_pct >= 20.0:
        return 100.0
    elif distance_pct >= 10.0:
        return 85.0
    elif distance_pct >= 5.0:
        return 70.0
    elif distance_pct >= 0.0:
        return 55.0
    elif distance_pct >= -5.0:
        return 35.0
    else:
        return 15.0


def calculate_ma200_position(daily_prices: list[dict]) -> dict:
    """
    Calculate current price position relative to 200-day SMA.
    Compute SMA200 from daily_prices close values.

    Args:
        daily_prices: list of dicts with 'close' (most-recent-first)

    Returns:
        dict with:
          - ma200: float
          - distance_pct: float (positive = above MA)
          - above_ma200: bool
          - score: float (0-100)
          - warning: str (optional)
    """
    if len(daily_prices) < 200:
        return {
            "ma200": 0.0,
            "distance_pct": 0.0,
            "above_ma200": False,
            "score": 0.0,
            "warning": f"Insufficient data for MA200: {len(daily_prices)} days available, 200 required",
        }

    # Calculate SMA200 from the first 200 close prices (most-recent-first)
    closes_200 = [daily_prices[i]["close"] for i in range(200)]
    ma200 = sum(closes_200) / 200.0

    current_price = daily_prices[0]["close"]

    if ma200 == 0:
        return {
            "ma200": 0.0,
            "distance_pct": 0.0,
            "above_ma200": False,
            "score": 0.0,
            "warning": "MA200 is zero",
        }

    distance_pct = ((current_price / ma200) - 1.0) * 100.0
    above_ma200 = distance_pct >= 0
    score = _score_ma200_distance(distance_pct)

    result = {
        "ma200": round(ma200, 2),
        "distance_pct": round(distance_pct, 2),
        "above_ma200": above_ma200,
        "score": score,
    }
    return result
