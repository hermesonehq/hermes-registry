"""Phase 1 output: JSON + Markdown.

Pure functions only — no FMP calls, no I/O. ``screen_parabolic.py`` is
responsible for fetching data, building the per-candidate dicts, and
calling :func:`build_json_report` / :func:`build_markdown_report` to render
output. Keeping the renderer pure means the schema contract is tested
against in-memory fixtures without any network dependency.
"""

from __future__ import annotations

from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"
SKILL_NAME = "parabolic-short-trade-planner"
PHASE = "screen"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def render_candidate(
    *,
    ticker: str,
    composite_result: dict,
    component_scores_raw: dict,
    raw_metrics: dict,
    state_caps: list[str],
    warnings: list[str],
    key_levels: dict,
    invalidation_checks_passed: bool,
    earnings_meta: dict | None = None,
    earnings_blackout_days: int = 2,
    market_data_as_of: str | None = None,
    market_cap_usd: float | None,
) -> dict:
    """Build one candidate dict in the v1.0 schema shape.

    ``components`` is rendered as **weighted** sub-scores so the values sum
    to the composite ``score``. The ``component_breakdown`` from the scorer
    is the source of truth.

    ``earnings_meta`` carries the four earnings fields (last/next dates,
    ``trading_days_since_earnings`` in TRADING days,
    ``earnings_within_days`` in CALENDAR days). ``earnings_blackout_days``
    is the configured threshold (CLI ``--exclude-earnings-within-days``)
    used to compute ``earnings_in_blackout_window`` here. The legacy
    ``earnings_within_2d`` field is kept (literal ≤2 calendar-day check)
    for backward compatibility with older readers.
    """
    components_weighted = {
        name: bd["weighted_score"] for name, bd in composite_result["component_breakdown"].items()
    }
    meta = earnings_meta or {}
    earnings_within_days = meta.get("earnings_within_days")
    earnings_in_blackout_window = (
        earnings_within_days is not None and earnings_within_days <= earnings_blackout_days
    )
    earnings_within_2d = earnings_within_days is not None and earnings_within_days <= 2
    return {
        "ticker": ticker,
        "rank": composite_result["grade"],
        "score": composite_result["score"],
        "state_caps": list(state_caps),
        "warnings": list(warnings),
        "components": components_weighted,
        "components_raw": component_scores_raw,
        "metrics": raw_metrics,
        "key_levels": key_levels,
        "invalidation_checks_passed": invalidation_checks_passed,
        # Earnings metadata block. Units are intentionally split:
        # ``earnings_within_days`` is CALENDAR days to the next earnings
        # event (forward, used by the hard blackout); ``trading_days_since_earnings``
        # is TRADING days since the last event (backward, used by the soft warning).
        "last_earnings_date": meta.get("last_earnings_date"),
        "next_earnings_date": meta.get("next_earnings_date"),
        "trading_days_since_earnings": meta.get("trading_days_since_earnings"),
        "earnings_within_days": earnings_within_days,
        "earnings_blackout_days": earnings_blackout_days,
        "earnings_in_blackout_window": earnings_in_blackout_window,
        "earnings_within_2d": earnings_within_2d,  # legacy fixed-name field
        "market_data_as_of": market_data_as_of,
        "market_cap_usd": market_cap_usd,
    }


def build_json_report(
    *,
    candidates: list[dict],
    mode: str,
    universe: str,
    as_of: str,
    run_date: str | None = None,
    data_source: str = "FMP",
    data_latency_sec: int = 0,
    generated_at: str | None = None,
) -> dict:
    """Top-level JSON report. ``candidates`` is a list of dicts shaped by
    :func:`render_candidate`.

    Date semantics:

    * ``as_of`` — Phase 2 planning date (= CLI ``--as-of`` / today). This
      contract is consumed by ``generate_pre_market_plan.py`` for plan IDs
      and SSR state filenames; never mutate.
    * ``run_date`` — same value as ``as_of`` (the planning date), surfaced
      under a distinct key for forward-compat readability.
    * ``generated_at`` — wallclock ISO-8601 timestamp.
    * ``market_data_as_of`` — derived from the candidates' per-symbol
      values: ``None`` when no candidates, the unique date when all share
      one, or ``max(...)`` with a top-level
      ``warnings: ["mixed_market_data_as_of"]`` annotation when mixed.
    """
    a_count = sum(1 for c in candidates if c.get("rank") == "A")
    md_dates = sorted(
        {c.get("market_data_as_of") for c in candidates if c.get("market_data_as_of")}
    )
    if not md_dates:
        market_data_as_of: str | None = None
        report_warnings: list[str] = []
    elif len(md_dates) == 1:
        market_data_as_of = md_dates[0]
        report_warnings = []
    else:
        market_data_as_of = md_dates[-1]
        report_warnings = ["mixed_market_data_as_of"]
    return {
        "schema_version": SCHEMA_VERSION,
        "skill": SKILL_NAME,
        "phase": PHASE,
        "generated_at": generated_at or _now_iso(),
        "as_of": as_of,
        "run_date": run_date if run_date is not None else as_of,
        "market_data_as_of": market_data_as_of,
        "warnings": report_warnings,
        "data_source": data_source,
        "data_latency_sec": data_latency_sec,
        "mode": mode,
        "universe": universe,
        "candidates_total": len(candidates),
        "candidates_a_rank": a_count,
        "candidates": candidates,
    }


def build_markdown_report(report: dict) -> str:
    """Render the JSON report as a Markdown watchlist."""
    lines: list[str] = []
    lines.append(f"# Parabolic Short Watchlist — {report['as_of']}")
    lines.append("")
    lines.append(f"- Mode: `{report['mode']}`")
    lines.append(f"- Universe: `{report['universe']}`")
    lines.append(
        f"- Candidates: {report['candidates_total']} (A-rank: {report['candidates_a_rank']})"
    )
    lines.append(f"- Data source: {report['data_source']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append("")
    if not report["candidates"]:
        lines.append("_No candidates met the screening thresholds._")
        return "\n".join(lines) + "\n"

    by_grade: dict[str, list[dict]] = {}
    for c in report["candidates"]:
        by_grade.setdefault(c["rank"], []).append(c)

    for grade in ("A", "B", "C", "D"):
        bucket = by_grade.get(grade, [])
        if not bucket:
            continue
        lines.append(f"## {grade}-rank ({len(bucket)})")
        lines.append("")
        for c in bucket:
            lines.append(f"### {c['ticker']} — score {c['score']}")
            metrics = c.get("metrics", {})
            r5 = metrics.get("return_5d_pct")
            ext20 = metrics.get("ext_20dma_pct")
            vol = metrics.get("volume_ratio_20d")
            atr = metrics.get("atr_14")
            r5_str = f"{r5:+.1f}%" if isinstance(r5, (int, float)) else "n/a"
            ext_str = f"{ext20:+.1f}%" if isinstance(ext20, (int, float)) else "n/a"
            vol_str = f"{vol:.1f}x" if isinstance(vol, (int, float)) else "n/a"
            atr_str = f"{atr:.2f}" if isinstance(atr, (int, float)) else "n/a"
            lines.append(
                f"- Return 5d: {r5_str} · 20DMA ext: {ext_str} · "
                f"Vol/20d: {vol_str} · ATR(14): {atr_str}"
            )
            kl = c.get("key_levels", {})
            kl_parts = []
            for k in ("dma_10", "dma_20", "dma_50", "prior_close"):
                v = kl.get(k)
                if isinstance(v, (int, float)):
                    kl_parts.append(f"{k}={v:.2f}")
            if kl_parts:
                lines.append("- Key levels: " + ", ".join(kl_parts))
            if c.get("state_caps"):
                lines.append(f"- State caps: {', '.join(c['state_caps'])}")
            if c.get("warnings"):
                lines.append(f"- Warnings: {', '.join(c['warnings'])}")
            lines.append("")
    return "\n".join(lines) + "\n"
