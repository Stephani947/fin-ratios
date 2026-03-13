"""
Polygon.io fetcher for fin-ratios.

Fetches fundamental financial data from the Polygon.io REST API
(https://polygon.io/docs/stocks/get_vx_reference_financials).

Authentication: API key via ``set_api_key()`` or the ``POLYGON_API_KEY``
environment variable.  Free tier: 5 requests/minute, ~2 years of history.

Example
-------
>>> from fin_ratios.fetchers.polygon import fetch_polygon, set_api_key
>>> set_api_key("your-api-key")
>>> data = fetch_polygon("AAPL", years=5)
>>> from fin_ratios.utils.quality_score import quality_score_from_series
>>> score = quality_score_from_series(data)
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Optional

# ── Module-level API key storage ──────────────────────────────────────────────

_KEY: Optional[str] = None


def set_api_key(key: str) -> None:
    """Store a Polygon.io API key module-wide.

    Parameters
    ----------
    key : str
        Your Polygon.io API key.
    """
    global _KEY
    _KEY = key


# ── Public API ─────────────────────────────────────────────────────────────────


def fetch_polygon(
    ticker: str,
    years: int = 5,
    api_key: Optional[str] = None,
    timeframe: str = "annual",
) -> list[dict]:
    """Fetch financial data from the Polygon.io REST API.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. ``'AAPL'``).
    years : int
        Number of years of historical data to retrieve (default 5).
    api_key : str, optional
        Polygon.io API key.  Falls back to the module-level key set via
        :func:`set_api_key` and then to the ``POLYGON_API_KEY`` environment
        variable.
    timeframe : str
        ``'annual'`` (default) or ``'quarterly'``.

    Returns
    -------
    list[dict]
        Annual records sorted oldest-first.  Each dict contains:

        ``revenue``, ``ebit``, ``net_income``, ``total_assets``,
        ``total_equity``, ``total_debt``, ``cash``, ``capex``,
        ``depreciation``, ``income_tax_expense``, ``ebt``,
        ``operating_cash_flow``, ``dividends_paid``,
        ``shares_outstanding``, ``gross_profit``, ``interest_expense``,
        ``current_assets``, ``current_liabilities``, ``accounts_receivable``.

    Raises
    ------
    ImportError
        If ``httpx`` is not installed.
    ValueError
        If no API key is available.
    RuntimeError
        If the Polygon.io API request fails.

    Example
    -------
    >>> from fin_ratios.fetchers.polygon import fetch_polygon, set_api_key
    >>> set_api_key("your-api-key")
    >>> data = fetch_polygon("AAPL", years=5)
    >>> from fin_ratios.utils.quality_score import quality_score_from_series
    >>> score = quality_score_from_series(data)
    """
    try:
        import httpx
    except ImportError as exc:
        raise ImportError(
            "httpx is required for the Polygon fetcher. Install it with: pip install httpx"
        ) from exc

    key = api_key or _KEY or os.environ.get("POLYGON_API_KEY")
    if not key:
        raise ValueError(
            "A Polygon.io API key is required. Provide it via the api_key "
            "parameter, fin_ratios.fetchers.polygon.set_api_key(), or the "
            "POLYGON_API_KEY environment variable."
        )

    # Polygon free tier covers the last ~2 years; paid tiers go further.
    today = date.today()
    start_date = (today - timedelta(days=max(years, 2) * 366)).isoformat()

    params: dict = {
        "ticker": ticker.upper(),
        "timeframe": timeframe,
        "limit": min(years, 100),
        "sort": "period_of_report_date",
        "order": "asc",
        "filing_date.gte": start_date,
        "apiKey": key,
    }

    url = "https://api.polygon.io/vX/reference/financials"

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, params=params)
    except Exception as exc:
        raise RuntimeError(f"Polygon API request failed for {ticker!r}: {exc}") from exc

    if resp.status_code == 401:
        raise RuntimeError("Polygon API returned 401 Unauthorized — check your API key.")
    if resp.status_code == 429:
        raise RuntimeError(
            "Polygon API rate limit exceeded (free tier: 5 req/min). Wait a moment and retry."
        )
    if not resp.is_success:
        raise RuntimeError(
            f"Polygon API request failed for {ticker!r}: "
            f"HTTP {resp.status_code} — {resp.text[:200]}"
        )

    try:
        payload = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Could not parse Polygon API response for {ticker!r}: {exc}") from exc

    results = payload.get("results", [])
    if not results:
        return []

    records: list[dict] = []
    for item in results:
        financials = item.get("financials", {})
        inc = financials.get("income_statement", {})
        bal = financials.get("balance_sheet", {})
        cf = financials.get("cash_flow_statement", {})

        def _v(section: dict, *keys: str) -> float:
            """Extract the first available value from a Polygon financials section."""
            for k in keys:
                node = section.get(k)
                if isinstance(node, dict):
                    val = node.get("value")
                    if val is not None:
                        try:
                            return float(val)
                        except (TypeError, ValueError):
                            pass
            return 0.0

        revenue = _v(inc, "revenues", "net_revenues", "total_revenues")
        gross_profit = _v(inc, "gross_profit")
        ebit = _v(inc, "operating_income", "income_loss_from_continuing_operations_before_tax")
        net_income = _v(inc, "net_income_loss", "net_income_loss_attributable_to_parent")
        tax_expense = _v(inc, "income_tax_expense_benefit")
        interest_exp = abs(_v(inc, "interest_expense_operating", "interest_expense"))
        # EBT: Polygon may expose it directly or we compute from net income + taxes
        ebt_raw = _v(
            inc, "income_loss_from_continuing_operations_before_tax", "income_before_income_taxes"
        )
        ebt = ebt_raw if ebt_raw else (net_income + tax_expense)

        total_assets = _v(bal, "assets")
        current_assets = _v(bal, "current_assets")
        cash = _v(
            bal,
            "cash_and_cash_equivalents_including_short_term_investments",
            "cash_and_cash_equivalents",
            "cash",
        )

        current_liab = _v(bal, "current_liabilities")
        total_equity = _v(bal, "equity", "stockholders_equity", "equity_attributable_to_parent")
        long_term_debt = _v(bal, "long_term_debt")
        ar = _v(
            bal,
            "accounts_receivable",
            "accounts_receivable_net_current",
            "trade_and_other_receivables_current",
        )

        ocf = _v(
            cf,
            "net_cash_flow_from_operating_activities",
            "net_cash_provided_by_used_in_operating_activities",
        )
        investing_cf = _v(
            cf,
            "net_cash_flow_from_investing_activities",
            "net_cash_provided_by_used_in_investing_activities",
        )
        # Capex is typically embedded in investing cash flows; Polygon doesn't
        # always expose it as a standalone field, so use absolute investing CF
        # as a conservative proxy when the direct field is absent.
        capex_direct = _v(
            cf, "payments_to_acquire_property_plant_and_equipment", "capital_expenditures"
        )
        capex = abs(capex_direct) if capex_direct else abs(investing_cf)

        dividends_paid = abs(
            _v(cf, "payments_of_dividends", "payments_of_dividends_common_stock", "dividends_paid")
        )
        depreciation = _v(
            inc, "depreciation_and_amortization", "depreciation_depletion_and_amortization"
        )
        if not depreciation:
            depreciation = _v(
                cf, "depreciation_depletion_and_amortization", "depreciation_and_amortization"
            )

        shares = _v(
            inc, "basic_average_shares", "diluted_average_shares", "basic_earnings_per_share"
        )  # fallback; usually wrong
        # Prefer balance-sheet share count if available
        shares_bs = _v(bal, "common_stock_shares_outstanding")
        if shares_bs:
            shares = shares_bs

        fiscal_year = str(item.get("fiscal_year", ""))

        records.append(
            {
                "fiscal_year": fiscal_year,
                "revenue": revenue,
                "gross_profit": gross_profit,
                "ebit": ebit,
                "net_income": net_income,
                "total_assets": total_assets,
                "current_assets": current_assets,
                "total_equity": total_equity,
                "total_debt": long_term_debt,
                "long_term_debt": long_term_debt,
                "cash": cash,
                "capex": capex,
                "depreciation": depreciation,
                "operating_cash_flow": ocf,
                "income_tax_expense": tax_expense,
                "ebt": ebt,
                "interest_expense": interest_exp,
                "current_liabilities": current_liab,
                "accounts_receivable": ar,
                "dividends_paid": dividends_paid,
                "shares_outstanding": shares,
            }
        )

    return records
