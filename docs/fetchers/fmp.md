# Financial Modeling Prep (FMP) Fetcher

Fetches annual financial statements from the FMP REST API. Free tier: 250 requests/day.

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

Get a free API key at [financialmodelingprep.com](https://financialmodelingprep.com).

## Usage

```python
from fin_ratios.fetchers.fmp import fetch_fmp

annual_data = fetch_fmp('AAPL', num_years=7, api_key='YOUR_FMP_KEY')
```

Or set the environment variable to avoid passing the key every call:

```bash
export FMP_API_KEY=your_key_here
```

```python
from fin_ratios.fetchers.fmp import fetch_fmp

annual_data = fetch_fmp('AAPL', num_years=7)  # reads from FMP_API_KEY env
```

## Coverage

FMP covers:
- US equities (NYSE, NASDAQ, OTC)
- International stocks (LSE, TSX, ASX, Euronext, etc.)
- ETFs, mutual funds
- Cryptocurrencies (basic financials not applicable)

## Advantages vs EDGAR

- Better international coverage
- More consistent XBRL normalisation
- Historical data goes back further for some tickers
- Forward estimates available on paid plans
