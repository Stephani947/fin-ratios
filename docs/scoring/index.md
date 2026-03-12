# Scoring Models

fin-ratios provides 8 institutional-grade scoring models that measure distinct dimensions of business quality and investment attractiveness.

## Overview

| Model | Input | Output | Min Years |
|-------|-------|--------|-----------|
| [Economic Moat](moat.md) | Annual time-series | 0–100, wide/narrow/none | 3 |
| [Capital Allocation](capital-allocation.md) | Annual time-series | 0–100, excellent–poor | 2 |
| [Earnings Quality](earnings-quality.md) | Annual time-series | 0–100, high–poor | 2 |
| [Quality Factor](quality-factor.md) | Annual time-series | 0–100, A–F | 3 |
| [Valuation Attractiveness](valuation.md) | Point-in-time snapshot | 0–100, attractive–overvalued | — |
| [Management Quality](management.md) | Annual time-series | 0–100, excellent–poor | 3 |
| [Dividend Safety](dividend-safety.md) | Annual time-series | 0–100, safe–danger/non-payer | 2 |
| [Investment Score](investment.md) | All of the above | 0–100, A+–F, conviction | 3 |

## Common Pattern

All time-series models follow the same API:

=== "Python"

    ```python
    # Pattern 1: bring your own data
    from fin_ratios.utils.moat_score import moat_score_from_series
    score = moat_score_from_series(annual_data)

    # Pattern 2: fetch from ticker
    from fin_ratios.utils.moat_score import moat_score
    score = moat_score(ticker='AAPL', years=7, source='edgar')

    # All results have the same interface
    print(score.score)         # int 0–100
    print(score.rating)        # 'wide' | 'narrow' | 'none'
    print(score.table())       # formatted text table
    print(score.to_dict())     # dict for JSON/API
    score._repr_html_()        # Jupyter rich display
    ```

=== "TypeScript"

    ```typescript
    import { moatScore } from 'fin-ratios'

    const score = moatScore(annualData)
    console.log(score.score)    // number 0–100
    console.log(score.rating)   // 'wide' | 'narrow' | 'none'
    console.log(score.evidence) // string[]
    ```

## Weighting in Investment Score

When combined into the [Investment Score](investment.md), models are weighted as:

| Model | Weight |
|-------|--------|
| Economic Moat | 25% |
| Capital Allocation | 20% |
| Earnings Quality | 20% |
| Management Quality | 15% |
| Valuation Attractiveness | 20% |

If Valuation is not provided, its 20% is redistributed proportionally across the other four.

## Score Interpretation Guide

| Range | Interpretation |
|-------|----------------|
| 75–100 | Excellent / Wide Moat / Safe |
| 50–74 | Good / Narrow Moat / Adequate |
| 25–49 | Fair / No Moat / Risky |
| 0–24 | Poor / Danger |
