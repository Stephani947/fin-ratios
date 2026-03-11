/**
 * Core ratio function tests — verifies the most commonly used calculations
 * produce correct values within expected tolerances.
 */
import { describe, it, expect } from 'vitest'
import {
  pe, peg, pb, ps, evEbitda, evEbit, grahamNumber,
  grossMargin, operatingMargin, netProfitMargin, roe, roa, roic, nopat,
  currentRatio, quickRatio, cashRatio, dso, dio, dpo, cashConversionCycle,
  debtToEquity, interestCoverageRatio, netDebtToEbitda,
  freeCashFlow, fcfMargin, fcfConversion, fcfYield,
  revenueGrowth, revenueCAGR,
  sharpeRatio, maximumDrawdown, historicalVaR,
  piotroskiFScore, altmanZScore,
} from '../index.js'

// ── Valuation ─────────────────────────────────────────────────────────────────

describe('valuation', () => {
  it('pe', () => expect(pe({ marketCap: 150, netIncome: 5 })).toBeCloseTo(30))
  it('pe zero netIncome', () => expect(pe({ marketCap: 150, netIncome: 0 })).toBeNull())

  it('peg', () => expect(peg({ peRatio: 20, epsGrowthRatePercent: 10 })).toBeCloseTo(2))

  it('pb', () => expect(pb({ marketCap: 100, totalEquity: 25 })).toBeCloseTo(4))

  it('ps', () => expect(ps({ marketCap: 500, revenue: 100 })).toBeCloseTo(5))

  it('evEbitda', () => expect(evEbitda({ enterpriseValue: 1200, ebitda: 100 })).toBeCloseTo(12))
  it('evEbitda zero', () => expect(evEbitda({ enterpriseValue: 1200, ebitda: 0 })).toBeNull())

  it('evEbit', () => expect(evEbit({ enterpriseValue: 1000, ebit: 80 })).toBeCloseTo(12.5))

  it('grahamNumber', () => {
    const g = grahamNumber({ eps: 5, bookValuePerShare: 20 })
    expect(g).toBeCloseTo(Math.sqrt(22.5 * 5 * 20), 2)
  })
  it('grahamNumber negative eps', () => expect(grahamNumber({ eps: -1, bookValuePerShare: 20 })).toBeNull())
})

// ── Profitability ─────────────────────────────────────────────────────────────

describe('profitability', () => {
  it('grossMargin', () => expect(grossMargin({ grossProfit: 60, revenue: 100 })).toBeCloseTo(0.6))
  it('operatingMargin', () => expect(operatingMargin({ ebit: 20, revenue: 100 })).toBeCloseTo(0.2))
  it('netProfitMargin', () => expect(netProfitMargin({ netIncome: 15, revenue: 100 })).toBeCloseTo(0.15))

  it('roe', () => expect(roe({ netIncome: 20, avgTotalEquity: 100 })).toBeCloseTo(0.2))
  it('roa', () => expect(roa({ netIncome: 10, avgTotalAssets: 200 })).toBeCloseTo(0.05))

  it('nopat', () => expect(nopat({ ebit: 50, taxRate: 0.2 })).toBeCloseTo(40))
  it('roic', () => expect(roic({ nopat: 30, investedCapital: 200 })).toBeCloseTo(0.15))
})

// ── Liquidity ─────────────────────────────────────────────────────────────────

describe('liquidity', () => {
  it('currentRatio', () => expect(currentRatio({ currentAssets: 200, currentLiabilities: 100 })).toBeCloseTo(2))
  it('quickRatio', () => expect(quickRatio({ cash: 70, shortTermInvestments: 30, accountsReceivable: 40, currentLiabilities: 100 })).toBeCloseTo(1.4))
  it('cashRatio', () => expect(cashRatio({ cash: 50, shortTermInvestments: 0, currentLiabilities: 100 })).toBeCloseTo(0.5))

  it('dso', () => expect(dso({ accountsReceivable: 100, revenue: 1200 })).toBeCloseTo(30.42, 0))
  it('dio', () => expect(dio({ inventory: 200, cogs: 1200 })).toBeCloseTo(60.83, 0))
  it('dpo', () => expect(dpo({ accountsPayable: 150, cogs: 1500 })).toBeCloseTo(36.5, 0))
  it('ccc', () => expect(cashConversionCycle({ dso: 30, dio: 60, dpo: 45 })).toBeCloseTo(45))
})

// ── Solvency ──────────────────────────────────────────────────────────────────

describe('solvency', () => {
  it('debtToEquity', () => expect(debtToEquity({ totalDebt: 500, totalEquity: 250 })).toBeCloseTo(2))
  it('interestCoverageRatio', () => expect(interestCoverageRatio({ ebit: 100, interestExpense: 20 })).toBeCloseTo(5))
  it('netDebtToEbitda', () => expect(netDebtToEbitda({ totalDebt: 300, cash: 100, ebitda: 100 })).toBeCloseTo(2))
})

// ── Cash Flow ─────────────────────────────────────────────────────────────────

describe('cashflow', () => {
  it('freeCashFlow', () => expect(freeCashFlow({ operatingCashFlow: 100, capex: 30 })).toBeCloseTo(70))
  it('fcfMargin', () => expect(fcfMargin({ freeCashFlow: 70, revenue: 500 })).toBeCloseTo(0.14))
  it('fcfConversion', () => expect(fcfConversion({ freeCashFlow: 80, netIncome: 100 })).toBeCloseTo(0.8))
  it('fcfYield', () => expect(fcfYield({ freeCashFlow: 50, marketCap: 1000 })).toBeCloseTo(0.05))
})

// ── Growth ────────────────────────────────────────────────────────────────────

describe('growth', () => {
  it('revenueGrowth', () => expect(revenueGrowth({ revenueCurrent: 110, revenuePrior: 100 })).toBeCloseTo(0.1))
  it('revenueCAGR', () => {
    const r = revenueCAGR({ revenueStart: 100, revenueEnd: 161.05, years: 5 })
    expect(r).toBeCloseTo(0.10, 2)
  })
})

// ── Risk ──────────────────────────────────────────────────────────────────────

describe('risk', () => {
  const returns = [0.05, -0.03, 0.08, -0.02, 0.06, 0.04, -0.01, 0.07]

  it('sharpeRatio result is finite', () => {
    const r = sharpeRatio({ returns, riskFreeRate: 0.02 })
    expect(isFinite(r ?? 0)).toBe(true)
  })

  it('maximumDrawdown is non-negative', () => {
    const prices = [100, 110, 90, 95, 85, 100]
    const r = maximumDrawdown({ prices })
    expect(r).toBeGreaterThanOrEqual(0)
  })

  it('historicalVaR is non-negative', () => {
    const r = historicalVaR({ returns, confidence: 0.95 })
    expect(r).toBeGreaterThanOrEqual(0)
  })
})

// ── Composite ─────────────────────────────────────────────────────────────────

describe('composite', () => {
  const piotroski_current = {
    netIncome: 500, totalAssets: 5000, operatingCashFlow: 600,
    longTermDebt: 1000, currentAssets: 800, currentLiabilities: 400,
    sharesOutstanding: 100, grossProfit: 1500, revenue: 4000,
  }
  const piotroski_prior = {
    netIncome: 400, totalAssets: 4800,
    longTermDebt: 1100, currentAssets: 750, currentLiabilities: 390,
    sharesOutstanding: 102, grossProfit: 1350, revenue: 3800,
  }

  it('piotroskiFScore returns 0–9', () => {
    const r = piotroskiFScore({ current: piotroski_current, prior: piotroski_prior })
    expect(r.score).toBeGreaterThanOrEqual(0)
    expect(r.score).toBeLessThanOrEqual(9)
  })

  it('altmanZScore returns valid z', () => {
    const r = altmanZScore({
      workingCapital: 400, totalAssets: 5000, retainedEarnings: 2000,
      ebit: 500, marketCap: 3000, totalLiabilities: 2000, revenue: 4000,
    })
    expect(typeof r!.z).toBe('number')
    expect(isFinite(r!.z)).toBe(true)
  })
})
