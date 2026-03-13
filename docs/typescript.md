# TypeScript API

All ratio functions and scoring utilities are available in TypeScript with full type safety.

## Installation

```bash
npm install fin-ratios
```

**Requires Node.js ≥ 18**

## Core Ratios

```typescript
import {
  pe, pb, ps, peg, evEbitda, grahamNumber,
  roe, roa, roic, grossMargin, operatingMargin,
  currentRatio, quickRatio, debtToEquity,
  freeCashFlow, fcfMargin, fcfYield,
  revenueGrowth, revenueCAGR,
  sharpeRatio, maximumDrawdown, historicalVaR,
  altmanZScore, piotroski,
} from 'fin-ratios'

// P/E ratio
pe({ marketCap: 3e12, netIncome: 1e11 })  // 30.0

// ROIC
roic({ nopat: 85e9, investedCapital: 600e9 })  // 0.142

// DCF
import { dcf2Stage } from 'fin-ratios'
const intrinsic = dcf2Stage({
  fcf: 72e9, growthStage1: 0.10, growthStage2: 0.04,
  wacc: 0.09, stage1Years: 5, terminalGrowth: 0.03,
})
```

## Scoring Utilities

```typescript
import {
  investmentScoreFromSeries,
  investmentScoreFromScores,
  qualityScoreFromSeries,
  moatScoreFromSeries,
  capitalAllocationScoreFromSeries,
  earningsQualityScoreFromSeries,
  valuationAttractivenessScore,
  managementQualityScoreFromSeries,
  dividendSafetyScoreFromSeries,
} from 'fin-ratios'

const score = investmentScoreFromSeries(annualData, {
  peRatio: 28.0,
  evEbitda: 18.0,
})
// { score: 74, grade: 'B+', conviction: 'buy', ... }
```

## Data Fetchers

```typescript
// SEC EDGAR (free, no key)
import { fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'
const data = await fetchEdgarFlat('AAPL', { numYears: 7 })

// Yahoo Finance
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'
const data2 = await fetchYahoo('AAPL')

// FMP
import { fetchFmp } from 'fin-ratios/fetchers/fmp'
const data3 = await fetchFmp('AAPL', { apiKey: 'YOUR_KEY' })

// Polygon.io
import { fetchPolygon, setPolygonApiKey } from 'fin-ratios/fetchers/polygon'
setPolygonApiKey('YOUR_KEY')
const data4 = await fetchPolygon('AAPL', { years: 5 })
```

## React Hooks

```typescript
import { useRatios, useHealthScore, useScenarioDcf } from 'fin-ratios/hooks'
```

See [React Hooks](integrations/react.md) for full documentation.

## Type Safety Notes

- **`noUncheckedIndexedAccess`** is enabled: array indexing returns `T | undefined`. Use the `!` assertion when bounds are known: `arr[0]!`.
- All ratio functions return `number | null` (never `NaN`).
- Scoring functions return typed result objects with full type definitions.

## ESM and CommonJS

The package ships both ESM (`.js`) and CommonJS (`.cjs`) builds:

```typescript
// ESM (recommended)
import { pe } from 'fin-ratios'

// CommonJS
const { pe } = require('fin-ratios')
```

Both formats include TypeScript declaration files (`.d.ts`).
