/**
 * Market and price data types.
 */

export interface MarketData {
  /** Current stock price */
  price: number
  /** Total market capitalization */
  marketCap: number
  /** Shares outstanding */
  sharesOutstanding?: number | null
  /** Enterprise value (if pre-calculated) */
  enterpriseValue?: number | null
  /** Analyst forward EPS estimate */
  forwardEps?: number | null
  /** Trailing 12-month EPS */
  trailingEps?: number | null
  /** Annual dividend per share */
  dividendPerShare?: number | null
  /** 52-week high */
  high52Week?: number | null
  /** 52-week low */
  low52Week?: number | null
  /** Ticker symbol */
  ticker?: string
  /** As-of date */
  asOf?: string
}

export interface PricePoint {
  date: string
  /** Adjusted close price */
  close: number
  /** Trading volume */
  volume?: number | null
}

export type PriceHistory = PricePoint[]

export interface Return {
  date: string
  /** Decimal return, e.g. 0.05 for 5% */
  value: number
}

export type ReturnSeries = Return[]
