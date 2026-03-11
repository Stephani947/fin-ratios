import { describe, it, expect } from 'vitest'
import { moatScore } from '../utils/moat-score.js'

function wideMoat() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (100 + y * 15) * 1e9,
    grossProfit:        (65  + y * 10) * 1e9,
    ebit:               (30  + y * 5)  * 1e9,
    totalEquity:        40e9,
    totalDebt:          5e9,
    totalAssets:        (70  + y * 8)  * 1e9,
    cash:               20e9,
    capex:              2e9,
    depreciation:       3e9,
    interestExpense:    0.2e9,
    incomeTaxExpense:   (7 + y * 1.2) * 1e9,
    currentAssets:      (30 + y * 3) * 1e9,
    currentLiabilities: (15 + y) * 1e9,
  }))
}

function noMoat() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (80  + y * 2)   * 1e9,
    grossProfit:        (16  + y * 0.2) * 1e9,
    ebit:               (2   + y * 0.1) * 1e9,
    totalEquity:        30e9,
    totalDebt:          60e9,
    totalAssets:        (100 + y * 12)  * 1e9,
    cash:               3e9,
    capex:              18e9,
    depreciation:       8e9,
    interestExpense:    4e9,
    incomeTaxExpense:   0.3e9,
    currentAssets:      (25 + y) * 1e9,
    currentLiabilities: (30 + y * 2) * 1e9,
  }))
}

describe('moatScore', () => {
  it('returns score in 0–100 range', () => {
    const r = moatScore(wideMoat())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('returns valid width', () => {
    const r = moatScore(wideMoat())
    expect(['wide', 'narrow', 'none']).toContain(r.width)
  })

  it('throws on fewer than 2 years', () => {
    expect(() => moatScore([wideMoat()[0]!])).toThrow('at least 2 years')
  })

  it('wide moat beats no moat', () => {
    const wide = moatScore(wideMoat())
    const none = moatScore(noMoat())
    expect(wide.score).toBeGreaterThan(none.score)
  })

  it('WACC override respected', () => {
    const r = moatScore(wideMoat(), { wacc: 0.11 })
    expect(r.waccUsed).toBe(0.11)
  })

  it('components are in 0–1 range', () => {
    const r = moatScore(wideMoat())
    const c = r.components
    for (const val of [c.roicPersistence, c.pricingPower, c.reinvestmentQuality,
                       c.operatingLeverage, c.capScore]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('capEstimateYears is non-negative', () => {
    expect(moatScore(wideMoat()).capEstimateYears).toBeGreaterThanOrEqual(0)
  })

  it('years analyzed matches input', () => {
    const data = wideMoat()
    expect(moatScore(data).yearsAnalyzed).toBe(data.length)
  })
})
