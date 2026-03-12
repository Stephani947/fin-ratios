import { describe, it, expect } from 'vitest'
import { dividendSafetyScoreFromSeries } from '../utils/dividend-score.js'
import type { AnnualDividendData } from '../utils/dividend-score.js'

/** Safe dividend: low FCF payout (<40%), low debt, 5+ consecutive growing dividends */
function safeDividendData(): AnnualDividendData[] {
  return [
    {
      year: 2018,
      dividendsPaid:      1.0e9,
      operatingCashFlow: 10e9,
      capex:              1.5e9,
      netIncome:          6e9,
      totalDebt:          4e9,
      cash:               3e9,
      ebit:               8e9,
      depreciation:       1e9,
    },
    {
      year: 2019,
      dividendsPaid:      1.1e9,
      operatingCashFlow: 11e9,
      capex:              1.5e9,
      netIncome:          6.5e9,
      totalDebt:          4e9,
      cash:               3.5e9,
      ebit:               8.8e9,
      depreciation:       1.1e9,
    },
    {
      year: 2020,
      dividendsPaid:      1.2e9,
      operatingCashFlow: 11.5e9,
      capex:              1.6e9,
      netIncome:          7e9,
      totalDebt:          3.5e9,
      cash:               4e9,
      ebit:               9.3e9,
      depreciation:       1.1e9,
    },
    {
      year: 2021,
      dividendsPaid:      1.3e9,
      operatingCashFlow: 12e9,
      capex:              1.7e9,
      netIncome:          7.5e9,
      totalDebt:          3e9,
      cash:               4.5e9,
      ebit:               9.8e9,
      depreciation:       1.2e9,
    },
    {
      year: 2022,
      dividendsPaid:      1.4e9,
      operatingCashFlow: 13e9,
      capex:              1.8e9,
      netIncome:          8e9,
      totalDebt:          2.5e9,
      cash:               5e9,
      ebit:               10.5e9,
      depreciation:       1.2e9,
    },
    {
      year: 2023,
      dividendsPaid:      1.5e9,
      operatingCashFlow: 14e9,
      capex:              1.9e9,
      netIncome:          8.5e9,
      totalDebt:          2e9,
      cash:               5.5e9,
      ebit:               11e9,
      depreciation:       1.3e9,
    },
  ]
}

/** Risky dividend: payout > 90% FCF, high debt ~4× EBITDA, one cut in history */
function riskyDividendData(): AnnualDividendData[] {
  return [
    {
      year: 2020,
      dividendsPaid:      3.5e9,
      operatingCashFlow:  5e9,
      capex:              1e9,
      netIncome:          3e9,
      totalDebt:          40e9,
      cash:               2e9,
      ebit:               8e9,
      depreciation:       2e9,
    },
    {
      year: 2021,
      // dividend cut
      dividendsPaid:      3.0e9,
      operatingCashFlow:  4.5e9,
      capex:              1.2e9,
      netIncome:          2.5e9,
      totalDebt:          42e9,
      cash:               1.5e9,
      ebit:               7.5e9,
      depreciation:       2e9,
    },
    {
      year: 2022,
      dividendsPaid:      3.2e9,
      operatingCashFlow:  4.8e9,
      capex:              1.3e9,
      netIncome:          2.8e9,
      totalDebt:          44e9,
      cash:               1.5e9,
      ebit:               7.8e9,
      depreciation:       2.1e9,
    },
    {
      year: 2023,
      dividendsPaid:      3.4e9,
      operatingCashFlow:  5.2e9,
      capex:              1.5e9,
      netIncome:          3.0e9,
      totalDebt:          46e9,
      cash:               1.5e9,
      ebit:               8e9,
      depreciation:       2.2e9,
    },
  ]
}

/** Non-payer: all dividendsPaid are 0 or undefined */
function nonPayerData(): AnnualDividendData[] {
  return [
    { year: 2021, dividendsPaid: 0, operatingCashFlow: 10e9, capex: 2e9, netIncome: 6e9 },
    { year: 2022, dividendsPaid: 0, operatingCashFlow: 11e9, capex: 2.2e9, netIncome: 6.5e9 },
    { year: 2023, operatingCashFlow: 12e9, capex: 2.5e9, netIncome: 7e9 },
  ]
}

describe('dividendSafetyScoreFromSeries', () => {
  it('safe dividend: score ≥ 70 and rating safe', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(r.score).toBeGreaterThanOrEqual(70)
    expect(r.rating).toBe('safe')
  })

  it('risky dividend: score ≤ 35', () => {
    const r = dividendSafetyScoreFromSeries(riskyDividendData())
    expect(r.score).toBeLessThanOrEqual(35)
  })

  it('non-payer: rating is non-payer and isDividendPayer is false', () => {
    const r = dividendSafetyScoreFromSeries(nonPayerData())
    expect(r.rating).toBe('non-payer')
    expect(r.isDividendPayer).toBe(false)
  })

  it('isDividendPayer is true when dividends are present', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(r.isDividendPayer).toBe(true)
  })

  it('score is in [0, 100] for dividend payer', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('score is in [0, 100] for risky payer', () => {
    const r = dividendSafetyScoreFromSeries(riskyDividendData())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('components has all four keys', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    const c = r.components
    expect(typeof c.fcfPayoutRatio).toBe('number')
    expect(typeof c.earningsPayoutRatio).toBe('number')
    expect(typeof c.balanceSheetStrength).toBe('number')
    expect(typeof c.dividendGrowthTrack).toBe('number')
  })

  it('component values are in [0, 1]', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    const c = r.components
    for (const val of [c.fcfPayoutRatio, c.earningsPayoutRatio, c.balanceSheetStrength, c.dividendGrowthTrack]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('evidence array is non-empty for dividend payer', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('evidence array is non-empty for non-payer', () => {
    const r = dividendSafetyScoreFromSeries(nonPayerData())
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('yearsAnalyzed matches input length', () => {
    const data = safeDividendData()
    const r = dividendSafetyScoreFromSeries(data)
    expect(r.yearsAnalyzed).toBe(data.length)
  })

  it('safe dividend scores higher than risky dividend', () => {
    const safe  = dividendSafetyScoreFromSeries(safeDividendData())
    const risky = dividendSafetyScoreFromSeries(riskyDividendData())
    expect(safe.score).toBeGreaterThan(risky.score)
  })

  it('interpretation contains the score', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(r.interpretation).toContain(`${r.score}`)
  })

  it('valid rating for dividend payer', () => {
    const r = dividendSafetyScoreFromSeries(safeDividendData())
    expect(['safe', 'adequate', 'risky', 'danger']).toContain(r.rating)
  })
})
