"""
Backtesting Utility for Scoring Strategies.

Simulates a score-based long/short strategy across multiple companies using
historical financial data.  Revenue growth is used as the return proxy since
stock prices are not available from financial statements alone.

Strategy logic
--------------
For each year t in the intersection of all company series:
  1. Score each company on all available data up to year t.
  2. Classify companies as 'high-score' (>= threshold) or 'low-score'.
  3. Compute next-year revenue growth as the return proxy for each group.
  4. Record the excess return: high-score group return − low-score group return.

The resulting excess returns series is used to compute CAGR, Sharpe, maximum
drawdown, and hit rate.

References
----------
Fama, E.F. & French, K.R. (1992) — The Cross-Section of Expected Stock Returns.
                                    Journal of Finance.
Piotroski, J.D. (2000)           — Value Investing: The Use of Historical
                                    Financial Statement Information.
                                    Journal of Accounting Research.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Minimal statistical helpers (no external deps) ────────────────────────────

def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or end <= 0 or years <= 0:
        return 0.0
    return (end / start) ** (1.0 / years) - 1.0


def _max_drawdown(returns: list[float]) -> float:
    """Maximum peak-to-trough of cumulative return series."""
    if not returns:
        return 0.0
    cum = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        cum *= (1.0 + r)
        if cum > peak:
            peak = cum
        dd = (peak - cum) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd


def _sharpe(excess_returns: list[float], rf: float = 0.0) -> float:
    """Annualised Sharpe of annual excess-return series."""
    if len(excess_returns) < 2:
        return 0.0
    mean_ex = _mean(excess_returns) - rf
    std_ex = _std(excess_returns)
    return mean_ex / std_ex if std_ex > 0 else 0.0


# ── Score function registry ────────────────────────────────────────────────────

def _get_score_fn(name: str) -> Callable[..., Any]:
    """Return the appropriate *_from_series function by name."""
    if name == "quality":
        from .quality_score import quality_score_from_series
        return quality_score_from_series
    if name == "moat":
        from .moat_score import moat_score_from_series
        return moat_score_from_series
    if name == "capital_allocation":
        from .capital_allocation import capital_allocation_score_from_series
        return capital_allocation_score_from_series
    if name == "earnings_quality":
        from .earnings_quality import earnings_quality_score_from_series
        return earnings_quality_score_from_series
    if name == "management":
        from .management_score import management_quality_score_from_series
        return management_quality_score_from_series
    raise ValueError(
        f"Unknown score_fn {name!r}. "
        "Valid options: 'quality', 'moat', 'capital_allocation', 'earnings_quality', 'management'."
    )


_MIN_YEARS_BY_FN = {
    "quality": 2,
    "moat": 2,
    "capital_allocation": 2,
    "earnings_quality": 2,
    "management": 3,
}


# ── Revenue accessor ───────────────────────────────────────────────────────────

def _get_revenue(record: Any) -> Optional[float]:
    """Extract revenue from a record (dict, dataclass, or object)."""
    if isinstance(record, dict):
        for key in ("revenue", "total_revenue", "net_revenue"):
            val = record.get(key)
            if val is not None:
                try:
                    v = float(val)
                    return v if v == v and v > 0 else None
                except (TypeError, ValueError):
                    pass
        return None
    for attr in ("revenue", "total_revenue", "net_revenue"):
        val = getattr(record, attr, None)
        if val is not None:
            try:
                v = float(val)
                return v if v == v and v > 0 else None
            except (TypeError, ValueError):
                pass
    return None


# ── Result types ───────────────────────────────────────────────────────────────

@dataclass
class BacktestResult:
    """Results of a score-based strategy backtest.

    Attributes
    ----------
    strategy_cagr   : Annualised revenue CAGR proxy for the high-score group.
    benchmark_cagr  : Annualised revenue CAGR proxy for all companies.
    excess_cagr     : strategy_cagr - benchmark_cagr.
    strategy_sharpe : Sharpe ratio computed on annual excess returns.
    max_drawdown    : Maximum peak-to-trough in the strategy excess-return series.
    hit_rate        : Fraction of periods where high-score group outperformed.
    annual_results  : Per-year breakdown: year, strategy_return, benchmark_return, excess.
    threshold       : Score threshold used to define the high-score group.
    score_fn_name   : Name of the scoring function used.
    years           : Number of periods evaluated.
    """
    strategy_cagr:   float
    benchmark_cagr:  float
    excess_cagr:     float
    strategy_sharpe: float
    max_drawdown:    float
    hit_rate:        float
    annual_results:  list[dict]
    threshold:       int
    score_fn_name:   str
    years:           int


# ── Core backtest logic ────────────────────────────────────────────────────────

def _score_series(
    data: list[Any],
    fn: Callable,
    wacc: Optional[float],
    min_years: int,
    fn_name: str,
) -> list[Optional[int]]:
    """Score a company for each rolling window ending at index t."""
    scores: list[Optional[int]] = []
    for t in range(len(data)):
        window = data[: t + 1]
        if len(window) < min_years:
            scores.append(None)
            continue
        try:
            if fn_name in ("quality", "moat", "capital_allocation"):
                result = fn(window, wacc=wacc)
            else:
                result = fn(window)
        except Exception:
            scores.append(None)
            continue
        scores.append(result.score)
    return scores


def backtest_quality_strategy(
    companies: list[list[Any]],
    threshold: int = 60,
    score_fn: str = "quality",
    wacc: Optional[float] = None,
) -> BacktestResult:
    """Simulate a scoring strategy across multiple companies over time.

    For each year t in the intersection of all company series:
      1. Score each company using all data up to (and including) year t.
      2. Divide into high-score (score >= threshold) and low-score groups.
      3. Compute next-year revenue growth as the return proxy for each group.
      4. Record the excess return (high - low or high - all).

    Parameters
    ----------
    companies : list of list
        Each inner list is one company's annual data (oldest first).
        All lists must have at least ``min_years + 1`` records.
    threshold : int
        Minimum score (0–100) to be included in the 'long' (high-score) group.
        Default 60.
    score_fn : str
        Scoring function to use: ``'quality'`` (default), ``'moat'``,
        ``'capital_allocation'``, ``'earnings_quality'``, ``'management'``.
    wacc : float, optional
        WACC override passed to scoring functions that accept it.

    Returns
    -------
    BacktestResult

    Raises
    ------
    ValueError
        If fewer than 2 companies are provided, or no company has enough data.
    """
    if len(companies) < 2:
        raise ValueError("backtest_quality_strategy requires at least 2 company series.")

    fn = _get_score_fn(score_fn)
    min_years = _MIN_YEARS_BY_FN.get(score_fn, 2)

    # Pre-compute score series for each company
    all_scores: list[list[Optional[int]]] = []
    for company_data in companies:
        s = _score_series(company_data, fn, wacc, min_years, score_fn)
        all_scores.append(s)

    # Find the minimum common length (so we can do same-year comparisons)
    min_len = min(len(c) for c in companies)
    if min_len < min_years + 1:
        raise ValueError(
            f"All company series must have at least {min_years + 1} years of data "
            f"(min_years={min_years} for scoring + 1 for next-year return)."
        )

    annual_results: list[dict] = []
    strategy_cumulative: list[float] = []  # cumulative (1 + r) products for high-score group
    benchmark_cumulative: list[float] = []

    # For each year t (0-indexed), score is based on data[0:t+1],
    # and next-year return uses revenue growth from data[t] to data[t+1].
    for t in range(min_years - 1, min_len - 1):
        high_returns: list[float] = []
        all_returns: list[float] = []

        for i, company_data in enumerate(companies):
            score_t = all_scores[i][t]
            if score_t is None:
                continue

            rev_t = _get_revenue(company_data[t])
            rev_t1 = _get_revenue(company_data[t + 1])
            if rev_t is None or rev_t1 is None or rev_t <= 0:
                continue

            growth = (rev_t1 - rev_t) / rev_t
            all_returns.append(growth)
            if score_t >= threshold:
                high_returns.append(growth)

        if not all_returns:
            continue

        bench_ret = _mean(all_returns)
        strat_ret = _mean(high_returns) if high_returns else bench_ret  # no high-score → use benchmark
        excess = strat_ret - bench_ret

        annual_results.append({
            "year_index":        t,
            "strategy_return":   round(strat_ret, 6),
            "benchmark_return":  round(bench_ret, 6),
            "excess":            round(excess, 6),
            "n_high_score":      len(high_returns),
            "n_total":           len(all_returns),
        })
        strategy_cumulative.append(strat_ret)
        benchmark_cumulative.append(bench_ret)

    if not annual_results:
        raise ValueError(
            "No valid periods could be evaluated. "
            "Ensure companies have overlapping years and sufficient revenue data."
        )

    n_periods = len(annual_results)

    # CAGR via compounding of annual returns
    def _period_cagr(returns: list[float]) -> float:
        if not returns:
            return 0.0
        compound = 1.0
        for r in returns:
            compound *= (1.0 + r)
        return compound ** (1.0 / len(returns)) - 1.0

    strat_cagr = _period_cagr(strategy_cumulative)
    bench_cagr = _period_cagr(benchmark_cumulative)
    excess_returns = [r["excess"] for r in annual_results]
    hit_rate = sum(1 for e in excess_returns if e > 0) / len(excess_returns)

    return BacktestResult(
        strategy_cagr=round(strat_cagr, 6),
        benchmark_cagr=round(bench_cagr, 6),
        excess_cagr=round(strat_cagr - bench_cagr, 6),
        strategy_sharpe=round(_sharpe(excess_returns), 4),
        max_drawdown=round(_max_drawdown(excess_returns), 4),
        hit_rate=round(hit_rate, 4),
        annual_results=annual_results,
        threshold=threshold,
        score_fn_name=score_fn,
        years=n_periods,
    )


# ── Summary ────────────────────────────────────────────────────────────────────

def summarize_backtest(result: BacktestResult) -> str:
    """Return a formatted text summary of backtest results.

    Parameters
    ----------
    result : BacktestResult
        The output of :func:`backtest_quality_strategy`.

    Returns
    -------
    str
        Multi-line human-readable summary.
    """
    w = 56
    sep = "─" * w
    hit_desc = (
        "strong alpha signal" if result.hit_rate >= 0.70 else
        "moderate alpha signal" if result.hit_rate >= 0.55 else
        "mixed results" if result.hit_rate >= 0.45 else
        "weak signal (worse than random)"
    )

    def _pct(v: float) -> str:
        return f"{v * 100:+.2f}%"

    lines = [
        f"Backtest Summary — {result.score_fn_name.replace('_', ' ').title()} Strategy",
        sep,
        f"{'Score threshold':<36} {result.threshold:>5}/100",
        f"{'Periods evaluated':<36} {result.years:>5}",
        sep,
        f"{'Strategy CAGR (revenue proxy)':<36} {_pct(result.strategy_cagr):>8}",
        f"{'Benchmark CAGR (all companies)':<36} {_pct(result.benchmark_cagr):>8}",
        f"{'Excess CAGR':<36} {_pct(result.excess_cagr):>8}",
        sep,
        f"{'Strategy Sharpe ratio':<36} {result.strategy_sharpe:>8.2f}",
        f"{'Max drawdown (excess returns)':<36} {result.max_drawdown*100:>7.1f}%",
        f"{'Hit rate':<36} {result.hit_rate*100:>7.1f}%  [{hit_desc}]",
        sep,
        "Annual breakdown:",
    ]
    for row in result.annual_results:
        yr = row["year_index"]
        sr = row["strategy_return"]
        br = row["benchmark_return"]
        ex = row["excess"]
        nh = row["n_high_score"]
        nt = row["n_total"]
        lines.append(
            f"  Period {yr:>2}: strat {sr*100:+.1f}%  bench {br*100:+.1f}%  "
            f"excess {ex*100:+.1f}%  [{nh}/{nt} high-score]"
        )
    lines += [
        sep,
        "Note: Returns are revenue-growth proxies, not stock price returns.",
        "Strategy signal strength is indicative only.",
    ]
    return "\n".join(lines)
