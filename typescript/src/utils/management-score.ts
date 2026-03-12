/**
 * Management Quality Score.
 *
 * Evaluates management's operational effectiveness using multi-year financial
 * series. A high-scoring management team consistently earns strong returns on
 * invested capital, expands or defends operating margins, treats shareholders
 * with respect by avoiding dilution, and delivers reliable revenue growth.
 *
 * Signals
 * -------
 * 1. ROIC Excellence        (35%) — level, trend, and consistency of ROIC
 * 2. Margin Stability       (25%) — operating margin level, trend, and stability
 * 3. Shareholder Orientation(25%) — share count trajectory (buybacks vs dilution)
 * 4. Revenue Execution      (15%) — revenue growth rate level and consistency
 *
 * Score:  0–100
 * Rating: 'excellent' (≥75), 'good' (50–74), 'fair' (25–49), 'poor' (<25)
 *
 * Minimum 3 years of data required.
 */

// ── Types ──────────────────────────────────────────────────────────────────────

/** One year of financial data for management quality analysis. */
export interface AnnualManagementData {
  revenue?: number
  ebit?: number
  totalAssets?: number
  totalEquity?: number
  totalDebt?: number
  cash?: number
  sharesOutstanding?: number
  incomeTaxExpense?: number
  ebt?: number
  interestExpense?: number
  year?: number | string
}

export interface ManagementComponents {
  roicExcellence: number        // 0–1
  marginStability: number       // 0–1
  shareholderOrientation: number // 0–1
  revenueExecution: number      // 0–1
}

export interface ManagementScore {
  score: number
  rating: 'excellent' | 'good' | 'fair' | 'poor'
  components: ManagementComponents
  hurdleRateUsed: number
  yearsAnalyzed: number
  evidence: string[]
  interpretation: string
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

function lerp(x: number, x0: number, x1: number, y0: number, y1: number): number {
  if (x1 === x0) return y0
  return y0 + clamp((x - x0) / (x1 - x0), 0, 1) * (y1 - y0)
}

function g(d: AnnualManagementData, k: keyof AnnualManagementData): number {
  const v = d[k]
  return typeof v === 'number' && isFinite(v) ? v : 0
}

// ── ROIC per year ──────────────────────────────────────────────────────────────

function yearRoic(d: AnnualManagementData): number | null {
  const ebit = g(d, 'ebit')
  const ic = g(d, 'totalEquity') + g(d, 'totalDebt') - g(d, 'cash')
  if (ic <= 0) return null
  const ebt = g(d, 'ebt') || (ebit - g(d, 'interestExpense'))
  const tax = g(d, 'incomeTaxExpense')
  const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.50) : 0.21
  return (ebit * (1 - taxRate)) / ic
}

// ── Hurdle rate estimation (simplified) ───────────────────────────────────────

function estimateHurdleRate(series: AnnualManagementData[], provided?: number): number {
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
    const ebt = g(d, 'ebt') || (g(d, 'ebit') - interest)
    const tax = g(d, 'incomeTaxExpense')
    const taxRate = ebt > 0 && tax > 0 ? clamp(tax / ebt, 0, 0.40) : 0.21
    costDebt = preTax * (1 - taxRate)
  }
  const wE = clamp(equity / totalCap, 0, 1)
  return clamp(wE * costEquity + (1 - wE) * costDebt, 0.06, 0.20)
}

// ── Signal 1: ROIC Excellence ─────────────────────────────────────────────────

function scoreRoicExcellence(series: AnnualManagementData[], hurdle: number): [number, string[]] {
  const roicVals = series.map(yearRoic).filter((r): r is number => r !== null)
  if (!roicVals.length) return [0.35, ['ROIC excellence: insufficient data (neutral score)']]

  const meanRoic = mean(roicVals)
  const slope = olsSlope(roicVals)
  const consistency = clamp(1 - cv(roicVals) * 0.5, 0, 1)
  const level = lerp(meanRoic, 0.05, 0.30, 0, 1)
  const trendAdj = slope > 0.01 ? 0.08 : slope < -0.01 ? -0.08 : 0
  const score = clamp(0.55 * level + 0.35 * consistency + trendAdj, 0, 1)

  const aboveHurdle = roicVals.filter(r => r > hurdle).length
  const dir = slope > 0.01 ? 'improving' : slope < -0.01 ? 'declining' : 'stable'
  return [score, [
    `ROIC excellence: mean ${(meanRoic * 100).toFixed(1)}%  (hurdle ${(hurdle * 100).toFixed(1)}%,  ${aboveHurdle}/${roicVals.length} years above)`,
    `ROIC trend: ${dir}  (OLS ${(slope * 100).toFixed(2)}%/yr)`,
  ]]
}

// ── Signal 2: Margin Stability ────────────────────────────────────────────────

function scoreMarginStability(series: AnnualManagementData[]): [number, string[]] {
  const margins = series
    .filter(d => g(d, 'revenue') > 0 && g(d, 'ebit') !== 0)
    .map(d => g(d, 'ebit') / g(d, 'revenue'))

  if (margins.length < 2) return [0.40, ['Margin stability: insufficient revenue/EBIT data (neutral score)']]

  const meanMargin = mean(margins)
  const slope = olsSlope(margins)
  const consistency = clamp(1 - cv(margins) * 1.0, 0, 1)
  const level = lerp(meanMargin, 0, 0.30, 0, 1)
  const trendAdj = slope > 0.005 ? 0.08 : slope < -0.005 ? -0.08 : 0
  const score = clamp(0.50 * level + 0.40 * consistency + trendAdj, 0, 1)

  const dir = slope > 0.005 ? 'expanding' : slope < -0.005 ? 'contracting' : 'stable'
  const quality = meanMargin >= 0.20 ? 'high' : meanMargin >= 0.10 ? 'moderate' : 'thin'
  return [score, [
    `Operating margin: mean ${(meanMargin * 100).toFixed(1)}%  (${quality} quality,  CV ${cv(margins).toFixed(3)})`,
    `Margin trend: ${dir}  (OLS ${(slope * 100).toFixed(3)}%/yr)`,
  ]]
}

// ── Signal 3: Shareholder Orientation ────────────────────────────────────────

function scoreShareholderOrientation(series: AnnualManagementData[]): [number, string[]] {
  const shares = series
    .map(d => g(d, 'sharesOutstanding'))
    .filter(s => s > 0)

  if (shares.length < 2) return [0.50, ['Shareholder orientation: share count data unavailable (neutral score)']]

  const meanShares = mean(shares)
  // OLS slope as a fraction of mean shares per year
  const slope = olsSlope(shares)
  const slopePct = meanShares > 0 ? slope / meanShares : 0
  const score = clamp(0.5 - slopePct * 5, 0, 1)

  const pctChange = (shares[shares.length - 1]! - shares[0]!) / shares[0]!
  const dir = slopePct < -0.01 ? 'declining (buybacks)' : slopePct > 0.01 ? 'growing (dilution)' : 'roughly flat'
  return [score, [
    `Share count: ${dir}  (${pctChange >= 0 ? '+' : ''}${(pctChange * 100).toFixed(1)}% over period)`,
    slopePct < -0.005
      ? 'Management is reducing share count — shareholder friendly'
      : slopePct > 0.02
        ? 'Material share dilution detected — value transfer risk'
        : 'Share count broadly stable',
  ]]
}

// ── Signal 4: Revenue Execution ───────────────────────────────────────────────

function scoreRevenueExecution(series: AnnualManagementData[]): [number, string[]] {
  const growthRates: number[] = []
  for (let i = 1; i < series.length; i++) {
    const prevRev = g(series[i - 1]!, 'revenue')
    const currRev = g(series[i]!, 'revenue')
    if (prevRev > 0) growthRates.push((currRev - prevRev) / prevRev)
  }
  if (!growthRates.length) return [0.40, ['Revenue execution: insufficient revenue data (neutral score)']]

  const meanGrowth = mean(growthRates)
  const level = lerp(meanGrowth, -0.05, 0.20, 0, 1)
  const consistency = clamp(1 - cv(growthRates) * 0.4, 0, 1)
  const score = clamp(0.65 * level + 0.35 * consistency, 0, 1)

  const posYears = growthRates.filter(r => r > 0).length
  const quality = meanGrowth >= 0.10 ? 'strong' : meanGrowth >= 0.04 ? 'adequate' : meanGrowth >= 0 ? 'sluggish' : 'declining'
  return [score, [
    `Revenue growth: mean ${(meanGrowth * 100).toFixed(1)}%/yr  (${quality},  ${posYears}/${growthRates.length} years positive)`,
  ]]
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute Management Quality Score from a sequence of annual financial records.
 *
 * @param annualData  Array in chronological order (oldest first). Minimum 3 years.
 * @param hurdleRate  Optional WACC override (e.g. 0.09 for 9%).
 * @returns ManagementScore with score (0–100), rating, components, evidence.
 *
 * @example
 *   const result = managementQualityScoreFromSeries([
 *     { year: 2020, revenue: 100e9, ebit: 22e9, totalEquity: 40e9, totalDebt: 10e9,
 *       cash: 5e9, sharesOutstanding: 5e9 },
 *     { year: 2021, revenue: 115e9, ebit: 26e9, totalEquity: 44e9, totalDebt: 10e9,
 *       cash: 7e9, sharesOutstanding: 4.9e9 },
 *     { year: 2022, revenue: 130e9, ebit: 30e9, totalEquity: 48e9, totalDebt: 9e9,
 *       cash: 9e9, sharesOutstanding: 4.75e9 },
 *   ])
 *   console.log(result.score)    // e.g. 78
 *   console.log(result.rating)   // 'excellent'
 */
export function managementQualityScoreFromSeries(
  annualData: AnnualManagementData[],
  hurdleRate?: number,
): ManagementScore {
  if (annualData.length < 3) {
    throw new Error('managementQualityScoreFromSeries requires at least 3 years of data.')
  }

  const hurdle = estimateHurdleRate(annualData, hurdleRate)

  const [roicScore, roicEv] = scoreRoicExcellence(annualData, hurdle)
  const [marginScore, marginEv] = scoreMarginStability(annualData)
  const [soScore, soEv] = scoreShareholderOrientation(annualData)
  const [revScore, revEv] = scoreRevenueExecution(annualData)

  const raw = 0.35 * roicScore + 0.25 * marginScore + 0.25 * soScore + 0.15 * revScore
  const score = Math.round(clamp(raw, 0, 1) * 100)

  const rating: ManagementScore['rating'] =
    score >= 75 ? 'excellent' :
    score >= 50 ? 'good' :
    score >= 25 ? 'fair' : 'poor'

  const desc: Record<ManagementScore['rating'], string> = {
    excellent: 'Management consistently earns high ROIC, protects margins, and treats shareholders well',
    good:      'Solid operational track record with most quality signals positive',
    fair:      'Mixed signals — some areas of strength but meaningful shortfalls elsewhere',
    poor:      'Weak returns, margin deterioration, or material shareholder dilution detected',
  }

  return {
    score,
    rating,
    components: {
      roicExcellence:         Math.round(roicScore  * 1e4) / 1e4,
      marginStability:        Math.round(marginScore * 1e4) / 1e4,
      shareholderOrientation: Math.round(soScore    * 1e4) / 1e4,
      revenueExecution:       Math.round(revScore   * 1e4) / 1e4,
    },
    hurdleRateUsed: hurdle,
    yearsAnalyzed: annualData.length,
    evidence: [...roicEv, ...marginEv, ...soEv, ...revEv],
    interpretation: `Score ${score}/100: ${desc[rating]}`,
  }
}
