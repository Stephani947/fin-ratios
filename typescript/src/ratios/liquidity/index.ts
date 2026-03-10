import { safeDivide } from '../../utils/safe-divide.js'

export function currentRatio(input: {
  currentAssets: number
  currentLiabilities: number
}): number | null {
  return safeDivide(input.currentAssets, input.currentLiabilities)
}
currentRatio.formula = 'Current Assets / Current Liabilities'
currentRatio.description = 'Ability to pay short-term obligations. > 1 generally healthy.'

export function quickRatio(input: {
  cash: number
  shortTermInvestments: number
  accountsReceivable: number
  currentLiabilities: number
}): number | null {
  const liquid = input.cash + input.shortTermInvestments + input.accountsReceivable
  return safeDivide(liquid, input.currentLiabilities)
}
quickRatio.formula = '(Cash + ST Investments + Accounts Receivable) / Current Liabilities'
quickRatio.description = 'Liquidity excluding inventory. More conservative than current ratio.'

export function cashRatio(input: {
  cash: number
  shortTermInvestments: number
  currentLiabilities: number
}): number | null {
  return safeDivide(input.cash + input.shortTermInvestments, input.currentLiabilities)
}
cashRatio.formula = '(Cash + Short-Term Investments) / Current Liabilities'
cashRatio.description = 'Most conservative liquidity measure. Only counts actual cash.'

export function operatingCashFlowRatio(input: {
  operatingCashFlow: number
  currentLiabilities: number
}): number | null {
  return safeDivide(input.operatingCashFlow, input.currentLiabilities)
}
operatingCashFlowRatio.formula = 'Operating Cash Flow / Current Liabilities'
operatingCashFlowRatio.description = 'How well operating cash flow covers short-term obligations.'

// ── Working Capital Cycle ─────────────────────────────────────────────────────

export function dso(input: {
  accountsReceivable: number
  revenue: number
}): number | null {
  return safeDivide(input.accountsReceivable * 365, input.revenue)
}
dso.formula = '(Accounts Receivable / Revenue) × 365'
dso.description = 'Days Sales Outstanding — average days to collect payment after a sale.'

export function dio(input: {
  inventory: number
  cogs: number
}): number | null {
  return safeDivide(input.inventory * 365, input.cogs)
}
dio.formula = '(Inventory / COGS) × 365'
dio.description = 'Days Inventory Outstanding — average days inventory is held before sale.'

export function dpo(input: {
  accountsPayable: number
  cogs: number
}): number | null {
  return safeDivide(input.accountsPayable * 365, input.cogs)
}
dpo.formula = '(Accounts Payable / COGS) × 365'
dpo.description = 'Days Payable Outstanding — average days taken to pay suppliers.'

export function cashConversionCycle(input: {
  dso: number
  dio: number
  dpo: number
}): number {
  return input.dso + input.dio - input.dpo
}
cashConversionCycle.formula = 'DSO + DIO - DPO'
cashConversionCycle.description = 'Days from cash outflow (inventory) to cash inflow (collections). Lower is better.'

export function defensiveIntervalRatio(input: {
  cash: number
  shortTermInvestments: number
  accountsReceivable: number
  dailyOperatingExpenses: number
}): number | null {
  const liquid = input.cash + input.shortTermInvestments + input.accountsReceivable
  return safeDivide(liquid, input.dailyOperatingExpenses)
}
defensiveIntervalRatio.formula = '(Cash + ST Investments + AR) / Daily Operating Expenses'
defensiveIntervalRatio.description = 'Days the company can operate using liquid assets alone, without new revenue.'
