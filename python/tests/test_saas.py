"""Tests for SaaS / tech metrics."""

import pytest
from fin_ratios import (
    rule_of_40, net_revenue_retention, gross_revenue_retention,
    magic_number, ltv_cac_ratio, cac_payback_period,
    burn_multiple, saas_quick_ratio, arr_per_fte,
    customer_lifetime_value, customer_acquisition_cost,
)


def test_rule_of_40_healthy():
    result = rule_of_40(revenue_growth_rate_pct=35, fcf_margin_pct=12)
    assert result == pytest.approx(47)

def test_rule_of_40_exactly_40():
    result = rule_of_40(revenue_growth_rate_pct=20, fcf_margin_pct=20)
    assert result == pytest.approx(40)

def test_rule_of_40_formula():
    assert hasattr(rule_of_40, "formula")


def test_nrr_expansion():
    # NRR = (beginning_arr + expansion - churn - contraction) / beginning_arr
    result = net_revenue_retention(
        beginning_arr=100e6, expansion=20e6, churn=5e6, contraction=2e6
    )
    assert result == pytest.approx(1.13)

def test_nrr_no_expansion():
    result = net_revenue_retention(
        beginning_arr=100e6, expansion=0, churn=10e6, contraction=0
    )
    assert result == pytest.approx(0.90)

def test_nrr_zero_beginning():
    assert net_revenue_retention(beginning_arr=0, expansion=10e6, churn=0, contraction=0) is None


def test_grr_basic():
    # GRR = (beginning_arr - churn - contraction) / beginning_arr
    result = gross_revenue_retention(beginning_arr=100e6, churn=5e6, contraction=0)
    assert result == pytest.approx(0.95)

def test_grr_no_churn():
    result = gross_revenue_retention(beginning_arr=100e6, churn=0, contraction=0)
    assert result == pytest.approx(1.0)


def test_burn_multiple_excellent():
    result = burn_multiple(net_burn_rate=800_000, net_new_arr=1_000_000)
    assert result == pytest.approx(0.8)

def test_burn_multiple_zero_arr():
    assert burn_multiple(net_burn_rate=500_000, net_new_arr=0) is None


def test_magic_number_efficient():
    # magic_number = (current_q_rev - prior_q_rev) * 4 / prior_q_sm_spend
    result = magic_number(
        current_quarter_revenue=1_500_000,
        prior_quarter_revenue=1_000_000,
        prior_quarter_sm_spend=400_000,
    )
    expected = (1_500_000 - 1_000_000) * 4 / 400_000
    assert result == pytest.approx(expected)

def test_magic_number_zero_sm():
    assert magic_number(
        current_quarter_revenue=1_500_000,
        prior_quarter_revenue=1_000_000,
        prior_quarter_sm_spend=0,
    ) is None


def test_ltv_cac_ratio_basic():
    result = ltv_cac_ratio(ltv=3000, cac=500)
    assert result == pytest.approx(6.0)

def test_ltv_cac_zero_cac():
    assert ltv_cac_ratio(ltv=3000, cac=0) is None


def test_cac_payback_basic():
    # payback = cac / (monthly_revenue × gross_margin)
    result = cac_payback_period(
        cac=1200,
        avg_monthly_revenue_per_customer=200,
        gross_margin_pct=0.50,
    )
    # 1200 / (200 × 0.50) = 12 months
    assert result == pytest.approx(12.0)


def test_saas_quick_ratio_excellent():
    # QR = (new_mrr + expansion_mrr) / (churned_mrr + contraction_mrr)
    result = saas_quick_ratio(new_mrr=40e6, expansion_mrr=20e6, churned_mrr=5e6, contraction_mrr=5e6)
    assert result == pytest.approx(6.0)

def test_saas_quick_ratio_zero_denominator():
    result = saas_quick_ratio(new_mrr=40e6, expansion_mrr=20e6, churned_mrr=0, contraction_mrr=0)
    assert result is None


def test_arr_per_fte_basic():
    result = arr_per_fte(arr=10_000_000, full_time_employees=50)
    assert result == pytest.approx(200_000.0)


def test_customer_ltv_basic():
    # LTV = (avg_monthly_revenue × gross_margin) / monthly_churn
    result = customer_lifetime_value(
        avg_monthly_revenue_per_customer=1000,
        gross_margin=0.70,
        monthly_churn_rate=0.05,
    )
    assert result == pytest.approx(14_000.0)

def test_customer_ltv_zero_churn():
    assert customer_lifetime_value(
        avg_monthly_revenue_per_customer=1000,
        gross_margin=0.70,
        monthly_churn_rate=0.0,
    ) is None


def test_cac_basic():
    result = customer_acquisition_cost(sales_and_marketing_spend=1_000_000, new_customers_acquired=500)
    assert result == pytest.approx(2000.0)
