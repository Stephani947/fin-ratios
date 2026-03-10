/**
 * Yahoo Finance fetcher — free, no API key required.
 * Uses Yahoo Finance's public JSON endpoints.
 *
 * For production use, consider using the `yahoo-finance2` npm package instead:
 *   npm install yahoo-finance2
 *
 * Rate limit: ~2,000 requests/hour (unofficial). Add delays for bulk requests.
 */

import type {
  IncomeStatement,
  BalanceSheet,
  CashFlowStatement,
  MarketData,
} from '../../types/index.js'

const BASE = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary'
const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (compatible; fin-ratios/0.1)',
  'Accept': 'application/json',
}

export interface YahooFetchOptions {
  /** Additional modules to include (default covers all financial statements) */
  modules?: string[]
}

export interface YahooData {
  marketData: MarketData
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement
  sector?: string
  industry?: string
  employeeCount?: number
  beta?: number
  dividendYield?: number
}

/**
 * Fetch comprehensive financial data for a stock ticker from Yahoo Finance.
 *
 * @example
 * const data = await fetchYahoo('AAPL')
 * const ratio = pe({ marketCap: data.marketData.marketCap, netIncome: data.income.netIncome })
 */
export async function fetchYahoo(
  ticker: string,
  options: YahooFetchOptions = {}
): Promise<YahooData> {
  const modules = [
    'financialData',
    'defaultKeyStatistics',
    'summaryDetail',
    'assetProfile',
    'incomeStatementHistory',
    'balanceSheetHistory',
    'cashflowStatementHistory',
    ...(options.modules ?? []),
  ].join(',')

  const url = `${BASE}/${encodeURIComponent(ticker)}?modules=${modules}`

  const resp = await fetch(url, { headers: HEADERS })
  if (!resp.ok) {
    throw new Error(`Yahoo Finance request failed: ${resp.status} for ${ticker}`)
  }

  const json = (await resp.json()) as Record<string, unknown>
  const result = (json?.quoteSummary as any)?.result?.[0]
  if (!result) {
    throw new Error(`No data returned for ${ticker}`)
  }

  const fd = result.financialData ?? {}
  const ks = result.defaultKeyStatistics ?? {}
  const sd = result.summaryDetail ?? {}
  const ap = result.assetProfile ?? {}

  // Income statement (TTM)
  const inc = result.incomeStatementHistory?.incomeStatementHistory?.[0] ?? {}
  // Balance sheet (most recent quarter/year)
  const bal = result.balanceSheetHistory?.balanceSheetHistory?.[0] ?? {}
  // Cash flow (most recent)
  const cf = result.cashflowStatementHistory?.cashflowStatementHistory?.[0] ?? {}

  const price = _n(fd.currentPrice) ?? _n(fd.regularMarketPrice) ?? 0
  const marketCap = _n(ks.marketCap) ?? 0
  const shares = _n(ks.sharesOutstanding) ?? 0

  const base: YahooData = {
    marketData: {
      price,
      marketCap,
      sharesOutstanding: shares,
      enterpriseValue: _n(ks.enterpriseValue),
      forwardEps: _n(ks.forwardEps),
      trailingEps: _n(ks.trailingEps),
      dividendPerShare: _n(sd.dividendRate),
      ticker,
    },
    income: {
      revenue: _n(inc.totalRevenue) ?? _n(fd.totalRevenue) ?? 0,
      grossProfit: _n(inc.grossProfit) ?? 0,
      cogs: (_n(inc.totalRevenue) ?? 0) - (_n(inc.grossProfit) ?? 0),
      ebit: _n(inc.ebit) ?? _n(fd.operatingCashflow) ?? 0,
      ebitda: _n(fd.ebitda) ?? 0,
      netIncome: _n(inc.netIncome) ?? _n(fd.netIncomeToCommon) ?? 0,
      interestExpense: Math.abs(_n(inc.interestExpense) ?? 0),
      incomeTaxExpense: _n(inc.incomeTaxExpense) ?? 0,
      ebt: _n(inc.pretaxIncome) ?? 0,
      depreciationAndAmortization: 0, // Not available in this module
      sharesOutstanding: shares,
      eps: _n(ks.trailingEps),
    },
    balance: {
      totalAssets: _n(bal.totalAssets) ?? 0,
      currentAssets: _n(bal.totalCurrentAssets) ?? 0,
      cash: _n(bal.cash) ?? _n(fd.totalCash) ?? 0,
      shortTermInvestments: _n(bal.shortTermInvestments),
      accountsReceivable: _n(bal.netReceivables) ?? 0,
      inventory: _n(bal.inventory) ?? 0,
      netPPE: _n(bal.propertyPlantEquipment) ?? 0,
      goodwill: _n(bal.goodWill),
      intangibleAssets: _n(bal.intangibleAssets),
      retainedEarnings: _n(bal.retainedEarnings) ?? 0,
      totalLiabilities: _n(bal.totalLiab) ?? 0,
      currentLiabilities: _n(bal.totalCurrentLiabilities) ?? 0,
      accountsPayable: _n(bal.accountsPayable) ?? 0,
      shortTermDebt: _n(bal.shortLongTermDebt),
      longTermDebt: _n(bal.longTermDebt) ?? _n(fd.totalDebt) ?? 0,
      totalDebt: _n(fd.totalDebt) ?? 0,
      totalEquity: _n(bal.totalStockholderEquity) ?? 0,
      sharesOutstanding: shares,
    },
    cashFlow: {
      operatingCashFlow: _n(cf.totalCashFromOperatingActivities) ?? _n(fd.operatingCashflow) ?? 0,
      capex: Math.abs(_n(cf.capitalExpenditures) ?? 0),
      investingCashFlow: _n(cf.totalCashflowsFromInvestingActivities),
      financingCashFlow: _n(cf.totalCashFromFinancingActivities),
      dividendsPaid: _n(cf.dividendsPaid),
      stockBasedCompensation: _n(cf.stockBasedCompensation),
    },
    sector: ap.sector,
    industry: ap.industry,
  }
  const empCount = _n(ap.fullTimeEmployees); if (empCount != null) base.employeeCount = empCount
  const betaVal  = _n(ks.beta);             if (betaVal  != null) base.beta          = betaVal
  const divYield = _n(sd.dividendYield);    if (divYield != null) base.dividendYield  = divYield
  return base
}

/**
 * Fetch price history (daily close prices) for risk calculations.
 *
 * @example
 * const prices = await fetchPriceHistory('AAPL', '1y')
 * const returns = pricesToReturns(prices)
 * const sharpe = sharpeRatio({ returns, riskFreeRate: 0.05 })
 */
export async function fetchPriceHistory(
  ticker: string,
  period: '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y' | 'max' = '1y'
): Promise<{ dates: string[]; prices: number[] }> {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=${period}&interval=1d`
  const resp = await fetch(url, { headers: HEADERS })
  if (!resp.ok) throw new Error(`Price history request failed for ${ticker}`)

  const json = (await resp.json()) as any
  const chart = json?.chart?.result?.[0]
  if (!chart) throw new Error(`No price data for ${ticker}`)

  const timestamps: number[] = chart.timestamp ?? []
  const closes: number[] = chart.indicators?.quote?.[0]?.close ?? []

  const dates: string[] = []
  const prices: number[] = []

  for (let i = 0; i < timestamps.length; i++) {
    if (closes[i] != null) {
      dates.push(new Date((timestamps[i] ?? 0) * 1000).toISOString().split('T')[0]!)
      prices.push(closes[i] as number)
    }
  }

  return { dates, prices }
}

function _n(v: unknown): number | null {
  if (v == null) return null
  const raw = typeof v === 'object' ? (v as any).raw ?? v : v
  const n = Number(raw)
  return isNaN(n) ? null : n
}
