# Historical Ratio Trends

Compute and analyse how key ratios have evolved over time for a given ticker.

## Usage

```python
from fin_ratios.utils.trends import ratio_history

history = ratio_history(
    ticker='AAPL',
    metrics=['gross_margin', 'roic', 'fcf_margin', 'revenue_growth'],
    years=7,
    source='edgar',  # edgar | yahoo | fmp | alphavantage
)

# Tabular view
print(history.table())

# Trend direction for each metric
print(history.trend('gross_margin'))  # 'improving' | 'stable' | 'deteriorating' | 'volatile'
print(history.trend('roic'))          # 'stable'

# CAGR over the period
print(history.cagr('revenue_growth'))

# Raw values
print(history.values('gross_margin'))  # [0.38, 0.39, 0.40, 0.41, ...]

# Rich display in Jupyter
history  # calls _repr_html_() automatically
```

## Output: `RatioHistory`

```python
@dataclass
class RatioHistory:
    ticker: str
    metrics: list[str]
    years: list[int]          # fiscal years covered
    data: dict[str, list]     # metric → list of values

    def table(self) -> str: ...
    def trend(self, metric: str) -> str: ...
    def cagr(self, metric: str) -> float | None: ...
    def values(self, metric: str) -> list: ...
    def to_dict(self) -> dict: ...
```

## Trend Detection

Trends are determined by OLS linear regression:

| Slope | CV (volatility) | Result |
|-------|----------------|--------|
| Positive | Low | `improving` |
| Negative | Low | `deteriorating` |
| Near-zero | Low | `stable` |
| Any | High | `volatile` |
