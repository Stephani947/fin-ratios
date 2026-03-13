# Alpha Vantage Fetcher

Fetches annual financial statements from the Alpha Vantage API.

**Free tier**: 25 requests/day · **Paid**: 75 req/min and above · [Get a free key](https://www.alphavantage.co/support/#api-key)

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

## Usage

=== "Python"

    ```python
    from fin_ratios.fetchers.alphavantage import fetch_alphavantage

    # Pass key directly
    annual_data = fetch_alphavantage('AAPL', num_years=5, api_key='YOUR_KEY')

    # Or set env var — key is picked up automatically
    # export ALPHAVANTAGE_API_KEY=your_key
    annual_data = fetch_alphavantage('AAPL', num_years=5)

    # Use with any scoring utility
    from fin_ratios.utils.investment_score import investment_score_from_series
    score = investment_score_from_series(annual_data)
    print(score.score, score.grade)
    ```

## Choosing Alpha Vantage vs Other Sources

| Source | Free requests | Auth | US coverage | International |
|--------|--------------|------|-------------|---------------|
| SEC EDGAR | Unlimited | None | Excellent | US-listed only |
| Yahoo Finance | Unlimited* | None | Good | Good |
| Alpha Vantage | 25/day | API key | Good | Partial |
| FMP | 250/day | API key | Excellent | Excellent |
| SimFin | 500/day | API key | Good | Partial |

*Yahoo Finance has no official rate limits but may throttle heavy usage.

## Notes

- Returns a standardised field list compatible with all fin-ratios scoring utilities
- Data is sourced from SEC filings via Alpha Vantage's normalisation layer
- For higher volume or international coverage, consider [FMP](fmp.md)
