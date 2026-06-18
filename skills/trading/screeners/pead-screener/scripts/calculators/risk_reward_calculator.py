#!/usr/bin/env python3
"""
Risk/Reward Calculator for PEAD Screener

Calculates risk/reward metrics for PEAD trade setups.

Entry: current_price (or slightly above red candle high)
Stop: red_candle['low']
Target: entry + (entry - stop) * target_multiplier

Scoring (20% weight in composite):
- R:R >= 3.0: 100
- R:R >= 2.5:  85
- R:R >= 2.0:  70
- R:R >= 1.5:  50
- R:R < 1.5:   25
"""


def calculate_risk_reward(
    current_price: float,
    red_candle: dict,
    target_multiplier: float = 2.0,
) -> dict:
    """
    Calculate risk/reward for a PEAD trade.

    Args:
        current_price: Current stock price (entry level)
        red_candle: Red candle dict with 'high' and 'low' keys
        target_multiplier: Target as multiple of risk (default: 2.0)

    Returns:
        {
            "entry_price": float,
            "stop_price": float,
            "target_price": float,
            "risk_pct": float,
            "reward_pct": float,
            "risk_reward_ratio": float,
            "score": float  # 0-100
        }
    """
    result = {
        "entry_price": current_price,
        "stop_price": 0.0,
        "target_price": 0.0,
        "risk_pct": 0.0,
        "reward_pct": 0.0,
        "risk_reward_ratio": 0.0,
        "score": 25.0,
    }

    if not red_candle or current_price <= 0:
        return result

    stop_price = red_candle["low"]
    if stop_price <= 0 or stop_price >= current_price:
        return result

    # Calculate risk and reward
    risk = current_price - stop_price
    reward = risk * target_multiplier
    target_price = current_price + reward

    risk_pct = (risk / current_price) * 100
    reward_pct = (reward / current_price) * 100

    # Risk/Reward ratio
    rr_ratio = reward / risk if risk > 0 else 0.0

    result["entry_price"] = round(current_price, 2)
    result["stop_price"] = round(stop_price, 2)
    result["target_price"] = round(target_price, 2)
    result["risk_pct"] = round(risk_pct, 2)
    result["reward_pct"] = round(reward_pct, 2)
    result["risk_reward_ratio"] = round(rr_ratio, 2)

    # Score based on R:R ratio
    if rr_ratio >= 3.0:
        result["score"] = 100.0
    elif rr_ratio >= 2.5:
        result["score"] = 85.0
    elif rr_ratio >= 2.0:
        result["score"] = 70.0
    elif rr_ratio >= 1.5:
        result["score"] = 50.0
    else:
        result["score"] = 25.0

    return result
