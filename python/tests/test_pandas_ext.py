"""Tests for ratios_from_df (pandas + polars support)."""
import pytest

pandas = pytest.importorskip("pandas")
pd = pandas

from fin_ratios.pandas_ext import ratios_from_df, check_columns  # noqa: E402

_BASE = {
    "revenue":          400e9,
    "gross_profit":     170e9,
    "ebit":             110e9,
    "net_income":       97e9,
    "total_assets":     352e9,
    "total_equity":     74e9,
    "total_debt":       111e9,
    "current_assets":   135e9,
    "current_liabilities": 145e9,
    "cash":             62e9,
    "operating_cash_flow": 114e9,
    "capex":            11e9,
    "accounts_receivable": 29e9,
    "inventory":        7e9,
    "cogs":             230e9,
    "accounts_payable": 62e9,
    "interest_expense": 3e9,
    "ebt":              126e9,
    "income_tax_expense": 29e9,
}


# ── pandas tests ─────────────────────────────────────────────────────────────

class TestPandas:
    def _df(self, rows=None):
        return pd.DataFrame(rows or [_BASE])

    def test_gross_margin(self):
        r = ratios_from_df(self._df(), ratios=["gross_margin"])
        assert abs(r["gross_margin"].iloc[0] - 170e9 / 400e9) < 1e-9

    def test_roe(self):
        r = ratios_from_df(self._df(), ratios=["roe"])
        assert abs(r["roe"].iloc[0] - 97e9 / 74e9) < 1e-9

    def test_roa(self):
        r = ratios_from_df(self._df(), ratios=["roa"])
        assert abs(r["roa"].iloc[0] - 97e9 / 352e9) < 1e-9

    def test_current_ratio(self):
        r = ratios_from_df(self._df(), ratios=["current_ratio"])
        assert abs(r["current_ratio"].iloc[0] - 135e9 / 145e9) < 1e-9

    def test_free_cash_flow(self):
        r = ratios_from_df(self._df(), ratios=["free_cash_flow"])
        assert abs(r["free_cash_flow"].iloc[0] - (114e9 - 11e9)) < 1e-6

    def test_all_metrics_no_error(self):
        r = ratios_from_df(self._df())
        assert len(r.columns) > 10

    def test_groupby(self):
        rows = [
            {"ticker": "AAPL", **_BASE},
            {"ticker": "MSFT", **_BASE, "revenue": 230e9, "gross_profit": 160e9},
        ]
        r = ratios_from_df(pd.DataFrame(rows), ratios=["gross_margin"], groupby="ticker")
        assert set(r["ticker"]) == {"AAPL", "MSFT"}
        aapl = r[r["ticker"] == "AAPL"]["gross_margin"].iloc[0]
        msft = r[r["ticker"] == "MSFT"]["gross_margin"].iloc[0]
        assert abs(aapl - 170e9 / 400e9) < 1e-9
        assert abs(msft - 160e9 / 230e9) < 1e-6

    def test_inplace(self):
        df = self._df()
        result = ratios_from_df(df, ratios=["gross_margin"], inplace=True)
        assert "gross_margin" in result.columns
        assert result is df

    def test_column_alias_total_revenue(self):
        row = {**_BASE}
        row["total_revenue"] = row.pop("revenue")
        r = ratios_from_df(pd.DataFrame([row]), ratios=["gross_margin"])
        assert abs(r["gross_margin"].iloc[0] - 170e9 / 400e9) < 1e-9

    def test_missing_column_returns_none(self):
        r = ratios_from_df(pd.DataFrame([{"revenue": 100, "gross_profit": 40}]),
                           ratios=["roe"])
        assert r["roe"].iloc[0] is None or str(r["roe"].iloc[0]) == "None"


def test_check_columns_pandas():
    df = pd.DataFrame([_BASE])
    result = check_columns(df)
    assert "resolved" in result
    assert "revenue" in result["resolved"]
    assert "missing" in result


# ── polars tests ─────────────────────────────────────────────────────────────

polars = pytest.importorskip("polars")
pl = polars


class TestPolars:
    def _df(self, rows=None):
        return pl.DataFrame(rows or [_BASE])

    def test_gross_margin(self):
        r = ratios_from_df(self._df(), ratios=["gross_margin"])
        assert abs(r["gross_margin"][0] - 170e9 / 400e9) < 1e-9

    def test_roe(self):
        r = ratios_from_df(self._df(), ratios=["roe"])
        assert abs(r["roe"][0] - 97e9 / 74e9) < 1e-9

    def test_roa(self):
        r = ratios_from_df(self._df(), ratios=["roa"])
        assert abs(r["roa"][0] - 97e9 / 352e9) < 1e-9

    def test_current_ratio(self):
        r = ratios_from_df(self._df(), ratios=["current_ratio"])
        assert abs(r["current_ratio"][0] - 135e9 / 145e9) < 1e-9

    def test_free_cash_flow(self):
        r = ratios_from_df(self._df(), ratios=["free_cash_flow"])
        assert abs(r["free_cash_flow"][0] - (114e9 - 11e9)) < 1e-6

    def test_all_metrics_no_error(self):
        r = ratios_from_df(self._df())
        assert len(r.columns) > 10

    def test_groupby(self):
        rows = [
            {"ticker": "AAPL", **_BASE},
            {"ticker": "MSFT", **_BASE, "revenue": 230e9, "gross_profit": 160e9},
        ]
        r = ratios_from_df(pl.DataFrame(rows), ratios=["gross_margin"], groupby="ticker")
        assert set(r["ticker"].to_list()) == {"AAPL", "MSFT"}

    def test_inplace(self):
        df = self._df()
        result = ratios_from_df(df, ratios=["gross_margin"], inplace=True)
        assert "gross_margin" in result.columns

    def test_returns_polars_dataframe(self):
        r = ratios_from_df(self._df(), ratios=["gross_margin"])
        assert isinstance(r, pl.DataFrame)

    def test_multiple_rows(self):
        rows = [_BASE, {**_BASE, "revenue": 200e9, "gross_profit": 80e9}]
        r = ratios_from_df(pl.DataFrame(rows), ratios=["gross_margin"])
        assert len(r) == 2
        assert abs(r["gross_margin"][0] - 170e9 / 400e9) < 1e-9
        assert abs(r["gross_margin"][1] - 80e9 / 200e9) < 1e-9


def test_check_columns_polars():
    df = pl.DataFrame([_BASE])
    result = check_columns(df)
    assert "resolved" in result
    assert "revenue" in result["resolved"]
