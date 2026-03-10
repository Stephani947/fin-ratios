import { safeDivide } from '../../utils/safe-divide.js'

export function freeCashFlow(input: {
  operatingCashFlow: number
  capex: number
}): number {
  return input.operatingCashFlow - Math.abs(input.capex)
}
freeCashFlow.formula = 'Operating Cash Flow - Capital Expenditures'
freeCashFlow.description = 'Cash available after maintaining/growing asset base. The most important cash flow metric.'

export function leveredFcf(input: {
  freeCashFlow: number
  debtIssuance: number
  debtRepayments: number
}): number {
  return input.freeCashFlow + input.debtIssuance - input.debtRepayments
}
leveredFcf.formula = 'FCF + Net Debt Change (Issuance - Repayments)'
leveredFcf.description = 'FCF after accounting for debt financing activities.'

export function unleveredFcf(input: {
  nopat: number
  depreciationAndAmortization: number
  capex: number
  changeInWorkingCapital: number
}): number {
  return input.nopat + input.depreciationAndAmortization - Math.abs(input.capex) - input.changeInWorkingCapital
}
unleveredFcf.formula = 'NOPAT + D&A - Capex - Change in Working Capital'
unleveredFcf.description = 'FCF before debt payments — used in DCF valuation as FCFF.'

export function ownerEarnings(input: {
  netIncome: number
  depreciationAndAmortization: number
  maintenanceCapex: number
  changeInWorkingCapital?: number
}): number {
  return (
    input.netIncome +
    input.depreciationAndAmortization -
    input.maintenanceCapex -
    (input.changeInWorkingCapital ?? 0)
  )
}
ownerEarnings.formula = 'Net Income + D&A - Maintenance Capex - Change in WC'
ownerEarnings.description = 'Buffett\'s owner earnings — true economic earnings available to shareholders.'

export function fcfYield(input: {
  freeCashFlow: number
  marketCap: number
}): number | null {
  return safeDivide(input.freeCashFlow, input.marketCap)
}
fcfYield.formula = 'Free Cash Flow / Market Capitalization'
fcfYield.description = 'FCF per dollar invested. Inverse of P/FCF. Higher = cheaper.'

export function fcfMargin(input: {
  freeCashFlow: number
  revenue: number
}): number | null {
  return safeDivide(input.freeCashFlow, input.revenue)
}
fcfMargin.formula = 'Free Cash Flow / Revenue'
fcfMargin.description = 'FCF generated per dollar of revenue.'

export function fcfConversion(input: {
  freeCashFlow: number
  netIncome: number
}): number | null {
  return safeDivide(input.freeCashFlow, input.netIncome)
}
fcfConversion.formula = 'Free Cash Flow / Net Income'
fcfConversion.description = 'FCF conversion > 1 means earnings are backed by real cash. < 1 raises quality concerns.'

export function ocfToSales(input: {
  operatingCashFlow: number
  revenue: number
}): number | null {
  return safeDivide(input.operatingCashFlow, input.revenue)
}
ocfToSales.formula = 'Operating Cash Flow / Revenue'
ocfToSales.description = 'Cash generated from operations per dollar of sales.'

export function capexToRevenue(input: {
  capex: number
  revenue: number
}): number | null {
  return safeDivide(Math.abs(input.capex), input.revenue)
}
capexToRevenue.formula = 'Capital Expenditures / Revenue'
capexToRevenue.description = 'Investment intensity. High in capital-intensive industries like manufacturing.'

export function capexToDepreciation(input: {
  capex: number
  depreciation: number
}): number | null {
  return safeDivide(Math.abs(input.capex), input.depreciation)
}
capexToDepreciation.formula = 'Capital Expenditures / Depreciation'
capexToDepreciation.description = '> 1 = company is investing more than assets are aging (growth). < 1 = under-investing.'

export function cashReturnOnAssets(input: {
  operatingCashFlow: number
  totalAssets: number
}): number | null {
  return safeDivide(input.operatingCashFlow, input.totalAssets)
}
cashReturnOnAssets.formula = 'Operating Cash Flow / Total Assets'
cashReturnOnAssets.description = 'Cash-based ROA. Harder to manipulate than accrual-based ROA.'
