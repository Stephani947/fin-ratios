# Peer Comparison

Compare key metrics across a set of peer companies.

## Usage

```python
from fin_ratios.utils.peers import compare_peers

comparison = compare_peers(
    ticker='AAPL',
    metrics=['gross_margin', 'roic', 'fcf_margin', 'net_debt_to_ebitda'],
    peers=['MSFT', 'GOOGL', 'META'],
    years=5,
    source='yahoo',
)

# Table output
print(comparison.table())

# Access individual data
print(comparison.data['AAPL']['gross_margin'])  # e.g. 0.43
print(comparison.rank('AAPL', 'roic'))          # e.g. 1 (best)
print(comparison.percentile('AAPL', 'roic'))    # e.g. 95th percentile in peer group
```

## Output: `PeerComparison`

```python
@dataclass
class PeerComparison:
    tickers: list[str]
    metrics: list[str]
    data: dict[str, dict[str, float | None]]  # ticker → metric → value

    def table(self) -> str: ...
    def rank(self, ticker: str, metric: str) -> int: ...
    def percentile(self, ticker: str, metric: str) -> float: ...
    def to_dict(self) -> dict: ...
```

## Notes

- Data is fetched live from the specified source; network calls are required
- Add the `[fetchers]` extra: `pip install "financial-ratios[fetchers]"`
- Metric values are the most recent available year
