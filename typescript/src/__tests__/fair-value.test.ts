import { describe, it, expect } from 'vitest'
import { fairValueRange } from '../utils/fair-value.js'

describe('fairValueRange', () => {
  it('returns result with all methods', () => {
    const r = fairValueRange({
      fcf: 90e9, shares: 15e9,
      eps: 6.0, bvps: 5.0,
      ebitda: 130e9, totalDebt: 100e9, cash: 60e9,
      ebit: 110e9, taxRate: 0.21,
      growthRate: 0.07, wacc: 0.09,
    })
    expect(r.methodsUsed).toBe(5)
    expect(Object.keys(r.estimates).length).toBe(5)
  })

  it('throws when no method can be computed', () => {
    expect(() => fairValueRange({})).toThrow('No valuation methods')
  })

  it('bear ≤ base ≤ bull', () => {
    const r = fairValueRange({ fcf: 80e9, shares: 10e9, eps: 5.0, bvps: 15.0 })
    expect(r.bearValue).toBeLessThanOrEqual(r.baseValue)
    expect(r.baseValue).toBeLessThanOrEqual(r.bullValue)
  })

  it('all values are positive', () => {
    const r = fairValueRange({ fcf: 50e9, shares: 5e9 })
    expect(r.baseValue).toBeGreaterThan(0)
    expect(r.bearValue).toBeGreaterThan(0)
    expect(r.bullValue).toBeGreaterThan(0)
  })

  it('upside computed when currentPrice provided', () => {
    const r = fairValueRange({ fcf: 100e9, shares: 10e9, currentPrice: 50 })
    expect(r.upsidePct).toBeDefined()
    expect(r.marginOfSafety).toBeDefined()
    expect(r.upsidePct).toBeCloseTo((r.baseValue / 50 - 1) * 100, 0)
  })

  it('no upside when no currentPrice', () => {
    const r = fairValueRange({ fcf: 50e9, shares: 5e9 })
    expect(r.upsidePct).toBeUndefined()
  })

  it('higher growth rate gives higher DCF value', () => {
    const r_low  = fairValueRange({ fcf: 50e9, shares: 5e9, growthRate: 0.03 })
    const r_high = fairValueRange({ fcf: 50e9, shares: 5e9, growthRate: 0.15 })
    expect(r_high.baseValue).toBeGreaterThan(r_low.baseValue)
  })

  it('graham number matches formula', () => {
    const r = fairValueRange({ eps: 5, bvps: 20 })
    const expected = Math.sqrt(22.5 * 5 * 20)
    expect(Math.abs(r.baseValue - expected)).toBeLessThan(0.01)
  })

  it('skips DCF when WACC <= terminal growth', () => {
    const r = fairValueRange({ fcf: 50e9, shares: 5e9, wacc: 0.02, terminalGrowth: 0.03, eps: 5, bvps: 10 })
    expect('DCF (2-stage)' in r.estimates).toBe(false)
  })

  it('methods_used equals number of estimate keys', () => {
    const r = fairValueRange({ fcf: 40e9, shares: 4e9, eps: 3, bvps: 8 })
    expect(r.methodsUsed).toBe(Object.keys(r.estimates).length)
  })
})
