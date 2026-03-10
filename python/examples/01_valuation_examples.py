"""
Example 01: Valuation Ratios
==============================
Demonstrates all valuation ratios with real-world style data.
No external dependencies required.

Run: python examples/01_valuation_examples.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fin_ratios import (
    pe, forward_pe, peg, pb, ps, p_fcf,
    enterprise_value, ev_ebitda, ev_ebit, ev_revenue, ev_fcf,
    tobin_q, graham_number, graham_intrinsic_value,
    dcf_2_stage, gordon_growth_model, reverse_dcf,
)

print("=" * 65)
print("VALUATION RATIOS — fin-ratios examples")
print("=" * 65)

# ── Example 1: Apple-like tech company ───────────────────────────────────────
print("\n[1] Apple-like Tech Company")
print("-" * 40)

aapl_market_cap = 3_000_000_000_000    # $3T
aapl_net_income = 100_000_000_000      # $100B
aapl_revenue = 390_000_000_000         # $390B
aapl_total_equity = 74_000_000_000     # $74B  (book value)
aapl_total_debt = 110_000_000_000
aapl_cash = 62_000_000_000
aapl_ebitda = 130_000_000_000
aapl_ebit = 120_000_000_000
aapl_ocf = 110_000_000_000
aapl_capex = 11_000_000_000
aapl_eps = 6.43
aapl_bvps = 4.50                        # Low due to buybacks
aapl_total_assets = 352_000_000_000

ev = enterprise_value(
    market_cap=aapl_market_cap,
    total_debt=aapl_total_debt,
    cash=aapl_cash,
)
print(f"  P/E Ratio:          {pe(aapl_market_cap, aapl_net_income):.1f}x")
print(f"  P/B Ratio:          {pb(aapl_market_cap, aapl_total_equity):.1f}x  (high due to buybacks reducing book value)")
print(f"  P/S Ratio:          {ps(aapl_market_cap, aapl_revenue):.1f}x")
print(f"  P/FCF:              {p_fcf(aapl_market_cap, aapl_ocf, aapl_capex):.1f}x")
print(f"  Enterprise Value:   ${ev/1e12:.2f}T")
print(f"  EV/EBITDA:          {ev_ebitda(ev, aapl_ebitda):.1f}x")
print(f"  EV/EBIT:            {ev_ebit(ev, aapl_ebit):.1f}x")
print(f"  EV/Revenue:         {ev_revenue(ev, aapl_revenue):.1f}x")
print(f"  Tobin's Q:          {tobin_q(aapl_market_cap, aapl_total_debt, aapl_total_assets):.2f}")
print(f"  Graham Number:      ${graham_number(aapl_eps, aapl_bvps):.2f}  (actual price ~$190 = well above Graham)")

# ── Example 2: Value stock (bank-like) ───────────────────────────────────────
print("\n[2] Value Stock (Bank-like)")
print("-" * 40)

bank_market_cap = 50_000_000_000
bank_net_income = 7_000_000_000
bank_revenue = 25_000_000_000
bank_equity = 60_000_000_000
bank_eps = 9.20
bank_bvps = 78.50
bank_growth_pct = 8.0
bank_aaa_yield = 5.5   # Current ~5.5%

print(f"  P/E:                {pe(bank_market_cap, bank_net_income):.1f}x")
print(f"  P/B:                {pb(bank_market_cap, bank_equity):.2f}x  (below 1x = trading below book)")
print(f"  PEG:                {peg(pe(bank_market_cap, bank_net_income), bank_growth_pct):.2f}  (< 1 = cheap vs growth)")
print(f"  Graham Number:      ${graham_number(bank_eps, bank_bvps):.2f}")
print(f"  Graham Intrinsic:   ${graham_intrinsic_value(bank_eps, bank_growth_pct, bank_aaa_yield):.2f}")

# ── Example 3: DCF Valuation ──────────────────────────────────────────────────
print("\n[3] 2-Stage DCF Valuation (high-growth SaaS)")
print("-" * 40)

dcf_result = dcf_2_stage(
    base_fcf=5_000_000_000,       # $5B current FCF
    growth_rate=0.20,              # 20% growth for 10 years
    years=10,
    terminal_growth_rate=0.03,     # 3% forever after
    wacc=0.10,                     # 10% WACC
    net_debt=-10_000_000_000,      # Net cash of $10B
    shares_outstanding=1_000_000_000,
)

if dcf_result:
    print(f"  PV of Stage 1 (10yr): ${dcf_result['pv_stage1']/1e9:.1f}B")
    print(f"  PV of Terminal Value: ${dcf_result['pv_terminal_value']/1e9:.1f}B")
    print(f"  Terminal Value (raw): ${dcf_result['terminal_value']/1e9:.1f}B")
    print(f"  Intrinsic Equity Val: ${dcf_result['intrinsic_value']/1e9:.1f}B")
    print(f"  Intrinsic Per Share:  ${dcf_result['intrinsic_value_per_share']:.2f}")
    print(f"  % from Terminal Val:  {dcf_result['pct_from_terminal']*100:.0f}%  (how much depends on terminal assumptions)")

# ── Example 4: Reverse DCF ────────────────────────────────────────────────────
print("\n[4] Reverse DCF — What does the market expect?")
print("-" * 40)

# Scenario: A stock trading at high valuation
rev_result = reverse_dcf(
    market_cap=500_000_000_000,    # $500B market cap
    base_fcf=10_000_000_000,       # $10B FCF
    years=10,
    terminal_growth_rate=0.03,
    wacc=0.10,
    net_debt=5_000_000_000,
)

if rev_result:
    g = rev_result["implied_growth_rate"]
    print(f"  {rev_result['interpretation']}")
    if g > 0.25:
        print(f"  ⚠ {g*100:.1f}% growth is extremely aggressive — priced for perfection")
    elif g > 0.15:
        print(f"  Ambitious but achievable for strong franchises")
    else:
        print(f"  Conservative — meaningful margin of safety")

# ── Example 5: Gordon Growth DDM ─────────────────────────────────────────────
print("\n[5] Gordon Growth Model (Dividend stock — Coca-Cola style)")
print("-" * 40)

ko_dividend = 1.94          # Annual dividend
ko_growth_rate = 0.05       # 5% dividend growth
ko_required_return = 0.085  # 8.5% required return

intrinsic = gordon_growth_model(ko_dividend, ko_required_return, ko_growth_rate)
print(f"  Next Dividend:      ${ko_dividend}")
print(f"  Growth Rate:        {ko_growth_rate*100}%")
print(f"  Required Return:    {ko_required_return*100}%")
print(f"  Intrinsic Value:    ${intrinsic:.2f}")

# ── Example 6: Formula transparency ──────────────────────────────────────────
print("\n[6] Formula Transparency")
print("-" * 40)
print(f"  pe.formula:         '{pe.formula}'")
print(f"  ev_ebitda.formula:  '{ev_ebitda.formula}'")
print(f"  dcf_2_stage.formula: '{dcf_2_stage.formula}'")
print(f"  graham_number.description: '{graham_number.description}'")
