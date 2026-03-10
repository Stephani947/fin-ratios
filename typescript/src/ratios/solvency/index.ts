import { safeDivide } from '../../utils/safe-divide.js'

export function debtToEquity(input: {
  totalDebt: number
  totalEquity: number
}): number | null {
  return safeDivide(input.totalDebt, input.totalEquity)
}
debtToEquity.formula = 'Total Debt / Total Equity'
debtToEquity.description = 'Financial leverage. Higher = more debt-financed.'

export function netDebtToEquity(input: {
  totalDebt: number
  cash: number
  totalEquity: number
}): number | null {
  const netDebt = input.totalDebt - input.cash
  return safeDivide(netDebt, input.totalEquity)
}
netDebtToEquity.formula = '(Total Debt - Cash) / Total Equity'
netDebtToEquity.description = 'Net leverage ratio. Negative = net cash position.'

export function netDebtToEbitda(input: {
  totalDebt: number
  cash: number
  ebitda: number
}): number | null {
  const netDebt = input.totalDebt - input.cash
  return safeDivide(netDebt, input.ebitda)
}
netDebtToEbitda.formula = '(Total Debt - Cash) / EBITDA'
netDebtToEbitda.description = 'Years to repay net debt from EBITDA. Lenders often require < 3x.'

export function debtToAssets(input: {
  totalDebt: number
  totalAssets: number
}): number | null {
  return safeDivide(input.totalDebt, input.totalAssets)
}
debtToAssets.formula = 'Total Debt / Total Assets'
debtToAssets.description = 'Proportion of assets financed by debt.'

export function debtToCapital(input: {
  totalDebt: number
  totalEquity: number
}): number | null {
  return safeDivide(input.totalDebt, input.totalDebt + input.totalEquity)
}
debtToCapital.formula = 'Total Debt / (Total Debt + Total Equity)'
debtToCapital.description = 'Proportion of capital structure that is debt.'

export function interestCoverageRatio(input: {
  ebit: number
  interestExpense: number
}): number | null {
  return safeDivide(input.ebit, input.interestExpense)
}
interestCoverageRatio.formula = 'EBIT / Interest Expense'
interestCoverageRatio.description = 'Times interest is covered by operating earnings. < 1.5 is risky.'

export function ebitdaCoverageRatio(input: {
  ebitda: number
  interestExpense: number
}): number | null {
  return safeDivide(input.ebitda, input.interestExpense)
}
ebitdaCoverageRatio.formula = 'EBITDA / Interest Expense'
ebitdaCoverageRatio.description = 'Softer coverage ratio including D&A add-back.'

export function debtServiceCoverageRatio(input: {
  netOperatingIncome: number
  annualDebtService: number
}): number | null {
  return safeDivide(input.netOperatingIncome, input.annualDebtService)
}
debtServiceCoverageRatio.formula = 'Net Operating Income / Annual Debt Service (Principal + Interest)'
debtServiceCoverageRatio.description = 'Lenders require DSCR > 1.25. Critical for real estate and leveraged deals.'

export function fixedChargeCoverageRatio(input: {
  ebit: number
  fixedCharges: number
  interestExpense: number
}): number | null {
  return safeDivide(input.ebit + input.fixedCharges, input.fixedCharges + input.interestExpense)
}
fixedChargeCoverageRatio.formula = '(EBIT + Fixed Charges) / (Fixed Charges + Interest Expense)'
fixedChargeCoverageRatio.description = 'Covers lease payments and other fixed obligations beyond interest.'

export function equityMultiplier(input: {
  totalAssets: number
  totalEquity: number
}): number | null {
  return safeDivide(input.totalAssets, input.totalEquity)
}
equityMultiplier.formula = 'Total Assets / Total Equity'
equityMultiplier.description = 'Leverage component of DuPont analysis.'
