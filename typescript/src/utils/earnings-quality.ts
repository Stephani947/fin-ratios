/**
 * Earnings Quality Score.
 *
 * Quantifies how reliable and sustainable a company's reported earnings are.
 * High-quality earnings are predominantly cash-backed, derived from core
 * operations, and free of aggressive accounting.
 *
 * Signals
 * -------
 * 1. Accruals Ratio         (30%) — (NI − CFO) / Avg Assets; Sloan (1996)
 * 2. Cash Earnings Quality  (25%) — CFO / NI; Richardson et al. (2005)
 * 3. Revenue Recognition    (20%) — Revenue growth vs AR growth spread
 * 4. Gross Margin Stability (15%) — stable margins signal genuine pricing
 * 5. Asset Efficiency Trend (10%) — declining asset turnover = potential concern
 *
 * Score:  0–100
 * Rating: 'high' (75–100), 'medium' (50–74), 'low' (25–49), 'poor' (0–24)
 */

// ── Types ──────────────────────────────────────────────────────────────────────

/** One year of financial data for earnings quality analysis. */
export interface AnnualEarningsData {
  revenue?: number
  grossProfit?: number
  netIncome?: number
  operatingCashFlow?: number
  totalAssets?: number
  accountsReceivable?: number
  year?: number | string
}

export interface EarningsQualityComponents {
  accrualsRatio: number          // 0–1
  cashEarnings: number           // 0–1
  revenueRecognition: number     // 0–1
  grossMarginStability: number   // 0–1
  assetEfficiency: number        // 0–1
}

export interface EarningsQualityResult {
  score: number                                          // 0–100
  rating: 'high' | 'medium' | 'low' | 'poor'
  components: EarningsQualityComponents
  yearsAnalyzed: number
  evidence: string[]
}

export interface EarningsQualityOptions {
  // reserved for future use
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

function g(d: AnnualEarningsData, k: keyof AnnualEarningsData): number {
  const v = d[k]
  return typeof v === 'number' && isFinite(v) ? v : 0
}

// ── Signal 1: Accruals Ratio ──────────────────────────────────────────────────

function scoreAccruals(series: AnnualEarningsData[]): [number, string[]] {
  const ratios: number[] = []
  for (let i = 0; i < series.length; i++) {
    const d = series[i]!
    const ni = g(d, 'netIncome')
    const cfo = g(d, 'operatingCashFlow')
    if (ni === 0 && cfo === 0) continue
    const prevAssets = i > 0 ? g(series[i - 1]!, 'totalAssets') : g(d, 'totalAssets')
    const avgAssets = (g(d, 'totalAssets') + prevAssets) / 2
    if (avgAssets <= 0) continue
    ratios.push((ni - cfo) / avgAssets)
  }
  if (!ratios.length) return [0.40, ['Accruals ratio: operating cash flow not available (neutral score)']]

  const ma = mean(ratios)
  const level = clamp(1 - (ma + 0.05) / 0.15, 0, 1)
  const stability = Math.max(0, 1 - cv(ratios))
  const score = clamp(0.70 * level + 0.30 * stability, 0, 1)
  const quality = ma < 0 ? 'cash-backed' : ma < 0.05 ? 'modest accruals' : 'high accruals'
  return [score, [
    `Accruals ratio: mean ${(ma * 100).toFixed(1)}% of assets  (${quality})`,
    ma < 0.02 ? 'Earnings predominantly backed by cash flows' : 'Elevated accruals — verify cash conversion',
  ]]
}

// ── Signal 2: Cash Earnings Quality ───────────────────────────────────────────

function scoreCashEarnings(series: AnnualEarningsData[]): [number, string[]] {
  const ratios: number[] = []
  for (const d of series) {
    const ni = g(d, 'netIncome')
    const cfo = g(d, 'operatingCashFlow')
    if (ni > 0) ratios.push(cfo / ni)
  }
  if (!ratios.length) return [0.40, ['Cash earnings quality: insufficient CFO/NI data (neutral score)']]

  const mr = mean(ratios)
  const level = clamp((mr - 0.5) / 1.0, 0, 1)
  const stability = Math.max(0, 1 - cv(ratios) * 0.8)
  const score = clamp(0.65 * level + 0.35 * stability, 0, 1)
  const above = ratios.filter(r => r >= 1).length
  const quality = mr >= 1.2 ? 'excellent' : mr >= 0.9 ? 'good' : 'weak'
  return [score, [
    `CFO/NI conversion: mean ${mr.toFixed(2)}×  (${above}/${ratios.length} years ≥ 1.0)`,
    `Cash earnings quality: ${quality}`,
  ]]
}

// ── Signal 3: Revenue Recognition ─────────────────────────────────────────────

function scoreRevenueRecognition(series: AnnualEarningsData[]): [number, string[]] {
  const spreads: number[] = []
  for (let i = 1; i < series.length; i++) {
    const prev = series[i - 1]!
    const curr = series[i]!
    if (g(prev, 'revenue') <= 0) continue
    const revGrowth = (g(curr, 'revenue') - g(prev, 'revenue')) / g(prev, 'revenue')
    const arPrev = g(prev, 'accountsReceivable')
    const arCurr = g(curr, 'accountsReceivable')
    if (arPrev > 0 && arCurr > 0) {
      spreads.push(revGrowth - (arCurr - arPrev) / arPrev)
    }
  }
  if (!spreads.length) return [0.45, ['Revenue recognition: accounts receivable data unavailable (neutral score)']]

  const ms = mean(spreads)
  const level = clamp((ms + 0.15) / 0.25, 0, 1)
  const consistency = Math.max(0, 1 - cv(spreads) * 0.5)
  const score = clamp(0.65 * level + 0.35 * consistency, 0, 1)
  const quality = ms > 0.05 ? 'conservative' : ms > -0.05 ? 'neutral' : 'aggressive'
  const pos = spreads.filter(s => s >= 0).length
  return [score, [
    `Revenue recognition: revenue-AR spread ${(ms * 100).toFixed(1)}%/yr  (${quality})`,
    `Revenue outpaced receivables in ${pos}/${spreads.length} periods`,
  ]]
}

// ── Signal 4: Gross Margin Stability ──────────────────────────────────────────

function scoreGrossMarginStability(series: AnnualEarningsData[]): [number, string[]] {
  const gms = series
    .filter(d => g(d, 'revenue') > 0 && g(d, 'grossProfit') > 0)
    .map(d => g(d, 'grossProfit') / g(d, 'revenue'))
  if (gms.length < 2) return [0.45, ['Gross margin stability: insufficient data (neutral score)']]

  const mgm = mean(gms)
  const cvGm = cv(gms)
  const slope = olsSlope(gms)
  const stability = clamp(1 - cvGm * 3, 0, 1)
  const trendAdj = slope > 0.005 ? 0.08 : slope < -0.005 ? -0.08 : 0
  const score = clamp(stability + trendAdj, 0, 1)
  const trend = slope > 0.005 ? 'improving' : slope < -0.005 ? 'eroding' : 'stable'
  const quality = cvGm < 0.05 ? 'high' : cvGm < 0.15 ? 'moderate' : 'low'
  return [score, [
    `Gross margin: mean ${(mgm * 100).toFixed(1)}%  stability ${quality} (CV ${cvGm.toFixed(3)})`,
    `Gross margin trend: ${trend}`,
  ]]
}

// ── Signal 5: Asset Efficiency ────────────────────────────────────────────────

function scoreAssetEfficiency(series: AnnualEarningsData[]): [number, string[]] {
  const tos = series
    .filter(d => g(d, 'totalAssets') > 0 && g(d, 'revenue') > 0)
    .map(d => g(d, 'revenue') / g(d, 'totalAssets'))
  if (tos.length < 2) return [0.45, ['Asset efficiency: insufficient data (neutral score)']]

  const slope = olsSlope(tos)
  const mto = mean(tos)
  const trendScore = clamp(0.5 + slope * 5, 0, 1)
  const level = clamp((mto - 0.2) / 1.5, 0, 1)
  const score = clamp(0.50 * trendScore + 0.50 * level, 0, 1)
  const dir = slope > 0.02 ? 'improving' : slope < -0.02 ? 'declining' : 'stable'
  return [score, [`Asset turnover: mean ${mto.toFixed(2)}×  trend ${dir}  (slope ${slope.toFixed(3)}/yr)`]]
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute Earnings Quality Score from a sequence of annual financial records.
 *
 * @param annualData - Array in chronological order (oldest first). Min 2 years.
 * @returns EarningsQualityResult with score (0–100), rating, components, evidence.
 */
export function earningsQualityScore(
  annualData: AnnualEarningsData[],
  _options: EarningsQualityOptions = {},
): EarningsQualityResult {
  if (annualData.length < 2) {
    throw new Error('earningsQualityScore requires at least 2 years of data.')
  }

  const [accScore, accEv]   = scoreAccruals(annualData)
  const [cfeScore, cfeEv]   = scoreCashEarnings(annualData)
  const [revScore, revEv]   = scoreRevenueRecognition(annualData)
  const [gmsScore, gmsEv]   = scoreGrossMarginStability(annualData)
  const [effScore, effEv]   = scoreAssetEfficiency(annualData)

  const raw = 0.30 * accScore + 0.25 * cfeScore + 0.20 * revScore + 0.15 * gmsScore + 0.10 * effScore
  const score = Math.round(clamp(raw, 0, 1) * 100)
  const rating: EarningsQualityResult['rating'] =
    score >= 75 ? 'high' :
    score >= 50 ? 'medium' :
    score >= 25 ? 'low' : 'poor'

  return {
    score,
    rating,
    components: {
      accrualsRatio:        Math.round(accScore * 1e4) / 1e4,
      cashEarnings:         Math.round(cfeScore * 1e4) / 1e4,
      revenueRecognition:   Math.round(revScore * 1e4) / 1e4,
      grossMarginStability: Math.round(gmsScore * 1e4) / 1e4,
      assetEfficiency:      Math.round(effScore * 1e4) / 1e4,
    },
    yearsAnalyzed: annualData.length,
    evidence: [...accEv, ...cfeEv, ...revEv, ...gmsEv, ...effEv],
  }
}
