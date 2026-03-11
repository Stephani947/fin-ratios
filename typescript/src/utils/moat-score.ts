/**
 * Quantitative Economic Moat Score.
 *
 * Scores a company's competitive moat from 0–100 using five financial signals
 * derived entirely from multi-year financial statements — no analyst opinions,
 * no qualitative inputs, fully reproducible.
 *
 * Signals
 * -------
 * 1. ROIC Persistence     — fraction of years ROIC > WACC, penalised for volatility
 * 2. Pricing Power        — gross margin level × stability
 * 3. Reinvestment Quality — incremental return on invested capital (ΔEBIT / net reinvestment)
 * 4. Operating Leverage   — degree of operating leverage (fixed-cost structure proxy)
 * 5. CAP Estimate         — statistical projection of competitive advantage period
 *
 * Weights: 30 / 25 / 20 / 15 / 10
 *
 * References
 * ----------
 * Mauboussin & Johnson (1997) — Competitive Advantage Period, CSFB
 * Greenwald & Kahn (2001)     — Competition Demystified, Portfolio/Penguin
 * Koller, Goedhart & Wessels (2020) — Valuation (7th ed.), McKinsey & Company
 */

import { safeDivide } from './safe-divide.js'

// ── Input / Output types ───────────────────────────────────────────────────────

/** One year of financial data for moat analysis. */
export interface AnnualFinancialData {
  // Income statement
  revenue?: number
  grossProfit?: number
  ebit?: number
  netIncome?: number
  ebt?: number
  interestExpense?: number
  incomeTaxExpense?: number
  // Balance sheet
  totalAssets?: number
  totalEquity?: number
  totalDebt?: number
  cash?: number
  currentAssets?: number
  currentLiabilities?: number
  // Cash flow
  capex?: number
  depreciation?: number
  // Optional
  year?: number | string
}

export interface MoatComponents {
  roicPersistence: number      // 0–1
  pricingPower: number         // 0–1
  reinvestmentQuality: number  // 0–1
  operatingLeverage: number    // 0–1
  capScore: number             // 0–1 (normalised CAP)
}

export interface MoatScoreResult {
  score: number                 // 0–100
  width: 'wide' | 'narrow' | 'none'
  components: MoatComponents
  capEstimateYears: number      // projected years of above-normal returns
  waccUsed: number              // WACC estimate applied
  yearsAnalyzed: number
  evidence: string[]
  interpretation: string
}

export interface MoatScoreOptions {
  /** Override the WACC used in analysis (e.g. 0.09 for 9%). */
  wacc?: number
}

// ── Statistical helpers ────────────────────────────────────────────────────────

function mean(xs: number[]): number {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0
}

function std(xs: number[]): number {
  if (xs.length < 2) return 0
  const m = mean(xs)
  return Math.sqrt(xs.reduce((s, x) => s + (x - m) ** 2, 0) / (xs.length - 1))
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

// ── Per-year ROIC ──────────────────────────────────────────────────────────────

function g(d: AnnualFinancialData, key: keyof AnnualFinancialData): number {
  const v = d[key]
  return (typeof v === 'number' && !isNaN(v)) ? v : 0
}

function yearRoic(d: AnnualFinancialData): number | null {
  const ebit = g(d, 'ebit')
  const equity = g(d, 'totalEquity')
  const debt = g(d, 'totalDebt')
  const cash = g(d, 'cash')
  const ic = equity + debt - cash
  if (ic <= 0 || ebit <= 0) return null

  const ebt = g(d, 'ebt') || (ebit - g(d, 'interestExpense'))
  const tax = g(d, 'incomeTaxExpense')
  const taxRate = ebt > 0 && tax > 0 ? Math.min(Math.max(tax / ebt, 0), 0.5) : 0.21
  return (ebit * (1 - taxRate)) / ic
}

// ── WACC estimation ────────────────────────────────────────────────────────────

function estimateWacc(series: AnnualFinancialData[], override?: number): number {
  if (override !== undefined) return override
  const d = series[series.length - 1]!
  const equity = g(d, 'totalEquity')
  const debt = g(d, 'totalDebt')
  const totalCap = equity + debt
  if (totalCap <= 0) return 0.09

  const we = equity / totalCap
  const wd = debt / totalCap

  const costEquity = 0.045 + 1.0 * 0.055  // CAPM: rf=4.5%, beta=1, ERP=5.5% → 10%

  const interest = g(d, 'interestExpense')
  const preCostDebt = debt > 0 && interest > 0 ? Math.min(interest / debt, 0.15) : 0.05
  const ebt = g(d, 'ebt') || (g(d, 'ebit') - interest)
  const tax = g(d, 'incomeTaxExpense')
  const taxRate = ebt > 0 && tax > 0 ? Math.min(Math.max(tax / ebt, 0), 0.4) : 0.21
  const costDebt = preCostDebt * (1 - taxRate)

  return Math.max(Math.min(we * costEquity + wd * costDebt, 0.20), 0.06)
}

// ── Five signal scorers ────────────────────────────────────────────────────────

function scoreRoicPersistence(
  roicSeries: number[], wacc: number,
): [number, string[]] {
  if (!roicSeries.length) return [0, ['Insufficient ROIC data']]

  const above = roicSeries.filter(r => r > wacc).length
  const pctAbove = above / roicSeries.length
  const roicCv = cv(roicSeries)
  const meanRoic = mean(roicSeries)
  const spread = meanRoic - wacc

  const stability = Math.max(0, 1 - roicCv * 0.4)
  const score = Math.min(Math.max(pctAbove * stability, 0), 1)

  return [score, [
    `ROIC exceeded WACC in ${above}/${roicSeries.length} years (${(pctAbove * 100).toFixed(0)}%)`,
    `Mean ROIC ${(meanRoic * 100).toFixed(1)}%  vs  WACC ${(wacc * 100).toFixed(1)}%  (spread ${spread >= 0 ? '+' : ''}${(spread * 100).toFixed(1)}%)`,
    `ROIC volatility (CV): ${roicCv.toFixed(2)} — ${roicCv < 0.15 ? 'highly stable' : roicCv < 0.30 ? 'stable' : 'volatile'}`,
  ]]
}

function scorePricingPower(gmSeries: number[]): [number, string[]] {
  if (!gmSeries.length) return [0.5, ['Gross margin unavailable — pricing power assumed neutral']]

  const meanGm = mean(gmSeries)
  const gmCv = cv(gmSeries)
  const slope = olsSlope(gmSeries)

  const level = Math.min(Math.max((meanGm - 0.20) / 0.40, 0), 1)
  const stability = Math.max(0, 1 - gmCv * 2.5)
  const trendAdj = Math.max(Math.min(slope * 10, 0.1), -0.1)
  const score = Math.min(Math.max(0.6 * level + 0.4 * stability + trendAdj, 0), 1)

  const trendLbl = slope > 0.005 ? 'improving' : slope < -0.005 ? 'declining' : 'stable'

  return [score, [
    `Mean gross margin ${(meanGm * 100).toFixed(1)}% over ${gmSeries.length} years`,
    `Gross margin CV ${gmCv.toFixed(3)} — ${gmCv < 0.05 ? 'excellent stability' : gmCv < 0.15 ? 'moderate' : 'high variability'}`,
    `Gross margin trend: ${trendLbl}`,
  ]]
}

function scoreReinvestmentQuality(series: AnnualFinancialData[]): [number, string[]] {
  if (series.length < 2) return [0.5, ['Insufficient data for reinvestment quality — assumed neutral']]

  const roiicVals: number[] = []
  let negativeCount = 0
  for (let i = 1; i < series.length; i++) {
    const prev = series[i - 1]!
    const curr = series[i]!
    const deltaEbit = g(curr, 'ebit') - g(prev, 'ebit')
    const netReinvest =
      (g(curr, 'capex') - g(curr, 'depreciation'))
      + (g(curr, 'currentAssets') - g(curr, 'currentLiabilities'))
      - (g(prev, 'currentAssets') - g(prev, 'currentLiabilities'))

    if (netReinvest > 1e6) {
      roiicVals.push(Math.max(Math.min(deltaEbit / netReinvest, 5), -1))
    } else {
      negativeCount++
    }
  }

  const totalPeriods = series.length - 1
  const capitalLight = !roiicVals.length || (negativeCount / totalPeriods > 0.5)

  if (capitalLight) {
    const ebitGrowth: number[] = []
    for (let i = 1; i < series.length; i++) {
      const prevEbit = g(series[i - 1]!, 'ebit')
      if (prevEbit > 0) ebitGrowth.push(g(series[i]!, 'ebit') / prevEbit - 1)
    }
    if (ebitGrowth.length && mean(ebitGrowth) > 0.05) {
      return [0.82, [
        'Capital-light model: EBIT growing with minimal net reinvestment',
        'Low reinvestment requirement is a strong moat signal',
      ]]
    }
    return [0.5, ['Reinvestment quality indeterminate (limited reinvestment data)']]
  }

  const meanRoiic = mean(roiicVals)
  const score = Math.min(Math.max(0.30 + meanRoiic * 0.70, 0), 1)

  return [score, [
    `Mean incremental ROIC (ROIIC): ${(meanRoiic * 100).toFixed(1)}%`,
    `Based on ${roiicVals.length} reinvestment period(s)`,
    meanRoiic > 0.5
      ? 'Excellent capital reinvestment efficiency'
      : meanRoiic > 0.15
        ? 'Adequate reinvestment returns'
        : 'Low incremental returns on reinvestment',
  ]]
}

function scoreOperatingLeverage(series: AnnualFinancialData[]): [number, string[]] {
  if (series.length < 2) return [0.5, ['Insufficient data for operating leverage']]

  const dolVals: number[] = []
  for (let i = 1; i < series.length; i++) {
    const prev = series[i - 1]!
    const curr = series[i]!
    if (g(prev, 'revenue') <= 0 || Math.abs(g(prev, 'ebit')) < 1e5) continue
    const pctRev = (g(curr, 'revenue') - g(prev, 'revenue')) / g(prev, 'revenue')
    const pctEbit = (g(curr, 'ebit') - g(prev, 'ebit')) / Math.abs(g(prev, 'ebit'))
    if (Math.abs(pctRev) > 0.005) {
      const dol = pctEbit / pctRev
      if (dol > 0 && dol < 25) dolVals.push(dol)
    }
  }

  if (!dolVals.length) return [0.4, ['Operating leverage indeterminate (insufficient revenue variance)']]

  const meanDol = mean(dolVals)
  const cvDol = cv(dolVals)
  const level = Math.min(Math.max((meanDol - 1) / 5, 0), 1)
  const consistency = Math.max(0, 1 - cvDol * 0.5)
  const score = Math.min(Math.max(0.65 * level + 0.35 * consistency, 0), 1)

  const quality = meanDol > 3
    ? 'High fixed-cost structure — strong scale advantages'
    : meanDol > 1.5
      ? 'Moderate operating leverage'
      : 'Variable cost structure — limited scale advantage'

  return [score, [
    `Mean degree of operating leverage (DOL): ${meanDol.toFixed(2)}×`,
    `DOL consistency: ${(consistency * 100).toFixed(0)}%`,
    quality,
  ]]
}

function scoreCap(
  roicSeries: number[], wacc: number,
): [number, number, string[]] {
  if (!roicSeries.length) return [0.3, 5, ['Insufficient data for CAP estimate']]

  const meanRoic = mean(roicSeries)
  const spread = meanRoic - wacc

  if (spread <= 0) {
    return [0, 0, [`ROIC ${(meanRoic * 100).toFixed(1)}% ≤ WACC ${(wacc * 100).toFixed(1)}%: no competitive advantage detected`]]
  }

  const slope = olsSlope(roicSeries)
  let capYears: number
  let direction: string

  if (slope < -0.005) {
    capYears = Math.min(Math.max(spread / Math.abs(slope), 0), 30)
    direction = 'declining'
  } else if (slope > 0.005) {
    capYears = Math.min(spread * 80 + 5, 30)
    direction = 'improving'
  } else {
    const roicCv = cv(roicSeries)
    capYears = Math.min(Math.max(spread * 60 / Math.max(roicCv, 0.1), 3), 25)
    direction = 'stable'
  }

  const capScore = Math.min(capYears / 20, 1)
  return [capScore, capYears, [
    `Estimated competitive advantage period: ${capYears.toFixed(1)} years`,
    `ROIC trend: ${direction} (slope ${slope >= 0 ? '+' : ''}${slope.toFixed(3)}/yr)`,
    `ROIC spread above WACC: ${spread >= 0 ? '+' : ''}${(spread * 100).toFixed(1)}%`,
  ]]
}

// ── Weights ────────────────────────────────────────────────────────────────────

const W = {
  roicPersistence:    0.30,
  pricingPower:       0.25,
  reinvestmentQuality:0.20,
  operatingLeverage:  0.15,
  cap:                0.10,
}

// ── Public API ─────────────────────────────────────────────────────────────────

/**
 * Compute a quantitative economic moat score from a sequence of annual data.
 *
 * @param annualData  Array of annual financial data objects, ordered chronologically
 *                    (oldest first). Minimum 2 years; 5–10 recommended.
 * @param options     Optional configuration (wacc override)
 *
 * @returns MoatScoreResult with score 0–100, width classification, and evidence
 *
 * @example
 *   const result = moatScore([
 *     { year: 2020, revenue: 274e9, grossProfit: 105e9, ebit: 66e9,
 *       totalEquity: 65e9, totalDebt: 112e9, totalAssets: 323e9, cash: 38e9,
 *       capex: 7e9, depreciation: 11e9 },
 *     { year: 2021, revenue: 365e9, grossProfit: 153e9, ebit: 109e9,
 *       totalEquity: 63e9, totalDebt: 122e9, totalAssets: 351e9, cash: 62e9,
 *       capex: 11e9, depreciation: 11e9 },
 *     // ... more years
 *   ])
 *   console.log(result.score)   // 82
 *   console.log(result.width)   // 'wide'
 */
export function moatScore(
  annualData: AnnualFinancialData[],
  options: MoatScoreOptions = {},
): MoatScoreResult {
  if (annualData.length < 2) {
    throw new Error('moatScore requires at least 2 years of data (3–10 recommended).')
  }

  const estWacc = estimateWacc(annualData, options.wacc)

  const roicSeries: number[] = annualData
    .map(yearRoic)
    .filter((r): r is number => r !== null)

  const gmSeries: number[] = annualData
    .filter(d => g(d, 'revenue') > 0)
    .map(d => (safeDivide(g(d, 'grossProfit'), g(d, 'revenue')) ?? 0))

  const [sRp, evRp] = scoreRoicPersistence(roicSeries, estWacc)
  const [sPp, evPp] = scorePricingPower(gmSeries)
  const [sRq, evRq] = scoreReinvestmentQuality(annualData)
  const [sOl, evOl] = scoreOperatingLeverage(annualData)
  const [sCp, capYears, evCp] = scoreCap(roicSeries, estWacc)

  const raw =
    W.roicPersistence     * sRp
    + W.pricingPower      * sPp
    + W.reinvestmentQuality * sRq
    + W.operatingLeverage * sOl
    + W.cap               * sCp

  const score = Math.round(Math.min(Math.max(raw * 100, 0), 100))
  const width: 'wide' | 'narrow' | 'none' =
    score >= 70 ? 'wide' : score >= 40 ? 'narrow' : 'none'

  const desc = {
    wide:   'Durable competitive advantage likely to persist for 10+ years',
    narrow: 'Real but limited or potentially fading competitive advantage',
    none:   'No detectable financial signature of a durable economic moat',
  }

  return {
    score,
    width,
    components: {
      roicPersistence:     parseFloat(sRp.toFixed(4)),
      pricingPower:        parseFloat(sPp.toFixed(4)),
      reinvestmentQuality: parseFloat(sRq.toFixed(4)),
      operatingLeverage:   parseFloat(sOl.toFixed(4)),
      capScore:            parseFloat(sCp.toFixed(4)),
    },
    capEstimateYears: parseFloat(capYears.toFixed(1)),
    waccUsed:         parseFloat(estWacc.toFixed(4)),
    yearsAnalyzed:    annualData.length,
    evidence:         [...evRp, ...evPp, ...evRq, ...evOl, ...evCp],
    interpretation:   `Score ${score}/100: ${desc[width]}`,
  }
}
