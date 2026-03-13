# Peer Comparison

Fetch and compare key financial metrics across a group of peer companies.

## Setup

```bash
pip install "financial-ratios[fetchers]"
```

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.peers import compare_peers

    comparison = compare_peers(
        ticker='AAPL',
        metrics=['gross_margin', 'roic', 'fcf_margin', 'net_debt_to_ebitda'],
        peers=['MSFT', 'GOOGL', 'META'],
        years=5,
        source='yahoo',  # 'yahoo' | 'edgar' | 'fmp'
    )

    # Formatted table
    print(comparison.table())
    #           gross_margin  roic  fcf_margin  net_debt/ebitda
    # AAPL            0.44  0.26        0.27             0.8
    # MSFT            0.69  0.27        0.34            -0.1
    # GOOGL           0.56  0.19        0.25            -0.4
    # META            0.81  0.27        0.36            -1.1

    # Rank AAPL in the peer group (1 = best)
    print(comparison.rank('AAPL', 'roic'))            # e.g. 2
    print(comparison.percentile('AAPL', 'gross_margin'))  # e.g. 25th percentile

    # Access raw values
    aapl_gm = comparison.data['AAPL']['gross_margin']

    # Export to dict / JSON
    d = comparison.to_dict()
    ```

## Automatic Peer Lookup

If you omit `peers`, a built-in sector peer map is used (covers 20+ major tickers):

```python
comparison = compare_peers(
    ticker='AAPL',
    metrics=['gross_margin', 'roic'],
    # peers not specified — uses built-in map
)
```

## Output: `PeerComparison`

```python
@dataclass
class PeerComparison:
    tickers: list[str]
    metrics: list[str]
    data: dict[str, dict[str, float | None]]  # ticker → metric → value

    def table(self) -> str
    def rank(self, ticker: str, metric: str) -> int
    def percentile(self, ticker: str, metric: str) -> float
    def to_dict(self) -> dict
```

Jupyter notebooks display a styled HTML table via `_repr_html_()`.

## Notes

- Requires network access; all tickers are fetched from the specified source
- Metric values represent the most recently available fiscal year
- Missing data for a ticker-metric pair returns `None` (not an error)
