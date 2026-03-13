"""
Example 02: Scoring Models Walkthrough
=======================================
Demonstrates all 8 institutional-grade scoring models with realistic data.
No network calls — all data is provided inline.

Run:
    python examples/02_scoring_walkthrough.py
"""

from fin_ratios.utils.moat_score import moat_score_from_series
from fin_ratios.utils.capital_allocation import capital_allocation_score_from_series
from fin_ratios.utils.earnings_quality import earnings_quality_score_from_series
from fin_ratios.utils.quality_score import quality_score_from_series
from fin_ratios.utils.valuation_score import valuation_attractiveness_score
from fin_ratios.utils.management_score import management_quality_score_from_series
from fin_ratios.utils.dividend_score import dividend_safety_score_from_series
from fin_ratios.utils.investment_score import investment_score_from_series

# ---------------------------------------------------------------------------
# Simulated 7-year annual data for a hypothetical large-cap technology company
# Oldest year first — required by all *_from_series functions
# ---------------------------------------------------------------------------
annual_data = [
    {  # Year 1
        "revenue": 260e9, "gross_profit": 100e9, "ebit": 62e9, "ebitda": 74e9,
        "net_income": 52e9, "operating_cash_flow": 68e9, "capex": 8e9,
        "total_assets": 310e9, "total_equity": 60e9, "total_debt": 90e9,
        "cash": 32e9, "depreciation": 12e9, "income_tax_expense": 12e9, "ebt": 64e9,
        "shares_outstanding": 16e9, "dividends_paid": 4e9, "buybacks": 12e9,
        "accounts_receivable": 22e9, "current_assets": 105e9, "current_liabilities": 72e9,
    },
    {  # Year 2
        "revenue": 275e9, "gross_profit": 107e9, "ebit": 67e9, "ebitda": 80e9,
        "net_income": 56e9, "operating_cash_flow": 73e9, "capex": 8.5e9,
        "total_assets": 305e9, "total_equity": 62e9, "total_debt": 88e9,
        "cash": 30e9, "depreciation": 13e9, "income_tax_expense": 13e9, "ebt": 69e9,
        "shares_outstanding": 15.7e9, "dividends_paid": 4.2e9, "buybacks": 14e9,
        "accounts_receivable": 23e9, "current_assets": 108e9, "current_liabilities": 74e9,
    },
    {  # Year 3
        "revenue": 290e9, "gross_profit": 114e9, "ebit": 72e9, "ebitda": 86e9,
        "net_income": 60e9, "operating_cash_flow": 78e9, "capex": 9e9,
        "total_assets": 302e9, "total_equity": 65e9, "total_debt": 86e9,
        "cash": 29e9, "depreciation": 14e9, "income_tax_expense": 14e9, "ebt": 74e9,
        "shares_outstanding": 15.5e9, "dividends_paid": 4.5e9, "buybacks": 15e9,
        "accounts_receivable": 24e9, "current_assets": 110e9, "current_liabilities": 75e9,
    },
    {  # Year 4
        "revenue": 300e9, "gross_profit": 120e9, "ebit": 75e9, "ebitda": 90e9,
        "net_income": 63e9, "operating_cash_flow": 82e9, "capex": 9.5e9,
        "total_assets": 300e9, "total_equity": 64e9, "total_debt": 84e9,
        "cash": 28e9, "depreciation": 15e9, "income_tax_expense": 15e9, "ebt": 78e9,
        "shares_outstanding": 15.3e9, "dividends_paid": 4.8e9, "buybacks": 16e9,
        "accounts_receivable": 25e9, "current_assets": 112e9, "current_liabilities": 76e9,
    },
    {  # Year 5
        "revenue": 312e9, "gross_profit": 126e9, "ebit": 79e9, "ebitda": 95e9,
        "net_income": 66e9, "operating_cash_flow": 86e9, "capex": 10e9,
        "total_assets": 298e9, "total_equity": 63e9, "total_debt": 82e9,
        "cash": 27e9, "depreciation": 16e9, "income_tax_expense": 16e9, "ebt": 82e9,
        "shares_outstanding": 15.1e9, "dividends_paid": 5.0e9, "buybacks": 17e9,
        "accounts_receivable": 26e9, "current_assets": 113e9, "current_liabilities": 77e9,
    },
    {  # Year 6
        "revenue": 325e9, "gross_profit": 132e9, "ebit": 83e9, "ebitda": 100e9,
        "net_income": 70e9, "operating_cash_flow": 90e9, "capex": 10.5e9,
        "total_assets": 295e9, "total_equity": 62e9, "total_debt": 80e9,
        "cash": 26e9, "depreciation": 17e9, "income_tax_expense": 17e9, "ebt": 87e9,
        "shares_outstanding": 15.0e9, "dividends_paid": 5.3e9, "buybacks": 18e9,
        "accounts_receivable": 27e9, "current_assets": 115e9, "current_liabilities": 78e9,
    },
    {  # Year 7 (most recent)
        "revenue": 340e9, "gross_profit": 138e9, "ebit": 87e9, "ebitda": 105e9,
        "net_income": 73e9, "operating_cash_flow": 94e9, "capex": 11e9,
        "total_assets": 292e9, "total_equity": 61e9, "total_debt": 78e9,
        "cash": 25e9, "depreciation": 18e9, "income_tax_expense": 18e9, "ebt": 91e9,
        "shares_outstanding": 14.8e9, "dividends_paid": 5.5e9, "buybacks": 20e9,
        "accounts_receivable": 28e9, "current_assets": 116e9, "current_liabilities": 79e9,
    },
]

WACC = 0.09
DIVIDER = "=" * 60


def print_section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# 1. Economic Moat Score
# ---------------------------------------------------------------------------
print_section("1. Economic Moat Score")
moat = moat_score_from_series(annual_data, wacc=WACC)
print(f"  Score : {moat.score}/100")
print(f"  Width : {moat.width}")
print(f"  Reason: {moat.interpretation}")

# ---------------------------------------------------------------------------
# 2. Capital Allocation Score
# ---------------------------------------------------------------------------
print_section("2. Capital Allocation Score")
ca = capital_allocation_score_from_series(annual_data, wacc=WACC)
print(f"  Score : {ca.score}/100")
print(f"  Rating: {ca.rating}")

# ---------------------------------------------------------------------------
# 3. Earnings Quality Score
# ---------------------------------------------------------------------------
print_section("3. Earnings Quality Score")
eq = earnings_quality_score_from_series(annual_data)
print(f"  Score : {eq.score}/100")
print(f"  Rating: {eq.rating}")

# ---------------------------------------------------------------------------
# 4. Quality Factor Score (composite: EQ 35% + Moat 35% + CA 30%)
# ---------------------------------------------------------------------------
print_section("4. Quality Factor Score")
qs = quality_score_from_series(annual_data, wacc=WACC)
print(f"  Score : {qs.score}/100")
print(f"  Grade : {qs.grade}")
print(f"  Detail: EQ={qs.components.earnings_quality}  Moat={qs.components.moat}  CA={qs.components.capital_allocation}")

# ---------------------------------------------------------------------------
# 5. Valuation Attractiveness Score  (point-in-time — not time-series)
# ---------------------------------------------------------------------------
print_section("5. Valuation Attractiveness Score")
val = valuation_attractiveness_score(
    pe_ratio=22.0,
    ev_ebitda=14.0,
    p_fcf=18.0,
    pb_ratio=3.5,
    dcf_upside_pct=20.0,
    risk_free_rate=0.045,
)
print(f"  Score : {val.score}/100")
print(f"  Rating: {val.rating}")

# ---------------------------------------------------------------------------
# 6. Management Quality Score
# ---------------------------------------------------------------------------
print_section("6. Management Quality Score")
mgmt = management_quality_score_from_series(annual_data, hurdle_rate=WACC)
print(f"  Score : {mgmt.score}/100")
print(f"  Rating: {mgmt.rating}")

# ---------------------------------------------------------------------------
# 7. Dividend Safety Score
# ---------------------------------------------------------------------------
print_section("7. Dividend Safety Score")
div = dividend_safety_score_from_series(annual_data)
print(f"  Score        : {div.score}/100")
print(f"  Rating       : {div.rating}")
print(f"  Payer        : {div.is_dividend_payer}")

# ---------------------------------------------------------------------------
# 8. Investment Score  (grand synthesis)
# ---------------------------------------------------------------------------
print_section("8. Investment Score — Grand Synthesis")
inv = investment_score_from_series(
    annual_data,
    wacc=WACC,
    pe_ratio=22.0,
    ev_ebitda=14.0,
    p_fcf=18.0,
    pb_ratio=3.5,
    dcf_upside_pct=20.0,
)
print(f"  Score     : {inv.score}/100")
print(f"  Grade     : {inv.grade}")
print(f"  Conviction: {inv.conviction}")
print(f"  Summary   : {inv.interpretation}")

print(f"\n{DIVIDER}")
print("  All scoring models demonstrated successfully!")
print(DIVIDER)
