"""Tests for Valuation Attractiveness Score."""
import pytest
from fin_ratios.utils.valuation_score import (
    valuation_attractiveness_score,
    ValuationScore,
    ValuationComponents,
)


class TestValuationAttractivenessScoreRatings:

    def test_attractive_scenario_score_and_rating(self):
        r = valuation_attractiveness_score(
            pe_ratio=12,
            ev_ebitda=7,
            p_fcf=11,
            pb_ratio=1.2,
        )
        assert r.score >= 70, f"Expected score ≥70 for cheap metrics, got {r.score}"
        assert r.rating == "attractive"

    def test_expensive_scenario_score_and_rating(self):
        r = valuation_attractiveness_score(
            pe_ratio=45,
            ev_ebitda=28,
            p_fcf=40,
            pb_ratio=8,
        )
        assert r.score <= 30, f"Expected score ≤30 for stretched metrics, got {r.score}"
        assert r.rating in ("expensive", "overvalued")

    def test_neutral_no_args_score_near_50(self):
        r = valuation_attractiveness_score()
        # All signals neutral → weighted average of 0.50 → score = 50
        assert 45 <= r.score <= 55, f"Expected score near 50 with no inputs, got {r.score}"
        assert r.rating == "fair"

    def test_partial_data_only_pe_ratio(self):
        r = valuation_attractiveness_score(pe_ratio=18)
        assert r.score is not None
        assert 0 <= r.score <= 100

    def test_earnings_yield_pct_overrides_pe_ratio(self):
        # earnings_yield_pct=10% is equivalent to PE=10 — very cheap
        r_ey = valuation_attractiveness_score(earnings_yield_pct=10.0)
        # pe_ratio=30 implies EY~3.3% — more expensive
        r_pe = valuation_attractiveness_score(pe_ratio=30)
        assert r_ey.score > r_pe.score

    def test_fcf_yield_pct_overrides_p_fcf(self):
        # high FCF yield should score better
        r_high = valuation_attractiveness_score(fcf_yield_pct=8.0)
        r_low = valuation_attractiveness_score(fcf_yield_pct=1.0)
        assert r_high.score > r_low.score

    def test_positive_dcf_upside_raises_score(self):
        r_no_dcf = valuation_attractiveness_score(pe_ratio=18)
        r_dcf_up = valuation_attractiveness_score(pe_ratio=18, dcf_upside_pct=40.0)
        assert r_dcf_up.score > r_no_dcf.score

    def test_negative_dcf_upside_lowers_score(self):
        r_no_dcf = valuation_attractiveness_score(pe_ratio=18)
        r_dcf_down = valuation_attractiveness_score(pe_ratio=18, dcf_upside_pct=-30.0)
        assert r_dcf_down.score < r_no_dcf.score

    def test_risk_free_rate_affects_earnings_yield_signal(self):
        # Same PE but different risk-free rate — lower rfr means EY spread is wider → higher score
        r_low_rf = valuation_attractiveness_score(pe_ratio=20, risk_free_rate=0.01)
        r_high_rf = valuation_attractiveness_score(pe_ratio=20, risk_free_rate=0.08)
        assert r_low_rf.score > r_high_rf.score

    def test_to_dict_has_required_keys(self):
        r = valuation_attractiveness_score(pe_ratio=15, ev_ebitda=9, pb_ratio=2.0)
        d = r.to_dict()
        for key in ("score", "rating", "components", "risk_free_rate", "evidence", "interpretation"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_components_has_all_signals(self):
        r = valuation_attractiveness_score(pe_ratio=15)
        d = r.to_dict()
        comp = d["components"]
        for key in ("earnings_yield", "fcf_yield", "ev_ebitda", "pb_ratio", "dcf_upside"):
            assert key in comp, f"Missing component key: {key}"

    def test_table_returns_non_empty_string(self):
        r = valuation_attractiveness_score(pe_ratio=20, ev_ebitda=12)
        t = r.table()
        assert isinstance(t, str)
        assert len(t) > 0
        assert "Valuation Attractiveness Score" in t

    def test_interpretation_is_non_empty_string(self):
        r = valuation_attractiveness_score(pe_ratio=20)
        assert isinstance(r.interpretation, str)
        assert len(r.interpretation) > 0
        assert str(r.score) in r.interpretation

    def test_score_in_valid_range_all_inputs(self):
        r = valuation_attractiveness_score(
            pe_ratio=15,
            ev_ebitda=9,
            p_fcf=14,
            pb_ratio=1.8,
            dcf_upside_pct=20.0,
            risk_free_rate=0.045,
        )
        assert 0 <= r.score <= 100
        assert isinstance(r, ValuationScore)
        assert isinstance(r.components, ValuationComponents)
