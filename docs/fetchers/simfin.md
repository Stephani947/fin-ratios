# SimFin Fetcher

Fetches annual financial statements from the SimFin API. Free tier: 500 requests/day.

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

Get a free API key at [simfin.com](https://simfin.com).

## Usage

```python
from fin_ratios.fetchers.simfin import fetch_simfin, set_api_key

set_api_key('YOUR_SIMFIN_KEY')

annual_data = fetch_simfin('AAPL', num_years=7)
```

Or via environment variable:

```bash
export SIMFIN_API_KEY=your_key
```

```python
from fin_ratios.fetchers.simfin import fetch_simfin

annual_data = fetch_simfin('AAPL', num_years=7)
```

## Notes

- SimFin focuses on standardised, analyst-adjusted financials with fewer XBRL quirks than raw EDGAR data
- Strong coverage for US equities; international coverage varies
- Returns standardised field set compatible with all scoring utilities
- 500 free requests/day; bulk data available on paid plans
