# Quick Start

## 5-Minute Investment Analysis

The fastest path to insight: fetch data from SEC EDGAR (free, no API key) and compute all scores.

=== "Python"

    ```python
    from fin_ratios.fetchers.edgar import fetch_edgar
    from fin_ratios.utils.investment_score import investment_score_from_series
    from fin_ratios.utils.quality_score import quality_score_from_series

    # Step 1: fetch 7 years of annual data (free, no key)
    annual_data = fetch_edgar('AAPL', num_years=7)

    # Step 2: quality score (Moat + Earnings Quality + Capital Allocation)
    quality = quality_score_from_series(annual_data)
    print(quality.table())

    # Step 3: full investment score (add valuation if you have it)
    inv = investment_score_from_series(
        annual_data,
        pe_ratio=22.0,     # optional: current P/E
        ev_ebitda=14.0,    # optional: current EV/EBITDA
    )
    print(f"\n{inv.score}/100 [{inv.grade}] — {inv.conviction}")
    ```

=== "TypeScript"

    ```typescript
    import { qualityScore, investmentScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarNormalized } from 'fin-ratios/fetchers/edgar'

    const annualData = await fetchEdgarNormalized('AAPL', { numYears: 7 })

    const quality = qualityScore(annualData)
    console.log(quality.score, quality.grade)

    const inv = investmentScoreFromSeries(annualData, {
      peRatio: 22.0,
      evEbitda: 14.0,
    })
    console.log(`${inv.score}/100 [${inv.grade}] — ${inv.conviction}`)
    ```

## Bring Your Own Data

All scoring utilities accept plain dicts or dataclasses — no fetcher required.

=== "Python"

    ```python
    from fin_ratios.utils.investment_score import investment_score_from_series

    # Each dict is one fiscal year (oldest first)
    annual_data = [
        {
            "revenue": 300e9, "gross_profit": 120e9, "ebit": 60e9,
            "net_income": 48e9, "operating_cash_flow": 55e9,
            "total_assets": 280e9, "total_equity": 90e9,
            "total_debt": 80e9, "cash": 30e9,
            "capex": 8e9, "depreciation": 12e9,
            "income_tax_expense": 12e9, "ebt": 60e9,
        },
        # ... add more years
    ]

    score = investment_score_from_series(annual_data, pe_ratio=18.0)
    print(score.score, score.grade)
    ```

=== "TypeScript"

    ```typescript
    import { investmentScoreFromSeries } from 'fin-ratios'

    const annualData = [
      {
        revenue: 300e9, grossProfit: 120e9, ebit: 60e9,
        netIncome: 48e9, operatingCashFlow: 55e9,
        totalAssets: 280e9, totalEquity: 90e9,
        totalDebt: 80e9, cash: 30e9,
        capex: 8e9, depreciation: 12e9,
        incomeTaxExpense: 12e9, ebt: 60e9,
      },
      // ... add more years
    ]

    const score = investmentScoreFromSeries(annualData, { peRatio: 18.0 })
    console.log(score.score, score.grade)
    ```

## CLI Quick Start

```bash
# Install
pip install "financial-ratios[fetchers]"

# Single ticker analysis (ratios)
fin-ratios AAPL

# Full scoring dashboard
fin-ratios score AAPL

# Compare multiple tickers
fin-ratios AAPL MSFT GOOGL --compare

# JSON output for scripting
fin-ratios AAPL --json

# Start REST API
fin-ratios api --port 8000
```

## Individual Ratios

=== "Python"

    ```python
    import fin_ratios as fr

    pe_ratio   = fr.pe(market_cap=3e12, net_income=1e11)           # 30.0
    roic       = fr.roic(nopat_value=85e9, invested_capital=500e9)  # 0.17
    moat       = fr.moat_score(ticker='AAPL')                       # needs fetchers
    ```

=== "TypeScript"

    ```typescript
    import { pe, roic } from 'fin-ratios'

    const peRatio = pe({ marketCap: 3e12, netIncome: 1e11 })   // 30
    const r       = roic({ nopat: 85e9, investedCapital: 5e11 }) // 0.17
    ```

## React Hooks

```typescript
import { useRatios, useHealthScore } from 'fin-ratios/hooks'

function StockCard({ ticker }: { ticker: string }) {
  const { data, loading } = useRatios(ticker)
  const health = useHealthScore(ticker)

  if (loading) return <div>Loading...</div>
  return (
    <div>
      <p>P/E: {data?.pe}</p>
      <p>Health: {health?.score}/100</p>
    </div>
  )
}
```
