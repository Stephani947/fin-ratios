# Dividend Safety Score

Assesses how sustainable a company's dividend is using four signals covering cash generation, earnings coverage, balance sheet strength, and track record.

**Score**: 0–100
**Rating**: `safe` (≥70) | `adequate` (45–69) | `risky` (20–44) | `danger` (<20) | `non-payer`

Companies that have never paid a dividend receive a `non-payer` rating (score 50) — no penalty, no reward.

## Signals

| Signal | Weight | Logic |
|--------|--------|-------|
| FCF payout ratio | 35% | Dividends / FCF; <50% is safe, >100% is unsustainable |
| Earnings payout ratio | 25% | Dividends / Net Income; <60% comfortable |
| Balance sheet strength | 25% | Net Debt / EBITDA; low leverage = more cushion for dividend |
| Dividend growth track | 15% | Number of years of consecutive dividend growth |

## Usage

=== "Python"

    ```python
    from fin_ratios.utils.dividend_score import (
        dividend_safety_score_from_series,
        dividend_safety_score,
    )
    from fin_ratios.fetchers.edgar import fetch_edgar

    annual_data = fetch_edgar('JNJ', num_years=7)
    score = dividend_safety_score_from_series(annual_data)

    print(score.score)             # 82
    print(score.rating)            # 'safe'
    print(score.is_dividend_payer) # True
    print(score.table())

    # One-liner
    score = dividend_safety_score('JNJ', years=7, source='yahoo')
    ```

=== "TypeScript"

    ```typescript
    import { dividendSafetyScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarFlat('JNJ')
    const score = dividendSafetyScoreFromSeries(annualData)

    console.log(score.score)            // 82
    console.log(score.rating)           // 'safe'
    console.log(score.isDividendPayer)  // true
    ```

## Minimum Requirements

- At least **2 years** of data
- `dividends_paid`, `operating_cash_flow`, `capex`, `net_income`, `total_debt`, `cash`, `ebitda` (or `ebit` + `depreciation`) required

## Output Structure

```python
@dataclass
class DividendSafetyScore:
    score: int
    rating: str   # safe / adequate / risky / danger / non-payer
    is_dividend_payer: bool
    components: DividendComponents
    evidence: list[str]
    interpretation: str
```

## Non-Payer Handling

```python
score = dividend_safety_score('GOOGL', years=5, source='yahoo')
print(score.rating)            # 'non-payer'
print(score.is_dividend_payer) # False
print(score.score)             # 50 (neutral)
```

## References

- Siegel, J. (2014). *Stocks for the Long Run* (5th ed.). McGraw-Hill.
- Dividend Aristocrats methodology (S&P Global).
