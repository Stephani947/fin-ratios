"""Tests for Earnings Quality Score."""
import pytest
from fin_ratios.utils.earnings_quality import (
    earnings_quality_score_from_series,
    EarningsQualityScore,
    EarningsQualityComponents,
)


# ── Synthetic datasets ─────────────────────────────────────────────────────────

def _high_quality():
    """Cash-backed earnings, stable margins, growing efficiently."""
    return [
        {
            "year": y,
            "revenue":            (100 + y * 12) * 1e9,
            "gross_profit":       (65  + y * 8)  * 1e9,
            "net_income":         (18  + y * 2)  * 1e9,
            "operating_cash_flow": (22 + y * 2.5) * 1e9,   # CFO > NI
            "total_assets":       (80  + y * 6)   * 1e9,
            "accounts_receivable": (8  + y * 0.8) * 1e9,   # grows with revenue
        }
        for y in range(8)
    ]


def _poor_quality():
    """High accruals, CFO < NI, AR growing faster than revenue."""
    return [
        {
            "year": y,
            "revenue":            (80  + y * 3)   * 1e9,
            "gross_profit":       (28  + y * 0.5) * 1e9,
            "net_income":         (10  + y * 1)   * 1e9,
            "operating_cash_flow": (5  + y * 0.2) * 1e9,   # CFO << NI
            "total_assets":       (120 + y * 15)  * 1e9,
            "accounts_receivable": (15 + y * 3)   * 1e9,   # AR growing fast
        }
        for y in range(8)
    ]


def _moderate_quality():
    """Decent but not exceptional earnings quality."""
    return [
        {
            "year": y,
            "revenue":            (60  + y * 5)   * 1e9,
            "gross_profit":       (30  + y * 2.5) * 1e9,
            "net_income":         (8   + y * 0.7) * 1e9,
            "operating_cash_flow": (9  + y * 0.8) * 1e9,
            "total_assets":       (70  + y * 5)   * 1e9,
        }
        for y in range(6)
    ]


def _minimal_data():
    """Only required fields, no CFO or AR data."""
    return [
        {"revenue": 100e9, "gross_profit": 40e9, "net_income": 10e9, "total_assets": 80e9},
        {"revenue": 110e9, "gross_profit": 44e9, "net_income": 11e9, "total_assets": 85e9},
        {"revenue": 120e9, "gross_profit": 48e9, "net_income": 12e9, "total_assets": 90e9},
    ]


# ── Basic structural tests ────────────────────────────────────────────────────

class TestEarningsQualityBasic:

    def test_returns_correct_type(self):
        r = earnings_quality_score_from_series(_high_quality())
        assert isinstance(r, EarningsQualityScore)
        assert isinstance(r.components, EarningsQualityComponents)

    def test_score_in_valid_range(self):
        for dataset in [_high_quality(), _poor_quality(), _moderate_quality()]:
            r = earnings_quality_score_from_series(dataset)
            assert 0 <= r.score <= 100

    def test_rating_valid_values(self):
        for dataset in [_high_quality(), _poor_quality(), _moderate_quality()]:
            r = earnings_quality_score_from_series(dataset)
            assert r.rating in ("high", "medium", "low", "poor")

    def test_components_in_unit_range(self):
        r = earnings_quality_score_from_series(_high_quality())
        c = r.components
        for val in [
            c.accruals_ratio, c.cash_earnings, c.revenue_recognition,
            c.gross_margin_stability, c.asset_efficiency,
        ]:
            assert 0.0 <= val <= 1.0

    def test_minimum_years_raises(self):
        with pytest.raises(ValueError, match="at least 2 years"):
            earnings_quality_score_from_series([_high_quality()[0]])

    def test_years_analyzed(self):
        data = _high_quality()
        r = earnings_quality_score_from_series(data)
        assert r.years_analyzed == len(data)


# ── Score ordering tests ──────────────────────────────────────────────────────

class TestEarningsQualityScores:

    def test_high_beats_poor(self):
        high = earnings_quality_score_from_series(_high_quality())
        poor = earnings_quality_score_from_series(_poor_quality())
        assert high.score > poor.score

    def test_high_quality_scores_above_50(self):
        r = earnings_quality_score_from_series(_high_quality())
        assert r.score >= 50, f"Expected ≥50 for high-quality data, got {r.score}"

    def test_poor_quality_below_high_quality(self):
        high = earnings_quality_score_from_series(_high_quality())
        poor = earnings_quality_score_from_series(_poor_quality())
        assert poor.score < high.score


# ── Output / display tests ────────────────────────────────────────────────────

class TestEarningsQualityOutput:

    def test_evidence_non_empty(self):
        r = earnings_quality_score_from_series(_high_quality())
        assert len(r.evidence) >= 1

    def test_table_returns_string(self):
        r = earnings_quality_score_from_series(_high_quality())
        t = r.table()
        assert isinstance(t, str)
        assert "Earnings Quality Score" in t
        assert "Accruals Ratio" in t

    def test_repr_html(self):
        r = earnings_quality_score_from_series(_high_quality())
        html = r._repr_html_()
        assert "<div" in html
        assert str(r.score) in html

    def test_to_dict_keys(self):
        r = earnings_quality_score_from_series(_high_quality())
        d = r.to_dict()
        for key in ("score", "rating", "components", "evidence", "years_analyzed"):
            assert key in d

    def test_interpretation_contains_score(self):
        r = earnings_quality_score_from_series(_high_quality())
        assert str(r.score) in r.interpretation


# ── Edge case tests ───────────────────────────────────────────────────────────

class TestEarningsQualityEdgeCases:

    def test_works_with_two_years(self):
        r = earnings_quality_score_from_series(_high_quality()[:2])
        assert 0 <= r.score <= 100

    def test_works_without_cfo(self):
        r = earnings_quality_score_from_series(_minimal_data())
        assert 0 <= r.score <= 100

    def test_works_without_accounts_receivable(self):
        data = [
            {"revenue": 100e9, "gross_profit": 60e9, "net_income": 15e9,
             "operating_cash_flow": 18e9, "total_assets": 80e9},
            {"revenue": 115e9, "gross_profit": 69e9, "net_income": 17e9,
             "operating_cash_flow": 20e9, "total_assets": 85e9},
        ]
        r = earnings_quality_score_from_series(data)
        assert 0 <= r.score <= 100

    def test_top_level_import(self):
        from fin_ratios import earnings_quality_score_from_series as f
        from fin_ratios import EarningsQualityScore as C
        assert f is not None
        assert C is not None
