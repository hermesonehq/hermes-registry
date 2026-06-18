"""Risk classification for individual indexes and TQQQ-aware combination."""

from __future__ import annotations

from models import IndexResult, RiskThresholds

_RISK_ORDER = {"NORMAL": 0, "CAUTION": 1, "HIGH": 2, "SEVERE": 3}


def classify_risk(
    d5: int,
    d15: int,
    d25: int,
    market_below_ma: bool | None,
    thresholds: RiskThresholds,
) -> str:
    """Classify a single index's risk level.

    market_below_ma may be True | False | None. None means MA could not be
    computed (insufficient data); SEVERE escalation is skipped in that case.
    """
    if d25 >= thresholds.severe_d25 or d15 >= thresholds.severe_d15:
        return "SEVERE"
    if market_below_ma is True and d25 >= thresholds.severe_ma_d25:
        return "SEVERE"
    if d25 >= thresholds.high_d25 or d15 >= thresholds.high_d15 or d5 >= thresholds.high_d5:
        return "HIGH"
    if d25 >= thresholds.caution_d25:
        return "CAUTION"
    return "NORMAL"


def combine_index_risks(results: list[IndexResult]) -> str:
    """Combine per-index risks into an overall risk level.

    Policy (TQQQ-aware, QQQ-weighted):
      - any SEVERE -> SEVERE
      - QQQ HIGH -> HIGH
      - QQQ NORMAL + SPY HIGH -> HIGH (broad-market degradation spills into TQQQ)
      - QQQ CAUTION + SPY in {CAUTION, HIGH} -> HIGH
      - otherwise: max risk across all indexes
    """
    if any(r.risk_level == "SEVERE" for r in results):
        return "SEVERE"

    qqq = next((r for r in results if r.symbol == "QQQ"), None)
    spy = next((r for r in results if r.symbol == "SPY"), None)

    if qqq and qqq.risk_level == "HIGH":
        return "HIGH"

    if qqq and spy:
        if qqq.risk_level == "NORMAL" and spy.risk_level == "HIGH":
            return "HIGH"
        if qqq.risk_level == "CAUTION" and spy.risk_level in ("CAUTION", "HIGH"):
            return "HIGH"

    return max((r.risk_level for r in results), key=lambda lv: _RISK_ORDER[lv])
