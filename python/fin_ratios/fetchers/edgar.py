"""
SEC EDGAR fetcher — completely free, no API key required.

Uses the official EDGAR XBRL API at data.sec.gov.
Covers all US-listed public companies with SEC filings.

Docs: https://www.sec.gov/edgar/sec-api-documentation
Rate limit: 10 requests/second (use delay_seconds >= 0.1)
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Optional


EDGAR_BASE = "https://data.sec.gov"
HEADERS = {
    "User-Agent": "fin-ratios-library contact@example.com",
    "Accept-Encoding": "gzip, deflate",
}


@dataclass
class EdgarFilingData:
    """Financial data extracted from an EDGAR filing."""
    ticker: str
    cik: str
    company_name: str
    fiscal_year: str = ""
    # Income statement
    revenue: float = 0.0
    gross_profit: float = 0.0
    operating_income: float = 0.0
    net_income: float = 0.0
    ebit: float = 0.0
    interest_expense: float = 0.0
    income_tax_expense: float = 0.0
    depreciation_amortization: float = 0.0
    eps_basic: float = 0.0
    eps_diluted: float = 0.0
    shares_outstanding: float = 0.0
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
    errors: list[str] = field(default_factory=list)


def get_cik(ticker: str) -> Optional[str]:
    """
    Resolve a ticker symbol to a CIK (Central Index Key) via EDGAR.
    """
    try:
        import urllib.request
        url = f"{EDGAR_BASE}/submissions/CIK{{:010d}}.json"
        # Use company_tickers.json to look up CIK
        req = urllib.request.Request(
            f"{EDGAR_BASE}/files/company_tickers.json",
            headers=HEADERS,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        # data = {idx: {cik_str, ticker, title}}
        for entry in data.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                return str(entry["cik_str"]).zfill(10)
    except Exception:
        pass
    return None


def fetch_edgar(ticker: str, num_years: int = 4) -> list[EdgarFilingData]:
    """
    Fetch annual financial data from SEC EDGAR for a US-listed company.

    Args:
        ticker: Stock ticker (e.g. 'AAPL', 'MSFT')
        num_years: Number of annual filings to fetch (max 10)

    Returns:
        List of EdgarFilingData, most recent first.

    Example:
        >>> filings = fetch_edgar('AAPL', num_years=3)
        >>> for f in filings:
        ...     print(f.fiscal_year, f.revenue, f.net_income)

    Rate limit: 10 requests/sec — add time.sleep(0.1) between calls in loops.
    """
    try:
        import urllib.request
    except ImportError:
        raise ImportError("urllib.request is in Python stdlib — this should always be available.")

    cik = get_cik(ticker)
    if not cik:
        return [_error_filing(ticker, "0", "Unknown", f"Could not resolve CIK for {ticker}")]

    try:
        req = urllib.request.Request(
            f"{EDGAR_BASE}/submissions/CIK{cik}.json",
            headers=HEADERS,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            submissions = json.loads(resp.read().decode())
    except Exception as e:
        return [_error_filing(ticker, cik, "", str(e))]

    company_name = submissions.get("name", ticker)

    # Find 10-K filings (annual reports)
    filings_data = submissions.get("filings", {}).get("recent", {})
    form_types = filings_data.get("form", [])
    accession_numbers = filings_data.get("accessionNumber", [])
    filing_dates = filings_data.get("filingDate", [])

    ten_k_filings = [
        (accession_numbers[i], filing_dates[i])
        for i, f in enumerate(form_types)
        if f == "10-K"
    ][:num_years]

    if not ten_k_filings:
        return [_error_filing(ticker, cik, company_name, "No 10-K filings found")]

    results = []
    for accession, filing_date in ten_k_filings:
        filing = EdgarFilingData(
            ticker=ticker,
            cik=cik,
            company_name=company_name,
            fiscal_year=filing_date[:4],
        )

        try:
            # Fetch XBRL company facts
            req = urllib.request.Request(
                f"{EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik}.json",
                headers=HEADERS,
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                facts = json.loads(resp.read().decode())

            us_gaap = facts.get("facts", {}).get("us-gaap", {})

            # Extract key metrics from XBRL facts
            year = int(filing.fiscal_year)
            filing.revenue = _get_xbrl_annual(us_gaap, year, [
                "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "SalesRevenueNet", "RevenueFromContractWithCustomer",
            ])
            filing.gross_profit = _get_xbrl_annual(us_gaap, year, ["GrossProfit"])
            filing.operating_income = _get_xbrl_annual(us_gaap, year, [
                "OperatingIncomeLoss", "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
            ])
            filing.net_income = _get_xbrl_annual(us_gaap, year, [
                "NetIncomeLoss", "ProfitLoss"
            ])
            filing.ebit = filing.operating_income or filing.net_income
            filing.interest_expense = _get_xbrl_annual(us_gaap, year, [
                "InterestExpense", "InterestAndDebtExpense"
            ])
            filing.income_tax_expense = _get_xbrl_annual(us_gaap, year, [
                "IncomeTaxExpenseBenefit"
            ])
            filing.total_assets = _get_xbrl_annual(us_gaap, year, ["Assets"])
            filing.current_assets = _get_xbrl_annual(us_gaap, year, ["AssetsCurrent"])
            filing.cash = _get_xbrl_annual(us_gaap, year, [
                "CashAndCashEquivalentsAtCarryingValue",
                "CashCashEquivalentsAndShortTermInvestments",
            ])
            filing.accounts_receivable = _get_xbrl_annual(us_gaap, year, [
                "AccountsReceivableNetCurrent", "ReceivablesNetCurrent"
            ])
            filing.inventory = _get_xbrl_annual(us_gaap, year, [
                "InventoryNet", "Inventories"
            ])
            filing.total_liabilities = _get_xbrl_annual(us_gaap, year, ["Liabilities"])
            filing.current_liabilities = _get_xbrl_annual(us_gaap, year, ["LiabilitiesCurrent"])
            filing.total_equity = _get_xbrl_annual(us_gaap, year, [
                "StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
            ])
            filing.long_term_debt = _get_xbrl_annual(us_gaap, year, [
                "LongTermDebtNoncurrent", "LongTermDebt"
            ])
            filing.retained_earnings = _get_xbrl_annual(us_gaap, year, [
                "RetainedEarningsAccumulatedDeficit"
            ])
            filing.operating_cash_flow = _get_xbrl_annual(us_gaap, year, [
                "NetCashProvidedByUsedInOperatingActivities"
            ])
            filing.capex = abs(_get_xbrl_annual(us_gaap, year, [
                "PaymentsToAcquirePropertyPlantAndEquipment",
                "CapitalExpendituresIncurredButNotYetPaid",
            ]))
            filing.shares_outstanding = _get_xbrl_annual(us_gaap, year, [
                "CommonStockSharesOutstanding",
                "WeightedAverageNumberOfSharesOutstandingBasic",
            ])

        except Exception as e:
            filing.errors.append(str(e))

        results.append(filing)
        time.sleep(0.11)  # Stay under 10 req/sec rate limit

    return results


def _get_xbrl_annual(us_gaap: dict, year: int, keys: list[str]) -> float:
    """Extract the most recent annual value for a GAAP concept."""
    for key in keys:
        concept = us_gaap.get(key, {})
        units = concept.get("units", {})
        usd_data = units.get("USD") or units.get("shares")
        if not usd_data:
            continue
        # Find 10-K filing for target year
        annual_vals = [
            entry for entry in usd_data
            if entry.get("form") == "10-K" and
            str(entry.get("end", ""))[:4] == str(year)
        ]
        if annual_vals:
            # Pick the one with most recent filed date
            latest = max(annual_vals, key=lambda x: x.get("filed", ""))
            val = latest.get("val", 0)
            return float(val) if val is not None else 0.0
    return 0.0


def _error_filing(ticker: str, cik: str, name: str, error: str) -> EdgarFilingData:
    f = EdgarFilingData(ticker=ticker, cik=cik, company_name=name)
    f.errors.append(error)
    return f
