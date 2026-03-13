"""REIT-specific financial metrics."""

from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def ffo(net_income: float, depreciation: float, gains_on_sale: float) -> float:
    """
    Funds From Operations (FFO).
    Formula: Net Income + Depreciation & Amortization - Gains on Sale of Properties
    The primary earnings metric for REITs — replaces net income.
    Why: GAAP depreciation overstates expenses for real estate (properties often appreciate).
    Reference: NAREIT (National Association of Real Estate Investment Trusts) White Paper.
    """
    return net_income + depreciation - gains_on_sale


ffo.formula = "Net Income + D&A - Gains on Sale of Properties"  # type: ignore[attr-defined]
ffo.description = "Primary REIT earnings metric. Strips out real estate depreciation distortion."  # type: ignore[attr-defined]


def affo(ffo_value: float, recurring_capex: float, straight_line_rent_adj: float) -> float:
    """
    Adjusted Funds From Operations (AFFO).
    Formula: FFO - Recurring Capex + Straight-Line Rent Adjustment
    Closer to true distributable cash flow than FFO.
    """
    return ffo_value - recurring_capex + straight_line_rent_adj


affo.formula = "FFO - Recurring Capex + Straight-Line Rent Adjustment"  # type: ignore[attr-defined]
affo.description = "Adjusted FFO — closer to actual distributable cash flow."  # type: ignore[attr-defined]


def p_ffo(market_cap: float, ffo_value: float) -> Optional[float]:
    """P/FFO — REIT equivalent of P/E ratio."""
    return safe_divide(market_cap, ffo_value)


p_ffo.formula = "Market Cap / FFO"  # type: ignore[attr-defined]
p_ffo.description = "REIT's P/E equivalent. Benchmark varies by REIT sub-sector."  # type: ignore[attr-defined]


def p_affo(market_cap: float, affo_value: float) -> Optional[float]:
    """P/AFFO — more conservative REIT valuation multiple."""
    return safe_divide(market_cap, affo_value)


p_affo.formula = "Market Cap / AFFO"  # type: ignore[attr-defined]
p_affo.description = "More conservative REIT valuation. Preferred by REIT analysts."  # type: ignore[attr-defined]


def net_operating_income(revenue: float, operating_expenses: float) -> float:
    """
    Net Operating Income (NOI).
    Formula: Revenue - Operating Expenses (excluding D&A and interest)
    The core property-level profitability metric.
    """
    return revenue - operating_expenses


net_operating_income.formula = "Revenue - Operating Expenses (ex-D&A, ex-interest)"  # type: ignore[attr-defined]
net_operating_income.description = "Core property profitability before debt and non-cash charges."  # type: ignore[attr-defined]


def cap_rate(noi: float, property_value: float) -> Optional[float]:
    """
    Capitalization Rate (Cap Rate).
    Formula: NOI / Property Value
    Benchmark: 4-5% premium markets (NYC, SF); 6-8% secondary markets; 8-10%+ tertiary
    Higher cap rate = higher yield but typically more risk.
    """
    return safe_divide(noi, property_value)


cap_rate.formula = "Net Operating Income / Property Value"  # type: ignore[attr-defined]
cap_rate.description = (
    "Expected annual return on property. Higher = higher yield, often higher risk."  # type: ignore[attr-defined]
)


def occupancy_rate(occupied_units: float, total_units: float) -> Optional[float]:
    """Occupancy rate — key operational health metric. > 95% is strong."""
    return safe_divide(occupied_units, total_units)


occupancy_rate.formula = "Occupied Units / Total Units"  # type: ignore[attr-defined]
occupancy_rate.description = "> 95% is strong. < 85% warrants investigation."  # type: ignore[attr-defined]
