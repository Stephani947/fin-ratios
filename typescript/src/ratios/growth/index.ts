import { safeDivide } from '../../utils/safe-divide.js'
import { cagr } from '../../utils/math.js'

function yoyGrowth(current: number, prior: number): number | null {
  if (prior === 0) return null
  return safeDivide(current - prior, Math.abs(prior))
}

export function revenueGrowth(input: {
  revenueCurrent: number
  revenuePrior: number
}): number | null {
  return yoyGrowth(input.revenueCurrent, input.revenuePrior)
}
revenueGrowth.formula = '(Revenue_t - Revenue_t-1) / |Revenue_t-1|'
revenueGrowth.description = 'Year-over-year revenue growth rate.'

export function revenueCAGR(input: {
  revenueStart: number
  revenueEnd: number
  years: number
}): number | null {
  return cagr(input.revenueStart, input.revenueEnd, input.years)
}
revenueCAGR.formula = '(Revenue_end / Revenue_start)^(1/years) - 1'
revenueCAGR.description = 'Compound annual growth rate of revenue over multiple years.'

export function epsGrowth(input: {
  epsCurrent: number
  epsPrior: number
}): number | null {
  return yoyGrowth(input.epsCurrent, input.epsPrior)
}
epsGrowth.formula = '(EPS_t - EPS_t-1) / |EPS_t-1|'
epsGrowth.description = 'Year-over-year earnings per share growth.'

export function ebitdaGrowth(input: {
  ebitdaCurrent: number
  ebitdaPrior: number
}): number | null {
  return yoyGrowth(input.ebitdaCurrent, input.ebitdaPrior)
}
ebitdaGrowth.formula = '(EBITDA_t - EBITDA_t-1) / |EBITDA_t-1|'
ebitdaGrowth.description = 'Year-over-year EBITDA growth.'

export function fcfGrowth(input: {
  fcfCurrent: number
  fcfPrior: number
}): number | null {
  return yoyGrowth(input.fcfCurrent, input.fcfPrior)
}
fcfGrowth.formula = '(FCF_t - FCF_t-1) / |FCF_t-1|'
fcfGrowth.description = 'Year-over-year free cash flow growth.'

export function bvpsGrowth(input: {
  bvpsCurrent: number
  bvpsPrior: number
}): number | null {
  return yoyGrowth(input.bvpsCurrent, input.bvpsPrior)
}
bvpsGrowth.formula = '(BVPS_t - BVPS_t-1) / |BVPS_t-1|'
bvpsGrowth.description = 'Book value per share growth — tracks compounding of equity.'

export function dividendGrowthRate(input: {
  dpsCurrent: number
  dpsPrior: number
}): number | null {
  return yoyGrowth(input.dpsCurrent, input.dpsPrior)
}
dividendGrowthRate.formula = '(DPS_t - DPS_t-1) / DPS_t-1'
dividendGrowthRate.description = 'Year-over-year dividend per share growth.'

export function earningsPowerValue(input: {
  ebit: number
  taxRate: number
  wacc: number
}): number | null {
  const nopatValue = input.ebit * (1 - input.taxRate)
  return safeDivide(nopatValue, input.wacc)
}
earningsPowerValue.formula = 'EBIT × (1 - Tax Rate) / WACC'
earningsPowerValue.description = 'EPV — intrinsic value assuming zero growth. Conservative floor for valuation.'
