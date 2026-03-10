"""
Risk and portfolio performance ratios.

References:
- Sharpe, W.F. (1966). Mutual Fund Performance. Journal of Business, 39(1), 119–138.
- Sortino, F.A., & van der Meer, R. (1991). Downside Risk. Journal of Portfolio Management, 17(4), 27–31.
- Treynor, J.L. (1965). How to Rate Management of Investment Funds. Harvard Business Review, 43(1), 63–75.
- Jensen, M.C. (1968). The Performance of Mutual Funds in the Period 1945–1964. Journal of Finance, 23(2), 389–416.
- Keating, C., & Shadwick, W.F. (2002). A Universal Performance Measure. Journal of Performance Measurement.
- Rockafellar, R.T., & Uryasev, S. (2000). Optimization of Conditional Value-at-Risk.
  Journal of Risk, 2(3), 21–41.
"""
from __future__ import annotations
import math
from typing import Optional
from fin_ratios._utils import (
    safe_divide, std_dev, mean, percentile, max_drawdown,
    prices_to_returns, annualize_return
)


# ── Beta ──────────────────────────────────────────────────────────────────────

def beta(stock_returns: list[float], market_returns: list[float]) -> Optional[float]:
    """
    Beta (Market Sensitivity).
    Formula: Cov(r_stock, r_market) / Var(r_market)
    Interpretation:
      β = 1.0: moves exactly with market
      β > 1.0: more volatile than market (amplified)
      β < 1.0: less volatile than market (defensive)
      β < 0.0: inverse to market (rare)
    Reference: Sharpe, W.F. (1964). Capital Asset Prices: A Theory of Market Equilibrium
               under Conditions of Risk. Journal of Finance, 19(3), 425–442.
    """
    if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
        return None
    n = len(stock_returns)
    mean_stock = sum(stock_returns) / n
    mean_market = sum(market_returns) / n
    covariance = sum((stock_returns[i] - mean_stock) * (market_returns[i] - mean_market) for i in range(n))
    variance_market = sum((r - mean_market) ** 2 for r in market_returns)
    return safe_divide(covariance, variance_market)

beta.formula = "Cov(r_stock, r_market) / Var(r_market)"  # type: ignore[attr-defined]
beta.description = "Sensitivity to market returns. β=1 moves with market; β>1 amplified."  # type: ignore[attr-defined]


# ── Jensen's Alpha ────────────────────────────────────────────────────────────

def jensens_alpha(
    portfolio_return: float,
    risk_free_rate: float,
    beta_val: float,
    market_return: float,
) -> float:
    """
    Jensen's Alpha.
    Formula: Rp - [Rf + β × (Rm - Rf)]
    Interpretation:
      α > 0: manager outperformed CAPM prediction (skill)
      α < 0: underperformed CAPM (lack of skill or bad luck)
    Reference: Jensen, M.C. (1968). The Performance of Mutual Funds 1945–1964.
               Journal of Finance, 23(2), 389–416.
    """
    return portfolio_return - (risk_free_rate + beta_val * (market_return - risk_free_rate))

jensens_alpha.formula = "Rp - [Rf + β × (Rm - Rf)]"  # type: ignore[attr-defined]
jensens_alpha.description = "Excess return above CAPM prediction. Positive = outperformance."  # type: ignore[attr-defined]


# ── Sharpe Ratio ──────────────────────────────────────────────────────────────

def sharpe_ratio(
    returns: list[float],
    risk_free_rate: float,
    periods_per_year: float = 252,
) -> Optional[float]:
    """
    Sharpe Ratio.
    Formula: (Annualized Return - Rf) / Annualized Volatility
    Interpretation:
      > 2.0: Excellent
      1.0–2.0: Good
      0.5–1.0: Acceptable
      < 0.5: Poor
    Reference: Sharpe, W.F. (1966). Mutual Fund Performance.
               Journal of Business, 39(1), 119–138.
    Note: Assumes normally distributed returns — use Sortino for asymmetric.
    """
    avg_return = mean(returns)
    vol = std_dev(returns, ddof=1)
    if avg_return is None or vol is None or vol == 0:
        return None
    annualized_return = annualize_return(avg_return, periods_per_year)
    annualized_vol = vol * math.sqrt(periods_per_year)
    return safe_divide(annualized_return - risk_free_rate, annualized_vol)

sharpe_ratio.formula = "(Annualized Return - Rf) / Annualized Volatility"  # type: ignore[attr-defined]
sharpe_ratio.description = "Risk-adjusted return per unit of total volatility. > 1 is good, > 2 is excellent."  # type: ignore[attr-defined]


# ── Sortino Ratio ─────────────────────────────────────────────────────────────

def sortino_ratio(
    returns: list[float],
    risk_free_rate: float,
    mar: float = 0.0,
    periods_per_year: float = 252,
) -> Optional[float]:
    """
    Sortino Ratio.
    Formula: (Annualized Return - Rf) / Downside Deviation
    Key advantage over Sharpe: only penalizes DOWNSIDE volatility (bad volatility).
    Upside volatility is not penalized (investors want upside surprises).
    Reference: Sortino, F.A., & van der Meer, R. (1991). Downside Risk.
               Journal of Portfolio Management, 17(4), 27–31.
    """
    avg_return = mean(returns)
    if avg_return is None:
        return None
    downside = [r for r in returns if r < mar]
    if not downside:
        return None
    downside_var = sum((r - mar) ** 2 for r in returns) / len(returns)
    downside_dev = math.sqrt(downside_var) * math.sqrt(periods_per_year)
    if downside_dev == 0:
        return None
    annualized_return = annualize_return(avg_return, periods_per_year)
    return safe_divide(annualized_return - risk_free_rate, downside_dev)

sortino_ratio.formula = "(Annualized Return - Rf) / Downside Deviation"  # type: ignore[attr-defined]
sortino_ratio.description = "Like Sharpe but only penalizes downside volatility."  # type: ignore[attr-defined]


# ── Treynor Ratio ─────────────────────────────────────────────────────────────

def treynor_ratio(
    portfolio_return: float,
    risk_free_rate: float,
    beta_val: float,
) -> Optional[float]:
    """
    Treynor Ratio.
    Formula: (Rp - Rf) / Beta
    Measures return per unit of SYSTEMATIC (market) risk, not total risk.
    Useful for comparing managers who hold diversified portfolios.
    Reference: Treynor, J.L. (1965). How to Rate Management of Investment Funds.
               Harvard Business Review, 43(1), 63–75.
    """
    return safe_divide(portfolio_return - risk_free_rate, beta_val)

treynor_ratio.formula = "(Portfolio Return - Risk-Free Rate) / Beta"  # type: ignore[attr-defined]
treynor_ratio.description = "Risk-adjusted return per unit of systematic (market) risk."  # type: ignore[attr-defined]


# ── Calmar Ratio ─────────────────────────────────────────────────────────────

def calmar_ratio(returns: list[float], periods_per_year: float = 252) -> Optional[float]:
    """
    Calmar Ratio.
    Formula: Annualized Return / Maximum Drawdown
    Measures return relative to worst-case historical loss.
    Popular in hedge fund and CTA (managed futures) analysis.
    Benchmark: > 0.5 acceptable; > 1.0 good; > 3.0 excellent
    Reference: Young, T.W. (1991). Calmar Ratio: A Smoother Tool. Futures Magazine.
    """
    avg_return = mean(returns)
    if avg_return is None:
        return None
    prices = [1.0]
    cur = 1.0
    for r in returns:
        cur *= (1 + r)
        prices.append(cur)
    mdd = max_drawdown(prices)
    if mdd is None or mdd == 0:
        return None
    annualized_return = annualize_return(avg_return, periods_per_year)
    return safe_divide(annualized_return, mdd)

calmar_ratio.formula = "Annualized Return / Maximum Drawdown"  # type: ignore[attr-defined]
calmar_ratio.description = "Return relative to worst drawdown. Popular in hedge fund analysis."  # type: ignore[attr-defined]


# ── Information Ratio ─────────────────────────────────────────────────────────

def information_ratio(
    portfolio_returns: list[float],
    benchmark_returns: list[float],
) -> Optional[float]:
    """
    Information Ratio (IR).
    Formula: Mean Active Return / Tracking Error
    Measures consistency of outperformance vs benchmark.
    Benchmark: IR > 0.5 is considered good; IR > 1.0 is exceptional.
    Reference: Grinold, R.C., & Kahn, R.N. (1999). Active Portfolio Management (2nd ed.). McGraw-Hill.
    """
    if len(portfolio_returns) != len(benchmark_returns):
        return None
    active = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
    avg_active = mean(active)
    te = std_dev(active, ddof=1)
    return safe_divide(avg_active, te)

information_ratio.formula = "Mean Active Return / Tracking Error"  # type: ignore[attr-defined]
information_ratio.description = "Consistency of active outperformance. IR > 0.5 is good."  # type: ignore[attr-defined]


# ── Omega Ratio ───────────────────────────────────────────────────────────────

def omega_ratio(returns: list[float], threshold: float = 0.0) -> Optional[float]:
    """
    Omega Ratio.
    Formula: Sum of gains above threshold / Sum of losses below threshold
    Key advantage: makes no distributional assumptions — fully non-parametric.
    Captures ALL higher moments (skewness, kurtosis) automatically.
    Omega > 1.0 means return distribution is favorable.
    Reference: Keating, C., & Shadwick, W.F. (2002). A Universal Performance Measure.
               Journal of Performance Measurement, 6(3), 59–84.
    """
    gains = sum(r - threshold for r in returns if r > threshold)
    losses = sum(threshold - r for r in returns if r < threshold)
    return safe_divide(gains, losses)

omega_ratio.formula = "E[returns above threshold] / E[returns below threshold]"  # type: ignore[attr-defined]
omega_ratio.description = "Non-parametric risk-adjusted return. > 1 is favorable."  # type: ignore[attr-defined]


# ── Maximum Drawdown ──────────────────────────────────────────────────────────

def maximum_drawdown(prices: list[float]) -> Optional[float]:
    """
    Maximum Drawdown (MDD).
    Formula: max[(Peak - Trough) / Peak]
    Measures the worst peak-to-trough loss in the period.
    """
    return max_drawdown(prices)

maximum_drawdown.formula = "(Peak - Trough) / Peak"  # type: ignore[attr-defined]
maximum_drawdown.description = "Largest peak-to-trough decline. Measures worst-case historical loss."  # type: ignore[attr-defined]


# ── Tracking Error ────────────────────────────────────────────────────────────

def tracking_error(
    portfolio_returns: list[float],
    benchmark_returns: list[float],
    periods_per_year: float = 252,
) -> Optional[float]:
    """
    Tracking Error (Active Risk).
    Formula: Annualized StdDev(Portfolio Return - Benchmark Return)
    Measures how closely a portfolio tracks its benchmark.
    Low TE = index-like; High TE = active/concentrated.
    """
    if len(portfolio_returns) != len(benchmark_returns):
        return None
    active = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
    te = std_dev(active, ddof=1)
    if te is None:
        return None
    return te * math.sqrt(periods_per_year)

tracking_error.formula = "Annualized StdDev(Portfolio Returns - Benchmark Returns)"  # type: ignore[attr-defined]
tracking_error.description = "How closely a portfolio tracks its benchmark."  # type: ignore[attr-defined]


# ── Value at Risk ─────────────────────────────────────────────────────────────

def historical_var(returns: list[float], confidence: float = 0.95) -> Optional[float]:
    """
    Historical Value at Risk (VaR).
    Formula: -Percentile(returns, 1 - confidence)
    Returns a positive value representing maximum expected loss at the confidence level.
    No distributional assumptions — directly uses historical distribution.
    Reference: Jorion, P. (2001). Value at Risk (2nd ed.). McGraw-Hill.
    """
    p = percentile(returns, 1 - confidence)
    return -p if p is not None else None

historical_var.formula = "-Percentile(returns, 1 - confidence)"  # type: ignore[attr-defined]
historical_var.description = "Historical VaR at given confidence level."  # type: ignore[attr-defined]


def parametric_var(returns: list[float], confidence: float = 0.95) -> Optional[float]:
    """
    Parametric VaR (Variance-Covariance Method).
    Formula: -(μ - z × σ)
    Assumes normally distributed returns. Computationally efficient.
    """
    mu = mean(returns)
    sigma = std_dev(returns, ddof=1)
    if mu is None or sigma is None:
        return None
    z_scores = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326, 0.999: 3.090}
    z = z_scores.get(confidence, 1.645)
    return -(mu - z * sigma)

parametric_var.formula = "-(μ - z × σ) where z is the normal quantile for confidence"  # type: ignore[attr-defined]
parametric_var.description = "Parametric VaR assuming normal distribution."  # type: ignore[attr-defined]


def conditional_var(returns: list[float], confidence: float = 0.95) -> Optional[float]:
    """
    Conditional VaR (CVaR) / Expected Shortfall (ES).
    Formula: -Mean(returns ≤ VaR threshold)
    Answers: 'Given we're in the worst X% of outcomes, what is the AVERAGE loss?'
    Superior to VaR as it measures tail risk, not just the threshold.
    Reference: Rockafellar, R.T., & Uryasev, S. (2000). Optimization of Conditional
               Value-at-Risk. Journal of Risk, 2(3), 21–41.
    """
    p = percentile(returns, 1 - confidence)
    if p is None:
        return None
    tail = [r for r in returns if r <= p]
    avg_tail = mean(tail)
    return -avg_tail if avg_tail is not None else None

conditional_var.formula = "-Mean(returns ≤ VaR threshold)"  # type: ignore[attr-defined]
conditional_var.description = "Average loss in the worst scenarios. Superior tail risk measure vs VaR."  # type: ignore[attr-defined]


# ── Ulcer Index ───────────────────────────────────────────────────────────────

def ulcer_index(prices: list[float]) -> Optional[float]:
    """
    Ulcer Index.
    Formula: sqrt(mean(drawdown_pct^2))
    Measures both the depth AND duration of drawdowns.
    Lower is less stressful / more stomach-friendly.
    Reference: Martin, P., & McCann, B. (1989). The Investor's Guide to Fidelity Funds.
    """
    if len(prices) < 2:
        return None
    peak = prices[0]
    drawdowns = []
    for p in prices:
        if p > peak:
            peak = p
        dd_pct = ((p - peak) / peak) * 100 if peak > 0 else 0.0
        drawdowns.append(dd_pct)
    mean_sq = sum(d ** 2 for d in drawdowns) / len(drawdowns)
    return math.sqrt(mean_sq)

ulcer_index.formula = "sqrt(mean(drawdown_pct^2))"  # type: ignore[attr-defined]
ulcer_index.description = "Measures drawdown depth and duration. Lower = less stressful."  # type: ignore[attr-defined]


# ── Capture Ratios ────────────────────────────────────────────────────────────

def upside_capture_ratio(
    portfolio_returns: list[float],
    benchmark_returns: list[float],
) -> Optional[float]:
    """
    Upside Capture Ratio.
    Formula: Portfolio Return (up markets) / Benchmark Return (up markets) × 100
    > 100% = outperformed benchmark in rising markets.
    """
    pairs = [(p, b) for p, b in zip(portfolio_returns, benchmark_returns) if b > 0]
    if not pairs:
        return None
    avg_port = mean([p for p, _ in pairs])
    avg_bench = mean([b for _, b in pairs])
    result = safe_divide(avg_port, avg_bench)
    return result * 100 if result is not None else None

upside_capture_ratio.formula = "Portfolio Return (up markets) / Benchmark Return (up markets) × 100"  # type: ignore[attr-defined]
upside_capture_ratio.description = "> 100% means outperformed in rising markets."  # type: ignore[attr-defined]


def downside_capture_ratio(
    portfolio_returns: list[float],
    benchmark_returns: list[float],
) -> Optional[float]:
    """
    Downside Capture Ratio.
    Formula: Portfolio Return (down markets) / Benchmark Return (down markets) × 100
    < 100% = lost less than benchmark in falling markets (defensive).
    """
    pairs = [(p, b) for p, b in zip(portfolio_returns, benchmark_returns) if b < 0]
    if not pairs:
        return None
    avg_port = mean([p for p, _ in pairs])
    avg_bench = mean([b for _, b in pairs])
    result = safe_divide(avg_port, avg_bench)
    return result * 100 if result is not None else None

downside_capture_ratio.formula = "Portfolio Return (down markets) / Benchmark Return (down markets) × 100"  # type: ignore[attr-defined]
downside_capture_ratio.description = "< 100% means lost less than benchmark in down markets."  # type: ignore[attr-defined]
