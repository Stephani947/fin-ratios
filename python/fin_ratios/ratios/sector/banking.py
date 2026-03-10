"""Banking and financial institution specific ratios."""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def net_interest_margin(
    interest_income: float,
    interest_expense: float,
    avg_earning_assets: float,
) -> Optional[float]:
    """
    Net Interest Margin (NIM).
    Formula: (Interest Income - Interest Expense) / Average Earning Assets
    Core profitability of a bank's lending business.
    Benchmark: US commercial banks typically 2-4%.
    """
    return safe_divide(interest_income - interest_expense, avg_earning_assets)

net_interest_margin.formula = "(Interest Income - Interest Expense) / Avg Earning Assets"  # type: ignore[attr-defined]
net_interest_margin.description = "Core bank profitability from lending. Benchmark: 2-4%."  # type: ignore[attr-defined]


def efficiency_ratio(
    non_interest_expense: float,
    net_interest_income: float,
    non_interest_income: float,
) -> Optional[float]:
    """
    Bank Efficiency Ratio.
    Formula: Non-Interest Expense / (Net Interest Income + Non-Interest Income)
    Cost to generate $1 of revenue. Lower = more efficient.
    Benchmark: < 50% = highly efficient; 50-60% = well-run; > 70% = concerning
    """
    return safe_divide(non_interest_expense, net_interest_income + non_interest_income)

efficiency_ratio.formula = "Non-Interest Expense / (Net Interest Income + Non-Interest Income)"  # type: ignore[attr-defined]
efficiency_ratio.description = "Cost per $1 of revenue. < 60% is well-run."  # type: ignore[attr-defined]


def loan_to_deposit_ratio(total_loans: float, total_deposits: float) -> Optional[float]:
    """
    Loan-to-Deposit Ratio (LDR).
    Benchmark: 80-90% is considered healthy. > 100% = borrowing to fund loans (risky).
    """
    return safe_divide(total_loans, total_deposits)

loan_to_deposit_ratio.formula = "Total Loans / Total Deposits"  # type: ignore[attr-defined]
loan_to_deposit_ratio.description = "Liquidity indicator. > 100% = more loans than deposits."  # type: ignore[attr-defined]


def npl_ratio(non_performing_loans: float, total_loans: float) -> Optional[float]:
    """
    Non-Performing Loan (NPL) Ratio.
    Benchmark: < 1% = excellent; 1-3% = acceptable; > 3% = concerning
    """
    return safe_divide(non_performing_loans, total_loans)

npl_ratio.formula = "Non-Performing Loans / Total Loans"  # type: ignore[attr-defined]
npl_ratio.description = "Asset quality metric. > 3% warrants scrutiny."  # type: ignore[attr-defined]


def provision_coverage_ratio(
    loan_loss_reserves: float,
    non_performing_loans: float,
) -> Optional[float]:
    """
    Provision Coverage Ratio.
    > 100% = fully reserved for bad loans (conservative)
    < 60% = potentially under-reserved
    """
    return safe_divide(loan_loss_reserves, non_performing_loans)

provision_coverage_ratio.formula = "Loan Loss Reserves / Non-Performing Loans"  # type: ignore[attr-defined]
provision_coverage_ratio.description = "> 100% = fully reserved. Conservative banks maintain 100-150%."  # type: ignore[attr-defined]


def tier1_capital_ratio(tier1_capital: float, risk_weighted_assets: float) -> Optional[float]:
    """
    Tier 1 Capital Ratio.
    Regulatory minimum: 6%; Well-capitalized: > 8%; Systemic banks: 10%+
    Basel III requirement.
    """
    return safe_divide(tier1_capital, risk_weighted_assets)

tier1_capital_ratio.formula = "Tier 1 Capital / Risk-Weighted Assets"  # type: ignore[attr-defined]
tier1_capital_ratio.description = "Core capital adequacy. Well-capitalized > 8% (Basel III)."  # type: ignore[attr-defined]


def cet1_ratio(common_equity_tier1: float, risk_weighted_assets: float) -> Optional[float]:
    """
    Common Equity Tier 1 (CET1) Ratio.
    Regulatory minimum: 4.5%; Recommended: 7%+ (including capital conservation buffer).
    Highest-quality capital — common equity only.
    """
    return safe_divide(common_equity_tier1, risk_weighted_assets)

cet1_ratio.formula = "Common Equity Tier 1 / Risk-Weighted Assets"  # type: ignore[attr-defined]
cet1_ratio.description = "Highest-quality capital ratio. Regulatory minimum 4.5%."  # type: ignore[attr-defined]


def tangible_book_value_per_share(
    total_equity: float,
    goodwill: float,
    intangible_assets: float,
    shares_outstanding: float,
) -> Optional[float]:
    """
    Tangible Book Value Per Share (TBVPS).
    Formula: (Equity - Goodwill - Intangibles) / Shares
    Most conservative per-share book value. Used extensively for banks.
    """
    tbv = total_equity - goodwill - intangible_assets
    return safe_divide(tbv, shares_outstanding)

tangible_book_value_per_share.formula = "(Equity - Goodwill - Intangibles) / Shares Outstanding"  # type: ignore[attr-defined]
tangible_book_value_per_share.description = "Conservative book value per share, stripped of acquisition premiums."  # type: ignore[attr-defined]
