"""
Financial Modeling Prep (FMP) fetcher.

Free tier: 250 req/day — covers most individual company lookups.
Paid plans: unlimited requests, real-time data, more endpoints.
Get a free API key at: https://financialmodelingprep.com/developer/docs

Install: pip install requests  (or use built-in urllib)
"""

from __future__ import annotations
import json
import urllib.request
from dataclasses import dataclass, field
from typing import Optional


FMP_BASE = "https://financialmodelingprep.com/api/v3"


@dataclass
class FmpFinancialData:
    ticker: str
    period: str = ""
    # Market
    price: float = 0.0
    market_cap: float = 0.0
    enterprise_value: float = 0.0
    shares_outstanding: float = 0.0
    beta: Optional[float] = None
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
    eps: float = 0.0
    eps_diluted: float = 0.0
    # Balance sheet
    total_assets: float = 0.0
    current_assets: float = 0.0
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    net_ppe: float = 0.0
    goodwill: float = 0.0
    intangible_assets: float = 0.0
    retained_earnings: float = 0.0
    total_liabilities: float = 0.0
    current_liabilities: float = 0.0
    accounts_payable: float = 0.0
    long_term_debt: float = 0.0
    total_debt: float = 0.0
    total_equity: float = 0.0
    # Cash flow
    operating_cash_flow: float = 0.0
    capex: float = 0.0
    free_cash_flow: float = 0.0
    # Ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    roic: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    errors: list[str] = field(default_factory=list)


def fetch_fmp(
    ticker: str,
    api_key: str,
    periods: int = 4,
    quarterly: bool = False,
) -> list[FmpFinancialData]:
    """
    Fetch financial statements and key ratios from Financial Modeling Prep.

    Args:
        ticker: Stock symbol (e.g. 'AAPL', 'MSFT', 'TSLA')
        api_key: FMP API key (get free key at financialmodelingprep.com)
        periods: Number of periods to fetch (annual years or quarters)
        quarterly: If True, fetch quarterly data

    Returns:
        List of FmpFinancialData, most recent first.

    Example:
        >>> filings = fetch_fmp('AAPL', api_key='YOUR_KEY', periods=3)
        >>> for f in filings:
        ...     print(f.period, f.revenue / 1e9, 'B')
    """
    period_param = "quarter" if quarterly else "annual"
    results: list[FmpFinancialData] = []

    # Fetch all statements in parallel (3 calls)
    try:
        income_data = _get(
            f"{FMP_BASE}/income-statement/{ticker}",
            api_key,
            {"period": period_param, "limit": periods},
        )
        balance_data = _get(
            f"{FMP_BASE}/balance-sheet-statement/{ticker}",
            api_key,
            {"period": period_param, "limit": periods},
        )
        cf_data = _get(
            f"{FMP_BASE}/cash-flow-statement/{ticker}",
            api_key,
            {"period": period_param, "limit": periods},
        )
        ratios_data = _get(
            f"{FMP_BASE}/ratios/{ticker}", api_key, {"period": period_param, "limit": periods}
        )
        profile_data = _get(f"{FMP_BASE}/profile/{ticker}", api_key, {})
        profile = profile_data[0] if profile_data else {}
    except Exception as e:
        f = FmpFinancialData(ticker=ticker)
        f.errors.append(str(e))
        return [f]

    for i in range(min(periods, len(income_data))):
        inc = income_data[i] if i < len(income_data) else {}
        bal = balance_data[i] if i < len(balance_data) else {}
        cf = cf_data[i] if i < len(cf_data) else {}
        rat = ratios_data[i] if i < len(ratios_data) else {}

        data = FmpFinancialData(
            ticker=ticker,
            period=inc.get("date", ""),
            # Market
            price=float(profile.get("price") or 0),
            market_cap=float(profile.get("mktCap") or 0),
            enterprise_value=float(inc.get("ebitda", 0) or 0)
            * float(rat.get("enterpriseValueMultiple") or 0)
            or 0,
            shares_outstanding=float(inc.get("weightedAverageShsOut") or 0),
            beta=_f(profile.get("beta")),
            # Income
            revenue=float(inc.get("revenue") or 0),
            gross_profit=float(inc.get("grossProfit") or 0),
            cogs=float(inc.get("costOfRevenue") or 0),
            ebit=float(inc.get("operatingIncome") or 0),
            ebitda=float(inc.get("ebitda") or 0),
            net_income=float(inc.get("netIncome") or 0),
            interest_expense=abs(float(inc.get("interestExpense") or 0)),
            income_tax_expense=float(inc.get("incomeTaxExpense") or 0),
            depreciation_amortization=float(inc.get("depreciationAndAmortization") or 0),
            eps=float(inc.get("eps") or 0),
            eps_diluted=float(inc.get("epsdiluted") or 0),
            # Balance sheet
            total_assets=float(bal.get("totalAssets") or 0),
            current_assets=float(bal.get("totalCurrentAssets") or 0),
            cash=float(bal.get("cashAndCashEquivalents") or 0),
            accounts_receivable=float(bal.get("netReceivables") or 0),
            inventory=float(bal.get("inventory") or 0),
            net_ppe=float(bal.get("propertyPlantEquipmentNet") or 0),
            goodwill=float(bal.get("goodwill") or 0),
            intangible_assets=float(bal.get("intangibleAssets") or 0),
            retained_earnings=float(bal.get("retainedEarnings") or 0),
            total_liabilities=float(bal.get("totalLiabilities") or 0),
            current_liabilities=float(bal.get("totalCurrentLiabilities") or 0),
            accounts_payable=float(bal.get("accountPayables") or 0),
            long_term_debt=float(bal.get("longTermDebt") or 0),
            total_debt=float(bal.get("totalDebt") or 0),
            total_equity=float(bal.get("totalStockholdersEquity") or 0),
            # Cash flow
            operating_cash_flow=float(cf.get("operatingCashFlow") or 0),
            capex=abs(float(cf.get("capitalExpenditure") or 0)),
            free_cash_flow=float(cf.get("freeCashFlow") or 0),
            # Ratios
            pe_ratio=_f(rat.get("priceEarningsRatio")),
            pb_ratio=_f(rat.get("priceToBookRatio")),
            ps_ratio=_f(rat.get("priceToSalesRatio")),
            ev_to_ebitda=_f(rat.get("enterpriseValueMultiple")),
            roic=_f(rat.get("returnOnCapitalEmployed")),
            roe=_f(rat.get("returnOnEquity")),
            roa=_f(rat.get("returnOnAssets")),
            gross_margin=_f(rat.get("grossProfitMargin")),
            operating_margin=_f(rat.get("operatingProfitMargin")),
            net_margin=_f(rat.get("netProfitMargin")),
            debt_to_equity=_f(rat.get("debtEquityRatio")),
            current_ratio=_f(rat.get("currentRatio")),
        )
        results.append(data)

    return results


def fetch_fmp_sp500(api_key: str) -> list[str]:
    """Fetch the current S&P 500 constituent list from FMP."""
    data = _get(f"{FMP_BASE}/sp500_constituent", api_key, {})
    return [item["symbol"] for item in data] if data else []


def _get(url: str, api_key: str, params: dict) -> list:
    params["apikey"] = api_key
    query = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{url}?{query}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "fin-ratios/0.1"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _f(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None
