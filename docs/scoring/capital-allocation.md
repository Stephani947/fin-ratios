# Capital Allocation Score

Measures how effectively management deploys capital — the difference between a company that compounds value and one that destroys it.

**Score**: 0–100
**Rating**: `excellent` (≥75) | `good` (50–74) | `fair` (25–49) | `poor` (<25)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| ROIC vs WACC spread | 35% | (ROIC − WACC) trend; positive spread = value creation |
| FCF generation quality | 30% | FCF / Net Income and FCF margin trend |
| Reinvestment efficiency | 20% | Revenue growth per dollar of invested capital |
| Shareholder returns discipline | 15% | Buyback yield and dividend growth vs earnings growth |

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.capital_allocation import (
        capital_allocation_score_from_series,
        capital_allocation_score,
    )
    from fin_ratios.fetchers.edgar import fetch_edgar

    annual_data = fetch_edgar('MSFT', num_years=7)
    score = capital_allocation_score_from_series(annual_data, wacc=0.09)

    print(score.score)    # 78
    print(score.rating)   # 'excellent'
    print(score.table())  # signal breakdown table

    # One-liner
    score = capital_allocation_score('MSFT', years=7, source='yahoo', wacc=0.09)
    ```

=== "TypeScript"

    ```typescript
    import { capitalAllocationScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('MSFT')
    const score = capitalAllocationScoreFromSeries(annualData, 0.09)

    console.log(score.score)   // 78
    console.log(score.rating)  // 'excellent'
    ```

## Output Structure

```python
@dataclass
class CapitalAllocationScore:
    score: int
    rating: str   # excellent / good / fair / poor
    components: CapitalAllocationComponents
    evidence: list[str]
    interpretation: str
```

## Minimum Data Requirements

- At least **3 years** of data
- `net_income`, `operating_cash_flow`, `capex`, `total_equity`, `total_debt`, `cash` needed for all signals

## References

- Mauboussin, M. (2012). *The Importance of Capital Allocation*. Credit Suisse.
- Koller, T., Goedhart, M., Wessels, D. (2020). *Valuation* (7th ed.). McKinsey & Company.
