"""Synthetic OHLCV builders for tests.

All builders return list[dict] in most-recent-first order
(history[0] = latest session).
"""

from __future__ import annotations

from datetime import date, timedelta


def make_bar(
    d: str,
    close: float,
    volume: int = 1_000_000,
    open_: float | None = None,
    high: float | None = None,
    low: float | None = None,
):
    """Build a single OHLCV bar dict."""
    return {
        "date": d,
        "open": open_ if open_ is not None else close,
        "high": high if high is not None else close + 0.5,
        "low": low if low is not None else close - 0.5,
        "close": close,
        "volume": volume,
    }


def date_seq(start: str, n: int, step_days: int = 1):
    """Yield n date strings going backwards from `start` (most-recent-first).

    Example: date_seq("2026-04-30", 3) -> ["2026-04-30", "2026-04-29", "2026-04-28"]
    """
    base = date.fromisoformat(start)
    return [(base - timedelta(days=i * step_days)).isoformat() for i in range(n)]


def make_history(closes: list[float], volumes: list[int] | None = None, start: str = "2026-04-30"):
    """Build a most-recent-first history from close/volume lists.

    closes[0] is the latest close. Default volume is 1_000_000.
    """
    if volumes is None:
        volumes = [1_000_000] * len(closes)
    if len(volumes) != len(closes):
        raise ValueError("closes and volumes must have the same length")
    dates = date_seq(start, len(closes))
    return [make_bar(d, c, v) for d, c, v in zip(dates, closes, volumes)]


def make_dd_history(
    *,
    dd_age: int,
    pre_dd_close: float = 100.0,
    dd_drop_pct: float = -0.0075,
    dd_volume_increase_pct: float = 0.20,
    sessions_after_dd_close: list[float] | None = None,
    sessions_after_dd_high: list[float] | None = None,
    start: str = "2026-04-30",
    base_volume: int = 1_000_000,
):
    """Build a history that contains a single Distribution Day at age=dd_age.

    Returned list is most-recent-first. effective_history[dd_age] is the DD bar.
    `sessions_after_dd_close` / `sessions_after_dd_high` describe (most-recent-first)
    the dd_age post-DD sessions; if None, they all stay flat at dd_close.
    """
    dd_close = pre_dd_close * (1 + dd_drop_pct)
    pre_dd_volume = base_volume
    dd_volume = int(pre_dd_volume * (1 + dd_volume_increase_pct))

    n_after = dd_age
    if sessions_after_dd_close is None:
        sessions_after_dd_close = [dd_close] * n_after
    if sessions_after_dd_high is None:
        sessions_after_dd_high = [c + 0.5 for c in sessions_after_dd_close]
    if len(sessions_after_dd_close) != n_after or len(sessions_after_dd_high) != n_after:
        raise ValueError("sessions_after_dd_* lengths must equal dd_age")

    bars: list[dict] = []
    dates = date_seq(start, n_after + 2)

    # Most-recent-first: post-DD sessions, then DD, then pre-DD baseline
    for i in range(n_after):
        bars.append(
            make_bar(
                dates[i],
                close=sessions_after_dd_close[i],
                volume=base_volume,
                high=sessions_after_dd_high[i],
            )
        )
    bars.append(
        make_bar(
            dates[n_after],
            close=dd_close,
            volume=dd_volume,
            high=pre_dd_close * 0.999,  # DD intraday high typically below pre-DD close
        )
    )
    bars.append(make_bar(dates[n_after + 1], close=pre_dd_close, volume=pre_dd_volume))
    return bars
