/**
 * Quality Factor Score.
 *
 * Synthesises three complementary quality dimensions into a single score:
 *   1. Earnings Quality    (35%) — reliability of reported earnings
 *   2. Economic Moat       (35%) — durability of competitive advantage
 *   3. Capital Allocation  (30%) — effectiveness of management's capital use
 *
 * Score:  0–100
 * Grade:  'exceptional' (80–100), 'strong' (60–79), 'moderate' (40–59),
 *         'weak' (20–39), 'poor' (0–19)
 *
 * References
 * ----------
 * Asness, Frazzini & Pedersen (2019) — Quality Minus Junk. Review of Accounting Studies.
 */

import { earningsQualityScore, type EarningsQualityResult } from './earnings-quality.js'
import { moatScore, type MoatScoreResult } from './moat-score.js'
import { capitalAllocationScore, type CapitalAllocationResult } from './capital-allocation.js'
import type { AnnualFinancialData } from './moat-score.js'

// ── Types ──────────────────────────────────────────────────────────────────────

export interface QualityComponents {
  earningsQuality: number    // 0–1
  moat: number               // 0–1
  capitalAllocation: number  // 0–1
}

export interface QualityFactorResult {
  score: number                                                          // 0–100
  grade: 'exceptional' | 'strong' | 'moderate' | 'weak' | 'poor'
  components: QualityComponents
  subScores: {
    earningsQuality: EarningsQualityResult
    moat: MoatScoreResult
    capitalAllocation: CapitalAllocationResult
  }
  yearsAnalyzed: number
  evidence: string[]
}

/** Input type that satisfies all three sub-score calculators. */
export type AnnualQualityData = AnnualFinancialData & {
  netIncome?: number
  operatingCashFlow?: number
  accountsReceivable?: number
}

export interface QualityScoreOptions {
  wacc?: number
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute Quality Factor Score from a sequence of annual financial records.
 *
 * @param annualData - Array in chronological order (oldest first). Min 2 years.
 * @param options    - Optional: `{ wacc }` to override WACC estimation.
 * @returns QualityFactorResult with score (0–100), grade, sub-scores, evidence.
 */
export function qualityScore(
  annualData: AnnualQualityData[],
  options: QualityScoreOptions = {},
): QualityFactorResult {
  if (annualData.length < 2) {
    throw new Error('qualityScore requires at least 2 years of data.')
  }

  const eq = earningsQualityScore(annualData as any)
  const ms = moatScore(annualData, options)
  const ca = capitalAllocationScore(annualData as any, options)

  const eqNorm = eq.score / 100
  const msNorm = ms.score / 100
  const caNorm = ca.score / 100

  const raw = 0.35 * eqNorm + 0.35 * msNorm + 0.30 * caNorm
  const score = Math.round(raw * 100)

  const grade: QualityFactorResult['grade'] =
    score >= 80 ? 'exceptional' :
    score >= 60 ? 'strong' :
    score >= 40 ? 'moderate' :
    score >= 20 ? 'weak' : 'poor'

  return {
    score,
    grade,
    components: {
      earningsQuality:   Math.round(eqNorm * 1e4) / 1e4,
      moat:              Math.round(msNorm * 1e4) / 1e4,
      capitalAllocation: Math.round(caNorm * 1e4) / 1e4,
    },
    subScores: { earningsQuality: eq, moat: ms, capitalAllocation: ca },
    yearsAnalyzed: annualData.length,
    evidence: [
      `Earnings Quality:   ${eq.score}/100 [${eq.rating.toUpperCase()}]`,
      `Economic Moat:      ${ms.score}/100 [${ms.width.toUpperCase()}]`,
      `Capital Allocation: ${ca.score}/100 [${ca.rating.toUpperCase()}]`,
    ],
  }
}
