export type {
  IncomeStatement,
  BalanceSheet,
  CashFlowStatement,
  FinancialStatements,
} from './financials.js'

export type {
  MarketData,
  PricePoint,
  PriceHistory,
  Return,
  ReturnSeries,
} from './market.js'

/** A ratio function that also exposes its formula string. */
export type RatioFn<TInput, TOutput> = ((input: TInput) => TOutput) & {
  formula: string
  description: string
}
