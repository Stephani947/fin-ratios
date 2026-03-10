import { safeDivide } from '../../utils/safe-divide.js'
import { stdDev, mean, percentile, maxDrawdown, pricesToReturns, annualizeReturn } from '../../utils/math.js'

// ── Beta ──────────────────────────────────────────────────────────────────────

export function beta(input: {
  stockReturns: number[]
  marketReturns: number[]
}): number | null {
  const { stockReturns, marketReturns } = input
  if (stockReturns.length !== marketReturns.length || stockReturns.length < 2) return null

  const n = stockReturns.length
  const meanStock = stockReturns.reduce((a, b) => a + b, 0) / n
  const meanMarket = marketReturns.reduce((a, b) => a + b, 0) / n

  let covariance = 0
  let varianceMarket = 0
  for (let i = 0; i < n; i++) {
    const ds = (stockReturns[i] ?? 0) - meanStock
    const dm = (marketReturns[i] ?? 0) - meanMarket
    covariance += ds * dm
    varianceMarket += dm * dm
  }

  return safeDivide(covariance, varianceMarket)
}
beta.formula = 'Cov(r_stock, r_market) / Var(r_market)'
beta.description = 'Sensitivity of stock returns to market returns. Beta = 1 means moves with market.'

// ── Jensen Alpha ──────────────────────────────────────────────────────────────

export function jensensAlpha(input: {
  portfolioReturn: number
  riskFreeRate: number
  beta: number
  marketReturn: number
}): number {
  return input.portfolioReturn - (input.riskFreeRate + input.beta * (input.marketReturn - input.riskFreeRate))
}
jensensAlpha.formula = 'Rp - [Rf + β × (Rm - Rf)]'
jensensAlpha.description = 'Excess return above what CAPM predicts. Positive = outperformance.'

// ── Sharpe Ratio ──────────────────────────────────────────────────────────────

export function sharpeRatio(input: {
  returns: number[]
  riskFreeRate: number
  periodsPerYear?: number
}): number | null {
  const { returns, riskFreeRate, periodsPerYear = 252 } = input
  const avgReturn = mean(returns)
  const vol = stdDev(returns, 1)
  if (avgReturn == null || vol == null || vol === 0) return null

  const annualizedReturn = annualizeReturn(avgReturn, periodsPerYear)
  const annualizedVol = vol * Math.sqrt(periodsPerYear)
  return safeDivide(annualizedReturn - riskFreeRate, annualizedVol)
}
sharpeRatio.formula = '(Annualized Return - Risk-Free Rate) / Annualized StdDev'
sharpeRatio.description = 'Risk-adjusted return per unit of total volatility. > 1 is good, > 2 is excellent.'

// ── Sortino Ratio ─────────────────────────────────────────────────────────────

export function sortinoRatio(input: {
  returns: number[]
  riskFreeRate: number
  mar?: number
  periodsPerYear?: number
}): number | null {
  const { returns, riskFreeRate, mar = 0, periodsPerYear = 252 } = input
  const avgReturn = mean(returns)
  if (avgReturn == null) return null

  const downsideReturns = returns.filter(r => r < mar)
  if (downsideReturns.length === 0) return null

  const downsideVariance = downsideReturns.reduce((sum, r) => sum + Math.pow(r - mar, 2), 0) / returns.length
  const downsideDeviation = Math.sqrt(downsideVariance) * Math.sqrt(periodsPerYear)
  if (downsideDeviation === 0) return null

  const annualizedReturn = annualizeReturn(avgReturn, periodsPerYear)
  return safeDivide(annualizedReturn - riskFreeRate, downsideDeviation)
}
sortinoRatio.formula = '(Annualized Return - Rf) / Downside Deviation'
sortinoRatio.description = 'Like Sharpe but penalizes only downside volatility. Better for asymmetric returns.'

// ── Treynor Ratio ─────────────────────────────────────────────────────────────

export function treynorRatio(input: {
  portfolioReturn: number
  riskFreeRate: number
  beta: number
}): number | null {
  return safeDivide(input.portfolioReturn - input.riskFreeRate, input.beta)
}
treynorRatio.formula = '(Portfolio Return - Risk-Free Rate) / Beta'
treynorRatio.description = 'Risk-adjusted return per unit of market (systematic) risk.'

// ── Calmar Ratio ─────────────────────────────────────────────────────────────

export function calmarRatio(input: {
  returns: number[]
  periodsPerYear?: number
}): number | null {
  const { returns, periodsPerYear = 252 } = input
  const avgReturn = mean(returns)
  if (avgReturn == null) return null

  const cumulative = returns.reduce((acc, r) => acc * (1 + r), 1)
  const prices = [1]
  let cur = 1
  for (const r of returns) {
    cur *= 1 + r
    prices.push(cur)
  }

  const mdd = maxDrawdown(prices)
  if (mdd == null || mdd === 0) return null

  const annualizedReturn = annualizeReturn(avgReturn, periodsPerYear)
  return safeDivide(annualizedReturn, mdd)
}
calmarRatio.formula = 'Annualized Return / Maximum Drawdown'
calmarRatio.description = 'Return relative to worst drawdown. Popular in hedge fund analysis.'

// ── Information Ratio ─────────────────────────────────────────────────────────

export function informationRatio(input: {
  portfolioReturns: number[]
  benchmarkReturns: number[]
}): number | null {
  const { portfolioReturns, benchmarkReturns } = input
  if (portfolioReturns.length !== benchmarkReturns.length) return null

  const activeReturns = portfolioReturns.map((r, i) => r - (benchmarkReturns[i] ?? 0))
  const avgActive = mean(activeReturns)
  const trackingErr = stdDev(activeReturns, 1)
  return safeDivide(avgActive, trackingErr)
}
informationRatio.formula = 'Mean Active Return / Tracking Error'
informationRatio.description = 'Skill of an active manager. IR > 0.5 is considered good.'

// ── Omega Ratio ───────────────────────────────────────────────────────────────

export function omegaRatio(input: {
  returns: number[]
  threshold?: number
}): number | null {
  const { returns, threshold = 0 } = input
  let gains = 0
  let losses = 0
  for (const r of returns) {
    if (r > threshold) gains += r - threshold
    else losses += threshold - r
  }
  return safeDivide(gains, losses)
}
omegaRatio.formula = 'E[returns above threshold] / E[returns below threshold]'
omegaRatio.description = 'Non-parametric risk-adjusted return. > 1 is desirable.'

// ── Max Drawdown ──────────────────────────────────────────────────────────────

export function maximumDrawdown(input: {
  prices: number[]
}): number | null {
  return maxDrawdown(input.prices)
}
maximumDrawdown.formula = '(Peak - Trough) / Peak'
maximumDrawdown.description = 'Largest peak-to-trough decline. Measures worst-case loss scenario.'

// ── Tracking Error ────────────────────────────────────────────────────────────

export function trackingError(input: {
  portfolioReturns: number[]
  benchmarkReturns: number[]
  periodsPerYear?: number
}): number | null {
  const { portfolioReturns, benchmarkReturns, periodsPerYear = 252 } = input
  if (portfolioReturns.length !== benchmarkReturns.length) return null

  const activeReturns = portfolioReturns.map((r, i) => r - (benchmarkReturns[i] ?? 0))
  const te = stdDev(activeReturns, 1)
  if (te == null) return null
  return te * Math.sqrt(periodsPerYear)
}
trackingError.formula = 'Annualized StdDev(Portfolio Returns - Benchmark Returns)'
trackingError.description = 'How closely a portfolio tracks its benchmark. Lower = more index-like.'

// ── VaR ───────────────────────────────────────────────────────────────────────

export function historicalVaR(input: {
  returns: number[]
  confidence?: number
}): number | null {
  const { returns, confidence = 0.95 } = input
  const p = percentile(returns, 1 - confidence)
  return p != null ? -p : null
}
historicalVaR.formula = '-Percentile(returns, 1 - confidence)'
historicalVaR.description = 'Historical VaR at given confidence level. Returns a positive loss value.'

export function parametricVaR(input: {
  returns: number[]
  confidence?: number
}): number | null {
  const { returns, confidence = 0.95 } = input
  const mu = mean(returns)
  const sigma = stdDev(returns, 1)
  if (mu == null || sigma == null) return null

  // Standard normal z-score for one-tailed
  const zScores: Record<number, number> = {
    0.90: 1.282,
    0.95: 1.645,
    0.99: 2.326,
    0.999: 3.090,
  }
  const z = zScores[confidence] ?? 1.645
  return -(mu - z * sigma)
}
parametricVaR.formula = '-(μ - z × σ)  where z is the normal quantile for confidence level'
parametricVaR.description = 'Parametric VaR assuming normal distribution.'

export function conditionalVaR(input: {
  returns: number[]
  confidence?: number
}): number | null {
  const { returns, confidence = 0.95 } = input
  const var_ = percentile(returns, 1 - confidence)
  if (var_ == null) return null

  const tailReturns = returns.filter(r => r <= var_)
  const cvar = mean(tailReturns)
  return cvar != null ? -cvar : null
}
conditionalVaR.formula = '-Mean(returns that are ≤ VaR threshold)'
conditionalVaR.description = 'CVaR / Expected Shortfall — average loss in the worst (1-confidence)% scenarios.'

// ── Ulcer Index ───────────────────────────────────────────────────────────────

export function ulcerIndex(input: {
  prices: number[]
}): number | null {
  const { prices } = input
  if (prices.length < 2) return null

  let peak = prices[0] ?? 0
  const drawdowns: number[] = []
  for (const p of prices) {
    if (p > peak) peak = p
    drawdowns.push(peak > 0 ? ((p - peak) / peak) * 100 : 0)
  }

  const meanSqDD = drawdowns.reduce((sum, d) => sum + d * d, 0) / drawdowns.length
  return Math.sqrt(meanSqDD)
}
ulcerIndex.formula = 'sqrt(mean(drawdown_pct^2))'
ulcerIndex.description = 'Measures drawdown depth and duration. Lower is less stressful.'

// ── Capture Ratios ────────────────────────────────────────────────────────────

export function upsideCaptureRatio(input: {
  portfolioReturns: number[]
  benchmarkReturns: number[]
}): number | null {
  const { portfolioReturns, benchmarkReturns } = input
  const upPeriods = benchmarkReturns
    .map((b, i) => ({ b, p: portfolioReturns[i] ?? 0 }))
    .filter(({ b }) => b > 0)

  if (upPeriods.length === 0) return null
  const portAvg = mean(upPeriods.map(x => x.p))
  const benchAvg = mean(upPeriods.map(x => x.b))
  return safeDivide(portAvg, benchAvg)
}
upsideCaptureRatio.formula = 'Portfolio Return (up markets) / Benchmark Return (up markets)'
upsideCaptureRatio.description = '> 100% means outperformed benchmark in up markets.'

export function downsideCaptureRatio(input: {
  portfolioReturns: number[]
  benchmarkReturns: number[]
}): number | null {
  const { portfolioReturns, benchmarkReturns } = input
  const downPeriods = benchmarkReturns
    .map((b, i) => ({ b, p: portfolioReturns[i] ?? 0 }))
    .filter(({ b }) => b < 0)

  if (downPeriods.length === 0) return null
  const portAvg = mean(downPeriods.map(x => x.p))
  const benchAvg = mean(downPeriods.map(x => x.b))
  return safeDivide(portAvg, benchAvg)
}
downsideCaptureRatio.formula = 'Portfolio Return (down markets) / Benchmark Return (down markets)'
downsideCaptureRatio.description = '< 100% means lost less than benchmark in down markets.'
