/**
 * React hooks for fin-ratios.
 *
 * Optional sub-path export: import from 'fin-ratios/hooks'
 *
 * NOTE: These hooks require React as a peer dependency.
 *       They are designed for client-side use in React applications.
 *
 * Usage:
 *   import { useRatios, useHealthScore, useRatioHistory } from 'fin-ratios/hooks'
 *
 *   function StockCard({ ticker }) {
 *     const { data, loading, error } = useRatios(ticker)
 *     if (loading) return <Spinner />
 *     if (error) return <Error message={error} />
 *     return <div>P/E: {data?.pe?.toFixed(1)}</div>
 *   }
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import type { RatioResults, FinancialData } from '../utils/compute-all.js'
import { computeAll } from '../utils/compute-all.js'
import type { ScenarioDcfInput, ScenarioDcfResult } from '../utils/scenario-dcf.js'
import { scenarioDcf } from '../utils/scenario-dcf.js'

// ── Types ──────────────────────────────────────────────────────────────────────

export interface UseRatiosState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export type FetcherFn<T> = (ticker: string) => Promise<T>

// ── useRatios ─────────────────────────────────────────────────────────────────

/**
 * Fetch and compute all financial ratios for a ticker.
 *
 * @param ticker    Stock ticker (e.g. 'AAPL'). Pass null/undefined to skip.
 * @param fetcher   Async function that fetches raw financial data. Must be
 *                  stable across renders (wrap in useCallback if needed).
 *
 * @example
 *   import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'
 *
 *   const { data, loading, error } = useRatios('AAPL', fetchYahoo)
 *   console.log(data?.grossMargin)   // 0.433
 *   console.log(data?.roic)          // 0.55
 */
export function useRatios<TRaw extends FinancialData>(
  ticker: string | null | undefined,
  fetcher: FetcherFn<TRaw>,
): UseRatiosState<RatioResults> {
  const [state, setState] = useState<UseRatiosState<RatioResults>>({
    data: null,
    loading: false,
    error: null,
    refetch: () => {},
  })

  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const fetch = useCallback(() => {
    if (!ticker) return

    setState((s: UseRatiosState<RatioResults>) => ({ ...s, loading: true, error: null }))

    fetcherRef.current(ticker)
      .then((raw: TRaw) => {
        const ratios = computeAll(raw)
        setState({ data: ratios, loading: false, error: null, refetch: fetch })
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : String(err)
        setState((s: UseRatiosState<RatioResults>) => ({ ...s, loading: false, error: message }))
      })
  }, [ticker])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { ...state, refetch: fetch }
}

// ── useRatio ──────────────────────────────────────────────────────────────────

/**
 * Fetch a single named ratio for a ticker.
 *
 * @param ticker   Stock ticker
 * @param ratio    Ratio name (key of RatioResults)
 * @param fetcher  Financial data fetcher function
 *
 * @example
 *   const { data: pe } = useRatio('AAPL', 'pe', fetchYahoo)
 */
export function useRatio<TRaw extends FinancialData, K extends keyof RatioResults>(
  ticker: string | null | undefined,
  ratio: K,
  fetcher: FetcherFn<TRaw>,
): UseRatiosState<RatioResults[K]> {
  const ratiosState = useRatios(ticker, fetcher)
  return {
    data: ratiosState.data ? ratiosState.data[ratio] ?? null : null,
    loading: ratiosState.loading,
    error: ratiosState.error,
    refetch: ratiosState.refetch,
  }
}

// ── useHealthScore ────────────────────────────────────────────────────────────

/**
 * Simplified hook that returns a normalized health score (0–100) based on
 * the computed ratios. Clients provide their own scoring function.
 *
 * @param ticker     Stock ticker
 * @param fetcher    Financial data fetcher
 * @param scoreFn    Custom function: (ratios: RatioResults) => number
 *
 * @example
 *   const { data: score } = useHealthScore('AAPL', fetchYahoo, (r) => {
 *     let s = 50
 *     if (r.roic && r.roic > 0.15) s += 20
 *     if (r.grossMargin && r.grossMargin > 0.4) s += 15
 *     if (r.currentRatio && r.currentRatio > 2) s += 15
 *     return Math.min(s, 100)
 *   })
 */
export function useHealthScore<TRaw extends FinancialData>(
  ticker: string | null | undefined,
  fetcher: FetcherFn<TRaw>,
  scoreFn: (ratios: RatioResults) => number,
): UseRatiosState<number> {
  const ratiosState = useRatios(ticker, fetcher)
  const score = ratiosState.data ? scoreFn(ratiosState.data) : null
  return {
    data: score,
    loading: ratiosState.loading,
    error: ratiosState.error,
    refetch: ratiosState.refetch,
  }
}

// ── useScenarioDcf ────────────────────────────────────────────────────────────

/**
 * Compute scenario DCF analysis reactively.
 *
 * @param input  ScenarioDcfInput (baseFcf, shares, currentPrice, scenarios)
 *
 * @example
 *   const { data } = useScenarioDcf({
 *     baseFcf: 100e9,
 *     sharesOutstanding: 15.7e9,
 *     currentPrice: 185,
 *   })
 *   console.log(data?.base.upsidePct)  // 0.074
 */
export function useScenarioDcf(
  input: ScenarioDcfInput | null,
): { data: ScenarioDcfResult | null } {
  const [data, setData] = useState<ScenarioDcfResult | null>(null)

  useEffect(() => {
    if (!input) {
      setData(null)
      return
    }
    setData(scenarioDcf(input))
  }, [
    input?.baseFcf,
    input?.sharesOutstanding,
    input?.currentPrice,
  ])

  return { data }
}

// ── useCompareRatios ──────────────────────────────────────────────────────────

/**
 * Fetch and compare ratios for multiple tickers in parallel.
 *
 * @param tickers  Array of ticker symbols
 * @param fetcher  Financial data fetcher
 *
 * @example
 *   const { data } = useCompareRatios(['AAPL', 'MSFT', 'GOOGL'], fetchYahoo)
 *   console.log(data?.AAPL?.grossMargin)  // 0.433
 *   console.log(data?.MSFT?.grossMargin)  // 0.695
 */
export function useCompareRatios<TRaw extends FinancialData>(
  tickers: string[],
  fetcher: FetcherFn<TRaw>,
): UseRatiosState<Record<string, RatioResults>> {
  const [state, setState] = useState<UseRatiosState<Record<string, RatioResults>>>({
    data: null,
    loading: false,
    error: null,
    refetch: () => {},
  })

  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const tickersKey = tickers.join(',')

  const fetch = useCallback(() => {
    if (!tickers.length) return

    setState((s: UseRatiosState<Record<string, RatioResults>>) => ({ ...s, loading: true, error: null }))

    Promise.allSettled(tickers.map(t => fetcherRef.current(t).then((raw: TRaw) => [t, computeAll(raw)] as const)))
      .then((results: PromiseSettledResult<readonly [string, RatioResults]>[]) => {
        const data: Record<string, RatioResults> = {}
        for (const result of results) {
          if (result.status === 'fulfilled') {
            const [ticker, ratios] = result.value
            data[ticker] = ratios
          }
        }
        setState({ data, loading: false, error: null, refetch: fetch })
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : String(err)
        setState((s: UseRatiosState<Record<string, RatioResults>>) => ({ ...s, loading: false, error: message }))
      })
  }, [tickersKey]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    fetch()
  }, [fetch])

  return { ...state, refetch: fetch }
}
