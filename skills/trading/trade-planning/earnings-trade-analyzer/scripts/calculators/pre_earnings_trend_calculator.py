#!/usr/bin/env python3
"""
Pre-Earnings Trend Calculator for Earnings Trade Analyzer

Calculates the 20-day price return before the earnings date to assess
the stock's momentum heading into the earnings report.

Scoring (30% weight):
  return >= 15%: 100
  return >= 10%:  85
  return >= 5%:   70
  return >= 0%:   50
  return >= -5%:  30
  return < -5%:   15
"""


def _find_index_by_date(daily_prices: list[dict], target_date: str) -> int:
    """Find the index of target_date in daily_prices (most-recent-first).

    Returns:
        Index if found, -1 otherwise.
    """
    for i, bar in enumerate(daily_prices):
        if bar.get("date") == target_date:
            return i
    return -1


def _score_trend(return_pct: float) -> float:
    """Score the 20-day pre-earnings return.

    Args:
        return_pct: 20-day return percentage (e.g. 8.5 for 8.5%)

    Returns:
        Score from 0 to 100.
    """
    if return_pct >= 15.0:
        return 100.0
    elif return_pct >= 10.0:
        return 85.0
    elif return_pct >= 5.0:
        return 70.0
    elif return_pct >= 0.0:
        return 50.0
    elif return_pct >= -5.0:
        return 30.0
    else:
        return 15.0


def calculate_pre_earnings_trend(daily_prices: list[dict], earnings_date: str) -> dict:
    """
    Calculate 20-day return before earnings date.

    Args:
        daily_prices: list of dicts with 'date', 'close' (most-recent-first)
        earnings_date: YYYY-MM-DD string

    Returns:
        dict with:
          - return_20d_pct: float
          - trend_direction: 'up' or 'down'
          - score: float (0-100)
          - warning: str (optional)
    """
    earnings_idx = _find_index_by_date(daily_prices, earnings_date)

    if earnings_idx == -1:
        return {
            "return_20d_pct": 0.0,
            "trend_direction": "up",
            "score": 0.0,
            "warning": f"Earnings date {earnings_date} not found in price data",
        }

    # 20 trading days before earnings date
    # In most-recent-first, 20 days before is at earnings_idx + 20
    lookback_idx = earnings_idx + 20

    if lookback_idx >= len(daily_prices):
        return {
            "return_20d_pct": 0.0,
            "trend_direction": "up",
            "score": 0.0,
            "warning": "Insufficient data for 20-day pre-earnings trend calculation",
        }

    close_at_earnings = daily_prices[earnings_idx]["close"]
    close_20d_before = daily_prices[lookback_idx]["close"]

    if close_20d_before == 0:
        return {
            "return_20d_pct": 0.0,
            "trend_direction": "up",
            "score": 0.0,
            "warning": "Price 20 days before earnings is zero",
        }

    return_20d_pct = ((close_at_earnings / close_20d_before) - 1.0) * 100.0
    trend_direction = "up" if return_20d_pct >= 0 else "down"
    score = _score_trend(return_20d_pct)

    result = {
        "return_20d_pct": round(return_20d_pct, 2),
        "trend_direction": trend_direction,
        "score": score,
    }
    return result
