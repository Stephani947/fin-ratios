"""Tests for Fair Value Range."""
import pytest
from fin_ratios.utils.fair_value import fair_value_range, FairValueRange


# ── Basic structural tests ────────────────────────────────────────────────────

class TestFairValueBasic:

    def test_returns_correct_type(self):
        r = fair_value_range(
            fcf=90e9, shares=15.5e9, growth_rate=0.07,
            eps=6.10, bvps=4.00,
        )
        assert isinstance(r, FairValueRange)

    def test_requires_at_least_one_method(self):
        with pytest.raises(ValueError, match="No valuation methods"):
            fair_value_range()

    def test_dcf_only(self):
        r = fair_value_range(
            fcf=100e9, shares=10e9,
            growth_rate=0.08, terminal_growth=0.03, wacc=0.09,
        )
        assert r.methods_used == 2  # DCF + FCF Yield both use fcf+shares
        assert r.base_value > 0

    def test_graham_only(self):
        r = fair_value_range(eps=5.0, bvps=20.0)
        assert r.methods_used == 1
        assert "Graham Number" in r.estimates
        import math
        expected = math.sqrt(22.5 * 5.0 * 20.0)
        assert abs(r.base_value - expected) < 0.01

    def test_all_methods(self):
        r = fair_value_range(
            fcf=90e9, shares=15e9,
            eps=6.0, bvps=5.0,
            ebitda=130e9, total_debt=100e9, cash=60e9,
            ebit=110e9, tax_rate=0.21,
            growth_rate=0.07, wacc=0.09,
        )
        assert r.methods_used == 5

    def test_methods_used_matches_estimates(self):
        r = fair_value_range(fcf=50e9, shares=5e9, eps=8.0, bvps=10.0)
        assert r.methods_used == len(r.estimates)


# ── Range ordering ────────────────────────────────────────────────────────────

class TestFairValueRange:

    def test_bear_le_base_le_bull(self):
        r = fair_value_range(
            fcf=80e9, shares=10e9,
            eps=5.0, bvps=15.0,
            ebitda=100e9, total_debt=50e9, cash=20e9,
        )
        assert r.bear_value <= r.base_value <= r.bull_value

    def test_all_values_positive(self):
        r = fair_value_range(fcf=50e9, shares=5e9, eps=8.0, bvps=12.0)
        assert r.base_value > 0
        assert r.bear_value > 0
        assert r.bull_value > 0

    def test_current_price_upside(self):
        r = fair_value_range(
            fcf=100e9, shares=10e9, eps=6.0, bvps=8.0,
            current_price=50.0,
        )
        assert r.upside_pct is not None
        # upside = (base / 50 - 1) * 100
        assert abs(r.upside_pct - (r.base_value / 50.0 - 1) * 100) < 0.01

    def test_no_upside_without_price(self):
        r = fair_value_range(fcf=50e9, shares=5e9)
        assert r.upside_pct is None
        assert r.margin_of_safety is None


# ── DCF edge cases ────────────────────────────────────────────────────────────

class TestFairValueDCF:

    def test_negative_fcf_skips_dcf(self):
        r = fair_value_range(eps=5.0, bvps=20.0)
        assert "DCF (2-stage)" not in r.estimates

    def test_wacc_less_than_terminal_skips_dcf(self):
        # wacc <= terminal_growth → undefined
        r = fair_value_range(
            fcf=50e9, shares=5e9,
            wacc=0.02, terminal_growth=0.03,
            eps=5.0, bvps=10.0,
        )
        assert "DCF (2-stage)" not in r.estimates

    def test_higher_growth_gives_higher_dcf(self):
        r_low = fair_value_range(fcf=50e9, shares=5e9, growth_rate=0.03)
        r_high = fair_value_range(fcf=50e9, shares=5e9, growth_rate=0.12)
        assert r_high.base_value > r_low.base_value


# ── Output / display tests ────────────────────────────────────────────────────

class TestFairValueOutput:

    def test_table_returns_string(self):
        r = fair_value_range(fcf=50e9, shares=5e9, eps=6.0, bvps=8.0)
        t = r.table()
        assert isinstance(t, str)
        assert "Fair Value Range" in t
        assert "Base" in t

    def test_repr_html(self):
        r = fair_value_range(fcf=50e9, shares=5e9, eps=6.0, bvps=8.0,
                             current_price=100.0)
        html = r._repr_html_()
        assert "<div" in html

    def test_to_dict_keys(self):
        r = fair_value_range(fcf=50e9, shares=5e9, eps=6.0, bvps=8.0)
        d = r.to_dict()
        for key in ("estimates", "base_value", "bull_value", "bear_value",
                    "methods_used", "interpretation"):
            assert key in d

    def test_to_dict_with_price_includes_upside(self):
        r = fair_value_range(fcf=50e9, shares=5e9, current_price=100.0)
        d = r.to_dict()
        assert "upside_pct" in d
        assert "margin_of_safety" in d

    def test_interpretation_string(self):
        r = fair_value_range(fcf=50e9, shares=5e9, current_price=5.0)
        assert isinstance(r.interpretation, str)
        assert len(r.interpretation) > 0

    def test_top_level_import(self):
        from fin_ratios import fair_value_range as f
        from fin_ratios import FairValueRange as C
        assert f is not None
        assert C is not None
