"""Tests for Dividend Safety Score."""
import pytest
from fin_ratios.utils.dividend_score import (
    dividend_safety_score_from_series,
    DividendSafetyScore,
    DividendComponents,
)


# ── Synthetic datasets ──────────────────────────────────────────────────────────

def _safe_dividend_payer():
    """Low FCF payout (<40%), low earnings payout, minimal debt, 6+ year streak."""
    return [
        {
            "year": y,
            "revenue":             (60 + y * 5) * 1e9,
            "ebit":                (15 + y * 1) * 1e9,
            "net_income":          (10 + y * 0.8) * 1e9,
            "total_assets":         90e9,
            "total_equity":         55e9,
            "total_debt":            8e9,   # low debt
            "cash":                  6e9,
            "capex":                 3e9,
            "depreciation":          4e9,
            "income_tax_expense":    3e9,
            "ebt":                  13e9,
            "operating_cash_flow":  (18 + y * 0.8) * 1e9,
            # dividends ~15% of FCF — very safe
            "dividends_paid":        2.2e9,
            "shares_outstanding":   500e6,
            "interest_expense":      0.3e9,
        }
        for y in range(7)
    ]


def _risky_dividend_payer():
    """High FCF payout (>90%), high debt, dividend cut in most recent year."""
    base_divs = [3e9, 3.2e9, 3.4e9, 3.6e9, 3.8e9, 2.0e9]  # cut in final year
    return [
        {
            "year": y,
            "revenue":             (40 + y * 1) * 1e9,
            "ebit":                 4e9,
            "net_income":           2.5e9,
            "total_assets":        150e9,
            "total_equity":         20e9,
            "total_debt":           80e9,   # very high debt
            "cash":                  3e9,
            "capex":                 8e9,
            "depreciation":          6e9,
            "income_tax_expense":    0.5e9,
            "ebt":                   1.5e9,
            "operating_cash_flow":   5e9,   # FCF = 5 - 8 = -3 → penalised
            "dividends_paid":        base_divs[y],
            "shares_outstanding":   300e6,
            "interest_expense":      4.5e9,
        }
        for y in range(6)
    ]


def _non_payer():
    """Company that has never paid dividends."""
    return [
        {
            "year": y,
            "revenue":             (50 + y * 8) * 1e9,
            "ebit":                (12 + y * 1) * 1e9,
            "net_income":          (8  + y * 0.8) * 1e9,
            "total_assets":         70e9,
            "total_equity":         45e9,
            "total_debt":           10e9,
            "cash":                  8e9,
            "capex":                 4e9,
            "depreciation":          5e9,
            "income_tax_expense":    2.5e9,
            "ebt":                  11e9,
            "operating_cash_flow":  15e9,
            "dividends_paid":        0.0,
            "shares_outstanding":   400e6,
            "interest_expense":      0.4e9,
        }
        for y in range(5)
    ]


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestDividendSafetyRatings:

    def test_safe_dividend_score_and_rating(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        assert r.score >= 70, f"Expected score ≥70 for safe dividend, got {r.score}"
        assert r.rating == "safe"

    def test_risky_dividend_score_and_rating(self):
        r = dividend_safety_score_from_series(_risky_dividend_payer())
        assert r.score <= 45, f"Expected score ≤45 for risky dividend, got {r.score}"
        assert r.rating in ("risky", "danger", "adequate")

    def test_non_payer_rating_and_flag(self):
        r = dividend_safety_score_from_series(_non_payer())
        assert r.rating == "non-payer"
        assert r.is_dividend_payer is False
        assert r.score == 50

    def test_payer_flag_true_when_dividends_present(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        assert r.is_dividend_payer is True

    def test_safe_beats_risky(self):
        safe = dividend_safety_score_from_series(_safe_dividend_payer())
        risky = dividend_safety_score_from_series(_risky_dividend_payer())
        assert safe.score > risky.score

    def test_fewer_than_2_years_raises(self):
        with pytest.raises(ValueError, match="at least 2 years"):
            dividend_safety_score_from_series([_safe_dividend_payer()[0]])

    def test_score_in_valid_range(self):
        for data in [_safe_dividend_payer(), _risky_dividend_payer(), _non_payer()]:
            r = dividend_safety_score_from_series(data)
            assert 0 <= r.score <= 100

    def test_to_dict_has_is_dividend_payer_key(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        d = r.to_dict()
        assert "is_dividend_payer" in d

    def test_to_dict_has_all_required_keys(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        d = r.to_dict()
        for key in ("score", "rating", "components", "years_analyzed",
                    "is_dividend_payer", "evidence", "interpretation"):
            assert key in d, f"Missing key: {key}"

    def test_table_is_non_empty_string(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        t = r.table()
        assert isinstance(t, str)
        assert len(t) > 0
        assert "Dividend Safety Score" in t

    def test_returns_correct_type(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        assert isinstance(r, DividendSafetyScore)
        assert isinstance(r.components, DividendComponents)

    def test_components_in_unit_range(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        c = r.components
        for val in (c.fcf_payout_ratio, c.earnings_payout_ratio,
                    c.balance_sheet_strength, c.dividend_growth_track):
            assert 0.0 <= val <= 1.0, f"Component {val} out of [0, 1]"

    def test_non_payer_to_dict_has_flag(self):
        r = dividend_safety_score_from_series(_non_payer())
        d = r.to_dict()
        assert d["is_dividend_payer"] is False
        assert d["rating"] == "non-payer"

    def test_evidence_non_empty_for_payer(self):
        r = dividend_safety_score_from_series(_safe_dividend_payer())
        assert len(r.evidence) >= 1
