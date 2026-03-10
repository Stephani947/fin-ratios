import { safeDivide } from '../../utils/safe-divide.js'

// ── Piotroski F-Score ─────────────────────────────────────────────────────────

export interface PiotroskiInput {
  current: {
    netIncome: number
    totalAssets: number
    operatingCashFlow: number
    longTermDebt: number
    currentAssets: number
    currentLiabilities: number
    sharesOutstanding: number
    grossProfit: number
    revenue: number
  }
  prior: {
    netIncome: number
    totalAssets: number
    longTermDebt: number
    currentAssets: number
    currentLiabilities: number
    sharesOutstanding: number
    grossProfit: number
    revenue: number
  }
}

export interface PiotroskiResult {
  score: number
  signals: {
    // Profitability
    roa_positive: boolean
    ocf_positive: boolean
    roa_improving: boolean
    quality_earnings: boolean
    // Leverage / Liquidity
    lower_leverage: boolean
    higher_liquidity: boolean
    no_dilution: boolean
    // Operating Efficiency
    higher_gross_margin: boolean
    higher_asset_turnover: boolean
  }
  interpretation: string
}

export function piotroskiFScore(input: PiotroskiInput): PiotroskiResult {
  const { current, prior } = input

  const roaCurrent = (current.netIncome / current.totalAssets)
  const roaPrior = (prior.netIncome / prior.totalAssets)
  const leverageCurrent = current.totalAssets > 0 ? current.longTermDebt / current.totalAssets : 0
  const leveragePrior = prior.totalAssets > 0 ? prior.longTermDebt / prior.totalAssets : 0
  const crCurrent = current.currentLiabilities > 0 ? current.currentAssets / current.currentLiabilities : 0
  const crPrior = prior.currentLiabilities > 0 ? prior.currentAssets / prior.currentLiabilities : 0
  const gmCurrent = current.revenue > 0 ? current.grossProfit / current.revenue : 0
  const gmPrior = prior.revenue > 0 ? prior.grossProfit / prior.revenue : 0
  const atCurrent = current.totalAssets > 0 ? current.revenue / current.totalAssets : 0
  const atPrior = prior.totalAssets > 0 ? prior.revenue / prior.totalAssets : 0

  const signals = {
    // F1: ROA positive
    roa_positive: roaCurrent > 0,
    // F2: Operating cash flow positive
    ocf_positive: current.operatingCashFlow > 0,
    // F3: ROA improving year over year
    roa_improving: roaCurrent > roaPrior,
    // F4: Accruals — OCF > NI (quality earnings, cash-backed)
    quality_earnings: current.operatingCashFlow > current.netIncome,
    // F5: Long-term debt / assets ratio declined
    lower_leverage: leverageCurrent < leveragePrior,
    // F6: Current ratio improved
    higher_liquidity: crCurrent > crPrior,
    // F7: No new shares issued (dilution)
    no_dilution: current.sharesOutstanding <= prior.sharesOutstanding,
    // F8: Gross margin improved
    higher_gross_margin: gmCurrent > gmPrior,
    // F9: Asset turnover improved
    higher_asset_turnover: atCurrent > atPrior,
  }

  const score = Object.values(signals).filter(Boolean).length

  let interpretation = ''
  if (score >= 8) interpretation = 'Strong (8-9): High financial strength, potential value opportunity'
  else if (score >= 6) interpretation = 'Good (6-7): Reasonably healthy fundamentals'
  else if (score >= 4) interpretation = 'Neutral (4-5): Mixed signals, further analysis needed'
  else interpretation = 'Weak (0-3): Multiple red flags, high risk'

  return { score, signals, interpretation }
}
piotroskiFScore.formula = '9 binary signals across Profitability, Leverage/Liquidity, Operating Efficiency'
piotroskiFScore.description = 'F-Score 0-9. >= 8 is strong buy signal. <= 2 is short signal.'

// ── Altman Z-Score ────────────────────────────────────────────────────────────

export interface AltmanInput {
  workingCapital: number
  retainedEarnings: number
  ebit: number
  marketCap: number
  totalLiabilities: number
  totalAssets: number
  revenue: number
}

export interface AltmanResult {
  z: number
  x1: number
  x2: number
  x3: number
  x4: number
  x5: number
  zone: 'safe' | 'grey' | 'distress'
  interpretation: string
}

export function altmanZScore(input: AltmanInput): AltmanResult | null {
  if (input.totalAssets === 0 || input.totalLiabilities === 0) return null

  const x1 = input.workingCapital / input.totalAssets
  const x2 = input.retainedEarnings / input.totalAssets
  const x3 = input.ebit / input.totalAssets
  const x4 = input.marketCap / input.totalLiabilities
  const x5 = input.revenue / input.totalAssets

  const z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

  let zone: 'safe' | 'grey' | 'distress'
  let interpretation: string
  if (z > 2.99) {
    zone = 'safe'
    interpretation = 'Safe zone (Z > 2.99): Low probability of bankruptcy'
  } else if (z > 1.81) {
    zone = 'grey'
    interpretation = 'Grey zone (1.81 < Z < 2.99): Uncertain, monitor closely'
  } else {
    zone = 'distress'
    interpretation = 'Distress zone (Z < 1.81): High probability of financial distress'
  }

  return { z, x1, x2, x3, x4, x5, zone, interpretation }
}
altmanZScore.formula = '1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5 (public manufacturing)'
altmanZScore.description = 'Bankruptcy prediction model. Safe > 2.99, Distress < 1.81.'

// ── Beneish M-Score ───────────────────────────────────────────────────────────

export interface BeneishInput {
  current: {
    revenue: number
    accountsReceivable: number
    grossProfit: number
    totalAssets: number
    depreciation: number
    ppGross: number
    sgaExpense: number
    totalDebt: number
    netIncome: number
    cashFlowFromOps: number
  }
  prior: {
    revenue: number
    accountsReceivable: number
    grossProfit: number
    totalAssets: number
    depreciation: number
    ppGross: number
    sgaExpense: number
    totalDebt: number
  }
}

export interface BeneishResult {
  mScore: number
  variables: {
    dsri: number
    gmi: number
    aqi: number
    sgi: number
    depi: number
    sgai: number
    lvgi: number
    tata: number
  }
  manipulationLikely: boolean
  interpretation: string
}

export function beneishMScore(input: BeneishInput): BeneishResult | null {
  const { current: c, prior: p } = input

  if (p.revenue === 0 || p.totalAssets === 0 || p.grossProfit === 0) return null

  // DSRI: Days Sales Receivable Index
  const dsri = safeDivide(
    safeDivide(c.accountsReceivable, c.revenue),
    safeDivide(p.accountsReceivable, p.revenue)
  )
  // GMI: Gross Margin Index
  const gmi = safeDivide(
    safeDivide(p.grossProfit, p.revenue),
    safeDivide(c.grossProfit, c.revenue)
  )
  // AQI: Asset Quality Index
  const aqiCurrent = c.totalAssets > 0
    ? 1 - (c.accountsReceivable + c.ppGross + c.cashFlowFromOps) / c.totalAssets
    : null
  const aqiPrior = p.totalAssets > 0
    ? 1 - (p.accountsReceivable + p.ppGross) / p.totalAssets
    : null
  const aqi = safeDivide(aqiCurrent, aqiPrior)
  // SGI: Sales Growth Index
  const sgi = safeDivide(c.revenue, p.revenue)
  // DEPI: Depreciation Index
  const depiCurrent = c.ppGross > 0 ? c.depreciation / (c.depreciation + c.ppGross) : null
  const depiPrior = p.ppGross > 0 ? p.depreciation / (p.depreciation + p.ppGross) : null
  const depi = safeDivide(depiPrior, depiCurrent)
  // SGAI: SG&A Expense Index
  const sgai = safeDivide(
    safeDivide(c.sgaExpense, c.revenue),
    safeDivide(p.sgaExpense, p.revenue)
  )
  // LVGI: Leverage Index
  const lvgi = safeDivide(
    safeDivide(c.totalDebt, c.totalAssets),
    safeDivide(p.totalDebt, p.totalAssets)
  )
  // TATA: Total Accruals to Total Assets
  const tata = c.totalAssets > 0
    ? (c.netIncome - c.cashFlowFromOps) / c.totalAssets
    : null

  if (
    dsri == null || gmi == null || aqi == null || sgi == null ||
    depi == null || sgai == null || lvgi == null || tata == null
  ) return null

  const mScore =
    -4.84 +
    0.92 * dsri +
    0.528 * gmi +
    0.404 * aqi +
    0.892 * sgi +
    0.115 * depi -
    0.172 * sgai +
    4.679 * tata -
    0.327 * lvgi

  const manipulationLikely = mScore > -2.22

  return {
    mScore,
    variables: { dsri, gmi, aqi, sgi, depi, sgai, lvgi, tata },
    manipulationLikely,
    interpretation: manipulationLikely
      ? `M-Score ${mScore.toFixed(2)} > -2.22: Possible earnings manipulation`
      : `M-Score ${mScore.toFixed(2)} ≤ -2.22: No strong sign of manipulation`,
  }
}
beneishMScore.formula = '-4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI + 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI'
beneishMScore.description = 'Earnings manipulation detector. M-Score > -2.22 indicates likely manipulation.'

// ── Greenblatt Magic Formula ───────────────────────────────────────────────────

export interface MagicFormulaResult {
  roic: number | null
  evEbit: number | null
}

export function magicFormula(input: {
  ebit: number
  netWorkingCapital: number
  netFixedAssets: number
  enterpriseValue: number
}): MagicFormulaResult {
  const tangibleCapital = input.netWorkingCapital + input.netFixedAssets
  return {
    roic: safeDivide(input.ebit, tangibleCapital),
    evEbit: safeDivide(input.enterpriseValue, input.ebit),
  }
}
magicFormula.formula = 'ROIC = EBIT / (Net Working Capital + Net Fixed Assets); Earnings Yield = EBIT / EV'
magicFormula.description = 'Greenblatt\'s Magic Formula: rank by ROIC + EV/EBIT. Best combo = buy.'

// ── Ohlson O-Score ────────────────────────────────────────────────────────────

export interface OhlsonInput {
  totalAssets: number
  totalLiabilities: number
  currentAssets: number
  currentLiabilities: number
  netIncome: number
  priorNetIncome: number
  operatingCashFlow: number
  workingCapital: number
  gnp: number // GNP price level index, often approximated as 1
}

export function ohlsonOScore(input: OhlsonInput): { oScore: number; bankruptcyProbability: number; interpretation: string } | null {
  if (input.totalAssets <= 0) return null

  const t1 = -1.32 - 0.407 * Math.log(input.totalAssets / input.gnp)
  const t2 = 6.03 * (input.totalLiabilities / input.totalAssets)
  const t3 = -1.43 * (input.workingCapital / input.totalAssets)
  const t4 = 0.0757 * (input.currentLiabilities / input.currentAssets)
  const t5 = input.totalLiabilities > input.totalAssets ? -1.72 * 1 : 0
  const t6 = -2.37 * (input.netIncome / input.totalAssets)
  const t7 = -1.83 * (input.operatingCashFlow / input.totalAssets)
  const t8 =
    0.285 * ((input.netIncome + input.priorNetIncome < 0) ? 1 : 0)
  const t9 =
    -0.521 *
    safeDivide(
      input.netIncome - input.priorNetIncome,
      Math.abs(input.netIncome) + Math.abs(input.priorNetIncome)
    )!

  const oScore = t1 + t2 + t3 + t4 + t5 + t6 + t7 + t8 + t9
  const bankruptcyProbability = 1 / (1 + Math.exp(-oScore))

  return {
    oScore,
    bankruptcyProbability,
    interpretation: bankruptcyProbability > 0.5
      ? `High bankruptcy risk (${(bankruptcyProbability * 100).toFixed(1)}% probability)`
      : `Low bankruptcy risk (${(bankruptcyProbability * 100).toFixed(1)}% probability)`,
  }
}
ohlsonOScore.formula = 'Logistic regression: -1.32 - 0.407*SIZE + 6.03*TLTA - 1.43*WCTA + 0.0757*CLCA ...'
ohlsonOScore.description = 'Bankruptcy prediction via logistic regression. Outputs probability 0-1.'

// ── Montier C-Score ────────────────────────────────────────────────────────────

export interface MontierCInput {
  current: {
    netIncome: number
    operatingCashFlow: number
    accountsReceivable: number
    revenue: number
    inventory: number
    cogs: number
    cash: number
    totalAssets: number
    longTermDebt: number
    grossProfit: number
  }
  prior: {
    accountsReceivable: number
    revenue: number
    inventory: number
    cogs: number
    cash: number
    totalAssets: number
    longTermDebt: number
    grossProfit: number
  }
}

export interface MontierCResult {
  score: number
  signals: {
    c1Accruals: boolean
    c2DsoIncreasing: boolean
    c3InventoryDaysIncreasing: boolean
    c4CashDeclining: boolean
    c5LeverageIncreasing: boolean
    c6GrossMarginDeclining: boolean
  }
  highRisk: boolean
  interpretation: string
}

/**
 * Montier C-Score (Earnings Quality / Creative Accounting Score).
 *
 * 6 binary signals — higher score = more red flags = lower earnings quality.
 *
 * Reference: Montier, J. (2008). Joining the Dark Side: Pirates, Spies and Short Sellers.
 *            Société Générale Cross Asset Research.
 */
export function montierCScore(input: MontierCInput): MontierCResult {
  const { current: c, prior: p } = input

  // C1: Net income > Operating cash flow (accrual-based earnings)
  const c1Accruals = c.netIncome > c.operatingCashFlow

  // C2: Days sales outstanding increasing
  const dsoCurrent = c.revenue > 0 ? c.accountsReceivable / c.revenue : 0
  const dsoPrior = p.revenue > 0 ? p.accountsReceivable / p.revenue : 0
  const c2DsoIncreasing = dsoCurrent > dsoPrior

  // C3: Days inventory outstanding increasing
  const dioCurrent = c.cogs > 0 ? c.inventory / c.cogs : 0
  const dioPrior = p.cogs > 0 ? p.inventory / p.cogs : 0
  const c3InventoryDaysIncreasing = dioCurrent > dioPrior

  // C4: Cash declining as % of total assets
  const cashPctCurrent = c.totalAssets > 0 ? c.cash / c.totalAssets : 0
  const cashPctPrior = p.totalAssets > 0 ? p.cash / p.totalAssets : 0
  const c4CashDeclining = cashPctCurrent < cashPctPrior

  // C5: Long-term debt increasing as % of total assets
  const ltdPctCurrent = c.totalAssets > 0 ? c.longTermDebt / c.totalAssets : 0
  const ltdPctPrior = p.totalAssets > 0 ? p.longTermDebt / p.totalAssets : 0
  const c5LeverageIncreasing = ltdPctCurrent > ltdPctPrior

  // C6: Gross margin declining
  const gmCurrent = c.revenue > 0 ? c.grossProfit / c.revenue : 0
  const gmPrior = p.revenue > 0 ? p.grossProfit / p.revenue : 0
  const c6GrossMarginDeclining = gmCurrent < gmPrior

  const signals = {
    c1Accruals,
    c2DsoIncreasing,
    c3InventoryDaysIncreasing,
    c4CashDeclining,
    c5LeverageIncreasing,
    c6GrossMarginDeclining,
  }

  const score = Object.values(signals).filter(Boolean).length
  const highRisk = score >= 4

  let interpretation: string
  if (score <= 1) interpretation = `C-Score ${score}/6: High earnings quality — few red flags`
  else if (score <= 3) interpretation = `C-Score ${score}/6: Moderate concern — review signals carefully`
  else interpretation = `C-Score ${score}/6: Significant red flags — possible earnings management`

  return { score, signals, highRisk, interpretation }
}

montierCScore.formula = '6 binary signals: accruals, DSO, inventory days, cash%, long-term debt%, gross margin'
montierCScore.description = 'Earnings quality score 0-6. Higher = more red flags. 4+ signals = high risk.'
