"""Tests for profitability ratios."""

import pytest
from fin_ratios import (
    gross_margin, operating_margin, ebitda_margin, net_profit_margin,
    roe, roa, roic, roce, rote,
    nopat, invested_capital,
    revenue_per_employee, profit_per_employee,
)
from fin_ratios.ratios.profitability import du_pont_3


def test_gross_margin_basic():
    assert gross_margin(gross_profit=600, revenue=1000) == pytest.approx(0.60)

def test_gross_margin_zero_revenue():
    assert gross_margin(gross_profit=100, revenue=0) is None

def test_operating_margin_basic():
    assert operating_margin(ebit=150, revenue=1000) == pytest.approx(0.15)

def test_net_profit_margin_basic():
    assert net_profit_margin(net_income=100, revenue=1000) == pytest.approx(0.10)

def test_ebitda_margin_basic():
    assert ebitda_margin(ebitda=200, revenue=1000) == pytest.approx(0.20)

def test_roe_basic():
    assert roe(net_income=120, avg_total_equity=600) == pytest.approx(0.20)

def test_roe_zero_equity():
    assert roe(net_income=100, avg_total_equity=0) is None

def test_roa_basic():
    assert roa(net_income=80, avg_total_assets=1000) == pytest.approx(0.08)

def test_nopat_basic():
    # NOPAT = EBIT × (1 - tax_rate) = 100 × 0.75 = 75
    result = nopat(ebit=100, tax_rate=0.25)
    assert result == pytest.approx(75.0)

def test_invested_capital_basic():
    # IC = Equity + Debt - Cash = 500 + 200 - 50 = 650
    result = invested_capital(total_equity=500, total_debt=200, cash=50)
    assert result == pytest.approx(650.0)

def test_roic_basic():
    nopat_val = nopat(ebit=100, tax_rate=0.25)  # 75
    ic_val = invested_capital(total_equity=500, total_debt=200, cash=50)  # 650
    result = roic(nopat_value=nopat_val, invested_capital=ic_val)
    assert result == pytest.approx(75.0 / 650.0)

def test_roic_zero_ic():
    assert roic(nopat_value=50, invested_capital=0) is None

def test_du_pont_3_roe():
    # ROE = NI / Avg Equity; internally decomposed
    result = du_pont_3(
        net_income=120, revenue=1000, avg_total_assets=800, avg_total_equity=600
    )
    assert "roe" in result
    assert result["roe"] == pytest.approx(120 / 600)

def test_revenue_per_employee_basic():
    result = revenue_per_employee(revenue=10_000_000, employee_count=100)
    assert result == pytest.approx(100_000.0)

def test_profit_per_employee_zero_employees():
    assert profit_per_employee(net_income=1_000_000, employee_count=0) is None

def test_all_profitability_have_formula():
    for fn in [gross_margin, operating_margin, net_profit_margin, roe, roa, roic]:
        assert hasattr(fn, "formula"), f"{fn.__name__} missing .formula"
