import { safeDivide } from '../../utils/safe-divide.js'

// ── P/E ──────────────────────────────────────────────────────────────────────

export function pe(input: {
  marketCap: number
  netIncome: number
}): number | null {
  return safeDivide(input.marketCap, input.netIncome)
}
pe.formula = 'Market Capitalization / Net Income'
pe.description = 'Trailing price-to-earnings ratio. How much investors pay per dollar of earnings.'

export function forwardPe(input: {
  price: number
  forwardEps: number
}): number | null {
  return safeDivide(input.price, input.forwardEps)
}
forwardPe.formula = 'Stock Price / Forward EPS Estimate'
forwardPe.description = 'P/E based on next twelve months analyst EPS estimate.'

// ── PEG ──────────────────────────────────────────────────────────────────────

export function peg(input: {
  peRatio: number
  epsGrowthRatePercent: number
}): number | null {
  return safeDivide(input.peRatio, input.epsGrowthRatePercent)
}
peg.formula = 'P/E Ratio / EPS Annual Growth Rate (%)'
peg.description = 'PEG ratio. < 1 may indicate undervaluation relative to growth.'

// ── P/B ──────────────────────────────────────────────────────────────────────

export function pb(input: {
  marketCap: number
  totalEquity: number
}): number | null {
  return safeDivide(input.marketCap, input.totalEquity)
}
pb.formula = 'Market Capitalization / Total Shareholders Equity'
pb.description = 'Price-to-book ratio. < 1 may indicate trading below net asset value.'

// ── P/S ──────────────────────────────────────────────────────────────────────

export function ps(input: {
  marketCap: number
  revenue: number
}): number | null {
  return safeDivide(input.marketCap, input.revenue)
}
ps.formula = 'Market Capitalization / Revenue'
ps.description = 'Price-to-sales ratio. Useful when earnings are negative.'

// ── P/FCF ─────────────────────────────────────────────────────────────────────

export function pFcf(input: {
  marketCap: number
  operatingCashFlow: number
  capex: number
}): number | null {
  const fcf = input.operatingCashFlow - Math.abs(input.capex)
  return safeDivide(input.marketCap, fcf)
}
pFcf.formula = 'Market Capitalization / (Operating Cash Flow - Capex)'
pFcf.description = 'Price-to-free-cash-flow. Often considered cleaner than P/E.'

// ── Enterprise Value ──────────────────────────────────────────────────────────

export function enterpriseValue(input: {
  marketCap: number
  totalDebt: number
  cash: number
  minorityInterest?: number | null
  preferredStock?: number | null
}): number {
  return (
    input.marketCap +
    input.totalDebt -
    input.cash +
    (input.minorityInterest ?? 0) +
    (input.preferredStock ?? 0)
  )
}
enterpriseValue.formula = 'Market Cap + Total Debt - Cash + Minority Interest + Preferred Stock'
enterpriseValue.description = 'Enterprise value — the theoretical takeover price of a company.'

// ── EV Multiples ─────────────────────────────────────────────────────────────

export function evEbitda(input: {
  enterpriseValue: number
  ebitda: number
}): number | null {
  return safeDivide(input.enterpriseValue, input.ebitda)
}
evEbitda.formula = 'Enterprise Value / EBITDA'
evEbitda.description = 'Capital-structure-neutral valuation multiple. Popular in LBO analysis.'

export function evEbit(input: {
  enterpriseValue: number
  ebit: number
}): number | null {
  return safeDivide(input.enterpriseValue, input.ebit)
}
evEbit.formula = 'Enterprise Value / EBIT'
evEbit.description = 'Like EV/EBITDA but accounts for depreciation-heavy businesses.'

export function evRevenue(input: {
  enterpriseValue: number
  revenue: number
}): number | null {
  return safeDivide(input.enterpriseValue, input.revenue)
}
evRevenue.formula = 'Enterprise Value / Revenue'
evRevenue.description = 'Useful for high-growth companies without positive EBITDA.'

export function evFcf(input: {
  enterpriseValue: number
  freeCashFlow: number
}): number | null {
  return safeDivide(input.enterpriseValue, input.freeCashFlow)
}
evFcf.formula = 'Enterprise Value / Free Cash Flow'
evFcf.description = 'EV-to-free-cash-flow. Preferred by value investors.'

export function evInvestedCapital(input: {
  enterpriseValue: number
  investedCapital: number
}): number | null {
  return safeDivide(input.enterpriseValue, input.investedCapital)
}
evInvestedCapital.formula = 'Enterprise Value / Invested Capital'
evInvestedCapital.description = 'Indicates whether the market values the company above its invested capital base.'

// ── Tobin's Q ─────────────────────────────────────────────────────────────────

export function tobinsQ(input: {
  marketCap: number
  totalDebt: number
  totalAssets: number
}): number | null {
  const marketValue = input.marketCap + input.totalDebt
  return safeDivide(marketValue, input.totalAssets)
}
tobinsQ.formula = '(Market Cap + Total Debt) / Total Assets'
tobinsQ.description = 'Q > 1 = market values firm above replacement cost. Q < 1 = below.'

// ── Graham Number ─────────────────────────────────────────────────────────────

export function grahamNumber(input: {
  eps: number
  bookValuePerShare: number
}): number | null {
  if (input.eps <= 0 || input.bookValuePerShare <= 0) return null
  return Math.sqrt(22.5 * input.eps * input.bookValuePerShare)
}
grahamNumber.formula = 'sqrt(22.5 × EPS × Book Value Per Share)'
grahamNumber.description = 'Ben Graham\'s estimate of fair value. Buy below, sell above.'

// ── Ben Graham Intrinsic Value ─────────────────────────────────────────────────

export function grahamIntrinsicValue(input: {
  eps: number
  growthRate: number
  aaaBondYield: number
}): number | null {
  if (input.aaaBondYield <= 0) return null
  // Graham's revised formula: V* = EPS × (8.5 + 2g) × 4.4 / Y
  return safeDivide(
    input.eps * (8.5 + 2 * input.growthRate) * 4.4,
    input.aaaBondYield
  )
}
grahamIntrinsicValue.formula = 'EPS × (8.5 + 2 × Growth Rate) × 4.4 / AAA Bond Yield'
grahamIntrinsicValue.description = 'Graham\'s 1962 revised intrinsic value formula. Use growth rate as %, e.g. 15.'
