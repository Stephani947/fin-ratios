"""Growth ratios — measure revenue, earnings, and value compounding over time."""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide, cagr


def _yoy(current: float, prior: float) -> Optional[float]:
    if prior == 0:
        return None
    return safe_divide(current - prior, abs(prior))


def revenue_growth(revenue_current: float, revenue_prior: float) -> Optional[float]:
    """Year-over-year revenue growth rate."""
    return _yoy(revenue_current, revenue_prior)

revenue_growth.formula = "(Revenue_t - Revenue_t-1) / |Revenue_t-1|"  # type: ignore[attr-defined]
revenue_growth.description = "Year-over-year revenue growth rate."  # type: ignore[attr-defined]


def revenue_cagr(revenue_start: float, revenue_end: float, years: float) -> Optional[float]:
    """
    Revenue Compound Annual Growth Rate (CAGR).
    Formula: (Revenue_end / Revenue_start)^(1/n) - 1
    Smooths out year-to-year volatility to show true growth trend.
    """
    return cagr(revenue_start, revenue_end, years)

revenue_cagr.formula = "(Revenue_end / Revenue_start)^(1/years) - 1"  # type: ignore[attr-defined]
revenue_cagr.description = "Compound annual growth rate of revenue over multiple years."  # type: ignore[attr-defined]


def eps_growth(eps_current: float, eps_prior: float) -> Optional[float]:
    """Year-over-year EPS growth rate."""
    return _yoy(eps_current, eps_prior)

eps_growth.formula = "(EPS_t - EPS_t-1) / |EPS_t-1|"  # type: ignore[attr-defined]
eps_growth.description = "Year-over-year earnings per share growth."  # type: ignore[attr-defined]


def ebitda_growth(ebitda_current: float, ebitda_prior: float) -> Optional[float]:
    """Year-over-year EBITDA growth rate."""
    return _yoy(ebitda_current, ebitda_prior)

ebitda_growth.formula = "(EBITDA_t - EBITDA_t-1) / |EBITDA_t-1|"  # type: ignore[attr-defined]
ebitda_growth.description = "Year-over-year EBITDA growth."  # type: ignore[attr-defined]


def fcf_growth(fcf_current: float, fcf_prior: float) -> Optional[float]:
    """Year-over-year FCF growth rate."""
    return _yoy(fcf_current, fcf_prior)

fcf_growth.formula = "(FCF_t - FCF_t-1) / |FCF_t-1|"  # type: ignore[attr-defined]
fcf_growth.description = "Year-over-year free cash flow growth."  # type: ignore[attr-defined]


def earnings_power_value(ebit: float, tax_rate: float, wacc: float) -> Optional[float]:
    """
    Earnings Power Value (EPV).
    Formula: EBIT × (1 - Tax Rate) / WACC
    Assumption: Zero growth — a conservative floor on intrinsic value.
    EPV > BV = good franchise; EPV < BV = value destruction.
    Reference: Greenwald, B., Kahn, J., Sonkin, P., & van Biema, M. (2001).
               Value Investing: From Graham to Buffett and Beyond. Wiley.
    """
    nopat_value = ebit * (1 - tax_rate)
    return safe_divide(nopat_value, wacc)

earnings_power_value.formula = "EBIT × (1 - Tax Rate) / WACC"  # type: ignore[attr-defined]
earnings_power_value.description = "EPV — intrinsic value assuming zero growth. Conservative lower bound."  # type: ignore[attr-defined]
