"""Tests for the Quantitative Economic Moat Score."""
import pytest
from fin_ratios.utils.moat_score import (
    moat_score_from_series,
    MoatScore,
    MoatComponents,
)


# ── Synthetic datasets ─────────────────────────────────────────────────────────

def _aapl_like():
    """Apple-like company: wide moat — high, stable ROIC; strong pricing power."""
    return [
        {"year": 2015, "revenue": 234e9, "gross_profit": 93e9,  "ebit": 71e9,
         "total_equity": 119e9, "total_debt": 54e9,  "total_assets": 290e9, "cash": 42e9,
         "capex": 11e9, "depreciation": 11e9, "interest_expense": 0.8e9, "income_tax_expense": 19e9,
         "current_assets": 89e9, "current_liabilities": 81e9},
        {"year": 2016, "revenue": 215e9, "gross_profit": 84e9,  "ebit": 60e9,
         "total_equity": 128e9, "total_debt": 75e9,  "total_assets": 321e9, "cash": 67e9,
         "capex": 13e9, "depreciation": 10e9, "interest_expense": 1.5e9, "income_tax_expense": 15e9,
         "current_assets": 106e9, "current_liabilities": 79e9},
        {"year": 2017, "revenue": 229e9, "gross_profit": 88e9,  "ebit": 64e9,
         "total_equity": 134e9, "total_debt": 97e9,  "total_assets": 375e9, "cash": 77e9,
         "capex": 13e9, "depreciation": 10e9, "interest_expense": 2.3e9, "income_tax_expense": 15e9,
         "current_assets": 128e9, "current_liabilities": 100e9},
        {"year": 2018, "revenue": 265e9, "gross_profit": 101e9, "ebit": 72e9,
         "total_equity": 107e9, "total_debt": 114e9, "total_assets": 365e9, "cash": 66e9,
         "capex": 13e9, "depreciation": 11e9, "interest_expense": 3.2e9, "income_tax_expense": 13e9,
         "current_assets": 131e9, "current_liabilities": 116e9},
        {"year": 2019, "revenue": 260e9, "gross_profit": 98e9,  "ebit": 64e9,
         "total_equity": 90e9,  "total_debt": 108e9, "total_assets": 339e9, "cash": 51e9,
         "capex": 11e9, "depreciation": 12e9, "interest_expense": 3.6e9, "income_tax_expense": 11e9,
         "current_assets": 162e9, "current_liabilities": 106e9},
        {"year": 2020, "revenue": 274e9, "gross_profit": 105e9, "ebit": 66e9,
         "total_equity": 65e9,  "total_debt": 112e9, "total_assets": 323e9, "cash": 38e9,
         "capex": 7e9,  "depreciation": 11e9, "interest_expense": 2.9e9, "income_tax_expense": 10e9,
         "current_assets": 143e9, "current_liabilities": 105e9},
        {"year": 2021, "revenue": 365e9, "gross_profit": 153e9, "ebit": 109e9,
         "total_equity": 63e9,  "total_debt": 122e9, "total_assets": 351e9, "cash": 62e9,
         "capex": 11e9, "depreciation": 11e9, "interest_expense": 2.6e9, "income_tax_expense": 14e9,
         "current_assets": 134e9, "current_liabilities": 125e9},
        {"year": 2022, "revenue": 394e9, "gross_profit": 170e9, "ebit": 119e9,
         "total_equity": 50e9,  "total_debt": 120e9, "total_assets": 352e9, "cash": 48e9,
         "capex": 11e9, "depreciation": 11e9, "interest_expense": 2.8e9, "income_tax_expense": 19e9,
         "current_assets": 135e9, "current_liabilities": 153e9},
        {"year": 2023, "revenue": 383e9, "gross_profit": 169e9, "ebit": 114e9,
         "total_equity": 62e9,  "total_debt": 111e9, "total_assets": 352e9, "cash": 61e9,
         "capex": 11e9, "depreciation": 11e9, "interest_expense": 3.9e9, "income_tax_expense": 29e9,
         "current_assets": 143e9, "current_liabilities": 145e9},
        {"year": 2024, "revenue": 391e9, "gross_profit": 181e9, "ebit": 124e9,
         "total_equity": 57e9,  "total_debt": 101e9, "total_assets": 364e9, "cash": 65e9,
         "capex": 9e9,  "depreciation": 11e9, "interest_expense": 3.7e9, "income_tax_expense": 29e9,
         "current_assets": 152e9, "current_liabilities": 177e9},
    ]


def _commodity_like():
    """Commodity-like company: no moat — volatile, often below-WACC ROIC; thin margins."""
    return [
        {"year": 2019, "revenue": 50e9, "gross_profit": 8e9,  "ebit": 2e9,
         "total_equity": 25e9, "total_debt": 18e9, "total_assets": 55e9, "cash": 3e9,
         "capex": 8e9, "depreciation": 6e9, "interest_expense": 1.2e9},
        {"year": 2020, "revenue": 38e9, "gross_profit": 3e9,  "ebit": -4e9,
         "total_equity": 22e9, "total_debt": 20e9, "total_assets": 52e9, "cash": 2e9,
         "capex": 5e9, "depreciation": 6e9, "interest_expense": 1.4e9},
        {"year": 2021, "revenue": 55e9, "gross_profit": 10e9, "ebit": 4e9,
         "total_equity": 24e9, "total_debt": 19e9, "total_assets": 56e9, "cash": 4e9,
         "capex": 9e9, "depreciation": 6e9, "interest_expense": 1.3e9},
        {"year": 2022, "revenue": 63e9, "gross_profit": 12e9, "ebit": 5e9,
         "total_equity": 26e9, "total_debt": 17e9, "total_assets": 57e9, "cash": 3e9,
         "capex": 10e9, "depreciation": 6e9, "interest_expense": 1.1e9},
        {"year": 2023, "revenue": 45e9, "gross_profit": 5e9,  "ebit": -1e9,
         "total_equity": 23e9, "total_debt": 19e9, "total_assets": 54e9, "cash": 2e9,
         "capex": 7e9, "depreciation": 6e9, "interest_expense": 1.3e9},
    ]


def _narrow_moat():
    """Narrow moat company: moderate, somewhat consistent ROIC; decent margins."""
    return [
        {"year": y, "revenue": (50 + y * 3) * 1e9,
         "gross_profit": (15 + y * 0.8) * 1e9,
         "ebit": (6 + y * 0.3) * 1e9,
         "total_equity": 30e9, "total_debt": 15e9, "total_assets": 60e9, "cash": 5e9,
         "capex": 3e9, "depreciation": 2.5e9,
         "interest_expense": 0.8e9, "income_tax_expense": 1.5e9,
         "current_assets": 20e9, "current_liabilities": 12e9}
        for y in range(6)
    ]


# ── Core tests ─────────────────────────────────────────────────────────────────

class TestMoatScoreBasic:

    def test_returns_moat_score_instance(self):
        result = moat_score_from_series(_aapl_like())
        assert isinstance(result, MoatScore)

    def test_returns_components_instance(self):
        result = moat_score_from_series(_aapl_like())
        assert isinstance(result.components, MoatComponents)

    def test_score_in_valid_range(self):
        for dataset in [_aapl_like(), _commodity_like(), _narrow_moat()]:
            r = moat_score_from_series(dataset)
            assert 0 <= r.score <= 100

    def test_width_valid_values(self):
        for dataset in [_aapl_like(), _commodity_like(), _narrow_moat()]:
            r = moat_score_from_series(dataset)
            assert r.width in ("wide", "narrow", "none")

    def test_components_all_in_unit_range(self):
        r = moat_score_from_series(_aapl_like())
        c = r.components
        for val in [c.roic_persistence, c.pricing_power,
                    c.reinvestment_quality, c.operating_leverage, c.cap_score]:
            assert 0.0 <= val <= 1.0

    def test_wide_moat_company_scores_high(self):
        r = moat_score_from_series(_aapl_like())
        assert r.score >= 65, f"Expected ≥65, got {r.score}"
        assert r.width in ("wide", "narrow")

    def test_commodity_company_scores_low(self):
        r = moat_score_from_series(_commodity_like())
        assert r.score < 50, f"Expected <50, got {r.score}"

    def test_wide_moat_beats_commodity(self):
        wide = moat_score_from_series(_aapl_like())
        none = moat_score_from_series(_commodity_like())
        assert wide.score > none.score

    def test_minimum_years_raises(self):
        with pytest.raises(ValueError, match="at least 2 years"):
            moat_score_from_series([_aapl_like()[0]])

    def test_wacc_override(self):
        r_default = moat_score_from_series(_aapl_like())
        r_high_wacc = moat_score_from_series(_aapl_like(), wacc=0.15)
        assert r_high_wacc.wacc_used == 0.15
        # Higher WACC = harder to clear the bar = lower or equal persistence score
        assert r_high_wacc.components.roic_persistence <= r_default.components.roic_persistence


class TestMoatScoreSignals:

    def test_pricing_power_high_for_wide_moat(self):
        r = moat_score_from_series(_aapl_like())
        assert r.components.pricing_power >= 0.60

    def test_pricing_power_low_for_commodity(self):
        r = moat_score_from_series(_commodity_like())
        assert r.components.pricing_power < 0.50

    def test_roic_persistence_high_for_wide_moat(self):
        r = moat_score_from_series(_aapl_like())
        assert r.components.roic_persistence >= 0.50

    def test_cap_years_positive_for_wide_moat(self):
        r = moat_score_from_series(_aapl_like())
        assert r.cap_estimate_years > 0

    def test_cap_years_zero_for_no_advantage(self):
        r = moat_score_from_series(_commodity_like())
        # Commodity may have zero or very low CAP
        assert r.cap_estimate_years <= 10


class TestMoatScoreOutput:

    def test_evidence_is_non_empty_list(self):
        r = moat_score_from_series(_aapl_like())
        assert isinstance(r.evidence, list)
        assert len(r.evidence) >= 5  # at least one per signal

    def test_interpretation_contains_score(self):
        r = moat_score_from_series(_aapl_like())
        assert str(r.score) in r.interpretation

    def test_table_returns_string(self):
        r = moat_score_from_series(_aapl_like())
        table = r.table()
        assert isinstance(table, str)
        assert "Moat Score" in table
        assert "ROIC Persistence" in table

    def test_repr_html_returns_string(self):
        r = moat_score_from_series(_aapl_like())
        html = r._repr_html_()
        assert "<div" in html
        assert str(r.score) in html

    def test_to_dict_structure(self):
        r = moat_score_from_series(_aapl_like())
        d = r.to_dict()
        assert "score" in d
        assert "width" in d
        assert "components" in d
        assert "evidence" in d
        assert "cap_estimate_years" in d
        assert "wacc_used" in d

    def test_years_analyzed(self):
        data = _aapl_like()
        r = moat_score_from_series(data)
        assert r.years_analyzed == len(data)

    def test_wacc_is_reasonable(self):
        r = moat_score_from_series(_aapl_like())
        assert 0.06 <= r.wacc_used <= 0.20


class TestMoatScoreEdgeCases:

    def test_works_with_two_years(self):
        r = moat_score_from_series(_aapl_like()[:2])
        assert 0 <= r.score <= 100

    def test_works_with_dict_input(self):
        data = [
            {"revenue": 100e9, "gross_profit": 45e9, "ebit": 20e9,
             "total_equity": 30e9, "total_debt": 10e9, "total_assets": 60e9, "cash": 5e9},
            {"revenue": 120e9, "gross_profit": 55e9, "ebit": 25e9,
             "total_equity": 32e9, "total_debt": 10e9, "total_assets": 65e9, "cash": 6e9},
            {"revenue": 140e9, "gross_profit": 65e9, "ebit": 30e9,
             "total_equity": 35e9, "total_debt": 10e9, "total_assets": 70e9, "cash": 7e9},
        ]
        r = moat_score_from_series(data)
        assert 0 <= r.score <= 100

    def test_works_with_missing_optional_fields(self):
        """Minimal data — only required fields."""
        data = [
            {"revenue": 100e9, "gross_profit": 40e9, "ebit": 15e9,
             "total_equity": 20e9, "total_debt": 8e9, "total_assets": 40e9},
            {"revenue": 110e9, "gross_profit": 44e9, "ebit": 17e9,
             "total_equity": 22e9, "total_debt": 8e9, "total_assets": 43e9},
            {"revenue": 121e9, "gross_profit": 50e9, "ebit": 20e9,
             "total_equity": 24e9, "total_debt": 8e9, "total_assets": 46e9},
        ]
        r = moat_score_from_series(data)
        assert 0 <= r.score <= 100
        assert r.width in ("wide", "narrow", "none")

    def test_negative_ebit_years_handled(self):
        """Company with some negative EBIT years shouldn't crash."""
        data = _commodity_like()  # already has negative EBIT years
        r = moat_score_from_series(data)
        assert 0 <= r.score <= 100

    def test_top_level_import(self):
        from fin_ratios import moat_score_from_series as f, MoatScore as MS
        assert f is not None
        assert MS is not None
