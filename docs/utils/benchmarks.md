# Sector Benchmarks

Compare a company's metrics against sector averages and historical percentile distributions.

## Usage

```python
from fin_ratios.utils.benchmarks import sector_benchmarks, percentile_rank

# Get benchmark distributions for a sector
benchmarks = sector_benchmarks('technology')

print(benchmarks['gross_margin'])
# {'p25': 0.35, 'p50': 0.52, 'p75': 0.68, 'mean': 0.53}

# Where does a value rank in the sector?
rank = percentile_rank('technology', 'gross_margin', 0.43)
print(rank)  # e.g. 38 (38th percentile)
```

## Supported Sectors

`technology`, `healthcare`, `financial_services`, `consumer_staples`, `consumer_discretionary`, `industrials`, `energy`, `materials`, `utilities`, `real_estate`, `communication_services`

## Supported Metrics

Standard ratios plus scoring model outputs: `gross_margin`, `operating_margin`, `net_profit_margin`, `roe`, `roa`, `roic`, `current_ratio`, `debt_to_equity`, `fcf_margin`, `pe`, `pb`, `ev_ebitda`, `moat_score`, `capital_allocation`, `earnings_quality`, `quality_score`.

## Benchmarks Data

Benchmarks are based on aggregated distributions from publicly available financial data. They are updated periodically and represent approximate industry norms rather than precise real-time market data.
