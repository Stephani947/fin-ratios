# Management Quality Score

Evaluates management's track record using four quantitative signals: capital discipline, margin consistency, shareholder treatment, and revenue execution.

**Score**: 0–100
**Rating**: `excellent` (≥75) | `good` (50–74) | `fair` (25–49) | `poor` (<25)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| ROIC excellence | 35% | Average ROIC vs hurdle (default 10%); sustained excess return indicates disciplined capital use |
| Margin stability | 25% | Low coefficient of variation in operating margin signals consistent execution |
| Shareholder orientation | 25% | Dilution rate — fewer new shares = more shareholder-friendly |
| Revenue execution | 15% | CAGR of revenue; consistent growth above zero |

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.management_score import (
        management_quality_score_from_series,
        management_quality_score,
    )
    from fin_ratios.fetchers.edgar import fetch_edgar

    annual_data = fetch_edgar('MSFT', num_years=7)
    score = management_quality_score_from_series(annual_data, hurdle_rate=0.10)

    print(score.score)    # 77
    print(score.rating)   # 'excellent'
    print(score.table())

    # One-liner
    score = management_quality_score('MSFT', years=7, source='edgar')
    ```

=== "TypeScript"

    ```typescript
    import { managementQualityScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('MSFT')
    const score = managementQualityScoreFromSeries(annualData, 0.10)

    console.log(score.score)   // 77
    console.log(score.rating)  // 'excellent'
    ```

## Minimum Requirements

- At least **3 years** of data (raises `ValueError` with fewer)
- `net_income`, `total_equity`, `total_debt`, `cash`, `revenue` needed for all signals
- `shares_outstanding` needed for dilution signal (gracefully skipped if absent)

## Output Structure

```python
@dataclass
class ManagementScore:
    score: int
    rating: str  # excellent / good / fair / poor
    components: ManagementComponents
    evidence: list[str]
    interpretation: str
    hurdle_rate: float
```

## Notes

- This score does not incorporate qualitative factors (communication, compensation philosophy, governance) — add those using your own weighting on top.
- Companies in capital-intensive industries (utilities, telecoms) often score lower on ROIC; consider adjusting `hurdle_rate` downward (e.g. `0.07`).

## References

- Mauboussin, M. (2012). *The Importance of Capital Allocation*. Credit Suisse.
- Dorsey, P. (2008). *The Little Book That Builds Wealth*. Wiley.
