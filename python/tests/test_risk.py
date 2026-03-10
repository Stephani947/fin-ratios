"""Tests for risk and portfolio ratios."""

import math
import pytest
from fin_ratios import (
    sharpe_ratio, sortino_ratio, treynor_ratio, calmar_ratio,
    information_ratio, omega_ratio,
    maximum_drawdown, historical_var, parametric_var, conditional_var,
    beta, jensens_alpha, tracking_error, ulcer_index,
    upside_capture_ratio, downside_capture_ratio,
)


def _returns_to_prices(returns: list[float], start: float = 100.0) -> list[float]:
    prices = [start]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    return prices


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def daily_returns():
    import random
    random.seed(42)
    return [random.gauss(0.0003, 0.01) for _ in range(252)]

@pytest.fixture
def daily_prices(daily_returns):
    return _returns_to_prices(daily_returns)

@pytest.fixture
def benchmark_returns():
    import random
    random.seed(123)
    return [random.gauss(0.0002, 0.008) for _ in range(252)]

@pytest.fixture
def benchmark_prices(benchmark_returns):
    return _returns_to_prices(benchmark_returns)


# ── Sharpe Ratio ──────────────────────────────────────────────────────────────

def test_sharpe_ratio_basic(daily_returns):
    result = sharpe_ratio(returns=daily_returns, risk_free_rate=0.05, periods_per_year=252)
    assert result is not None
    assert isinstance(result, float)
    assert -5 < result < 10

def test_sharpe_ratio_zero_std_dev():
    result = sharpe_ratio(returns=[0.01] * 100, risk_free_rate=0.0)
    assert result is None

def test_sharpe_formula():
    assert hasattr(sharpe_ratio, "formula")


# ── Sortino Ratio ─────────────────────────────────────────────────────────────

def test_sortino_ratio_basic(daily_returns):
    result = sortino_ratio(returns=daily_returns, risk_free_rate=0.05, periods_per_year=252)
    assert result is not None
    assert isinstance(result, float)


# ── Maximum Drawdown ──────────────────────────────────────────────────────────
# maximum_drawdown takes prices, not returns

def test_max_drawdown_known():
    prices = [100, 120, 150, 100, 80, 75]
    result = maximum_drawdown(prices=prices)
    assert result is not None
    # 150 → 75 is a 50% peak-to-trough drawdown
    assert abs(result) >= 0.40

def test_max_drawdown_no_drawdown():
    # Always rising — peak is last point, never a lower trough after
    prices = [100, 105, 110, 115, 120]
    result = maximum_drawdown(prices=prices)
    assert result == pytest.approx(0.0)

def test_max_drawdown_empty():
    result = maximum_drawdown(prices=[])
    assert result is None


# ── VaR ──────────────────────────────────────────────────────────────────────

def test_historical_var_basic(daily_returns):
    result = historical_var(returns=daily_returns, confidence=0.95)
    assert result is not None
    assert result > 0

def test_historical_var_99_gt_95(daily_returns):
    var95 = historical_var(returns=daily_returns, confidence=0.95)
    var99 = historical_var(returns=daily_returns, confidence=0.99)
    assert var99 is not None and var95 is not None
    assert var99 >= var95

def test_parametric_var_basic(daily_returns):
    result = parametric_var(returns=daily_returns, confidence=0.95)
    assert result is not None
    assert result > 0

def test_conditional_var_basic(daily_returns):
    result = conditional_var(returns=daily_returns, confidence=0.95)
    var = historical_var(returns=daily_returns, confidence=0.95)
    assert result is not None and var is not None
    assert result >= var

def test_historical_var_empty():
    assert historical_var(returns=[], confidence=0.95) is None


# ── Beta & Jensen's Alpha ─────────────────────────────────────────────────────
# beta takes stock_returns, market_returns

def test_beta_perfectly_correlated():
    market = [0.01, -0.02, 0.03, -0.01, 0.02]
    stock  = [0.01, -0.02, 0.03, -0.01, 0.02]
    result = beta(stock_returns=stock, market_returns=market)
    assert result == pytest.approx(1.0, rel=1e-3)

def test_beta_double_market():
    market = [0.01, -0.02, 0.03, -0.01, 0.02]
    stock  = [0.02, -0.04, 0.06, -0.02, 0.04]
    result = beta(stock_returns=stock, market_returns=market)
    assert result == pytest.approx(2.0, rel=1e-3)

def test_beta_mismatched_lengths():
    result = beta(stock_returns=[0.01, 0.02], market_returns=[0.01])
    assert result is None

def test_jensens_alpha_outperformance():
    result = jensens_alpha(
        portfolio_return=0.15, risk_free_rate=0.02,
        beta_val=1.0, market_return=0.10,
    )
    assert result == pytest.approx(0.05, rel=1e-3)


# ── Calmar Ratio ──────────────────────────────────────────────────────────────
# calmar_ratio takes a returns list + periods_per_year

def test_calmar_ratio_basic(daily_returns):
    result = calmar_ratio(returns=daily_returns, periods_per_year=252)
    # Should be a finite number or None
    assert result is None or isinstance(result, float)

def test_calmar_ratio_all_positive():
    returns = [0.01] * 50
    result = calmar_ratio(returns=returns, periods_per_year=252)
    # All positive → no drawdown → ratio undefined (None) or very high
    assert result is None or result > 0


# ── Omega Ratio ───────────────────────────────────────────────────────────────

def test_omega_ratio_with_mixed_returns():
    returns = [0.02, -0.01, 0.03, -0.005, 0.015, -0.008, 0.025]
    result = omega_ratio(returns=returns, threshold=0.0)
    assert result is not None
    assert result > 0

def test_omega_ratio_no_losses_returns_none():
    # All returns above threshold → no denominator → None
    result = omega_ratio(returns=[0.05, 0.04, 0.06, 0.03], threshold=0.0)
    assert result is None


# ── Tracking Error & Information Ratio ───────────────────────────────────────

def test_tracking_error_basic(daily_returns, benchmark_returns):
    result = tracking_error(portfolio_returns=daily_returns, benchmark_returns=benchmark_returns)
    assert result is not None
    assert result > 0

def test_information_ratio_basic(daily_returns, benchmark_returns):
    # information_ratio takes portfolio_returns and benchmark_returns only (no periods)
    result = information_ratio(
        portfolio_returns=daily_returns,
        benchmark_returns=benchmark_returns,
    )
    assert result is not None
    assert isinstance(result, float)


# ── Ulcer Index ───────────────────────────────────────────────────────────────
# ulcer_index takes prices, not returns

def test_ulcer_index_basic(daily_prices):
    result = ulcer_index(prices=daily_prices)
    assert result is not None
    assert result >= 0

def test_ulcer_index_zero_for_constant_growth():
    prices = [100 * (1.01 ** i) for i in range(50)]  # monotonically rising
    result = ulcer_index(prices=prices)
    assert result == pytest.approx(0.0, abs=1e-10)


# ── Capture Ratios ────────────────────────────────────────────────────────────

def test_upside_capture_basic(daily_returns, benchmark_returns):
    result = upside_capture_ratio(
        portfolio_returns=daily_returns,
        benchmark_returns=benchmark_returns,
    )
    assert result is not None

def test_downside_capture_basic(daily_returns, benchmark_returns):
    result = downside_capture_ratio(
        portfolio_returns=daily_returns,
        benchmark_returns=benchmark_returns,
    )
    assert result is not None
