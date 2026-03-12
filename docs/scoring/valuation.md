# Valuation Attractiveness Score

Measures whether a stock is attractively priced based on five complementary valuation signals.

**Score**: 0–100 (higher = cheaper / more attractive)
**Rating**: `attractive` (≥65) | `fair` (40–64) | `expensive` (20–39) | `overvalued` (<20)

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| Earnings Yield vs Risk-Free | 25% | E/P − 10yr treasury; excess yield mapped to 0–1 |
| FCF Yield | 25% | FCF / Market Cap; 5%+ = high score |
| EV/EBITDA | 20% | < 8x = excellent, > 20x = poor |
| Price-to-Book | 15% | < 1.5x = excellent, > 6x = poor |
| DCF Upside | 15% | margin of safety to intrinsic value (optional) |

Missing signals receive a neutral score (0.50) so partial inputs still yield meaningful results.

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.valuation_score import valuation_attractiveness_score

    score = valuation_attractiveness_score(
        pe_ratio=15.0,         # trailing P/E
        ev_ebitda=9.0,         # EV/EBITDA
        p_fcf=14.0,            # Price/FCF
        pb_ratio=2.0,          # Price/Book
        dcf_upside_pct=25.0,   # 25% margin of safety to DCF
        risk_free_rate=0.045,  # 10yr treasury
    )

    print(score.score)          # 75
    print(score.rating)         # 'attractive'
    print(score.table())
    ```

=== "TypeScript"

    ```typescript
    import { valuationAttractivenessScore } from 'fin-ratios'

    const score = valuationAttractivenessScore({
      peRatio: 15.0,
      evEbitda: 9.0,
      pFcf: 14.0,
      pbRatio: 2.0,
      dcfUpsidePct: 25.0,
      riskFreeRate: 0.045,
    })

    console.log(score.score)   // 75
    console.log(score.rating)  // 'attractive'
    ```

## Alternative Inputs

You can provide yield percentages directly instead of ratios:

```python
score = valuation_attractiveness_score(
    earnings_yield_pct=6.5,   # 1/PE → 6.5% (overrides pe_ratio)
    fcf_yield_pct=5.2,        # FCF/MarketCap → 5.2% (overrides p_fcf)
)
```

## Earnings Yield Scoring Detail

The earnings yield signal compares E/P against the risk-free rate:

- E/P − rf = +4%+ → score 1.0 (strong equity premium)
- E/P − rf = 0% → score ~0.5 (parity with bonds)
- E/P − rf = −4% → score 0.0 (stocks yield less than bonds)

This implements the **Fed Model** logic (Yardeni, 1997), adjusted to avoid its known flaws by using excess yield rather than absolute comparison.

## References

- Damodaran, A. (2012). *Investment Valuation* (3rd ed.). Wiley.
- Greenblatt, J. (2010). *The Little Book That Still Beats the Market*.
- Shiller, R.J. (2000). *Irrational Exuberance*. Princeton University Press.
