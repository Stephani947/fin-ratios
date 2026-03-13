"""Efficiency / activity ratios — measure how well assets are utilized."""

from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def asset_turnover(revenue: float, avg_total_assets: float) -> Optional[float]:
    """
    Asset Turnover Ratio.
    Formula: Revenue / Average Total Assets
    Benchmark: Retail 2-3x; manufacturing 0.5-1.5x; software 0.5-1.0x
    High turnover = asset-light; Low = capital-intensive.
    """
    return safe_divide(revenue, avg_total_assets)


asset_turnover.formula = "Revenue / Average Total Assets"  # type: ignore[attr-defined]
asset_turnover.description = "Revenue generated per dollar of assets deployed."  # type: ignore[attr-defined]


def fixed_asset_turnover(revenue: float, avg_net_ppe: float) -> Optional[float]:
    """
    Fixed Asset Turnover.
    Formula: Revenue / Average Net PP&E
    Measures efficiency of physical assets specifically.
    """
    return safe_divide(revenue, avg_net_ppe)


fixed_asset_turnover.formula = "Revenue / Average Net PP&E"  # type: ignore[attr-defined]
fixed_asset_turnover.description = "Revenue generated per dollar of fixed assets."  # type: ignore[attr-defined]


def inventory_turnover(cogs: float, avg_inventory: float) -> Optional[float]:
    """
    Inventory Turnover.
    Formula: COGS / Average Inventory
    Benchmark: Grocery 15-20x; auto 5-8x; luxury goods 1-3x
    High = less cash tied up in inventory.
    """
    return safe_divide(cogs, avg_inventory)


inventory_turnover.formula = "COGS / Average Inventory"  # type: ignore[attr-defined]
inventory_turnover.description = "Times inventory is sold per year. Higher = less capital tied up."  # type: ignore[attr-defined]


def receivables_turnover(revenue: float, avg_accounts_receivable: float) -> Optional[float]:
    """
    Receivables Turnover.
    Formula: Revenue / Average Accounts Receivable
    Higher = faster collections / shorter DSO.
    """
    return safe_divide(revenue, avg_accounts_receivable)


receivables_turnover.formula = "Revenue / Average Accounts Receivable"  # type: ignore[attr-defined]
receivables_turnover.description = "How quickly accounts receivable is collected."  # type: ignore[attr-defined]


def payables_turnover(cogs: float, avg_accounts_payable: float) -> Optional[float]:
    """
    Payables Turnover.
    Formula: COGS / Average Accounts Payable
    Lower = company takes longer to pay suppliers (more float).
    """
    return safe_divide(cogs, avg_accounts_payable)


payables_turnover.formula = "COGS / Average Accounts Payable"  # type: ignore[attr-defined]
payables_turnover.description = "How quickly the company pays its suppliers."  # type: ignore[attr-defined]


def capital_turnover(revenue: float, invested_capital: float) -> Optional[float]:
    """
    Capital Turnover.
    Formula: Revenue / Invested Capital
    Combined with NOPAT margin = ROIC (key value driver).
    """
    return safe_divide(revenue, invested_capital)


capital_turnover.formula = "Revenue / Invested Capital"  # type: ignore[attr-defined]
capital_turnover.description = "Revenue generated per dollar of invested capital."  # type: ignore[attr-defined]


def operating_leverage(
    ebit_current: float,
    ebit_prior: float,
    revenue_current: float,
    revenue_prior: float,
) -> Optional[float]:
    """
    Degree of Operating Leverage (DOL).
    Formula: % Change in EBIT / % Change in Revenue
    Interpretation: DOL = 3 means a 10% revenue increase → 30% EBIT increase.
    High fixed-cost businesses have higher DOL (more volatile).
    Reference: Mandelker, G.N., & Rhee, S.G. (1984). The Impact of the Degrees of
               Operating and Financial Leverage on Systematic Risk of Common Stock.
               Journal of Financial and Quantitative Analysis, 19(1), 45–57.
    """
    if ebit_prior == 0 or revenue_prior == 0:
        return None
    pct_ebit = (ebit_current - ebit_prior) / abs(ebit_prior)
    pct_rev = (revenue_current - revenue_prior) / abs(revenue_prior)
    return safe_divide(pct_ebit, pct_rev)


operating_leverage.formula = "% Change in EBIT / % Change in Revenue"  # type: ignore[attr-defined]
operating_leverage.description = "Sensitivity of EBIT to revenue changes. High = more fixed costs."  # type: ignore[attr-defined]
