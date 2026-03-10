"""Tests for composite scoring models."""

import pytest
from fin_ratios import piotroski_f_score, altman_z_score, beneish_m_score
from fin_ratios.ratios.composite import magic_formula, ohlson_o_score


# ── Piotroski F-Score ─────────────────────────────────────────────────────────

STRONG = dict(
    current_net_income=8_500_000,
    current_total_assets=100_000_000,
    current_operating_cf=12_000_000,
    current_long_term_debt=20_000_000,
    current_current_assets=35_000_000,
    current_current_liabilities=15_000_000,
    current_shares_outstanding=10_000_000,
    current_gross_profit=45_000_000,
    current_revenue=90_000_000,
    prior_net_income=5_000_000,
    prior_total_assets=95_000_000,
    prior_long_term_debt=25_000_000,
    prior_current_assets=28_000_000,
    prior_current_liabilities=14_000_000,
    prior_shares_outstanding=10_500_000,
    prior_gross_profit=38_000_000,
    prior_revenue=80_000_000,
)

WEAK = dict(
    current_net_income=-2_000_000,
    current_total_assets=100_000_000,
    current_operating_cf=-500_000,
    current_long_term_debt=45_000_000,
    current_current_assets=18_000_000,
    current_current_liabilities=15_000_000,
    current_shares_outstanding=12_000_000,
    current_gross_profit=20_000_000,
    current_revenue=80_000_000,
    prior_net_income=3_000_000,
    prior_total_assets=95_000_000,
    prior_long_term_debt=30_000_000,
    prior_current_assets=25_000_000,
    prior_current_liabilities=12_000_000,
    prior_shares_outstanding=10_000_000,
    prior_gross_profit=28_000_000,
    prior_revenue=90_000_000,
)


def test_piotroski_strong():
    result = piotroski_f_score(**STRONG)
    assert result["score"] == 9
    assert "Strong" in result["interpretation"]

def test_piotroski_weak():
    result = piotroski_f_score(**WEAK)
    assert result["score"] <= 3
    assert "Weak" in result["interpretation"]

def test_piotroski_score_range():
    result = piotroski_f_score(**STRONG)
    assert 0 <= result["score"] <= 9

def test_piotroski_has_signals():
    result = piotroski_f_score(**STRONG)
    assert "signals" in result
    assert len(result["signals"]) == 9

def test_piotroski_all_signals_boolean():
    result = piotroski_f_score(**STRONG)
    for signal_val in result["signals"].values():
        assert isinstance(signal_val, bool)


# ── Altman Z-Score ────────────────────────────────────────────────────────────

def test_altman_safe_zone():
    result = altman_z_score(
        working_capital=500e6,
        retained_earnings=200e6,
        ebit=90e6,
        market_cap=3000e6,
        total_liabilities=210e6,
        total_assets=411e6,
        revenue=212e6,
    )
    assert result is not None
    assert result["zone"] == "safe"
    assert result["z_score"] > 2.99

def test_altman_distress_zone():
    result = altman_z_score(
        working_capital=-20e6,
        retained_earnings=-50e6,
        ebit=-5e6,
        market_cap=80e6,
        total_liabilities=200e6,
        total_assets=250e6,
        revenue=150e6,
    )
    assert result is not None
    assert result["zone"] == "distress"
    assert result["z_score"] < 1.81

def test_altman_grey_zone():
    result = altman_z_score(
        working_capital=30e6,
        retained_earnings=15e6,
        ebit=8e6,
        market_cap=120e6,
        total_liabilities=80e6,
        total_assets=180e6,
        revenue=160e6,
    )
    assert result is not None
    assert result["zone"] == "grey"

def test_altman_zero_assets():
    result = altman_z_score(
        working_capital=10e6, retained_earnings=5e6, ebit=2e6,
        market_cap=50e6, total_liabilities=30e6, total_assets=0, revenue=20e6,
    )
    assert result is None

def test_altman_has_interpretation():
    result = altman_z_score(
        working_capital=500e6, retained_earnings=200e6, ebit=90e6,
        market_cap=3000e6, total_liabilities=210e6, total_assets=411e6, revenue=212e6,
    )
    assert "interpretation" in result
    assert len(result["interpretation"]) > 0

def test_altman_formula_coefficients():
    # Z = 1.2×X1 + ... with X1 = WC/TA
    # Isolate: all other numerators = 0, WC=10, TA=100
    result = altman_z_score(
        working_capital=10, retained_earnings=0, ebit=0,
        market_cap=0, total_liabilities=1, total_assets=100, revenue=0,
    )
    assert result is not None
    x1 = 10 / 100
    expected = 1.2 * x1
    assert result["z_score"] == pytest.approx(expected, rel=1e-3)


# ── Beneish M-Score ───────────────────────────────────────────────────────────

CLEAN_KWARGS = dict(
    c_revenue=100e6, c_accounts_receivable=12e6, c_gross_profit=40e6,
    c_total_assets=150e6, c_depreciation=8e6, c_pp_gross=50e6,
    c_sga_expense=15e6, c_total_debt=30e6, c_net_income=8e6, c_cash_from_ops=11e6,
    p_revenue=90e6, p_accounts_receivable=10e6, p_gross_profit=35e6,
    p_total_assets=140e6, p_depreciation=7e6, p_pp_gross=45e6,
    p_sga_expense=14e6, p_total_debt=30e6,
)

SUSPICIOUS_KWARGS = dict(
    c_revenue=110e6, c_accounts_receivable=25e6, c_gross_profit=38e6,
    c_total_assets=155e6, c_depreciation=6e6, c_pp_gross=55e6,
    c_sga_expense=20e6, c_total_debt=45e6, c_net_income=12e6, c_cash_from_ops=3e6,
    p_revenue=90e6, p_accounts_receivable=10e6, p_gross_profit=38e6,
    p_total_assets=140e6, p_depreciation=8e6, p_pp_gross=45e6,
    p_sga_expense=14e6, p_total_debt=30e6,
)


def test_beneish_clean():
    result = beneish_m_score(**CLEAN_KWARGS)
    assert result is not None
    assert result["manipulation_likely"] is False
    assert result["m_score"] < -2.22

def test_beneish_suspicious():
    result = beneish_m_score(**SUSPICIOUS_KWARGS)
    assert result is not None
    assert result["manipulation_likely"] is True
    assert result["m_score"] > -2.22

def test_beneish_has_variables():
    result = beneish_m_score(**CLEAN_KWARGS)
    assert result is not None
    variables = result["variables"]
    for key in ["dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi"]:
        assert key in variables

def test_beneish_zero_prior_revenue():
    kwargs = CLEAN_KWARGS.copy()
    kwargs["p_revenue"] = 0
    result = beneish_m_score(**kwargs)
    assert result is None


# ── Magic Formula ─────────────────────────────────────────────────────────────

def test_magic_formula_basic():
    result = magic_formula(
        ebit=3e9,
        net_working_capital=0.5e9,
        net_fixed_assets=0.3e9,
        enterprise_value=40e9,
    )
    assert result is not None
    assert result["roic"] is not None
    assert result["earnings_yield"] is not None
    # ROIC = EBIT / (NWC + NFA) = 3e9 / 0.8e9
    assert result["roic"] == pytest.approx(3e9 / 0.8e9)

def test_magic_formula_zero_ev():
    result = magic_formula(
        ebit=1e9, net_working_capital=0.5e9, net_fixed_assets=0.3e9,
        enterprise_value=0,
    )
    assert result["earnings_yield"] is None


# ── Ohlson O-Score ────────────────────────────────────────────────────────────

def test_ohlson_returns_probability():
    result = ohlson_o_score(
        total_assets=500e6, total_liabilities=200e6,
        current_assets=140e6, current_liabilities=60e6,
        net_income=30e6, prior_net_income=25e6,
        operating_cash_flow=40e6, working_capital=80e6,
    )
    assert result is not None
    assert 0.0 <= result["bankruptcy_probability"] <= 1.0

def test_ohlson_distressed_company():
    result = ohlson_o_score(
        total_assets=100e6, total_liabilities=180e6,
        current_assets=50e6, current_liabilities=80e6,
        net_income=-20e6, prior_net_income=-10e6,
        operating_cash_flow=-5e6, working_capital=-30e6,
    )
    assert result is not None
    assert result["bankruptcy_probability"] > 0.5
