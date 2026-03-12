/**
 * Investment Score — Grand Synthesis.
 *
 * Combines five complementary dimensions into a single conviction-weighted
 * investment score. The score is designed to surface the highest-quality,
 * best-priced businesses — the intersection of durable moat, disciplined
 * capital allocation, reliable earnings, strong management, and attractive
 * valuation.
 *
 * Weights (all five present):
 *   Moat                25% — durability of competitive advantage
 *   Capital Allocation  20% — effectiveness of management's capital use
 *   Earnings Quality    20% — reliability and sustainability of reported earnings
 *   Management          15% — operational execution and shareholder orientation
 *   Valuation           20% — price attractiveness vs intrinsic value
 *
 * If valuation is omitted, its 20% weight is redistributed proportionally
 * across the remaining four factors.
 *
 * Score:  0–100
 * Grade:  'A+' (≥90), 'A' (80–89), 'B+' (70–79), 'B' (60–69),
 *         'C' (45–59), 'D' (25–44), 'F' (<25)
 * Conviction: 'strongBuy' | 'buy' | 'hold' | 'sell' | 'strongSell'
 */

import { moatScore } from './moat-score.js'
import { capitalAllocationScore } from './capital-allocation.js'
import { earningsQualityScore } from './earnings-quality.js'
import { managementQualityScoreFromSeries } from './management-score.js'
import { valuationAttractivenessScore } from './valuation-score.js'
import type { AnnualQualityData } from './quality-score.js'
import type { ValuationParams } from './valuation-score.js'

// Re-export these types so callers can import them from a single location
export type { AnnualQualityData } from './quality-score.js'
export type { ValuationParams } from './valuation-score.js'

// ── Types ──────────────────────────────────────────────────────────────────────

export interface InvestmentComponents {
  moat: number | null
  capitalAllocation: number | null
  earningsQuality: number | null
  management: number | null
  valuation: number | null
}

export interface InvestmentScore {
  score: number
  grade: 'A+' | 'A' | 'B+' | 'B' | 'C' | 'D' | 'F'
  conviction: 'strongBuy' | 'buy' | 'hold' | 'sell' | 'strongSell'
  components: InvestmentComponents
  evidence: string[]
  interpretation: string
}

export interface InvestmentScoreInputs {
  moatScore: number
  capitalAllocationScore: number
  earningsQualityScore: number
  managementScore: number
  valuationScore?: number
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x))
}

function gradeFromScore(score: number): InvestmentScore['grade'] {
  if (score >= 90) return 'A+'
  if (score >= 80) return 'A'
  if (score >= 70) return 'B+'
  if (score >= 60) return 'B'
  if (score >= 45) return 'C'
  if (score >= 25) return 'D'
  return 'F'
}

function convictionFromScore(score: number): InvestmentScore['conviction'] {
  if (score >= 80) return 'strongBuy'
  if (score >= 65) return 'buy'
  if (score >= 45) return 'hold'
  if (score >= 30) return 'sell'
  return 'strongSell'
}

// ── Weighted combination ───────────────────────────────────────────────────────

function computeWeightedScore(inputs: InvestmentScoreInputs): number {
  const hasValuation = inputs.valuationScore !== undefined

  if (hasValuation) {
    // Full weights: Moat 25%, CA 20%, EQ 20%, Mgmt 15%, Val 20%
    return (
      0.25 * inputs.moatScore +
      0.20 * inputs.capitalAllocationScore +
      0.20 * inputs.earningsQualityScore +
      0.15 * inputs.managementScore +
      0.20 * inputs.valuationScore!
    )
  }

  // Redistribute valuation's 20% proportionally among the other four.
  // Base weights without valuation: 25, 20, 20, 15 → sum = 80
  // Scale each up by 100/80 = 1.25
  return (
    0.3125 * inputs.moatScore +
    0.2500 * inputs.capitalAllocationScore +
    0.2500 * inputs.earningsQualityScore +
    0.1875 * inputs.managementScore
  )
}

// ── investmentScoreFromScores ─────────────────────────────────────────────────

/**
 * Combine pre-computed sub-scores into an Investment Score.
 *
 * @param inputs - Individual sub-scores (0–100 each). `valuationScore` is optional.
 * @returns InvestmentScore with grade, conviction, components, and evidence.
 *
 * @example
 *   const result = investmentScoreFromScores({
 *     moatScore:             78,
 *     capitalAllocationScore: 65,
 *     earningsQualityScore:  71,
 *     managementScore:       80,
 *     valuationScore:        62,
 *   })
 *   console.log(result.grade)      // 'B+'
 *   console.log(result.conviction) // 'buy'
 */
export function investmentScoreFromScores(inputs: InvestmentScoreInputs): InvestmentScore {
  const rawScore = computeWeightedScore(inputs)
  const score = Math.round(clamp(rawScore, 0, 100))
  const grade = gradeFromScore(score)
  const conviction = convictionFromScore(score)

  const hasVal = inputs.valuationScore !== undefined

  const evidence: string[] = [
    `Economic Moat:         ${inputs.moatScore}/100  (weight ${hasVal ? '25' : '31'}%)`,
    `Capital Allocation:    ${inputs.capitalAllocationScore}/100  (weight ${hasVal ? '20' : '25'}%)`,
    `Earnings Quality:      ${inputs.earningsQualityScore}/100  (weight ${hasVal ? '20' : '25'}%)`,
    `Management Quality:    ${inputs.managementScore}/100  (weight ${hasVal ? '15' : '19'}%)`,
  ]
  if (hasVal) {
    evidence.push(`Valuation:             ${inputs.valuationScore}/100  (weight 20%)`)
  } else {
    evidence.push('Valuation:             not provided (weight redistributed)')
  }

  const convictionLabel: Record<InvestmentScore['conviction'], string> = {
    strongBuy:  'Strong Buy — exceptional quality at an attractive price',
    buy:        'Buy — above-average quality with reasonable valuation',
    hold:       'Hold — average quality or price adequately reflects value',
    sell:       'Sell — below-average quality or price significantly exceeds value',
    strongSell: 'Strong Sell — poor quality and/or materially overpriced',
  }

  return {
    score,
    grade,
    conviction,
    components: {
      moat:              inputs.moatScore,
      capitalAllocation: inputs.capitalAllocationScore,
      earningsQuality:   inputs.earningsQualityScore,
      management:        inputs.managementScore,
      valuation:         inputs.valuationScore ?? null,
    },
    evidence,
    interpretation: `Grade ${grade}  |  Score ${score}/100  |  ${convictionLabel[conviction]}`,
  }
}

// ── investmentScoreFromSeries ─────────────────────────────────────────────────

/**
 * Compute all sub-scores from annual financial data, then combine into an
 * Investment Score. The management sub-score requires at least 3 years;
 * all other sub-scores require at least 2 years.
 *
 * @param annualData      - Array in chronological order (oldest first). Min 3 years.
 * @param valuationParams - Optional point-in-time valuation multiples.
 * @param wacc            - Optional WACC override applied to moat and capital allocation.
 * @returns InvestmentScore with grade, conviction, components, and evidence.
 *
 * @example
 *   const result = investmentScoreFromSeries(
 *     [
 *       { year: 2020, revenue: 100e9, grossProfit: 60e9, ebit: 25e9,
 *         netIncome: 20e9, operatingCashFlow: 24e9, totalAssets: 80e9,
 *         totalEquity: 40e9, totalDebt: 12e9, cash: 6e9,
 *         capex: 3e9, depreciation: 4e9, sharesOutstanding: 5e9 },
 *       // ... more years
 *     ],
 *     { peRatio: 18, evEbitda: 11, pbRatio: 3.1, dcfUpsidePct: 22 },
 *   )
 *   console.log(result.grade)      // e.g. 'B+'
 *   console.log(result.conviction) // 'buy'
 */
export function investmentScoreFromSeries(
  annualData: AnnualQualityData[],
  valuationParams?: ValuationParams,
  wacc?: number,
): InvestmentScore {
  if (annualData.length < 3) {
    throw new Error('investmentScoreFromSeries requires at least 3 years of data.')
  }

  const waccOpt = wacc !== undefined ? { wacc } : {}

  const moatResult = moatScore(annualData as any, waccOpt)
  const caResult   = capitalAllocationScore(annualData as any, waccOpt)
  const eqResult   = earningsQualityScore(annualData as any)
  const mgmtResult = managementQualityScoreFromSeries(annualData as any, wacc)

  const inputs: InvestmentScoreInputs = {
    moatScore:             moatResult.score,
    capitalAllocationScore: caResult.score,
    earningsQualityScore:  eqResult.score,
    managementScore:       mgmtResult.score,
  }

  if (valuationParams !== undefined) {
    const valResult = valuationAttractivenessScore(valuationParams)
    inputs.valuationScore = valResult.score
  }

  return investmentScoreFromScores(inputs)
}
