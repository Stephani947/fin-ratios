import { safeDivide } from '../../utils/safe-divide.js'

export function assetTurnover(input: {
  revenue: number
  avgTotalAssets: number
}): number | null {
  return safeDivide(input.revenue, input.avgTotalAssets)
}
assetTurnover.formula = 'Revenue / Average Total Assets'
assetTurnover.description = 'Sales generated per dollar of total assets.'

export function fixedAssetTurnover(input: {
  revenue: number
  avgNetPPE: number
}): number | null {
  return safeDivide(input.revenue, input.avgNetPPE)
}
fixedAssetTurnover.formula = 'Revenue / Average Net PP&E'
fixedAssetTurnover.description = 'Efficiency of physical asset use. Low in capital-intensive industries.'

export function inventoryTurnover(input: {
  cogs: number
  avgInventory: number
}): number | null {
  return safeDivide(input.cogs, input.avgInventory)
}
inventoryTurnover.formula = 'COGS / Average Inventory'
inventoryTurnover.description = 'How many times inventory is sold per year. Higher = less cash tied up.'

export function receivablesTurnover(input: {
  revenue: number
  avgAccountsReceivable: number
}): number | null {
  return safeDivide(input.revenue, input.avgAccountsReceivable)
}
receivablesTurnover.formula = 'Revenue / Average Accounts Receivable'
receivablesTurnover.description = 'How quickly the company collects what it is owed.'

export function payablesTurnover(input: {
  cogs: number
  avgAccountsPayable: number
}): number | null {
  return safeDivide(input.cogs, input.avgAccountsPayable)
}
payablesTurnover.formula = 'COGS / Average Accounts Payable'
payablesTurnover.description = 'How quickly the company pays its suppliers.'

export function workingCapitalTurnover(input: {
  revenue: number
  avgWorkingCapital: number
}): number | null {
  return safeDivide(input.revenue, input.avgWorkingCapital)
}
workingCapitalTurnover.formula = 'Revenue / Average Working Capital'
workingCapitalTurnover.description = 'Revenue generated from each dollar of working capital.'

export function capitalTurnover(input: {
  revenue: number
  investedCapital: number
}): number | null {
  return safeDivide(input.revenue, input.investedCapital)
}
capitalTurnover.formula = 'Revenue / Invested Capital'
capitalTurnover.description = 'Sales generated per dollar of invested capital.'

export function operatingLeverage(input: {
  ebitCurrent: number
  ebitPrior: number
  revenueCurrent: number
  revenuePrior: number
}): number | null {
  const ebitChange = safeDivide(
    input.ebitCurrent - input.ebitPrior,
    Math.abs(input.ebitPrior)
  )
  const revenueChange = safeDivide(
    input.revenueCurrent - input.revenuePrior,
    Math.abs(input.revenuePrior)
  )
  return safeDivide(ebitChange, revenueChange)
}
operatingLeverage.formula = '% Change in EBIT / % Change in Revenue'
operatingLeverage.description = 'Sensitivity of operating income to revenue changes. High = more fixed costs.'
