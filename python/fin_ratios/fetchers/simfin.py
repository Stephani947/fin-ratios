"""
SimFin data fetcher.

SimFin provides free structured financial data for US and international companies.
Free tier: 500 API requests/day. Data includes income statements, balance sheets,
cash flow statements, and share price data.

Sign up for a free API key at: https://simfin.com/

Usage:
    from fin_ratios.fetchers.simfin import fetch_simfin

    data = fetch_simfin('AAPL', api_key='your-key')
    print(data.revenue)        # 390_000_000_000
    print(data.net_income)     # 96_000_000_000

    # Or set globally
    import fin_ratios.fetchers.simfin as sf
    sf.set_api_key('your-key')
    data = fetch_simfin('MSFT')
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

from fin_ratios.cache import cached

_SIMFIN_API_KEY: str = ""
_BASE_URL = "https://backend.simfin.com/api/v3"


def set_api_key(key: str) -> None:
    """Set SimFin API key globally."""
    global _SIMFIN_API_KEY
    _SIMFIN_API_KEY = key


def _get_key(api_key: Optional[str]) -> str:
    key = api_key or _SIMFIN_API_KEY or os.environ.get("SIMFIN_API_KEY", "")
    if not key:
        raise ValueError(
            "SimFin API key required. Pass api_key= or call set_api_key() "
            "or set SIMFIN_API_KEY environment variable. "
            "Get a free key at https://simfin.com/"
        )
    return key


@dataclass
class SimFinData:
    """Standardized financial data from SimFin API."""

    ticker: str
    company_name: str = ""
    fiscal_year: str = ""
    period: str = "FY"

    # Income Statement
    revenue: float = 0.0
    gross_profit: float = 0.0
    ebit: float = 0.0
    ebitda: float = 0.0
    net_income: float = 0.0
    interest_expense: float = 0.0
    income_tax_expense: float = 0.0
    ebt: float = 0.0
    cogs: float = 0.0
    sga_expense: float = 0.0
    rd_expense: float = 0.0
    depreciation: float = 0.0

    # Balance Sheet
    total_assets: float = 0.0
    current_assets: float = 0.0
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    total_liabilities: float = 0.0
    current_liabilities: float = 0.0
    long_term_debt: float = 0.0
    total_debt: float = 0.0
    total_equity: float = 0.0
    retained_earnings: float = 0.0
    accounts_payable: float = 0.0

    # Cash Flow
    operating_cash_flow: float = 0.0
    capex: float = 0.0
    dividends_paid: float = 0.0

    # Market (if available)
    market_cap: float = 0.0
    shares_outstanding: float = 0.0
    enterprise_value: float = 0.0

    # Raw metadata
    _raw: dict = field(default_factory=dict, repr=False)


@cached("simfin")
def fetch_simfin(
    ticker: str,
    api_key: Optional[str] = None,
    period: str = "FY",
    year: Optional[int] = None,
) -> SimFinData:
    """
    Fetch the most recent annual financials for a ticker from SimFin.

    Args:
        ticker:   Stock ticker symbol (e.g. 'AAPL', 'MSFT')
        api_key:  SimFin API key. Falls back to set_api_key() / SIMFIN_API_KEY env var.
        period:   Reporting period — 'FY' (annual), 'Q1'-'Q4' (quarterly), 'TTM'
        year:     Specific fiscal year (e.g. 2023). If None, uses most recent.

    Returns:
        SimFinData with standardized financial fields.

    Raises:
        ValueError:  Missing API key
        RuntimeError: API error or ticker not found
    """
    key = _get_key(api_key)
    headers = {"Authorization": f"api-key {key}"}

    income = _fetch_statement(ticker, "income", period, year, headers)
    balance = _fetch_statement(ticker, "balance", period, year, headers)
    cashflow = _fetch_statement(ticker, "cashflow", period, year, headers)

    return _parse(ticker, income, balance, cashflow)


def _fetch_statement(
    ticker: str,
    statement: str,
    period: str,
    year: Optional[int],
    headers: dict,
) -> dict:
    """Fetch a single financial statement from SimFin API."""
    try:
        import httpx
    except ImportError:
        raise ImportError("SimFin fetcher requires httpx: pip install httpx")

    # SimFin v3 endpoint
    url = f"{_BASE_URL}/companies/statements/compact"
    params: dict[str, Any] = {
        "ticker": ticker.upper(),
        "statements": statement,
        "period": period,
    }
    if year:
        params["fyear"] = year

    resp = httpx.get(url, headers=headers, params=params, timeout=15.0)
    if resp.status_code == 403:
        raise RuntimeError("Invalid SimFin API key or quota exceeded")
    if resp.status_code == 404:
        raise RuntimeError(f"Ticker '{ticker}' not found on SimFin")
    if resp.status_code != 200:
        raise RuntimeError(f"SimFin API error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    if not data or not isinstance(data, list) or not data[0].get("statements"):
        raise RuntimeError(f"No {statement} data returned for {ticker}")

    return data[0]


def _safe_float(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _parse(
    ticker: str,
    income_resp: dict,
    balance_resp: dict,
    cashflow_resp: dict,
) -> SimFinData:
    """Parse SimFin API response into SimFinData."""

    def _extract(resp: dict, stmt_type: str) -> tuple[list[str], list[Any]]:
        stmts = resp.get("statements", [])
        for s in stmts:
            if s.get("statement") == stmt_type:
                cols = s.get("columns", [])
                rows = s.get("data", [])
                if rows:
                    return cols, rows[-1]  # most recent period
        return [], []

    def _row_dict(cols: list[str], row: list[Any]) -> dict[str, Any]:
        return dict(zip(cols, row)) if cols and row else {}

    inc_cols, inc_row = _extract(income_resp, "pl")
    bal_cols, bal_row = _extract(balance_resp, "bs")
    cf_cols, cf_row = _extract(cashflow_resp, "cf")

    i = _row_dict(inc_cols, inc_row)
    b = _row_dict(bal_cols, bal_row)
    c = _row_dict(cf_cols, cf_row)

    # SimFin uses standardized column names
    revenue = _safe_float(i.get("Revenue"))
    gross_profit = _safe_float(i.get("Gross Profit"))
    ebit = _safe_float(i.get("Operating Income (Loss)") or i.get("EBIT"))
    net_income = _safe_float(i.get("Net Income") or i.get("Net Income (Common)"))
    interest_exp = _safe_float(i.get("Interest Expense, Net"))
    tax_exp = _safe_float(i.get("Income Tax (Expense) Benefit, Net"))
    ebt = _safe_float(i.get("Pretax Income (Loss)"))
    cogs = _safe_float(i.get("Cost of Revenue"))
    sga = _safe_float(i.get("Selling, General & Administrative"))
    rd = _safe_float(i.get("Research & Development"))
    depr = _safe_float(i.get("Depreciation & Amortization"))
    ebitda = ebit + depr if ebit and depr else 0.0

    total_assets = _safe_float(b.get("Total Assets"))
    current_assets = _safe_float(b.get("Total Current Assets"))
    cash = _safe_float(
        b.get("Cash, Cash Equivalents & Short Term Investments") or b.get("Cash & Cash Equivalents")
    )
    ar = _safe_float(b.get("Accounts & Notes Receivable") or b.get("Accounts Receivable"))
    inventory = _safe_float(b.get("Inventories"))
    total_liabilities = _safe_float(b.get("Total Liabilities"))
    current_liabilities = _safe_float(b.get("Total Current Liabilities"))
    lt_debt = _safe_float(b.get("Long Term Debt") or b.get("Long-Term Debt"))
    total_debt = lt_debt + _safe_float(b.get("Short Term Debt") or b.get("Short-Term Debt"))
    equity = _safe_float(b.get("Total Equity") or b.get("Shareholders' Equity"))
    retained = _safe_float(b.get("Retained Earnings"))
    payables = _safe_float(b.get("Payables & Accruals") or b.get("Accounts Payable"))

    ocf = _safe_float(c.get("Net Cash from Operating Activities"))
    capex = abs(
        _safe_float(
            c.get("Acquisition of Fixed Assets & Intangibles") or c.get("Capital Expenditure")
        )
    )

    fiscal_year = str(income_resp.get("fyear", ""))
    company_name = income_resp.get("companyName", "")

    return SimFinData(
        ticker=ticker.upper(),
        company_name=company_name,
        fiscal_year=fiscal_year,
        revenue=revenue,
        gross_profit=gross_profit,
        ebit=ebit,
        ebitda=ebitda,
        net_income=net_income,
        interest_expense=abs(interest_exp),
        income_tax_expense=abs(tax_exp),
        ebt=ebt,
        cogs=cogs,
        sga_expense=sga,
        rd_expense=rd,
        depreciation=depr,
        total_assets=total_assets,
        current_assets=current_assets,
        cash=cash,
        accounts_receivable=ar,
        inventory=inventory,
        total_liabilities=total_liabilities,
        current_liabilities=current_liabilities,
        long_term_debt=lt_debt,
        total_debt=total_debt,
        total_equity=equity,
        retained_earnings=retained,
        accounts_payable=payables,
        operating_cash_flow=ocf,
        capex=capex,
        _raw={"income": i, "balance": b, "cashflow": c},
    )
