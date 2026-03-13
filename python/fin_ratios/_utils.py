"""Shared math utilities used across all ratio modules."""

from __future__ import annotations
import math
from typing import Optional


def safe_divide(
    numerator: Optional[float],
    denominator: Optional[float],
) -> Optional[float]:
    """Divide two numbers, returning None instead of ZeroDivisionError / NaN."""
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


def std_dev(values: list[float], ddof: int = 1) -> Optional[float]:
    """Sample (ddof=1) or population (ddof=0) standard deviation."""
    if len(values) < 2:
        return None
    mean_ = sum(values) / len(values)
    variance = sum((v - mean_) ** 2 for v in values) / (len(values) - ddof)
    return math.sqrt(variance)


def mean(values: list[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def percentile(values: list[float], p: float) -> Optional[float]:
    """p in [0, 1]. Uses linear interpolation."""
    if not values:
        return None
    sorted_vals = sorted(values)
    idx = p * (len(sorted_vals) - 1)
    lower = int(idx)
    upper = math.ceil(idx)
    if lower == upper:
        return sorted_vals[lower]
    return sorted_vals[lower] + (sorted_vals[upper] - sorted_vals[lower]) * (idx - lower)


def max_drawdown(prices: list[float]) -> Optional[float]:
    """Returns maximum drawdown as a positive decimal (e.g. 0.3 for 30%)."""
    if len(prices) < 2:
        return None
    peak = prices[0]
    max_dd = 0.0
    for p in prices:
        if p > peak:
            peak = p
        if peak > 0:
            dd = (peak - p) / peak
            if dd > max_dd:
                max_dd = dd
    return max_dd


def prices_to_returns(prices: list[float]) -> list[float]:
    returns = []
    for i in range(1, len(prices)):
        prev, curr = prices[i - 1], prices[i]
        if prev != 0:
            returns.append((curr - prev) / prev)
    return returns


def cagr(start: Optional[float], end: Optional[float], years: float) -> Optional[float]:
    if start is None or end is None or years <= 0 or start <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def annualize_return(periodic_return: float, periods_per_year: float) -> float:
    return (1 + periodic_return) ** periods_per_year - 1
