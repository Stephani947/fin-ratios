import { describe, it, expect } from 'vitest'
import {
  investmentScoreFromScores,
  investmentScoreFromSeries,
} from '../utils/investment-score.js'
import type { AnnualQualityData } from '../utils/investment-score.js'

// ── helpers ───────────────────────────────────────────────────────────────────

/** 4 years of high-quality annual data: strong moat, high ROIC, growing revenue */
function highQualitySeries(): AnnualQualityData[] {
  return [
    {
      year: 2020,
      revenue:           100e9,
      grossProfit:        65e9,
      ebit:               25e9,
      netIncome:          20e9,
      operatingCashFlow:  22e9,
      totalAssets:        80e9,
      totalEquity:        40e9,
      totalDebt:           8e9,
      cash:                5e9,
      capex:               2e9,
      depreciation:        3e9,
      incomeTaxExpense:    5.2e9,
      ebt:                24.5e9,
      interestExpense:     0.5e9,
      accountsReceivable:  6e9,
    },
    {
      year: 2021,
      revenue:           118e9,
      grossProfit:        77e9,
      ebit:               30e9,
      netIncome:          24e9,
      operatingCashFlow:  26e9,
      totalAssets:        90e9,
      totalEquity:        44e9,
      totalDebt:           7e9,
      cash:                7e9,
      capex:               2.2e9,
      depreciation:        3.2e9,
      incomeTaxExpense:    6.3e9,
      ebt:                29.4e9,
      interestExpense:     0.4e9,
      accountsReceivable:  7e9,
    },
    {
      year: 2022,
      revenue:           138e9,
      grossProfit:        90e9,
      ebit:               36e9,
      netIncome:          29e9,
      operatingCashFlow:  31e9,
      totalAssets:       100e9,
      totalEquity:        49e9,
      totalDebt:           6e9,
      cash:                9e9,
      capex:               2.5e9,
      depreciation:        3.5e9,
      incomeTaxExpense:    7.5e9,
      ebt:                35.5e9,
      interestExpense:     0.35e9,
      accountsReceivable:  8e9,
    },
    {
      year: 2023,
      revenue:           160e9,
      grossProfit:       104e9,
      ebit:               43e9,
      netIncome:          34e9,
      operatingCashFlow:  37e9,
      totalAssets:       112e9,
      totalEquity:        54e9,
      totalDebt:           5e9,
      cash:               11e9,
      capex:               2.8e9,
      depreciation:        3.8e9,
      incomeTaxExpense:    8.9e9,
      ebt:                42.6e9,
      interestExpense:     0.3e9,
      accountsReceivable:  9e9,
    },
  ]
}

// ── investmentScoreFromScores ─────────────────────────────────────────────────

describe('investmentScoreFromScores', () => {
  it('all high sub-scores → score ≥ 75 and conviction buy or strongBuy', () => {
    const r = investmentScoreFromScores({
      moatScore:              80,
      capitalAllocationScore: 75,
      earningsQualityScore:   80,
      managementScore:        75,
      valuationScore:         70,
    })
    expect(r.score).toBeGreaterThanOrEqual(75)
    expect(['buy', 'strongBuy']).toContain(r.conviction)
  })

  it('all low sub-scores → score ≤ 30 and conviction sell or strongSell', () => {
    const r = investmentScoreFromScores({
      moatScore:              20,
      capitalAllocationScore: 25,
      earningsQualityScore:   25,
      managementScore:        20,
      valuationScore:         15,
    })
    expect(r.score).toBeLessThanOrEqual(30)
    expect(['sell', 'strongSell']).toContain(r.conviction)
  })

  it('missing valuationScore → still returns valid InvestmentScore', () => {
    const r = investmentScoreFromScores({
      moatScore:              70,
      capitalAllocationScore: 65,
      earningsQualityScore:   68,
      managementScore:        72,
    })
    expect(typeof r.score).toBe('number')
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
    expect(r.components.valuation).toBeNull()
  })

  it('components has all five fields', () => {
    const r = investmentScoreFromScores({
      moatScore:              70,
      capitalAllocationScore: 65,
      earningsQualityScore:   68,
      managementScore:        72,
      valuationScore:         60,
    })
    const c = r.components
    expect(typeof c.moat).toBe('number')
    expect(typeof c.capitalAllocation).toBe('number')
    expect(typeof c.earningsQuality).toBe('number')
    expect(typeof c.management).toBe('number')
    expect(typeof c.valuation).toBe('number')
  })

  it('evidence array is non-empty', () => {
    const r = investmentScoreFromScores({
      moatScore:              70,
      capitalAllocationScore: 65,
      earningsQualityScore:   68,
      managementScore:        72,
      valuationScore:         60,
    })
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('grade A+ for score ≥ 90', () => {
    const r = investmentScoreFromScores({
      moatScore:              95,
      capitalAllocationScore: 95,
      earningsQualityScore:   95,
      managementScore:        95,
      valuationScore:         95,
    })
    expect(r.grade).toBe('A+')
  })

  it('grade F for score < 25', () => {
    const r = investmentScoreFromScores({
      moatScore:              10,
      capitalAllocationScore: 10,
      earningsQualityScore:   10,
      managementScore:        10,
      valuationScore:         10,
    })
    expect(r.grade).toBe('F')
  })

  it('grade mapping covers all valid grades', () => {
    const validGrades = ['A+', 'A', 'B+', 'B', 'C', 'D', 'F']
    const r = investmentScoreFromScores({
      moatScore:              65,
      capitalAllocationScore: 65,
      earningsQualityScore:   65,
      managementScore:        65,
      valuationScore:         65,
    })
    expect(validGrades).toContain(r.grade)
  })

  it('score is in [0, 100]', () => {
    const r = investmentScoreFromScores({
      moatScore:              50,
      capitalAllocationScore: 50,
      earningsQualityScore:   50,
      managementScore:        50,
      valuationScore:         50,
    })
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('interpretation includes grade and score', () => {
    const r = investmentScoreFromScores({
      moatScore:              70,
      capitalAllocationScore: 65,
      earningsQualityScore:   68,
      managementScore:        72,
      valuationScore:         60,
    })
    expect(r.interpretation).toContain(r.grade)
    expect(r.interpretation).toContain(`${r.score}`)
  })

  it('valuation weight redistribution: omitting valuationScore gives higher weight to other factors', () => {
    // Without valuation, moat gets 31.25% vs 25% → higher-moat score should pull total up more
    const withVal    = investmentScoreFromScores({ moatScore: 90, capitalAllocationScore: 50, earningsQualityScore: 50, managementScore: 50, valuationScore: 50 })
    const withoutVal = investmentScoreFromScores({ moatScore: 90, capitalAllocationScore: 50, earningsQualityScore: 50, managementScore: 50 })
    // Without valuation, moat contributes 31.25% vs 25%, so score should be higher
    expect(withoutVal.score).toBeGreaterThanOrEqual(withVal.score)
  })
})

// ── investmentScoreFromSeries ─────────────────────────────────────────────────

describe('investmentScoreFromSeries', () => {
  it('4-year high-quality data → returns valid InvestmentScore', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    expect(typeof r.score).toBe('number')
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('with valuationParams → valuation component is not null', () => {
    const r = investmentScoreFromSeries(
      highQualitySeries(),
      { peRatio: 18, evEbitda: 11, pbRatio: 3.1, dcfUpsidePct: 22 },
    )
    expect(r.components.valuation).not.toBeNull()
    expect(typeof r.components.valuation).toBe('number')
  })

  it('without valuationParams → valuation component is null', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    expect(r.components.valuation).toBeNull()
  })

  it('throws when fewer than 3 years provided', () => {
    const twoYears = highQualitySeries().slice(0, 2)
    expect(() => investmentScoreFromSeries(twoYears)).toThrow()
  })

  it('all components present and non-null (except valuation when not given)', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    const c = r.components
    expect(c.moat).not.toBeNull()
    expect(c.capitalAllocation).not.toBeNull()
    expect(c.earningsQuality).not.toBeNull()
    expect(c.management).not.toBeNull()
  })

  it('evidence is non-empty', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('grade is one of the valid grades', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    expect(['A+', 'A', 'B+', 'B', 'C', 'D', 'F']).toContain(r.grade)
  })

  it('conviction is one of the valid values', () => {
    const r = investmentScoreFromSeries(highQualitySeries())
    expect(['strongBuy', 'buy', 'hold', 'sell', 'strongSell']).toContain(r.conviction)
  })
})
