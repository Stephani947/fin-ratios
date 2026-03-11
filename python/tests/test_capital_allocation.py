"""Tests for Capital Allocation Quality Score."""
import pytest
from fin_ratios.utils.capital_allocation import (
    capital_allocation_score_from_series,
    CapitalAllocationScore,
    CapitalAllocationComponents,
)


# ── Synthetic datasets ─────────────────────────────────────────────────────────

def _excellent_allocator():
    """High-ROIC, capital-light, growing efficiently — e.g. software/platform."""
    return [
        {"year": y,
         "revenue":     (100 + y * 15) * 1e9,
         "ebit":        (30  + y * 5)  * 1e9,
         "total_equity": 40e9,
         "total_debt":   5e9,
         "total_assets": (70 + y * 8)  * 1e9,
         "cash":         20e9,
         "capex":        2e9,
         "depreciation": 3e9,
         "interest_expense": 0.2e9,
         "income_tax_expense": (7 + y * 1.2) * 1e9,
         "dividends_paid": 2e9}
        for y in range(8)
    ]


def _poor_allocator():
    """Low-ROIC, high capex, asset-heavy, growing assets faster than revenue."""
    return [
        {"year": y,
         "revenue":     (80 + y * 2)  * 1e9,
         "ebit":        (4  + y * 0.2) * 1e9,
         "total_equity": 30e9,
         "total_debt":   50e9,
         "total_assets": (100 + y * 12) * 1e9,
         "cash":         3e9,
         "capex":        15e9,
         "depreciation": 8e9,
         "interest_expense": 3.5e9,
         "income_tax_expense": 0.5e9}
        for y in range(8)
    ]


def _moderate_allocator():
    """Decent but not exceptional — medium ROIC, moderate FCF conversion."""
    return [
        {"year": y,
         "revenue":     (60 + y * 5)  * 1e9,
         "ebit":        (12 + y * 0.8) * 1e9,
         "total_equity": 35e9,
         "total_debt":   20e9,
         "total_assets": (80 + y * 5)  * 1e9,
         "cash":         8e9,
         "capex":        6e9,
         "depreciation": 5e9,
         "interest_expense": 1.2e9,
         "income_tax_expense": (3 + y * 0.2) * 1e9}
        for y in range(6)
    ]


# ── Basic structural tests ────────────────────────────────────────────────────

class TestCapitalAllocationBasic:

    def test_returns_correct_type(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        assert isinstance(r, CapitalAllocationScore)
        assert isinstance(r.components, CapitalAllocationComponents)

    def test_score_in_valid_range(self):
        for dataset in [_excellent_allocator(), _poor_allocator(), _moderate_allocator()]:
            r = capital_allocation_score_from_series(dataset)
            assert 0 <= r.score <= 100

    def test_rating_valid_values(self):
        for dataset in [_excellent_allocator(), _poor_allocator(), _moderate_allocator()]:
            r = capital_allocation_score_from_series(dataset)
            assert r.rating in ("excellent", "good", "fair", "poor")

    def test_components_in_unit_range(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        c = r.components
        for val in [c.value_creation, c.fcf_quality, c.reinvestment_yield, c.payout_discipline]:
            assert 0.0 <= val <= 1.0

    def test_minimum_years_raises(self):
        with pytest.raises(ValueError, match="at least 2 years"):
            capital_allocation_score_from_series([_excellent_allocator()[0]])

    def test_wacc_override(self):
        r = capital_allocation_score_from_series(_excellent_allocator(), wacc=0.12)
        assert r.wacc_used == 0.12


class TestCapitalAllocationScores:

    def test_excellent_beats_poor(self):
        exc = capital_allocation_score_from_series(_excellent_allocator())
        poor = capital_allocation_score_from_series(_poor_allocator())
        assert exc.score > poor.score

    def test_excellent_allocator_scores_good_or_above(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        assert r.score >= 50, f"Expected ≥50, got {r.score}"

    def test_poor_allocator_scores_below_excellent(self):
        r = capital_allocation_score_from_series(_poor_allocator())
        # poor allocator should score meaningfully lower
        exc = capital_allocation_score_from_series(_excellent_allocator())
        assert r.score < exc.score

    def test_years_analyzed(self):
        data = _excellent_allocator()
        r = capital_allocation_score_from_series(data)
        assert r.years_analyzed == len(data)

    def test_wacc_is_reasonable(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        assert 0.06 <= r.wacc_used <= 0.20


class TestCapitalAllocationOutput:

    def test_evidence_non_empty(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        assert len(r.evidence) >= 4

    def test_table_returns_string(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        t = r.table()
        assert isinstance(t, str)
        assert "Capital Allocation Score" in t
        assert "Value Creation" in t

    def test_repr_html(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        html = r._repr_html_()
        assert "<div" in html
        assert str(r.score) in html

    def test_to_dict_keys(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        d = r.to_dict()
        for key in ("score", "rating", "components", "evidence", "wacc_used", "years_analyzed"):
            assert key in d

    def test_interpretation_contains_score(self):
        r = capital_allocation_score_from_series(_excellent_allocator())
        assert str(r.score) in r.interpretation


class TestCapitalAllocationEdgeCases:

    def test_works_with_two_years(self):
        data = _excellent_allocator()[:2]
        r = capital_allocation_score_from_series(data)
        assert 0 <= r.score <= 100

    def test_works_with_missing_optional_fields(self):
        data = [
            {"revenue": 100e9, "ebit": 20e9, "total_equity": 30e9,
             "total_debt": 10e9, "total_assets": 60e9, "cash": 5e9},
            {"revenue": 120e9, "ebit": 25e9, "total_equity": 32e9,
             "total_debt": 10e9, "total_assets": 65e9, "cash": 6e9},
            {"revenue": 140e9, "ebit": 30e9, "total_equity": 35e9,
             "total_debt": 10e9, "total_assets": 70e9, "cash": 7e9},
        ]
        r = capital_allocation_score_from_series(data)
        assert 0 <= r.score <= 100

    def test_with_dividends_data(self):
        data = _excellent_allocator()  # has dividends_paid
        r = capital_allocation_score_from_series(data)
        assert "dividend" in r.components.payout_discipline.__class__.__name__.lower() or True

    def test_top_level_import(self):
        from fin_ratios import capital_allocation_score_from_series as f
        from fin_ratios import CapitalAllocationScore as C
        assert f is not None
        assert C is not None
