# Economic Moat Score

Measures the durability of a company's competitive advantage using five quantitative signals derived from annual financial statements.

**Score**: 0–100 (higher = wider moat)
**Width**: `wide` (≥65) | `narrow` (40–64) | `none` (<40)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| ROIC persistence | 30% | ROIC trend over 5+ years, adjusted for WACC hurdle |
| Gross margin stability | 25% | Coefficient of variation of gross margin |
| FCF conversion quality | 20% | FCF / Net Income consistency |
| Reinvestment yield | 15% | (CapEx + R&D) / Revenue — sustaining investment |
| Revenue growth durability | 10% | Revenue CAGR and growth consistency |

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
    roic_persistence: Optional[float]
    gross_margin_stability: Optional[float]
    fcf_conversion: Optional[float]
    reinvestment_yield: Optional[float]
    revenue_durability: Optional[float]
```

## Minimum Data Requirements

- At least **3 years** of data for a meaningful score
- 5+ years recommended for ROIC persistence signal
- `ebit`, `income_tax_expense`, `invested_capital` (or `total_equity` + `total_debt` + `cash`) required for ROIC

## References

- Mauboussin, M. & Callahan, D. (2013). *Measuring the Moat: Assessing the Magnitude and Sustainability of Value Creation*.
- Morningstar Economic Moat methodology.
- Buffett, W. (1999 Letter to Berkshire Shareholders) — moat as durable competitive advantage.
