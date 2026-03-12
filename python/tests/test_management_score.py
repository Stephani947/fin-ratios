"""Tests for Management Quality Score."""
import pytest
from fin_ratios.utils.management_score import (
    management_quality_score_from_series,
    ManagementScore,
    ManagementComponents,
)


# ── Synthetic datasets ──────────────────────────────────────────────────────────

def _strong_management():
    """High ROIC 20%+, improving margins, declining share count, solid revenue growth."""
    return [
        {
            "year": y,
            "revenue":              (80  + y * 12) * 1e9,
            "ebit":                 (18  + y * 3)  * 1e9,
            "total_equity":          45e9,
            "total_debt":            10e9,
            "cash":                  15e9,
            "capex":                  3e9,
            "depreciation":           4e9,
            "income_tax_expense":   ( 4  + y * 0.7) * 1e9,
            "ebt":                  (16  + y * 2.8) * 1e9,
            "total_assets":          80e9,
            "operating_cash_flow":  (20  + y * 2.5) * 1e9,
            "net_income":           (12  + y * 2)   * 1e9,
            "dividends_paid":         2e9,
            # Share count declining 2% per year — buybacks
            "shares_outstanding":   (1000 - y * 20) * 1e6,
            "interest_expense":       0.5e9,
        }
        for y in range(5)
    ]


def _weak_management():
    """Low ROIC ~4%, declining margins, diluting shares, flat/declining revenue."""
    return [
        {
            "year": y,
            "revenue":              (50 + y * 0.5) * 1e9,
            "ebit":                 ( 4 - y * 0.3) * 1e9,
            "total_equity":          20e9,
            "total_debt":            60e9,
            "cash":                   2e9,
            "capex":                 12e9,
            "depreciation":           7e9,
            "income_tax_expense":     0.5e9,
            "ebt":                    1e9,
            "total_assets":         (120 + y * 10) * 1e9,
            "operating_cash_flow":    6e9,
            "net_income":             0.8e9,
            "dividends_paid":         0.0,
            # Share count growing 4% per year — dilution
            "shares_outstanding":   (500 + y * 20) * 1e6,
            "interest_expense":       3.5e9,
        }
        for y in range(5)
    ]


def _base_record(y: int, shares: float) -> dict:
    """Minimal valid record for testing isolated signals."""
    return {
        "year": y,
        "revenue":            (50 + y * 5) * 1e9,
        "ebit":               (10 + y * 1) * 1e9,
        "total_equity":        30e9,
        "total_debt":          10e9,
        "cash":                 5e9,
        "capex":                3e9,
        "depreciation":         4e9,
        "income_tax_expense":   2.5e9,
        "ebt":                  9e9,
        "total_assets":        60e9,
        "operating_cash_flow": 12e9,
        "net_income":           7e9,
        "dividends_paid":       1e9,
        "shares_outstanding":  shares,
        "interest_expense":     0.8e9,
    }


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestManagementScoreRatings:

    def test_strong_management_score_and_rating(self):
        r = management_quality_score_from_series(_strong_management())
        assert r.score >= 60, f"Expected score ≥60 for strong management, got {r.score}"
        assert r.rating in ("excellent", "good"), f"Expected good/excellent, got {r.rating}"

    def test_weak_management_score_and_rating(self):
        r = management_quality_score_from_series(_weak_management())
        assert r.score <= 50, f"Expected score ≤50 for weak management, got {r.score}"
        assert r.rating in ("fair", "poor"), f"Expected fair/poor, got {r.rating}"

    def test_strong_beats_weak(self):
        strong = management_quality_score_from_series(_strong_management())
        weak = management_quality_score_from_series(_weak_management())
        assert strong.score > weak.score

    def test_fewer_than_3_years_raises(self):
        with pytest.raises(ValueError, match="at least 3 years"):
            management_quality_score_from_series(_strong_management()[:2])

    def test_declining_shares_raises_shareholder_orientation_score(self):
        # Declining shares (buybacks)
        buyback_data = [_base_record(y, (1000 - y * 30) * 1e6) for y in range(4)]
        # Diluting shares
        dilution_data = [_base_record(y, (1000 + y * 40) * 1e6) for y in range(4)]
        r_buy = management_quality_score_from_series(buyback_data)
        r_dil = management_quality_score_from_series(dilution_data)
        assert r_buy.components.shareholder_orientation > r_dil.components.shareholder_orientation

    def test_improving_margins_raises_margin_stability_score(self):
        # Expanding margins
        improving = [
            dict(_base_record(y, 800e6), ebit=(8 + y * 2) * 1e9)
            for y in range(4)
        ]
        # Contracting margins
        contracting = [
            dict(_base_record(y, 800e6), ebit=(14 - y * 2) * 1e9)
            for y in range(4)
        ]
        r_imp = management_quality_score_from_series(improving)
        r_con = management_quality_score_from_series(contracting)
        assert r_imp.components.margin_stability >= r_con.components.margin_stability

    def test_returns_correct_type(self):
        r = management_quality_score_from_series(_strong_management())
        assert isinstance(r, ManagementScore)
        assert isinstance(r.components, ManagementComponents)

    def test_score_in_valid_range(self):
        for data in [_strong_management(), _weak_management()]:
            r = management_quality_score_from_series(data)
            assert 0 <= r.score <= 100

    def test_years_analyzed_matches_input(self):
        data = _strong_management()
        r = management_quality_score_from_series(data)
        assert r.years_analyzed == len(data)

    def test_to_dict_has_required_keys(self):
        r = management_quality_score_from_series(_strong_management())
        d = r.to_dict()
        for key in ("score", "rating", "components", "hurdle_rate_used",
                    "years_analyzed", "evidence", "interpretation"):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_components_has_all_signals(self):
        r = management_quality_score_from_series(_strong_management())
        d = r.to_dict()["components"]
        for key in ("roic_excellence", "margin_stability",
                    "shareholder_orientation", "revenue_execution"):
            assert key in d, f"Missing component: {key}"

    def test_table_is_non_empty_string(self):
        r = management_quality_score_from_series(_strong_management())
        t = r.table()
        assert isinstance(t, str)
        assert "Management Quality Score" in t
        assert "ROIC Excellence" in t

    def test_interpretation_is_non_empty(self):
        r = management_quality_score_from_series(_strong_management())
        assert isinstance(r.interpretation, str)
        assert len(r.interpretation) > 0
        assert str(r.score) in r.interpretation

    def test_evidence_list_non_empty(self):
        r = management_quality_score_from_series(_strong_management())
        assert len(r.evidence) >= 4

    def test_hurdle_rate_override(self):
        r = management_quality_score_from_series(_strong_management(), hurdle_rate=0.15)
        assert r.hurdle_rate_used == 0.15
