# Quality Factor Score

A composite score that blends Earnings Quality, Economic Moat, and Capital Allocation into a single quality grade — the quantitative definition of a "quality" stock.

**Score**: 0–100
**Grade**: `exceptional` (≥85) | `high` (70–84) | `above_average` (55–69) | `average` (40–54) | `below_average` (25–39) | `poor` (<25)

## Weights

| Component | Weight |
|-----------|--------|
| Earnings Quality | 35% |
| Economic Moat | 35% |
| Capital Allocation | 30% |

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.quality_score import quality_score_from_series, quality_score
    from fin_ratios.fetchers.edgar import fetch_edgar

    annual_data = fetch_edgar('AAPL', num_years=7)
    score = quality_score_from_series(annual_data, wacc=0.09)

    print(score.score)     # 80
    print(score.grade)     # 'high'
    print(score.table())   # full breakdown

    # One-liner
    score = quality_score('AAPL', years=7, source='yahoo', wacc=0.09)
    ```

=== "TypeScript"

    ```typescript
    import { qualityScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('AAPL')
    const score = qualityScoreFromSeries(annualData, 0.09)

    console.log(score.score)   // 80
    console.log(score.grade)   // 'high'
    ```

## Output Structure

```python
@dataclass
class QualityFactorScore:
    score: int
    grade: str
    components: QualityComponents
    evidence: list[str]
    interpretation: str

@dataclass
class QualityComponents:
    earnings_quality: Optional[int]
    moat: Optional[int]
    capital_allocation: Optional[int]
```

## Use with Portfolio

The quality score is designed to be used as a screening and ranking tool:

```python
from fin_ratios.utils.portfolio import PortfolioQuality
from fin_ratios.utils.quality_score import quality_score

holdings = [
    {'ticker': 'AAPL', 'weight': 0.30},
    {'ticker': 'MSFT', 'weight': 0.25},
    {'ticker': 'GOOGL', 'weight': 0.20},
    {'ticker': 'NVDA', 'weight': 0.25},
]

# Compute individual quality scores
scored = [
    quality_score(h['ticker'], years=5, source='yahoo')
    for h in holdings
]

# Weighted portfolio quality
portfolio = PortfolioQuality(
    holdings=[
        {'score': s.score, 'weight': h['weight']}
        for s, h in zip(scored, holdings)
    ]
)
print(portfolio.weighted_score)
```

## References

- Asness, C., Frazzini, A., Pedersen, L.H. (2019). *Quality Minus Junk*. Review of Accounting Studies.
- Novy-Marx, R. (2013). *The Other Side of Value: The Gross Profitability Premium*. Journal of Financial Economics.
