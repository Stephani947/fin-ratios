/**
 * Capital Allocation Quality Score.
 *
 * Measures how effectively management deploys the capital entrusted to it.
 * A company that consistently earns above-WACC returns, converts NOPAT to FCF
 * efficiently, grows assets proportionally with revenue, and handles shareholder
 * distributions with discipline scores highest.
 *
 * Signals
 * -------
 * 1. Value Creation     (35%) — ROIC vs WACC spread level and trend
 * 2. FCF Quality        (25%) — NOPAT-to-FCF conversion rate and consistency
 * 3. Reinvestment Yield (25%) — incremental revenue per dollar of incremental assets
 * 4. Payout Discipline  (15%) — dividend FCF coverage; FCF retention vs ROIC logic
 *
 * Score: 0–100
 * Rating: 'excellent' (75–100), 'good' (50–74), 'fair' (25–49), 'poor' (0–24)
 */

import { safeDivide } from './safe-divide.js'

// ── Input / Output types ───────────────────────────────────────────────────────

/** One year of financial data for capital allocation analysis. */
export interface AnnualCapitalData {
  revenue?: number
  ebit?: number
  ebt?: number
  interestExpense?: number
  incomeTaxExpense?: number
  totalAssets?: number
  totalEquity?: number
  totalDebt?: number
  cash?: number
  capex?: number
  depreciation?: number
  dividendsPaid?: number
  year?: number | string
}

export interface CapitalAllocationComponents {
  valueCreation: number       // 0–1
  fcfQuality: number          // 0–1
  reinvestmentYield: number   // 0–1
  payoutDiscipline: number    // 0–1
}

export interface CapitalAllocationResult {
  score: number                                            // 0–100
  rating: 'excellent' | 'good' | 'fair' | 'poor'
  components: CapitalAllocationComponents
  waccUsed: number
  yearsAnalyzed: number
  evidence: string[]
}

export interface CapitalAllocationOptions {
  wacc?: number
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function mean(xs: number[]): number {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0
}

function std(xs: number[]): number {
  if (xs.length < 2) return 0
  const m = mean(xs)
  return Math.sqrt(xs.reduce((a, x) => a + (x - m) ** 2, 0) / (xs.length - 1))
}

function cv(xs: number[]): number {
  const m = mean(xs)
  return Math.abs(m) > 1e-9 ? std(xs) / Math.abs(m) : 1
}

function olsSlope(ys: number[]): number {
  const n = ys.length
  if (n < 2) return 0
  const xm = (n - 1) / 2
  const ym = mean(ys)
  const ssXX = Array.from({ length: n }, (_, i) => (i - xm) ** 2).reduce((a, b) => a + b, 0)
  const ssXY = Array.from({ length: n }, (_, i) => (i - xm) * ((ys[i] ?? 0) - ym)).reduce((a, b) => a + b, 0)
  return ssXX ? ssXY / ssXX : 0
}

function clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x))
}

function g(d: AnnualCapitalData, k: keyof AnnualCapitalData): number {
  const v = d[k]
  return typeof v === 'number' && isFinite(v) ? v : 0
}

// ── WACC estimation ────────────────────────────────────────────────────────────

function estimateWacc(series: AnnualCapitalData[], provided?: number): number {
  if (provided !== undefined) return provided
  const d = series[series.length - 1]!
  const equity = g(d, 'totalEquity')
  const debt = g(d, 'totalDebt')
  const cash = g(d, 'cash')
  const totalCap = equity + debt - cash
  if (totalCap <= 0) return 0.10
  const costEquity = 0.045 + 0.055
  const interest = g(d, 'interestExpense')
  let costDebt = 0.04
  if (debt > 0 && interest > 0) {
    const preTax = clamp(interest / debt, 0.02, 0.15)
    const ebt = g(d, 'ebt') || g(d, 'ebit') - interest
    const tax = g(d, 'incomeTaxExpense')
    const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.40) : 0.21
    costDebt = preTax * (1 - taxRate)
  }
  const wE = clamp(equity / totalCap, 0, 1)
  return clamp(wE * costEquity + (1 - wE) * costDebt, 0.06, 0.20)
}

// ── ROIC ──────────────────────────────────────────────────────────────────────

function yearRoic(d: AnnualCapitalData): number | null {
  const ebit = g(d, 'ebit')
  const ic = g(d, 'totalEquity') + g(d, 'totalDebt') - g(d, 'cash')
  if (ic <= 0) return null
  const ebt = g(d, 'ebt') || ebit - g(d, 'interestExpense')
  const tax = g(d, 'incomeTaxExpense')
  const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.50) : 0.21
  return (ebit * (1 - taxRate)) / ic
}

// ── Signal 1: Value Creation ──────────────────────────────────────────────────

function scoreValueCreation(series: AnnualCapitalData[], wacc: number): [number, string[]] {
  const roicVals = series.map(yearRoic).filter((r): r is number => r !== null)
  if (!roicVals.length) return [0.30, ['Value creation: insufficient ROIC data (neutral score)']]

  const spreads = roicVals.map(r => r - wacc)
  const ms = mean(spreads)
  const slope = olsSlope(spreads)
  const level = clamp((ms + 0.05) / 0.25, 0, 1)
  const trendAdj = slope > 0.01 ? 0.10 : slope < -0.01 ? -0.10 : 0
  const consistency = Math.max(0, 1 - cv(spreads) * 0.5)
  const score = clamp(0.60 * level + 0.40 * consistency + trendAdj, 0, 1)

  const pos = spreads.filter(s => s > 0).length
  const dir = slope > 0.01 ? 'improving' : slope < -0.01 ? 'declining' : 'stable'
  return [score, [
    `Value creation: mean ROIC-WACC spread ${(ms * 100).toFixed(1)}%  (${pos}/${spreads.length} years positive)`,
    `Spread trend: ${dir}  (OLS ${(slope * 100).toFixed(2)}%/yr)`,
  ]]
}

// ── Signal 2: FCF Quality ─────────────────────────────────────────────────────

function scoreFcfQuality(series: AnnualCapitalData[]): [number, string[]] {
  const conversions: number[] = []
  for (const d of series) {
    const ebit = g(d, 'ebit')
    if (ebit <= 0) continue
    const ebt = g(d, 'ebt') || ebit - g(d, 'interestExpense')
    const tax = g(d, 'incomeTaxExpense')
    const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.50) : 0.21
    const nopat = ebit * (1 - taxRate)
    if (nopat <= 0) continue
    const fcf = nopat + g(d, 'depreciation') - g(d, 'capex')
    conversions.push(fcf / nopat)
  }
  if (!conversions.length) return [0.40, ['FCF quality: insufficient data (neutral score)']]

  const mc = mean(conversions)
  const level = clamp(mc / 1.2, 0, 1)
  const stability = Math.max(0, 1 - cv(conversions) * 1.5)
  const score = clamp(0.65 * level + 0.35 * stability, 0, 1)
  const quality = mc >= 1.0 ? 'capital-light' : mc < 0.5 ? 'capital-heavy' : 'moderate'
  return [score, [`FCF quality: mean NOPAT-to-FCF conversion ${(mc * 100).toFixed(0)}%  (${quality})`]]
}

// ── Signal 3: Reinvestment Yield ──────────────────────────────────────────────

function scoreReinvestmentYield(series: AnnualCapitalData[]): [number, string[]] {
  const yields: number[] = []
  for (let i = 1; i < series.length; i++) {
    const prev = series[i - 1]!
    const curr = series[i]!
    const da = g(curr, 'totalAssets') - g(prev, 'totalAssets')
    const dr = g(curr, 'revenue') - g(prev, 'revenue')
    if (da > 1e6) yields.push(dr / da)
  }
  if (!yields.length) return [0.40, ['Reinvestment yield: insufficient data (neutral score)']]

  const my = mean(yields)
  const level = clamp((my + 0.2) / 1.7, 0, 1)
  const consistency = Math.max(0, 1 - cv(yields) * 0.5)
  const score = clamp(0.65 * level + 0.35 * consistency, 0, 1)
  const pos = yields.filter(y => y > 0).length
  return [score, [
    `Reinvestment yield: mean incremental revenue/asset ${my.toFixed(2)}x  (${pos}/${yields.length} periods productive)`,
  ]]
}

// ── Signal 4: Payout Discipline ───────────────────────────────────────────────

function scorePayoutDiscipline(series: AnnualCapitalData[], wacc: number): [number, string[]] {
  const coverages: number[] = []
  for (const d of series) {
    const ebit = g(d, 'ebit')
    if (ebit <= 0) continue
    const ebt = g(d, 'ebt') || ebit - g(d, 'interestExpense')
    const tax = g(d, 'incomeTaxExpense')
    const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.50) : 0.21
    const nopat = ebit * (1 - taxRate)
    const fcf = nopat + g(d, 'depreciation') - g(d, 'capex')
    const div = g(d, 'dividendsPaid')
    if (div > 0) coverages.push(fcf > 0 ? fcf / div : 0)
  }
  if (coverages.length) {
    const mc = mean(coverages)
    const score = clamp((mc - 0.5) / 2.0, 0, 1)
    const health = mc >= 2.0 ? 'healthy' : mc >= 1.0 ? 'tight' : 'stressed'
    return [score, [`Payout discipline: mean FCF/dividend coverage ${mc.toFixed(1)}x  (${health})`]]
  }

  const roicVals = series.map(yearRoic).filter((r): r is number => r !== null)
  const mr = mean(roicVals)
  if (mr > wacc * 1.2) return [0.70, ['Payout discipline: retaining FCF in above-WACC business (good reinvestment)']]
  if (mr <= wacc) return [0.35, ['Payout discipline: retaining FCF despite below-WACC returns (concerning)']]
  return [0.50, ['Payout discipline: no dividend data available (neutral score)']]
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute Capital Allocation Score from a sequence of annual financial records.
 *
 * @param annualData - Array of annual records in chronological order (oldest first).
 *                     Minimum 2 years required.
 * @param options    - Optional: `{ wacc }` to override WACC estimation.
 * @returns CapitalAllocationResult with score (0–100), rating, components, and evidence.
 */
export function capitalAllocationScore(
  annualData: AnnualCapitalData[],
  options: CapitalAllocationOptions = {},
): CapitalAllocationResult {
  if (annualData.length < 2) {
    throw new Error('capitalAllocationScore requires at least 2 years of data.')
  }

  const wacc = estimateWacc(annualData, options.wacc)

  const [vcScore, vcEv] = scoreValueCreation(annualData, wacc)
  const [fcfScore, fcfEv] = scoreFcfQuality(annualData)
  const [riScore, riEv] = scoreReinvestmentYield(annualData)
  const [pdScore, pdEv] = scorePayoutDiscipline(annualData, wacc)

  const raw = 0.35 * vcScore + 0.25 * fcfScore + 0.25 * riScore + 0.15 * pdScore
  const score = Math.round(clamp(raw, 0, 1) * 100)

  const rating: CapitalAllocationResult['rating'] =
    score >= 75 ? 'excellent' :
    score >= 50 ? 'good' :
    score >= 25 ? 'fair' : 'poor'

  return {
    score,
    rating,
    components: {
      valueCreation:    Math.round(vcScore  * 1e4) / 1e4,
      fcfQuality:       Math.round(fcfScore * 1e4) / 1e4,
      reinvestmentYield: Math.round(riScore * 1e4) / 1e4,
      payoutDiscipline: Math.round(pdScore  * 1e4) / 1e4,
    },
    waccUsed: wacc,
    yearsAnalyzed: annualData.length,
    evidence: [...vcEv, ...fcfEv, ...riEv, ...pdEv],
  }
}
