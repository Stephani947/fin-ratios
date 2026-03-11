import { describe, it, expect } from 'vitest'
import { earningsQualityScore } from '../utils/earnings-quality.js'

function highQuality() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (100 + y * 12) * 1e9,
    grossProfit:        (65  + y * 8)  * 1e9,
    netIncome:          (18  + y * 2)  * 1e9,
    operatingCashFlow:  (22  + y * 2.5) * 1e9,
    totalAssets:        (80  + y * 6)  * 1e9,
    accountsReceivable: (8   + y * 0.8) * 1e9,
  }))
}

function poorQuality() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (80  + y * 3)  * 1e9,
    grossProfit:        (28  + y * 0.5) * 1e9,
    netIncome:          (10  + y * 1)  * 1e9,
    operatingCashFlow:  (4   + y * 0.1) * 1e9,
    totalAssets:        (120 + y * 15) * 1e9,
    accountsReceivable: (15  + y * 3)  * 1e9,
  }))
}

describe('earningsQualityScore', () => {
  it('returns score in 0–100 range', () => {
    const r = earningsQualityScore(highQuality())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('returns valid rating', () => {
    const r = earningsQualityScore(highQuality())
    expect(['high', 'medium', 'low', 'poor']).toContain(r.rating)
  })

  it('components are in 0–1 range', () => {
    const r = earningsQualityScore(highQuality())
    const c = r.components
    for (const val of [c.accrualsRatio, c.cashEarnings, c.revenueRecognition,
                       c.grossMarginStability, c.assetEfficiency]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('throws on fewer than 2 years', () => {
    expect(() => earningsQualityScore([highQuality()[0]!])).toThrow('at least 2 years')
  })

  it('high quality beats poor quality', () => {
    const high = earningsQualityScore(highQuality())
    const poor = earningsQualityScore(poorQuality())
    expect(high.score).toBeGreaterThan(poor.score)
  })

  it('years analyzed matches input length', () => {
    const data = highQuality()
    expect(earningsQualityScore(data).yearsAnalyzed).toBe(data.length)
  })

  it('evidence array is non-empty', () => {
    expect(earningsQualityScore(highQuality()).evidence.length).toBeGreaterThan(0)
  })

  it('works without optional fields (CFO, AR)', () => {
    const minimal = Array.from({ length: 3 }, (_, y) => ({
      revenue: (100 + y * 10) * 1e9,
      grossProfit: (50 + y * 5) * 1e9,
      netIncome: (12 + y) * 1e9,
      totalAssets: (80 + y * 5) * 1e9,
    }))
    const r = earningsQualityScore(minimal)
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })
})
