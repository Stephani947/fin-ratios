"""
Liquidity ratios — measure ability to meet short-term obligations.

References:
- Beaver, W.H. (1966). Financial Ratios as Predictors of Failure.
  Journal of Accounting Research, 4, 71–111.
"""

from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
    """
    Current Ratio.
    Formula: Current Assets / Current Liabilities
    Benchmark: 1.5-3.0 is healthy. < 1.0 = potential near-term liquidity risk.
    Note: Too high (> 5) may indicate poor capital allocation (excess idle cash).
    """
    return safe_divide(current_assets, current_liabilities)


current_ratio.formula = "Current Assets / Current Liabilities"  # type: ignore[attr-defined]
current_ratio.description = "Ability to pay short-term obligations. > 1.5 is generally healthy."  # type: ignore[attr-defined]


def quick_ratio(
    cash: float,
    short_term_investments: float,
    accounts_receivable: float,
    current_liabilities: float,
) -> Optional[float]:
    """
    Quick Ratio (Acid-Test Ratio).
    Formula: (Cash + ST Investments + Accounts Receivable) / Current Liabilities
    Interpretation: Excludes inventory — more conservative than current ratio.
    Benchmark: > 1.0 is healthy. Tech companies often 2-5x.
    """
    liquid = cash + short_term_investments + accounts_receivable
    return safe_divide(liquid, current_liabilities)


quick_ratio.formula = "(Cash + ST Investments + Accounts Receivable) / Current Liabilities"  # type: ignore[attr-defined]
quick_ratio.description = "Liquidity without inventory. More conservative than current ratio."  # type: ignore[attr-defined]


def cash_ratio(
    cash: float, short_term_investments: float, current_liabilities: float
) -> Optional[float]:
    """
    Cash Ratio.
    Formula: (Cash + Short-Term Investments) / Current Liabilities
    Interpretation: Most conservative liquidity measure — only actual cash counts.
    """
    return safe_divide(cash + short_term_investments, current_liabilities)


cash_ratio.formula = "(Cash + Short-Term Investments) / Current Liabilities"  # type: ignore[attr-defined]
cash_ratio.description = "Most conservative liquidity measure. Only counts actual cash."  # type: ignore[attr-defined]


def operating_cash_flow_ratio(
    operating_cash_flow: float, current_liabilities: float
) -> Optional[float]:
    """
    Operating Cash Flow Ratio.
    Formula: Operating Cash Flow / Current Liabilities
    Interpretation: Can the company generate enough cash from operations to cover current debts?
    """
    return safe_divide(operating_cash_flow, current_liabilities)


operating_cash_flow_ratio.formula = "Operating Cash Flow / Current Liabilities"  # type: ignore[attr-defined]
operating_cash_flow_ratio.description = "How well operating cash covers short-term obligations."  # type: ignore[attr-defined]


# ── Working Capital Cycle ─────────────────────────────────────────────────────


def dso(accounts_receivable: float, revenue: float) -> Optional[float]:
    """
    Days Sales Outstanding (DSO).
    Formula: (Accounts Receivable / Revenue) × 365
    Interpretation: Average days to collect payment. Lower = faster collections.
    Benchmark: < 45 days is good for most industries.
    """
    return safe_divide(accounts_receivable * 365, revenue)


dso.formula = "(Accounts Receivable / Revenue) × 365"  # type: ignore[attr-defined]
dso.description = "Average days to collect payment after a sale. Lower is faster."  # type: ignore[attr-defined]


def dio(inventory: float, cogs: float) -> Optional[float]:
    """
    Days Inventory Outstanding (DIO).
    Formula: (Inventory / COGS) × 365
    Interpretation: Average days inventory is held. Lower = less cash tied up.
    """
    return safe_divide(inventory * 365, cogs)


dio.formula = "(Inventory / COGS) × 365"  # type: ignore[attr-defined]
dio.description = "Average days inventory is held before being sold. Lower is better."  # type: ignore[attr-defined]


def dpo(accounts_payable: float, cogs: float) -> Optional[float]:
    """
    Days Payable Outstanding (DPO).
    Formula: (Accounts Payable / COGS) × 365
    Interpretation: Average days to pay suppliers. Higher = more float (good for buyer).
    """
    return safe_divide(accounts_payable * 365, cogs)


dpo.formula = "(Accounts Payable / COGS) × 365"  # type: ignore[attr-defined]
dpo.description = "Average days taken to pay suppliers. Higher gives more working capital float."  # type: ignore[attr-defined]


def cash_conversion_cycle(dso_days: float, dio_days: float, dpo_days: float) -> float:
    """
    Cash Conversion Cycle (CCC).
    Formula: DSO + DIO - DPO
    Interpretation: Days from cash outflow to cash inflow.
      Negative CCC (e.g. Amazon, Costco) = customers pay before suppliers — float business.
      High positive CCC = capital-intensive, cash hungry.
    Reference: Richards, V.D., & Laughlin, E.J. (1980). A Cash Conversion Cycle Approach
               to Liquidity Analysis. Financial Management, 9(1), 32–38.
    """
    return dso_days + dio_days - dpo_days


cash_conversion_cycle.formula = "DSO + DIO - DPO"  # type: ignore[attr-defined]
cash_conversion_cycle.description = (
    "Days from paying for inventory to collecting from customers. Negative = float business."  # type: ignore[attr-defined]
)


def defensive_interval_ratio(
    cash: float,
    short_term_investments: float,
    accounts_receivable: float,
    daily_operating_expenses: float,
) -> Optional[float]:
    """
    Defensive Interval Ratio.
    Formula: (Cash + ST Investments + AR) / Daily Operating Expenses
    Interpretation: Days a company can operate using only liquid assets, without new revenue.
    """
    liquid = cash + short_term_investments + accounts_receivable
    return safe_divide(liquid, daily_operating_expenses)


defensive_interval_ratio.formula = "(Cash + ST Investments + AR) / Daily Operating Expenses"  # type: ignore[attr-defined]
defensive_interval_ratio.description = "Days the company can survive on liquid assets alone."  # type: ignore[attr-defined]
