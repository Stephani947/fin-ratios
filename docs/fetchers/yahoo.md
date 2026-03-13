# Yahoo Finance Fetcher

Fetches annual financial statements from Yahoo Finance using `yfinance`. Free, no API key required.

## Installation

```bash
pip install "financial-ratios[fetchers]"
```

## Usage

```python
from fin_ratios.fetchers.yahoo import fetch_yahoo

# Returns list of dicts, oldest-first, ready for scoring utilities
annual_data = fetch_yahoo('AAPL', num_years=7)

# Each record contains: revenue, gross_profit, ebit, net_income,
# operating_cash_flow, capex, total_assets, total_equity, total_debt, cash, ...
print(annual_data[0]['revenue'])  # earliest year
```

## Batch Fetch

```python
from fin_ratios.fetchers.yahoo import fetch_yahoo_batch

tickers = ['AAPL', 'MSFT', 'GOOGL']
data = fetch_yahoo_batch(tickers, num_years=5)
# Returns dict: {'AAPL': [...], 'MSFT': [...], ...}
```

## Fields Returned

| Field | Description |
|-------|-------------|
| `revenue` | Total revenue |
| `gross_profit` | Gross profit |
| `ebit` | Operating income |
| `ebitda` | EBITDA |
| `net_income` | Net income |
| `operating_cash_flow` | Cash from operations |
| `capex` | Capital expenditures (positive) |
| `total_assets` | Total assets |
| `total_equity` | Shareholders' equity |
| `total_debt` | Total debt |
| `cash` | Cash and equivalents |
| `accounts_receivable` | Trade receivables |
| `inventory` | Inventory |
| `depreciation` | Depreciation & amortization |
| `income_tax_expense` | Tax expense |
| `interest_expense` | Interest charges |
| `dividends_paid` | Cash dividends paid |
| `shares_outstanding` | Diluted shares |

## Limitations

- Rate limiting: Yahoo may throttle heavy usage. For production, consider SEC EDGAR or a paid API.
- Data quality: Yahoo Finance data can have gaps or errors, especially for non-US companies.
- No forward estimates.
