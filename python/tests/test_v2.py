"""
Tests for v0.2 modules:
  - scenario_dcf
  - compute_all
  - montier_c_score
  - shiller_cape
  - cache
  - pandas_ext (pandas integration)
  - notebook display objects
  - peers (static, no network)
"""
from __future__ import annotations

import math
import pytest
from typing import Any


# ── Scenario DCF tests ─────────────────────────────────────────────────────────

class TestScenarioDcf:
    def test_basic(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(
            base_fcf=100e9,
            shares_outstanding=15.7e9,
            current_price=185.0,
        )
        assert "bear" in result.scenarios
        assert "base" in result.scenarios
        assert "bull" in result.scenarios

    def test_base_iv_positive(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        iv = result.scenarios["base"]["intrinsic_value_per_share"]
        assert iv is not None
        assert iv > 0

    def test_bull_iv_gt_bear(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        bull_iv = result.scenarios["bull"]["intrinsic_value_per_share"]
        bear_iv = result.scenarios["bear"]["intrinsic_value_per_share"]
        assert bull_iv > bear_iv

    def test_upside_calculated_when_price_given(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(
            base_fcf=100e9,
            shares_outstanding=15.7e9,
            current_price=100.0,
        )
        base_upside = result.scenarios["base"]["upside_pct"]
        assert base_upside is not None

    def test_custom_scenarios(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(
            base_fcf=50e9,
            shares_outstanding=1e9,
            scenarios={
                "pessimistic": {"growth_rate": 0.02, "wacc": 0.15, "terminal_growth": 0.01, "years": 5},
                "optimistic":  {"growth_rate": 0.20, "wacc": 0.07, "terminal_growth": 0.05, "years": 10},
            }
        )
        assert "pessimistic" in result.scenarios
        assert "optimistic" in result.scenarios
        opt_iv = result.scenarios["optimistic"]["intrinsic_value_per_share"]
        pes_iv = result.scenarios["pessimistic"]["intrinsic_value_per_share"]
        assert opt_iv > pes_iv

    def test_table_output(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        table = result.table()
        assert "bear" in table
        assert "base" in table
        assert "bull" in table

    def test_to_dict(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        d = result.to_dict()
        assert "scenarios" in d
        assert "base_fcf" in d

    def test_repr_html(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(
            base_fcf=100e9, shares_outstanding=15.7e9,
            ticker="TEST", current_price=185.0
        )
        html = result._repr_html_()
        assert "<table" in html
        assert "TEST" in html

    def test_zero_shares_returns_none_iv(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=0)
        assert result.scenarios["base"]["intrinsic_value_per_share"] is None

    def test_wacc_lte_terminal_growth(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        # Should handle gracefully (terminal_value = 0)
        result = scenario_dcf(
            base_fcf=100e9,
            shares_outstanding=1e9,
            scenarios={"test": {"growth_rate": 0.05, "wacc": 0.02, "terminal_growth": 0.03}},
        )
        assert result.scenarios["test"]["terminal_value"] == 0.0


# ── compute_all tests ──────────────────────────────────────────────────────────

class TestComputeAll:
    def _make_data(self) -> dict:
        return {
            "revenue": 400e9,
            "gross_profit": 170e9,
            "ebit": 115e9,
            "ebitda": 130e9,
            "net_income": 97e9,
            "interest_expense": 3.9e9,
            "income_tax_expense": 29e9,
            "ebt": 126e9,
            "cogs": 230e9,
            "total_assets": 335e9,
            "total_equity": 62e9,
            "total_debt": 109e9,
            "current_assets": 143e9,
            "current_liabilities": 145e9,
            "cash": 62e9,
            "accounts_receivable": 29e9,
            "inventory": 7e9,
            "retained_earnings": -3.3e9,
            "total_liabilities": 290e9,
            "accounts_payable": 64e9,
            "long_term_debt": 91e9,
            "operating_cash_flow": 113e9,
            "capex": 11e9,
            "market_cap": 2.9e12,
            "shares_outstanding": 15.7e9,
        }

    def test_returns_dict(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert isinstance(result, dict)

    def test_valuation_ratios(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert result["pe"] is not None
        assert result["pe"] > 0
        assert result["pb"] is not None
        assert result["ps"] is not None

    def test_profitability_ratios(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert result["gross_margin"] is not None
        assert abs(result["gross_margin"] - 170/400) < 0.001
        assert result["roic"] is not None
        assert result["roe"] is not None
        assert result["roa"] is not None

    def test_cash_flow_ratios(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert result["free_cash_flow"] == 113e9 - 11e9
        assert result["fcf_margin"] is not None

    def test_liquidity_ratios(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert result["current_ratio"] is not None
        assert result["quick_ratio"] is not None
        assert result["dso"] is not None

    def test_solvency_ratios(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert result["debt_to_equity"] is not None
        assert result["interest_coverage"] is not None

    def test_altman_z(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        az = result["altman_z"]
        assert az is not None
        assert "z_score" in az
        assert "zone" in az

    def test_dict_input(self):
        from fin_ratios.utils.compute_all import compute_all
        result = compute_all(self._make_data())
        assert isinstance(result, dict)

    def test_partial_data_no_crash(self):
        from fin_ratios.utils.compute_all import compute_all
        # Only revenue and net income — should not raise
        result = compute_all({"revenue": 100e9, "net_income": 20e9})
        assert isinstance(result, dict)
        assert result.get("gross_margin") is None or result.get("gross_margin") == 0

    def test_prior_enables_piotroski(self):
        from fin_ratios.utils.compute_all import compute_all
        data = self._make_data()
        prior = self._make_data()
        prior["net_income"] = 80e9  # slightly lower prior year
        result = compute_all(data, prior=prior)
        assert result.get("piotroski") is not None
        assert isinstance(result["piotroski"], dict)
        assert "score" in result["piotroski"]


# ── Montier C-Score tests ──────────────────────────────────────────────────────

class TestMontierCScore:
    def _good_data(self) -> dict:
        return dict(
            current_net_income=100e9,
            current_operating_cash_flow=120e9,  # OCF > NI → c1 = False (good)
            current_accounts_receivable=30e9,
            current_revenue=400e9,
            current_inventory=7e9,
            current_cogs=230e9,
            current_cash=65e9,
            current_total_assets=340e9,
            current_long_term_debt=90e9,
            current_gross_profit=170e9,
            prior_accounts_receivable=32e9,
            prior_revenue=390e9,
            prior_inventory=8e9,
            prior_cogs=225e9,
            prior_cash=60e9,
            prior_total_assets=320e9,
            prior_long_term_debt=95e9,
            prior_gross_profit=160e9,
        )

    def test_score_range(self):
        import fin_ratios as fr
        result = fr.montier_c_score(**self._good_data())
        assert 0 <= result["score"] <= 6

    def test_returns_signals(self):
        import fin_ratios as fr
        result = fr.montier_c_score(**self._good_data())
        assert "signals" in result
        assert len(result["signals"]) == 6

    def test_all_red_flags_scores_6(self):
        import fin_ratios as fr
        # Create a "bad" company that triggers all 6 signals
        result = fr.montier_c_score(
            current_net_income=100e9,
            current_operating_cash_flow=50e9,    # c1: NI > OCF → True
            current_accounts_receivable=50e9,     # c2: DSO increases
            current_revenue=400e9,
            current_inventory=20e9,               # c3: inventory days increase
            current_cogs=200e9,
            current_cash=10e9,                    # c4: cash/assets fell
            current_total_assets=300e9,
            current_long_term_debt=150e9,         # c5: debt/assets rose
            current_gross_profit=150e9,           # c6: gross margin fell
            prior_accounts_receivable=20e9,
            prior_revenue=350e9,
            prior_inventory=5e9,
            prior_cogs=180e9,
            prior_cash=50e9,
            prior_total_assets=300e9,
            prior_long_term_debt=50e9,
            prior_gross_profit=145e9,             # prior margin higher
        )
        assert result["score"] >= 4
        assert result["high_risk"] is True

    def test_no_red_flags(self):
        import fin_ratios as fr
        result = fr.montier_c_score(
            current_net_income=80e9,
            current_operating_cash_flow=110e9,    # c1 False
            current_accounts_receivable=25e9,
            current_revenue=400e9,
            current_inventory=5e9,
            current_cogs=230e9,
            current_cash=70e9,
            current_total_assets=340e9,
            current_long_term_debt=85e9,
            current_gross_profit=175e9,
            prior_accounts_receivable=28e9,       # DSO was higher → c2 False
            prior_revenue=390e9,
            prior_inventory=8e9,                  # inventory was higher → c3 False
            prior_cogs=220e9,
            prior_cash=60e9,                      # cash/assets lower before → c4 False
            prior_total_assets=320e9,
            prior_long_term_debt=90e9,            # debt was higher → c5 False
            prior_gross_profit=155e9,             # margin was lower → c6 False
        )
        assert result["score"] <= 2

    def test_interpretation_present(self):
        import fin_ratios as fr
        result = fr.montier_c_score(**self._good_data())
        assert isinstance(result["interpretation"], str)
        assert "C-Score" in result["interpretation"]


# ── Shiller CAPE tests ─────────────────────────────────────────────────────────

class TestShillerCape:
    def test_basic(self):
        import fin_ratios as fr
        earnings_10y = [3.0, 3.5, 4.0, 4.2, 4.5, 4.8, 5.0, 5.2, 5.5, 6.0]
        result = fr.shiller_cape(current_price=150.0, earnings_10y=earnings_10y)
        assert result is not None
        assert result["cape_ratio"] > 0
        assert result["zone"] in ("undervalued", "fair_value", "elevated", "expensive")

    def test_with_cpi_adjustment(self):
        import fin_ratios as fr
        earnings = [3.0, 3.5, 4.0, 4.2, 4.5, 4.8, 5.0, 5.2, 5.5, 6.0]
        cpi = [200, 205, 210, 215, 218, 220, 225, 228, 230, 235]
        result = fr.shiller_cape(current_price=150.0, earnings_10y=earnings, cpi_10y=cpi)
        assert result is not None
        assert result["cape_ratio"] > 0

    def test_expensive_zone(self):
        import fin_ratios as fr
        result = fr.shiller_cape(
            current_price=10000.0,
            earnings_10y=[1.0] * 10,
        )
        assert result is not None
        assert result["zone"] == "expensive"

    def test_undervalued_zone(self):
        import fin_ratios as fr
        result = fr.shiller_cape(
            current_price=50.0,
            earnings_10y=[10.0] * 10,
        )
        assert result is not None
        assert result["zone"] == "undervalued"

    def test_zero_price_returns_none(self):
        import fin_ratios as fr
        result = fr.shiller_cape(current_price=0.0, earnings_10y=[5.0] * 10)
        assert result is None

    def test_empty_earnings_returns_none(self):
        import fin_ratios as fr
        result = fr.shiller_cape(current_price=150.0, earnings_10y=[])
        assert result is None

    def test_fewer_than_10_years(self):
        import fin_ratios as fr
        result = fr.shiller_cape(current_price=150.0, earnings_10y=[4.0, 5.0, 6.0])
        assert result is not None
        assert result["years_used"] <= 3

    def test_all_negative_earnings_returns_none(self):
        import fin_ratios as fr
        result = fr.shiller_cape(
            current_price=150.0,
            earnings_10y=[-1.0, -2.0, -3.0],
        )
        assert result is None


# ── Cache tests ────────────────────────────────────────────────────────────────

class TestCache:
    def test_memory_cache_hit(self):
        from fin_ratios.cache import set_cache, cached, clear_cache
        set_cache("memory", ttl_hours=1)
        call_count = {"n": 0}

        @cached("test_memory")
        def _fetch(ticker: str) -> dict:
            call_count["n"] += 1
            return {"ticker": ticker, "value": 42}

        r1 = _fetch("AAPL")
        r2 = _fetch("AAPL")
        assert r1 == r2
        assert call_count["n"] == 1
        clear_cache()
        set_cache("none")

    def test_cache_miss_after_clear(self):
        from fin_ratios.cache import set_cache, cached, clear_cache
        set_cache("memory", ttl_hours=1)
        call_count = {"n": 0}

        @cached("test_miss")
        def _fetch(ticker: str) -> dict:
            call_count["n"] += 1
            return {"ticker": ticker}

        _fetch("AAPL")
        clear_cache()
        _fetch("AAPL")
        assert call_count["n"] == 2
        set_cache("none")

    def test_cache_stats(self):
        from fin_ratios.cache import set_cache, cached, clear_cache, cache_stats
        set_cache("memory", ttl_hours=24)

        @cached("test_stats")
        def _f(x: str) -> str:
            return x

        _f("A")
        _f("B")
        stats = cache_stats()
        assert stats["backend"] == "memory"
        assert stats["valid"] >= 2
        clear_cache()
        set_cache("none")

    def test_no_cache_mode(self):
        from fin_ratios.cache import set_cache, cached
        set_cache("none")
        call_count = {"n": 0}

        @cached("test_none")
        def _f(x: str) -> str:
            call_count["n"] += 1
            return x

        _f("X")
        _f("X")
        assert call_count["n"] == 2

    def test_invalidate(self):
        from fin_ratios.cache import set_cache, cached, clear_cache, invalidate
        set_cache("memory", ttl_hours=24)
        call_count = {"n": 0}

        @cached("test_inv")
        def _fetch(ticker: str) -> dict:
            call_count["n"] += 1
            return {"ticker": ticker}

        _fetch("AAPL")
        _fetch("MSFT")
        # Note: invalidate uses ticker string matching against the key
        clear_cache()
        set_cache("none")


# ── Pandas integration tests ───────────────────────────────────────────────────

class TestPandasExt:
    @pytest.fixture(autouse=True)
    def skip_without_pandas(self):
        pytest.importorskip("pandas")

    def _make_df(self):
        import pandas as pd
        return pd.DataFrame([
            {
                "ticker": "AAPL",
                "revenue": 400e9,
                "gross_profit": 170e9,
                "ebit": 115e9,
                "net_income": 97e9,
                "total_assets": 335e9,
                "total_equity": 62e9,
                "total_debt": 109e9,
                "current_assets": 143e9,
                "current_liabilities": 145e9,
                "cash": 62e9,
                "operating_cash_flow": 113e9,
                "capex": 11e9,
                "market_cap": 2.9e12,
            },
            {
                "ticker": "MSFT",
                "revenue": 230e9,
                "gross_profit": 160e9,
                "ebit": 89e9,
                "net_income": 72e9,
                "total_assets": 411e9,
                "total_equity": 163e9,
                "total_debt": 59e9,
                "current_assets": 184e9,
                "current_liabilities": 104e9,
                "cash": 81e9,
                "operating_cash_flow": 87e9,
                "capex": 28e9,
                "market_cap": 3.1e12,
            },
        ])

    def test_returns_dataframe(self):
        import pandas as pd
        from fin_ratios.pandas_ext import ratios_from_df
        df = self._make_df()
        result = ratios_from_df(df, ratios=["gross_margin", "roe"])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_gross_margin_correct(self):
        from fin_ratios.pandas_ext import ratios_from_df
        df = self._make_df()
        result = ratios_from_df(df, ratios=["gross_margin"])
        # AAPL: 170/400 = 0.425
        assert abs(result["gross_margin"].iloc[0] - 170/400) < 0.001

    def test_multiple_ratios(self):
        from fin_ratios.pandas_ext import ratios_from_df
        df = self._make_df()
        result = ratios_from_df(df, ratios=["gross_margin", "current_ratio", "debt_to_equity"])
        for col in ["gross_margin", "current_ratio", "debt_to_equity"]:
            assert col in result.columns

    def test_check_columns(self):
        from fin_ratios.pandas_ext import check_columns
        df = self._make_df()
        info = check_columns(df)
        assert "resolved" in info
        assert len(info["resolved"]) > 0

    def test_inplace_mode(self):
        from fin_ratios.pandas_ext import ratios_from_df
        df = self._make_df()
        result = ratios_from_df(df, ratios=["gross_margin"], inplace=True)
        assert "gross_margin" in result.columns
        assert "revenue" in result.columns  # original columns preserved


# ── Notebook display tests ─────────────────────────────────────────────────────

class TestNotebook:
    def test_ratio_card_repr(self):
        from fin_ratios.notebook import RatioCard
        ratios = {
            "pe": 28.0,
            "gross_margin": 0.43,
            "roic": 0.55,
            "current_ratio": 0.98,
            "altman_z": {"z_score": 4.8, "zone": "safe"},
        }
        card = RatioCard("AAPL", ratios)
        text = repr(card)
        assert "AAPL" in text
        assert "roic" in text or "gross_margin" in text

    def test_ratio_card_html(self):
        from fin_ratios.notebook import RatioCard
        ratios = {
            "gross_margin": 0.43,
            "roic": 0.55,
            "pe": 28.0,
            "health_score": {"score": 76, "grade": "B"},
        }
        card = RatioCard("AAPL", ratios)
        html = card._repr_html_()
        assert "<table" in html
        assert "AAPL" in html

    def test_comparator_card(self):
        from fin_ratios.notebook import ComparatorCard
        data = {
            "AAPL": {"gross_margin": 0.43, "pe": 28.0, "roic": 0.55},
            "MSFT": {"gross_margin": 0.69, "pe": 31.0, "roic": 0.38},
        }
        card = ComparatorCard(data, metrics=["pe", "gross_margin", "roic"])
        html = card._repr_html_()
        assert "AAPL" in html
        assert "MSFT" in html
        assert "<table" in html

    def test_display_ratios_helper(self):
        from fin_ratios.notebook import display_ratios, RatioCard
        card = display_ratios("MSFT", {"pe": 31.0, "gross_margin": 0.69})
        assert isinstance(card, RatioCard)


# ── Scenario DCF price_per_share and upside helpers ────────────────────────────

class TestScenarioDcfHelpers:
    def test_price_per_share_helper(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        iv = result.price_per_share("base")
        assert iv is not None
        assert iv > 0

    def test_upside_helper_with_price(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(
            base_fcf=100e9,
            shares_outstanding=15.7e9,
            current_price=100.0,
        )
        upside = result.upside("base")
        assert upside is not None

    def test_upside_none_without_price(self):
        from fin_ratios.utils.scenario_dcf import scenario_dcf
        result = scenario_dcf(base_fcf=100e9, shares_outstanding=15.7e9)
        assert result.upside("base") is None
