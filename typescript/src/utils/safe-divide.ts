/**
 * Divides numerator by denominator.
 * Returns null instead of Infinity/NaN when denominator is 0 or either input is null/undefined.
 */
export function safeDivide(
  numerator: number | null | undefined,
  denominator: number | null | undefined
): number | null {
  if (numerator == null || denominator == null) return null
  if (denominator === 0) return null
  return numerator / denominator
}
