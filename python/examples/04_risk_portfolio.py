"""
Example 04: Risk and Portfolio Ratios
======================================
Demonstrates Sharpe, Sortino, Calmar, Omega, VaR, CVaR, Beta,
Ulcer Index, Capture Ratios, and more.

Run: python examples/04_risk_portfolio.py
"""
import sys
import math
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fin_ratios import (
    beta, jensens_alpha, sharpe_ratio, sortino_ratio,
    treynor_ratio, calmar_ratio, information_ratio, omega_ratio,
    maximum_drawdown, tracking_error,
    historical_var, parametric_var, conditional_var,
    ulcer_index, upside_capture_ratio, downside_capture_ratio,
)

random.seed(42)

def generate_returns(
    annual_return: float,
    annual_vol: float,
    n: int = 252,
    seed: int = 42
) -> list[float]:
    """Generate synthetic daily returns with given annual stats."""
    random.seed(seed)
    daily_mean = annual_return / 252
    daily_vol = annual_vol / math.sqrt(252)
    return [
        random.gauss(daily_mean, daily_vol)
        for _ in range(n)
    ]


print("=" * 65)
print("RISK & PORTFOLIO RATIOS — fin-ratios examples")
print("=" * 65)

RISK_FREE_RATE = 0.05  # 5% risk-free rate

# ── Generate return series for comparison ────────────────────────────────────
market_returns = generate_returns(0.12, 0.18, seed=1)    # Market: 12% return, 18% vol
fund_a_returns = generate_returns(0.18, 0.20, seed=2)    # High return, high vol
fund_b_returns = generate_returns(0.14, 0.12, seed=3)    # Moderate return, low vol
fund_c_returns = generate_returns(0.08, 0.25, seed=4)    # Low return, high vol (bad)
fund_d_returns = generate_returns(0.22, 0.30, seed=5)    # High return, very high vol

print("\n[1] Comparing 4 Funds on Multiple Risk-Adjusted Metrics")
print("-" * 65)

funds = {
    "Fund A (aggressive)":  fund_a_returns,
    "Fund B (quality)":     fund_b_returns,
    "Fund C (poor Sharpe)": fund_c_returns,
    "Fund D (volatile)":    fund_d_returns,
}

print(f"\n  {'Fund':<25} {'Sharpe':>8} {'Sortino':>8} {'Calmar':>8} {'Omega':>8} {'MaxDD':>8}")
print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for name, returns in funds.items():
    sh = sharpe_ratio(returns, RISK_FREE_RATE)
    so = sortino_ratio(returns, RISK_FREE_RATE)
    cal = calmar_ratio(returns)
    om = omega_ratio(returns, threshold=RISK_FREE_RATE / 252)

    prices = [1.0]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    mdd = maximum_drawdown(prices)

    print(f"  {name:<25} "
          f"{sh:>8.2f} " if sh else f"  {'N/A':>8} "
          f"{so:>8.2f} " if so else f"{'N/A':>8} "
          f"{cal:>8.2f} " if cal else f"{'N/A':>8} "
          f"{om:>8.2f} " if om else f"{'N/A':>8} "
          f"{mdd*100:>7.1f}%" if mdd else f"{'N/A':>8}")

# Clean print
print()
for name, returns in funds.items():
    sh = sharpe_ratio(returns, RISK_FREE_RATE) or 0
    so = sortino_ratio(returns, RISK_FREE_RATE) or 0
    cal = calmar_ratio(returns) or 0
    om = omega_ratio(returns, threshold=RISK_FREE_RATE / 252) or 0
    prices = [1.0]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    mdd = (maximum_drawdown(prices) or 0) * 100
    print(f"  {name:<25}  Sharpe={sh:5.2f}  Sortino={so:5.2f}  Calmar={cal:5.2f}  Omega={om:5.2f}  MaxDD={mdd:5.1f}%")


# ── Beta and Alpha ────────────────────────────────────────────────────────────
print("\n[2] Beta and Jensen's Alpha")
print("-" * 65)

for name, returns in funds.items():
    b = beta(returns, market_returns)
    if b is None:
        continue
    # Compute actual annualized return
    total_return = 1.0
    for r in returns:
        total_return *= (1 + r)
    ann_return = (total_return ** (252 / len(returns))) - 1

    # Market annualized
    mkt_total = 1.0
    for r in market_returns:
        mkt_total *= (1 + r)
    mkt_return = (mkt_total ** (252 / len(market_returns))) - 1

    alpha = jensens_alpha(ann_return, RISK_FREE_RATE, b, mkt_return)
    treynor = treynor_ratio(ann_return, RISK_FREE_RATE, b)
    print(f"  {name:<25}  β={b:5.2f}  Jensen α={alpha*100:+5.1f}%  Treynor={treynor*100:5.1f}%")


# ── Value at Risk ─────────────────────────────────────────────────────────────
print("\n[3] Value at Risk (3 Methods) — Fund A at 95% confidence")
print("-" * 65)

fund_for_var = fund_a_returns
hvar = historical_var(fund_for_var, 0.95)
pvar = parametric_var(fund_for_var, 0.95)
cvar = conditional_var(fund_for_var, 0.95)

print(f"  Portfolio: 252 daily returns, 95% confidence")
print(f"  Historical VaR:    {hvar*100:.2f}%  (don't lose more on 95% of days)")
print(f"  Parametric VaR:    {pvar*100:.2f}%  (assumes normal distribution)")
print(f"  CVaR (Expected Shortfall): {cvar*100:.2f}%  (avg loss in WORST 5% of days)")
print(f"  CVaR > VaR because CVaR = avg of worst outcomes, not just the threshold")

print("\n  VaR at different confidence levels (Historical):")
for conf in [0.90, 0.95, 0.99]:
    v = historical_var(fund_for_var, conf)
    print(f"    {conf*100:.0f}% VaR: {v*100:.2f}%")


# ── Ulcer Index ───────────────────────────────────────────────────────────────
print("\n[4] Ulcer Index — Measures Drawdown Stress")
print("-" * 65)
print("  Lower Ulcer Index = smoother ride = less 'stress' for investor")

for name, returns in funds.items():
    prices = [1.0]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    ui = ulcer_index(prices)
    mdd = maximum_drawdown(prices)
    if ui and mdd:
        print(f"  {name:<25}  UI={ui:5.2f}  MaxDD={mdd*100:5.1f}%")


# ── Information Ratio ─────────────────────────────────────────────────────────
print("\n[5] Information Ratio vs S&P 500 Benchmark")
print("-" * 65)
print("  IR > 0.5 = Good; > 1.0 = Exceptional active management skill")

benchmark = market_returns
for name, returns in funds.items():
    ir = information_ratio(returns, benchmark)
    te = tracking_error(returns, benchmark)
    if ir and te:
        print(f"  {name:<25}  IR={ir:6.3f}  Tracking Error={te*100:.1f}%/yr")


# ── Upside/Downside Capture ───────────────────────────────────────────────────
print("\n[6] Upside / Downside Capture Ratios vs Market")
print("-" * 65)
print("  Ideal: High upside capture (>100%) + Low downside capture (<100%)")

for name, returns in funds.items():
    up = upside_capture_ratio(returns, market_returns)
    down = downside_capture_ratio(returns, market_returns)
    if up and down:
        ideal = "✓ Good" if up > 100 and down < 100 else ("✗ Poor" if up < 100 and down > 100 else "~ Mixed")
        print(f"  {name:<25}  Upside={up:6.1f}%  Downside={down:6.1f}%  {ideal}")


# ── Real-world interpretation ─────────────────────────────────────────────────
print("\n[7] Real-World Benchmarks")
print("-" * 65)
benchmarks = [
    ("S&P 500 (historical avg)", 0.50),
    ("Good hedge fund",          1.00),
    ("Excellent hedge fund",     1.50),
    ("Exceptional (rare)",       2.00),
]
print("  Sharpe Ratio Benchmarks:")
for label, value in benchmarks:
    print(f"    {label:<35} ≈ {value:.2f}")

print("\n  Our funds:")
for name, returns in funds.items():
    sh = sharpe_ratio(returns, RISK_FREE_RATE)
    if sh:
        category = (
            "Exceptional" if sh > 2.0 else
            "Excellent" if sh > 1.5 else
            "Good" if sh > 1.0 else
            "Acceptable" if sh > 0.5 else
            "Poor"
        )
        print(f"    {name:<25}  Sharpe={sh:.2f}  → {category}")
