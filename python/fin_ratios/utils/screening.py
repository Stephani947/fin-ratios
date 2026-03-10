"""
Stock screening / filtering utility.

Applies a set of ratio-based filters to a universe of stocks and returns
those that match all criteria.

Usage:
    from fin_ratios.utils.screening import screen

    universe = [
        {"ticker": "AAPL", "pe": 28, "roic": 0.55, "piotroski_score": 8},
        {"ticker": "IBM",  "pe": 15, "roic": 0.08, "piotroski_score": 4},
        {"ticker": "NVDA", "pe": 55, "roic": 0.45, "piotroski_score": 7},
    ]

    results = screen(universe, {
        "pe":               "< 35",
        "roic":             "> 0.20",
        "piotroski_score":  ">= 7",
    })
    # => [{"ticker": "AAPL", ...}]
"""

from __future__ import annotations

import operator
from typing import Any


# Mapping operator strings to Python operator functions
_OPS: dict[str, Any] = {
    ">":  operator.gt,
    ">=": operator.ge,
    "<":  operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


def _parse_filter(expr: str) -> tuple[Any, float]:
    """Parse "< 35" or ">= 0.20" into (operator_fn, threshold)."""
    expr = expr.strip()
    for op_str in (">=", "<=", "!=", ">", "<", "=="):
        if expr.startswith(op_str):
            threshold = float(expr[len(op_str):].strip())
            return _OPS[op_str], threshold
    raise ValueError(
        f"Invalid filter expression: '{expr}'. "
        f"Use one of: >, >=, <, <=, ==, !=   e.g. '> 0.15'"
    )


def screen(
    universe: list[dict[str, Any]],
    filters: dict[str, str],
    require_all: bool = True,
) -> list[dict[str, Any]]:
    """
    Filter a universe of stocks by ratio criteria.

    Args:
        universe:    List of dicts, each representing one stock.
                     Keys are metric names; values are floats (or None).
        filters:     Dict mapping metric name to filter expression string.
                     Expressions: "> 0.15", ">= 7", "< 20", "<= 2.5", "== 9"
        require_all: If True (default), stock must pass ALL filters.
                     If False, stock passes if it matches ANY filter.

    Returns:
        Filtered list of stock dicts that satisfy the criteria.

    Examples:
        # Magic Formula screen: cheap + high quality
        screen(universe, {
            "ev_ebitda":       "< 15",
            "roic":            "> 0.15",
        })

        # Deep-value Piotroski screen
        screen(universe, {
            "piotroski_score": ">= 8",
            "pe":              "< 15",
            "debt_to_equity":  "< 1.0",
        })

        # Altman safe zone only
        screen(universe, {"altman_z": "> 2.99"})

        # SaaS Rule of 40 filter
        screen(universe, {"rule_of_40": ">= 40"})
    """
    parsed = {metric: _parse_filter(expr) for metric, expr in filters.items()}

    results = []
    for stock in universe:
        passes = []
        for metric, (op_fn, threshold) in parsed.items():
            value = stock.get(metric)
            if value is None:
                passes.append(False)
                continue
            try:
                passes.append(op_fn(float(value), threshold))
            except (TypeError, ValueError):
                passes.append(False)

        if not passes:
            continue
        if require_all and all(passes):
            results.append(stock)
        elif not require_all and any(passes):
            results.append(stock)

    return results


def rank(
    universe: list[dict[str, Any]],
    metrics: list[str],
    ascending: list[bool] | None = None,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """
    Rank stocks by one or more metrics (Greenblatt-style combined rank).

    Each stock gets a rank per metric (1 = best). The combined rank is the
    sum of individual ranks. Stocks with the lowest combined rank appear first.

    Args:
        universe:  List of stock dicts.
        metrics:   Metric names to rank by.
        ascending: Per-metric sort direction.
                   True = lower value is better (e.g. P/E, D/E).
                   False = higher value is better (e.g. ROIC, margin).
                   Defaults to False (higher = better) for all metrics.
        top_n:     If provided, return only the top N results.

    Returns:
        List of dicts with added "_rank" and "_combined_rank" keys, sorted
        by combined rank ascending.

    Example:
        # Greenblatt Magic Formula: cheapest + highest quality
        ranked = rank(
            universe,
            metrics=["ev_ebitda", "roic"],
            ascending=[True, False],   # low EV/EBITDA = cheap; high ROIC = quality
            top_n=20,
        )
    """
    if ascending is None:
        ascending = [False] * len(metrics)

    if len(ascending) != len(metrics):
        raise ValueError("ascending must have the same length as metrics")

    # Assign per-metric ranks
    for i, (metric, asc) in enumerate(zip(metrics, ascending)):
        valid = [(j, stock) for j, stock in enumerate(universe)
                 if stock.get(metric) is not None]
        valid.sort(key=lambda x: float(x[1][metric]), reverse=not asc)
        for rank_pos, (orig_idx, _) in enumerate(valid, start=1):
            universe[orig_idx][f"_rank_{metric}"] = rank_pos
        # Stocks with None get worst rank
        worst_rank = len(valid) + 1
        for stock in universe:
            if stock.get(metric) is None:
                stock[f"_rank_{metric}"] = worst_rank

    # Combined rank = sum of individual ranks
    for stock in universe:
        stock["_combined_rank"] = sum(stock.get(f"_rank_{m}", 0) for m in metrics)

    universe.sort(key=lambda s: s["_combined_rank"])

    if top_n is not None:
        return universe[:top_n]
    return universe
