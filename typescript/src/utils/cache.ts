/**
 * In-memory caching layer for fin-ratios fetchers.
 *
 * Prevents redundant network calls and respects API rate limits.
 *
 * Usage:
 *   import { setCache, cached, clearCache } from 'fin-ratios/utils/cache'
 *
 *   setCache({ ttlMs: 60 * 60 * 1000 })  // 1 hour TTL
 *
 *   const fetchCached = cached('yahoo', fetchYahoo)
 *   const data = await fetchCached('AAPL')  // first call: network
 *   const data2 = await fetchCached('AAPL') // instant from cache
 */

export interface CacheOptions {
  /** Time-to-live in milliseconds (default: 24 hours) */
  ttlMs?: number
  /** Maximum number of entries before eviction (default: 500) */
  maxSize?: number
}

interface CacheEntry<T> {
  expiry: number
  value: T
}

let _ttlMs = 24 * 60 * 60 * 1000
let _maxSize = 500
const _store = new Map<string, CacheEntry<unknown>>()

/**
 * Configure the global cache settings.
 *
 * @example
 *   setCache({ ttlMs: 60 * 60 * 1000 }) // 1 hour
 *   setCache({ ttlMs: 0 })               // disable (TTL = 0 means no caching)
 */
export function setCache(options: CacheOptions): void {
  if (options.ttlMs !== undefined) _ttlMs = options.ttlMs
  if (options.maxSize !== undefined) _maxSize = options.maxSize
}

/**
 * Wrap an async fetcher function with transparent caching.
 *
 * The cache key is derived from the namespace + all arguments (JSON-serialized).
 *
 * @param namespace  A unique prefix for this fetcher (e.g. 'yahoo', 'edgar')
 * @param fn         The async function to wrap
 * @returns          The wrapped function with identical signature
 *
 * @example
 *   const fetchYahooCached = cached('yahoo', fetchYahoo)
 *   const data = await fetchYahooCached('AAPL')
 */
export function cached<TArgs extends unknown[], TReturn>(
  namespace: string,
  fn: (...args: TArgs) => Promise<TReturn>,
): (...args: TArgs) => Promise<TReturn> {
  return async (...args: TArgs): Promise<TReturn> => {
    if (_ttlMs === 0) return fn(...args)

    const key = _makeKey(namespace, args)
    const entry = _store.get(key) as CacheEntry<TReturn> | undefined

    if (entry && entry.expiry > Date.now()) {
      return entry.value
    }

    const value = await fn(...args)
    _evict()
    _store.set(key, { expiry: Date.now() + _ttlMs, value })
    return value
  }
}

/** Remove all cached entries. */
export function clearCache(): void {
  _store.clear()
}

/**
 * Remove cached entries for a specific ticker (case-insensitive).
 * Returns the number of entries removed.
 */
export function invalidate(ticker: string): number {
  const lower = ticker.toLowerCase()
  let removed = 0
  for (const [key] of _store) {
    if (key.includes(lower)) {
      _store.delete(key)
      removed++
    }
  }
  return removed
}

/** Return cache statistics. */
export function cacheStats(): { total: number; valid: number; ttlMs: number; maxSize: number } {
  const now = Date.now()
  let valid = 0
  for (const entry of _store.values()) {
    if ((entry as CacheEntry<unknown>).expiry > now) valid++
  }
  return { total: _store.size, valid, ttlMs: _ttlMs, maxSize: _maxSize }
}

// ── internals ──────────────────────────────────────────────────────────────────

function _makeKey(namespace: string, args: unknown[]): string {
  return `${namespace}:${JSON.stringify(args)}`
}

function _evict(): void {
  if (_store.size < _maxSize) return
  const now = Date.now()
  // First evict expired entries
  for (const [key, entry] of _store) {
    if ((entry as CacheEntry<unknown>).expiry <= now) {
      _store.delete(key)
    }
  }
  // If still over limit, evict oldest entries
  if (_store.size >= _maxSize) {
    const oldest = Array.from(_store.keys()).slice(0, Math.floor(_maxSize * 0.2))
    for (const key of oldest) _store.delete(key)
  }
}
