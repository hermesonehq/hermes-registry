#!/usr/bin/env python3
"""
PEAD Stock Screener - Main Orchestrator

Screens post-earnings gap-up stocks for Post-Earnings Announcement Drift (PEAD)
patterns using weekly candle analysis.

Two input modes:
  Mode A: FMP earnings calendar -> profile batch -> gap filter -> weekly analysis
  Mode B: earnings-trade-analyzer JSON output -> grade filter -> weekly analysis

Usage:
    # Mode A: FMP earnings calendar (default)
    python3 screen_pead.py --api-key YOUR_KEY --output-dir reports/

    # Mode B: From earnings-trade-analyzer JSON
    python3 screen_pead.py --candidates-json reports/earnings_analysis.json --output-dir reports/

Output:
    - JSON: pead_screener_YYYY-MM-DD_HHMMSS.json
    - Markdown: pead_screener_YYYY-MM-DD_HHMMSS.md
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from calculators.breakout_calculator import calculate_breakout
from calculators.liquidity_calculator import calculate_liquidity
from calculators.risk_reward_calculator import calculate_risk_reward
from calculators.weekly_candle_calculator import analyze_weekly_pattern, daily_to_weekly
from fmp_client import ApiCallBudgetExceeded, FMPClient
from report_generator import generate_json_report, generate_markdown_report
from scorer import calculate_composite_score

logger = logging.getLogger(__name__)


def calculate_price_gap(daily_prices: list[dict], earnings_date: str, timing: str) -> float:
    """Calculate actual price gap from daily OHLCV data.

    BMO: gap = (open[earnings_date] / close[prev_day]) - 1
    AMC/unknown: gap = (open[next_day] / close[earnings_date]) - 1

    Args:
        daily_prices: Most-recent-first daily price data
        earnings_date: YYYY-MM-DD string
        timing: 'bmo', 'amc', or empty/unknown

    Returns:
        Gap percentage (e.g. 6.3 for 6.3%), or 0.0 if calculation not possible.
    """
    # Find earnings date index
    earnings_idx = -1
    for i, bar in enumerate(daily_prices):
        if bar.get("date") == earnings_date:
            earnings_idx = i
            break

    if earnings_idx == -1:
        return 0.0

    timing_lower = (timing or "").lower().strip()

    if timing_lower == "bmo":
        # BMO: gap = open[earnings_date] / close[prev_day] - 1
        prev_idx = earnings_idx + 1  # most-recent-first
        if prev_idx >= len(daily_prices):
            return 0.0
        base_price = daily_prices[prev_idx].get("close", 0)
        gap_price = daily_prices[earnings_idx].get("open", 0)
    else:
        # AMC or unknown: gap = open[next_day] / close[earnings_date] - 1
        next_idx = earnings_idx - 1  # most-recent-first
        if next_idx < 0:
            return 0.0
        base_price = daily_prices[earnings_idx].get("close", 0)
        gap_price = daily_prices[next_idx].get("open", 0)

    if not base_price:
        return 0.0

    return round(((gap_price / base_price) - 1.0) * 100.0, 2)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="PEAD Stock Screener - Post-Earnings Announcement Drift"
    )

    # Common arguments
    parser.add_argument(
        "--api-key", help="FMP API key (defaults to FMP_API_KEY environment variable)"
    )
    parser.add_argument(
        "--watch-weeks",
        type=int,
        default=5,
        help="Monitoring period in weeks after earnings (default: 5)",
    )
    parser.add_argument(
        "--max-api-calls",
        type=int,
        default=200,
        help="API call budget (default: 200)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Top results to include in report (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/",
        help="Output directory for reports (default: reports/)",
    )

    # Mode A arguments
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=14,
        help="Days back for earnings calendar (Mode A, default: 14)",
    )
    parser.add_argument(
        "--min-gap",
        type=float,
        default=3.0,
        help="Minimum earnings gap %% (Mode A, default: 3.0)",
    )
    parser.add_argument(
        "--min-market-cap",
        type=float,
        default=500_000_000,
        help="Minimum market cap (Mode A, default: 500000000)",
    )

    # Mode B arguments
    parser.add_argument(
        "--candidates-json",
        help="Path to earnings-trade-analyzer JSON output (Mode B)",
    )
    parser.add_argument(
        "--min-grade",
        default="B",
        choices=["A", "B", "C", "D"],
        help="Minimum grade filter (Mode B, default: B)",
    )

    return parser.parse_args()


def validate_input_json(data: dict) -> list[dict]:
    """
    Validate earnings-trade-analyzer JSON output for Mode B.

    Checks:
    1. schema_version == "1.0" -> ValueError if mismatch
    2. 'results' key exists and is a list
    3. Each result has required fields: symbol, earnings_date, earnings_timing, gap_pct, grade
    4. Missing fields -> warn + skip that record (don't abort unless ALL fail)

    Returns:
        Validated list of result dicts.

    Raises:
        ValueError: If schema_version != "1.0" or all records are invalid
    """
    # Check schema version
    schema_version = data.get("schema_version", "")
    if schema_version != "1.0":
        raise ValueError(
            f"Schema version mismatch: expected '1.0', got '{schema_version}'. "
            "This input may be from an incompatible version of earnings-trade-analyzer."
        )

    # Check results key
    results = data.get("results")
    if not isinstance(results, list):
        raise ValueError("Input JSON missing 'results' key or 'results' is not a list")

    required_fields = ["symbol", "earnings_date", "earnings_timing", "gap_pct", "grade"]
    valid_timings = {"bmo", "amc", "unknown"}
    valid_grades = {"A", "B", "C", "D"}
    validated = []

    for i, record in enumerate(results):
        # Check required field existence
        missing = [f for f in required_fields if f not in record]
        if missing:
            logger.warning(
                "Skipping record %d: missing required fields %s (has keys: %s)",
                i,
                missing,
                list(record.keys()),
            )
            continue

        # Type and value range validation
        errors = []
        if not isinstance(record["symbol"], str) or not record["symbol"].strip():
            errors.append("symbol must be a non-empty string")
        if not isinstance(record["earnings_date"], str) or len(record["earnings_date"]) != 10:
            errors.append("earnings_date must be YYYY-MM-DD string")
        if record["earnings_timing"] not in valid_timings:
            errors.append(f"earnings_timing '{record['earnings_timing']}' not in {valid_timings}")
        if not isinstance(record["gap_pct"], (int, float)):
            errors.append(f"gap_pct must be numeric, got {type(record['gap_pct']).__name__}")
        if record["grade"] not in valid_grades:
            errors.append(f"grade '{record['grade']}' not in {valid_grades}")

        if errors:
            logger.warning(
                "Skipping record %d (%s): %s",
                i,
                record.get("symbol", "?"),
                "; ".join(errors),
            )
            continue

        validated.append(record)

    if not validated:
        raise ValueError(
            f"All {len(results)} records failed validation. No valid candidates to process."
        )

    return validated


def calculate_setup_quality(gap_pct: float, pattern_result: dict) -> float:
    """Calculate setup quality score based on earnings gap and pattern.

    Args:
        gap_pct: Earnings gap percentage
        pattern_result: Result from analyze_weekly_pattern()

    Returns:
        Setup quality score (0-100)
    """
    score = 0.0

    # Gap quality (0-50 points)
    if gap_pct >= 10.0:
        score += 50
    elif gap_pct >= 7.0:
        score += 40
    elif gap_pct >= 5.0:
        score += 30
    elif gap_pct >= 3.0:
        score += 20
    else:
        score += 10

    # Pattern quality (0-50 points)
    stage = pattern_result.get("stage", "MONITORING")
    weeks = pattern_result.get("weeks_since_earnings", 0)
    red_candle = pattern_result.get("red_candle")

    if stage == "BREAKOUT":
        score += 50
    elif stage == "SIGNAL_READY":
        score += 40
        # Bonus for red candle with long lower wick (institutional support)
        if red_candle and red_candle.get("lower_wick_pct", 0) > 30:
            score += 5
    elif stage == "MONITORING":
        # Earlier in the cycle is better
        if weeks <= 2:
            score += 25
        else:
            score += 15
    else:  # EXPIRED
        score += 0

    return min(100.0, score)


def analyze_stock(
    symbol: str,
    daily_prices: list[dict],
    earnings_date: str,
    earnings_timing: str,
    gap_pct: float,
    current_price: float,
    watch_weeks: int = 5,
) -> Optional[dict]:
    """
    Full PEAD analysis for a single stock.

    Args:
        symbol: Stock symbol
        daily_prices: Most-recent-first daily OHLCV data
        earnings_date: Earnings announcement date (YYYY-MM-DD)
        earnings_timing: 'bmo' (before market open) or 'amc' (after market close)
        gap_pct: Earnings gap percentage
        current_price: Current stock price
        watch_weeks: Maximum monitoring window in weeks

    Returns:
        Analysis result dict or None on failure
    """
    if not daily_prices or len(daily_prices) < 5:
        return None

    # 1. Convert to weekly candles
    weekly_candles = daily_to_weekly(daily_prices, earnings_date=earnings_date)
    if not weekly_candles:
        return None

    # 2. Analyze weekly pattern
    pattern = analyze_weekly_pattern(weekly_candles, earnings_date, watch_weeks=watch_weeks)

    # 3. Calculate setup quality
    setup_score = calculate_setup_quality(gap_pct, pattern)

    # 4. Calculate breakout
    red_candle = pattern.get("red_candle")
    if red_candle:
        breakout = calculate_breakout(weekly_candles, red_candle, current_price)
    else:
        breakout = {
            "is_breakout": False,
            "breakout_pct": 0.0,
            "volume_confirmation": False,
            "score": 0.0,
        }

    # 5. Calculate liquidity
    liquidity = calculate_liquidity(daily_prices, current_price)

    # 6. Calculate risk/reward
    if red_candle:
        rr = calculate_risk_reward(current_price, red_candle)
    else:
        rr = {
            "entry_price": current_price,
            "stop_price": 0.0,
            "target_price": 0.0,
            "risk_pct": 0.0,
            "reward_pct": 0.0,
            "risk_reward_ratio": 0.0,
            "score": 25.0,
        }

    # 7. Composite score
    composite = calculate_composite_score(
        setup_score=setup_score,
        breakout_score=breakout["score"],
        liquidity_score=liquidity["score"],
        rr_score=rr["score"],
    )

    return {
        "symbol": symbol,
        "stage": pattern["stage"],
        "earnings_date": earnings_date,
        "earnings_timing": earnings_timing,
        "gap_pct": gap_pct,
        "weeks_since_earnings": pattern["weeks_since_earnings"],
        "red_candle": red_candle,
        "current_price": current_price,
        "breakout_pct": breakout["breakout_pct"],
        "entry_price": rr["entry_price"],
        "stop_price": rr["stop_price"],
        "target_price": rr["target_price"],
        "risk_pct": rr["risk_pct"],
        "risk_reward_ratio": rr["risk_reward_ratio"],
        "adv20_dollar": liquidity["adv20_dollar"],
        "composite_score": composite["composite_score"],
        "rating": composite["rating"],
        "guidance": composite["guidance"],
        "components": composite["component_breakdown"],
    }


def main():
    args = parse_arguments()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    print("=" * 70)
    print("PEAD Stock Screener")
    print("Post-Earnings Announcement Drift")
    print("=" * 70)
    print()

    # Determine mode
    mode = "B" if args.candidates_json else "A"
    print(f"Mode: {mode} ({'JSON Input' if mode == 'B' else 'FMP Earnings Calendar'})")

    # Initialize FMP client (needed for both modes for historical data)
    try:
        client = FMPClient(api_key=args.api_key, max_api_calls=args.max_api_calls)
        print("FMP API client initialized")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # ========================================================================
    # Phase 1: Get Candidates
    # ========================================================================
    print()
    print("Phase 1: Get Candidates")
    print("-" * 70)

    candidates = []

    if mode == "A":
        candidates = _get_candidates_mode_a(client, args)
    else:
        candidates = _get_candidates_mode_b(args)

    if not candidates:
        print("  No candidates found. Exiting.")
        sys.exit(0)

    print(f"  Total candidates: {len(candidates)}")
    print()

    # ========================================================================
    # Phase 1.5: Budget Check
    # ========================================================================
    print("Phase 1.5: Budget Check")
    print("-" * 70)

    api_stats = client.get_api_stats()
    remaining = api_stats["budget_remaining"]
    needed = len(candidates)  # 1 historical call per candidate
    print(f"  API calls remaining: {remaining}")
    print(f"  Estimated calls needed: {needed} (1 per candidate)")

    if needed > remaining:
        # Trim candidates to fit budget
        candidates = candidates[:remaining]
        print(f"  WARNING: Trimmed to {len(candidates)} candidates to fit API budget")
    else:
        print("  Budget sufficient")
    print()

    # ========================================================================
    # Phase 2: Fetch Historical Data & Weekly Candle Analysis
    # ========================================================================
    print("Phase 2: Fetch Historical Data")
    print("-" * 70)

    results = []
    for i, candidate in enumerate(candidates):
        symbol = candidate["symbol"]
        if (i + 1) % 10 == 0 or i == len(candidates) - 1:
            print(f"  Progress: {i + 1}/{len(candidates)}", flush=True)

        try:
            data = client.get_historical_prices(symbol, days=90)
        except ApiCallBudgetExceeded:
            print(f"  WARNING: API budget exceeded at {symbol}. Processing collected data.")
            break

        if not data or "historical" not in data:
            continue

        daily_prices = data["historical"]
        if not daily_prices:
            continue

        current_price = daily_prices[0].get("close", 0)
        if current_price <= 0:
            continue

        # Calculate actual price gap if not already provided (Mode A)
        gap_pct = candidate.get("gap_pct")
        if gap_pct is None:
            gap_pct = calculate_price_gap(
                daily_prices,
                candidate["earnings_date"],
                candidate.get("earnings_timing", ""),
            )

        # Apply min-gap filter (using actual price gap, not EPS estimate)
        if mode == "A" and abs(gap_pct) < args.min_gap:
            continue

        # Run analysis
        analysis = analyze_stock(
            symbol=symbol,
            daily_prices=daily_prices,
            earnings_date=candidate["earnings_date"],
            earnings_timing=candidate.get("earnings_timing", ""),
            gap_pct=gap_pct,
            current_price=current_price,
            watch_weeks=args.watch_weeks,
        )

        if analysis:
            print(
                f"  {symbol:6} Stage: {analysis['stage']:14} "
                f"Score: {analysis['composite_score']:5.1f} ({analysis['rating']})"
            )
            results.append(analysis)

    print()

    # ========================================================================
    # Phase 3: Score & Report
    # ========================================================================
    print("Phase 3: Generate Reports")
    print("-" * 70)

    # Create output directory if needed
    os.makedirs(args.output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    json_file = os.path.join(args.output_dir, f"pead_screener_{timestamp}.json")
    md_file = os.path.join(args.output_dir, f"pead_screener_{timestamp}.md")

    api_stats = client.get_api_stats()

    metadata = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lookback_days": args.lookback_days if mode == "A" else None,
        "watch_weeks": args.watch_weeks,
        "mode": mode,
        "input_file": args.candidates_json if mode == "B" else None,
        "min_gap": args.min_gap if mode == "A" else None,
        "min_market_cap": args.min_market_cap if mode == "A" else None,
        "min_grade": args.min_grade if mode == "B" else None,
        "api_stats": api_stats,
    }

    # Sort by stage priority then composite score before top-N cutoff
    stage_priority = {"BREAKOUT": 0, "SIGNAL_READY": 1, "MONITORING": 2, "EXPIRED": 3}
    results.sort(
        key=lambda r: (stage_priority.get(r["stage"], 9), -r["composite_score"]),
    )
    top_results = results[: args.top] if len(results) > args.top else results

    generate_json_report(top_results, metadata, json_file)
    generate_markdown_report(top_results, metadata, md_file)

    # ========================================================================
    # Summary
    # ========================================================================
    print()
    print("=" * 70)
    print("PEAD Screening Complete")
    print("=" * 70)

    # Stage counts
    stage_counts = {}
    for r in results:
        stage = r.get("stage", "UNKNOWN")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    print()
    print("Stage Distribution:")
    for stage in ["BREAKOUT", "SIGNAL_READY", "MONITORING", "EXPIRED"]:
        count = stage_counts.get(stage, 0)
        print(f"  {stage:14} {count}")

    # Top 5
    if results:
        print()
        print(f"Top {min(5, len(results))} Results:")
        # Sort by stage priority then score
        stage_priority = {"BREAKOUT": 0, "SIGNAL_READY": 1, "MONITORING": 2, "EXPIRED": 3}
        sorted_results = sorted(
            results,
            key=lambda r: (stage_priority.get(r["stage"], 9), -r["composite_score"]),
        )
        for i, r in enumerate(sorted_results[:5], 1):
            print(
                f"  {i}. {r['symbol']:6} {r['stage']:14} "
                f"Score: {r['composite_score']:5.1f} ({r['rating']})"
            )
    else:
        print()
        print("  No PEAD candidates found.")

    print()
    print(f"  JSON Report:    {json_file}")
    print(f"  Markdown Report: {md_file}")
    print()
    print("API Usage:")
    print(f"  API calls made: {api_stats['api_calls_made']}")
    print(f"  Budget remaining: {api_stats['budget_remaining']}")
    print()


def _get_candidates_mode_a(client: FMPClient, args) -> list[dict]:
    """Get candidates from FMP earnings calendar (Mode A)."""
    # Calculate date range
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=args.lookback_days)).strftime("%Y-%m-%d")

    print(f"  Fetching earnings calendar: {from_date} to {to_date}")

    earnings = client.get_earnings_calendar(from_date, to_date)
    if not earnings:
        print("  WARNING: No earnings data returned")
        return []

    print(f"  Raw earnings events: {len(earnings)}")

    # Get unique symbols
    symbols = list(set(e.get("symbol", "") for e in earnings if e.get("symbol")))
    if not symbols:
        return []

    # Fetch company profiles for market cap filtering
    print(f"  Fetching profiles for {len(symbols)} symbols...")
    profiles = client.get_company_profiles(symbols)

    # Build candidates with market cap filter (gap filter deferred to Phase 2
    # where actual price data is available for accurate gap calculation)
    grade_map = {e.get("symbol"): e for e in earnings}
    candidates = []

    for symbol in symbols:
        earning = grade_map.get(symbol, {})
        profile = profiles.get(symbol, {})

        # Market cap filter
        market_cap = profile.get("mktCap", 0) or 0
        if market_cap < args.min_market_cap:
            continue

        timing = earning.get("time", "")
        # Normalize timing
        if timing in ("bmo", "Before Market Open"):
            timing = "bmo"
        elif timing in ("amc", "After Market Close"):
            timing = "amc"

        candidates.append(
            {
                "symbol": symbol,
                "earnings_date": earning.get("date", ""),
                "earnings_timing": timing,
                "gap_pct": None,  # Calculated from price data in Phase 2
                "market_cap": market_cap,
            }
        )

    print(f"  Candidates after market cap filter: {len(candidates)}")
    return candidates


def _get_candidates_mode_b(args) -> list[dict]:
    """Get candidates from earnings-trade-analyzer JSON (Mode B).

    Raises:
        SystemExit(1): On file not found, JSON parse error, or validation error.
    """
    json_path = args.candidates_json
    print(f"  Loading: {json_path}")

    if not os.path.exists(json_path):
        print(f"  ERROR: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        data = json.load(f)

    # Validation errors are fatal in Mode B (bad input should not silently succeed)
    validated = validate_input_json(data)

    print(f"  Validated records: {len(validated)}")

    # Grade filter
    grade_order = {"A": 0, "B": 1, "C": 2, "D": 3}
    min_grade_rank = grade_order.get(args.min_grade, 1)

    candidates = []
    for record in validated:
        grade = record.get("grade", "D")
        grade_rank = grade_order.get(grade, 3)
        if grade_rank <= min_grade_rank:
            candidates.append(
                {
                    "symbol": record["symbol"],
                    "earnings_date": record["earnings_date"],
                    "earnings_timing": record.get("earnings_timing", ""),
                    "gap_pct": record.get("gap_pct", 0),
                    "grade": grade,
                }
            )

    print(f"  After grade filter (>= {args.min_grade}): {len(candidates)}")
    return candidates


if __name__ == "__main__":
    main()
