"""
Intrinsic value and DCF models.

References:
- Williams, J.B. (1938). The Theory of Investment Value. Harvard University Press.
- Gordon, M.J. (1959). Dividends, Earnings, and Stock Prices. Review of Economics and Statistics, 41(2), 99-105.
- Damodaran, A. (2012). Investment Valuation (3rd ed.). Wiley.
"""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def dcf_2_stage(
    base_fcf: float,
    growth_rate: float,
    years: int,
    terminal_growth_rate: float,
    wacc: float,
    net_debt: float = 0.0,
    shares_outstanding: Optional[float] = None,
) -> Optional[dict]:
    """
    2-Stage Discounted Cash Flow Model.

    Stage 1: Explicit FCF projections growing at `growth_rate` for `years` years.
    Stage 2: Terminal value using Gordon Growth Model.

    Formula:
        EV = Σ [FCF_t / (1+WACC)^t] + [FCF_n*(1+g_T) / (WACC - g_T)] / (1+WACC)^n
        Equity Value = EV - Net Debt
        Intrinsic Value Per Share = Equity Value / Shares Outstanding

    Args:
        base_fcf: Trailing twelve-month free cash flow
        growth_rate: Stage 1 annual FCF growth rate (decimal, e.g. 0.15 for 15%)
        years: Number of years in high-growth stage
        terminal_growth_rate: Perpetual growth rate (decimal, typically 0.02-0.03)
        wacc: Weighted average cost of capital (decimal)
        net_debt: Total debt minus cash (positive = net debt, negative = net cash)
        shares_outstanding: Number of shares for per-share value

    Returns:
        dict with keys: intrinsic_value, intrinsic_value_per_share, pv_stage1,
                        pv_terminal_value, terminal_value, margin_of_safety_50pct

    Reference: Damodaran, A. (2012). Investment Valuation (3rd ed.). Wiley. Ch. 13.
    """
    if wacc <= terminal_growth_rate or wacc <= 0:
        return None

    pv_stage1 = 0.0
    fcf = base_fcf
    for t in range(1, years + 1):
        fcf *= (1 + growth_rate)
        pv_stage1 += fcf / (1 + wacc) ** t

    terminal_fcf = fcf * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    pv_terminal_value = terminal_value / (1 + wacc) ** years

    ev = pv_stage1 + pv_terminal_value
    equity_value = ev - net_debt
    intrinsic_value_per_share = safe_divide(equity_value, shares_outstanding)

    return {
        "intrinsic_value": equity_value,
        "intrinsic_value_per_share": intrinsic_value_per_share,
        "pv_stage1": pv_stage1,
        "pv_terminal_value": pv_terminal_value,
        "terminal_value": terminal_value,
        "pct_from_terminal": safe_divide(pv_terminal_value, ev),
    }

dcf_2_stage.formula = "Σ FCF_t/(1+WACC)^t + [FCF_n*(1+gT)/(WACC-gT)]/(1+WACC)^n"  # type: ignore[attr-defined]
dcf_2_stage.description = "2-stage DCF. Stage 1 explicit growth, Stage 2 terminal via Gordon Growth Model."  # type: ignore[attr-defined]


def gordon_growth_model(
    next_dividend: float,
    required_return: float,
    dividend_growth_rate: float,
) -> Optional[float]:
    """
    Gordon Growth Model (Dividend Discount Model — Constant Growth).

    Formula: P = D1 / (r - g)

    Assumptions:
    - Dividends grow at a constant rate g in perpetuity.
    - r > g (otherwise the model breaks down).

    Args:
        next_dividend: D1 — expected dividend over next 12 months
        required_return: r — investor's required rate of return (decimal)
        dividend_growth_rate: g — constant annual dividend growth rate (decimal)

    Reference: Gordon, M.J. (1959). Dividends, Earnings, and Stock Prices.
               Review of Economics and Statistics, 41(2), 99-105.
    """
    if required_return <= dividend_growth_rate:
        return None
    return safe_divide(next_dividend, required_return - dividend_growth_rate)

gordon_growth_model.formula = "D1 / (r - g)"  # type: ignore[attr-defined]
gordon_growth_model.description = "Constant-growth DDM. Only valid when required_return > growth_rate."  # type: ignore[attr-defined]


def reverse_dcf(
    market_cap: float,
    base_fcf: float,
    years: int,
    terminal_growth_rate: float,
    wacc: float,
    net_debt: float = 0.0,
) -> Optional[dict]:
    """
    Reverse DCF — solves for the implied FCF growth rate baked into the current price.

    Uses bisection search over 60 iterations to find g such that DCF(g) = market_cap.

    Interpretation:
    - If implied growth rate is unrealistically high (e.g. > 30%), the stock may be overvalued.
    - If implied growth is achievable/conservative, the stock may be undervalued.

    Reference: Mauboussin, M.J. (2006). More Than You Know. Columbia University Press.
    """
    target_ev = market_cap + net_debt

    def compute_ev(g: float) -> Optional[float]:
        result = dcf_2_stage(
            base_fcf=base_fcf,
            growth_rate=g,
            years=years,
            terminal_growth_rate=terminal_growth_rate,
            wacc=wacc,
        )
        return result["intrinsic_value"] + net_debt if result else None

    low, high = -0.50, 5.0
    for _ in range(60):
        mid = (low + high) / 2
        ev = compute_ev(mid)
        if ev is None:
            return None
        if abs(ev - target_ev) < 1000:
            break
        if ev < target_ev:
            low = mid
        else:
            high = mid

    implied_growth = (low + high) / 2
    return {
        "implied_growth_rate": implied_growth,
        "implied_growth_pct": implied_growth * 100,
        "interpretation": (
            f"Market implies {implied_growth * 100:.1f}% annual FCF growth "
            f"over {years} years at {wacc * 100:.1f}% WACC"
        ),
    }

reverse_dcf.formula = "Solve g: DCF(baseFCF, g, years, gT, WACC) = Market Cap"  # type: ignore[attr-defined]
reverse_dcf.description = "Reverse-engineers the FCF growth rate implied by the current stock price."  # type: ignore[attr-defined]
