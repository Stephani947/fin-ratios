# SEC EDGAR Fetcher

Fetches annual financial statements from the SEC's EDGAR XBRL API. Free, no API key, US-listed companies only.

## Installation

```bash
pip install "financial-ratios[fetchers]"
```

## Usage

=== "Python"

    ```python
    from fin_ratios.fetchers.edgar import fetch_edgar

    # Returns list of dicts, oldest-first
    annual_data = fetch_edgar('AAPL', num_years=7)

    print(len(annual_data))          # 7
    print(annual_data[0]['revenue']) # earliest year
    ```

=== "TypeScript"

    ```typescript
    import { fetchEdgarNormalized } from 'fin-ratios/fetchers/edgar'

    // Returns oldest-first flat records, ready for all scoring utilities
    const annualData = await fetchEdgarNormalized('AAPL', { numYears: 7 })

    console.log(annualData.length)          // 7
    console.log(annualData[0].revenue)      // earliest year
    ```

## TypeScript: Raw vs Normalized

The TypeScript fetcher exposes two functions:

```typescript
import { fetchEdgar, fetchEdgarNormalized, flattenEdgarData } from 'fin-ratios/fetchers/edgar'

// Raw: XBRL response with nested structure, newest-first
const raw = await fetchEdgar('AAPL')

// Normalized: flat records, oldest-first — compatible with all scoring utilities
const normalized = await fetchEdgarNormalized('AAPL')

// Or convert manually from raw
const normalized2 = flattenEdgarData(raw)
```

## Data Quality Notes

- EDGAR uses XBRL tags that vary by filer. Some fields may be `null` for certain companies.
- Non-US companies that file 20-F forms may have partial coverage.
- Small companies and recent IPOs may have fewer years available.
- Data is sourced directly from official SEC filings — generally reliable for US large/mid caps.

## Fields Returned

Same standard set as all other fetchers: `revenue`, `gross_profit`, `ebit`, `ebitda`, `net_income`, `operating_cash_flow`, `capex`, `total_assets`, `total_equity`, `total_debt`, `cash`, `accounts_receivable`, `inventory`, `depreciation`, `income_tax_expense`, `interest_expense`, `dividends_paid`, `shares_outstanding`.
