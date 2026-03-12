import { describe, it, expect } from 'vitest'
import { managementQualityScoreFromSeries } from '../utils/management-score.js'
import type { AnnualManagementData } from '../utils/management-score.js'

/** Strong management: high ROIC ~22%, expanding margins, declining share count */
function strongManagementData(): AnnualManagementData[] {
  return [
    {
      year: 2020,
      revenue: 100e9,
      ebit: 22e9,
      totalAssets: 80e9,
      totalEquity: 40e9,
      totalDebt: 8e9,
      cash: 5e9,
      sharesOutstanding: 5_000e6,
      incomeTaxExpense: 4.6e9,
      ebt: 21.5e9,
      interestExpense: 0.5e9,
    },
    {
      year: 2021,
      revenue: 118e9,
      ebit: 27e9,
      totalAssets: 90e9,
      totalEquity: 44e9,
      totalDebt: 7e9,
      cash: 7e9,
      sharesOutstanding: 4_900e6,
      incomeTaxExpense: 5.7e9,
      ebt: 26.4e9,
      interestExpense: 0.4e9,
    },
    {
      year: 2022,
      revenue: 138e9,
      ebit: 32e9,
      totalAssets: 100e9,
      totalEquity: 49e9,
      totalDebt: 6e9,
      cash: 9e9,
      sharesOutstanding: 4_780e6,
      incomeTaxExpense: 6.7e9,
      ebt: 31.5e9,
      interestExpense: 0.35e9,
    },
    {
      year: 2023,
      revenue: 160e9,
      ebit: 38e9,
      totalAssets: 112e9,
      totalEquity: 54e9,
      totalDebt: 5e9,
      cash: 11e9,
      sharesOutstanding: 4_640e6,
      incomeTaxExpense: 8e9,
      ebt: 37.6e9,
      interestExpense: 0.30e9,
    },
  ]
}

/** Weak management: low ROIC ~5%, contracting margins, increasing share count */
function weakManagementData(): AnnualManagementData[] {
  return [
    {
      year: 2020,
      revenue: 80e9,
      ebit: 4e9,
      totalAssets: 120e9,
      totalEquity: 30e9,
      totalDebt: 50e9,
      cash: 3e9,
      sharesOutstanding: 3_000e6,
      incomeTaxExpense: 0.5e9,
      ebt: 1.5e9,
      interestExpense: 2.5e9,
    },
    {
      year: 2021,
      revenue: 82e9,
      ebit: 3.5e9,
      totalAssets: 125e9,
      totalEquity: 29e9,
      totalDebt: 52e9,
      cash: 3e9,
      sharesOutstanding: 3_200e6,
      incomeTaxExpense: 0.4e9,
      ebt: 1.0e9,
      interestExpense: 2.6e9,
    },
    {
      year: 2022,
      revenue: 83e9,
      ebit: 3.0e9,
      totalAssets: 130e9,
      totalEquity: 28e9,
      totalDebt: 55e9,
      cash: 2.5e9,
      sharesOutstanding: 3_450e6,
      incomeTaxExpense: 0.3e9,
      ebt: 0.5e9,
      interestExpense: 2.8e9,
    },
    {
      year: 2023,
      revenue: 82e9,
      ebit: 2.5e9,
      totalAssets: 135e9,
      totalEquity: 27e9,
      totalDebt: 58e9,
      cash: 2e9,
      sharesOutstanding: 3_700e6,
      incomeTaxExpense: 0.2e9,
      ebt: 0.2e9,
      interestExpense: 2.9e9,
    },
  ]
}

describe('managementQualityScoreFromSeries', () => {
  it('strong management: score ≥ 65 and rating good or excellent', () => {
    const r = managementQualityScoreFromSeries(strongManagementData())
    expect(r.score).toBeGreaterThanOrEqual(65)
    expect(['good', 'excellent']).toContain(r.rating)
  })

  it('weak management: score ≤ 40 and rating fair or poor', () => {
    const r = managementQualityScoreFromSeries(weakManagementData())
    expect(r.score).toBeLessThanOrEqual(40)
    expect(['fair', 'poor']).toContain(r.rating)
  })

  it('throws Error if fewer than 3 years of data provided', () => {
    const twoYears = strongManagementData().slice(0, 2)
    expect(() => managementQualityScoreFromSeries(twoYears)).toThrow()
  })

  it('declining shares → higher shareholderOrientation than flat shares', () => {
    const base = strongManagementData()
    // Flat share count version
    const flat = base.map(d => ({ ...d, sharesOutstanding: 5_000e6 }))
    const rDeclining = managementQualityScoreFromSeries(base)
    const rFlat      = managementQualityScoreFromSeries(flat)
    expect(rDeclining.components.shareholderOrientation).toBeGreaterThan(
      rFlat.components.shareholderOrientation,
    )
  })

  it('evidence array is non-empty', () => {
    const r = managementQualityScoreFromSeries(strongManagementData())
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('score is in [0, 100]', () => {
    const r1 = managementQualityScoreFromSeries(strongManagementData())
    const r2 = managementQualityScoreFromSeries(weakManagementData())
    expect(r1.score).toBeGreaterThanOrEqual(0)
    expect(r1.score).toBeLessThanOrEqual(100)
    expect(r2.score).toBeGreaterThanOrEqual(0)
    expect(r2.score).toBeLessThanOrEqual(100)
  })

  it('components has all four keys', () => {
    const r = managementQualityScoreFromSeries(strongManagementData())
    const c = r.components
    expect(typeof c.roicExcellence).toBe('number')
    expect(typeof c.marginStability).toBe('number')
    expect(typeof c.shareholderOrientation).toBe('number')
    expect(typeof c.revenueExecution).toBe('number')
  })

  it('component values are in [0, 1]', () => {
    const r = managementQualityScoreFromSeries(strongManagementData())
    const c = r.components
    for (const val of [c.roicExcellence, c.marginStability, c.shareholderOrientation, c.revenueExecution]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('yearsAnalyzed matches input length', () => {
    const data = strongManagementData()
    const r = managementQualityScoreFromSeries(data)
    expect(r.yearsAnalyzed).toBe(data.length)
  })

  it('hurdleRate override is respected', () => {
    const r = managementQualityScoreFromSeries(strongManagementData(), 0.12)
    expect(r.hurdleRateUsed).toBe(0.12)
  })

  it('strong management scores higher than weak management', () => {
    const strong = managementQualityScoreFromSeries(strongManagementData())
    const weak   = managementQualityScoreFromSeries(weakManagementData())
    expect(strong.score).toBeGreaterThan(weak.score)
  })

  it('interpretation contains the score', () => {
    const r = managementQualityScoreFromSeries(strongManagementData())
    expect(r.interpretation).toContain(`${r.score}`)
  })
})
