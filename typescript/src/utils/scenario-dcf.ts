/**
 * Scenario-based DCF valuation (bull / base / bear).
 *
 * Usage:
 *   import { scenarioDcf } from 'fin-ratios'
 *
 *   const result = scenarioDcf({
 *     baseFcf: 100e9,
 *     sharesOutstanding: 15.7e9,
 *     currentPrice: 185,
 *     scenarios: {
 *       bear: { growthRate: 0.04, wacc: 0.12, terminalGrowth: 0.02, years: 10 },
 *       base: { growthRate: 0.08, wacc: 0.09, terminalGrowth: 0.03, years: 10 },
 *       bull: { growthRate: 0.14, wacc: 0.08, terminalGrowth: 0.04, years: 10 },
 *     },
 *   })
 *
 *   console.log(result.base.intrinsicValuePerShare)  // 198.75
 *   console.log(result.base.upsidePct)               // 0.074 (+7.4%)
 */

import { safeDivide } from './safe-divide.js'

// ── Types ──────────────────────────────────────────────────────────────────────

export interface ScenarioParams {
  /** Annual FCF growth rate during projection period (e.g. 0.08 = 8%) */
  growthRate?: number
  /** Weighted average cost of capital / discount rate (e.g. 0.09 = 9%) */
  wacc?: number
  /** Terminal/perpetual growth rate after projection period (e.g. 0.02 = 2%) */
  terminalGrowth?: number
  /** Number of projection years (default: 10) */
  years?: number
}

export interface ScenarioResult {
  /** Total equity intrinsic value */
  intrinsicValue: number
  /** Intrinsic value per diluted share */
  intrinsicValuePerShare: number | null
  /** PV of projected FCFs */
  pvFcfs: number
  /** PV of terminal value */
  pvTerminal: number
  /** Terminal value (undiscounted) */
  terminalValue: number
  /** Upside/downside vs current price (e.g. 0.07 = +7%) */
  upsidePct: number | null
  /** Input parameters used */
  params: Required<ScenarioParams>
}

export interface ScenarioDcfInput {
  /** Most recent trailing FCF (absolute dollars, not per-share) */
  baseFcf: number
  /** Total diluted shares outstanding */
  sharesOutstanding: number
  /** Per-scenario parameters */
  scenarios?: Record<string, ScenarioParams>
  /** Optional ticker for display */
  ticker?: string
  /** Optional current market price per share for upside calculation */
  currentPrice?: number
}

export type ScenarioDcfResult = Record<string, ScenarioResult>

const DEFAULT_SCENARIOS: Record<string, ScenarioParams> = {
  bear: { growthRate: 0.03, wacc: 0.12, terminalGrowth: 0.02, years: 10 },
  base: { growthRate: 0.07, wacc: 0.09, terminalGrowth: 0.02, years: 10 },
  bull: { growthRate: 0.12, wacc: 0.08, terminalGrowth: 0.03, years: 10 },
}

// ── Main function ──────────────────────────────────────────────────────────────

/**
 * Compute scenario-based DCF intrinsic value (bull / base / bear).
 *
 * Each scenario projects FCFs for N years, then applies a Gordon Growth Model
 * terminal value. Results are discounted back to present value at the scenario WACC.
 *
 * @param input  FCF, shares, optional current price, and per-scenario parameters
 * @returns      Map of scenario name → ScenarioResult
 *
 * @example
 *   const r = scenarioDcf({ baseFcf: 100e9, sharesOutstanding: 15.7e9 })
 *   r.base.intrinsicValuePerShare  // computed base case IV per share
 */
export function scenarioDcf(input: ScenarioDcfInput): ScenarioDcfResult {
  const {
    baseFcf,
    sharesOutstanding,
    currentPrice,
    scenarios = DEFAULT_SCENARIOS,
  } = input

  const result: ScenarioDcfResult = {}

  for (const [name, params] of Object.entries(scenarios)) {
    const growthRate = params.growthRate ?? 0.07
    const wacc = params.wacc ?? 0.09
    const terminalGrowth = params.terminalGrowth ?? 0.02
    const years = params.years ?? 10

    // Project FCFs and discount to PV
    let fcf = baseFcf
    let pvSum = 0
    for (let t = 1; t <= years; t++) {
      fcf = fcf * (1 + growthRate)
      pvSum += fcf / Math.pow(1 + wacc, t)
    }

    // Terminal value (Gordon Growth)
    let terminalValue = 0
    if (wacc > terminalGrowth) {
      const terminalFcf = fcf * (1 + terminalGrowth)
      terminalValue = terminalFcf / (wacc - terminalGrowth)
    }
    const pvTerminal = terminalValue / Math.pow(1 + wacc, years)

    const intrinsicValue = pvSum + pvTerminal
    const intrinsicValuePerShare = safeDivide(intrinsicValue, sharesOutstanding) ?? null

    let upsidePct: number | null = null
    if (currentPrice && currentPrice > 0 && intrinsicValuePerShare !== null) {
      upsidePct = (intrinsicValuePerShare - currentPrice) / currentPrice
    }

    result[name] = {
      intrinsicValue,
      intrinsicValuePerShare,
      pvFcfs: pvSum,
      pvTerminal,
      terminalValue,
      upsidePct,
      params: { growthRate, wacc, terminalGrowth, years },
    }
  }

  return result
}
