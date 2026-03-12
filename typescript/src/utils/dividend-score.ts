/**
 * Dividend Safety Score.
 *
 * Assesses the probability that a company can maintain and grow its dividend
 * using multi-year financial data. The analysis covers free cash flow coverage,
 * earnings coverage, balance sheet capacity, and dividend growth track record.
 *
 * Non-payers receive a special rating rather than a scored assessment.
 *
 * Signals (dividend-payers only)
 * -------
 * 1. FCF Payout Ratio       (35%) — dividends as fraction of free cash flow
 * 2. Earnings Payout Ratio  (25%) — dividends as fraction of net income
 * 3. Balance Sheet Strength (25%) — net debt / EBITDA capacity headroom
 * 4. Dividend Growth Track  (15%) — consecutive years of non-declining dividends
 *
 * Score:  0–100
 * Rating: 'safe' (≥70), 'adequate' (45–69), 'risky' (20–44), 'danger' (<20), 'non-payer'
 */

// ── Types ──────────────────────────────────────────────────────────────────────

export interface DividendComponents {
  fcfPayoutRatio: number        // 0–1
  earningsPayoutRatio: number   // 0–1
  balanceSheetStrength: number  // 0–1
  dividendGrowthTrack: number   // 0–1
}

export interface DividendSafetyScore {
  score: number
  rating: 'safe' | 'adequate' | 'risky' | 'danger' | 'non-payer'
  components: DividendComponents
  isDividendPayer: boolean
  yearsAnalyzed: number
  evidence: string[]
  interpretation: string
}

/** One year of financial data for dividend safety analysis. */
export type AnnualDividendData = {
  dividendsPaid?: number
  operatingCashFlow?: number
  capex?: number
  netIncome?: number
  totalDebt?: number
  cash?: number
  ebit?: number
  depreciation?: number
  year?: number | string
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function mean(xs: number[]): number {
  return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0
}

function clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x))
}

function g(d: AnnualDividendData, k: keyof AnnualDividendData): number {
  const v = d[k]
  return typeof v === 'number' && isFinite(v) ? v : 0
}

// ── Payer detection ───────────────────────────────────────────────────────────

function isDividendPayer(series: AnnualDividendData[]): boolean {
  return series.some(d => {
    const div = d.dividendsPaid
    return typeof div === 'number' && isFinite(div) && div > 0
  })
}

// ── Signal 1: FCF Payout Ratio ────────────────────────────────────────────────

function scoreFcfPayout(series: AnnualDividendData[]): [number, string[]] {
  const ratios: number[] = []
  for (const d of series) {
    const div = g(d, 'dividendsPaid')
    if (div <= 0) continue
    const cfo = g(d, 'operatingCashFlow')
    const capex = g(d, 'capex')
    const fcf = cfo - capex
    if (fcf !== 0) ratios.push(div / fcf)
  }
  if (!ratios.length) return [0.50, ['FCF payout ratio: no dividend/FCF overlap (neutral score)']]

  const avg = mean(ratios)
  let score: number
  if (avg < 0.4)       score = 1.0
  else if (avg < 0.6)  score = 0.75
  else if (avg < 0.8)  score = 0.45
  else if (avg <= 1.0) score = 0.15
  else                 score = 0.0

  const quality = avg < 0.4 ? 'very well covered' : avg < 0.6 ? 'adequately covered' : avg < 0.8 ? 'tight' : avg <= 1.0 ? 'stressed' : 'uncovered by FCF'
  return [score, [
    `FCF payout ratio: mean ${(avg * 100).toFixed(0)}%  (${quality})`,
  ]]
}

// ── Signal 2: Earnings Payout Ratio ───────────────────────────────────────────

function scoreEarningsPayout(series: AnnualDividendData[]): [number, string[]] {
  const ratios: number[] = []
  for (const d of series) {
    const div = g(d, 'dividendsPaid')
    const ni = g(d, 'netIncome')
    if (div > 0 && ni > 0) ratios.push(div / ni)
  }
  if (!ratios.length) return [0.50, ['Earnings payout ratio: no dividend/earnings overlap (neutral score)']]

  const avg = mean(ratios)
  let score: number
  if (avg < 0.35)      score = 1.0
  else if (avg < 0.55) score = 0.75
  else if (avg < 0.75) score = 0.45
  else if (avg <= 1.0) score = 0.20
  else                 score = 0.0

  const quality = avg < 0.35 ? 'conservative' : avg < 0.55 ? 'moderate' : avg < 0.75 ? 'elevated' : avg <= 1.0 ? 'high' : 'exceeds earnings'
  return [score, [
    `Earnings payout ratio: mean ${(avg * 100).toFixed(0)}%  (${quality})`,
  ]]
}

// ── Signal 3: Balance Sheet Strength ──────────────────────────────────────────

function scoreBalanceSheet(series: AnnualDividendData[]): [number, string[]] {
  // Use most recent year
  const d = series[series.length - 1]!
  const totalDebt = g(d, 'totalDebt')
  const cash = g(d, 'cash')
  const netDebt = totalDebt - cash
  const ebit = g(d, 'ebit')
  const dep = g(d, 'depreciation')
  const ebitda = ebit + dep

  if (ebitda <= 0) {
    return [0.30, ['Balance sheet strength: EBITDA unavailable or negative (below-neutral score)']]
  }

  const ratio = netDebt / ebitda
  let score: number
  if (ratio < 0)       score = 1.0
  else if (ratio < 1)  score = 0.85
  else if (ratio < 2)  score = 0.65
  else if (ratio < 3)  score = 0.40
  else if (ratio < 4)  score = 0.20
  else                 score = 0.05

  const quality = ratio < 0 ? 'net cash position' : ratio < 1 ? 'very low leverage' : ratio < 2 ? 'modest leverage' : ratio < 3 ? 'moderate leverage' : ratio < 4 ? 'elevated leverage' : 'highly levered'
  return [score, [
    `Net debt / EBITDA: ${ratio.toFixed(2)}×  (${quality})`,
  ]]
}

// ── Signal 4: Dividend Growth Track ───────────────────────────────────────────

function scoreDividendGrowthTrack(series: AnnualDividendData[]): [number, string[]] {
  const divs = series.map(d => g(d, 'dividendsPaid')).filter(d => d > 0)
  if (divs.length < 2) {
    return [0.15, ['Dividend growth track: insufficient history (below-neutral score)']]
  }

  let consecutive = 0
  for (let i = 1; i < divs.length; i++) {
    if ((divs[i] ?? 0) >= (divs[i - 1] ?? 0)) {
      consecutive++
    } else {
      consecutive = 0  // reset on any cut
    }
  }

  let score: number
  if (consecutive >= 10)     score = 1.0
  else if (consecutive >= 7) score = 0.75
  else if (consecutive >= 4) score = 0.55
  else if (consecutive >= 2) score = 0.35
  else                       score = 0.15

  const label = consecutive >= 10 ? 'dividend aristocrat-level streak' : consecutive >= 7 ? 'strong track record' : consecutive >= 4 ? 'solid track record' : consecutive >= 2 ? 'limited track record' : 'recent cut or minimal history'
  return [score, [
    `Dividend growth track: ${consecutive} consecutive non-declining year(s)  (${label})`,
  ]]
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute Dividend Safety Score from a sequence of annual financial records.
 *
 * @param annualData - Array in chronological order (oldest first). Min 2 years recommended.
 * @returns DividendSafetyScore with score (0–100), rating, components, and evidence.
 *
 * @example
 *   const result = dividendSafetyScoreFromSeries([
 *     { year: 2020, dividendsPaid: 1.2e9, operatingCashFlow: 8e9, capex: 2e9,
 *       netIncome: 5e9, totalDebt: 10e9, cash: 3e9, ebit: 7e9, depreciation: 1e9 },
 *     { year: 2021, dividendsPaid: 1.3e9, operatingCashFlow: 9e9, capex: 2.2e9,
 *       netIncome: 5.5e9, totalDebt: 9e9, cash: 3.5e9, ebit: 7.8e9, depreciation: 1.1e9 },
 *   ])
 *   console.log(result.score)   // e.g. 74
 *   console.log(result.rating)  // 'safe'
 */
export function dividendSafetyScoreFromSeries(
  annualData: AnnualDividendData[],
): DividendSafetyScore {
  const payer = isDividendPayer(annualData)

  if (!payer) {
    return {
      score: 50,
      rating: 'non-payer',
      isDividendPayer: false,
      yearsAnalyzed: annualData.length,
      components: {
        fcfPayoutRatio:      0.5,
        earningsPayoutRatio: 0.5,
        balanceSheetStrength: 0.5,
        dividendGrowthTrack: 0.5,
      },
      evidence: ['No dividends detected across the provided data series'],
      interpretation: 'Score 50/100: Company does not pay a dividend — score is not meaningful',
    }
  }

  const [fcfScore, fcfEv] = scoreFcfPayout(annualData)
  const [epScore, epEv] = scoreEarningsPayout(annualData)
  const [bsScore, bsEv] = scoreBalanceSheet(annualData)
  const [dgtScore, dgtEv] = scoreDividendGrowthTrack(annualData)

  const raw = 0.35 * fcfScore + 0.25 * epScore + 0.25 * bsScore + 0.15 * dgtScore
  const score = Math.round(clamp(raw, 0, 1) * 100)

  const rating: DividendSafetyScore['rating'] =
    score >= 70 ? 'safe' :
    score >= 45 ? 'adequate' :
    score >= 20 ? 'risky' : 'danger'

  const desc: Record<Exclude<DividendSafetyScore['rating'], 'non-payer'>, string> = {
    safe:     'Dividend well-covered by cash flows with a strong balance sheet',
    adequate: 'Dividend appears sustainable but headroom is limited in some areas',
    risky:    'Coverage is strained — dividend could be at risk in a downturn',
    danger:   'Dividend likely unsustainable; cut probability is high',
  }

  return {
    score,
    rating,
    components: {
      fcfPayoutRatio:       Math.round(fcfScore  * 1e4) / 1e4,
      earningsPayoutRatio:  Math.round(epScore   * 1e4) / 1e4,
      balanceSheetStrength: Math.round(bsScore   * 1e4) / 1e4,
      dividendGrowthTrack:  Math.round(dgtScore  * 1e4) / 1e4,
    },
    isDividendPayer: true,
    yearsAnalyzed: annualData.length,
    evidence: [...fcfEv, ...epEv, ...bsEv, ...dgtEv],
    interpretation: `Score ${score}/100: ${desc[rating]}`,
  }
}
