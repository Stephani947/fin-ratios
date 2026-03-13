# Earnings Quality Score

Measures how closely reported earnings track real cash generation. Low earnings quality often precedes earnings disappointments or restatements.

**Score**: 0–100 (higher = higher quality)
**Rating**: `high` (≥70) | `medium` (45–69) | `low` (20–44) | `poor` (<20)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| Accruals Ratio | 30% | (Net Income − OCF) / Total Assets; lower accruals = more cash-backed earnings (Sloan, 1996) |
| Cash Earnings Quality | 25% | OCF / Net Income over time; ratio above 1.0 means cash generation exceeds reported profit |
| Revenue Recognition Quality | 20% | Change in receivables vs revenue growth; aggressive receivables growth may signal channel stuffing or premature recognition |
| Gross Margin Stability | 15% | Coefficient of variation of gross margin; stable margins indicate genuine pricing, not accounting smoothing |
| Asset Efficiency Trend | 10% | Asset turnover trend; improving efficiency signals real operational leverage, not financial engineering |

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.earnings_quality import (
        earnings_quality_score_from_series,
        earnings_quality_score,
    )
    from fin_ratios.fetchers.edgar import fetch_edgar

    annual_data = fetch_edgar('AAPL', num_years=7)
    score = earnings_quality_score_from_series(annual_data)

    print(score.score)    # 84
    print(score.rating)   # 'high'
    print(score.table())

    # One-liner
    score = earnings_quality_score('AAPL', years=7, source='yahoo')
    ```

=== "TypeScript"

    ```typescript
    import { earningsQualityScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('AAPL')
    const score = earningsQualityScoreFromSeries(annualData)

    console.log(score.score)   // 84
    console.log(score.rating)  // 'high'
    ```

## Interpreting Accruals

The accruals ratio is the most predictive signal:

- `< −0.05` → possibly aggressive cash collection; investigate
- `−0.05 to +0.05` → healthy, earnings closely match cash
- `> +0.10` → earnings significantly exceed cash generation; risk of overstatement

## Output Structure

```python
@dataclass
class EarningsQualityScore:
    score: int
    rating: str   # high / medium / low / poor
    components: EarningsQualityComponents
    evidence: list[str]
    interpretation: str

@dataclass
class EarningsQualityComponents:
    accruals_ratio: float          # 0–1
    cash_earnings: float           # 0–1
    revenue_recognition: float     # 0–1
    gross_margin_stability: float  # 0–1
    asset_efficiency: float        # 0–1
```

## Minimum Data Requirements

- At least **3 years** of data
- `net_income`, `operating_cash_flow`, `total_assets`, `capex`, `depreciation` required

## References

- Sloan, R.G. (1996). *Do Stock Prices Fully Reflect Information in Accruals and Cash Flows About Future Earnings?* The Accounting Review.
- Richardson, S. et al. (2005). *Accrual Reliability, Earnings Persistence and Stock Prices*. Journal of Accounting and Economics.
- Penman, S. (2013). *Financial Statement Analysis and Security Valuation* (5th ed.).
