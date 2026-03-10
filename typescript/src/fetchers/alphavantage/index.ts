/**
 * Alpha Vantage fetcher for fin-ratios (TypeScript).
 *
 * Free tier: 25 requests/day. Premium: higher limits.
 * Get a free API key at https://www.alphavantage.co/support/#api-key
 *
 * @example
 * import { fetchAlphaVantage } from 'fin-ratios/fetchers/alphavantage'
 * const data = await fetchAlphaVantage('IBM', { apiKey: 'your_key' })
 * console.log(data.income.revenue)
 */

import type { IncomeStatement, BalanceSheet, CashFlowStatement, MarketData } from '../../types/index.js'

const BASE = 'https://www.alphavantage.co/query'

export interface AlphaVantageOptions {
  apiKey: string
  periods?: number
  quarterly?: boolean
}

export interface AlphaVantagePeriodData {
  period: string
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement
  marketData: MarketData
}

/**
 * Fetch financial statements from Alpha Vantage for a given ticker.
 */
export async function fetchAlphaVantage(
  ticker: string,
  options: AlphaVantageOptions
): Promise<AlphaVantagePeriodData[]> {
  const { apiKey, periods = 4, quarterly = false } = options

  const freq = quarterly ? 'quarterlyReports' : 'annualReports'

  const [incData, balData, cfData, quoteData] = await Promise.all([
    _get({ function: 'INCOME_STATEMENT', symbol: ticker, apikey: apiKey }),
    _get({ function: 'BALANCE_SHEET',    symbol: ticker, apikey: apiKey }),
    _get({ function: 'CASH_FLOW',        symbol: ticker, apikey: apiKey }),
    _get({ function: 'GLOBAL_QUOTE',     symbol: ticker, apikey: apiKey }),
  ]) as any[]

  const incReports: any[] = (incData[freq] ?? []).slice(0, periods)
  const balReports: any[] = (balData[freq] ?? []).slice(0, periods)
  const cfReports:  any[] = (cfData[freq]  ?? []).slice(0, periods)
  const quote = quoteData['Global Quote'] ?? {}

  const price = _n(quote['05. price'])
  const results: AlphaVantagePeriodData[] = []

  for (let i = 0; i < incReports.length; i++) {
    const inc = incReports[i] ?? {}
    const bal = balReports[i] ?? {}
    const cf  = cfReports[i]  ?? {}

    results.push({
      period: inc.fiscalDateEnding ?? '',
      income: {
        revenue:                    _n(inc.totalRevenue),
        grossProfit:                _n(inc.grossProfit),
        cogs:                       _n(inc.costOfRevenue),
        ebit:                       _n(inc.ebit),
        ebitda:                     _n(inc.ebitda),
        netIncome:                  _n(inc.netIncome),
        interestExpense:            Math.abs(_n(inc.interestExpense)),
        incomeTaxExpense:           _n(inc.incomeTaxExpense),
        ebt:                        _n(inc.incomeBeforeTax),
        depreciationAndAmortization:_n(inc.depreciationAndAmortization),
        sharesOutstanding:          _n(inc.commonStockSharesOutstanding),
        eps:                        0,
      },
      balance: {
        totalAssets:        _n(bal.totalAssets),
        currentAssets:      _n(bal.totalCurrentAssets),
        cash:               _n(bal.cashAndCashEquivalentsAtCarryingValue),
        accountsReceivable: _n(bal.currentNetReceivables),
        inventory:          _n(bal.inventory),
        netPPE:             _n(bal.propertyPlantEquipmentNet),
        goodwill:           _n(bal.goodwill),
        retainedEarnings:   _n(bal.retainedEarnings),
        totalLiabilities:   _n(bal.totalLiabilities),
        currentLiabilities: _n(bal.totalCurrentLiabilities),
        accountsPayable:    _n(bal.currentAccountsPayable),
        longTermDebt:       _n(bal.longTermDebtNoncurrent),
        totalDebt:          _n(bal.shortLongTermDebtTotal),
        totalEquity:        _n(bal.totalShareholderEquity),
        sharesOutstanding:  _n(bal.commonStockSharesOutstanding),
      },
      cashFlow: {
        operatingCashFlow: _n(cf.operatingCashflow),
        capex:             Math.abs(_n(cf.capitalExpenditures)),
        investingCashFlow: _n(cf.cashflowFromInvestment),
        financingCashFlow: _n(cf.cashflowFromFinancing),
        dividendsPaid:     _n(cf.dividendPayout),
      },
      marketData: {
        price,
        marketCap:         0, // not returned by Alpha Vantage income statement endpoints
        sharesOutstanding: _n(inc.commonStockSharesOutstanding),
        ticker,
      },
    })
  }

  return results
}

async function _get(params: Record<string, string>): Promise<unknown> {
  const query = new URLSearchParams(params)
  const resp = await fetch(`${BASE}?${query}`)
  if (!resp.ok) throw new Error(`Alpha Vantage request failed: ${resp.status}`)
  return resp.json()
}

function _n(v: unknown): number {
  if (v == null || v === 'None' || v === '-') return 0
  const n = Number(v)
  return isNaN(n) ? 0 : n
}
