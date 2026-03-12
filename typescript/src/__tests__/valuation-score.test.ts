import { describe, it, expect } from 'vitest'
import { valuationAttractivenessScore } from '../utils/valuation-score.js'

describe('valuationAttractivenessScore', () => {
  it('attractive case: low multiples → score ≥ 70 and rating attractive', () => {
    const r = valuationAttractivenessScore({
      peRatio: 12,
      evEbitda: 7,
      pFcf: 11,
      pbRatio: 1.2,
    })
    expect(r.score).toBeGreaterThanOrEqual(70)
    expect(r.rating).toBe('attractive')
  })

  it('expensive case: high multiples → score ≤ 30 and rating expensive or overvalued', () => {
    const r = valuationAttractivenessScore({
      peRatio: 45,
      evEbitda: 28,
      pFcf: 40,
      pbRatio: 8,
    })
    expect(r.score).toBeLessThanOrEqual(30)
    expect(['expensive', 'overvalued']).toContain(r.rating)
  })

  it('neutral (no params): score near 50', () => {
    const r = valuationAttractivenessScore({})
    // All signals default to 0.5, so score should be 50
    expect(r.score).toBe(50)
  })

  it('earningsYieldPct overrides peRatio', () => {
    // earningsYieldPct=10 → ey=0.10, much higher than pe=100 → ey=0.01
    const withPe    = valuationAttractivenessScore({ peRatio: 100 })
    const withEyPct = valuationAttractivenessScore({ earningsYieldPct: 10 })
    expect(withEyPct.score).toBeGreaterThan(withPe.score)
  })

  it('fcfYieldPct overrides pFcf', () => {
    // fcfYieldPct=8 → fy=0.08, much better than pFcf=100 → fy=0.01
    const withPFcf    = valuationAttractivenessScore({ pFcf: 100 })
    const withFcfPct  = valuationAttractivenessScore({ fcfYieldPct: 8 })
    expect(withFcfPct.score).toBeGreaterThan(withPFcf.score)
  })

  it('positive dcfUpsidePct increases score vs absent', () => {
    const without = valuationAttractivenessScore({ peRatio: 18 })
    const with_   = valuationAttractivenessScore({ peRatio: 18, dcfUpsidePct: 40 })
    expect(with_.score).toBeGreaterThan(without.score)
  })

  it('higher riskFreeRate reduces earnings yield spread score', () => {
    const lowRf  = valuationAttractivenessScore({ peRatio: 20, riskFreeRate: 0.02 })
    const highRf = valuationAttractivenessScore({ peRatio: 20, riskFreeRate: 0.08 })
    // At pe=20, ey=5%; with rf=2% spread is +3%, with rf=8% spread is -3%
    expect(lowRf.score).toBeGreaterThan(highRf.score)
  })

  it('result has all required fields', () => {
    const r = valuationAttractivenessScore({ peRatio: 18, evEbitda: 11, pbRatio: 3 })
    expect(typeof r.score).toBe('number')
    expect(['attractive', 'fair', 'expensive', 'overvalued']).toContain(r.rating)
    expect(r.components).toBeDefined()
    expect(Array.isArray(r.evidence)).toBe(true)
    expect(typeof r.interpretation).toBe('string')
  })

  it('components has all five keys', () => {
    const r = valuationAttractivenessScore({ peRatio: 15, evEbitda: 9, pFcf: 14, pbRatio: 2, dcfUpsidePct: 20 })
    const c = r.components
    expect(typeof c.earningsYield).toBe('number')
    expect(typeof c.fcfYield).toBe('number')
    expect(typeof c.evEbitda).toBe('number')
    expect(typeof c.pbRatio).toBe('number')
    expect(typeof c.dcfUpside).toBe('number')
  })

  it('component values are in [0, 1]', () => {
    const r = valuationAttractivenessScore({ peRatio: 15, evEbitda: 9, pFcf: 14, pbRatio: 2, dcfUpsidePct: 20 })
    const c = r.components
    for (const val of [c.earningsYield, c.fcfYield, c.evEbitda, c.pbRatio, c.dcfUpside]) {
      expect(val).toBeGreaterThanOrEqual(0)
      expect(val).toBeLessThanOrEqual(1)
    }
  })

  it('score is in [0, 100]', () => {
    const r = valuationAttractivenessScore({ peRatio: 8, evEbitda: 4, pFcf: 8, pbRatio: 0.8, dcfUpsidePct: 60 })
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(100)
  })

  it('evidence array is non-empty with inputs provided', () => {
    const r = valuationAttractivenessScore({ peRatio: 18, evEbitda: 12 })
    expect(r.evidence.length).toBeGreaterThan(0)
  })

  it('riskFreeRate is reflected in result', () => {
    const r = valuationAttractivenessScore({ peRatio: 20, riskFreeRate: 0.05 })
    expect(r.riskFreeRate).toBe(0.05)
  })

  it('default riskFreeRate is 0.045 when not provided', () => {
    const r = valuationAttractivenessScore({ peRatio: 20 })
    expect(r.riskFreeRate).toBe(0.045)
  })

  it('interpretation includes the score', () => {
    const r = valuationAttractivenessScore({ peRatio: 18 })
    expect(r.interpretation).toContain(`${r.score}`)
  })
})
