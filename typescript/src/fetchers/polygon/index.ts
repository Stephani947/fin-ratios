/**
 * Polygon.io fetcher for fin-ratios (TypeScript).
 *
 * Fetches fundamental financial data from the Polygon.io REST API.
 * API key required — get one at https://polygon.io.
 * US companies only.  Free tier: 5 req/min, ~2 years of history.
 *
 * @example
 * import { fetchPolygon, setPolygonApiKey } from 'fin-ratios/fetchers/polygon'
 * setPolygonApiKey('your-api-key')
 * const data = await fetchPolygon('AAPL', { numYears: 5 })
 * // data is oldest-first and compatible with all scoring utilities
 */

const POLYGON_BASE = 'https://api.polygon.io/vX/reference/financials'

// ── Module-level key storage ───────────────────────────────────────────────────

let _moduleKey: string | undefined

/**
 * Store a Polygon.io API key module-wide.
 * Subsequent calls to {@link fetchPolygon} will use this key unless overridden
 * via the {@link PolygonOptions.apiKey} option.
 */
export function setPolygonApiKey(key: string): void {
  _moduleKey = key
}

// ── Types ──────────────────────────────────────────────────────────────────────

export interface PolygonOptions {
  /** Number of annual periods to retrieve (default: 5). */
  numYears?: number
  /**
   * Polygon.io API key.  Falls back to the module-level key set via
   * {@link setPolygonApiKey} and then to the `POLYGON_API_KEY` environment
   * variable (Node.js only).
   */
  apiKey?: string
  /** ``'annual'`` (default) or ``'quarterly'``. */
  timeframe?: 'annual' | 'quarterly'
}

/**
 * Normalised annual financial record returned by {@link fetchPolygon}.
 * Field names are compatible with the `EdgarAnnualRecord` type used by the
 * EDGAR fetcher, so the data can be passed directly to all scoring utilities:
 * `moatScore`, `capitalAllocationScore`, `earningsQualityScore`,
 * `qualityScore`, `investmentScore`, etc.
 */
export interface PolygonAnnualRecord {
  /** Four-digit fiscal year string, e.g. ``'2023'``. */
  year: string
  revenue: number
  grossProfit: number
  /** Operating income (EBIT). */
  ebit: number
  netIncome: number
  totalAssets: number
  totalEquity: number
  /** Long-term debt (used as total debt proxy). */
  totalDebt: number
  cash: number
  /** Capital expenditures (absolute value). */
  capex: number
  depreciation: number
  operatingCashFlow: number
  incomeTaxExpense: number
  ebt: number
  interestExpense: number
  currentAssets: number
  currentLiabilities: number
  accountsReceivable: number
  /** Dividends paid (absolute value).  Zero for non-payers. */
  dividendsPaid?: number
  /** Shares outstanding (or weighted-average basic shares). */
  sharesOutstanding?: number
}

// ── Internal Polygon response types ───────────────────────────────────────────

interface _PolygonValue {
  value?: number | null
  unit?: string
  label?: string
}

interface _PolygonFinancials {
  income_statement?: Record<string, _PolygonValue>
  balance_sheet?: Record<string, _PolygonValue>
  cash_flow_statement?: Record<string, _PolygonValue>
}

interface _PolygonResult {
  fiscal_year?: string | number
  period_of_report_date?: string
  financials?: _PolygonFinancials
}

interface _PolygonResponse {
  results?: _PolygonResult[]
  status?: string
  request_id?: string
  next_url?: string
}

// ── Public API ─────────────────────────────────────────────────────────────────

/**
 * Fetch annual financial data from Polygon.io.
 *
 * @param ticker - Stock ticker symbol (e.g. ``'AAPL'``).
 * @param options - Options including API key, number of years, and timeframe.
 * @returns Oldest-first list of annual records compatible with all scoring
 *   utilities (moatScore, capitalAllocationScore, qualityScore, etc.).
 *
 * @throws {Error} If no API key is available.
 * @throws {Error} If the Polygon.io API request fails.
 *
 * @example
 * import { fetchPolygon } from 'fin-ratios/fetchers/polygon'
 * const data = await fetchPolygon('AAPL', { numYears: 5, apiKey: 'your-key' })
 */
export async function fetchPolygon(
  ticker: string,
  options: PolygonOptions = {}
): Promise<PolygonAnnualRecord[]> {
  const { numYears = 5, timeframe = 'annual' } = options

  // Resolve API key: option > module-level > env var
  const apiKey =
    options.apiKey ??
    _moduleKey ??
    (typeof process !== 'undefined' ? process.env['POLYGON_API_KEY'] : undefined)

  if (!apiKey) {
    throw new Error(
      'Polygon.io API key is required. Provide it via options.apiKey, ' +
        'setPolygonApiKey(), or the POLYGON_API_KEY environment variable.'
    )
  }

  // Build start date: go back numYears years from today
  const startDate = _startDate(Math.max(numYears, 2))

  const params = new URLSearchParams({
    ticker:                  ticker.toUpperCase(),
    timeframe,
    limit:                   String(Math.min(numYears, 100)),
    sort:                    'period_of_report_date',
    order:                   'asc',
    'filing_date.gte':       startDate,
    apiKey,
  })

  const url = `${POLYGON_BASE}?${params.toString()}`

  let payload: _PolygonResponse
  try {
    const resp = await fetch(url)
    if (resp.status === 401) {
      throw new Error(
        'Polygon API returned 401 Unauthorized — check your API key.'
      )
    }
    if (resp.status === 429) {
      throw new Error(
        'Polygon API rate limit exceeded (free tier: 5 req/min). ' +
          'Wait a moment and retry.'
      )
    }
    if (!resp.ok) {
      const body = await resp.text().catch(() => '')
      throw new Error(
        `Polygon API request failed for ${ticker}: HTTP ${resp.status} — ${body.slice(0, 200)}`
      )
    }
    payload = (await resp.json()) as _PolygonResponse
  } catch (err) {
    // Re-throw errors we constructed above; wrap unexpected fetch failures
    if (err instanceof Error && err.message.startsWith('Polygon API')) throw err
    throw new Error(
      `Polygon API request failed for ${ticker}: ${err instanceof Error ? err.message : String(err)}`
    )
  }

  const results = payload.results ?? []
  return results.map(item => _mapRecord(item))
}

// ── Mapping helpers ────────────────────────────────────────────────────────────

function _mapRecord(item: _PolygonResult): PolygonAnnualRecord {
  const inc = item.financials?.income_statement    ?? {}
  const bal = item.financials?.balance_sheet       ?? {}
  const cf  = item.financials?.cash_flow_statement ?? {}

  const revenue      = _v(inc, 'revenues', 'net_revenues', 'total_revenues')
  const grossProfit  = _v(inc, 'gross_profit')
  const ebit         = _v(inc, 'operating_income',
                           'income_loss_from_continuing_operations_before_tax')
  const netIncome    = _v(inc, 'net_income_loss', 'net_income_loss_attributable_to_parent')
  const taxExpense   = _v(inc, 'income_tax_expense_benefit')
  const interestExp  = Math.abs(_v(inc, 'interest_expense_operating', 'interest_expense'))

  // EBT: prefer direct field, fall back to net income + taxes
  const ebtDirect    = _v(inc, 'income_loss_from_continuing_operations_before_tax',
                           'income_before_income_taxes')
  const ebt          = ebtDirect !== 0 ? ebtDirect : netIncome + taxExpense

  const totalAssets  = _v(bal, 'assets')
  const currentAssets = _v(bal, 'current_assets')
  const cash         = _v(bal,
                          'cash_and_cash_equivalents_including_short_term_investments',
                          'cash_and_cash_equivalents', 'cash')
  const currentLiab  = _v(bal, 'current_liabilities')
  const totalEquity  = _v(bal, 'equity', 'stockholders_equity',
                           'equity_attributable_to_parent')
  const longTermDebt = _v(bal, 'long_term_debt')
  const ar           = _v(bal, 'accounts_receivable',
                           'accounts_receivable_net_current',
                           'trade_and_other_receivables_current')

  const ocf          = _v(cf, 'net_cash_flow_from_operating_activities',
                           'net_cash_provided_by_used_in_operating_activities')
  const investingCf  = _v(cf, 'net_cash_flow_from_investing_activities',
                           'net_cash_provided_by_used_in_investing_activities')
  const capexDirect  = _v(cf,
                           'payments_to_acquire_property_plant_and_equipment',
                           'capital_expenditures')
  const capex        = capexDirect !== 0 ? Math.abs(capexDirect) : Math.abs(investingCf)

  const dividendsPaid = Math.abs(
    _v(cf, 'payments_of_dividends', 'payments_of_dividends_common_stock', 'dividends_paid')
  )

  let depreciation = _v(inc, 'depreciation_and_amortization',
                         'depreciation_depletion_and_amortization')
  if (depreciation === 0) {
    depreciation = _v(cf, 'depreciation_depletion_and_amortization',
                      'depreciation_and_amortization')
  }

  // Shares: prefer balance-sheet figure; fall back to income-statement weighted avg
  const sharesBS    = _v(bal, 'common_stock_shares_outstanding')
  const sharesInc   = _v(inc, 'basic_average_shares', 'diluted_average_shares')
  const sharesOutstanding = sharesBS !== 0 ? sharesBS : sharesInc !== 0 ? sharesInc : undefined

  const year = String(item.fiscal_year ?? item.period_of_report_date?.slice(0, 4) ?? '')

  return {
    year,
    revenue,
    grossProfit,
    ebit,
    netIncome,
    totalAssets,
    totalEquity,
    totalDebt:          longTermDebt,
    cash,
    capex,
    depreciation,
    operatingCashFlow:  ocf,
    incomeTaxExpense:   taxExpense,
    ebt,
    interestExpense:    interestExp,
    currentAssets,
    currentLiabilities: currentLiab,
    accountsReceivable: ar,
    dividendsPaid:      dividendsPaid,
    ...(sharesOutstanding !== undefined ? { sharesOutstanding } : {}),
  }
}

/** Extract the first non-zero numeric value from a Polygon section by key priority. */
function _v(
  section: Record<string, _PolygonValue>,
  ...keys: string[]
): number {
  for (const k of keys) {
    const node = section[k]
    if (node && node.value != null) {
      const n = Number(node.value)
      if (!isNaN(n)) return n
    }
  }
  return 0
}

/** Return an ISO date string N years ago from today. */
function _startDate(years: number): string {
  const d = new Date()
  d.setFullYear(d.getFullYear() - years)
  return d.toISOString().slice(0, 10)
}
