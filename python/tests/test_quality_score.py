"""Tests for Quality Factor Score and Portfolio Quality."""
import pytest
from fin_ratios.utils.quality_score import (
    quality_score_from_series,
    QualityFactorScore,
    QualityComponents,
)
from fin_ratios.utils.portfolio import (
    portfolio_quality_from_series,
    PortfolioQuality,
    HoldingQuality,
)


# ── Synthetic datasets ─────────────────────────────────────────────────────────

def _excellent_company():
    """High ROIC, cash-backed earnings, capital-light, stable margins."""
    return [
        {
            "year": y,
            "revenue":             (100 + y * 15) * 1e9,
            "gross_profit":        (65  + y * 10) * 1e9,
            "ebit":                (30  + y * 5)  * 1e9,
            "net_income":          (22  + y * 4)  * 1e9,
            "operating_cash_flow": (26  + y * 4.5) * 1e9,
            "total_equity":        40e9,
            "total_debt":          5e9,
            "total_assets":        (70  + y * 8)  * 1e9,
            "cash":                20e9,
            "capex":               2e9,
            "depreciation":        3e9,
            "interest_expense":    0.2e9,
            "income_tax_expense":  (6  + y * 1.2) * 1e9,
            "dividends_paid":      2e9,
            "accounts_receivable": (8  + y * 1)   * 1e9,
        }
        for y in range(8)
    ]


def _weak_company():
    """Low ROIC, high accruals, asset-heavy."""
    return [
        {
            "year": y,
            "revenue":             (80  + y * 2)   * 1e9,
            "gross_profit":        (20  + y * 0.3) * 1e9,
            "ebit":                (4   + y * 0.2) * 1e9,
            "net_income":          (5   + y * 0.3) * 1e9,
            "operating_cash_flow": (2   + y * 0.1) * 1e9,   # CFO << NI
            "total_equity":        30e9,
            "total_debt":          50e9,
            "total_assets":        (100 + y * 12)  * 1e9,
            "cash":                3e9,
            "capex":               15e9,
            "depreciation":        8e9,
            "interest_expense":    3.5e9,
            "income_tax_expense":  0.5e9,
            "accounts_receivable": (10  + y * 3)   * 1e9,   # AR growing fast
        }
        for y in range(8)
    ]


# ── Quality Score basic tests ─────────────────────────────────────────────────

class TestQualityScoreBasic:

    def test_returns_correct_type(self):
        r = quality_score_from_series(_excellent_company())
        assert isinstance(r, QualityFactorScore)
        assert isinstance(r.components, QualityComponents)

    def test_score_in_valid_range(self):
        for data in [_excellent_company(), _weak_company()]:
            r = quality_score_from_series(data)
            assert 0 <= r.score <= 100

    def test_grade_valid_values(self):
        for data in [_excellent_company(), _weak_company()]:
            r = quality_score_from_series(data)
            assert r.grade in ("exceptional", "strong", "moderate", "weak", "poor")

    def test_components_in_unit_range(self):
        r = quality_score_from_series(_excellent_company())
        c = r.components
        for val in [c.earnings_quality, c.moat, c.capital_allocation]:
            assert 0.0 <= val <= 1.0

    def test_minimum_years_raises(self):
        with pytest.raises(ValueError, match="at least 2 years"):
            quality_score_from_series([_excellent_company()[0]])

    def test_years_analyzed(self):
        data = _excellent_company()
        r = quality_score_from_series(data)
        assert r.years_analyzed == len(data)

    def test_wacc_override(self):
        r = quality_score_from_series(_excellent_company(), wacc=0.10)
        assert r.sub_scores["moat"].wacc_used == 0.10

    def test_excellent_beats_weak(self):
        exc = quality_score_from_series(_excellent_company())
        weak = quality_score_from_series(_weak_company())
        assert exc.score > weak.score


# ── Sub-scores drill-down ─────────────────────────────────────────────────────

class TestQualityScoreSubScores:

    def test_sub_scores_keys_present(self):
        r = quality_score_from_series(_excellent_company())
        assert "earnings_quality" in r.sub_scores
        assert "moat" in r.sub_scores
        assert "capital_allocation" in r.sub_scores

    def test_sub_scores_are_correct_types(self):
        from fin_ratios.utils.earnings_quality import EarningsQualityScore
        from fin_ratios.utils.moat_score import MoatScore
        from fin_ratios.utils.capital_allocation import CapitalAllocationScore
        r = quality_score_from_series(_excellent_company())
        assert isinstance(r.sub_scores["earnings_quality"], EarningsQualityScore)
        assert isinstance(r.sub_scores["moat"], MoatScore)
        assert isinstance(r.sub_scores["capital_allocation"], CapitalAllocationScore)


# ── Output tests ──────────────────────────────────────────────────────────────

class TestQualityScoreOutput:

    def test_evidence_non_empty(self):
        r = quality_score_from_series(_excellent_company())
        assert len(r.evidence) >= 3

    def test_table_contains_all_dimensions(self):
        r = quality_score_from_series(_excellent_company())
        t = r.table()
        assert "Earnings Quality" in t
        assert "Economic Moat" in t
        assert "Capital Allocation" in t

    def test_repr_html(self):
        r = quality_score_from_series(_excellent_company())
        html = r._repr_html_()
        assert "<div" in html
        assert str(r.score) in html

    def test_to_dict_keys(self):
        r = quality_score_from_series(_excellent_company())
        d = r.to_dict()
        for key in ("score", "grade", "components", "sub_scores",
                    "evidence", "years_analyzed"):
            assert key in d

    def test_interpretation_contains_grade(self):
        r = quality_score_from_series(_excellent_company())
        assert r.grade.upper() in r.interpretation

    def test_top_level_import(self):
        from fin_ratios import quality_score_from_series as f
        from fin_ratios import QualityFactorScore as C
        assert f is not None
        assert C is not None


# ── Portfolio tests ───────────────────────────────────────────────────────────

class TestPortfolioQuality:

    def _portfolio_data(self):
        return {
            "GOOD":  (0.60, _excellent_company()),
            "WEAK":  (0.40, _weak_company()),
        }

    def test_returns_correct_type(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        assert isinstance(r, PortfolioQuality)

    def test_score_in_valid_range(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        assert 0 <= r.weighted_quality_score <= 100

    def test_grade_valid(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        assert r.grade in ("exceptional", "strong", "moderate", "weak", "poor")

    def test_holdings_count(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        assert len(r.holdings) == 2

    def test_weights_normalised(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        total = sum(h.weight for h in r.holdings)
        assert abs(total - 1.0) < 1e-9

    def test_weighted_score_between_components(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        scores = [h.quality.score for h in r.holdings if h.quality]
        assert min(scores) <= r.weighted_quality_score <= max(scores)

    def test_table_returns_string(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        t = r.table()
        assert isinstance(t, str)
        assert "Portfolio Quality" in t

    def test_repr_html(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        html = r._repr_html_()
        assert "<div" in html

    def test_to_dict_keys(self):
        r = portfolio_quality_from_series(self._portfolio_data())
        d = r.to_dict()
        for key in ("weighted_quality_score", "grade", "holdings", "effective_weight"):
            assert key in d

    def test_empty_holdings_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            portfolio_quality_from_series({})

    def test_error_holding_excluded_from_avg(self):
        """A holding that errors out should be excluded from weighted average."""
        bad_data: list = [{"revenue": 1}]  # insufficient years
        good_data = _excellent_company()
        holdings = {
            "GOOD": (0.50, good_data),
            "BAD":  (0.50, bad_data),
        }
        r = portfolio_quality_from_series(holdings)
        assert len(r.errors) >= 1
        assert r.effective_weight < 1.0

    def test_top_level_portfolio_import(self):
        from fin_ratios import portfolio_quality_from_series as f
        from fin_ratios import PortfolioQuality as C
        assert f is not None
        assert C is not None
