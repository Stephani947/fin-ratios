/**
 * Portfolio Quality Analysis.
 *
 * Aggregates quality scores across a portfolio of holdings weighted by
 * position size. Provides a composite view of portfolio quality tilt.
 *
 * Usage (bring your own data):
 *   const result = portfolioQuality([
 *     { ticker: 'AAPL', weight: 0.30, annualData: [...] },
 *     { ticker: 'MSFT', weight: 0.70, annualData: [...] },
 *   ])
 */

import { qualityScore, type QualityFactorResult, type AnnualQualityData } from './quality-score.js'

// ── Types ──────────────────────────────────────────────────────────────────────

export interface HoldingInput {
  ticker: string
  weight: number
  annualData: AnnualQualityData[]
}

export interface HoldingResult {
  ticker: string
  weight: number             // normalised weight
  quality: QualityFactorResult | null
  error?: string
}

export interface PortfolioQualityResult {
  holdings: HoldingResult[]
  weightedQualityScore: number        // 0–100
  weightedMoatScore: number           // 0–100
  weightedEarningsQuality: number     // 0–100
  weightedCapitalAllocation: number   // 0–100
  effectiveWeight: number             // fraction of portfolio successfully analysed
  grade: 'exceptional' | 'strong' | 'moderate' | 'weak' | 'poor'
  errors: string[]
}

export interface PortfolioOptions {
  wacc?: number
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute portfolio-level quality scores from pre-loaded holding data.
 *
 * Weights are normalised automatically — they need not sum to 1.
 * Holdings whose data fails to compute are excluded from weighted averages
 * and reported in `errors`.
 *
 * @param holdings - Array of { ticker, weight, annualData } objects.
 * @param options  - Optional: `{ wacc }` override applied to all holdings.
 */
export function portfolioQuality(
  holdings: HoldingInput[],
  options: PortfolioOptions = {},
): PortfolioQualityResult {
  if (!holdings.length) throw new Error('holdings must be a non-empty array.')

  const totalWeight = holdings.reduce((s, h) => s + h.weight, 0)
  if (totalWeight <= 0) throw new Error('Sum of holding weights must be positive.')

  const results: HoldingResult[] = holdings.map(h => {
    const normWeight = h.weight / totalWeight
    try {
      const q = qualityScore(h.annualData, options)
      return { ticker: h.ticker, weight: normWeight, quality: q }
    } catch (err) {
      return {
        ticker: h.ticker,
        weight: normWeight,
        quality: null,
        error: err instanceof Error ? err.message : String(err),
      }
    }
  })

  const successful = results.filter((r): r is HoldingResult & { quality: QualityFactorResult } =>
    r.quality !== null
  )

  if (!successful.length) {
    throw new Error('All holdings failed to compute. Check data and minimum year requirements.')
  }

  const effWeight = successful.reduce((s, h) => s + h.weight, 0)
  const renorm = effWeight > 0 ? 1 / effWeight : 1

  const wavg = (fn: (q: QualityFactorResult) => number): number =>
    Math.round(successful.reduce((s, h) => s + h.weight * fn(h.quality) * renorm, 0) * 10) / 10

  const wq  = wavg(q => q.score)
  const wm  = wavg(q => q.subScores.moat.score)
  const weq = wavg(q => q.subScores.earningsQuality.score)
  const wca = wavg(q => q.subScores.capitalAllocation.score)

  const grade: PortfolioQualityResult['grade'] =
    wq >= 80 ? 'exceptional' :
    wq >= 60 ? 'strong' :
    wq >= 40 ? 'moderate' :
    wq >= 20 ? 'weak' : 'poor'

  return {
    holdings: results,
    weightedQualityScore:      wq,
    weightedMoatScore:         wm,
    weightedEarningsQuality:   weq,
    weightedCapitalAllocation: wca,
    effectiveWeight:           Math.round(effWeight * 1e4) / 1e4,
    grade,
    errors: results.filter(r => r.error).map(r => `${r.ticker}: ${r.error}`),
  }
}
