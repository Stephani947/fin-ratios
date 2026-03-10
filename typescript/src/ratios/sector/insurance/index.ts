import { safeDivide } from '../../../utils/safe-divide.js'

export function lossRatio(input: {
  lossesIncurred: number
  premiumsEarned: number
}): number | null {
  return safeDivide(input.lossesIncurred, input.premiumsEarned)
}
lossRatio.formula = 'Losses Incurred / Premiums Earned'
lossRatio.description = 'Portion of premiums paid out as claims. < 60% is generally good for P&C.'

export function expenseRatio(input: {
  underwritingExpenses: number
  premiumsWritten: number
}): number | null {
  return safeDivide(input.underwritingExpenses, input.premiumsWritten)
}
expenseRatio.formula = 'Underwriting Expenses / Net Premiums Written'
expenseRatio.description = 'Cost of writing insurance. Lower is more efficient.'

export function combinedRatio(input: {
  lossRatio: number
  expenseRatio: number
}): number {
  return input.lossRatio + input.expenseRatio
}
combinedRatio.formula = 'Loss Ratio + Expense Ratio'
combinedRatio.description = 'The key insurance profitability metric. < 100% = underwriting profit. > 100% = loss.'

export function underwritingProfitMargin(input: {
  combinedRatio: number
}): number {
  return 1 - input.combinedRatio
}
underwritingProfitMargin.formula = '1 - Combined Ratio'
underwritingProfitMargin.description = 'Positive = underwriting profit. Most insurers also earn investment income.'

export function premiumsToSurplus(input: {
  netPremiumsWritten: number
  policyholderSurplus: number
}): number | null {
  return safeDivide(input.netPremiumsWritten, input.policyholderSurplus)
}
premiumsToSurplus.formula = 'Net Premiums Written / Policyholder Surplus'
premiumsToSurplus.description = 'Leverage ratio for insurers. > 3x is considered risky.'
