/**
 * Batch compute all applicable ratios from a single financial data object.
 *
 * Usage:
 *   import { computeAll } from 'fin-ratios'
 *
 *   const data = await fetchYahoo('AAPL')
 *   const ratios = computeAll(data)
 *   console.log(ratios.pe)           // 28.3
 *   console.log(ratios.roic)         // 0.55
 *   console.log(ratios.altmanZ)      // { zScore: 4.8, zone: 'safe', ... }
 */

import { safeDivide } from './safe-divide.js'

// Import all ratio functions
import {
  pe, pb, ps, peg, pFcf, evEbitda, evEbit, evRevenue, evFcf, tobinsQ, grahamNumber,
} from '../ratios/valuation/index.js'
import {
  grossMargin, operatingMargin, ebitdaMargin, netProfitMargin,
  roe, roa, nopat, roic, roce, investedCapital,
} from '../ratios/profitability/index.js'
import {
  currentRatio, quickRatio, dso, dio, dpo, cashConversionCycle,
} from '../ratios/liquidity/index.js'
import {
  debtToEquity, netDebtToEquity, netDebtToEbitda,
  debtToAssets, interestCoverageRatio, equityMultiplier,
} from '../ratios/solvency/index.js'
import {
  assetTurnover, receivablesTurnover, inventoryTurnover, payablesTurnover,
} from '../ratios/efficiency/index.js'
import {
  freeCashFlow, fcfYield, fcfMargin, fcfConversion, ocfToSales, capexToRevenue,
} from '../ratios/cashflow/index.js'
import {
  altmanZScore, piotroskiFScore,
} from '../ratios/composite/index.js'

// ── Input type ────────────────────────────────────────────────────────────────

export interface FinancialData {
  // Income Statement
  revenue?: number
  grossProfit?: number
  ebit?: number
  ebitda?: number
  netIncome?: number
  interestExpense?: number
  incomeTaxExpense?: number
  ebt?: number
  cogs?: number
  // Balance Sheet
  totalAssets?: number
  totalEquity?: number
  totalDebt?: number
  currentAssets?: number
  currentLiabilities?: number
  cash?: number
  accountsReceivable?: number
  inventory?: number
  retainedEarnings?: number
  totalLiabilities?: number
  accountsPayable?: number
  longTermDebt?: number
  sharesOutstanding?: number
  // Cash Flow
  operatingCashFlow?: number
  capex?: number
  // Market
  marketCap?: number
  enterpriseValue?: number
  epsGrowthPct?: number
  // Prior period (for Piotroski)
  prior?: Omit<FinancialData, 'prior' | 'marketCap' | 'enterpriseValue' | 'epsGrowthPct'>
}

// ── Output type ───────────────────────────────────────────────────────────────

export interface RatioResults {
  // Valuation
  pe?: number | null
  pb?: number | null
  ps?: number | null
  peg?: number | null
  pFcf?: number | null
  enterpriseValue?: number | null
  evEbitda?: number | null
  evEbit?: number | null
  evRevenue?: number | null
  evFcf?: number | null
  tobinsQ?: number | null
  grahamNumber?: number | null
  // Profitability
  grossMargin?: number | null
  operatingMargin?: number | null
  netMargin?: number | null
  ebitdaMargin?: number | null
  roe?: number | null
  roa?: number | null
  roic?: number | null
  roce?: number | null
  nopat?: number | null
  investedCapital?: number | null
  // Cash Flow
  freeCashFlow?: number | null
  fcfMargin?: number | null
  fcfConversion?: number | null
  ocfToSales?: number | null
  capexToRevenue?: number | null
  fcfYield?: number | null
  // Liquidity
  currentRatio?: number | null
  quickRatio?: number | null
  dso?: number | null
  dio?: number | null
  dpo?: number | null
  cashConversionCycle?: number | null
  // Solvency
  debtToEquity?: number | null
  netDebtToEquity?: number | null
  netDebtToEbitda?: number | null
  debtToAssets?: number | null
  interestCoverage?: number | null
  equityMultiplier?: number | null
  // Efficiency
  assetTurnover?: number | null
  receivablesTurnover?: number | null
  inventoryTurnover?: number | null
  payablesTurnover?: number | null
  // Composite
  altmanZ?: ReturnType<typeof altmanZScore>
  piotroski?: ReturnType<typeof piotroskiFScore> | null
}

// ── Helper ────────────────────────────────────────────────────────────────────

function g(data: FinancialData, key: keyof FinancialData): number {
  const v = data[key]
  if (v === undefined || v === null || typeof v === 'object') return 0
  return (v as number) || 0
}

function gn(data: FinancialData, key: keyof FinancialData): number | undefined {
  const v = data[key]
  if (v === undefined || v === null || typeof v === 'object') return undefined
  return (v as number) || undefined
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Compute all applicable financial ratios from a data object.
 *
 * Returns a flat object with 40+ ratio values. Complex scores (Altman, Piotroski)
 * are nested objects. Returns undefined for unavailable ratios.
 *
 * @param data  Financial data object with income/balance/cashflow/market fields
 * @returns     Flat object of ratio name → value
 *
 * @example
 *   const data = await fetchYahoo('AAPL')
 *   const r = computeAll(data)
 *   console.log(r.grossMargin)  // 0.433
 *   console.log(r.roic)         // 0.55
 *   console.log(r.altmanZ?.zone) // 'safe'
 */
export function computeAll(data: FinancialData): RatioResults {
  const result: RatioResults = {}

  const revenue = g(data, 'revenue')
  const grossProfit = g(data, 'grossProfit')
  const ebit = g(data, 'ebit')
  const ebitda = g(data, 'ebitda')
  const netIncome = g(data, 'netIncome')
  const totalAssets = g(data, 'totalAssets')
  const totalEquity = g(data, 'totalEquity')
  const totalDebt = g(data, 'totalDebt')
  const currentAssets = g(data, 'currentAssets')
  const currentLiabilities = g(data, 'currentLiabilities')
  const cash = g(data, 'cash')
  const accountsReceivable = g(data, 'accountsReceivable')
  const inventory = g(data, 'inventory')
  const marketCap = g(data, 'marketCap')
  const operatingCashFlow = g(data, 'operatingCashFlow')
  const capexRaw = g(data, 'capex')
  const interestExpense = g(data, 'interestExpense')
  const incomeTaxExpense = g(data, 'incomeTaxExpense')
  const ebt = g(data, 'ebt')
  const cogs = g(data, 'cogs')
  const accountsPayable = g(data, 'accountsPayable')
  const retainedEarnings = g(data, 'retainedEarnings')
  const totalLiabilities = g(data, 'totalLiabilities')
  const sharesOutstanding = g(data, 'sharesOutstanding')

  const fcf = freeCashFlow({ operatingCashFlow, capex: capexRaw })
  const ev = data.enterpriseValue || (marketCap + totalDebt - cash) || undefined

  const taxRate = ebt ? Math.min(Math.max(safeDivide(incomeTaxExpense, ebt) ?? 0.21, 0), 0.5) : 0.21
  const nopatVal = nopat({ ebit, taxRate })
  const icVal = investedCapital({ totalEquity, totalDebt, cash })

  // ── Valuation ───────────────────────────────────────────────────────────────
  result.pe = pe({ marketCap, netIncome })
  result.pb = pb({ marketCap, totalEquity })
  result.ps = ps({ marketCap, revenue })
  if (result.pe && data.epsGrowthPct) {
    result.peg = peg({ peRatio: result.pe, epsGrowthRatePercent: data.epsGrowthPct })
  }
  if (operatingCashFlow) result.pFcf = pFcf({ marketCap, operatingCashFlow, capex: capexRaw })
  result.enterpriseValue = ev ?? null
  if (ev && ebitda) result.evEbitda = evEbitda({ enterpriseValue: ev, ebitda })
  if (ev && ebit) result.evEbit = evEbit({ enterpriseValue: ev, ebit })
  if (ev && revenue) result.evRevenue = evRevenue({ enterpriseValue: ev, revenue })
  if (ev && fcf) result.evFcf = evFcf({ enterpriseValue: ev, freeCashFlow: fcf })
  result.tobinsQ = tobinsQ({ marketCap, totalDebt, totalAssets })
  if (sharesOutstanding) {
    const eps = safeDivide(netIncome, sharesOutstanding)
    const bvps = safeDivide(totalEquity, sharesOutstanding)
    if (eps && bvps) result.grahamNumber = grahamNumber({ eps, bookValuePerShare: bvps })
  }

  // ── Profitability ────────────────────────────────────────────────────────────
  result.grossMargin = grossMargin({ grossProfit, revenue })
  result.operatingMargin = operatingMargin({ ebit, revenue })
  result.netMargin = netProfitMargin({ netIncome, revenue })
  if (ebitda) result.ebitdaMargin = ebitdaMargin({ ebitda, revenue })
  result.roe = roe({ netIncome, avgTotalEquity: totalEquity })
  result.roa = roa({ netIncome, avgTotalAssets: totalAssets })
  result.nopat = nopatVal
  result.investedCapital = icVal
  if (nopatVal && icVal) result.roic = roic({ nopat: nopatVal, investedCapital: icVal })
  result.roce = roce({ ebit, totalAssets, currentLiabilities })

  // ── Cash Flow ────────────────────────────────────────────────────────────────
  result.freeCashFlow = fcf ?? null
  if (fcf) {
    result.fcfMargin = fcfMargin({ freeCashFlow: fcf, revenue })
    result.fcfConversion = fcfConversion({ freeCashFlow: fcf, netIncome })
    if (marketCap) result.fcfYield = fcfYield({ freeCashFlow: fcf, marketCap })
  }

  result.ocfToSales = ocfToSales({ operatingCashFlow, revenue })
  result.capexToRevenue = capexToRevenue({ capex: capexRaw, revenue })

  // ── Liquidity ────────────────────────────────────────────────────────────────
  result.currentRatio = currentRatio({ currentAssets, currentLiabilities })
  result.quickRatio = quickRatio({ cash, shortTermInvestments: 0, accountsReceivable, currentLiabilities })
  result.dso = dso({ accountsReceivable, revenue })
  if (cogs) {
    result.dio = dio({ inventory, cogs })
    result.dpo = dpo({ accountsPayable, cogs })
  }
  if (result.dso != null) {
    result.cashConversionCycle = cashConversionCycle({
      dso: result.dso,
      dio: result.dio ?? 0,
      dpo: result.dpo ?? 0,
    })
  }

  // ── Solvency ─────────────────────────────────────────────────────────────────
  result.debtToEquity = debtToEquity({ totalDebt, totalEquity })
  result.netDebtToEquity = netDebtToEquity({ totalDebt, cash, totalEquity })
  if (ebitda) result.netDebtToEbitda = netDebtToEbitda({ totalDebt, cash, ebitda })
  result.debtToAssets = debtToAssets({ totalDebt, totalAssets })
  result.interestCoverage = interestCoverageRatio({ ebit, interestExpense })
  result.equityMultiplier = equityMultiplier({ totalAssets, totalEquity })

  // ── Efficiency ───────────────────────────────────────────────────────────────
  result.assetTurnover = assetTurnover({ revenue, avgTotalAssets: totalAssets })
  result.receivablesTurnover = receivablesTurnover({ revenue, avgAccountsReceivable: accountsReceivable })
  if (cogs) {
    result.inventoryTurnover = inventoryTurnover({ cogs, avgInventory: inventory })
    result.payablesTurnover = payablesTurnover({ cogs, avgAccountsPayable: accountsPayable })
  }

  // ── Composite ────────────────────────────────────────────────────────────────
  if (totalAssets && totalLiabilities) {
    result.altmanZ = altmanZScore({
      workingCapital: currentAssets - currentLiabilities,
      retainedEarnings,
      ebit,
      marketCap,
      totalLiabilities,
      totalAssets,
      revenue,
    })
  }

  if (data.prior) {
    const p = data.prior
    const pGet = (key: keyof typeof p): number => {
      const v = p[key]
      return (typeof v === 'number' ? v : 0) || 0
    }
    try {
      result.piotroski = piotroskiFScore({
        current: {
          netIncome,
          totalAssets,
          operatingCashFlow,
          longTermDebt: g(data, 'longTermDebt'),
          currentAssets,
          currentLiabilities,
          sharesOutstanding,
          grossProfit,
          revenue,
        },
        prior: {
          netIncome: pGet('netIncome'),
          totalAssets: pGet('totalAssets'),
          longTermDebt: pGet('longTermDebt'),
          currentAssets: pGet('currentAssets'),
          currentLiabilities: pGet('currentLiabilities'),
          sharesOutstanding: pGet('sharesOutstanding'),
          grossProfit: pGet('grossProfit'),
          revenue: pGet('revenue'),
        },
      })
    } catch {
      result.piotroski = null
    }
  }

  return result
}
