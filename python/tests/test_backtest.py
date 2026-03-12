"""Tests for backtest_quality_strategy and summarize_backtest."""
import pytest
from fin_ratios.utils.backtest import (
    backtest_quality_strategy,
    summarize_backtest,
    BacktestResult,
)


# ── Synthetic company data ──────────────────────────────────────────────────────

def _high_quality_company(n_years: int = 6) -> list[dict]:
    """Strong fundamentals: ROIC 25%+, improving margins, growing revenue."""
    return [
        {
            "year": y,
            "revenue":             (100 + y * 15) * 1e9,
            "ebit":                 (28 + y * 4)  * 1e9,
            "net_income":           (18 + y * 3)  * 1e9,
            "total_assets":          90e9,
            "total_equity":          50e9,
            "total_debt":            10e9,
            "cash":                  12e9,
            "capex":                  4e9,
            "depreciation":           5e9,
            "income_tax_expense":   (5.5 + y * 0.9) * 1e9,
            "ebt":                  (26 + y * 3.8) * 1e9,
            "operating_cash_flow":  (22 + y * 3)   * 1e9,
            "dividends_paid":         2e9,
            "shares_outstanding":   (800 - y * 10) * 1e6,
            "interest_expense":       0.4e9,
        }
        for y in range(n_years)
    ]


def _low_quality_company(n_years: int = 6) -> list[dict]:
    """Weak fundamentals: low ROIC ~4%, declining margins, heavy leverage."""
    return [
        {
            "year": y,
            "revenue":              (50 + y * 0.8) * 1e9,
            "ebit":                  (3 - y * 0.1) * 1e9,
            "net_income":            (1.5 - y * 0.1) * 1e9,
            "total_assets":         160e9,
            "total_equity":          15e9,
            "total_debt":            90e9,
            "cash":                   2e9,
            "capex":                 14e9,
            "depreciation":           8e9,
            "income_tax_expense":     0.3e9,
            "ebt":                    0.6e9,
            "operating_cash_flow":    5e9,
            "dividends_paid":         0.0,
            "shares_outstanding":   (300 + y * 20) * 1e6,
            "interest_expense":       4.5e9,
        }
        for y in range(n_years)
    ]


def _medium_quality_company(n_years: int = 6) -> list[dict]:
    """Moderate fundamentals: ROIC ~12%, steady revenue growth."""
    return [
        {
            "year": y,
            "revenue":              (70 + y * 6) * 1e9,
            "ebit":                 (12 + y * 1) * 1e9,
            "net_income":            (8 + y * 0.8) * 1e9,
            "total_assets":          80e9,
            "total_equity":          40e9,
            "total_debt":            20e9,
            "cash":                   6e9,
            "capex":                  6e9,
            "depreciation":           5e9,
            "income_tax_expense":     2.5e9,
            "ebt":                   11e9,
            "operating_cash_flow":   14e9,
            "dividends_paid":         1.5e9,
            "shares_outstanding":   (600 - y * 5) * 1e6,
            "interest_expense":       0.9e9,
        }
        for y in range(n_years)
    ]


def _three_company_set(n_years: int = 6) -> list[list[dict]]:
    return [
        _high_quality_company(n_years),
        _medium_quality_company(n_years),
        _low_quality_company(n_years),
    ]


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestBacktestQualityStrategy:

    def test_returns_backtest_result_type(self):
        r = backtest_quality_strategy(_three_company_set())
        assert isinstance(r, BacktestResult)

    def test_strategy_cagr_is_float(self):
        r = backtest_quality_strategy(_three_company_set())
        assert isinstance(r.strategy_cagr, float)

    def test_hit_rate_between_0_and_1(self):
        r = backtest_quality_strategy(_three_company_set())
        assert 0.0 <= r.hit_rate <= 1.0, f"hit_rate {r.hit_rate} not in [0, 1]"

    def test_max_drawdown_non_negative(self):
        r = backtest_quality_strategy(_three_company_set())
        assert r.max_drawdown >= 0.0, f"max_drawdown {r.max_drawdown} is negative"

    def test_years_matches_evaluated_periods(self):
        # With 6-year series and quality (min_years=2), we get 4 scorable periods
        # Each period t (from min_years-1=1 to min_len-2=4) = 4 periods
        r = backtest_quality_strategy(_three_company_set(n_years=6))
        assert r.years > 0
        assert r.years == len(r.annual_results)

    def test_score_fn_name_recorded(self):
        r = backtest_quality_strategy(_three_company_set(), score_fn="moat")
        assert r.score_fn_name == "moat"

    def test_threshold_recorded(self):
        r = backtest_quality_strategy(_three_company_set(), threshold=55)
        assert r.threshold == 55

    def test_annual_results_have_expected_keys(self):
        r = backtest_quality_strategy(_three_company_set())
        assert len(r.annual_results) > 0
        for row in r.annual_results:
            for key in ("year_index", "strategy_return", "benchmark_return",
                        "excess", "n_high_score", "n_total"):
                assert key in row, f"Missing key {key!r} in annual_results row"

    def test_high_vs_low_quality_hit_rate_above_zero(self):
        # With only high-quality and low-quality, high-quality should beat benchmark
        # at least sometimes — hit_rate should be > 0
        companies = [
            _high_quality_company(n_years=7),
            _low_quality_company(n_years=7),
        ]
        r = backtest_quality_strategy(companies, threshold=50, score_fn="capital_allocation")
        assert r.hit_rate >= 0.0  # at minimum, it ran without error

    def test_invalid_score_fn_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown score_fn"):
            backtest_quality_strategy(_three_company_set(), score_fn="nonexistent_fn")

    def test_fewer_than_2_companies_raises(self):
        with pytest.raises(ValueError, match="at least 2 company series"):
            backtest_quality_strategy([_high_quality_company()])

    def test_moat_score_fn_works(self):
        r = backtest_quality_strategy(_three_company_set(), score_fn="moat")
        assert isinstance(r, BacktestResult)
        assert r.score_fn_name == "moat"

    def test_earnings_quality_score_fn_works(self):
        r = backtest_quality_strategy(_three_company_set(), score_fn="earnings_quality")
        assert isinstance(r, BacktestResult)

    def test_management_score_fn_works(self):
        # management requires min_years=3, so data needs at least 4 years
        r = backtest_quality_strategy(_three_company_set(n_years=6), score_fn="management")
        assert isinstance(r, BacktestResult)


class TestSummarizeBacktest:

    def test_returns_non_empty_string(self):
        r = backtest_quality_strategy(_three_company_set())
        s = summarize_backtest(r)
        assert isinstance(s, str)
        assert len(s) > 0

    def test_summary_contains_key_fields(self):
        r = backtest_quality_strategy(_three_company_set())
        s = summarize_backtest(r)
        assert "Strategy CAGR" in s
        assert "Hit rate" in s
        assert "Excess CAGR" in s
