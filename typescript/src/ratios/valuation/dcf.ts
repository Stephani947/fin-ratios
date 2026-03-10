import { safeDivide } from '../../utils/safe-divide.js'

/**
 * 2-stage DCF model.
 * Stage 1: explicit FCF projections (or constant growth from base FCF).
 * Stage 2: terminal value via Gordon Growth Model.
 */
export function dcf2Stage(input: {
  /** Base free cash flow (TTM) */
  baseFcf: number
  /** Stage 1 annual growth rate (decimal, e.g. 0.15 for 15%) */
  growthRate: number
  /** Number of years in high-growth stage */
  years: number
  /** Terminal growth rate (decimal, e.g. 0.03 for 3%) */
  terminalGrowthRate: number
  /** Weighted average cost of capital (decimal) */
  wacc: number
  /** Net debt to subtract from enterprise value */
  netDebt?: number
  /** Shares outstanding to get per-share value */
  sharesOutstanding?: number
}): {
  intrinsicValue: number
  intrinsicValuePerShare: number | null
  pvStage1: number
  pvTerminalValue: number
  terminalValue: number
} | null {
  if (input.wacc <= input.terminalGrowthRate) return null
  if (input.wacc <= 0) return null

  let pvStage1 = 0
  let fcf = input.baseFcf
  for (let t = 1; t <= input.years; t++) {
    fcf = fcf * (1 + input.growthRate)
    pvStage1 += fcf / Math.pow(1 + input.wacc, t)
  }

  const terminalFcf = fcf * (1 + input.terminalGrowthRate)
  const terminalValue = terminalFcf / (input.wacc - input.terminalGrowthRate)
  const pvTerminalValue = terminalValue / Math.pow(1 + input.wacc, input.years)

  const enterpriseValue = pvStage1 + pvTerminalValue
  const intrinsicValue = enterpriseValue - (input.netDebt ?? 0)
  const intrinsicValuePerShare = input.sharesOutstanding
    ? safeDivide(intrinsicValue, input.sharesOutstanding)
    : null

  return { intrinsicValue, intrinsicValuePerShare, pvStage1, pvTerminalValue, terminalValue }
}
dcf2Stage.formula = 'Sum(FCF_t / (1+WACC)^t) + [FCF_n*(1+g) / (WACC-g)] / (1+WACC)^n'
dcf2Stage.description = '2-stage DCF. Stage 1 explicit growth, Stage 2 terminal value via Gordon Growth Model.'

/**
 * Gordon Growth (Dividend Discount) Model for dividend-paying stocks.
 */
export function gordonGrowthModel(input: {
  nextDividend: number
  requiredReturn: number
  dividendGrowthRate: number
}): number | null {
  if (input.requiredReturn <= input.dividendGrowthRate) return null
  return safeDivide(input.nextDividend, input.requiredReturn - input.dividendGrowthRate)
}
gordonGrowthModel.formula = 'D1 / (r - g)'
gordonGrowthModel.description = 'DDM for stable dividend-paying stocks. Only valid when r > g.'

/**
 * Reverse DCF — solves for the implied FCF growth rate baked into the current market price.
 * Uses bisection method over 20 iterations.
 */
export function reverseDcf(input: {
  marketCap: number
  baseFcf: number
  years: number
  terminalGrowthRate: number
  wacc: number
  netDebt?: number
}): { impliedGrowthRate: number; interpretation: string } | null {
  const target = input.marketCap + (input.netDebt ?? 0)

  const computeEV = (g: number): number | null => {
    const result = dcf2Stage({
      baseFcf: input.baseFcf,
      growthRate: g,
      years: input.years,
      terminalGrowthRate: input.terminalGrowthRate,
      wacc: input.wacc,
    })
    return result?.intrinsicValue ?? null
  }

  let low = -0.5
  let high = 5.0

  for (let i = 0; i < 50; i++) {
    const mid = (low + high) / 2
    const ev = computeEV(mid)
    if (ev == null) return null
    if (Math.abs(ev - target) < 1) break
    if (ev < target) low = mid
    else high = mid
  }

  const impliedGrowthRate = (low + high) / 2

  return {
    impliedGrowthRate,
    interpretation: `Market implies ${(impliedGrowthRate * 100).toFixed(1)}% annual FCF growth over ${input.years} years`,
  }
}
reverseDcf.formula = 'Solve g such that DCF(g) = Market Cap'
reverseDcf.description = 'Reverse-engineers the FCF growth rate implied by the current stock price.'
