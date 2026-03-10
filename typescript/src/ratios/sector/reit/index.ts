import { safeDivide } from '../../../utils/safe-divide.js'

export function ffo(input: {
  netIncome: number
  depreciation: number
  gainsOnSaleOfProperties: number
}): number {
  return input.netIncome + input.depreciation - input.gainsOnSaleOfProperties
}
ffo.formula = 'Net Income + Depreciation & Amortization - Gains on Sale of Properties'
ffo.description = 'Funds From Operations — the primary REIT earnings metric, strips out real estate depreciation.'

export function affo(input: {
  ffo: number
  recurringCapex: number
  straightLineRentAdjustment: number
}): number {
  return input.ffo - input.recurringCapex + input.straightLineRentAdjustment
}
affo.formula = 'FFO - Recurring Capex + Straight-Line Rent Adjustment'
affo.description = 'Adjusted FFO — closer to actual distributable cash flow.'

export function pFfo(input: {
  marketCap: number
  ffo: number
}): number | null {
  return safeDivide(input.marketCap, input.ffo)
}
pFfo.formula = 'Market Cap / FFO'
pFfo.description = 'Price-to-FFO — the REIT equivalent of P/E.'

export function pAffo(input: {
  marketCap: number
  affo: number
}): number | null {
  return safeDivide(input.marketCap, input.affo)
}
pAffo.formula = 'Market Cap / AFFO'
pAffo.description = 'Price-to-AFFO. More conservative and widely used by REIT analysts.'

export function netOperatingIncome(input: {
  revenue: number
  operatingExpenses: number
}): number {
  return input.revenue - input.operatingExpenses
}
netOperatingIncome.formula = 'Revenue - Operating Expenses (excluding D&A and interest)'
netOperatingIncome.description = 'NOI — the core profitability metric for real estate properties.'

export function capRate(input: {
  noi: number
  propertyValue: number
}): number | null {
  return safeDivide(input.noi, input.propertyValue)
}
capRate.formula = 'Net Operating Income / Property Value'
capRate.description = 'Expected annual return on a property. Higher cap rate = higher yield, often higher risk.'

export function occupancyRate(input: {
  occupiedUnits: number
  totalUnits: number
}): number | null {
  return safeDivide(input.occupiedUnits, input.totalUnits)
}
occupancyRate.formula = 'Occupied Units / Total Units'
occupancyRate.description = 'Key operational metric. > 95% is generally considered strong.'
