"""Tests for Investment Score."""
import pytest
from fin_ratios.utils.investment_score import (
    investment_score_from_scores,
    investment_score_from_series,
    InvestmentScore,
    InvestmentComponents,
)


# ── Synthetic series data ───────────────────────────────────────────────────────

def _high_quality_series():
    """Strong fundamentals: high ROIC, growing revenue/margins, no dividends (non-payer)."""
    return [
        {
            "year": y,
            "revenue":             (80 + y * 12) * 1e9,
            "ebit":                (22 + y * 3)  * 1e9,
            "net_income":          (15 + y * 2)  * 1e9,
            "total_assets":         90e9,
            "total_equity":         50e9,
            "total_debt":           10e9,
            "cash":                 12e9,
            "capex":                 4e9,
            "depreciation":          5e9,
            "income_tax_expense":  (4.5 + y * 0.6) * 1e9,
            "ebt":                 (20 + y * 2.8)  * 1e9,
            "operating_cash_flow": (20 + y * 2.5)  * 1e9,
            "dividends_paid":        0.0,
            "shares_outstanding":  (800 - y * 15) * 1e6,
            "interest_expense":      0.5e9,
        }
        for y in range(5)
    ]


def _low_quality_series():
    """Weak fundamentals: low ROIC, shrinking margins, heavy debt."""
    return [
        {
            "year": y,
            "revenue":             (50 + y * 0.5) * 1e9,
            "ebit":                 (3 - y * 0.2) * 1e9,
            "net_income":           (1 - y * 0.1) * 1e9,
            "total_assets":        160e9,
            "total_equity":         15e9,
            "total_debt":           90e9,
            "cash":                  2e9,
            "capex":                14e9,
            "depreciation":          8e9,
            "income_tax_expense":    0.4e9,
            "ebt":                   0.5e9,
            "operating_cash_flow":   4e9,
            "dividends_paid":        0.0,
            "shares_outstanding":  (400 + y * 25) * 1e6,
            "interest_expense":      5e9,
        }
        for y in range(5)
    ]


# ── Tests: investment_score_from_scores ────────────────────────────────────────

class TestInvestmentScoreFromScores:

    def test_strong_scores_high_score_and_grade(self):
        r = investment_score_from_scores(
            moat_score=80,
            capital_allocation_score=75,
            earnings_quality_score=80,
            management_score=75,
            valuation_score=70,
        )
        assert r.score >= 75, f"Expected score ≥75 for strong inputs, got {r.score}"
        assert r.grade in ("A+", "A", "B+"), f"Expected A+/A/B+, got {r.grade}"
        assert r.conviction in ("strong_buy", "buy"), f"Expected buy conviction, got {r.conviction}"

    def test_weak_scores_low_score_and_sell_conviction(self):
        r = investment_score_from_scores(
            moat_score=20,
            capital_allocation_score=25,
            earnings_quality_score=25,
            management_score=20,
            valuation_score=15,
        )
        assert r.score <= 30, f"Expected score ≤30 for weak inputs, got {r.score}"
        assert r.conviction in ("sell", "strong_sell"), f"Expected sell conviction, got {r.conviction}"

    def test_valuation_score_none_still_computes(self):
        r = investment_score_from_scores(
            moat_score=60,
            capital_allocation_score=60,
            earnings_quality_score=60,
            management_score=60,
            valuation_score=None,
        )
        assert r.score is not None
        assert 0 <= r.score <= 100
        assert r.components.valuation is None

    def test_grade_mapping_a_plus(self):
        r = investment_score_from_scores(
            moat_score=95, capital_allocation_score=95,
            earnings_quality_score=95, management_score=95,
            valuation_score=95,
        )
        assert r.grade == "A+"
        assert r.score >= 90

    def test_grade_mapping_a(self):
        r = investment_score_from_scores(
            moat_score=82, capital_allocation_score=82,
            earnings_quality_score=82, management_score=82,
            valuation_score=82,
        )
        assert r.grade == "A"
        assert 80 <= r.score <= 89

    def test_grade_mapping_b_plus(self):
        r = investment_score_from_scores(
            moat_score=72, capital_allocation_score=72,
            earnings_quality_score=72, management_score=72,
            valuation_score=72,
        )
        assert r.grade == "B+"

    def test_grade_mapping_b(self):
        r = investment_score_from_scores(
            moat_score=62, capital_allocation_score=62,
            earnings_quality_score=62, management_score=62,
            valuation_score=62,
        )
        assert r.grade == "B"

    def test_grade_mapping_c(self):
        r = investment_score_from_scores(
            moat_score=52, capital_allocation_score=52,
            earnings_quality_score=52, management_score=52,
            valuation_score=52,
        )
        assert r.grade == "C"

    def test_conviction_buy_at_70_plus(self):
        r = investment_score_from_scores(
            moat_score=72, capital_allocation_score=72,
            earnings_quality_score=72, management_score=72,
            valuation_score=72,
        )
        assert r.conviction in ("buy", "strong_buy")

    def test_conviction_sell_below_30(self):
        r = investment_score_from_scores(
            moat_score=20, capital_allocation_score=20,
            earnings_quality_score=20, management_score=20,
            valuation_score=20,
        )
        assert r.conviction in ("sell", "strong_sell")

    def test_to_dict_has_required_keys(self):
        r = investment_score_from_scores(
            moat_score=60, capital_allocation_score=60,
            earnings_quality_score=60, management_score=60,
        )
        d = r.to_dict()
        for key in ("score", "grade", "conviction", "components",
                    "years_analyzed", "evidence", "interpretation"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_components_has_all_fields(self):
        r = investment_score_from_scores(
            moat_score=60, capital_allocation_score=60,
            earnings_quality_score=60, management_score=60,
            valuation_score=55,
        )
        comp = r.to_dict()["components"]
        for key in ("moat", "capital_allocation", "earnings_quality",
                    "management", "valuation", "dividend_safety"):
            assert key in comp, f"Missing component key: {key}"

    def test_evidence_list_non_empty(self):
        r = investment_score_from_scores(
            moat_score=70, capital_allocation_score=65,
            earnings_quality_score=70, management_score=65,
            valuation_score=60,
        )
        assert len(r.evidence) >= 4


# ── Tests: investment_score_from_series ────────────────────────────────────────

class TestInvestmentScoreFromSeries:

    def test_returns_investment_score_instance(self):
        r = investment_score_from_series(_high_quality_series())
        assert isinstance(r, InvestmentScore)
        assert isinstance(r.components, InvestmentComponents)

    def test_with_valuation_params(self):
        r = investment_score_from_series(
            _high_quality_series(),
            pe_ratio=15,
            ev_ebitda=9,
        )
        assert isinstance(r, InvestmentScore)
        assert r.components.valuation is not None

    def test_high_quality_beats_low_quality(self):
        r_high = investment_score_from_series(_high_quality_series())
        r_low = investment_score_from_series(_low_quality_series())
        assert r_high.score > r_low.score

    def test_years_analyzed_matches_input(self):
        data = _high_quality_series()
        r = investment_score_from_series(data)
        assert r.years_analyzed == len(data)

    def test_fewer_than_3_years_raises(self):
        with pytest.raises(ValueError, match="at least 3 years"):
            investment_score_from_series(_high_quality_series()[:2])
