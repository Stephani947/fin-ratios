# Alpha Vantage Fetcher

Fetches annual financial statements from the Alpha Vantage API. Free tier: 25 requests/day.

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

Get a free API key at [alphavantage.co](https://www.alphavantage.co/support/#api-key).

## Usage

```python
from fin_ratios.fetchers.alphavantage import fetch_alphavantage

annual_data = fetch_alphavantage('AAPL', num_years=5, api_key='YOUR_KEY')
```

Or via environment variable:

```bash
export ALPHAVANTAGE_API_KEY=your_key
```

```python
annual_data = fetch_alphavantage('AAPL', num_years=5)
```

## Notes

- 25 requests/day on the free tier; 75/min on paid plans
- US equities and some international symbols supported
- Returns standardised field set compatible with all scoring utilities
