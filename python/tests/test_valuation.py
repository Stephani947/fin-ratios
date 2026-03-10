"""Tests for valuation ratios."""

import math
import pytest
from fin_ratios import (
    pe, forward_pe, peg, pb, ps, p_fcf,
    ev_ebitda, ev_ebit, ev_revenue, ev_fcf,
    tobin_q, graham_number, graham_intrinsic_value,
)
from fin_ratios.ratios.valuation_dcf import dcf_2_stage, gordon_growth_model, reverse_dcf


# ── P/E ───────────────────────────────────────────────────────────────────────

def test_pe_basic():
    assert pe(market_cap=3_000_000, net_income=100_000) == pytest.approx(30.0)

def test_pe_zero_income():
    assert pe(market_cap=1_000_000, net_income=0) is None

def test_pe_negative_income():
    result = pe(market_cap=1_000_000, net_income=-50_000)
    assert result == pytest.approx(-20.0)

def test_pe_has_formula():
    assert hasattr(pe, "formula")
    assert "Net Income" in pe.formula


# ── Forward P/E ───────────────────────────────────────────────────────────────

def test_forward_pe_basic():
    assert forward_pe(price=150.0, forward_eps=7.5) == pytest.approx(20.0)

def test_forward_pe_zero_eps():
    assert forward_pe(price=150.0, forward_eps=0.0) is None


# ── PEG ──────────────────────────────────────────────────────────────────────

def test_peg_basic():
    result = peg(pe_ratio=20.0, eps_growth_rate_pct=10.0)
    assert result == pytest.approx(2.0)

def test_peg_zero_growth():
    assert peg(pe_ratio=20.0, eps_growth_rate_pct=0.0) is None


# ── P/B ──────────────────────────────────────────────────────────────────────

def test_pb_basic():
    assert pb(market_cap=500_000, total_equity=100_000) == pytest.approx(5.0)

def test_pb_zero_equity():
    assert pb(market_cap=500_000, total_equity=0) is None


# ── P/S ──────────────────────────────────────────────────────────────────────

def test_ps_basic():
    assert ps(market_cap=300_000, revenue=100_000) == pytest.approx(3.0)


# ── EV/EBITDA ─────────────────────────────────────────────────────────────────

def test_ev_ebitda_basic():
    # ev_ebitda takes `ev` not `enterprise_value`
    assert ev_ebitda(ev=3_060_000_000_000, ebitda=130_000_000_000) == pytest.approx(23.538, rel=1e-3)

def test_ev_ebitda_zero():
    assert ev_ebitda(ev=1e9, ebitda=0) is None


# ── Graham Number ─────────────────────────────────────────────────────────────

def test_graham_number_basic():
    result = graham_number(eps=6.43, book_value_per_share=4.50)
    assert result == pytest.approx(math.sqrt(22.5 * 6.43 * 4.50), rel=1e-4)

def test_graham_number_negative_eps():
    assert graham_number(eps=-1.0, book_value_per_share=10.0) is None

def test_graham_number_zero_bvps():
    assert graham_number(eps=5.0, book_value_per_share=0.0) is None


# ── Graham Intrinsic Value ────────────────────────────────────────────────────

def test_graham_intrinsic_value_basic():
    # V* = EPS × (8.5 + 2g) × 4.4 / Y; when Y == 4.4 → V* = EPS × (8.5 + 2g)
    result = graham_intrinsic_value(eps=5.0, growth_rate=10.0, aaa_bond_yield=4.4)
    # 5 × (8.5 + 20) = 5 × 28.5 = 142.5
    assert result == pytest.approx(142.5)


# ── Tobin's Q ────────────────────────────────────────────────────────────────

def test_tobins_q_basic():
    result = tobin_q(market_cap=500e6, total_debt=100e6, total_assets=400e6)
    assert result == pytest.approx(1.5)


# ── DCF ──────────────────────────────────────────────────────────────────────

def test_dcf_2_stage_returns_positive():
    result = dcf_2_stage(
        base_fcf=5_000_000_000,
        growth_rate=0.15,
        years=10,
        terminal_growth_rate=0.03,
        wacc=0.10,
        net_debt=-2_000_000_000,
        shares_outstanding=1_000_000_000,
    )
    assert result is not None
    assert result["intrinsic_value"] > 0
    assert result["intrinsic_value_per_share"] > 0

def test_dcf_invalid_wacc_less_than_terminal():
    result = dcf_2_stage(
        base_fcf=1e9, growth_rate=0.10, years=10,
        terminal_growth_rate=0.12,  # > wacc — invalid
        wacc=0.10,
    )
    assert result is None


# ── Gordon Growth Model ──────────────────────────────────────────────────────

def test_gordon_growth_basic():
    # P = D1 / (r - g) = 2 / (0.09 - 0.04) = 40
    result = gordon_growth_model(next_dividend=2.0, required_return=0.09, dividend_growth_rate=0.04)
    assert result == pytest.approx(40.0)

def test_gordon_growth_rate_exceeds_return():
    result = gordon_growth_model(next_dividend=2.0, required_return=0.05, dividend_growth_rate=0.06)
    assert result is None


# ── Reverse DCF ──────────────────────────────────────────────────────────────

def test_reverse_dcf_returns_interpretation():
    result = reverse_dcf(
        market_cap=500_000_000_000,
        base_fcf=10_000_000_000,
        years=10,
        terminal_growth_rate=0.03,
        wacc=0.10,
    )
    assert result is not None
    assert "implied_growth_rate" in result
    assert "interpretation" in result
    assert 0 < result["implied_growth_rate"] < 1
