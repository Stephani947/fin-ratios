"""
Pandas / Polars DataFrame integration.

Compute financial ratios from a DataFrame with standardized column names.
Supports both Pandas and Polars (auto-detected at runtime).

Column name conventions (case-insensitive):
    revenue, gross_profit, ebit, ebitda, net_income, operating_cash_flow,
    capex, total_assets, total_equity, total_debt, current_assets,
    current_liabilities, cash, accounts_receivable, inventory, market_cap,
    shares_outstanding, interest_expense, accounts_payable, retained_earnings,
    total_liabilities, cogs, long_term_debt, income_tax_expense, ebt

Usage:
    from fin_ratios.pandas_ext import ratios_from_df

    df = pd.read_csv('financials.csv')
    ratios = ratios_from_df(df, ratios=['gross_margin', 'roic', 'current_ratio'])
    print(ratios.head())

    # Multi-company analysis (groupby ticker)
    ratios = ratios_from_df(df, ratios=['pe', 'roic'], groupby='ticker')

    # Polars works identically
    import polars as pl
    df = pl.read_csv('financials.csv')
    ratios = ratios_from_df(df, ratios=['gross_margin', 'roic'])
"""

from __future__ import annotations

from typing import Any, Optional


# ── Column aliases (maps common variations to canonical names) ────────────────

_ALIASES: dict[str, list[str]] = {
    "revenue": ["revenue", "total_revenue", "net_revenue", "sales"],
    "gross_profit": ["gross_profit", "gross_income"],
    "ebit": ["ebit", "operating_income", "operating_profit"],
    "ebitda": ["ebitda"],
    "net_income": ["net_income", "net_profit", "earnings", "net_earnings"],
    "operating_cash_flow": [
        "operating_cash_flow",
        "cash_from_operations",
        "cfo",
        "net_cash_from_operating_activities",
    ],
    "capex": ["capex", "capital_expenditures", "purchase_of_ppe", "capital_expenditure"],
    "total_assets": ["total_assets", "assets"],
    "total_equity": [
        "total_equity",
        "shareholders_equity",
        "total_stockholders_equity",
        "equity",
        "book_value",
    ],
    "total_debt": ["total_debt", "debt", "total_borrowings"],
    "current_assets": ["current_assets"],
    "current_liabilities": ["current_liabilities"],
    "cash": ["cash", "cash_and_equivalents", "cash_and_cash_equivalents"],
    "accounts_receivable": ["accounts_receivable", "receivables", "trade_receivables"],
    "inventory": ["inventory", "inventories"],
    "market_cap": ["market_cap", "market_capitalization"],
    "shares_outstanding": ["shares_outstanding", "diluted_shares", "weighted_avg_shares"],
    "interest_expense": ["interest_expense", "interest_paid"],
    "accounts_payable": ["accounts_payable", "trade_payables", "payables"],
    "retained_earnings": ["retained_earnings"],
    "total_liabilities": ["total_liabilities", "liabilities"],
    "cogs": ["cogs", "cost_of_goods_sold", "cost_of_revenue", "cost_of_sales"],
    "long_term_debt": ["long_term_debt", "long_term_borrowings"],
    "income_tax_expense": ["income_tax_expense", "tax_expense", "taxes"],
    "ebt": ["ebt", "pre_tax_income", "income_before_tax"],
    "enterprise_value": ["enterprise_value", "ev"],
    "eps_growth_pct": ["eps_growth_pct", "eps_growth", "earnings_growth"],
}


def _resolve_columns(df_cols: list[str]) -> dict[str, str]:
    """Map canonical field names to actual DataFrame column names."""
    cols_lower = {c.lower().strip(): c for c in df_cols}
    mapping: dict[str, str] = {}
    for canonical, aliases in _ALIASES.items():
        for alias in aliases:
            if alias in cols_lower:
                mapping[canonical] = cols_lower[alias]
                break
    return mapping


def _row_to_dict(row: Any, col_map: dict[str, str]) -> dict[str, float]:
    """Extract a single row into a canonical field dict."""
    d: dict[str, float] = {}
    for canonical, col in col_map.items():
        try:
            val = row[col]
            if val is not None and not _is_nan(val):
                d[canonical] = float(val)
        except (KeyError, TypeError, ValueError):
            pass
    return d


def _is_nan(v: Any) -> bool:
    try:
        import math

        return math.isnan(float(v))
    except (TypeError, ValueError):
        return False


# ── Ratio computation from a single row dict ──────────────────────────────────

_ALL_METRICS = [
    "pe",
    "pb",
    "ps",
    "peg",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "ebitda_margin",
    "roe",
    "roa",
    "roic",
    "roce",
    "fcf_margin",
    "fcf_conversion",
    "ocf_to_sales",
    "capex_to_revenue",
    "current_ratio",
    "quick_ratio",
    "debt_to_equity",
    "net_debt_to_equity",
    "net_debt_to_ebitda",
    "debt_to_assets",
    "interest_coverage",
    "asset_turnover",
    "receivables_turnover",
    "inventory_turnover",
    "dso",
    "dio",
    "dpo",
    "ev_ebitda",
    "tobin_q",
    "free_cash_flow",
    "fcf_yield",
]


def _compute_row(row_dict: dict[str, float], metrics: list[str]) -> dict[str, Optional[float]]:
    """Compute requested metrics from a row dict."""
    import fin_ratios as _fr
    from fin_ratios._utils import safe_divide

    d = row_dict
    g = d.get  # shorthand getter

    fcf = None
    if g("operating_cash_flow") is not None and g("capex") is not None:
        fcf = _fr.free_cash_flow(
            operating_cash_flow=g("operating_cash_flow", 0),
            capex=g("capex", 0),
        )

    ev = g("enterprise_value") or (
        (g("market_cap", 0) + g("total_debt", 0) - g("cash", 0)) if g("market_cap") else None
    )

    nopat_val = None
    ic_val = None
    if g("ebit") is not None and g("total_equity") is not None:
        tax_rate = safe_divide(g("income_tax_expense", 0), g("ebt", 0)) or 0.21
        tax_rate = min(max(tax_rate, 0), 0.5)
        nopat_val = _fr.nopat(ebit=g("ebit", 0), tax_rate=tax_rate)
        ic_val = _fr.invested_capital(
            total_equity=g("total_equity", 0),
            total_debt=g("total_debt", 0),
            cash=g("cash", 0),
        )

    _dispatch: dict[str, Any] = {
        "pe": lambda: _fr.pe(market_cap=g("market_cap", 0), net_income=g("net_income", 0)),
        "pb": lambda: _fr.pb(market_cap=g("market_cap", 0), total_equity=g("total_equity", 0)),
        "ps": lambda: _fr.ps(market_cap=g("market_cap", 0), revenue=g("revenue", 0)),
        "peg": lambda: (
            _fr.peg(
                pe_ratio=_fr.pe(market_cap=g("market_cap", 0), net_income=g("net_income", 0)),  # type: ignore[arg-type]
                eps_growth_rate_pct=g("eps_growth_pct", 0),
            )
            if g("eps_growth_pct") and g("market_cap")
            else None
        ),
        "ev_ebitda": lambda: (
            _fr.ev_ebitda(ev=ev, ebitda=g("ebitda", 0)) if ev and g("ebitda") else None
        ),
        "gross_margin": lambda: _fr.gross_margin(
            gross_profit=g("gross_profit", 0), revenue=g("revenue", 0)
        ),
        "operating_margin": lambda: _fr.operating_margin(
            ebit=g("ebit", 0), revenue=g("revenue", 0)
        ),
        "net_margin": lambda: _fr.net_profit_margin(
            net_income=g("net_income", 0), revenue=g("revenue", 0)
        ),
        "ebitda_margin": lambda: (
            _fr.ebitda_margin(ebitda=g("ebitda", 0), revenue=g("revenue", 0))
            if g("ebitda")
            else None
        ),
        "roe": lambda: _fr.roe(
            net_income=g("net_income", 0), avg_total_equity=g("total_equity", 0)
        ),
        "roa": lambda: _fr.roa(
            net_income=g("net_income", 0), avg_total_assets=g("total_assets", 0)
        ),
        "roic": lambda: (
            _fr.roic(nopat_value=nopat_val, invested_capital=ic_val)
            if nopat_val and ic_val
            else None
        ),
        "roce": lambda: _fr.roce(
            ebit=g("ebit", 0),
            total_assets=g("total_assets", 0),
            current_liabilities=g("current_liabilities", 0),
        ),
        "fcf_margin": lambda: _fr.fcf_margin(fcf=fcf, revenue=g("revenue", 0)) if fcf else None,
        "fcf_conversion": lambda: (
            _fr.fcf_conversion(fcf=fcf, net_income=g("net_income", 0)) if fcf else None
        ),
        "ocf_to_sales": lambda: _fr.ocf_to_sales(
            operating_cash_flow=g("operating_cash_flow", 0), revenue=g("revenue", 0)
        ),
        "capex_to_revenue": lambda: _fr.capex_to_revenue(
            capex=g("capex", 0), revenue=g("revenue", 0)
        ),
        "free_cash_flow": lambda: fcf,
        "fcf_yield": lambda: (
            _fr.fcf_yield(fcf=fcf, market_cap=g("market_cap", 0))
            if fcf and g("market_cap")
            else None
        ),
        "current_ratio": lambda: _fr.current_ratio(
            current_assets=g("current_assets", 0), current_liabilities=g("current_liabilities", 0)
        ),
        "quick_ratio": lambda: _fr.quick_ratio(
            cash=g("cash", 0),
            short_term_investments=0,
            accounts_receivable=g("accounts_receivable", 0),
            current_liabilities=g("current_liabilities", 0),
        ),
        "dso": lambda: _fr.dso(
            accounts_receivable=g("accounts_receivable", 0), revenue=g("revenue", 0)
        ),
        "dio": lambda: (
            _fr.dio(inventory=g("inventory", 0), cogs=g("cogs", 0)) if g("cogs") else None
        ),
        "dpo": lambda: (
            _fr.dpo(accounts_payable=g("accounts_payable", 0), cogs=g("cogs", 0))
            if g("cogs")
            else None
        ),
        "debt_to_equity": lambda: _fr.debt_to_equity(
            total_debt=g("total_debt", 0), total_equity=g("total_equity", 0)
        ),
        "net_debt_to_equity": lambda: _fr.net_debt_to_equity(
            total_debt=g("total_debt", 0), cash=g("cash", 0), total_equity=g("total_equity", 0)
        ),
        "net_debt_to_ebitda": lambda: (
            _fr.net_debt_to_ebitda(
                total_debt=g("total_debt", 0), cash=g("cash", 0), ebitda=g("ebitda", 0)
            )
            if g("ebitda")
            else None
        ),
        "debt_to_assets": lambda: _fr.debt_to_assets(
            total_debt=g("total_debt", 0), total_assets=g("total_assets", 0)
        ),
        "interest_coverage": lambda: _fr.interest_coverage_ratio(
            ebit=g("ebit", 0), interest_expense=g("interest_expense", 0)
        ),
        "asset_turnover": lambda: _fr.asset_turnover(
            revenue=g("revenue", 0), avg_total_assets=g("total_assets", 0)
        ),
        "receivables_turnover": lambda: _fr.receivables_turnover(
            revenue=g("revenue", 0), avg_accounts_receivable=g("accounts_receivable", 0)
        ),
        "inventory_turnover": lambda: (
            _fr.inventory_turnover(cogs=g("cogs", 0), avg_inventory=g("inventory", 0))
            if g("cogs")
            else None
        ),
        "tobin_q": lambda: _fr.tobin_q(
            market_cap=g("market_cap", 0),
            total_debt=g("total_debt", 0),
            total_assets=g("total_assets", 0),
        ),
    }

    result: dict[str, Optional[float]] = {}
    for m in metrics:
        fn = _dispatch.get(m)
        if fn is None:
            result[m] = None
            continue
        try:
            val = fn()
            result[m] = float(val) if val is not None else None
        except Exception:
            result[m] = None
    return result


# ── Main public API ────────────────────────────────────────────────────────────


def ratios_from_df(
    df: Any,
    ratios: Optional[list[str]] = None,
    groupby: Optional[str] = None,
    inplace: bool = False,
) -> Any:
    """
    Compute financial ratios from a DataFrame row by row.

    Supports both pandas.DataFrame and polars.DataFrame (auto-detected).
    Column names are resolved case-insensitively with common aliases.

    Args:
        df:       DataFrame with financial columns (see module docstring for names)
        ratios:   List of ratio names to compute. If None, computes all applicable.
        groupby:  Optional column name to group by (e.g. 'ticker'). When set,
                  uses the most recent row per group (no averaging).
        inplace:  If True, add ratio columns to the original DataFrame and return it.
                  If False (default), return a new DataFrame with only the ratio columns
                  (plus groupby column if specified).

    Returns:
        DataFrame with computed ratio columns.

    Example:
        df = pd.DataFrame({
            'ticker': ['AAPL', 'MSFT'],
            'revenue': [400e9, 230e9],
            'gross_profit': [170e9, 160e9],
            'net_income': [100e9, 72e9],
            'total_equity': [60e9, 160e9],
            'total_assets': [330e9, 410e9],
        })
        result = ratios_from_df(df, ratios=['gross_margin', 'roe', 'roa'])
        print(result)
    """
    if ratios is None:
        ratios = _ALL_METRICS

    # Detect library
    df_type = type(df).__module__.split(".")[0]
    is_polars = df_type == "polars"

    if is_polars:
        return _ratios_polars(df, ratios, groupby, inplace)
    else:
        return _ratios_pandas(df, ratios, groupby, inplace)


def _ratios_pandas(df: Any, ratios: list[str], groupby: Optional[str], inplace: bool) -> Any:
    import pandas as pd

    cols = list(df.columns)
    col_map = _resolve_columns(cols)

    def _process_group(sub_df: Any) -> Any:
        rows = []
        for _, row in sub_df.iterrows():
            row_d = _row_to_dict(row, col_map)
            ratio_vals = _compute_row(row_d, ratios)
            rows.append(ratio_vals)
        return pd.DataFrame(rows, index=sub_df.index)

    if groupby and groupby in df.columns:
        pieces = []
        for grp_key, grp_df in df.groupby(groupby, sort=False):
            ratio_df = _process_group(grp_df)
            ratio_df.insert(0, groupby, grp_key)
            pieces.append(ratio_df)
        ratio_frame = pd.concat(pieces)
    else:
        ratio_frame = _process_group(df)

    if inplace:
        for col in ratio_frame.columns:
            if col != groupby:
                df[col] = ratio_frame[col].values
        return df

    return ratio_frame


def _ratios_polars(df: Any, ratios: list[str], groupby: Optional[str], inplace: bool) -> Any:
    import polars as pl

    cols = [c for c in df.columns]
    col_map = _resolve_columns(cols)

    rows_out = []
    for row in df.iter_rows(named=True):
        row_d = {
            canonical: row[col]
            for canonical, col in col_map.items()
            if col in row and row[col] is not None
        }
        row_d_clean: dict[str, float] = {}
        for k, v in row_d.items():
            try:
                fv = float(v)
                if not _is_nan(fv):
                    row_d_clean[k] = fv
            except (TypeError, ValueError):
                pass

        ratio_vals = _compute_row(row_d_clean, ratios)
        if groupby and groupby in row:
            ratio_vals = {groupby: row[groupby], **ratio_vals}  # type: ignore[assignment]
        rows_out.append(ratio_vals)

    ratio_frame = pl.DataFrame(rows_out)

    if inplace:
        for col in ratio_frame.columns:
            if col != groupby:
                df = df.with_columns(ratio_frame[col].alias(col))
        return df

    return ratio_frame


# ── Convenience: column name checker ──────────────────────────────────────────


def check_columns(df: Any) -> dict:
    """
    Check which canonical columns were resolved from a DataFrame.

    Useful for debugging column mapping issues.

    Returns dict of {canonical_name: matched_column_name}.
    """
    try:
        cols = list(df.columns)
    except AttributeError:
        return {}
    resolved = _resolve_columns(cols)
    missing = [k for k in _ALIASES if k not in resolved]
    return {
        "resolved": resolved,
        "missing": missing,
        "note": f"{len(resolved)} of {len(_ALIASES)} columns matched",
    }
