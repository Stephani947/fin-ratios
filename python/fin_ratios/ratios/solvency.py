"""
Solvency and leverage ratios — measure long-term financial stability.

References:
- Altman, E.I. (1968). Financial Ratios, Discriminant Analysis and the Prediction of
  Corporate Bankruptcy. The Journal of Finance, 23(4), 589–609.
"""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def debt_to_equity(total_debt: float, total_equity: float) -> Optional[float]:
    """
    Debt-to-Equity Ratio (D/E).
    Formula: Total Debt / Total Equity
    Benchmark: < 1.0 conservative; 1-2 moderate; > 2 highly leveraged
    Note: Varies hugely by industry — utilities/banks run much higher D/E than tech.
    """
    return safe_divide(total_debt, total_equity)

debt_to_equity.formula = "Total Debt / Total Equity"  # type: ignore[attr-defined]
debt_to_equity.description = "Financial leverage. Higher = more debt-financed."  # type: ignore[attr-defined]


def net_debt_to_equity(total_debt: float, cash: float, total_equity: float) -> Optional[float]:
    """
    Net Debt-to-Equity.
    Formula: (Total Debt - Cash) / Total Equity
    Negative = net cash position (no net debt).
    """
    return safe_divide(total_debt - cash, total_equity)

net_debt_to_equity.formula = "(Total Debt - Cash) / Total Equity"  # type: ignore[attr-defined]
net_debt_to_equity.description = "Net leverage after netting out cash. Negative = net cash."  # type: ignore[attr-defined]


def net_debt_to_ebitda(total_debt: float, cash: float, ebitda: float) -> Optional[float]:
    """
    Net Debt / EBITDA.
    Formula: (Total Debt - Cash) / EBITDA
    Benchmark: Lenders often require < 3x. Investment grade typically < 2x.
    Interpretation: Approximate years to repay net debt from EBITDA.
    """
    return safe_divide(total_debt - cash, ebitda)

net_debt_to_ebitda.formula = "(Total Debt - Cash) / EBITDA"  # type: ignore[attr-defined]
net_debt_to_ebitda.description = "Years to repay net debt from EBITDA. Lenders often require < 3x."  # type: ignore[attr-defined]


def debt_to_assets(total_debt: float, total_assets: float) -> Optional[float]:
    """
    Debt-to-Assets Ratio.
    Formula: Total Debt / Total Assets
    Interpretation: Proportion of assets financed by creditors.
    """
    return safe_divide(total_debt, total_assets)

debt_to_assets.formula = "Total Debt / Total Assets"  # type: ignore[attr-defined]
debt_to_assets.description = "Proportion of total assets financed by debt."  # type: ignore[attr-defined]


def debt_to_capital(total_debt: float, total_equity: float) -> Optional[float]:
    """
    Debt-to-Capital Ratio.
    Formula: Total Debt / (Total Debt + Total Equity)
    """
    return safe_divide(total_debt, total_debt + total_equity)

debt_to_capital.formula = "Total Debt / (Total Debt + Total Equity)"  # type: ignore[attr-defined]
debt_to_capital.description = "Debt as a proportion of total capital structure."  # type: ignore[attr-defined]


def interest_coverage_ratio(ebit: float, interest_expense: float) -> Optional[float]:
    """
    Interest Coverage Ratio (ICR / Times Interest Earned).
    Formula: EBIT / Interest Expense
    Benchmark: > 3x healthy; < 1.5x risky; < 1.0x cannot cover interest from operations
    Credit agencies watch this closely for downgrades.
    """
    return safe_divide(ebit, interest_expense)

interest_coverage_ratio.formula = "EBIT / Interest Expense"  # type: ignore[attr-defined]
interest_coverage_ratio.description = "Times interest is earned. < 1.5 is considered risky."  # type: ignore[attr-defined]


def ebitda_coverage_ratio(ebitda: float, interest_expense: float) -> Optional[float]:
    """
    EBITDA Interest Coverage Ratio.
    Formula: EBITDA / Interest Expense
    Softer version — adds back non-cash D&A before coverage calculation.
    """
    return safe_divide(ebitda, interest_expense)

ebitda_coverage_ratio.formula = "EBITDA / Interest Expense"  # type: ignore[attr-defined]
ebitda_coverage_ratio.description = "Softer coverage ratio adding back D&A non-cash charges."  # type: ignore[attr-defined]


def debt_service_coverage_ratio(
    net_operating_income: float,
    annual_debt_service: float,
) -> Optional[float]:
    """
    Debt Service Coverage Ratio (DSCR).
    Formula: Net Operating Income / (Principal Payments + Interest)
    Benchmark: Lenders require > 1.25x for commercial real estate; > 1.35x for construction.
    Critical for real estate, leveraged buyouts, project finance.
    """
    return safe_divide(net_operating_income, annual_debt_service)

debt_service_coverage_ratio.formula = "Net Operating Income / Annual Debt Service (Principal + Interest)"  # type: ignore[attr-defined]
debt_service_coverage_ratio.description = "Lenders require > 1.25x. Critical for real estate and LBO deals."  # type: ignore[attr-defined]


def equity_multiplier(total_assets: float, total_equity: float) -> Optional[float]:
    """
    Equity Multiplier (Financial Leverage Ratio).
    Formula: Total Assets / Total Equity
    This is the leverage component of the DuPont ROE decomposition.
    """
    return safe_divide(total_assets, total_equity)

equity_multiplier.formula = "Total Assets / Total Equity"  # type: ignore[attr-defined]
equity_multiplier.description = "Leverage component of DuPont analysis. Higher = more debt-financed."  # type: ignore[attr-defined]
