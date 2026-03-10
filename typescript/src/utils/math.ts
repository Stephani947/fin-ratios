/**
 * Compound Annual Growth Rate.
 * @param start - starting value
 * @param end - ending value
 * @param years - number of years
 */
export function cagr(
  start: number | null | undefined,
  end: number | null | undefined,
  years: number
): number | null {
  if (start == null || end == null || years <= 0) return null
  if (start <= 0) return null
  return Math.pow(end / start, 1 / years) - 1
}

/**
 * Annualizes a sub-annual return.
 * @param returnValue - periodic return (decimal)
 * @param periodsPerYear - e.g. 252 for daily, 12 for monthly, 4 for quarterly
 */
export function annualizeReturn(returnValue: number, periodsPerYear: number): number {
  return Math.pow(1 + returnValue, periodsPerYear) - 1
}

/**
 * Standard deviation of an array of numbers.
 * @param values - array of returns or values
 * @param ddof - degrees of freedom (0 = population, 1 = sample). Default: 1
 */
export function stdDev(values: number[], ddof = 1): number | null {
  if (values.length < 2) return null
  const mean = values.reduce((a, b) => a + b, 0) / values.length
  const variance =
    values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / (values.length - ddof)
  return Math.sqrt(variance)
}

/**
 * Arithmetic mean of an array.
 */
export function mean(values: number[]): number | null {
  if (values.length === 0) return null
  return values.reduce((a, b) => a + b, 0) / values.length
}

/**
 * Percentile of a sorted or unsorted array.
 * @param values - array of numbers
 * @param percentile - 0–1 (e.g. 0.05 for 5th percentile)
 */
export function percentile(values: number[], p: number): number | null {
  if (values.length === 0) return null
  const sorted = [...values].sort((a, b) => a - b)
  const idx = p * (sorted.length - 1)
  const lower = Math.floor(idx)
  const upper = Math.ceil(idx)
  if (lower === upper) return sorted[lower] ?? null
  const lv = sorted[lower]
  const uv = sorted[upper]
  if (lv == null || uv == null) return null
  return lv + (uv - lv) * (idx - lower)
}

/**
 * Maximum drawdown from a series of prices or cumulative returns.
 * Returns a positive decimal, e.g. 0.3 for a 30% drawdown.
 */
export function maxDrawdown(prices: number[]): number | null {
  if (prices.length < 2) return null
  let peak = prices[0] ?? 0
  let maxDD = 0
  for (const price of prices) {
    if (price > peak) peak = price
    const dd = peak > 0 ? (peak - price) / peak : 0
    if (dd > maxDD) maxDD = dd
  }
  return maxDD
}

/**
 * Convert an array of prices to period returns.
 */
export function pricesToReturns(prices: number[]): number[] {
  const returns: number[] = []
  for (let i = 1; i < prices.length; i++) {
    const prev = prices[i - 1]
    const curr = prices[i]
    if (prev != null && curr != null && prev !== 0) {
      returns.push((curr - prev) / prev)
    }
  }
  return returns
}
