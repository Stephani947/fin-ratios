/**
 * Core financial statement types.
 * All monetary values should be in the same currency unit (e.g., USD thousands).
 * Use null for unavailable/inapplicable fields.
 */

export interface IncomeStatement {
  /** Total revenue / net sales */
  revenue: number
  /** Revenue minus cost of goods sold */
  grossProfit: number
  /** Cost of goods sold */
  cogs: number
  /** Earnings before interest and taxes */
  ebit: number
  /** EBIT + Depreciation + Amortization */
  ebitda: number
  /** Net income after all expenses and taxes */
  netIncome: number
  /** Interest expense (positive = expense) */
  interestExpense: number
  /** Income tax expense */
  incomeTaxExpense: number
  /** Earnings before taxes */
  ebt: number
  /** Depreciation and amortization */
  depreciationAndAmortization: number
  /** Research and development expense */
  researchAndDevelopment?: number | null
  /** Selling, general and administrative expense */
  sgaExpense?: number | null
  /** Basic shares outstanding */
  sharesOutstanding: number
  /** Diluted shares outstanding */
  sharesOutstandingDiluted?: number | null
  /** Earnings per share (basic) */
  eps?: number | null
  /** Earnings per share (diluted) */
  epsDiluted?: number | null
  /** Fiscal period label, e.g. "2024-Q1" or "FY2023" */
  period?: string
}

export interface BalanceSheet {
  // Assets
  /** Total assets */
  totalAssets: number
  /** Current assets */
  currentAssets: number
  /** Cash and cash equivalents */
  cash: number
  /** Short-term investments */
  shortTermInvestments?: number | null
  /** Accounts receivable */
  accountsReceivable: number
  /** Inventory */
  inventory: number
  /** Net PP&E (property, plant, equipment) */
  netPPE: number
  /** Goodwill */
  goodwill?: number | null
  /** Intangible assets (excluding goodwill) */
  intangibleAssets?: number | null
  /** Retained earnings */
  retainedEarnings: number

  // Liabilities
  /** Total liabilities */
  totalLiabilities: number
  /** Current liabilities */
  currentLiabilities: number
  /** Accounts payable */
  accountsPayable: number
  /** Short-term debt */
  shortTermDebt?: number | null
  /** Long-term debt */
  longTermDebt: number
  /** Total debt (short-term + long-term) */
  totalDebt: number

  // Equity
  /** Total shareholders' equity */
  totalEquity: number
  /** Number of shares outstanding */
  sharesOutstanding?: number | null

  period?: string
}

export interface CashFlowStatement {
  /** Cash from operating activities */
  operatingCashFlow: number
  /** Capital expenditures (positive = spending, negative also common) */
  capex: number
  /** Cash from investing activities */
  investingCashFlow?: number | null
  /** Cash from financing activities */
  financingCashFlow?: number | null
  /** Net change in cash */
  netChangeInCash?: number | null
  /** Stock-based compensation */
  stockBasedCompensation?: number | null
  /** Dividends paid */
  dividendsPaid?: number | null
  /** Debt repayments */
  debtRepayments?: number | null
  /** Debt issuance */
  debtIssuance?: number | null
  /** Depreciation and amortization (from cash flow statement) */
  depreciationAndAmortization?: number | null

  period?: string
}

/**
 * Convenience bundle of all three statements for a single period.
 */
export interface FinancialStatements {
  income: IncomeStatement
  balance: BalanceSheet
  cashFlow: CashFlowStatement
}
