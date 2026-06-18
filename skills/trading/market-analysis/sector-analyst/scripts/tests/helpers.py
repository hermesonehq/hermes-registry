"""Test data factories for sector-analyst tests."""


def make_sector_row(
    sector: str,
    ratio: float = 0.20,
    ma_10: float = 0.19,
    trend: str = "Up",
    slope: float = 0.005,
    status: str = "Above MA",
) -> dict:
    """Create a single sector CSV row dict."""
    return {
        "Sector": sector,
        "Ratio": str(ratio),
        "10MA": str(ma_10),
        "Trend": trend,
        "Slope": str(slope),
        "Status": status,
    }


ALL_SECTORS = [
    "Technology",
    "Consumer Cyclical",
    "Communication Services",
    "Financial",
    "Industrials",
    "Utilities",
    "Consumer Defensive",
    "Healthcare",
    "Real Estate",
    "Energy",
    "Basic Materials",
]


def make_full_sector_set(
    ratio: float = 0.20,
    trend: str = "Up",
    slope: float = 0.005,
) -> list[dict]:
    """Create a full set of 11 sector rows with uniform defaults."""
    return [make_sector_row(s, ratio=ratio, trend=trend, slope=slope) for s in ALL_SECTORS]


def make_early_cycle_scenario() -> list[dict]:
    """Early cycle: cyclical sectors high, defensive sectors low."""
    leaders = {
        "Technology",
        "Communication Services",
        "Industrials",
        "Consumer Cyclical",
        "Financial",
    }
    rows = []
    for s in ALL_SECTORS:
        if s in leaders:
            rows.append(make_sector_row(s, ratio=0.35, trend="Up", slope=0.010))
        else:
            rows.append(make_sector_row(s, ratio=0.10, trend="Down", slope=-0.005))
    return rows


def make_late_cycle_scenario() -> list[dict]:
    """Late cycle: energy/materials high, tech/consumer cyclical low."""
    commodity_leaders = {"Energy", "Basic Materials"}
    cyclical_low = {"Technology", "Consumer Cyclical"}
    rows = []
    for s in ALL_SECTORS:
        if s in commodity_leaders:
            rows.append(make_sector_row(s, ratio=0.40, trend="Up", slope=0.012))
        elif s in cyclical_low:
            rows.append(make_sector_row(s, ratio=0.10, trend="Down", slope=-0.008))
        else:
            rows.append(make_sector_row(s, ratio=0.20, trend="Up", slope=0.002))
    return rows


def make_recession_scenario() -> list[dict]:
    """Recession: defensive sectors high, cyclical/commodity low."""
    defensives = {"Utilities", "Healthcare", "Consumer Defensive"}
    rows = []
    for s in ALL_SECTORS:
        if s in defensives:
            rows.append(make_sector_row(s, ratio=0.40, trend="Up", slope=0.010))
        else:
            rows.append(make_sector_row(s, ratio=0.08, trend="Down", slope=-0.008))
    return rows
