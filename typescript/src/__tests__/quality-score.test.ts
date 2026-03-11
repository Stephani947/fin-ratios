import { describe, it, expect } from 'vitest'
import { qualityScore } from '../utils/quality-score.js'
import { portfolioQuality } from '../utils/portfolio.js'

function excellentCompany() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (100 + y * 15) * 1e9,
    grossProfit:        (65  + y * 10) * 1e9,
    ebit:               (30  + y * 5)  * 1e9,
    netIncome:          (22  + y * 4)  * 1e9,
    operatingCashFlow:  (26  + y * 4.5) * 1e9,
    totalEquity:        40e9,
    totalDebt:          5e9,
    totalAssets:        (70  + y * 8)  * 1e9,
    cash:               20e9,
    capex:              2e9,
    depreciation:       3e9,
    interestExpense:    0.2e9,
    incomeTaxExpense:   (6 + y * 1.2) * 1e9,
    currentAssets:      (30 + y * 3)  * 1e9,
    currentLiabilities: (15 + y)      * 1e9,
    accountsReceivable: (8  + y * 1)  * 1e9,
  }))
}

function weakCompany() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:            (80  + y * 2)   * 1e9,
    grossProfit:        (20  + y * 0.3) * 1e9,
    ebit:               (4   + y * 0.2) * 1e9,
    netIncome:          (5   + y * 0.3) * 1e9,
    operatingCashFlow:  (2   + y * 0.1) * 1e9,
    totalEquity:        30e9,
    totalDebt:          50e9,
    totalAssets:        (100 + y * 12)  * 1e9,
    cash:               3e9,
    capex:              15e9,
    depreciation:       8e9,
    interestExpense:    3.5e9,
    incomeTaxExpense:   0.5e9,
    currentAssets:      (25 + y) * 1e9,
    currentLiabilities: (28 + y * 2) * 1e9,
    accountsReceivable: (10 + y * 3) * 1e9,
  }))
}

describe('qualityScore', () => {
  it('returns score in 0–100', () => {
    const r = qualityScore(excellentCompany())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('returns valid grade', () => {
    const r = qualityScore(excellentCompany())
    expect(['exceptional', 'strong', 'moderate', 'weak', 'poor']).toContain(r.grade)
  })

  it('throws on fewer than 2 years', () => {
    expect(() => qualityScore([excellentCompany()[0]!])).toThrow('at least 2 years')
  })

  it('excellent beats weak', () => {
    const exc  = qualityScore(excellentCompany())
    const weak = qualityScore(weakCompany())
    expect(exc.score).toBeGreaterThan(weak.score)
  })

  it('components are in 0–1 range', () => {
    const r = qualityScore(excellentCompany())
    const c = r.components
    for (const val of [c.earningsQuality, c.moat, c.capitalAllocation]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('subScores has all three keys', () => {
    const r = qualityScore(excellentCompany())
    expect(r.subScores.earningsQuality).toBeDefined()
    expect(r.subScores.moat).toBeDefined()
    expect(r.subScores.capitalAllocation).toBeDefined()
  })

  it('evidence contains all three dimension names', () => {
    const r = qualityScore(excellentCompany())
    const text = r.evidence.join(' ')
    expect(text).toMatch(/Earnings Quality/)
    expect(text).toMatch(/Moat/)
    expect(text).toMatch(/Capital Allocation/)
  })

  it('WACC override propagates to sub-scores', () => {
    const r = qualityScore(excellentCompany(), { wacc: 0.11 })
    expect(r.subScores.moat.waccUsed).toBe(0.11)
    expect(r.subScores.capitalAllocation.waccUsed).toBe(0.11)
  })

  it('years analyzed matches input', () => {
    const data = excellentCompany()
    expect(qualityScore(data).yearsAnalyzed).toBe(data.length)
  })
})

describe('portfolioQuality', () => {
  const holdings = [
    { ticker: 'GOOD', weight: 0.6, annualData: excellentCompany() },
    { ticker: 'WEAK', weight: 0.4, annualData: weakCompany() },
  ]

  it('returns valid result', () => {
    const r = portfolioQuality(holdings)
    expect(r.weightedQualityScore).toBeGreaterThanOrEqual(0)
    expect(r.weightedQualityScore).toBeLessThanOrEqual(100)
  })

  it('grade is valid', () => {
    const r = portfolioQuality(holdings)
    expect(['exceptional', 'strong', 'moderate', 'weak', 'poor']).toContain(r.grade)
  })

  it('throws on empty holdings', () => {
    expect(() => portfolioQuality([])).toThrow('non-empty')
  })

  it('holdings count matches input', () => {
    const r = portfolioQuality(holdings)
    expect(r.holdings.length).toBe(2)
  })

  it('weighted score between component scores', () => {
    const r = portfolioQuality(holdings)
    const scores = r.holdings.filter(h => h.quality).map(h => h.quality!.score)
    expect(r.weightedQualityScore).toBeGreaterThanOrEqual(Math.min(...scores) - 1)
    expect(r.weightedQualityScore).toBeLessThanOrEqual(Math.max(...scores) + 1)
  })

  it('error holdings excluded from average', () => {
    const bad = [{ ticker: 'BAD', weight: 0.5, annualData: [excellentCompany()[0]!] }]
    const good = [{ ticker: 'GOOD', weight: 0.5, annualData: excellentCompany() }]
    const r = portfolioQuality([...good, ...bad])
    expect(r.errors.length).toBeGreaterThan(0)
    expect(r.effectiveWeight).toBeLessThan(1.0)
  })

  it('normalises weights', () => {
    const r = portfolioQuality([
      { ticker: 'A', weight: 30, annualData: excellentCompany() },
      { ticker: 'B', weight: 70, annualData: weakCompany() },
    ])
    const total = r.holdings.reduce((s, h) => s + h.weight, 0)
    expect(Math.abs(total - 1.0)).toBeLessThan(1e-9)
  })
})
