import { safeDivide } from '../../utils/safe-divide.js'

// ── Margin Ratios ─────────────────────────────────────────────────────────────

export function grossMargin(input: {
  grossProfit: number
  revenue: number
}): number | null {
  return safeDivide(input.grossProfit, input.revenue)
}
grossMargin.formula = 'Gross Profit / Revenue'
grossMargin.description = 'Percentage of revenue remaining after cost of goods sold.'

export function operatingMargin(input: {
  ebit: number
  revenue: number
}): number | null {
  return safeDivide(input.ebit, input.revenue)
}
operatingMargin.formula = 'EBIT / Revenue'
operatingMargin.description = 'Operating income as a percentage of revenue.'

export function ebitdaMargin(input: {
  ebitda: number
  revenue: number
}): number | null {
  return safeDivide(input.ebitda, input.revenue)
}
ebitdaMargin.formula = 'EBITDA / Revenue'
ebitdaMargin.description = 'Earnings before interest, taxes, D&A as % of revenue.'

export function netProfitMargin(input: {
  netIncome: number
  revenue: number
}): number | null {
  return safeDivide(input.netIncome, input.revenue)
}
netProfitMargin.formula = 'Net Income / Revenue'
netProfitMargin.description = 'Bottom-line profitability after all expenses.'

export function nopatMargin(input: {
  nopat: number
  revenue: number
}): number | null {
  return safeDivide(input.nopat, input.revenue)
}
nopatMargin.formula = 'NOPAT / Revenue'
nopatMargin.description = 'Net operating profit after tax as % of revenue.'

// ── Return Ratios ─────────────────────────────────────────────────────────────

export function roe(input: {
  netIncome: number
  avgTotalEquity: number
}): number | null {
  return safeDivide(input.netIncome, input.avgTotalEquity)
}
roe.formula = 'Net Income / Average Total Equity'
roe.description = 'Return on equity — how efficiently a company uses shareholder capital.'

export function roa(input: {
  netIncome: number
  avgTotalAssets: number
}): number | null {
  return safeDivide(input.netIncome, input.avgTotalAssets)
}
roa.formula = 'Net Income / Average Total Assets'
roa.description = 'Return on assets — how efficiently assets are used to generate profit.'

export function nopat(input: {
  ebit: number
  taxRate: number
}): number {
  return input.ebit * (1 - input.taxRate)
}
nopat.formula = 'EBIT × (1 - Effective Tax Rate)'
nopat.description = 'Net operating profit after tax — removes financing effects.'

export function roic(input: {
  nopat: number
  investedCapital: number
}): number | null {
  return safeDivide(input.nopat, input.investedCapital)
}
roic.formula = 'NOPAT / Invested Capital'
roic.description = 'ROIC vs WACC determines whether a company creates or destroys value.'

export function roce(input: {
  ebit: number
  totalAssets: number
  currentLiabilities: number
}): number | null {
  const capitalEmployed = input.totalAssets - input.currentLiabilities
  return safeDivide(input.ebit, capitalEmployed)
}
roce.formula = 'EBIT / (Total Assets - Current Liabilities)'
roce.description = 'Return on capital employed. Includes both equity and long-term debt.'

export function rote(input: {
  netIncome: number
  avgTotalEquity: number
  avgGoodwill: number
  avgIntangibleAssets: number
}): number | null {
  const tangibleEquity = input.avgTotalEquity - input.avgGoodwill - input.avgIntangibleAssets
  return safeDivide(input.netIncome, tangibleEquity)
}
rote.formula = 'Net Income / (Avg Equity - Avg Goodwill - Avg Intangibles)'
rote.description = 'Return on tangible equity. Strips acquisition premiums from the denominator.'

// ── DuPont Analysis ───────────────────────────────────────────────────────────

export interface DuPont3Factor {
  netProfitMargin: number | null
  assetTurnover: number | null
  equityMultiplier: number | null
  roe: number | null
}

export function duPont3(input: {
  netIncome: number
  revenue: number
  avgTotalAssets: number
  avgTotalEquity: number
}): DuPont3Factor {
  const margin = safeDivide(input.netIncome, input.revenue)
  const turnover = safeDivide(input.revenue, input.avgTotalAssets)
  const multiplier = safeDivide(input.avgTotalAssets, input.avgTotalEquity)
  const roeVal =
    margin != null && turnover != null && multiplier != null
      ? margin * turnover * multiplier
      : null
  return { netProfitMargin: margin, assetTurnover: turnover, equityMultiplier: multiplier, roe: roeVal }
}
duPont3.formula = 'ROE = Net Profit Margin × Asset Turnover × Equity Multiplier'
duPont3.description = '3-factor DuPont decomposition of ROE.'

// ── Per-Employee ──────────────────────────────────────────────────────────────

export function revenuePerEmployee(input: {
  revenue: number
  employeeCount: number
}): number | null {
  return safeDivide(input.revenue, input.employeeCount)
}
revenuePerEmployee.formula = 'Revenue / Full-Time Employees'
revenuePerEmployee.description = 'Measures workforce productivity.'

export function profitPerEmployee(input: {
  netIncome: number
  employeeCount: number
}): number | null {
  return safeDivide(input.netIncome, input.employeeCount)
}
profitPerEmployee.formula = 'Net Income / Full-Time Employees'
profitPerEmployee.description = 'Net income generated per employee.'

// ── Invested Capital ──────────────────────────────────────────────────────────

export function investedCapital(input: {
  totalEquity: number
  totalDebt: number
  cash: number
}): number {
  return input.totalEquity + input.totalDebt - input.cash
}
investedCapital.formula = 'Total Equity + Total Debt - Excess Cash'
investedCapital.description = 'Capital deployed to generate operating returns.'
