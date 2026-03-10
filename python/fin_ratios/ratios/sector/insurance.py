"""Insurance company specific ratios."""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def loss_ratio(losses_incurred: float, premiums_earned: float) -> Optional[float]:
    """
    Loss Ratio.
    Formula: Losses Incurred / Premiums Earned
    Benchmark: P&C: < 60% is good; 60-75% is acceptable; > 80% is poor
    """
    return safe_divide(losses_incurred, premiums_earned)

loss_ratio.formula = "Losses Incurred / Premiums Earned"  # type: ignore[attr-defined]
loss_ratio.description = "Portion of premiums paid out as claims. P&C benchmark: < 60%."  # type: ignore[attr-defined]


def expense_ratio(underwriting_expenses: float, premiums_written: float) -> Optional[float]:
    """
    Expense Ratio.
    Formula: Underwriting Expenses / Net Premiums Written
    Cost efficiency of writing insurance policies.
    """
    return safe_divide(underwriting_expenses, premiums_written)

expense_ratio.formula = "Underwriting Expenses / Net Premiums Written"  # type: ignore[attr-defined]
expense_ratio.description = "Cost of writing insurance. Lower = more efficient operations."  # type: ignore[attr-defined]


def combined_ratio(loss_ratio_val: float, expense_ratio_val: float) -> float:
    """
    Combined Ratio — the KEY insurance profitability metric.
    Formula: Loss Ratio + Expense Ratio
    < 100%: Underwriting PROFIT
    = 100%: Break-even on underwriting
    > 100%: Underwriting LOSS (insurer relies on investment income to profit)
    Benchmark: Top insurers sustain < 95%; > 105% is unsustainable long-term
    """
    return loss_ratio_val + expense_ratio_val

combined_ratio.formula = "Loss Ratio + Expense Ratio"  # type: ignore[attr-defined]
combined_ratio.description = "< 100% = underwriting profit. > 100% = underwriting loss."  # type: ignore[attr-defined]


def underwriting_profit_margin(combined_ratio_val: float) -> float:
    """
    Underwriting Profit Margin.
    Formula: 1 - Combined Ratio
    Positive = underwriting profit. Negative = underwriting loss.
    """
    return 1 - combined_ratio_val

underwriting_profit_margin.formula = "1 - Combined Ratio"  # type: ignore[attr-defined]
underwriting_profit_margin.description = "Positive = underwriting profit. Most insurers also earn investment income."  # type: ignore[attr-defined]


def premiums_to_surplus(
    net_premiums_written: float,
    policyholder_surplus: float,
) -> Optional[float]:
    """
    Premiums-to-Surplus Ratio (Kenney Ratio).
    Benchmark: < 2x is conservative; 2-3x is normal; > 3x = over-leveraged
    """
    return safe_divide(net_premiums_written, policyholder_surplus)

premiums_to_surplus.formula = "Net Premiums Written / Policyholder Surplus"  # type: ignore[attr-defined]
premiums_to_surplus.description = "Insurance leverage ratio. > 3x is considered risky."  # type: ignore[attr-defined]
