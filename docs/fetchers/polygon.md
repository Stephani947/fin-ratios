# Polygon.io Fetcher

Fetches annual financial statements from the Polygon.io REST API.

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

Get an API key at [polygon.io](https://polygon.io). Free tier available.

## Usage

=== "Python"

    ```python
    from fin_ratios.fetchers.polygon import fetch_polygon, set_api_key

    # Set key once
    set_api_key('YOUR_POLYGON_KEY')

    annual_data = fetch_polygon('AAPL', years=7)
    ```

    Or via environment variable:

    ```bash
    export POLYGON_API_KEY=your_key
    ```

    ```python
    from fin_ratios.fetchers.polygon import fetch_polygon

    annual_data = fetch_polygon('AAPL', years=7)
    ```

=== "TypeScript"

    ```typescript
    import { fetchPolygon, setPolygonApiKey } from 'fin-ratios/fetchers/polygon'

    setPolygonApiKey('YOUR_POLYGON_KEY')

    const annualData = await fetchPolygon('AAPL', { years: 7 })
    ```

    Or via environment variable (`POLYGON_API_KEY`).

## Key Resolution Order

1. Parameter `api_key=...` / `options.apiKey`
2. Module-level key set via `set_api_key()` / `setPolygonApiKey()`
3. `POLYGON_API_KEY` environment variable

## Fields Returned

Standard field set: `revenue`, `gross_profit`, `ebit`, `net_income`, `operating_cash_flow`, `capex`, `total_assets`, `total_equity`, `total_debt`, `cash`, `depreciation`, `income_tax_expense`, `interest_expense`, `dividends_paid`.

## Notes

- Returns oldest-first, compatible with all `*_from_series` utilities
- Uses the `vX/reference/financials` endpoint
- Polygon's free tier has limited historical depth; paid plans cover 10+ years
