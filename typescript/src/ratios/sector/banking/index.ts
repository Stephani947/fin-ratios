import { safeDivide } from '../../../utils/safe-divide.js'

export function netInterestMargin(input: {
  interestIncome: number
  interestExpense: number
  avgEarningAssets: number
}): number | null {
  return safeDivide(input.interestIncome - input.interestExpense, input.avgEarningAssets)
}
netInterestMargin.formula = '(Interest Income - Interest Expense) / Average Earning Assets'
netInterestMargin.description = 'NIM — core profitability of a bank\'s lending activity.'

export function efficiencyRatio(input: {
  nonInterestExpense: number
  netInterestIncome: number
  nonInterestIncome: number
}): number | null {
  return safeDivide(input.nonInterestExpense, input.netInterestIncome + input.nonInterestIncome)
}
efficiencyRatio.formula = 'Non-Interest Expense / (Net Interest Income + Non-Interest Income)'
efficiencyRatio.description = 'Cost to generate $1 of revenue. Lower is better. < 60% is well-run.'

export function loanToDepositRatio(input: {
  totalLoans: number
  totalDeposits: number
}): number | null {
  return safeDivide(input.totalLoans, input.totalDeposits)
}
loanToDepositRatio.formula = 'Total Loans / Total Deposits'
loanToDepositRatio.description = 'Liquidity indicator. > 100% means more loans than deposits (reliant on borrowing).'

export function nplRatio(input: {
  nonPerformingLoans: number
  totalLoans: number
}): number | null {
  return safeDivide(input.nonPerformingLoans, input.totalLoans)
}
nplRatio.formula = 'Non-Performing Loans / Total Loans'
nplRatio.description = 'Asset quality metric. > 2-3% warrants scrutiny.'

export function provisionCoverageRatio(input: {
  loanLossReserves: number
  nonPerformingLoans: number
}): number | null {
  return safeDivide(input.loanLossReserves, input.nonPerformingLoans)
}
provisionCoverageRatio.formula = 'Loan Loss Reserves / Non-Performing Loans'
provisionCoverageRatio.description = 'How much of bad loans are reserved for. > 100% is conservative.'

export function tier1CapitalRatio(input: {
  tier1Capital: number
  riskWeightedAssets: number
}): number | null {
  return safeDivide(input.tier1Capital, input.riskWeightedAssets)
}
tier1CapitalRatio.formula = 'Tier 1 Capital / Risk-Weighted Assets'
tier1CapitalRatio.description = 'Core capital adequacy. Regulatory minimum is 6%, well-capitalized is > 8%.'

export function cet1Ratio(input: {
  commonEquityTier1: number
  riskWeightedAssets: number
}): number | null {
  return safeDivide(input.commonEquityTier1, input.riskWeightedAssets)
}
cet1Ratio.formula = 'Common Equity Tier 1 / Risk-Weighted Assets'
cet1Ratio.description = 'Highest-quality capital ratio. Regulatory minimum is 4.5%.'

export function tangibleBookValuePerShare(input: {
  totalEquity: number
  goodwill: number
  intangibleAssets: number
  sharesOutstanding: number
}): number | null {
  const tbv = input.totalEquity - input.goodwill - input.intangibleAssets
  return safeDivide(tbv, input.sharesOutstanding)
}
tangibleBookValuePerShare.formula = '(Equity - Goodwill - Intangibles) / Shares Outstanding'
tangibleBookValuePerShare.description = 'TBVPS — the most conservative per-share book value for banks.'
