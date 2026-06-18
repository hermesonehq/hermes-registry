#!/usr/bin/env python3
"""
MA50 Position Calculator for Earnings Trade Analyzer

Calculates the current price position relative to the 50-day Simple Moving Average.
SMA50 is computed from daily close prices directly.

Scoring (10% weight):
  distance >= 10%: 100
  distance >= 5%:   80
  distance >= 0%:   60
  distance >= -5%:  35
  distance < -5%:   15
"""


def _score_ma50_distance(distance_pct: float) -> float:
    """Score the distance from MA50.

    Args:
        distance_pct: Percentage distance from MA50 (positive = above)

    Returns:
        Score from 0 to 100.
    """
    if distance_pct >= 10.0:
        return 100.0
    elif distance_pct >= 5.0:
        return 80.0
    elif distance_pct >= 0.0:
        return 60.0
    elif distance_pct >= -5.0:
        return 35.0
    else:
        return 15.0


def calculate_ma50_position(daily_prices: list[dict]) -> dict:
    """
    Calculate current price position relative to 50-day SMA.

    Args:
        daily_prices: list of dicts with 'close' (most-recent-first)

    Returns:
        dict with:
          - ma50: float
          - distance_pct: float (positive = above MA)
          - above_ma50: bool
          - score: float (0-100)
          - warning: str (optional)
    """
    if len(daily_prices) < 50:
        return {
            "ma50": 0.0,
            "distance_pct": 0.0,
            "above_ma50": False,
            "score": 0.0,
            "warning": f"Insufficient data for MA50: {len(daily_prices)} days available, 50 required",
        }

    # Calculate SMA50 from the first 50 close prices (most-recent-first)
    closes_50 = [daily_prices[i]["close"] for i in range(50)]
    ma50 = sum(closes_50) / 50.0

    current_price = daily_prices[0]["close"]

    if ma50 == 0:
        return {
            "ma50": 0.0,
            "distance_pct": 0.0,
            "above_ma50": False,
            "score": 0.0,
            "warning": "MA50 is zero",
        }

    distance_pct = ((current_price / ma50) - 1.0) * 100.0
    above_ma50 = distance_pct >= 0
    score = _score_ma50_distance(distance_pct)

    result = {
        "ma50": round(ma50, 2),
        "distance_pct": round(distance_pct, 2),
        "above_ma50": above_ma50,
        "score": score,
    }
    return result
