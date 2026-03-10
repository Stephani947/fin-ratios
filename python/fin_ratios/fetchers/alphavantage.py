"""
Alpha Vantage fetcher — free tier: 25 API requests/day, 5/minute.
Premium tiers: higher limits + more endpoints.
Get a free API key at: https://www.alphavantage.co/support/#api-key

Documentation: https://www.alphavantage.co/documentation/
"""
from __future__ import annotations
import json
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Optional


AV_BASE = "https://www.alphavantage.co/query"


@dataclass
class AlphaVantageData:
    ticker: str
    period: str = ""
    fiscal_year_end: str = ""
    # Income statement
    revenue: float = 0.0
    gross_profit: float = 0.0
    cogs: float = 0.0
    ebit: float = 0.0
    ebitda: float = 0.0
    net_income: float = 0.0
    interest_expense: float = 0.0
    income_tax_expense: float = 0.0
    depreciation_amortization: float = 0.0
    # Balance sheet
    total_assets: float = 0.0
    current_assets: float = 0.0
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    total_liabilities: float = 0.0
    current_liabilities: float = 0.0
    total_equity: float = 0.0
    long_term_debt: float = 0.0
    retained_earnings: float = 0.0
    # Cash flow
    operating_cash_flow: float = 0.0
    capex: float = 0.0
    # Quote
    price: float = 0.0
    market_cap: float = 0.0
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    eps: Optional[float] = None
    beta: Optional[float] = None
    errors: list[str] = field(default_factory=list)


def fetch_alphavantage(
    ticker: str,
    api_key: str,
    periods: int = 4,
    quarterly: bool = False,
) -> list[AlphaVantageData]:
    """
    Fetch annual or quarterly financial statements from Alpha Vantage.

    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'IBM')
        api_key: Alpha Vantage API key
        periods: Number of periods to return
        quarterly: Fetch quarterly instead of annual

    Returns:
        List of AlphaVantageData, most recent first.

    Example:
        >>> data = fetch_alphavantage('AAPL', api_key='YOUR_KEY')
        >>> from fin_ratios import gross_margin
        >>> print(f"Gross margin: {gross_margin(data[0].gross_profit, data[0].revenue):.1%}")
    """
    period_key = "quarterlyReports" if quarterly else "annualReports"
    results: list[AlphaVantageData] = []

    try:
        inc_raw = _get(AV_BASE, {
            "function": "INCOME_STATEMENT",
            "symbol": ticker,
            "apikey": api_key,
        })
        time.sleep(0.5)  # 5 req/min limit on free tier

        bal_raw = _get(AV_BASE, {
            "function": "BALANCE_SHEET",
            "symbol": ticker,
            "apikey": api_key,
        })
        time.sleep(0.5)

        cf_raw = _get(AV_BASE, {
            "function": "CASH_FLOW",
            "symbol": ticker,
            "apikey": api_key,
        })
        time.sleep(0.5)

        overview_raw = _get(AV_BASE, {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": api_key,
        })

        inc_reports = inc_raw.get(period_key, [])[:periods]
        bal_reports = bal_raw.get(period_key, [])[:periods]
        cf_reports = cf_raw.get(period_key, [])[:periods]

        for i in range(min(periods, len(inc_reports))):
            inc = inc_reports[i] if i < len(inc_reports) else {}
            bal = bal_reports[i] if i < len(bal_reports) else {}
            cf = cf_reports[i] if i < len(cf_reports) else {}

            data = AlphaVantageData(
                ticker=ticker,
                period=inc.get("fiscalDateEnding", ""),
                fiscal_year_end=overview_raw.get("FiscalYearEnd", ""),
                # Income
                revenue=_f(inc.get("totalRevenue")) or 0,
                gross_profit=_f(inc.get("grossProfit")) or 0,
                cogs=_f(inc.get("costOfRevenue")) or 0,
                ebit=_f(inc.get("ebit")) or 0,
                ebitda=_f(inc.get("ebitda")) or 0,
                net_income=_f(inc.get("netIncome")) or 0,
                interest_expense=abs(_f(inc.get("interestExpense")) or 0),
                income_tax_expense=_f(inc.get("incomeTaxExpense")) or 0,
                depreciation_amortization=_f(inc.get("depreciationAndAmortization")) or 0,
                # Balance
                total_assets=_f(bal.get("totalAssets")) or 0,
                current_assets=_f(bal.get("totalCurrentAssets")) or 0,
                cash=_f(bal.get("cashAndCashEquivalentsAtCarryingValue")) or 0,
                accounts_receivable=_f(bal.get("currentNetReceivables")) or 0,
                inventory=_f(bal.get("inventory")) or 0,
                total_liabilities=_f(bal.get("totalLiabilities")) or 0,
                current_liabilities=_f(bal.get("totalCurrentLiabilities")) or 0,
                total_equity=_f(bal.get("totalShareholderEquity")) or 0,
                long_term_debt=_f(bal.get("longTermDebtNoncurrent")) or 0,
                retained_earnings=_f(bal.get("retainedEarnings")) or 0,
                # Cash flow
                operating_cash_flow=_f(cf.get("operatingCashflow")) or 0,
                capex=abs(_f(cf.get("capitalExpenditures")) or 0),
                # Quote from overview
                pe_ratio=_f(overview_raw.get("PERatio")),
                pb_ratio=_f(overview_raw.get("PriceToBookRatio")),
                eps=_f(overview_raw.get("EPS")),
                beta=_f(overview_raw.get("Beta")),
                market_cap=_f(overview_raw.get("MarketCapitalization")) or 0,
            )
            results.append(data)

    except Exception as e:
        d = AlphaVantageData(ticker=ticker)
        d.errors.append(str(e))
        return [d]

    return results


def _get(url: str, params: dict) -> dict:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "fin-ratios/0.1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def _f(v) -> Optional[float]:
    try:
        if v in (None, "None", "N/A", "-"):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None
