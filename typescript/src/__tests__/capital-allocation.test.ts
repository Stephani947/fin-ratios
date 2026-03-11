import { describe, it, expect } from 'vitest'
import { capitalAllocationScore } from '../utils/capital-allocation.js'

function excellentAllocator() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:          (100 + y * 15) * 1e9,
    ebit:             (30  + y * 5)  * 1e9,
    totalEquity:      40e9,
    totalDebt:        5e9,
    totalAssets:      (70  + y * 8)  * 1e9,
    cash:             20e9,
    capex:            2e9,
    depreciation:     3e9,
    interestExpense:  0.2e9,
    incomeTaxExpense: (7 + y * 1.2) * 1e9,
    dividendsPaid:    2e9,
  }))
}

function poorAllocator() {
  return Array.from({ length: 8 }, (_, y) => ({
    year: 2016 + y,
    revenue:          (80  + y * 2)   * 1e9,
    ebit:             (4   + y * 0.2) * 1e9,
    totalEquity:      30e9,
    totalDebt:        50e9,
    totalAssets:      (100 + y * 12)  * 1e9,
    cash:             3e9,
    capex:            15e9,
    depreciation:     8e9,
    interestExpense:  3.5e9,
    incomeTaxExpense: 0.5e9,
  }))
}

describe('capitalAllocationScore', () => {
  it('returns score in 0–100 range', () => {
    const r = capitalAllocationScore(excellentAllocator())
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('returns valid rating', () => {
    const r = capitalAllocationScore(excellentAllocator())
    expect(['excellent', 'good', 'fair', 'poor']).toContain(r.rating)
  })

  it('components are in 0–1 range', () => {
    const r = capitalAllocationScore(excellentAllocator())
    const c = r.components
    for (const val of [c.valueCreation, c.fcfQuality, c.reinvestmentYield, c.payoutDiscipline]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('throws on fewer than 2 years', () => {
    expect(() => capitalAllocationScore([excellentAllocator()[0]!])).toThrow('at least 2 years')
  })

  it('excellent allocator beats poor allocator', () => {
    const exc = capitalAllocationScore(excellentAllocator())
    const poor = capitalAllocationScore(poorAllocator())
    expect(exc.score).toBeGreaterThan(poor.score)
  })

  it('WACC override is respected', () => {
    const r = capitalAllocationScore(excellentAllocator(), { wacc: 0.12 })
    expect(r.waccUsed).toBe(0.12)
  })

  it('WACC is within [6%, 20%] bounds when auto-estimated', () => {
    const r = capitalAllocationScore(excellentAllocator())
    expect(r.waccUsed).toBeGreaterThanOrEqual(0.06)
    expect(r.waccUsed).toBeLessThanOrEqual(0.20)
  })

  it('years analyzed matches input', () => {
    const data = excellentAllocator()
    expect(capitalAllocationScore(data).yearsAnalyzed).toBe(data.length)
  })

  it('evidence is non-empty', () => {
    expect(capitalAllocationScore(excellentAllocator()).evidence.length).toBeGreaterThan(0)
  })
})
