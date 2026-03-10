"""Tests for liquidity and solvency ratios."""

import pytest
from fin_ratios import (
    current_ratio, quick_ratio, cash_ratio, operating_cash_flow_ratio,
    dso, dio, dpo, cash_conversion_cycle, defensive_interval_ratio,
    debt_to_equity, net_debt_to_equity, net_debt_to_ebitda,
    debt_to_assets, debt_to_capital, interest_coverage_ratio,
    ebitda_coverage_ratio, debt_service_coverage_ratio, equity_multiplier,
)


# ── Liquidity ─────────────────────────────────────────────────────────────────

def test_current_ratio_basic():
    assert current_ratio(current_assets=200, current_liabilities=100) == pytest.approx(2.0)

def test_current_ratio_zero_liabilities():
    assert current_ratio(current_assets=200, current_liabilities=0) is None

def test_quick_ratio_basic():
    # (Cash + ST investments + AR) / CL
    result = quick_ratio(cash=50, short_term_investments=20, accounts_receivable=30, current_liabilities=100)
    assert result == pytest.approx(1.0)

def test_cash_ratio_basic():
    # cash_ratio takes (cash, short_term_investments, current_liabilities)
    result = cash_ratio(cash=50, short_term_investments=20, current_liabilities=100)
    assert result == pytest.approx(0.70)

def test_ocf_ratio_basic():
    assert operating_cash_flow_ratio(operating_cash_flow=120, current_liabilities=100) == pytest.approx(1.20)

def test_dso_basic():
    # DSO = AR / Revenue × 365 = 50/1000 × 365 = 18.25
    result = dso(accounts_receivable=50, revenue=1000)
    assert result == pytest.approx(18.25)

def test_dio_basic():
    result = dio(inventory=100, cogs=1000)
    assert result == pytest.approx(36.5)

def test_dpo_basic():
    result = dpo(accounts_payable=60, cogs=1000)
    assert result == pytest.approx(21.9)

def test_ccc_basic():
    # CCC = DSO + DIO - DPO
    dso_val = dso(accounts_receivable=50, revenue=1000)
    dio_val = dio(inventory=100, cogs=1000)
    dpo_val = dpo(accounts_payable=60, cogs=1000)
    result = cash_conversion_cycle(dso_days=dso_val, dio_days=dio_val, dpo_days=dpo_val)
    assert result == pytest.approx(dso_val + dio_val - dpo_val)

def test_ccc_negative_amazon_style():
    # Negative CCC = suppliers fund operations
    result = cash_conversion_cycle(dso_days=5, dio_days=30, dpo_days=50)
    assert result == pytest.approx(-15)


# ── Solvency ──────────────────────────────────────────────────────────────────

def test_debt_to_equity_basic():
    assert debt_to_equity(total_debt=500, total_equity=1000) == pytest.approx(0.5)

def test_debt_to_equity_zero_equity():
    assert debt_to_equity(total_debt=500, total_equity=0) is None

def test_net_debt_to_equity_basic():
    # Net debt = total debt - cash = 500 - 100 = 400
    result = net_debt_to_equity(total_debt=500, cash=100, total_equity=1000)
    assert result == pytest.approx(0.40)

def test_net_debt_to_ebitda_basic():
    # Net debt = 400; EBITDA = 200; ratio = 2.0
    result = net_debt_to_ebitda(total_debt=500, cash=100, ebitda=200)
    assert result == pytest.approx(2.0)

def test_debt_to_assets_basic():
    assert debt_to_assets(total_debt=400, total_assets=1000) == pytest.approx(0.40)

def test_interest_coverage_basic():
    # ICR = EBIT / Interest = 500 / 100 = 5.0
    assert interest_coverage_ratio(ebit=500, interest_expense=100) == pytest.approx(5.0)

def test_interest_coverage_zero_interest():
    assert interest_coverage_ratio(ebit=500, interest_expense=0) is None

def test_ebitda_coverage_basic():
    assert ebitda_coverage_ratio(ebitda=600, interest_expense=100) == pytest.approx(6.0)

def test_dscr_basic():
    # DSCR = NOI / annual_debt_service
    assert debt_service_coverage_ratio(net_operating_income=600, annual_debt_service=200) == pytest.approx(3.0)

def test_equity_multiplier_basic():
    # EM = Assets / Equity = 1000 / 400 = 2.5
    assert equity_multiplier(total_assets=1000, total_equity=400) == pytest.approx(2.5)
