/**
 * SEC EDGAR fetcher for fin-ratios (TypeScript).
 *
 * Fetches financial data from the free SEC EDGAR XBRL API.
 * No API key required. US companies only.
 *
 * Rate limit: ~10 requests/second (SEC guidelines). Add delays for bulk use.
 *
 * @example
 * import { fetchEdgar } from 'fin-ratios/fetchers/edgar'
 * const filings = await fetchEdgar('AAPL', { numYears: 3 })
 * for (const f of filings) {
 *   console.log(`${f.fiscalYear}: Revenue $${(f.income.revenue/1e9).toFixed(1)}B`)
 * }
 */

import type { IncomeStatement, BalanceSheet, CashFlowStatement } from '../../types/index.js'

const COMPANY_TICKERS_URL = 'https://data.sec.gov/files/company_tickers.json'
const EDGAR_BASE = 'https://data.sec.gov/api/xbrl/companyfacts'

const HEADERS = {
  'User-Agent': 'fin-ratios/0.1.0 contact@fin-ratios.dev',
  'Accept-Encoding': 'gzip, deflate',
}

export interface EdgarOptions {
  numYears?: number
}

export interface EdgarFilingData {
  fiscalYear: string
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement
}

/**
 * Fetch multi-year annual filings from SEC EDGAR for a US stock ticker.
 */
export async function fetchEdgar(
  ticker: string,
  options: EdgarOptions = {}
): Promise<EdgarFilingData[]> {
  const { numYears = 3 } = options

  // Step 1: Resolve ticker → CIK
  const tickerMap = (await _get(COMPANY_TICKERS_URL)) as Record<string, { cik_str: number; ticker: string; title: string }>
  const entry = Object.values(tickerMap).find(v => v.ticker.toUpperCase() === ticker.toUpperCase())
  if (!entry) throw new Error(`EDGAR: ticker ${ticker} not found`)

  const cik = String(entry.cik_str).padStart(10, '0')

  // Step 2: Fetch company facts (XBRL)
  const facts = (await _get(`${EDGAR_BASE}/CIK${cik}.json`)) as {
    facts: {
      'us-gaap'?: Record<string, { units: { USD?: { val: number; end: string; form: string; fp: string }[] } }>
    }
  }

  const gaap = facts.facts['us-gaap'] ?? {}

  function _annual(concept: string): { end: string; val: number }[] {
    const entries = gaap[concept]?.units?.USD ?? []
    return entries
      .filter(e => e.form === '10-K')
      .sort((a, b) => b.end.localeCompare(a.end))
  }

  function _latestForYear(concept: string, year: string): number {
    const annual = _annual(concept)
    const match = annual.find(e => e.end.startsWith(year))
    return match?.val ?? 0
  }

  // Collect available fiscal years from revenue
  const revenueEntries = _annual('Revenues').concat(_annual('RevenueFromContractWithCustomerExcludingAssessedTax'))
  const years = [...new Set(revenueEntries.map(e => e.end.slice(0, 4)))].slice(0, numYears)

  const results: EdgarFilingData[] = []

  for (const year of years) {
    const rev   = _latestForYear('Revenues', year) || _latestForYear('RevenueFromContractWithCustomerExcludingAssessedTax', year)
    const ni    = _latestForYear('NetIncomeLoss', year)
    const ebit  = _latestForYear('OperatingIncomeLoss', year)
    const ta    = _latestForYear('Assets', year)
    const ca    = _latestForYear('AssetsCurrent', year)
    const cash  = _latestForYear('CashAndCashEquivalentsAtCarryingValue', year)
    const ar    = _latestForYear('AccountsReceivableNetCurrent', year)
    const inv   = _latestForYear('InventoryNet', year)
    const cl    = _latestForYear('LiabilitiesCurrent', year)
    const tl    = _latestForYear('Liabilities', year)
    const ltd   = _latestForYear('LongTermDebt', year)
    const re    = _latestForYear('RetainedEarningsAccumulatedDeficit', year)
    const te    = _latestForYear('StockholdersEquity', year)
    const ocf   = _latestForYear('NetCashProvidedByUsedInOperatingActivities', year)
    const capex = _latestForYear('PaymentsToAcquirePropertyPlantAndEquipment', year)
    const gp    = _latestForYear('GrossProfit', year)
    const int   = _latestForYear('InterestExpense', year)
    const tax   = _latestForYear('IncomeTaxExpense', year) || _latestForYear('IncomeTaxesPaidNet', year)

    results.push({
      fiscalYear: year,
      income: {
        revenue: rev, grossProfit: gp, cogs: rev - gp,
        ebit, ebitda: 0, netIncome: ni,
        interestExpense: Math.abs(int), incomeTaxExpense: tax, ebt: ni + tax,
        depreciationAndAmortization: 0, sharesOutstanding: 0, eps: 0,
      },
      balance: {
        totalAssets: ta, currentAssets: ca, cash, accountsReceivable: ar,
        inventory: inv, netPPE: 0, goodwill: 0,
        retainedEarnings: re, totalLiabilities: tl, currentLiabilities: cl,
        accountsPayable: 0, longTermDebt: ltd, totalDebt: ltd,
        totalEquity: te, sharesOutstanding: 0,
      },
      cashFlow: {
        operatingCashFlow: ocf, capex: Math.abs(capex),
        investingCashFlow: 0, financingCashFlow: 0,
      },
    })
  }

  return results
}

async function _get(url: string): Promise<unknown> {
  const resp = await fetch(url, { headers: HEADERS })
  if (!resp.ok) throw new Error(`EDGAR request failed: ${resp.status} ${url}`)
  return resp.json()
}
