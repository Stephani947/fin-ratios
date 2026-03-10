"""
Industry benchmark medians and percentile ranking.

Benchmarks are approximate medians derived from S&P 500 data (2022–2024).
They give directional context, not investment advice.

Usage:
    from fin_ratios.utils.benchmarks import sector_benchmarks, percentile_rank

    b = sector_benchmarks("Technology")
    print(b.pe_median)  # 28.5

    pct = percentile_rank("Technology", "pe", 35)
    print(f"P/E of 35 is at the {pct:.0f}th percentile for Technology stocks")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SectorBenchmarks:
    """Approximate median ratios by sector (S&P 500 constituents, 2022–2024)."""
    sector: str

    # Valuation
    pe_median: Optional[float] = None
    pb_median: Optional[float] = None
    ps_median: Optional[float] = None
    ev_ebitda_median: Optional[float] = None
    p_fcf_median: Optional[float] = None

    # Profitability
    gross_margin_median: Optional[float] = None
    operating_margin_median: Optional[float] = None
    net_margin_median: Optional[float] = None
    roe_median: Optional[float] = None
    roa_median: Optional[float] = None
    roic_median: Optional[float] = None

    # Cash flow
    fcf_margin_median: Optional[float] = None
    fcf_conversion_median: Optional[float] = None

    # Balance sheet
    debt_to_equity_median: Optional[float] = None
    current_ratio_median: Optional[float] = None

    # Growth (5yr CAGR)
    revenue_growth_5yr_median: Optional[float] = None

    # Percentile distributions (p25, p50, p75) for percentile_rank()
    _distributions: dict = field(default_factory=dict, repr=False)


# ── Benchmark data ─────────────────────────────────────────────────────────────
# Source: approximate medians from S&P 500 sector analysis (2022–2024).
# p25 / p50 / p75 allow interpolated percentile ranking.

_BENCHMARKS: dict[str, dict] = {
    "Technology": {
        "pe":                  {"p25": 22,    "p50": 30,    "p75": 45},
        "pb":                  {"p25": 5,     "p50": 9,     "p75": 18},
        "ps":                  {"p25": 3,     "p50": 6,     "p75": 12},
        "ev_ebitda":           {"p25": 16,    "p50": 22,    "p75": 35},
        "p_fcf":               {"p25": 20,    "p50": 28,    "p75": 45},
        "gross_margin":        {"p25": 0.50,  "p50": 0.65,  "p75": 0.77},
        "operating_margin":    {"p25": 0.10,  "p50": 0.22,  "p75": 0.34},
        "net_margin":          {"p25": 0.07,  "p50": 0.17,  "p75": 0.27},
        "roe":                 {"p25": 0.15,  "p50": 0.28,  "p75": 0.50},
        "roa":                 {"p25": 0.06,  "p50": 0.12,  "p75": 0.22},
        "roic":                {"p25": 0.10,  "p50": 0.20,  "p75": 0.38},
        "fcf_margin":          {"p25": 0.08,  "p50": 0.18,  "p75": 0.28},
        "fcf_conversion":      {"p25": 0.70,  "p50": 0.90,  "p75": 1.10},
        "debt_to_equity":      {"p25": 0.10,  "p50": 0.40,  "p75": 1.00},
        "current_ratio":       {"p25": 1.5,   "p50": 2.3,   "p75": 4.0},
        "revenue_growth_5yr":  {"p25": 0.06,  "p50": 0.12,  "p75": 0.25},
    },
    "Healthcare": {
        "pe":                  {"p25": 18,    "p50": 25,    "p75": 38},
        "pb":                  {"p25": 3,     "p50": 5,     "p75": 10},
        "ps":                  {"p25": 2,     "p50": 4,     "p75": 8},
        "ev_ebitda":           {"p25": 12,    "p50": 18,    "p75": 28},
        "gross_margin":        {"p25": 0.40,  "p50": 0.58,  "p75": 0.72},
        "operating_margin":    {"p25": 0.08,  "p50": 0.17,  "p75": 0.28},
        "net_margin":          {"p25": 0.05,  "p50": 0.13,  "p75": 0.22},
        "roe":                 {"p25": 0.10,  "p50": 0.20,  "p75": 0.35},
        "roa":                 {"p25": 0.05,  "p50": 0.10,  "p75": 0.17},
        "roic":                {"p25": 0.08,  "p50": 0.15,  "p75": 0.28},
        "fcf_margin":          {"p25": 0.06,  "p50": 0.13,  "p75": 0.22},
        "debt_to_equity":      {"p25": 0.20,  "p50": 0.55,  "p75": 1.20},
        "current_ratio":       {"p25": 1.4,   "p50": 2.0,   "p75": 3.5},
        "revenue_growth_5yr":  {"p25": 0.04,  "p50": 0.08,  "p75": 0.16},
    },
    "Financials": {
        "pe":                  {"p25": 10,    "p50": 13,    "p75": 18},
        "pb":                  {"p25": 1.0,   "p50": 1.5,   "p75": 2.5},
        "ps":                  {"p25": 1.5,   "p50": 2.5,   "p75": 4.0},
        "ev_ebitda":           {"p25": 8,     "p50": 12,    "p75": 18},
        "gross_margin":        {"p25": 0.45,  "p50": 0.58,  "p75": 0.70},
        "operating_margin":    {"p25": 0.20,  "p50": 0.30,  "p75": 0.42},
        "net_margin":          {"p25": 0.15,  "p50": 0.23,  "p75": 0.33},
        "roe":                 {"p25": 0.08,  "p50": 0.12,  "p75": 0.18},
        "roa":                 {"p25": 0.006, "p50": 0.01,  "p75": 0.016},
        "debt_to_equity":      {"p25": 0.5,   "p50": 2.0,   "p75": 6.0},
        "revenue_growth_5yr":  {"p25": 0.02,  "p50": 0.06,  "p75": 0.12},
    },
    "Consumer Discretionary": {
        "pe":                  {"p25": 18,    "p50": 25,    "p75": 40},
        "pb":                  {"p25": 3,     "p50": 6,     "p75": 12},
        "ps":                  {"p25": 1.0,   "p50": 2.0,   "p75": 4.0},
        "ev_ebitda":           {"p25": 12,    "p50": 17,    "p75": 26},
        "gross_margin":        {"p25": 0.28,  "p50": 0.42,  "p75": 0.60},
        "operating_margin":    {"p25": 0.05,  "p50": 0.10,  "p75": 0.18},
        "net_margin":          {"p25": 0.03,  "p50": 0.07,  "p75": 0.14},
        "roe":                 {"p25": 0.12,  "p50": 0.22,  "p75": 0.40},
        "roa":                 {"p25": 0.04,  "p50": 0.08,  "p75": 0.15},
        "roic":                {"p25": 0.08,  "p50": 0.14,  "p75": 0.25},
        "fcf_margin":          {"p25": 0.03,  "p50": 0.07,  "p75": 0.13},
        "debt_to_equity":      {"p25": 0.30,  "p50": 0.80,  "p75": 2.00},
        "current_ratio":       {"p25": 1.1,   "p50": 1.5,   "p75": 2.5},
        "revenue_growth_5yr":  {"p25": 0.03,  "p50": 0.07,  "p75": 0.15},
    },
    "Consumer Staples": {
        "pe":                  {"p25": 18,    "p50": 23,    "p75": 32},
        "pb":                  {"p25": 3,     "p50": 6,     "p75": 12},
        "ps":                  {"p25": 0.8,   "p50": 1.4,   "p75": 2.5},
        "ev_ebitda":           {"p25": 12,    "p50": 16,    "p75": 22},
        "gross_margin":        {"p25": 0.28,  "p50": 0.40,  "p75": 0.55},
        "operating_margin":    {"p25": 0.08,  "p50": 0.13,  "p75": 0.20},
        "net_margin":          {"p25": 0.05,  "p50": 0.09,  "p75": 0.15},
        "roe":                 {"p25": 0.15,  "p50": 0.25,  "p75": 0.40},
        "roa":                 {"p25": 0.06,  "p50": 0.10,  "p75": 0.16},
        "roic":                {"p25": 0.10,  "p50": 0.17,  "p75": 0.28},
        "fcf_margin":          {"p25": 0.05,  "p50": 0.08,  "p75": 0.14},
        "debt_to_equity":      {"p25": 0.40,  "p50": 1.00,  "p75": 2.50},
        "revenue_growth_5yr":  {"p25": 0.02,  "p50": 0.05,  "p75": 0.10},
    },
    "Industrials": {
        "pe":                  {"p25": 18,    "p50": 24,    "p75": 35},
        "pb":                  {"p25": 3,     "p50": 5,     "p75": 9},
        "ps":                  {"p25": 1.0,   "p50": 2.0,   "p75": 3.5},
        "ev_ebitda":           {"p25": 12,    "p50": 16,    "p75": 23},
        "gross_margin":        {"p25": 0.25,  "p50": 0.35,  "p75": 0.50},
        "operating_margin":    {"p25": 0.07,  "p50": 0.12,  "p75": 0.20},
        "net_margin":          {"p25": 0.05,  "p50": 0.09,  "p75": 0.15},
        "roe":                 {"p25": 0.12,  "p50": 0.20,  "p75": 0.32},
        "roa":                 {"p25": 0.05,  "p50": 0.09,  "p75": 0.15},
        "roic":                {"p25": 0.09,  "p50": 0.15,  "p75": 0.25},
        "fcf_margin":          {"p25": 0.04,  "p50": 0.08,  "p75": 0.14},
        "debt_to_equity":      {"p25": 0.30,  "p50": 0.80,  "p75": 2.00},
        "current_ratio":       {"p25": 1.2,   "p50": 1.8,   "p75": 3.0},
        "revenue_growth_5yr":  {"p25": 0.03,  "p50": 0.07,  "p75": 0.13},
    },
    "Energy": {
        "pe":                  {"p25": 8,     "p50": 12,    "p75": 20},
        "pb":                  {"p25": 1.0,   "p50": 1.8,   "p75": 3.5},
        "ps":                  {"p25": 0.5,   "p50": 1.0,   "p75": 2.0},
        "ev_ebitda":           {"p25": 4,     "p50": 7,     "p75": 12},
        "gross_margin":        {"p25": 0.15,  "p50": 0.28,  "p75": 0.45},
        "operating_margin":    {"p25": 0.06,  "p50": 0.14,  "p75": 0.24},
        "net_margin":          {"p25": 0.04,  "p50": 0.10,  "p75": 0.18},
        "roe":                 {"p25": 0.06,  "p50": 0.13,  "p75": 0.24},
        "roa":                 {"p25": 0.03,  "p50": 0.07,  "p75": 0.13},
        "roic":                {"p25": 0.06,  "p50": 0.12,  "p75": 0.22},
        "fcf_margin":          {"p25": 0.05,  "p50": 0.10,  "p75": 0.18},
        "debt_to_equity":      {"p25": 0.20,  "p50": 0.60,  "p75": 1.50},
        "revenue_growth_5yr":  {"p25": -0.02, "p50": 0.04,  "p75": 0.12},
    },
    "Real Estate": {
        "pe":                  {"p25": 25,    "p50": 40,    "p75": 65},
        "pb":                  {"p25": 1.2,   "p50": 2.0,   "p75": 3.5},
        "ps":                  {"p25": 4,     "p50": 8,     "p75": 14},
        "ev_ebitda":           {"p25": 18,    "p50": 25,    "p75": 38},
        "gross_margin":        {"p25": 0.40,  "p50": 0.55,  "p75": 0.70},
        "operating_margin":    {"p25": 0.20,  "p50": 0.30,  "p75": 0.45},
        "net_margin":          {"p25": 0.10,  "p50": 0.20,  "p75": 0.35},
        "roe":                 {"p25": 0.04,  "p50": 0.08,  "p75": 0.14},
        "roa":                 {"p25": 0.02,  "p50": 0.04,  "p75": 0.08},
        "debt_to_equity":      {"p25": 0.60,  "p50": 1.20,  "p75": 2.50},
        "revenue_growth_5yr":  {"p25": 0.03,  "p50": 0.07,  "p75": 0.14},
    },
    "Utilities": {
        "pe":                  {"p25": 16,    "p50": 20,    "p75": 28},
        "pb":                  {"p25": 1.5,   "p50": 2.0,   "p75": 3.0},
        "ps":                  {"p25": 1.5,   "p50": 2.5,   "p75": 3.8},
        "ev_ebitda":           {"p25": 9,     "p50": 12,    "p75": 16},
        "gross_margin":        {"p25": 0.25,  "p50": 0.35,  "p75": 0.48},
        "operating_margin":    {"p25": 0.12,  "p50": 0.20,  "p75": 0.30},
        "net_margin":          {"p25": 0.08,  "p50": 0.13,  "p75": 0.20},
        "roe":                 {"p25": 0.08,  "p50": 0.12,  "p75": 0.16},
        "roa":                 {"p25": 0.02,  "p50": 0.04,  "p75": 0.06},
        "debt_to_equity":      {"p25": 0.80,  "p50": 1.50,  "p75": 3.00},
        "revenue_growth_5yr":  {"p25": 0.01,  "p50": 0.04,  "p75": 0.08},
    },
    "Communication Services": {
        "pe":                  {"p25": 16,    "p50": 23,    "p75": 38},
        "pb":                  {"p25": 2.5,   "p50": 5.0,   "p75": 10},
        "ps":                  {"p25": 1.5,   "p50": 3.0,   "p75": 6.0},
        "ev_ebitda":           {"p25": 8,     "p50": 14,    "p75": 24},
        "gross_margin":        {"p25": 0.35,  "p50": 0.52,  "p75": 0.68},
        "operating_margin":    {"p25": 0.08,  "p50": 0.18,  "p75": 0.30},
        "net_margin":          {"p25": 0.06,  "p50": 0.13,  "p75": 0.25},
        "roe":                 {"p25": 0.08,  "p50": 0.18,  "p75": 0.35},
        "roa":                 {"p25": 0.04,  "p50": 0.09,  "p75": 0.18},
        "roic":                {"p25": 0.06,  "p50": 0.13,  "p75": 0.26},
        "fcf_margin":          {"p25": 0.05,  "p50": 0.12,  "p75": 0.22},
        "debt_to_equity":      {"p25": 0.20,  "p50": 0.70,  "p75": 2.00},
        "revenue_growth_5yr":  {"p25": 0.03,  "p50": 0.08,  "p75": 0.18},
    },
    "Materials": {
        "pe":                  {"p25": 14,    "p50": 20,    "p75": 30},
        "pb":                  {"p25": 2.0,   "p50": 3.0,   "p75": 5.0},
        "ps":                  {"p25": 0.8,   "p50": 1.5,   "p75": 2.8},
        "ev_ebitda":           {"p25": 8,     "p50": 12,    "p75": 18},
        "gross_margin":        {"p25": 0.20,  "p50": 0.32,  "p75": 0.48},
        "operating_margin":    {"p25": 0.08,  "p50": 0.14,  "p75": 0.22},
        "net_margin":          {"p25": 0.05,  "p50": 0.10,  "p75": 0.17},
        "roe":                 {"p25": 0.10,  "p50": 0.17,  "p75": 0.28},
        "roa":                 {"p25": 0.05,  "p50": 0.09,  "p75": 0.15},
        "roic":                {"p25": 0.07,  "p50": 0.13,  "p75": 0.22},
        "fcf_margin":          {"p25": 0.04,  "p50": 0.08,  "p75": 0.15},
        "debt_to_equity":      {"p25": 0.20,  "p50": 0.55,  "p75": 1.30},
        "revenue_growth_5yr":  {"p25": 0.01,  "p50": 0.06,  "p75": 0.13},
    },
    # Broad market (fallback)
    "S&P 500": {
        "pe":                  {"p25": 16,    "p50": 22,    "p75": 34},
        "pb":                  {"p25": 2.5,   "p50": 4.0,   "p75": 8.0},
        "ps":                  {"p25": 1.2,   "p50": 2.5,   "p75": 5.0},
        "ev_ebitda":           {"p25": 11,    "p50": 16,    "p75": 25},
        "gross_margin":        {"p25": 0.30,  "p50": 0.45,  "p75": 0.63},
        "operating_margin":    {"p25": 0.07,  "p50": 0.14,  "p75": 0.24},
        "net_margin":          {"p25": 0.05,  "p50": 0.10,  "p75": 0.20},
        "roe":                 {"p25": 0.10,  "p50": 0.18,  "p75": 0.32},
        "roa":                 {"p25": 0.04,  "p50": 0.08,  "p75": 0.15},
        "roic":                {"p25": 0.08,  "p50": 0.15,  "p75": 0.27},
        "fcf_margin":          {"p25": 0.05,  "p50": 0.10,  "p75": 0.18},
        "fcf_conversion":      {"p25": 0.60,  "p50": 0.85,  "p75": 1.10},
        "debt_to_equity":      {"p25": 0.20,  "p50": 0.70,  "p75": 1.80},
        "current_ratio":       {"p25": 1.2,   "p50": 1.8,   "p75": 3.2},
        "revenue_growth_5yr":  {"p25": 0.03,  "p50": 0.08,  "p75": 0.16},
    },
}


def sector_benchmarks(sector: str) -> SectorBenchmarks:
    """
    Return benchmark medians for a sector.

    Falls back to "S&P 500" if sector is not recognised.

    Args:
        sector: e.g. "Technology", "Healthcare", "Financials"

    Returns:
        SectorBenchmarks dataclass with median values and distribution data.

    Example:
        b = sector_benchmarks("Technology")
        print(b.pe_median)          # 30
        print(b.roic_median)        # 0.20 (20%)
    """
    data = _BENCHMARKS.get(sector) or _BENCHMARKS.get("S&P 500", {})

    def _med(key: str) -> Optional[float]:
        return data.get(key, {}).get("p50")

    return SectorBenchmarks(
        sector=sector,
        pe_median=_med("pe"),
        pb_median=_med("pb"),
        ps_median=_med("ps"),
        ev_ebitda_median=_med("ev_ebitda"),
        p_fcf_median=_med("p_fcf"),
        gross_margin_median=_med("gross_margin"),
        operating_margin_median=_med("operating_margin"),
        net_margin_median=_med("net_margin"),
        roe_median=_med("roe"),
        roa_median=_med("roa"),
        roic_median=_med("roic"),
        fcf_margin_median=_med("fcf_margin"),
        fcf_conversion_median=_med("fcf_conversion"),
        debt_to_equity_median=_med("debt_to_equity"),
        current_ratio_median=_med("current_ratio"),
        revenue_growth_5yr_median=_med("revenue_growth_5yr"),
        _distributions=data,
    )


def percentile_rank(sector: str, metric: str, value: float) -> float:
    """
    Return the approximate percentile rank (0–100) of a value within a sector.

    Uses linear interpolation between p25, p50, p75 anchor points.
    Outside the p25–p75 range, extrapolates linearly (capped at 0/100).

    Args:
        sector: e.g. "Technology"
        metric: e.g. "pe", "roic", "gross_margin", "operating_margin"
        value:  the raw metric value (e.g. 0.25 for 25% ROIC, not 25)

    Returns:
        float in [0, 100]. Higher = better relative to peers
        for profitability metrics; lower P/E = cheaper, so context matters.

    Example:
        rank = percentile_rank("Technology", "roic", 0.35)
        print(f"ROIC of 35% is in the {rank:.0f}th percentile for Tech")
        # => "ROIC of 35% is in the 82nd percentile for Tech"
    """
    data = _BENCHMARKS.get(sector) or _BENCHMARKS.get("S&P 500", {})
    dist = data.get(metric)
    if not dist:
        return 50.0  # unknown metric: return median

    p25, p50, p75 = dist["p25"], dist["p50"], dist["p75"]

    if value <= p25:
        # Below p25: interpolate from 0 to 25
        span = p25 - (p25 - (p50 - p25))  # extrapolate lower bound
        if span == 0:
            return 0.0
        pct = 25 * (value - (p25 - (p50 - p25))) / (p50 - p25)
        return max(0.0, min(25.0, pct))

    if value <= p50:
        # p25 to p50 → 25th to 50th
        span = p50 - p25
        if span == 0:
            return 25.0
        return 25.0 + 25.0 * (value - p25) / span

    if value <= p75:
        # p50 to p75 → 50th to 75th
        span = p75 - p50
        if span == 0:
            return 75.0
        return 50.0 + 25.0 * (value - p50) / span

    # Above p75: interpolate from 75 to 100
    span = p75 - p50
    if span == 0:
        return 100.0
    pct = 75.0 + 25.0 * (value - p75) / span
    return min(100.0, pct)


def available_sectors() -> list[str]:
    """Return the list of sectors with benchmark data."""
    return [s for s in _BENCHMARKS if s != "S&P 500"]
