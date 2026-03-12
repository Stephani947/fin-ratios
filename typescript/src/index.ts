// ── Types ─────────────────────────────────────────────────────────────────────
export type {
  IncomeStatement,
  BalanceSheet,
  CashFlowStatement,
  FinancialStatements,
  MarketData,
  PriceHistory,
  PricePoint,
  Return,
  ReturnSeries,
  RatioFn,
} from './types/index.js'

// ── Valuation ─────────────────────────────────────────────────────────────────
export {
  pe,
  forwardPe,
  peg,
  pb,
  ps,
  pFcf,
  enterpriseValue,
  evEbitda,
  evEbit,
  evRevenue,
  evFcf,
  evInvestedCapital,
  tobinsQ,
  grahamNumber,
  grahamIntrinsicValue,
} from './ratios/valuation/index.js'

export {
  dcf2Stage,
  gordonGrowthModel,
  reverseDcf,
} from './ratios/valuation/dcf.js'

// ── Profitability ─────────────────────────────────────────────────────────────
export {
  grossMargin,
  operatingMargin,
  ebitdaMargin,
  netProfitMargin,
  nopatMargin,
  roe,
  roa,
  nopat,
  roic,
  roce,
  rote,
  duPont3,
  revenuePerEmployee,
  profitPerEmployee,
  investedCapital,
} from './ratios/profitability/index.js'

export type { DuPont3Factor } from './ratios/profitability/index.js'

// ── Liquidity ─────────────────────────────────────────────────────────────────
export {
  currentRatio,
  quickRatio,
  cashRatio,
  operatingCashFlowRatio,
  dso,
  dio,
  dpo,
  cashConversionCycle,
  defensiveIntervalRatio,
} from './ratios/liquidity/index.js'

// ── Solvency ──────────────────────────────────────────────────────────────────
export {
  debtToEquity,
  netDebtToEquity,
  netDebtToEbitda,
  debtToAssets,
  debtToCapital,
  interestCoverageRatio,
  ebitdaCoverageRatio,
  debtServiceCoverageRatio,
  fixedChargeCoverageRatio,
  equityMultiplier,
} from './ratios/solvency/index.js'

// ── Efficiency ────────────────────────────────────────────────────────────────
export {
  assetTurnover,
  fixedAssetTurnover,
  inventoryTurnover,
  receivablesTurnover,
  payablesTurnover,
  workingCapitalTurnover,
  capitalTurnover,
  operatingLeverage,
} from './ratios/efficiency/index.js'

// ── Cash Flow ─────────────────────────────────────────────────────────────────
export {
  freeCashFlow,
  leveredFcf,
  unleveredFcf,
  ownerEarnings,
  fcfYield,
  fcfMargin,
  fcfConversion,
  ocfToSales,
  capexToRevenue,
  capexToDepreciation,
  cashReturnOnAssets,
} from './ratios/cashflow/index.js'

// ── Growth ────────────────────────────────────────────────────────────────────
export {
  revenueGrowth,
  revenueCAGR,
  epsGrowth,
  ebitdaGrowth,
  fcfGrowth,
  bvpsGrowth,
  dividendGrowthRate,
  earningsPowerValue,
} from './ratios/growth/index.js'

// ── Risk / Portfolio ──────────────────────────────────────────────────────────
export {
  beta,
  jensensAlpha,
  sharpeRatio,
  sortinoRatio,
  treynorRatio,
  calmarRatio,
  informationRatio,
  omegaRatio,
  maximumDrawdown,
  trackingError,
  historicalVaR,
  parametricVaR,
  conditionalVaR,
  ulcerIndex,
  upsideCaptureRatio,
  downsideCaptureRatio,
} from './ratios/risk/index.js'

// ── Composite Scores ──────────────────────────────────────────────────────────
export {
  piotroskiFScore,
  altmanZScore,
  beneishMScore,
  magicFormula,
  ohlsonOScore,
  montierCScore,
} from './ratios/composite/index.js'

export type {
  PiotroskiInput,
  PiotroskiResult,
  AltmanInput,
  AltmanResult,
  BeneishInput,
  BeneishResult,
  MagicFormulaResult,
  OhlsonInput,
  MontierCInput,
  MontierCResult,
} from './ratios/composite/index.js'

// ── Sector: SaaS ──────────────────────────────────────────────────────────────
export {
  ruleOf40,
  magicNumber,
  netRevenueRetention,
  grossRevenueRetention,
  customerAcquisitionCost,
  customerLifetimeValue,
  ltvCacRatio,
  cacPaybackPeriod,
  burnMultiple,
  saasQuickRatio,
  arrPerFte,
} from './ratios/sector/saas/index.js'

// ── Sector: REIT ──────────────────────────────────────────────────────────────
export {
  ffo,
  affo,
  pFfo,
  pAffo,
  netOperatingIncome,
  capRate,
  occupancyRate,
} from './ratios/sector/reit/index.js'

// ── Sector: Banking ───────────────────────────────────────────────────────────
export {
  netInterestMargin,
  efficiencyRatio,
  loanToDepositRatio,
  nplRatio,
  provisionCoverageRatio,
  tier1CapitalRatio,
  cet1Ratio,
  tangibleBookValuePerShare,
} from './ratios/sector/banking/index.js'

// ── Sector: Insurance ─────────────────────────────────────────────────────────
export {
  lossRatio,
  expenseRatio,
  combinedRatio,
  underwritingProfitMargin,
  premiumsToSurplus,
} from './ratios/sector/insurance/index.js'

// ── Utils (public) ────────────────────────────────────────────────────────────
export { safeDivide } from './utils/safe-divide.js'
export {
  cagr,
  stdDev,
  mean,
  percentile,
  maxDrawdown,
  pricesToReturns,
  annualizeReturn,
} from './utils/math.js'

export { computeAll } from './utils/compute-all.js'
export type { FinancialData, RatioResults } from './utils/compute-all.js'

export { scenarioDcf } from './utils/scenario-dcf.js'
export type { ScenarioDcfInput, ScenarioDcfResult, ScenarioParams, ScenarioResult } from './utils/scenario-dcf.js'

export {
  setCache,
  cached,
  clearCache,
  invalidate as invalidateCache,
  cacheStats,
} from './utils/cache.js'
export type { CacheOptions } from './utils/cache.js'

export { moatScore } from './utils/moat-score.js'
export type {
  AnnualFinancialData,
  MoatComponents,
  MoatScoreResult,
  MoatScoreOptions,
} from './utils/moat-score.js'

export { capitalAllocationScore } from './utils/capital-allocation.js'
export type {
  AnnualCapitalData,
  CapitalAllocationComponents,
  CapitalAllocationResult,
  CapitalAllocationOptions,
} from './utils/capital-allocation.js'

export { earningsQualityScore } from './utils/earnings-quality.js'
export type {
  AnnualEarningsData,
  EarningsQualityComponents,
  EarningsQualityResult,
  EarningsQualityOptions,
} from './utils/earnings-quality.js'

export { fairValueRange } from './utils/fair-value.js'
export type {
  FairValueOptions,
  FairValueRange,
} from './utils/fair-value.js'

export { qualityScore } from './utils/quality-score.js'
export type {
  QualityComponents,
  QualityFactorResult,
  AnnualQualityData,
  QualityScoreOptions,
} from './utils/quality-score.js'

export { portfolioQuality } from './utils/portfolio.js'
export type {
  HoldingInput,
  HoldingResult,
  PortfolioQualityResult,
  PortfolioOptions,
} from './utils/portfolio.js'

export { valuationAttractivenessScore } from './utils/valuation-score.js'
export type {
  ValuationComponents,
  ValuationScore,
  ValuationParams,
} from './utils/valuation-score.js'

export { managementQualityScoreFromSeries } from './utils/management-score.js'
export type {
  AnnualManagementData,
  ManagementComponents,
  ManagementScore,
} from './utils/management-score.js'

export { dividendSafetyScoreFromSeries } from './utils/dividend-score.js'
export type {
  AnnualDividendData,
  DividendComponents,
  DividendSafetyScore,
} from './utils/dividend-score.js'

export { investmentScoreFromScores, investmentScoreFromSeries } from './utils/investment-score.js'
export type {
  InvestmentComponents,
  InvestmentScore,
  InvestmentScoreInputs,
} from './utils/investment-score.js'
