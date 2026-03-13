# Sector Benchmarks

Compare any financial metric or scoring model output against sector-level percentile distributions.

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.benchmarks import sector_benchmarks, percentile_rank

    # Get full benchmark distribution for a sector
    benchmarks = sector_benchmarks('technology')

    # Each metric returns p25, p50, p75, mean
    print(benchmarks['gross_margin'])
    # {'p25': 0.35, 'p50': 0.52, 'p75': 0.68, 'mean': 0.53}

    print(benchmarks['roic'])
    # {'p25': 0.08, 'p50': 0.14, 'p75': 0.25, 'mean': 0.16}

    print(benchmarks['moat_score'])
    # {'p25': 42, 'p50': 58, 'p75': 71, 'mean': 57}

    # Rank a single value in the sector distribution
    rank = percentile_rank('technology', 'gross_margin', 0.43)
    print(f"{rank}th percentile")  # e.g. 38th percentile

    rank = percentile_rank('technology', 'moat_score', 74)
    print(f"{rank}th percentile")  # e.g. 79th percentile
    ```

## Combining with Scoring

```python
from fin_ratios.utils.moat_score import moat_score_from_series
from fin_ratios.utils.benchmarks import percentile_rank
from fin_ratios.fetchers.edgar import fetch_edgar

annual_data = fetch_edgar('AAPL', num_years=7)
moat = moat_score_from_series(annual_data)

rank = percentile_rank('technology', 'moat_score', moat.score)
print(f"Moat score {moat.score}/100 — {rank}th percentile in Technology sector")
```

## Supported Sectors

| Sector key | GICS sector |
|---|---|
| `technology` | Information Technology |
| `healthcare` | Health Care |
| `financial_services` | Financials |
| `consumer_staples` | Consumer Staples |
| `consumer_discretionary` | Consumer Discretionary |
| `industrials` | Industrials |
| `energy` | Energy |
| `materials` | Materials |
| `utilities` | Utilities |
| `real_estate` | Real Estate |
| `communication_services` | Communication Services |

## Supported Metrics

**Financial ratios:** `gross_margin`, `operating_margin`, `net_profit_margin`, `roe`, `roa`, `roic`, `current_ratio`, `debt_to_equity`, `fcf_margin`, `pe`, `pb`, `ev_ebitda`

**Scoring model outputs:** `moat_score`, `capital_allocation`, `earnings_quality`, `quality_score`

## Data Notes

Benchmarks are pre-computed distributions derived from publicly available financial data across S&P 500 constituents and represent approximate industry norms. They are periodically updated and serve as relative context, not absolute thresholds.
