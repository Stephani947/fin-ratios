# Investment Score

The Investment Score is a grand synthesis of all scoring models into a single, actionable rating.

**Score**: 0–100
**Grade**: `A+` (≥90) | `A` (80–89) | `B+` (70–79) | `B` (60–69) | `C` (45–59) | `D` (25–44) | `F` (<25)
**Conviction**: `strong_buy` | `buy` | `hold` | `sell` | `strong_sell`

## Weights

| Component | Weight | Notes |
|-----------|--------|-------|
| Economic Moat | 25% | Business durability |
| Capital Allocation | 20% | Management discipline |
| Earnings Quality | 20% | Accruals and cash backing |
| Management Quality | 15% | ROIC trend, margins, dilution |
| Valuation | 20% | Attractiveness vs intrinsic value |

If Valuation is omitted, its 20% is redistributed proportionally.

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.investment_score import (
        investment_score_from_series,
        investment_score_from_scores,
    )
    from fin_ratios.fetchers.edgar import fetch_edgar

    # Option A: from raw annual data
    annual_data = fetch_edgar('AAPL', num_years=7)
    score = investment_score_from_series(
        annual_data,
        pe_ratio=22.0,     # optional valuation inputs
        ev_ebitda=14.0,
    )
    print(score.score, score.grade, score.conviction)
    # → 74 B+ buy

    # Option B: from pre-computed sub-scores
    score = investment_score_from_scores(
        moat_score=78,
        capital_allocation_score=71,
        earnings_quality_score=82,
        management_score=68,
        valuation_score=45,
    )
    ```

=== "TypeScript"

    ```typescript
    import { investmentScoreFromSeries, investmentScoreFromScores } from 'fin-ratios'
    import { fetchEdgarNormalized } from 'fin-ratios/fetchers/edgar'

    // Option A: from raw annual data
    const annualData = await fetchEdgarNormalized('AAPL', { numYears: 7 })
    const score = investmentScoreFromSeries(annualData, {
      peRatio: 22.0,
      evEbitda: 14.0,
    })
    console.log(score.score, score.grade, score.conviction)

    // Option B: from pre-computed scores
    const score2 = investmentScoreFromScores({
      moatScore: 78,
      capitalAllocationScore: 71,
      earningsQualityScore: 82,
      managementScore: 68,
      valuationScore: 45,
    })
    ```

## Output Structure

```python
@dataclass
class InvestmentScore:
    score: int              # 0–100
    grade: str              # A+ / A / B+ / B / C / D / F
    conviction: str         # strong_buy / buy / hold / sell / strong_sell
    components: InvestmentComponents
    evidence: list[str]
    interpretation: str

@dataclass
class InvestmentComponents:
    moat: Optional[int]
    capital_allocation: Optional[int]
    earnings_quality: Optional[int]
    management: Optional[int]
    valuation: Optional[int]
```

## Conviction Mapping

| Score Range | Conviction |
|-------------|------------|
| ≥ 80 | Strong Buy |
| 65–79 | Buy |
| 45–64 | Hold |
| 25–44 | Sell |
| < 25 | Strong Sell |
