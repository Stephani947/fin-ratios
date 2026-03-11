/**
 * Fair Value Range.
 *
 * Synthesises multiple valuation methods into a bull/base/bear fair value
 * estimate. No single method is reliable in isolation — the composite range
 * reflects where multiple frameworks converge.
 *
 * Methods
 * -------
 * 1. DCF (2-stage)         — discounted cash flow with explicit + terminal stage
 * 2. Graham Number         — Benjamin Graham's geometric mean intrinsic value
 * 3. FCF Yield             — normalise FCF at a target yield
 * 4. EV/EBITDA Multiple    — EBITDA × target multiple, bridge to equity
 * 5. Earnings Power Value  — no-growth: NOPAT / WACC
 *
 * References
 * ----------
 * Graham & Dodd (1934)    — Security Analysis
 * Koller et al. (2020)    — Valuation (7th ed.), McKinsey & Company
 * Greenwald et al. (2001) — Value Investing: From Graham to Buffett
 */

// ── Types ──────────────────────────────────────────────────────────────────────

export interface FairValueOptions {
  // DCF
  fcf?: number
  shares?: number
  growthRate?: number        // default 0.08
  terminalGrowth?: number   // default 0.03
  wacc?: number             // default 0.09
  dcfYears?: number         // default 10
  // Graham Number
  eps?: number
  bvps?: number
  // FCF Yield
  targetYield?: number      // default 0.04
  // EV/EBITDA
  ebitda?: number
  totalDebt?: number
  cash?: number
  evEbitdaMultiple?: number // default 12
  // EPV
  ebit?: number
  taxRate?: number          // default 0.21
  // Market context
  currentPrice?: number
}

export interface FairValueRange {
  estimates: Record<string, number>   // per-method fair value per share
  baseValue: number                   // trimmed median
  bullValue: number                   // 75th percentile
  bearValue: number                   // 25th percentile
  methodsUsed: number
  currentPrice?: number
  upsidePct?: number
  marginOfSafety?: number
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function percentile(xs: number[], p: number): number {
  if (!xs.length) return 0
  const sorted = [...xs].sort((a, b) => a - b)
  const idx = (p / 100) * (sorted.length - 1)
  const lo = Math.floor(idx)
  const hi = Math.min(lo + 1, sorted.length - 1)
  return (sorted[lo] ?? 0) + ((sorted[hi] ?? 0) - (sorted[lo] ?? 0)) * (idx - lo)
}

function trimmedMean(xs: number[]): number {
  if (xs.length <= 3) return xs.reduce((a, b) => a + b, 0) / xs.length
  const sorted = [...xs].sort((a, b) => a - b).slice(1, -1)
  return sorted.reduce((a, b) => a + b, 0) / sorted.length
}

function round2(x: number): number {
  return Math.round(x * 100) / 100
}

// ── Per-method calculators ─────────────────────────────────────────────────────

function dcfValue(
  fcf: number, growthRate: number, terminalGrowth: number,
  wacc: number, shares: number, years: number,
): number | null {
  if (wacc <= terminalGrowth || fcf <= 0 || shares <= 0) return null
  let pv = 0
  let cf = fcf
  for (let i = 1; i <= years; i++) {
    cf *= (1 + growthRate)
    pv += cf / (1 + wacc) ** i
  }
  const terminal = cf * (1 + terminalGrowth) / (wacc - terminalGrowth)
  pv += terminal / (1 + wacc) ** years
  return pv / shares
}

function grahamValue(eps: number, bvps: number): number | null {
  return eps > 0 && bvps > 0 ? Math.sqrt(22.5 * eps * bvps) : null
}

function fcfYieldValue(fcf: number, shares: number, targetYield: number): number | null {
  return fcf > 0 && shares > 0 && targetYield > 0 ? (fcf / targetYield) / shares : null
}

function evEbitdaValue(
  ebitda: number, totalDebt: number, cash: number, shares: number, multiple: number,
): number | null {
  if (ebitda <= 0 || shares <= 0) return null
  const equityValue = ebitda * multiple - totalDebt + cash
  return equityValue > 0 ? equityValue / shares : null
}

function epvValue(
  ebit: number, taxRate: number, wacc: number,
  shares: number, cash: number, totalDebt: number,
): number | null {
  if (ebit <= 0 || wacc <= 0 || shares <= 0) return null
  const equityValue = ebit * (1 - taxRate) / wacc + cash - totalDebt
  return equityValue > 0 ? equityValue / shares : null
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute a composite fair value range from multiple valuation methods.
 *
 * All monetary inputs must be in the same unit (e.g. total dollars or millions).
 * `fcf`, `ebitda`, and `ebit` are total company values; `shares` converts to per-share.
 *
 * @throws Error if no method can be computed from the provided inputs.
 */
export function fairValueRange(options: FairValueOptions): FairValueRange {
  const {
    fcf, shares,
    growthRate = 0.08, terminalGrowth = 0.03, wacc = 0.09, dcfYears = 10,
    eps, bvps,
    targetYield = 0.04,
    ebitda, totalDebt = 0, cash = 0, evEbitdaMultiple = 12,
    ebit, taxRate = 0.21,
    currentPrice,
  } = options

  const estimates: Record<string, number> = {}

  if (fcf && fcf > 0 && shares && shares > 0) {
    const v = dcfValue(fcf, growthRate, terminalGrowth, wacc, shares, dcfYears)
    if (v && v > 0) estimates['DCF (2-stage)'] = v

    const fy = fcfYieldValue(fcf, shares, targetYield)
    if (fy && fy > 0) estimates[`FCF Yield (${(targetYield * 100).toFixed(0)}%)`] = fy
  }

  if (eps && bvps) {
    const g = grahamValue(eps, bvps)
    if (g && g > 0) estimates['Graham Number'] = g
  }

  if (ebitda && ebitda > 0 && shares && shares > 0) {
    const v = evEbitdaValue(ebitda, totalDebt, cash, shares, evEbitdaMultiple)
    if (v && v > 0) estimates[`EV/EBITDA (${evEbitdaMultiple.toFixed(0)}×)`] = v
  }

  if (ebit && ebit > 0 && shares && shares > 0) {
    const v = epvValue(ebit, taxRate, wacc, shares, cash, totalDebt)
    if (v && v > 0) estimates['Earnings Power Value'] = v
  }

  if (!Object.keys(estimates).length) {
    throw new Error(
      'No valuation methods could be computed. ' +
      'Provide at least one of: (fcf + shares), (eps + bvps), (ebitda + shares), (ebit + shares).'
    )
  }

  const vals = Object.values(estimates)
  const baseValue = round2(trimmedMean(vals))
  const bearValue = round2(percentile(vals, 25))
  const bullValue = round2(percentile(vals, 75))

  const result: FairValueRange = {
    estimates: Object.fromEntries(Object.entries(estimates).map(([k, v]) => [k, round2(v)])),
    baseValue,
    bearValue,
    bullValue,
    methodsUsed: vals.length,
  }

  if (currentPrice !== undefined && currentPrice > 0) {
    result.currentPrice = currentPrice
    result.upsidePct    = Math.round((baseValue / currentPrice - 1) * 1000) / 10
    result.marginOfSafety = Math.round((bearValue / currentPrice - 1) * 1000) / 10
  }

  return result
}
