/**
 * SEC EDGAR fetcher for fin-ratios (TypeScript).
 *
 * Fetches financial data from the free SEC EDGAR XBRL API.
 * No API key required. US companies only.
 *
 * Rate limit: ~10 requests/second (SEC guidelines). Add delays for bulk use.
 *
 * @example
 * import { fetchEdgar, fetchEdgarNormalized } from 'fin-ratios/fetchers/edgar'
 *
 * // Structured filings (newest-first)
 * const filings = await fetchEdgar('AAPL', { numYears: 5 })
 *
 * // Flat records ready for scoring utilities (oldest-first)
 * const annualData = await fetchEdgarNormalized('AAPL', { numYears: 10 })
 * const quality = qualityScore(annualData)
 */

import type { IncomeStatement, BalanceSheet, CashFlowStatement } from '../../types/index.js'
import type { AnnualQualityData } from '../../utils/quality-score.js'
import type { AnnualCapitalData } from '../../utils/capital-allocation.js'

const COMPANY_TICKERS_URL = 'https://data.sec.gov/files/company_tickers.json'
const EDGAR_BASE = 'https://data.sec.gov/api/xbrl/companyfacts'

const HEADERS = {
  'User-Agent': 'fin-ratios/1.0 contact@fin-ratios.dev',
  'Accept-Encoding': 'gzip, deflate',
}

export interface EdgarOptions {
  numYears?: number
}

export interface EdgarFilingData {
  fiscalYear: string
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement & { dividendsPaid: number }
}

/**
 * Normalised annual record that satisfies all scoring utility input types:
 * moatScore, capitalAllocationScore, earningsQualityScore, qualityScore.
 */
export type EdgarAnnualRecord = AnnualQualityData &
  AnnualCapitalData & {
    year: string
    sharesOutstanding?: number
    currentAssets?: number
    currentLiabilities?: number
  }

/**
 * Fetch multi-year annual filings from SEC EDGAR for a US stock ticker.
 * Returns newest-first.
 */
export async function fetchEdgar(
  ticker: string,
  options: EdgarOptions = {}
): Promise<EdgarFilingData[]> {
  const { numYears = 5 } = options

  // Resolve ticker → CIK
  const tickerMap = (await _get(COMPANY_TICKERS_URL)) as Record<
    string,
    { cik_str: number; ticker: string; title: string }
  >
  const entry = Object.values(tickerMap).find(
    v => v.ticker.toUpperCase() === ticker.toUpperCase()
  )
  if (!entry) throw new Error(`EDGAR: ticker ${ticker} not found`)

  const cik = String(entry.cik_str).padStart(10, '0')
  const facts = (await _get(`${EDGAR_BASE}/CIK${cik}.json`)) as {
    facts: {
      'us-gaap'?: Record<
        string,
        {
          units: {
            USD?: { val: number; end: string; form: string; fp: string }[]
            shares?: { val: number; end: string; form: string; fp: string }[]
          }
        }
      >
    }
  }

  const gaap = facts.facts['us-gaap'] ?? {}

  function _annual(concept: string): { end: string; val: number }[] {
    return (gaap[concept]?.units?.USD ?? [])
      .filter(e => e.form === '10-K')
      .sort((a, b) => b.end.localeCompare(a.end))
  }

  function _annualShares(concept: string): { end: string; val: number }[] {
    return (gaap[concept]?.units?.shares ?? [])
      .filter(e => e.form === '10-K')
      .sort((a, b) => b.end.localeCompare(a.end))
  }

  function _pick(concept: string, year: string): number {
    return _annual(concept).find(e => e.end.startsWith(year))?.val ?? 0
  }

  function _pickShares(concept: string, year: string): number {
    return _annualShares(concept).find(e => e.end.startsWith(year))?.val ?? 0
  }

  // Determine available fiscal years from revenue
  const revEntries = _annual('Revenues').concat(
    _annual('RevenueFromContractWithCustomerExcludingAssessedTax')
  )
  const years = [...new Set(revEntries.map(e => e.end.slice(0, 4)))].slice(0, numYears)

  return years.map(year => {
    const rev   = _pick('Revenues', year) || _pick('RevenueFromContractWithCustomerExcludingAssessedTax', year)
    const gp    = _pick('GrossProfit', year)
    const ebit  = _pick('OperatingIncomeLoss', year)
    const ni    = _pick('NetIncomeLoss', year)
    const tax   = _pick('IncomeTaxExpenseBenefit', year) || _pick('IncomeTaxesPaidNet', year)
    const int_  = _pick('InterestExpense', year) || _pick('InterestAndDebtExpense', year)
    const depr  = _pick('DepreciationDepletionAndAmortization', year) || _pick('DepreciationAndAmortization', year)
    const ta    = _pick('Assets', year)
    const ca    = _pick('AssetsCurrent', year)
    const cash  = _pick('CashAndCashEquivalentsAtCarryingValue', year) || _pick('CashCashEquivalentsAndShortTermInvestments', year)
    const ar    = _pick('AccountsReceivableNetCurrent', year)
    const inv   = _pick('InventoryNet', year)
    const cl    = _pick('LiabilitiesCurrent', year)
    const tl    = _pick('Liabilities', year)
    const ltd   = _pick('LongTermDebt', year) || _pick('LongTermDebtNoncurrent', year)
    const std   = _pick('ShortTermBorrowings', year) || _pick('DebtCurrent', year)
    const re    = _pick('RetainedEarningsAccumulatedDeficit', year)
    const te    = _pick('StockholdersEquity', year) || _pick('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', year)
    const ocf   = _pick('NetCashProvidedByUsedInOperatingActivities', year)
    const capex = _pick('PaymentsToAcquirePropertyPlantAndEquipment', year)
    const divs  = _pick('PaymentsOfDividends', year) || _pick('PaymentsOfDividendsCommonStock', year)
    const shs   = _pickShares('CommonStockSharesOutstanding', year) || _pickShares('CommonStockSharesIssued', year)

    const totalDebt = ltd + std
    const ebt = ni + tax

    return {
      fiscalYear: year,
      income: {
        revenue: rev, grossProfit: gp, cogs: rev - gp,
        ebit, ebitda: ebit + depr, netIncome: ni,
        interestExpense: Math.abs(int_), incomeTaxExpense: tax, ebt,
        depreciationAndAmortization: depr,
        sharesOutstanding: shs, eps: shs > 0 ? ni / shs : 0,
      },
      balance: {
        totalAssets: ta, currentAssets: ca, cash, accountsReceivable: ar,
        inventory: inv, netPPE: 0, goodwill: 0,
        retainedEarnings: re, totalLiabilities: tl, currentLiabilities: cl,
        accountsPayable: _pick('AccountsPayableCurrent', year),
        longTermDebt: ltd, totalDebt,
        totalEquity: te, sharesOutstanding: shs,
      },
      cashFlow: {
        operatingCashFlow: ocf, capex: Math.abs(capex),
        investingCashFlow: 0, financingCashFlow: 0,
        dividendsPaid: Math.abs(divs),
      },
    }
  })
}

/**
 * Flatten EDGAR filings into a list of normalised annual records, oldest-first.
 * The returned type satisfies all scoring utility inputs:
 * moatScore, capitalAllocationScore, earningsQualityScore, qualityScore.
 */
export function normalizeForScoring(filings: EdgarFilingData[]): EdgarAnnualRecord[] {
  return [...filings].reverse().map(f => {
    const rec: EdgarAnnualRecord = {
      year:               f.fiscalYear,
      revenue:            f.income.revenue,
      grossProfit:        f.income.grossProfit,
      ebit:               f.income.ebit,
      ebt:                f.income.ebt,
      netIncome:          f.income.netIncome,
      incomeTaxExpense:   f.income.incomeTaxExpense,
      interestExpense:    f.income.interestExpense,
      totalAssets:        f.balance.totalAssets,
      totalEquity:        f.balance.totalEquity,
      totalDebt:          f.balance.totalDebt,
      cash:               f.balance.cash,
      currentAssets:      f.balance.currentAssets,
      currentLiabilities: f.balance.currentLiabilities,
      capex:              f.cashFlow.capex,
      depreciation:       f.income.depreciationAndAmortization,
      operatingCashFlow:  f.cashFlow.operatingCashFlow,
      accountsReceivable: f.balance.accountsReceivable,
    }
    rec.dividendsPaid = f.cashFlow.dividendsPaid
    if (f.balance.sharesOutstanding)  rec.sharesOutstanding = f.balance.sharesOutstanding
    return rec
  })
}

/**
 * @deprecated Use `normalizeForScoring` instead.
 * Kept for backwards compatibility.
 */
export function flattenEdgarData(filings: EdgarFilingData[]): EdgarAnnualRecord[] {
  return normalizeForScoring(filings)
}

/**
 * Fetch EDGAR data and return normalised annual records (oldest-first),
 * ready to pass directly to qualityScore(), moatScore(), etc.
 *
 * @example
 * const annualData = await fetchEdgarNormalized('AAPL', { numYears: 10 })
 * const qs = qualityScore(annualData)
 */
export async function fetchEdgarNormalized(
  ticker: string,
  options: EdgarOptions = {},
): Promise<EdgarAnnualRecord[]> {
  return normalizeForScoring(await fetchEdgar(ticker, options))
}

/**
 * @deprecated Use `fetchEdgarNormalized` instead.
 */
export async function fetchEdgarFlat(
  ticker: string,
  options: EdgarOptions = {},
): Promise<EdgarAnnualRecord[]> {
  return fetchEdgarNormalized(ticker, options)
}

async function _get(url: string): Promise<unknown> {
  const resp = await fetch(url, { headers: HEADERS })
  if (!resp.ok) throw new Error(`EDGAR fetch failed: ${resp.status} ${url}`)
  return resp.json()
}
