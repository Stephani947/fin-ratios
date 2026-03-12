/**
 * Valuation Attractiveness Score.
 *
 * Provides a point-in-time assessment of how attractively a security is priced
 * relative to its earnings power, free cash flow generation, asset value, and
 * intrinsic value estimate. Higher scores indicate greater margin of safety.
 *
 * Signals
 * -------
 * 1. Earnings Yield Spread  (25%) — excess earnings yield over risk-free rate
 * 2. FCF Yield              (25%) — free cash flow yield on market price
 * 3. EV/EBITDA              (20%) — enterprise multiple vs historical norms
 * 4. P/B Ratio              (15%) — price-to-book premium or discount
 * 5. DCF Upside             (15%) — percentage gap to intrinsic value estimate
 *
 * Score:  0–100
 * Rating: 'attractive' (≥65), 'fair' (40–64), 'expensive' (20–39), 'overvalued' (<20)
 */

// ── Types ──────────────────────────────────────────────────────────────────────

export interface ValuationComponents {
  earningsYield: number   // 0–1
  fcfYield: number        // 0–1
  evEbitda: number        // 0–1
  pbRatio: number         // 0–1
  dcfUpside: number       // 0–1
}

export interface ValuationScore {
  score: number
  rating: 'attractive' | 'fair' | 'expensive' | 'overvalued'
  components: ValuationComponents
  riskFreeRate: number
  evidence: string[]
  interpretation: string
}

export interface ValuationParams {
  peRatio?: number
  evEbitda?: number
  pFcf?: number
  pbRatio?: number
  fcfYieldPct?: number
  earningsYieldPct?: number
  dcfUpsidePct?: number
  riskFreeRate?: number
}

// ── Internal helpers ───────────────────────────────────────────────────────────

function _clamp(x: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, x))
}

function _lerp(x: number, x0: number, x1: number, y0: number, y1: number): number {
  if (x1 === x0) return y0
  const t = (x - x0) / (x1 - x0)
  return y0 + _clamp(t, 0, 1) * (y1 - y0)
}

// ── Signal 1: Earnings Yield Spread ───────────────────────────────────────────

function scoreEarningsYield(params: ValuationParams, rf: number): [number, string[]] {
  let ey: number | null = null
  if (params.earningsYieldPct !== undefined) {
    ey = params.earningsYieldPct / 100
  } else if (params.peRatio !== undefined && params.peRatio > 0) {
    ey = 1 / params.peRatio
  }

  if (ey === null) {
    return [0.5, ['Earnings yield: no P/E or earnings yield data (neutral score)']]
  }

  const excess = ey - rf
  const score = _lerp(excess, -0.04, 0.04, 0.0, 1.0)
  const label = excess >= 0.02 ? 'attractive' : excess >= 0 ? 'slight premium' : 'below risk-free'
  return [score, [
    `Earnings yield: ${(ey * 100).toFixed(2)}%  vs  risk-free ${(rf * 100).toFixed(2)}%  (spread ${excess >= 0 ? '+' : ''}${(excess * 100).toFixed(2)}%)`,
    `Earnings yield spread: ${label}`,
  ]]
}

// ── Signal 2: FCF Yield ────────────────────────────────────────────────────────

function scoreFcfYield(params: ValuationParams): [number, string[]] {
  let fy: number | null = null
  if (params.fcfYieldPct !== undefined) {
    fy = params.fcfYieldPct / 100
  } else if (params.pFcf !== undefined && params.pFcf > 0) {
    fy = 1 / params.pFcf
  }

  if (fy === null) {
    return [0.5, ['FCF yield: no P/FCF or FCF yield data (neutral score)']]
  }

  let score: number
  if (fy < 0.02) {
    score = _lerp(fy, -0.02, 0.02, 0, 0.3)
  } else if (fy < 0.05) {
    score = _lerp(fy, 0.02, 0.05, 0.3, 0.7)
  } else {
    score = _lerp(fy, 0.05, 0.08, 0.7, 1.0)
  }

  const label = fy >= 0.06 ? 'excellent' : fy >= 0.04 ? 'good' : fy >= 0.02 ? 'modest' : 'thin'
  return [score, [
    `FCF yield: ${(fy * 100).toFixed(2)}%  (${label})`,
  ]]
}

// ── Signal 3: EV/EBITDA ───────────────────────────────────────────────────────

function scoreEvEbitda(params: ValuationParams): [number, string[]] {
  if (params.evEbitda === undefined) {
    return [0.5, ['EV/EBITDA: not provided (neutral score)']]
  }
  const ev = params.evEbitda
  if (ev <= 0) {
    return [0.2, ['EV/EBITDA: negative or zero (uninvestable or distressed)']]
  }

  let score: number
  if (ev < 12) {
    score = _lerp(ev, 5, 12, 1, 0.6)
  } else if (ev < 20) {
    score = _lerp(ev, 12, 20, 0.6, 0.2)
  } else {
    score = _lerp(ev, 20, 30, 0.2, 0.05)
  }

  const label = ev < 10 ? 'deep value' : ev < 14 ? 'reasonable' : ev < 20 ? 'full valued' : 'expensive'
  return [score, [
    `EV/EBITDA: ${ev.toFixed(1)}×  (${label})`,
  ]]
}

// ── Signal 4: P/B Ratio ───────────────────────────────────────────────────────

function scorePbRatio(params: ValuationParams): [number, string[]] {
  if (params.pbRatio === undefined) {
    return [0.5, ['P/B ratio: not provided (neutral score)']]
  }
  const pb = params.pbRatio
  if (pb <= 0) {
    return [0.15, ['P/B ratio: negative book value — balance sheet impaired']]
  }

  let score: number
  if (pb < 2) {
    score = _lerp(pb, 0.5, 2, 1, 0.65)
  } else if (pb < 4) {
    score = _lerp(pb, 2, 4, 0.65, 0.3)
  } else {
    score = _lerp(pb, 4, 8, 0.3, 0.05)
  }

  const label = pb < 1.5 ? 'near book value' : pb < 3 ? 'moderate premium' : pb < 5 ? 'high premium' : 'very high premium'
  return [score, [
    `P/B ratio: ${pb.toFixed(2)}×  (${label})`,
  ]]
}

// ── Signal 5: DCF Upside ──────────────────────────────────────────────────────

function scoreDcfUpside(params: ValuationParams): [number, string[]] {
  if (params.dcfUpsidePct === undefined) {
    return [0.5, ['DCF upside: not provided (neutral score)']]
  }
  const u = params.dcfUpsidePct / 100

  let score: number
  if (u < 0) {
    score = _lerp(u, -0.5, 0, 0, 0.3)
  } else if (u < 0.3) {
    score = _lerp(u, 0, 0.3, 0.3, 0.75)
  } else {
    score = _lerp(u, 0.3, 0.6, 0.75, 1.0)
  }

  const label = u >= 0.3 ? 'significant margin of safety' : u >= 0.1 ? 'modest upside' : u >= 0 ? 'fairly valued' : 'trading above intrinsic value'
  return [score, [
    `DCF upside: ${(u * 100).toFixed(1)}%  (${label})`,
  ]]
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute a point-in-time Valuation Attractiveness Score.
 *
 * @param params - Valuation multiples and optional risk-free rate override.
 *                 At least one input is required; missing signals default to 0.5.
 * @returns ValuationScore with score (0–100), rating, components, and evidence.
 *
 * @example
 *   const result = valuationAttractivenessScore({
 *     peRatio: 18,
 *     evEbitda: 11,
 *     pFcf: 22,
 *     pbRatio: 3.2,
 *     dcfUpsidePct: 25,
 *   })
 *   console.log(result.score)   // e.g. 62
 *   console.log(result.rating)  // 'fair'
 */
export function valuationAttractivenessScore(params: ValuationParams): ValuationScore {
  const rf = params.riskFreeRate ?? 0.045

  const [eyScore, eyEv] = scoreEarningsYield(params, rf)
  const [fyScore, fyEv] = scoreFcfYield(params)
  const [evScore, evEv] = scoreEvEbitda(params)
  const [pbScore, pbEv] = scorePbRatio(params)
  const [dcfScore, dcfEv] = scoreDcfUpside(params)

  const raw = 0.25 * eyScore + 0.25 * fyScore + 0.20 * evScore + 0.15 * pbScore + 0.15 * dcfScore
  const score = Math.round(_clamp(raw, 0, 1) * 100)

  const rating: ValuationScore['rating'] =
    score >= 65 ? 'attractive' :
    score >= 40 ? 'fair' :
    score >= 20 ? 'expensive' : 'overvalued'

  const desc: Record<ValuationScore['rating'], string> = {
    attractive: 'Multiple signals indicate price is below intrinsic value — margin of safety present',
    fair:       'Price appears broadly in line with fundamental value',
    expensive:  'Price embeds optimistic assumptions — limited margin of safety',
    overvalued: 'Price materially exceeds indicated intrinsic value across multiple metrics',
  }

  return {
    score,
    rating,
    components: {
      earningsYield: Math.round(eyScore  * 1e4) / 1e4,
      fcfYield:      Math.round(fyScore  * 1e4) / 1e4,
      evEbitda:      Math.round(evScore  * 1e4) / 1e4,
      pbRatio:       Math.round(pbScore  * 1e4) / 1e4,
      dcfUpside:     Math.round(dcfScore * 1e4) / 1e4,
    },
    riskFreeRate: rf,
    evidence: [...eyEv, ...fyEv, ...evEv, ...pbEv, ...dcfEv],
    interpretation: `Score ${score}/100: ${desc[rating]}`,
  }
}
