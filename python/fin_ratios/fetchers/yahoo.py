"""
Yahoo Finance fetcher — uses yfinance (free, no API key required).

Install: pip install yfinance

Maps yfinance data into fin_ratios standard types.
"""

from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class YahooFinancialData:
    """Structured data fetched from Yahoo Finance for a single ticker."""

    ticker: str
    # Market data
    price: float = 0.0
    market_cap: float = 0.0
    enterprise_value: float = 0.0
    shares_outstanding: float = 0.0
    # Income statement
    revenue: float = 0.0
    gross_profit: float = 0.0
    cogs: float = 0.0
    ebit: float = 0.0
    ebitda: float = 0.0
    net_income: float = 0.0
    interest_expense: float = 0.0
    income_tax_expense: float = 0.0
    ebt: float = 0.0
    depreciation_and_amortization: float = 0.0
    # Balance sheet
    total_assets: float = 0.0
    current_assets: float = 0.0
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    net_ppe: float = 0.0
    retained_earnings: float = 0.0
    goodwill: float = 0.0
    intangible_assets: float = 0.0
    total_liabilities: float = 0.0
    current_liabilities: float = 0.0
    accounts_payable: float = 0.0
    long_term_debt: float = 0.0
    total_debt: float = 0.0
    total_equity: float = 0.0
    # Cash flow
    operating_cash_flow: float = 0.0
    capex: float = 0.0
    # Derived
    working_capital: float = 0.0
    net_debt: float = 0.0
    # Pre-computed ratios from Yahoo
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    ev_to_revenue: Optional[float] = None
    debt_to_equity: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    current_ratio_val: Optional[float] = None
    gross_margins: Optional[float] = None
    operating_margins: Optional[float] = None
    profit_margins: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    trailing_eps: Optional[float] = None
    forward_eps: Optional[float] = None
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None
    sector: str = ""
    industry: str = ""
    employee_count: int = 0
    price_history: list[float] = field(default_factory=list)
    price_history_dates: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def fetch_yahoo(
    ticker: str,
    include_history: bool = False,
    history_period: str = "1y",
) -> YahooFinancialData:
    """
    Fetch comprehensive financial data for a ticker from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        include_history: Whether to fetch price history for risk calculations
        history_period: Period for price history ('1y', '2y', '5y', 'max')

    Returns:
        YahooFinancialData with all available fields populated.

    Example:
        >>> data = fetch_yahoo('AAPL')
        >>> from fin_ratios import pe, roic
        >>> print(f"P/E: {pe(data.market_cap, data.net_income):.1f}")
    """
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("yfinance is required. Install with: pip install yfinance")

    result = YahooFinancialData(ticker=ticker)

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        # Market data
        result.price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0)
        result.market_cap = float(info.get("marketCap") or 0)
        result.enterprise_value = float(info.get("enterpriseValue") or 0)
        result.shares_outstanding = float(info.get("sharesOutstanding") or 0)

        # Pre-computed ratios from Yahoo
        result.trailing_pe = _safe_float(info.get("trailingPE"))
        result.forward_pe = _safe_float(info.get("forwardPE"))
        result.price_to_book = _safe_float(info.get("priceToBook"))
        result.price_to_sales = _safe_float(info.get("priceToSalesTrailing12Months"))
        result.ev_to_ebitda = _safe_float(info.get("enterpriseToEbitda"))
        result.ev_to_revenue = _safe_float(info.get("enterpriseToRevenue"))
        result.debt_to_equity = _safe_float(info.get("debtToEquity"))
        result.return_on_equity = _safe_float(info.get("returnOnEquity"))
        result.return_on_assets = _safe_float(info.get("returnOnAssets"))
        result.current_ratio_val = _safe_float(info.get("currentRatio"))
        result.gross_margins = _safe_float(info.get("grossMargins"))
        result.operating_margins = _safe_float(info.get("operatingMargins"))
        result.profit_margins = _safe_float(info.get("profitMargins"))
        result.revenue_growth = _safe_float(info.get("revenueGrowth"))
        result.earnings_growth = _safe_float(info.get("earningsGrowth"))
        result.trailing_eps = _safe_float(info.get("trailingEps"))
        result.forward_eps = _safe_float(info.get("forwardEps"))
        result.beta = _safe_float(info.get("beta"))
        result.dividend_yield = _safe_float(info.get("dividendYield"))
        result.sector = info.get("sector") or ""
        result.industry = info.get("industry") or ""
        result.employee_count = int(info.get("fullTimeEmployees") or 0)

        # Raw totals for computed ratios
        result.revenue = float(info.get("totalRevenue") or 0)
        result.ebitda = float(info.get("ebitda") or 0)
        result.net_income = float(info.get("netIncomeToCommon") or 0)
        result.total_debt = float(info.get("totalDebt") or 0)
        result.cash = float(info.get("totalCash") or 0)
        result.operating_cash_flow = float(info.get("operatingCashflow") or 0)
        result.capex = abs(float(info.get("capitalExpenditures") or 0))
        result.net_debt = result.total_debt - result.cash

        # Full financial statements
        try:
            income = stock.income_stmt
            if income is not None and not income.empty:
                col = income.columns[0]  # Most recent year
                result.gross_profit = _get_row(income, col, ["Gross Profit", "GrossProfit"])
                result.ebit = _get_row(income, col, ["EBIT", "Operating Income", "OperatingIncome"])
                result.interest_expense = abs(
                    _get_row(
                        income, col, ["Interest Expense", "InterestExpense", "Net Interest Income"]
                    )
                )
                result.depreciation_and_amortization = _get_row(
                    income, col, ["Reconciled Depreciation", "Depreciation & Amortization"]
                )
                result.income_tax_expense = _get_row(
                    income, col, ["Tax Provision", "Income Tax Expense"]
                )
                result.ebt = _get_row(income, col, ["Pretax Income", "EarningsBeforeTax"])
                result.cogs = _get_row(income, col, ["Cost Of Revenue", "CostOfRevenue", "COGS"])
        except Exception as e:
            result.errors.append(f"income_stmt: {e}")

        try:
            balance = stock.balance_sheet
            if balance is not None and not balance.empty:
                col = balance.columns[0]
                result.total_assets = _get_row(balance, col, ["Total Assets", "TotalAssets"])
                result.current_assets = _get_row(balance, col, ["Current Assets", "CurrentAssets"])
                result.accounts_receivable = _get_row(
                    balance, col, ["Accounts Receivable", "Net Receivables"]
                )
                result.inventory = _get_row(balance, col, ["Inventory"])
                result.net_ppe = _get_row(
                    balance,
                    col,
                    ["Net PPE", "Property Plant Equipment Net", "Net Property Plant And Equipment"],
                )
                result.retained_earnings = _get_row(
                    balance, col, ["Retained Earnings", "RetainedEarnings"]
                )
                result.goodwill = _get_row(balance, col, ["Goodwill"])
                result.intangible_assets = _get_row(
                    balance, col, ["Other Intangible Assets", "Intangible Assets"]
                )
                result.total_liabilities = _get_row(
                    balance, col, ["Total Liabilities Net Minority Interest", "Total Liabilities"]
                )
                result.current_liabilities = _get_row(
                    balance, col, ["Current Liabilities", "CurrentLiabilities"]
                )
                result.accounts_payable = _get_row(
                    balance, col, ["Accounts Payable", "AccountsPayable"]
                )
                result.long_term_debt = _get_row(balance, col, ["Long Term Debt", "LongTermDebt"])
                result.total_equity = _get_row(
                    balance,
                    col,
                    [
                        "Stockholders Equity",
                        "Total Stockholders Equity",
                        "Stockholders' Equity",
                        "TotalEquityGrossMinorityInterest",
                    ],
                )
                result.working_capital = result.current_assets - result.current_liabilities
        except Exception as e:
            result.errors.append(f"balance_sheet: {e}")

        try:
            cf = stock.cash_flow
            if cf is not None and not cf.empty:
                col = cf.columns[0]
                if result.operating_cash_flow == 0:
                    result.operating_cash_flow = _get_row(
                        cf, col, ["Operating Cash Flow", "Cash From Operations"]
                    )
                capex_raw = _get_row(cf, col, ["Capital Expenditure", "Purchases Of PPE", "CapEx"])
                result.capex = abs(capex_raw)
        except Exception as e:
            result.errors.append(f"cash_flow: {e}")

        if include_history:
            try:
                hist = stock.history(period=history_period)
                if not hist.empty:
                    result.price_history = hist["Close"].tolist()
                    result.price_history_dates = [str(d.date()) for d in hist.index]
            except Exception as e:
                result.errors.append(f"history: {e}")

    except Exception as e:
        result.errors.append(f"general: {e}")

    return result


def fetch_yahoo_batch(
    tickers: list[str],
    delay_seconds: float = 0.5,
    verbose: bool = True,
) -> dict[str, YahooFinancialData]:
    """
    Fetch data for multiple tickers with rate limiting.

    Args:
        tickers: List of ticker symbols
        delay_seconds: Delay between requests to avoid rate limiting
        verbose: Print progress

    Returns:
        Dict mapping ticker -> YahooFinancialData
    """
    import time

    results = {}
    total = len(tickers)
    for i, ticker in enumerate(tickers):
        if verbose and i % 10 == 0:
            print(f"  Fetching {i + 1}/{total}: {ticker}")
        results[ticker] = fetch_yahoo(ticker)
        if delay_seconds > 0:
            time.sleep(delay_seconds)
    return results


def _safe_float(v) -> Optional[float]:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _get_row(df, col, keys: list[str]) -> float:
    for key in keys:
        try:
            val = df.loc[key, col]
            if val is not None and not (isinstance(val, float) and val != val):  # not NaN
                return float(val)
        except (KeyError, TypeError):
            continue
    return 0.0
