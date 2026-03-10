"""
Example 03: Composite Scoring Systems
=======================================
Demonstrates Piotroski F-Score, Altman Z-Score, Beneish M-Score,
Ohlson O-Score, and Greenblatt Magic Formula with realistic examples.

These are the rarest ratios — entire academic papers distilled into single scores.

Run: python examples/03_composite_scores.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fin_ratios import (
    piotroski_f_score, altman_z_score, beneish_m_score,
    magic_formula, ohlson_o_score,
)


def print_section(title: str):
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print("=" * 65)


# ── PIOTROSKI F-SCORE ─────────────────────────────────────────────────────────
print_section("PIOTROSKI F-SCORE (9 signals, 0-9 scale)")
print("  Reference: Piotroski (2000) Journal of Accounting Research")
print("  Showed F≥8 companies outperformed F≤2 by ~23% annually (1976-96)")

# Example A: Strong company (high F-Score expected)
print("\n[A] Strong Company — Improving on all fronts")
result_a = piotroski_f_score(
    # CURRENT YEAR
    current_net_income=8_500_000,
    current_total_assets=100_000_000,
    current_operating_cf=12_000_000,    # OCF > NI (quality earnings)
    current_long_term_debt=20_000_000,
    current_current_assets=35_000_000,
    current_current_liabilities=15_000_000,
    current_shares_outstanding=10_000_000,
    current_gross_profit=45_000_000,
    current_revenue=90_000_000,
    # PRIOR YEAR
    prior_net_income=5_000_000,
    prior_total_assets=95_000_000,
    prior_long_term_debt=25_000_000,     # Debt REDUCED
    prior_current_assets=28_000_000,
    prior_current_liabilities=14_000_000,
    prior_shares_outstanding=10_500_000, # Shares REDUCED (buybacks)
    prior_gross_profit=38_000_000,
    prior_revenue=80_000_000,
)
print(f"  F-Score: {result_a['score']}/9 → {result_a['interpretation']}")
print("  Signals:")
for signal, val in result_a["signals"].items():
    icon = "✓" if val else "✗"
    print(f"    {icon} {signal.replace('_', ' ').upper()}")

# Example B: Weak company (low F-Score expected)
print("\n[B] Weak Company — Deteriorating fundamentals")
result_b = piotroski_f_score(
    # CURRENT YEAR (worse in every dimension)
    current_net_income=-2_000_000,       # Losing money
    current_total_assets=100_000_000,
    current_operating_cf=-500_000,       # OCF negative
    current_long_term_debt=45_000_000,   # More debt
    current_current_assets=18_000_000,   # Less liquid
    current_current_liabilities=15_000_000,
    current_shares_outstanding=12_000_000,  # Diluted
    current_gross_profit=20_000_000,
    current_revenue=80_000_000,          # Revenue dropped
    # PRIOR YEAR
    prior_net_income=3_000_000,
    prior_total_assets=95_000_000,
    prior_long_term_debt=30_000_000,
    prior_current_assets=25_000_000,
    prior_current_liabilities=12_000_000,
    prior_shares_outstanding=10_000_000,
    prior_gross_profit=28_000_000,
    prior_revenue=90_000_000,
)
print(f"  F-Score: {result_b['score']}/9 → {result_b['interpretation']}")

# Example C: Microsoft-like consistency
print("\n[C] Microsoft-like — Consistent compounder")
result_c = piotroski_f_score(
    current_net_income=72_000_000_000,
    current_total_assets=411_000_000_000,
    current_operating_cf=87_000_000_000,
    current_long_term_debt=41_000_000_000,
    current_current_assets=184_000_000_000,
    current_current_liabilities=95_000_000_000,
    current_shares_outstanding=7_430_000_000,
    current_gross_profit=146_000_000_000,
    current_revenue=212_000_000_000,
    prior_net_income=61_000_000_000,
    prior_total_assets=380_000_000_000,
    prior_long_term_debt=47_000_000_000,
    prior_current_assets=170_000_000_000,
    prior_current_liabilities=88_000_000_000,
    prior_shares_outstanding=7_500_000_000,
    prior_gross_profit=135_000_000_000,
    prior_revenue=198_000_000_000,
)
print(f"  F-Score: {result_c['score']}/9 → {result_c['interpretation']}")


# ── ALTMAN Z-SCORE ────────────────────────────────────────────────────────────
print_section("ALTMAN Z-SCORE (Bankruptcy Prediction)")
print("  Reference: Altman (1968) Journal of Finance")
print("  Accuracy: ~72-80% for 2-year bankruptcy prediction")
print("  Safe > 2.99  |  Grey 1.81-2.99  |  Distress < 1.81")

companies = [
    ("Microsoft (Safe Zone)",    500e9,  200e9,  90e9,  3000e9, 210e9,  411e9,  212e9),
    ("Mid-quality Industrial",   80e6,   60e6,   12e6,  250e6,  90e6,   200e6,  180e6),
    ("Distressed Retailer",      -20e6,  -50e6,  -5e6,  80e6,   200e6,  250e6,  150e6),
    ("Borderline (Grey Zone)",   30e6,   15e6,   8e6,   120e6,  80e6,   180e6,  160e6),
]

print()
for name, wc, re, ebit, mc, tl, ta, rev in companies:
    z = altman_z_score(
        working_capital=wc,
        retained_earnings=re,
        ebit=ebit,
        market_cap=mc,
        total_liabilities=tl,
        total_assets=ta,
        revenue=rev,
    )
    if z:
        zone_icon = {"safe": "✅", "grey": "⚠️ ", "distress": "🚨"}
        icon = zone_icon.get(z["zone"], "?")
        print(f"  {icon} {name:<35} Z={z['z_score']:.2f} ({z['zone'].upper()})")
        print(f"       X1={z['x1_working_capital']:.3f}  X2={z['x2_retained_earnings']:.3f}  "
              f"X3={z['x3_ebit']:.3f}  X4={z['x4_market_vs_liabilities']:.3f}  "
              f"X5={z['x5_revenue']:.3f}")


# ── BENEISH M-SCORE ───────────────────────────────────────────────────────────
print_section("BENEISH M-SCORE (Earnings Manipulation Detection)")
print("  Reference: Beneish (1999) Financial Analysts Journal")
print("  Famous: Flagged Enron's manipulation BEFORE the collapse")
print("  Threshold: M > -2.22 = possible manipulation")

companies_b = [
    {
        "name": "Clean company (M < -2.22 = no manipulation)",
        "c_revenue": 100e6, "c_ar": 12e6, "c_gp": 40e6, "c_ta": 150e6,
        "c_dep": 8e6, "c_pp": 50e6, "c_sga": 15e6, "c_debt": 30e6,
        "c_ni": 8e6, "c_cfo": 11e6,
        "p_revenue": 90e6, "p_ar": 10e6, "p_gp": 35e6, "p_ta": 140e6,
        "p_dep": 7e6, "p_pp": 45e6, "p_sga": 14e6, "p_debt": 30e6,
    },
    {
        "name": "Suspicious (inflating receivables + declining GM + high accruals)",
        "c_revenue": 110e6, "c_ar": 25e6,  # AR grew much faster than revenue
        "c_gp": 38e6,       # Gross margin declining
        "c_ta": 155e6, "c_dep": 6e6,        # Depreciation slowing (boosting earnings)
        "c_pp": 55e6, "c_sga": 20e6,         # SGA growing fast
        "c_debt": 45e6,                       # More debt
        "c_ni": 12e6,       # NI high but...
        "c_cfo": 3e6,        # ...cash flow very low = high accruals (red flag!)
        "p_revenue": 90e6, "p_ar": 10e6, "p_gp": 38e6, "p_ta": 140e6,
        "p_dep": 8e6, "p_pp": 45e6, "p_sga": 14e6, "p_debt": 30e6,
    },
]

for data in companies_b:
    m = beneish_m_score(
        c_revenue=data["c_revenue"], c_accounts_receivable=data["c_ar"],
        c_gross_profit=data["c_gp"], c_total_assets=data["c_ta"],
        c_depreciation=data["c_dep"], c_pp_gross=data["c_pp"],
        c_sga_expense=data["c_sga"], c_total_debt=data["c_debt"],
        c_net_income=data["c_ni"], c_cash_from_ops=data["c_cfo"],
        p_revenue=data["p_revenue"], p_accounts_receivable=data["p_ar"],
        p_gross_profit=data["p_gp"], p_total_assets=data["p_ta"],
        p_depreciation=data["p_dep"], p_pp_gross=data["p_pp"],
        p_sga_expense=data["p_sga"], p_total_debt=data["p_debt"],
    )
    if m:
        icon = "⚠️  FLAGGED" if m["manipulation_likely"] else "✅ Clean"
        print(f"\n  {data['name']}")
        print(f"  M-Score: {m['m_score']:.2f}  →  {icon}")
        print(f"  Key variables: DSRI={m['variables']['dsri']:.2f}  GMI={m['variables']['gmi']:.2f}  "
              f"TATA={m['variables']['tata']:.3f}  AQI={m['variables']['aqi']:.2f}")


# ── GREENBLATT MAGIC FORMULA ──────────────────────────────────────────────────
print_section("GREENBLATT MAGIC FORMULA")
print("  Reference: Greenblatt (2005) The Little Book That Beats the Market")
print("  Strategy: Rank by ROIC + Earnings Yield, buy top 20-30 stocks")

candidates = [
    ("AutoZone",      2.8e9,  6e9,   1.5e9, 15e9 ),  # (EBIT, NWC, Net FA, EV)
    ("Meta",          50e9,  20e9,   5e9,  1200e9),
    ("Old Coal Co",   0.5e9,  2e9,   8e9,   8e9  ),
    ("Capital-light", 3e9,    0.5e9, 0.3e9, 40e9 ),
]

print(f"\n  {'Company':<20} {'ROIC':>8} {'Earn.Yield':>12} {'Notes'}")
print(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*20}")
for name, ebit, nwc, net_fa, ev in candidates:
    r = magic_formula(ebit=ebit, net_working_capital=nwc, net_fixed_assets=net_fa, enterprise_value=ev)
    roic_str = f"{r['roic_pct']:.1f}%" if r["roic_pct"] else "N/A"
    ey_str = f"{r['earnings_yield_pct']:.1f}%" if r["earnings_yield_pct"] else "N/A"
    print(f"  {name:<20} {roic_str:>8} {ey_str:>12}")


# ── OHLSON O-SCORE ────────────────────────────────────────────────────────────
print_section("OHLSON O-SCORE (Bankruptcy Probability)")
print("  Reference: Ohlson (1980) Journal of Accounting Research")
print("  Returns PROBABILITY of bankruptcy (0-1), not just a zone")

examples = [
    {
        "name": "Healthy company",
        "total_assets": 500e6, "total_liabilities": 200e6,
        "current_assets": 150e6, "current_liabilities": 80e6,
        "net_income": 40e6, "prior_net_income": 35e6,
        "operating_cf": 55e6, "working_capital": 70e6,
    },
    {
        "name": "Near-distress (losing money, high debt)",
        "total_assets": 200e6, "total_liabilities": 190e6,  # Nearly insolvent
        "current_assets": 40e6, "current_liabilities": 50e6,   # CL > CA
        "net_income": -15e6, "prior_net_income": -8e6,          # Consecutive losses
        "operating_cf": -5e6, "working_capital": -10e6,
    },
]

for ex in examples:
    o = ohlson_o_score(
        total_assets=ex["total_assets"],
        total_liabilities=ex["total_liabilities"],
        current_assets=ex["current_assets"],
        current_liabilities=ex["current_liabilities"],
        net_income=ex["net_income"],
        prior_net_income=ex["prior_net_income"],
        operating_cash_flow=ex["operating_cf"],
        working_capital=ex["working_capital"],
    )
    if o:
        icon = "🚨" if o["high_risk"] else "✅"
        print(f"\n  {icon} {ex['name']}")
        print(f"     Bankruptcy probability: {o['bankruptcy_probability_pct']:.1f}%")
        print(f"     O-Score: {o['o_score']:.2f}")

print("\n" + "=" * 65)
print("All composite scores demonstrated successfully!")
print("=" * 65)
