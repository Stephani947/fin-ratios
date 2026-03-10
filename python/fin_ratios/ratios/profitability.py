"""
Profitability ratios — measure how efficiently a company generates profit.

References:
- Penman, S.H. (2013). Financial Statement Analysis and Security Valuation (5th ed.). McGraw-Hill.
- Soliman, M.T. (2008). The Use of DuPont Analysis by Market Participants. The Accounting Review, 83(3), 823–853.
"""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


# ── Margin Ratios ─────────────────────────────────────────────────────────────

def gross_margin(gross_profit: float, revenue: float) -> Optional[float]:
    """
    Gross Profit Margin.
    Formula: Gross Profit / Revenue
    Benchmark: Software 70-80%+; Retail 20-30%; Manufacturing 15-40%
    Interpretation: Pricing power and production cost efficiency.
    """
    return safe_divide(gross_profit, revenue)

gross_margin.formula = "Gross Profit / Revenue"  # type: ignore[attr-defined]
gross_margin.description = "Percentage of revenue remaining after cost of goods sold."  # type: ignore[attr-defined]


def operating_margin(ebit: float, revenue: float) -> Optional[float]:
    """
    Operating Profit Margin (EBIT Margin).
    Formula: EBIT / Revenue
    Benchmark: S&P 500 avg ~15%; software 20-35%; grocery 2-5%
    """
    return safe_divide(ebit, revenue)

operating_margin.formula = "EBIT / Revenue"  # type: ignore[attr-defined]
operating_margin.description = "Operating income as a percentage of revenue."  # type: ignore[attr-defined]


def ebitda_margin(ebitda: float, revenue: float) -> Optional[float]:
    """EBITDA Margin — operating margin before non-cash charges."""
    return safe_divide(ebitda, revenue)

ebitda_margin.formula = "EBITDA / Revenue"  # type: ignore[attr-defined]
ebitda_margin.description = "EBITDA as % of revenue. Proxy for cash generation capacity."  # type: ignore[attr-defined]


def net_profit_margin(net_income: float, revenue: float) -> Optional[float]:
    """
    Net Profit Margin.
    Formula: Net Income / Revenue
    Benchmark: S&P 500 avg ~10-12%; wide variation by sector
    """
    return safe_divide(net_income, revenue)

net_profit_margin.formula = "Net Income / Revenue"  # type: ignore[attr-defined]
net_profit_margin.description = "Bottom-line profitability after all expenses, interest and taxes."  # type: ignore[attr-defined]


# ── Return Ratios ─────────────────────────────────────────────────────────────

def roe(net_income: float, avg_total_equity: float) -> Optional[float]:
    """
    Return on Equity (ROE).
    Formula: Net Income / Average Total Shareholders' Equity
    Benchmark: > 15% is generally considered good; Buffett looks for > 20%
    Reference: Soliman (2008) demonstrates ROE drives stock returns via DuPont.
    """
    return safe_divide(net_income, avg_total_equity)

roe.formula = "Net Income / Average Total Shareholders' Equity"  # type: ignore[attr-defined]
roe.description = "How efficiently a company uses shareholder capital to generate profit."  # type: ignore[attr-defined]


def roa(net_income: float, avg_total_assets: float) -> Optional[float]:
    """
    Return on Assets (ROA).
    Formula: Net Income / Average Total Assets
    Benchmark: > 5% is good; banks typically 0.5-1.5%; asset-light firms 15-30%+
    """
    return safe_divide(net_income, avg_total_assets)

roa.formula = "Net Income / Average Total Assets"  # type: ignore[attr-defined]
roa.description = "How efficiently a company's assets generate profit."  # type: ignore[attr-defined]


def nopat(ebit: float, tax_rate: float) -> float:
    """
    Net Operating Profit After Tax (NOPAT).
    Formula: EBIT × (1 - Tax Rate)
    Removes financing structure effects for pure operational comparison.
    """
    return ebit * (1 - tax_rate)

nopat.formula = "EBIT × (1 - Effective Tax Rate)"  # type: ignore[attr-defined]
nopat.description = "Operating profit after tax, removing financing effects."  # type: ignore[attr-defined]


def roic(nopat_value: float, invested_capital: float) -> Optional[float]:
    """
    Return on Invested Capital (ROIC).
    Formula: NOPAT / Invested Capital
    Interpretation: The single best measure of value creation.
      ROIC > WACC → creates value (positive spread)
      ROIC < WACC → destroys value (negative spread)
    Benchmark: World-class companies sustain 20-40%+ ROIC
    Reference: Koller, T., Goedhart, M., & Wessels, D. (2020). Valuation (7th ed.). Wiley/McKinsey. Ch. 3.
    """
    return safe_divide(nopat_value, invested_capital)

roic.formula = "NOPAT / Invested Capital"  # type: ignore[attr-defined]
roic.description = "ROIC vs WACC determines whether a company creates or destroys economic value."  # type: ignore[attr-defined]


def roce(ebit: float, total_assets: float, current_liabilities: float) -> Optional[float]:
    """
    Return on Capital Employed (ROCE).
    Formula: EBIT / (Total Assets - Current Liabilities)
    Capital Employed = Total Assets - Current Liabilities
    """
    capital_employed = total_assets - current_liabilities
    return safe_divide(ebit, capital_employed)

roce.formula = "EBIT / (Total Assets - Current Liabilities)"  # type: ignore[attr-defined]
roce.description = "Measures return on all long-term capital (debt + equity)."  # type: ignore[attr-defined]


def rote(
    net_income: float,
    avg_total_equity: float,
    avg_goodwill: float,
    avg_intangible_assets: float,
) -> Optional[float]:
    """
    Return on Tangible Equity (ROTE).
    Formula: Net Income / (Avg Equity - Avg Goodwill - Avg Intangibles)
    Interpretation: Strips acquisition premiums. Preferred for banks and acquirers.
    """
    tangible_equity = avg_total_equity - avg_goodwill - avg_intangible_assets
    return safe_divide(net_income, tangible_equity)

rote.formula = "Net Income / (Avg Equity - Avg Goodwill - Avg Intangibles)"  # type: ignore[attr-defined]
rote.description = "ROE stripped of acquisition premiums. Preferred for serial acquirers."  # type: ignore[attr-defined]


# ── DuPont Analysis ───────────────────────────────────────────────────────────

def du_pont_3(
    net_income: float,
    revenue: float,
    avg_total_assets: float,
    avg_total_equity: float,
) -> dict:
    """
    3-Factor DuPont Decomposition of ROE.
    Formula: ROE = Net Profit Margin × Asset Turnover × Equity Multiplier

    Developed by Donaldson Brown at DuPont Corporation in the 1920s.
    Reference: Soliman, M.T. (2008). The Use of DuPont Analysis by Market Participants.
               The Accounting Review, 83(3), 823–853.
    """
    margin = safe_divide(net_income, revenue)
    turnover = safe_divide(revenue, avg_total_assets)
    multiplier = safe_divide(avg_total_assets, avg_total_equity)
    roe_val = (
        margin * turnover * multiplier
        if margin is not None and turnover is not None and multiplier is not None
        else None
    )
    return {
        "net_profit_margin": margin,
        "asset_turnover": turnover,
        "equity_multiplier": multiplier,
        "roe": roe_val,
    }

du_pont_3.formula = "ROE = Net Profit Margin × Asset Turnover × Equity Multiplier"  # type: ignore[attr-defined]
du_pont_3.description = "Decomposes ROE into margin, efficiency, and leverage components."  # type: ignore[attr-defined]


# ── Capital & Per-Employee ─────────────────────────────────────────────────────

def invested_capital(total_equity: float, total_debt: float, cash: float) -> float:
    """
    Invested Capital.
    Formula: Total Equity + Total Debt - Excess Cash
    """
    return total_equity + total_debt - cash

invested_capital.formula = "Total Equity + Total Debt - Excess Cash"  # type: ignore[attr-defined]
invested_capital.description = "Capital deployed to generate operating returns."  # type: ignore[attr-defined]


def revenue_per_employee(revenue: float, employee_count: float) -> Optional[float]:
    """Revenue generated per full-time employee."""
    return safe_divide(revenue, employee_count)

revenue_per_employee.formula = "Revenue / Full-Time Employees"  # type: ignore[attr-defined]
revenue_per_employee.description = "Workforce productivity. Apple: ~$2M/employee; Walmart: ~$250K/employee"  # type: ignore[attr-defined]


def profit_per_employee(net_income: float, employee_count: float) -> Optional[float]:
    """Net income generated per full-time employee."""
    return safe_divide(net_income, employee_count)

profit_per_employee.formula = "Net Income / Full-Time Employees"  # type: ignore[attr-defined]
profit_per_employee.description = "Net profit generated per employee."  # type: ignore[attr-defined]
