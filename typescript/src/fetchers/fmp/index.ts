/**
 * Financial Modeling Prep (FMP) fetcher.
 * Free tier: 250 requests/day.
 * Get API key: https://financialmodelingprep.com/developer/docs
 */

import type {
  IncomeStatement,
  BalanceSheet,
  CashFlowStatement,
  MarketData,
} from '../../types/index.js'

const FMP_BASE = 'https://financialmodelingprep.com/api/v3'

export interface FmpOptions {
  apiKey: string
  periods?: number
  quarterly?: boolean
}

export interface FmpPeriodData {
  period: string
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement
  marketData: MarketData
  ratios?: Record<string, number | null>
}

/**
 * Fetch financial statements from Financial Modeling Prep.
 *
 * @example
 * const data = await fetchFmp('AAPL', { apiKey: 'your_key', periods: 4 })
 * for (const period of data) {
 *   const roicVal = roic({ nopat: ..., investedCapital: ... })
 * }
 */
export async function fetchFmp(
  ticker: string,
  options: FmpOptions
): Promise<FmpPeriodData[]> {
  const { apiKey, periods = 4, quarterly = false } = options
  const period = quarterly ? 'quarter' : 'annual'
  const limit = periods

  const [incData, balData, cfData, ratioData, profileData] = await Promise.all([
    _get(`${FMP_BASE}/income-statement/${ticker}`, apiKey, { period, limit }),
    _get(`${FMP_BASE}/balance-sheet-statement/${ticker}`, apiKey, { period, limit }),
    _get(`${FMP_BASE}/cash-flow-statement/${ticker}`, apiKey, { period, limit }),
    _get(`${FMP_BASE}/ratios/${ticker}`, apiKey, { period, limit }),
    _get(`${FMP_BASE}/profile/${ticker}`, apiKey, {}),
  ])

  const profile = (profileData as any[])[0] ?? {}
  const results: FmpPeriodData[] = []

  for (let i = 0; i < Math.min(limit, (incData as any[]).length); i++) {
    const inc = (incData as any[])[i] ?? {}
    const bal = (balData as any[])[i] ?? {}
    const cf = (cfData as any[])[i] ?? {}
    const rat = (ratioData as any[])[i] ?? {}

    results.push({
      period: inc.date ?? '',
      income: {
        revenue: _n(inc.revenue),
        grossProfit: _n(inc.grossProfit),
        cogs: _n(inc.costOfRevenue),
        ebit: _n(inc.operatingIncome),
        ebitda: _n(inc.ebitda),
        netIncome: _n(inc.netIncome),
        interestExpense: Math.abs(_n(inc.interestExpense)),
        incomeTaxExpense: _n(inc.incomeTaxExpense),
        ebt: _n(inc.incomeBeforeTax),
        depreciationAndAmortization: _n(inc.depreciationAndAmortization),
        sharesOutstanding: _n(inc.weightedAverageShsOut),
        eps: _n(inc.eps),
        epsDiluted: _n(inc.epsdiluted),
      },
      balance: {
        totalAssets: _n(bal.totalAssets),
        currentAssets: _n(bal.totalCurrentAssets),
        cash: _n(bal.cashAndCashEquivalents),
        accountsReceivable: _n(bal.netReceivables),
        inventory: _n(bal.inventory),
        netPPE: _n(bal.propertyPlantEquipmentNet),
        goodwill: _n(bal.goodwill),
        intangibleAssets: _n(bal.intangibleAssets),
        retainedEarnings: _n(bal.retainedEarnings),
        totalLiabilities: _n(bal.totalLiabilities),
        currentLiabilities: _n(bal.totalCurrentLiabilities),
        accountsPayable: _n(bal.accountPayables),
        longTermDebt: _n(bal.longTermDebt),
        totalDebt: _n(bal.totalDebt),
        totalEquity: _n(bal.totalStockholdersEquity),
        sharesOutstanding: _n(inc.weightedAverageShsOut),
      },
      cashFlow: {
        operatingCashFlow: _n(cf.operatingCashFlow),
        capex: Math.abs(_n(cf.capitalExpenditure)),
        investingCashFlow: _n(cf.investingActivitiesCashFlow),
        financingCashFlow: _n(cf.financingActivitiesCashFlow),
        dividendsPaid: _n(cf.commonDividendsPaid),
        stockBasedCompensation: _n(cf.stockBasedCompensation),
        debtRepayments: _n(cf.debtRepayment),
      },
      marketData: {
        price: _n(profile.price),
        marketCap: _n(profile.mktCap),
        sharesOutstanding: _n(inc.weightedAverageShsOut),
        ticker,
      },
      ratios: {
        peRatio: _n(rat.priceEarningsRatio),
        pbRatio: _n(rat.priceToBookRatio),
        psRatio: _n(rat.priceToSalesRatio),
        evToEbitda: _n(rat.enterpriseValueMultiple),
        roic: _n(rat.returnOnCapitalEmployed),
        roe: _n(rat.returnOnEquity),
        roa: _n(rat.returnOnAssets),
        currentRatio: _n(rat.currentRatio),
        debtToEquity: _n(rat.debtEquityRatio),
        grossMargin: _n(rat.grossProfitMargin),
        operatingMargin: _n(rat.operatingProfitMargin),
        netMargin: _n(rat.netProfitMargin),
      },
    })
  }

  return results
}

/** Fetch the current S&P 500 constituent list. */
export async function fetchFmpSp500(apiKey: string): Promise<string[]> {
  const data = (await _get(`${FMP_BASE}/sp500_constituent`, apiKey, {})) as any[]
  return data.map(d => d.symbol).filter(Boolean)
}

async function _get(url: string, apiKey: string, params: Record<string, unknown>): Promise<unknown> {
  const query = new URLSearchParams({ ...Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)])), apikey: apiKey })
  const resp = await fetch(`${url}?${query}`)
  if (!resp.ok) throw new Error(`FMP request failed: ${resp.status} ${url}`)
  return resp.json()
}

function _n(v: unknown): number {
  if (v == null) return 0
  const n = Number(v)
  return isNaN(n) ? 0 : n
}
