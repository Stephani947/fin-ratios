"""Cash flow ratios — measure quality and quantity of cash generation."""

from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def free_cash_flow(operating_cash_flow: float, capex: float) -> float:
    """
    Free Cash Flow (FCF).
    Formula: Operating Cash Flow - Capital Expenditures
    The most important measure of a business's cash-generating ability.
    Buffett considers this the foundation of intrinsic value.
    """
    return operating_cash_flow - abs(capex)


free_cash_flow.formula = "Operating Cash Flow - Capital Expenditures"  # type: ignore[attr-defined]
free_cash_flow.description = "Cash available after maintaining/growing asset base."  # type: ignore[attr-defined]


def levered_fcf(
    fcf: float,
    debt_issuance: float,
    debt_repayments: float,
) -> float:
    """
    Levered Free Cash Flow.
    Formula: FCF + Net Debt Change (Issuance - Repayments)
    Cash available to equity holders after debt service.
    """
    return fcf + debt_issuance - debt_repayments


levered_fcf.formula = "FCF + Debt Issuance - Debt Repayments"  # type: ignore[attr-defined]
levered_fcf.description = "FCF after accounting for debt financing activities."  # type: ignore[attr-defined]


def unlevered_fcf(
    nopat: float,
    depreciation_and_amortization: float,
    capex: float,
    change_in_working_capital: float,
) -> float:
    """
    Unlevered Free Cash Flow (FCFF — Free Cash Flow to Firm).
    Formula: NOPAT + D&A - Capex - Change in Working Capital
    Used in DCF models to value the whole enterprise (before debt effects).
    Reference: Damodaran, A. (2012). Investment Valuation (3rd ed.). Wiley. Ch. 11.
    """
    return nopat + depreciation_and_amortization - abs(capex) - change_in_working_capital


unlevered_fcf.formula = "NOPAT + D&A - Capex - Change in Working Capital"  # type: ignore[attr-defined]
unlevered_fcf.description = "FCF before debt payments — used in DCF to value the whole firm."  # type: ignore[attr-defined]


def owner_earnings(
    net_income: float,
    depreciation_and_amortization: float,
    maintenance_capex: float,
    change_in_working_capital: float = 0.0,
) -> float:
    """
    Owner Earnings (Buffett's Definition).
    Formula: Net Income + D&A - Maintenance Capex - Change in WC

    Warren Buffett introduced this concept in the 1986 Berkshire Hathaway letter.
    Key distinction: uses MAINTENANCE capex only (not total capex which includes growth).
    Reference: Buffett, W. (1986). Berkshire Hathaway Annual Letter to Shareholders.
    """
    return (
        net_income + depreciation_and_amortization - maintenance_capex - change_in_working_capital
    )


owner_earnings.formula = "Net Income + D&A - Maintenance Capex - Change in WC"  # type: ignore[attr-defined]
owner_earnings.description = "Buffett's owner earnings — true economic earnings to equity holders."  # type: ignore[attr-defined]


def fcf_yield(fcf: float, market_cap: float) -> Optional[float]:
    """
    FCF Yield.
    Formula: Free Cash Flow / Market Capitalization
    Interpretation: Inverse of P/FCF. Higher = cheaper.
    Benchmark: > 5% is attractive; < 2% is expensive
    """
    return safe_divide(fcf, market_cap)


fcf_yield.formula = "Free Cash Flow / Market Capitalization"  # type: ignore[attr-defined]
fcf_yield.description = "FCF per dollar invested. Inverse of P/FCF. Higher = cheaper."  # type: ignore[attr-defined]


def fcf_margin(fcf: float, revenue: float) -> Optional[float]:
    """FCF Margin — FCF generated per dollar of revenue."""
    return safe_divide(fcf, revenue)


fcf_margin.formula = "Free Cash Flow / Revenue"  # type: ignore[attr-defined]
fcf_margin.description = "FCF generated per dollar of revenue."  # type: ignore[attr-defined]


def fcf_conversion(fcf: float, net_income: float) -> Optional[float]:
    """
    FCF Conversion Rate.
    Formula: Free Cash Flow / Net Income
    > 1.0 = cash earnings exceed accounting earnings (quality signal)
    < 1.0 = accrual earnings exceed cash (quality concern)
    """
    return safe_divide(fcf, net_income)


fcf_conversion.formula = "Free Cash Flow / Net Income"  # type: ignore[attr-defined]
fcf_conversion.description = (
    "> 1 means earnings are backed by real cash. < 1 raises quality concerns."  # type: ignore[attr-defined]
)


def ocf_to_sales(operating_cash_flow: float, revenue: float) -> Optional[float]:
    """Operating Cash Flow to Sales — cash generated per dollar of sales."""
    return safe_divide(operating_cash_flow, revenue)


ocf_to_sales.formula = "Operating Cash Flow / Revenue"  # type: ignore[attr-defined]
ocf_to_sales.description = "Cash generated from operations per dollar of sales."  # type: ignore[attr-defined]


def capex_to_revenue(capex: float, revenue: float) -> Optional[float]:
    """Capex Intensity — investment spending as % of revenue."""
    return safe_divide(abs(capex), revenue)


capex_to_revenue.formula = "Capital Expenditures / Revenue"  # type: ignore[attr-defined]
capex_to_revenue.description = "Investment intensity. High in capital-intensive industries."  # type: ignore[attr-defined]


def capex_to_depreciation(capex: float, depreciation: float) -> Optional[float]:
    """
    Capex-to-Depreciation Ratio.
    > 1 = investing more than assets are aging (growth investment)
    < 1 = under-investing (harvesting the business)
    = 1 = maintenance mode
    """
    return safe_divide(abs(capex), depreciation)


capex_to_depreciation.formula = "Capital Expenditures / Depreciation"  # type: ignore[attr-defined]
capex_to_depreciation.description = "> 1: growing asset base. < 1: under-investing."  # type: ignore[attr-defined]
