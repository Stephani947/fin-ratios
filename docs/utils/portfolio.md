# Portfolio Quality

Compute a weighted quality score across a portfolio of holdings.

## Usage

```python
from fin_ratios.utils.portfolio import portfolio_quality

holdings = [
    {'ticker': 'AAPL', 'weight': 0.30},
    {'ticker': 'MSFT', 'weight': 0.25},
    {'ticker': 'GOOGL', 'weight': 0.20},
    {'ticker': 'AMZN', 'weight': 0.15},
    {'ticker': 'NVDA', 'weight': 0.10},
]

result = portfolio_quality(
    holdings=holdings,
    years=5,
    source='yahoo',
    wacc=0.09,
)

print(result.weighted_score)       # e.g. 74
print(result.weighted_grade)       # e.g. 'B+'
print(result.table())              # breakdown by holding

# Individual holding details
for h in result.holdings:
    print(f"{h.ticker}: {h.score} ({h.grade}), weight={h.weight:.0%}")
```

## Pre-computed Scores

If you already have scores computed, skip the fetch:

```python
from fin_ratios.utils.portfolio import PortfolioQuality, HoldingQuality

result = PortfolioQuality(
    holdings=[
        HoldingQuality(ticker='AAPL', score=82, grade='A', weight=0.30),
        HoldingQuality(ticker='MSFT', score=78, grade='B+', weight=0.25),
        HoldingQuality(ticker='GOOGL', score=71, grade='B+', weight=0.20),
        HoldingQuality(ticker='AMZN', score=68, grade='B', weight=0.15),
        HoldingQuality(ticker='NVDA', score=59, grade='C', weight=0.10),
    ]
)

print(result.weighted_score)   # weighted average
```

## Output: `PortfolioQuality`

```python
@dataclass
class PortfolioQuality:
    weighted_score: float
    weighted_grade: str
    holdings: list[HoldingQuality]

    def table(self) -> str: ...
    def to_dict(self) -> dict: ...

@dataclass
class HoldingQuality:
    ticker: str
    score: int
    grade: str
    weight: float
    score_detail: Optional[QualityFactorScore] = None
```
