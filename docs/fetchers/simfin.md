# SimFin Fetcher

Fetches standardised annual financial statements from the SimFin API.

**Free tier**: 500 requests/day · [Get a free key](https://simfin.com)

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

## Usage

=== "Python"

    ```python
    from fin_ratios.fetchers.simfin import fetch_simfin, set_api_key

    # Option 1: set key once per session
    set_api_key('YOUR_SIMFIN_KEY')
    annual_data = fetch_simfin('AAPL', num_years=7)

    # Option 2: pass key directly
    annual_data = fetch_simfin('AAPL', num_years=7, api_key='YOUR_SIMFIN_KEY')

    # Option 3: env var — picked up automatically
    # export SIMFIN_API_KEY=your_key
    annual_data = fetch_simfin('AAPL', num_years=7)

    # Use with scoring utilities
    from fin_ratios.utils.quality_score import quality_score_from_series
    quality = quality_score_from_series(annual_data)
    print(quality.score, quality.grade)
    ```

## Why SimFin?

SimFin applies its own normalisation layer on top of raw filings, which reduces the XBRL tag inconsistencies common with direct SEC EDGAR access. This makes it a good choice when EDGAR returns odd values for a specific ticker.

## Notes

- 500 free requests/day; bulk data and higher limits on paid plans
- Strong US equity coverage; international coverage varies by exchange
- Returns standardised field set compatible with all fin-ratios scoring utilities
- SimFin uses analyst-adjusted figures for some line items (e.g. normalised D&A)
