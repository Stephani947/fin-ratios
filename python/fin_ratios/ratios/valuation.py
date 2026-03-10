"""
Valuation ratios — measure how expensive a security is relative to fundamentals.

References:
- Graham, B., & Dodd, D. (1934). Security Analysis. McGraw-Hill.
- Damodaran, A. (2012). Investment Valuation (3rd ed.). Wiley.
- Greenblatt, J. (2005). The Little Book That Beats the Market. Wiley.
"""
from __future__ import annotations
import math
from typing import Optional
from fin_ratios._utils import safe_divide


# ── Price-to-Earnings ─────────────────────────────────────────────────────────

def pe(market_cap: float, net_income: float) -> Optional[float]:
    """
    Trailing Price-to-Earnings Ratio.
    Formula: Market Cap / Net Income
    Interpretation: How much investors pay per $1 of annual earnings.
    Benchmark: S&P 500 historical avg ~16x; high-growth stocks 30-100x+
    """
    return safe_divide(market_cap, net_income)

pe.formula = "Market Capitalization / Net Income"  # type: ignore[attr-defined]
pe.description = "How much investors pay per $1 of earnings. Lower = cheaper."  # type: ignore[attr-defined]


def forward_pe(price: float, forward_eps: float) -> Optional[float]:
    """
    Forward Price-to-Earnings Ratio.
    Formula: Stock Price / Analyst Forward EPS Estimate
    Interpretation: P/E based on expected next-12-months earnings.
    """
    return safe_divide(price, forward_eps)

forward_pe.formula = "Stock Price / Forward EPS Estimate"  # type: ignore[attr-defined]
forward_pe.description = "P/E based on next twelve months analyst EPS estimate."  # type: ignore[attr-defined]


# ── PEG ──────────────────────────────────────────────────────────────────────

def peg(pe_ratio: float, eps_growth_rate_pct: float) -> Optional[float]:
    """
    PEG Ratio (Price/Earnings-to-Growth).
    Formula: P/E Ratio / EPS Annual Growth Rate (%)
    Interpretation: < 1 = potentially undervalued relative to growth.
    Reference: Lynch, P. (1989). One Up on Wall Street.
    """
    return safe_divide(pe_ratio, eps_growth_rate_pct)

peg.formula = "P/E Ratio / EPS Annual Growth Rate (%)"  # type: ignore[attr-defined]
peg.description = "< 1 may indicate undervaluation relative to growth."  # type: ignore[attr-defined]


# ── Price-to-Book ─────────────────────────────────────────────────────────────

def pb(market_cap: float, total_equity: float) -> Optional[float]:
    """
    Price-to-Book Ratio.
    Formula: Market Cap / Total Shareholders' Equity
    Interpretation: < 1 = trading below net asset value (book).
    Benchmark: S&P 500 avg ~4x; banks often 1-2x; tech 10-20x+
    """
    return safe_divide(market_cap, total_equity)

pb.formula = "Market Capitalization / Total Shareholders' Equity"  # type: ignore[attr-defined]
pb.description = "< 1 may indicate trading below net asset value."  # type: ignore[attr-defined]


# ── Price-to-Sales ────────────────────────────────────────────────────────────

def ps(market_cap: float, revenue: float) -> Optional[float]:
    """
    Price-to-Sales Ratio.
    Formula: Market Cap / Revenue
    Interpretation: Useful when earnings are negative (startups, turnarounds).
    Benchmark: SaaS companies 5-20x; industrials 0.5-2x
    """
    return safe_divide(market_cap, revenue)

ps.formula = "Market Capitalization / Revenue"  # type: ignore[attr-defined]
ps.description = "Useful when earnings are negative."  # type: ignore[attr-defined]


# ── Price-to-FCF ──────────────────────────────────────────────────────────────

def p_fcf(market_cap: float, operating_cash_flow: float, capex: float) -> Optional[float]:
    """
    Price-to-Free-Cash-Flow Ratio.
    Formula: Market Cap / (Operating Cash Flow - Capex)
    Interpretation: Often considered cleaner than P/E (harder to manipulate).
    """
    fcf = operating_cash_flow - abs(capex)
    return safe_divide(market_cap, fcf)

p_fcf.formula = "Market Cap / (Operating Cash Flow - Capex)"  # type: ignore[attr-defined]
p_fcf.description = "Often considered cleaner than P/E (cash-based, harder to manipulate)."  # type: ignore[attr-defined]


# ── Enterprise Value ──────────────────────────────────────────────────────────

def enterprise_value(
    market_cap: float,
    total_debt: float,
    cash: float,
    minority_interest: float = 0.0,
    preferred_stock: float = 0.0,
) -> float:
    """
    Enterprise Value.
    Formula: Market Cap + Total Debt - Cash + Minority Interest + Preferred Stock
    Interpretation: Theoretical takeover price — what you actually pay to own a business.
    """
    return market_cap + total_debt - cash + minority_interest + preferred_stock

enterprise_value.formula = "Market Cap + Total Debt - Cash + Minority Interest + Preferred Stock"  # type: ignore[attr-defined]
enterprise_value.description = "Theoretical takeover price — capital-structure-neutral valuation base."  # type: ignore[attr-defined]


# ── EV Multiples ──────────────────────────────────────────────────────────────

def ev_ebitda(ev: float, ebitda: float) -> Optional[float]:
    """
    EV/EBITDA Multiple.
    Formula: Enterprise Value / EBITDA
    Interpretation: Capital-structure-neutral multiple. Widely used in LBO/M&A.
    Benchmark: S&P 500 avg ~14x; varies heavily by sector
    Reference: Koller, T., Goedhart, M., & Wessels, D. (2020). Valuation (7th ed.). Wiley/McKinsey.
    """
    return safe_divide(ev, ebitda)

ev_ebitda.formula = "Enterprise Value / EBITDA"  # type: ignore[attr-defined]
ev_ebitda.description = "Capital-structure-neutral valuation multiple. Popular in LBO analysis."  # type: ignore[attr-defined]


def ev_ebit(ev: float, ebit: float) -> Optional[float]:
    """
    EV/EBIT Multiple.
    Like EV/EBITDA but accounts for depreciation — better for capital-heavy businesses.
    """
    return safe_divide(ev, ebit)

ev_ebit.formula = "Enterprise Value / EBIT"  # type: ignore[attr-defined]
ev_ebit.description = "Like EV/EBITDA but penalizes capital-intensive businesses."  # type: ignore[attr-defined]


def ev_revenue(ev: float, revenue: float) -> Optional[float]:
    """EV/Revenue Multiple — useful for high-growth companies with negative EBITDA."""
    return safe_divide(ev, revenue)

ev_revenue.formula = "Enterprise Value / Revenue"  # type: ignore[attr-defined]
ev_revenue.description = "Useful for high-growth companies without positive EBITDA."  # type: ignore[attr-defined]


def ev_fcf(ev: float, free_cash_flow: float) -> Optional[float]:
    """EV/Free Cash Flow — preferred by value investors for its cash-based nature."""
    return safe_divide(ev, free_cash_flow)

ev_fcf.formula = "Enterprise Value / Free Cash Flow"  # type: ignore[attr-defined]
ev_fcf.description = "EV-to-free-cash-flow. Preferred by value investors."  # type: ignore[attr-defined]


# ── Tobin's Q ─────────────────────────────────────────────────────────────────

def tobin_q(market_cap: float, total_debt: float, total_assets: float) -> Optional[float]:
    """
    Tobin's Q Ratio.
    Formula: (Market Cap + Total Debt) / Total Assets
    Interpretation: Q > 1 = market values firm above replacement cost (growth expected).
    Reference: Tobin, J. (1969). A general equilibrium approach to monetary theory.
               Journal of Money, Credit and Banking, 1(1), 15–29.
    """
    return safe_divide(market_cap + total_debt, total_assets)

tobin_q.formula = "(Market Cap + Total Debt) / Total Assets"  # type: ignore[attr-defined]
tobin_q.description = "Q > 1: market values firm above asset replacement cost."  # type: ignore[attr-defined]


# ── Graham Models ─────────────────────────────────────────────────────────────

def graham_number(eps: float, book_value_per_share: float) -> Optional[float]:
    """
    Graham Number — Ben Graham's conservative intrinsic value estimate.
    Formula: sqrt(22.5 × EPS × Book Value Per Share)
    Interpretation: Maximum price a defensive investor should pay.
    Reference: Graham, B. (1973). The Intelligent Investor (4th ed.). Harper & Row.
    Note: 22.5 = 15 (max P/E) × 1.5 (max P/B) per Graham's criteria.
    """
    if eps <= 0 or book_value_per_share <= 0:
        return None
    return math.sqrt(22.5 * eps * book_value_per_share)

graham_number.formula = "sqrt(22.5 × EPS × Book Value Per Share)"  # type: ignore[attr-defined]
graham_number.description = "Graham's maximum fair value. Buy when price < Graham Number."  # type: ignore[attr-defined]


def graham_intrinsic_value(
    eps: float,
    growth_rate: float,
    aaa_bond_yield: float,
) -> Optional[float]:
    """
    Graham's Revised Intrinsic Value Formula (1974 edition).
    Formula: EPS × (8.5 + 2g) × 4.4 / Y
    Where: g = expected 7-10yr EPS growth rate (%), Y = current AAA bond yield (%)
    The 4.4 represents the AAA bond yield in 1962 when Graham derived the formula.
    Reference: Graham, B. (1974). The Intelligent Investor (Revised ed.). Harper & Row. Ch. 11.
    """
    if aaa_bond_yield <= 0:
        return None
    return safe_divide(eps * (8.5 + 2 * growth_rate) * 4.4, aaa_bond_yield)

graham_intrinsic_value.formula = "EPS × (8.5 + 2 × Growth%) × 4.4 / AAA Bond Yield%"  # type: ignore[attr-defined]
graham_intrinsic_value.description = "Graham's 1974 revised intrinsic value. growth_rate and aaa_bond_yield as percentages."  # type: ignore[attr-defined]
