#!/usr/bin/env python3
"""
PEAD Screener - 4-Component Composite Scoring Engine

Combines component scores into a weighted composite (0-100).

Component Weights:
1. Setup Quality:      30%
2. Breakout Strength:  25%
3. Liquidity:          25%
4. Risk/Reward:        20%
Total: 100%

Rating Bands:
  85-100: Strong Setup  - High-conviction PEAD trade, full position size
  70-84:  Good Setup    - Solid PEAD setup, standard position size
  55-69:  Developing    - Watchlist, wait for cleaner breakout
  <55:    Weak          - Not actionable
"""

COMPONENT_WEIGHTS = {
    "setup_quality": 0.30,
    "breakout_strength": 0.25,
    "liquidity": 0.25,
    "risk_reward": 0.20,
}

COMPONENT_LABELS = {
    "setup_quality": "Setup Quality",
    "breakout_strength": "Breakout Strength",
    "liquidity": "Liquidity",
    "risk_reward": "Risk/Reward",
}


def calculate_composite_score(
    setup_score: float,
    breakout_score: float,
    liquidity_score: float,
    rr_score: float,
) -> dict:
    """
    Calculate weighted composite PEAD score.

    Args:
        setup_score: Setup Quality score (0-100)
        breakout_score: Breakout Strength score (0-100)
        liquidity_score: Liquidity score (0-100)
        rr_score: Risk/Reward score (0-100)

    Returns:
        Dict with composite_score, rating, guidance, component breakdown
    """
    component_scores = {
        "setup_quality": setup_score,
        "breakout_strength": breakout_score,
        "liquidity": liquidity_score,
        "risk_reward": rr_score,
    }

    # Calculate weighted composite
    composite = 0.0
    for key, weight in COMPONENT_WEIGHTS.items():
        composite += component_scores[key] * weight

    composite = round(composite, 1)

    # Find weakest and strongest
    weakest_key = min(component_scores, key=component_scores.get)
    strongest_key = max(component_scores, key=component_scores.get)

    # Rating
    rating_info = _get_rating(composite)

    return {
        "composite_score": composite,
        "rating": rating_info["rating"],
        "rating_description": rating_info["description"],
        "guidance": rating_info["guidance"],
        "weakest_component": COMPONENT_LABELS[weakest_key],
        "weakest_score": component_scores[weakest_key],
        "strongest_component": COMPONENT_LABELS[strongest_key],
        "strongest_score": component_scores[strongest_key],
        "component_breakdown": {
            k: {
                "score": component_scores[k],
                "weight": w,
                "weighted": round(component_scores[k] * w, 1),
                "label": COMPONENT_LABELS[k],
            }
            for k, w in COMPONENT_WEIGHTS.items()
        },
    }


def _get_rating(composite: float) -> dict:
    """Map composite score to rating and guidance."""
    if composite >= 85:
        return {
            "rating": "Strong Setup",
            "description": "High-conviction PEAD trade with all components aligned",
            "guidance": "High-conviction PEAD trade, full position size",
        }
    elif composite >= 70:
        return {
            "rating": "Good Setup",
            "description": "Solid PEAD setup with minor imperfections",
            "guidance": "Solid PEAD setup, standard position size",
        }
    elif composite >= 55:
        return {
            "rating": "Developing",
            "description": "PEAD pattern forming but not yet fully actionable",
            "guidance": "Watchlist, wait for cleaner breakout",
        }
    else:
        return {
            "rating": "Weak",
            "description": "Insufficient PEAD characteristics for trading",
            "guidance": "Not actionable",
        }
