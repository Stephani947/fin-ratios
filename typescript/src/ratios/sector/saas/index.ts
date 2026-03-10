import { safeDivide } from '../../../utils/safe-divide.js'

export function ruleOf40(input: {
  revenueGrowthRatePct: number
  fcfMarginPct: number
}): number {
  return input.revenueGrowthRatePct + input.fcfMarginPct
}
ruleOf40.formula = 'Revenue Growth Rate (%) + FCF Margin (%)'
ruleOf40.description = 'SaaS health metric. > 40 = healthy balance of growth and profitability.'

export function magicNumber(input: {
  currentQuarterRevenue: number
  priorQuarterRevenue: number
  priorQuarterSalesAndMarketingSpend: number
}): number | null {
  const netNewArrAnnualized = (input.currentQuarterRevenue - input.priorQuarterRevenue) * 4
  return safeDivide(netNewArrAnnualized, input.priorQuarterSalesAndMarketingSpend)
}
magicNumber.formula = '(Current Quarter Revenue - Prior Quarter Revenue) × 4 / Prior Quarter S&M'
magicNumber.description = 'SaaS go-to-market efficiency. > 0.75 is good, > 1.0 is exceptional.'

export function netRevenueRetention(input: {
  beginningArr: number
  expansion: number
  churn: number
  contraction: number
}): number | null {
  return safeDivide(
    input.beginningArr + input.expansion - input.churn - input.contraction,
    input.beginningArr
  )
}
netRevenueRetention.formula = '(Beginning ARR + Expansion - Churn - Contraction) / Beginning ARR'
netRevenueRetention.description = 'NRR > 100% means existing customers generate more revenue over time (net expansion).'

export function grossRevenueRetention(input: {
  beginningArr: number
  churn: number
  contraction: number
}): number | null {
  return safeDivide(
    input.beginningArr - input.churn - input.contraction,
    input.beginningArr
  )
}
grossRevenueRetention.formula = '(Beginning ARR - Churn - Contraction) / Beginning ARR'
grossRevenueRetention.description = 'GRR measures pure retention without expansion. Best case = 100%.'

export function customerAcquisitionCost(input: {
  salesAndMarketingSpend: number
  newCustomersAcquired: number
}): number | null {
  return safeDivide(input.salesAndMarketingSpend, input.newCustomersAcquired)
}
customerAcquisitionCost.formula = 'Sales & Marketing Spend / New Customers Acquired'
customerAcquisitionCost.description = 'Cost to acquire one new customer.'

export function customerLifetimeValue(input: {
  avgMonthlyRevenuePerCustomer: number
  grossMargin: number
  monthlyChurnRate: number
}): number | null {
  if (input.monthlyChurnRate <= 0) return null
  return safeDivide(
    input.avgMonthlyRevenuePerCustomer * input.grossMargin,
    input.monthlyChurnRate
  )
}
customerLifetimeValue.formula = '(Avg Monthly Revenue × Gross Margin) / Monthly Churn Rate'
customerLifetimeValue.description = 'Expected revenue from a customer over their lifetime.'

export function ltvCacRatio(input: {
  ltv: number
  cac: number
}): number | null {
  return safeDivide(input.ltv, input.cac)
}
ltvCacRatio.formula = 'LTV / CAC'
ltvCacRatio.description = 'LTV:CAC > 3 is healthy. < 1 means you lose money on every customer.'

export function cacPaybackPeriod(input: {
  cac: number
  avgMonthlyRevenuePerCustomer: number
  grossMarginPct: number
}): number | null {
  const monthlyMargin = input.avgMonthlyRevenuePerCustomer * input.grossMarginPct
  return safeDivide(input.cac, monthlyMargin)
}
cacPaybackPeriod.formula = 'CAC / (Avg Monthly Revenue × Gross Margin %)'
cacPaybackPeriod.description = 'Months to recoup customer acquisition cost. < 12 months is excellent.'

export function burnMultiple(input: {
  netBurnRate: number
  netNewArr: number
}): number | null {
  return safeDivide(input.netBurnRate, input.netNewArr)
}
burnMultiple.formula = 'Net Burn Rate / Net New ARR'
burnMultiple.description = 'Cash spent to acquire $1 of new ARR. < 1 is excellent, > 2 is concerning.'

export function saasQuickRatio(input: {
  newMrr: number
  expansionMrr: number
  churnedMrr: number
  contractionMrr: number
}): number | null {
  const gained = input.newMrr + input.expansionMrr
  const lost = input.churnedMrr + input.contractionMrr
  return safeDivide(gained, lost)
}
saasQuickRatio.formula = '(New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)'
saasQuickRatio.description = 'Growth efficiency. > 4 is excellent, < 1 means shrinking.'

export function arrPerFte(input: {
  arr: number
  fullTimeEmployees: number
}): number | null {
  return safeDivide(input.arr, input.fullTimeEmployees)
}
arrPerFte.formula = 'ARR / Full-Time Employees'
arrPerFte.description = 'Productivity benchmark. > $200k/FTE is world-class.'
