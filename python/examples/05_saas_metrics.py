"""
Example 05: SaaS Metrics
=========================
Demonstrates Rule of 40, NRR, Magic Number, LTV/CAC, Burn Multiple,
and all other SaaS-specific ratios with realistic examples.

Run: python examples/05_saas_metrics.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fin_ratios.ratios.sector.saas import (
    rule_of_40, magic_number, net_revenue_retention,
    gross_revenue_retention, customer_acquisition_cost,
    customer_lifetime_value, ltv_cac_ratio, cac_payback_period,
    burn_multiple, saas_quick_ratio, arr_per_fte,
)


print("=" * 65)
print("SaaS METRICS — fin-ratios examples")
print("=" * 65)

# ── Three companies for comparison ────────────────────────────────────────────
companies = {
    "Snowflake-like": {
        "arr": 3_200_000_000,
        "rev_growth_pct": 33,
        "fcf_margin_pct": 26,
        "nrr": 1.27,            # 127% NRR
        "expansion": 600_000_000,
        "churn": 80_000_000,
        "contraction": 10_000_000,
        "beg_arr": 2_700_000_000,
        "q_rev_curr": 868_000_000,
        "q_rev_prior": 774_000_000,
        "q_sm": 380_000_000,
        "new_mrr": 50_000_000,
        "expansion_mrr": 30_000_000,
        "churned_mrr": 8_000_000,
        "contraction_mrr": 2_000_000,
        "cac": 25_000,
        "avg_mrr_per_cust": 12_000,
        "gross_margin": 0.68,
        "monthly_churn": 0.008,
        "burn": 0,               # Profitable
        "net_new_arr_monthly": 40_000_000,
        "ftes": 5_800,
    },
    "Good-not-great SaaS": {
        "arr": 200_000_000,
        "rev_growth_pct": 30,
        "fcf_margin_pct": 5,    # R40 = 35 (just below threshold)
        "nrr": 1.10,
        "expansion": 28_000_000,
        "churn": 14_000_000,
        "contraction": 4_000_000,
        "beg_arr": 160_000_000,
        "q_rev_curr": 52_000_000,
        "q_rev_prior": 40_000_000,
        "q_sm": 30_000_000,
        "new_mrr": 2_500_000,
        "expansion_mrr": 800_000,
        "churned_mrr": 900_000,
        "contraction_mrr": 200_000,
        "cac": 8_000,
        "avg_mrr_per_cust": 2_500,
        "gross_margin": 0.72,
        "monthly_churn": 0.015,
        "burn": 1_500_000,
        "net_new_arr_monthly": 3_500_000,
        "ftes": 350,
    },
    "Struggling SaaS": {
        "arr": 25_000_000,
        "rev_growth_pct": 15,
        "fcf_margin_pct": -25,  # Still burning cash
        "nrr": 0.88,             # Net revenue retention < 100% = leaky bucket
        "expansion": 1_500_000,
        "churn": 3_500_000,
        "contraction": 1_000_000,
        "beg_arr": 27_000_000,
        "q_rev_curr": 6_500_000,
        "q_rev_prior": 5_700_000,
        "q_sm": 4_000_000,
        "new_mrr": 200_000,
        "expansion_mrr": 80_000,
        "churned_mrr": 300_000,
        "contraction_mrr": 100_000,
        "cac": 12_000,
        "avg_mrr_per_cust": 1_800,
        "gross_margin": 0.60,
        "monthly_churn": 0.045,  # High churn
        "burn": 500_000,
        "net_new_arr_monthly": 200_000,
        "ftes": 80,
    },
}

# ── Print comparison ──────────────────────────────────────────────────────────
print(f"\n{'Metric':<30} {'Snowflake-like':>18} {'Good-not-great':>16} {'Struggling':>14}")
print("-" * 80)

for name, d in companies.items():
    # Compute all metrics
    d["_r40"] = rule_of_40(d["rev_growth_pct"], d["fcf_margin_pct"])
    d["_nrr"] = net_revenue_retention(d["beg_arr"], d["expansion"], d["churn"], d["contraction"])
    d["_grr"] = gross_revenue_retention(d["beg_arr"], d["churn"], d["contraction"])
    d["_magic"] = magic_number(d["q_rev_curr"], d["q_rev_prior"], d["q_sm"])
    d["_ltv"] = customer_lifetime_value(d["avg_mrr_per_cust"], d["gross_margin"], d["monthly_churn"])
    d["_cac"] = d["cac"]
    d["_ltv_cac"] = ltv_cac_ratio(d["_ltv"] or 0, d["_cac"])
    d["_payback"] = cac_payback_period(d["_cac"], d["avg_mrr_per_cust"], d["gross_margin"])
    d["_saas_qr"] = saas_quick_ratio(d["new_mrr"], d["expansion_mrr"], d["churned_mrr"], d["contraction_mrr"])
    d["_arr_fte"] = arr_per_fte(d["arr"], d["ftes"])

    if d.get("burn") and d.get("burn") > 0:
        d["_burn_mult"] = burn_multiple(d["burn"], d["net_new_arr_monthly"])
    else:
        d["_burn_mult"] = 0.0  # Profitable

rows = [
    ("Rule of 40", "_r40", lambda v: f"{v:.0f}%  {'✅' if v >= 40 else '⚠️'}"),
    ("NRR", "_nrr", lambda v: f"{v*100:.0f}%  {'✅' if v >= 1.10 else ('⚠️' if v >= 1.0 else '🚨')}"),
    ("GRR", "_grr", lambda v: f"{v*100:.0f}%"),
    ("Magic Number", "_magic", lambda v: f"{v:.2f}  {'✅' if v >= 0.75 else '⚠️'}"),
    ("LTV/CAC", "_ltv_cac", lambda v: f"{v:.1f}x  {'✅' if v >= 3 else ('⚠️' if v >= 1 else '🚨')}"),
    ("CAC Payback (months)", "_payback", lambda v: f"{v:.0f} mo  {'✅' if v <= 12 else '⚠️'}"),
    ("SaaS Quick Ratio", "_saas_qr", lambda v: f"{v:.1f}  {'✅' if v >= 4 else ('⚠️' if v >= 2 else '🚨')}"),
    ("Burn Multiple", "_burn_mult", lambda v: f"{v:.2f}x  {'✅' if v <= 1 else ('⚠️' if v <= 2 else '🚨')}"),
    ("ARR/FTE ($K)", "_arr_fte", lambda v: f"${v/1e3:.0f}K  {'✅' if v >= 200e3 else '⚠️'}"),
]

for label, key, fmt in rows:
    vals = []
    for d in companies.values():
        v = d.get(key)
        vals.append(fmt(v) if v is not None else "N/A")
    print(f"  {label:<30} {vals[0]:>18} {vals[1]:>16} {vals[2]:>14}")


# ── Deep dive on NRR ─────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("Deep Dive: Net Revenue Retention")
print("=" * 65)
print("\nNRR shows what happens to $100 of ARR from existing customers:")

for name, d in companies.items():
    nrr = d["_nrr"] or 0
    print(f"\n  {name}:")
    print(f"    Beginning ARR:       ${d['beg_arr']/1e6:.0f}M")
    print(f"    + Expansion:        +${d['expansion']/1e6:.0f}M  (upsells, seat expansion)")
    print(f"    - Churn:            -${d['churn']/1e6:.0f}M  (cancelled contracts)")
    print(f"    - Contraction:      -${d['contraction']/1e6:.0f}M  (downgraded plans)")
    print(f"    = Ending ARR:        ${(d['beg_arr'] + d['expansion'] - d['churn'] - d['contraction'])/1e6:.0f}M")
    print(f"    NRR: {nrr*100:.0f}%  ({'GROWING from existing base' if nrr > 1 else 'SHRINKING even without churn'})")


# ── Cohort LTV analysis ───────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("LTV / CAC Analysis at Different Churn Rates")
print("=" * 65)
print("\nImpact of monthly churn rate on LTV (assuming $500/mo ARPU, 70% GM, $5,000 CAC):")
print(f"\n  {'Monthly Churn':>15} {'Avg Lifetime (mo)':>20} {'LTV':>12} {'LTV/CAC':>10} {'Payback':>10}")
print(f"  {'-'*15} {'-'*20} {'-'*12} {'-'*10} {'-'*10}")
for churn_pct in [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]:
    churn = churn_pct / 100
    ltv = customer_lifetime_value(500, 0.70, churn)
    if ltv:
        ltv_cac = ltv_cac_ratio(ltv, 5000) or 0
        payback = cac_payback_period(5000, 500, 0.70) or 0
        avg_life = 1 / churn
        print(f"  {churn_pct:>14.1f}%  {avg_life:>18.0f} mo  ${ltv:>10,.0f}  {ltv_cac:>9.1f}x  {payback:>8.0f} mo")
