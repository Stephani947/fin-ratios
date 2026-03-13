# Pandas & Polars Integration

Compute ratios directly on DataFrames — with or without groupby.

## Installation

```bash
pip install "financial-ratios[pandas]"
# or for Polars
pip install polars
```

## Usage

```python
import pandas as pd
from fin_ratios.pandas_ext import ratios_from_df

df = pd.DataFrame({
    'ticker':      ['AAPL', 'AAPL', 'MSFT', 'MSFT'],
    'year':        [2022,   2023,   2022,   2023  ],
    'revenue':     [394e9,  383e9,  198e9,  212e9 ],
    'gross_profit':[170e9,  169e9,  136e9,  146e9 ],
    'net_income':  [100e9,   97e9,   73e9,   72e9 ],
    'total_equity':[ 50e9,   62e9,  166e9,  200e9 ],
    'total_assets':[352e9,  353e9,  364e9,  411e9 ],
})

# Compute selected ratios
result = ratios_from_df(
    df,
    ratios=['gross_margin', 'net_profit_margin', 'roe', 'roa'],
    groupby='ticker',
)
print(result[['ticker', 'year', 'gross_margin', 'roe']])
```

## Inplace Mode

```python
# Add ratio columns to the original DataFrame
ratios_from_df(df, ratios=['gross_margin', 'roe'], inplace=True)
print(df.columns)  # includes 'gross_margin', 'roe'
```

## Column Name Aliases

`ratios_from_df` recognises common alternative column names:

| Standard | Aliases accepted |
|----------|-----------------|
| `revenue` | `net_sales`, `total_revenue` |
| `net_income` | `net_earnings`, `profit` |
| `total_equity` | `shareholders_equity` |
| `operating_cash_flow` | `cash_from_operations`, `ocf` |

## Polars Support

```python
import polars as pl
from fin_ratios.pandas_ext import ratios_from_df

df = pl.DataFrame({
    'ticker': ['AAPL', 'MSFT'],
    'revenue': [383e9, 212e9],
    'gross_profit': [169e9, 146e9],
})

result = ratios_from_df(df, ratios=['gross_margin'])
# Returns pl.DataFrame with added columns
```

## Available Ratios

Any ratio function in fin_ratios that takes named scalar inputs: `gross_margin`, `operating_margin`, `net_profit_margin`, `ebitda_margin`, `roe`, `roa`, `roic`, `current_ratio`, `quick_ratio`, `debt_to_equity`, `free_cash_flow`, `fcf_margin`, and more.
