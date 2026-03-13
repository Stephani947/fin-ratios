# React Hooks

fin-ratios ships React hooks for building financial dashboards. Hooks are in the `fin-ratios/hooks` sub-path.

## Installation

```bash
npm install fin-ratios
# React is a peer dependency — install separately if needed
npm install react
```

## Available Hooks

### `useRatios`

Fetch and compute ratios for a ticker:

```typescript
import { useRatios } from 'fin-ratios/hooks'

function StockCard({ ticker }: { ticker: string }) {
  const { data, loading, error } = useRatios(ticker)

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error.message}</p>

  return (
    <div>
      <p>P/E: {data?.pe?.toFixed(1)}</p>
      <p>ROE: {((data?.roe ?? 0) * 100).toFixed(1)}%</p>
    </div>
  )
}
```

### `useRatio`

Single ratio with custom inputs:

```typescript
import { useRatio } from 'fin-ratios/hooks'

const { value } = useRatio('pe', { marketCap: 3e12, netIncome: 1e11 })
// value = 30
```

### `useHealthScore`

Overall financial health score (0–100):

```typescript
import { useHealthScore } from 'fin-ratios/hooks'

const { score, grade, loading } = useHealthScore(ticker)
// score = 74, grade = 'B+'
```

### `useScenarioDcf`

Three-scenario DCF valuation:

```typescript
import { useScenarioDcf } from 'fin-ratios/hooks'

const { bear, base, bull, loading } = useScenarioDcf({
  ticker,
  wacc: 0.09,
  currentPrice: 185,
})
```

### `useCompareRatios`

Side-by-side comparison across multiple tickers:

```typescript
import { useCompareRatios } from 'fin-ratios/hooks'

const { data, loading } = useCompareRatios(
  ['AAPL', 'MSFT', 'GOOGL'],
  ['pe', 'roe', 'fcf_margin'],
)
```

## Notes

- Hooks use the Yahoo Finance fetcher internally — no API key required
- Data is fetched client-side; for server-side rendering use the core functions directly
- React 18+ required
