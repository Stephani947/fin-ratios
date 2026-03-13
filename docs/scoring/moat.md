# Economic Moat Score

Measures the durability of a company's competitive advantage using five quantitative signals derived from annual financial statements.

**Score**: 0–100 (higher = wider moat)
**Width**: `wide` (≥65) | `narrow` (40–64) | `none` (<40)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| ROIC Persistence | 30% | Average ROIC vs WACC hurdle across years; sustained excess returns signal a durable advantage |
| Pricing Power | 25% | Gross margin level and stability; high, stable gross margins indicate pricing authority over suppliers and customers |
| Reinvestment Quality | 20% | Incremental return on invested capital (ROIIC); high returns on new capital signal a scalable moat |
| Operating Leverage | 15% | Revenue growth relative to asset growth; asset-light growth indicates structural efficiency advantage |
| CAP Estimate | 10% | Competitive Advantage Period — projected years of above-WACC returns, based on ROIC spread and its stability |

Default WACC hurdle: **10%**. Override with `wacc=0.08` for capital-light businesses.

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.moat_score import moat_score_from_series, moat_score
    from fin_ratios.fetchers.edgar import fetch_edgar

    # From raw annual data (oldest first)
    annual_data = fetch_edgar('AAPL', num_years=7)
    score = moat_score_from_series(annual_data, wacc=0.09)

    print(score.score)     # 82
    print(score.width)     # 'wide'
    print(score.table())   # formatted signal breakdown

    # One-liner (fetches automatically)
    score = moat_score('AAPL', years=7, source='edgar', wacc=0.09)
    ```

=== "TypeScript"

    ```typescript
    import { moatScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('AAPL')
    const score = moatScoreFromSeries(annualData, 0.09)

    console.log(score.score)   // 82
    console.log(score.width)   // 'wide'
    ```

## Output Structure

```python
@dataclass
class MoatScore:
    score: int              # 0–100
    width: str              # wide / narrow / none
    components: MoatComponents
    evidence: list[str]
    interpretation: str

@dataclass
class MoatComponents:
    roic_persistence: float      # 0–1
    pricing_power: float         # 0–1
    reinvestment_quality: float  # 0–1
    operating_leverage: float    # 0–1
    cap_score: float             # 0–1

# cap_estimate_years is a top-level field on MoatScore (not in components)
```

## Minimum Data Requirements

- At least **3 years** of data for a meaningful score
- 5+ years recommended for ROIC persistence signal
- `ebit`, `income_tax_expense`, `invested_capital` (or `total_equity` + `total_debt` + `cash`) required for ROIC

## References

- Mauboussin, M. & Callahan, D. (2013). *Measuring the Moat: Assessing the Magnitude and Sustainability of Value Creation*.
- Morningstar Economic Moat methodology.
- Buffett, W. (1999 Letter to Berkshire Shareholders) — moat as durable competitive advantage.
