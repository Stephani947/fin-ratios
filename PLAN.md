# fin-ratios — Implementation Plan

## Vision

The most comprehensive, developer-friendly financial ratios library available.
Available in TypeScript and Python with identical APIs.
Zero opinions on data source — bring your own data, or use built-in fetchers.

---

## Architecture

### Core Principles

1. **Pure functions** — every ratio is a pure function: `(inputs) => number | null`
2. **Typed inputs** — structured financial statement objects, not loose primitives
3. **Formula transparency** — every exported function has a `.formula` string property
4. **Null-safe** — missing data returns `null`, never `NaN` or throws by default
5. **Tree-shakeable** — import only what you need
6. **Fetcher-optional** — fetchers are separate optional modules, core has zero network deps
7. **Historical support** — functions accept arrays of period inputs for trend calculation

### Project Structure

```
fin-ratios/
├── typescript/
│   ├── src/
│   │   ├── types/
│   │   │   ├── financials.ts       # IncomeStatement, BalanceSheet, CashFlowStatement
│   │   │   ├── market.ts           # MarketData, PriceHistory
│   │   │   └── index.ts
│   │   ├── ratios/
│   │   │   ├── valuation/
│   │   │   ├── profitability/
│   │   │   ├── liquidity/
│   │   │   ├── solvency/
│   │   │   ├── efficiency/
│   │   │   ├── cashflow/
│   │   │   ├── risk/
│   │   │   ├── growth/
│   │   │   ├── composite/          # Multi-metric scoring systems
│   │   │   └── sector/             # Sector-specific ratios
│   │   │       ├── banking/
│   │   │       ├── insurance/
│   │   │       ├── reit/
│   │   │       └── saas/
│   │   ├── fetchers/               # Optional data source adapters
│   │   │   ├── yahoo/
│   │   │   ├── fmp/                # Financial Modeling Prep
│   │   │   ├── alphavantage/
│   │   │   └── edgar/              # SEC EDGAR (free, no key needed)
│   │   ├── utils/
│   │   │   ├── safe-divide.ts
│   │   │   ├── cagr.ts
│   │   │   └── normalize.ts
│   │   └── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── vitest.config.ts
├── python/
│   ├── fin_ratios/
│   │   ├── types/
│   │   │   ├── financials.py
│   │   │   └── market.py
│   │   ├── ratios/
│   │   │   └── (mirrors TS structure)
│   │   ├── fetchers/
│   │   └── __init__.py
│   ├── pyproject.toml
│   └── tests/
├── docs/
│   └── ratios/                     # Per-ratio documentation
└── examples/
    ├── typescript/
    └── python/
```

---

## Full Ratio Catalog

### 1. Valuation Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| P/E (Trailing) | Price / EPS | marketCap, netIncome, sharesOutstanding |
| P/E (Forward) | Price / ForwardEPS | price, analystEPSEstimate |
| PEG Ratio | P/E / EPS Growth Rate | pe, epsGrowthRate |
| Shiller CAPE | Price / Avg10YrRealEPS | priceHistory[10y], earningsHistory[10y], cpiHistory |
| P/B | MarketCap / BookValue | marketCap, totalEquity |
| P/S | MarketCap / Revenue | marketCap, revenue |
| P/FCF | MarketCap / FreeCashFlow | marketCap, operatingCashFlow, capex |
| EV/EBITDA | EV / EBITDA | marketCap, debt, cash, ebitda |
| EV/EBIT | EV / EBIT | marketCap, debt, cash, ebit |
| EV/Revenue | EV / Revenue | marketCap, debt, cash, revenue |
| EV/FCF | EV / FCF | marketCap, debt, cash, fcf |
| EV/NOPAT | EV / NOPAT | ev, nopat |
| EV/Invested Capital | EV / IC | ev, investedCapital |
| Tobin's Q | (MarketCap + Debt) / TotalAssets | marketCap, debt, totalAssets |
| Graham Number | sqrt(22.5 * EPS * BVPS) | eps, bookValuePerShare |
| Graham Intrinsic Value | EPS * (8.5 + 2g) * 4.4/Y | eps, growthRate, aaa_bondYield |
| P/NAV | MarketCap / NetAssetValue | marketCap, nav |
| Price/Owner Earnings | Price / OwnerEarnings | price, ownerEarnings, sharesOutstanding |
| Reverse DCF (implied growth) | Solve for g in DCF = MarketCap | marketCap, fcf, wacc, terminalMultiple |

### 2. Profitability Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Gross Margin | GrossProfit / Revenue | grossProfit, revenue |
| Operating Margin | EBIT / Revenue | ebit, revenue |
| EBITDA Margin | EBITDA / Revenue | ebitda, revenue |
| Net Profit Margin | NetIncome / Revenue | netIncome, revenue |
| NOPAT Margin | NOPAT / Revenue | nopat, revenue |
| ROE | NetIncome / AvgEquity | netIncome, avgTotalEquity |
| ROA | NetIncome / AvgAssets | netIncome, avgTotalAssets |
| ROIC | NOPAT / InvestedCapital | nopat, investedCapital |
| ROCE | EBIT / CapitalEmployed | ebit, totalAssets, currentLiabilities |
| ROTE | NetIncome / AvgTangibleEquity | netIncome, equity, intangibles, goodwill |
| ROE (DuPont 3-factor) | Margin * Turnover * Leverage | netMargin, assetTurnover, equityMultiplier |
| ROE (DuPont 5-factor) | (EBT/EBIT)*(EBIT/Rev)*(Rev/Assets)*(Assets/Eq)*(NI/EBT) | full income stmt + balance sheet |
| Revenue per Employee | Revenue / Employees | revenue, employeeCount |
| Profit per Employee | NetIncome / Employees | netIncome, employeeCount |
| Incremental ROIC | DeltaNOPAT / DeltaIC | nopat[t], nopat[t-1], ic[t], ic[t-1] |

### 3. Liquidity Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Current Ratio | CurrentAssets / CurrentLiabilities | currentAssets, currentLiabilities |
| Quick Ratio | (Cash + ST Investments + AR) / CL | cash, stInvestments, accountsReceivable, currentLiabilities |
| Cash Ratio | Cash / CurrentLiabilities | cash, currentLiabilities |
| Operating CF Ratio | OperatingCF / CurrentLiabilities | operatingCashFlow, currentLiabilities |
| Days Sales Outstanding (DSO) | AR / (Revenue / 365) | accountsReceivable, revenue |
| Days Inventory Outstanding (DIO) | Inventory / (COGS / 365) | inventory, cogs |
| Days Payable Outstanding (DPO) | AP / (COGS / 365) | accountsPayable, cogs |
| Cash Conversion Cycle (CCC) | DSO + DIO - DPO | dso, dio, dpo |
| Net Trade Cycle | CCC / (Revenue / 365) | ccc, revenue |
| Defensive Interval Ratio | (Cash + ST Inv + AR) / Daily Op Expenses | liquid assets, dailyOperatingExpenses |

### 4. Solvency / Leverage Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Debt-to-Equity | TotalDebt / TotalEquity | totalDebt, totalEquity |
| Net Debt-to-Equity | NetDebt / TotalEquity | debt, cash, equity |
| Net Debt-to-EBITDA | NetDebt / EBITDA | netDebt, ebitda |
| Debt-to-Assets | TotalDebt / TotalAssets | totalDebt, totalAssets |
| Debt-to-Capital | Debt / (Debt + Equity) | debt, equity |
| Interest Coverage (ICR) | EBIT / InterestExpense | ebit, interestExpense |
| EBITDA Coverage | EBITDA / InterestExpense | ebitda, interestExpense |
| Debt Service Coverage (DSCR) | NOI / TotalDebtService | noi, principalPayments, interestExpense |
| Fixed Charge Coverage | (EBIT + FixedCharges) / (FixedCharges + Interest) | ebit, fixedCharges, interestExpense |
| Equity Multiplier | TotalAssets / TotalEquity | totalAssets, totalEquity |
| Capital Adequacy Ratio | Tier1+Tier2 / RWA | (banking specific) |

### 5. Efficiency / Activity Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Asset Turnover | Revenue / AvgTotalAssets | revenue, avgTotalAssets |
| Fixed Asset Turnover | Revenue / AvgNetFixedAssets | revenue, avgNetPPE |
| Inventory Turnover | COGS / AvgInventory | cogs, avgInventory |
| Receivables Turnover | Revenue / AvgAR | revenue, avgAccountsReceivable |
| Payables Turnover | COGS / AvgAP | cogs, avgAccountsPayable |
| Working Capital Turnover | Revenue / AvgWorkingCapital | revenue, avgWorkingCapital |
| Capital Turnover | Revenue / InvestedCapital | revenue, investedCapital |
| Operating Leverage | % Change EBIT / % Change Revenue | ebit[t], ebit[t-1], revenue[t], revenue[t-1] |

### 6. Cash Flow Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Free Cash Flow (FCF) | OperatingCF - Capex | operatingCashFlow, capex |
| Levered FCF | FCF - DebtRepayments + DebtIssuance | fcf, netDebtChange |
| Unlevered FCF (UFCF) | NOPAT + D&A - CapexNet - ChangeInWC | nopat, da, capex, changeInWC |
| Owner Earnings (Buffett) | NI + D&A - MaintenanceCapex | netIncome, da, maintenanceCapex |
| FCF Yield | FCF / MarketCap | fcf, marketCap |
| FCF Margin | FCF / Revenue | fcf, revenue |
| FCF Conversion | FCF / NetIncome | fcf, netIncome |
| FCF-to-Revenue | FCF / Revenue | fcf, revenue |
| OCF-to-Sales | OperatingCF / Revenue | operatingCashFlow, revenue |
| Capex-to-Revenue | Capex / Revenue | capex, revenue |
| Capex-to-Depreciation | Capex / Depreciation | capex, depreciation |
| Cash Return on Assets | OperatingCF / TotalAssets | operatingCashFlow, totalAssets |

### 7. Growth Ratios

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Revenue Growth YoY | (Rev_t - Rev_t-1) / Rev_t-1 | revenue[t], revenue[t-1] |
| Revenue CAGR | (RevEnd/RevStart)^(1/n) - 1 | revenueHistory[], years |
| EPS Growth | (EPS_t - EPS_t-1) / EPS_t-1 | eps[t], eps[t-1] |
| EBITDA Growth | same | ebitda series |
| FCF Growth | same | fcf series |
| Book Value Per Share Growth | same | bvps series |
| Dividend Growth Rate | same | dps series |
| Earnings Power Value (EPV) | EBIT(1-t) / WACC | ebit, taxRate, wacc |

### 8. Risk / Portfolio Ratios (hardest to find, biggest differentiator)

| Ratio | Formula | Inputs Needed |
|-------|---------|---------------|
| Beta | Cov(r_stock, r_market) / Var(r_market) | priceHistory[], marketHistory[] |
| Alpha (Jensen's) | r_p - [r_f + B*(r_m - r_f)] | portfolioReturn, riskFreeRate, beta, marketReturn |
| Sharpe Ratio | (Rp - Rf) / StdDev(Rp) | returns[], riskFreeRate |
| Sortino Ratio | (Rp - Rf) / DownsideDeviation | returns[], riskFreeRate, mar |
| Treynor Ratio | (Rp - Rf) / Beta | portfolioReturn, riskFreeRate, beta |
| Calmar Ratio | AnnualReturn / MaxDrawdown | returns[] |
| Information Ratio | ActiveReturn / TrackingError | portfolioReturns[], benchmarkReturns[] |
| Omega Ratio | E[gains above L] / E[losses below L] | returns[], threshold |
| Kappa Ratio (n=3) | (Rp-L) / LPM_n^(1/n) | returns[], threshold, n |
| Upside Capture Ratio | PortfolioReturn(up) / BenchmarkReturn(up) | portfolioReturns[], benchmarkReturns[] |
| Downside Capture Ratio | same for down markets | portfolioReturns[], benchmarkReturns[] |
| Tracking Error | StdDev(Rp - Rb) | portfolioReturns[], benchmarkReturns[] |
| R-Squared | Corr(Rp, Rb)^2 | portfolioReturns[], benchmarkReturns[] |
| Maximum Drawdown | (Peak - Trough) / Peak | priceHistory[] or returns[] |
| Value at Risk (VaR) | percentile(returns, 1-conf) | returns[], confidence |
| CVaR / Expected Shortfall | Mean of returns below VaR | returns[], confidence |
| VaR (Parametric) | -mu + z*sigma (normal assumption) | returns[], confidence |
| VaR (Historical) | empirical percentile | returns[], confidence |
| VaR (Monte Carlo) | simulated distribution percentile | returns[], simulations, confidence |
| Ulcer Index | sqrt(mean(drawdown^2)) | priceHistory[] |
| Pain Ratio | (Rp - Rf) / UlcerIndex | returns[], ulcerIndex |
| Martin Ratio | same as Pain Ratio | returns[], ulcerIndex |
| Sterling Ratio | AnnualReturn / AvgMaxDrawdown | returns[], lookback |
| Burke Ratio | (Rp-Rf) / sqrt(sum(drawdown^2)) | returns[], riskFreeRate |

### 9. Composite Scoring Systems (rarest, highest value)

| Score | What It Measures | Inputs Needed |
|-------|-----------------|---------------|
| **Piotroski F-Score** (0-9) | Financial strength (9 binary signals) | Full 3-statement data, 2 periods |
| **Altman Z-Score** | Bankruptcy probability | Full balance sheet + income stmt + market cap |
| **Altman Z'-Score** | Private company variant | Same, no market data |
| **Altman Z''-Score** | Non-manufacturing variant | Same |
| **Beneish M-Score** | Earnings manipulation probability (8 variables) | Full 3-statement, 2 periods |
| **Montier C-Score** | Earnings manipulation (simpler, 6 signals) | Key accounting items, 2 periods |
| **Ohlson O-Score** | Bankruptcy (logistic regression) | Balance sheet + income, 2 periods |
| **Greenblatt Magic Formula** | ROIC + EV/EBIT ranking | Balance sheet, income, market cap |
| **Quality Score (QS)** | Composite: profitability + stability + growth | All 3 statements |
| **Momentum Score** | 12-1 month price momentum | priceHistory[] |

#### Piotroski F-Score Signals (9 binary tests)
**Profitability (4):**
- ROA > 0
- Operating CF > 0
- Delta ROA > 0 (improving)
- Accruals: CF > NI (quality earnings)

**Leverage/Liquidity (3):**
- Delta Long-term Debt/Assets < 0 (less leveraged)
- Delta Current Ratio > 0 (more liquid)
- No new shares issued (dilution check)

**Operating Efficiency (2):**
- Delta Gross Margin > 0
- Delta Asset Turnover > 0

#### Beneish M-Score Variables (8)
- DSRI: Days Sales Receivable Index
- GMI: Gross Margin Index
- AQI: Asset Quality Index
- SGI: Sales Growth Index
- DEPI: Depreciation Index
- SGAI: SG&A Expense Index
- LVGI: Leverage Index
- TATA: Total Accruals to Total Assets

M-Score = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI
(> -2.22 suggests manipulation)

#### Altman Z-Score
- X1 = Working Capital / Total Assets
- X2 = Retained Earnings / Total Assets
- X3 = EBIT / Total Assets
- X4 = Market Cap / Total Liabilities
- X5 = Revenue / Total Assets
- Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
(> 2.99 safe zone, < 1.81 distress zone)

### 10. Sector-Specific Ratios

#### Banking
| Ratio | Formula |
|-------|---------|
| Net Interest Margin (NIM) | (InterestIncome - InterestExpense) / AvgEarningAssets |
| Net Interest Spread | Avg Yield on Assets - Avg Rate on Liabilities |
| Efficiency Ratio | NonInterestExpense / (NetInterestIncome + NonInterestIncome) |
| Loan-to-Deposit Ratio | TotalLoans / TotalDeposits |
| NPL Ratio | NonPerformingLoans / TotalLoans |
| Provision Coverage Ratio | LoanLossReserves / NPL |
| Tier 1 Capital Ratio | Tier1Capital / RiskWeightedAssets |
| CET1 Ratio | CommonEquityTier1 / RWA |
| Return on Risk-Weighted Assets | NetIncome / RWA |
| Tangible Book Value Per Share | (Equity - Intangibles - Goodwill) / Shares |
| Price-to-Tangible Book | MarketCap / TangibleBookValue |

#### Insurance
| Ratio | Formula |
|-------|---------|
| Loss Ratio | Losses / Premiums Earned |
| Expense Ratio | Underwriting Expenses / Premiums Written |
| Combined Ratio | Loss Ratio + Expense Ratio |
| Operating Ratio | Combined Ratio - Investment Income Ratio |
| Underwriting Profit Margin | 1 - Combined Ratio |
| Return on Equity (Ins-adjusted) | NetIncome / AvgEquity |
| Premiums-to-Surplus | Net Premiums Written / Policyholder Surplus |
| Reserve Development Ratio | Prior Year Reserve Development / Prior Premiums |

#### REIT
| Ratio | Formula |
|-------|---------|
| FFO (Funds From Operations) | NetIncome + Depreciation - GainsOnSales |
| AFFO (Adjusted FFO) | FFO - RecurringCapex + StraightLineRentAdj |
| P/FFO | MarketCap / FFO |
| P/AFFO | MarketCap / AFFO |
| Net Operating Income (NOI) | Revenue - OperatingExpenses (excl. D&A, interest) |
| Cap Rate | NOI / PropertyValue |
| Debt-to-Gross-Assets | TotalDebt / GrossAssets |
| Debt-to-EBITDA (REIT) | TotalDebt / EBITDA |
| Occupancy Rate | OccupiedSF / TotalSF |
| Same-Store NOI Growth | NOI growth for properties owned 12+ months |

#### SaaS / Tech
| Ratio | Formula |
|-------|---------|
| Rule of 40 | RevenueGrowthRate% + FCFMargin% (or EBITDA margin) |
| ARR Growth | (ARR_t - ARR_t-1) / ARR_t-1 |
| Net Revenue Retention (NRR) | (BegARR + Expansion - Churn - Contraction) / BegARR |
| Gross Revenue Retention (GRR) | (BegARR - Churn - Contraction) / BegARR |
| Magic Number | (QuarterlyRevGrowth * 4) / PriorQuarterS&MSpend |
| CAC (Customer Acquisition Cost) | S&MSpend / NewCustomers |
| LTV (Customer Lifetime Value) | AvgRevPerCustomer / ChurnRate * GrossMargin |
| LTV/CAC | LTV / CAC |
| CAC Payback Period | CAC / (AvgMRR * GrossMargin%) |
| Burn Multiple | NetBurnRate / NetNewARR |
| Sales Efficiency | NewARR / S&MSpend |
| Quick Ratio (SaaS) | (NewMRR + Expansion) / (Churned + Contraction) |
| Hype Ratio | EV/ARR / NRR |
| ARR per FTE | ARR / FullTimeEmployees |

### 11. Intrinsic Value Models

| Model | Description | Inputs |
|-------|-------------|--------|
| DCF (2-stage) | PV of FCF in growth stage + terminal value | fcf[], growthRate, terminalGrowthRate, wacc, years |
| DCF (3-stage) | High growth + transition + terminal | fcf[], g1, g2, gT, wacc |
| DDM (Gordon Growth) | D1 / (r - g) | nextDividend, requiredReturn, growthRate |
| DDM (Multi-stage) | Sum PV dividends + terminal | dividends[], growthRates[], requiredReturn |
| Residual Income Model | BookValue + PV(future RI) | bvps, eps[], requiredReturn |
| Earnings Power Value (EPV) | EBIT(1-t) / WACC | ebit, taxRate, wacc |
| Graham Number | sqrt(22.5 * EPS * BVPS) | eps, bvps |
| Ben Graham Formula | EPS * (8.5 + 2g) * 4.4 / AAA_Yield | eps, growthRate, aaa_yieldRate |
| Reverse DCF | Implied growth rate from current price | marketCap, fcf, wacc |
| FCFE Model | PV of FCF to Equity | fcfe[], requiredReturn, terminalValue |
| FCFF Model | PV of FCF to Firm, then net debt | fcff[], wacc, debt, cash |
| Sum-of-parts | Sum of segment DCFs | segmentData[] |

---

## API Design (TypeScript)

```typescript
// Bring your own data
import { pe, evEbitda, altmanZScore, sharpeRatio } from 'fin-ratios'

// Simple ratio
const ratio = pe({ marketCap: 100_000_000, netIncome: 5_000_000 })
// => 20

// With null safety
const ratio = pe({ marketCap: 100_000_000, netIncome: 0 })
// => null (division by zero handled)

// Access formula
console.log(pe.formula)
// => "Market Capitalization / Net Income"

// Composite score
const score = altmanZScore({
  workingCapital: 50_000_000,
  retainedEarnings: 200_000_000,
  ebit: 30_000_000,
  marketCap: 500_000_000,
  totalLiabilities: 100_000_000,
  totalAssets: 300_000_000,
  revenue: 400_000_000
})
// => { z: 3.42, zone: 'safe', interpretation: 'Low bankruptcy risk' }

// Historical trend
import { roic, historicalRatios } from 'fin-ratios'
const trend = historicalRatios(roic, [period2021, period2022, period2023])
// => [{ period: '2021', value: 0.15 }, ...]

// Use a fetcher (optional, separate install)
import { fetchFMP } from 'fin-ratios/fetchers/fmp'
const data = await fetchFMP('AAPL', { apiKey: 'xxx', periods: 4 })
const ratio = pe(data)
```

---

## API Design (Python)

```python
from fin_ratios import pe, ev_ebitda, altman_z_score, sharpe_ratio
from fin_ratios.types import IncomeStatement, BalanceSheet, MarketData

# Simple ratio
result = pe(market_cap=100_000_000, net_income=5_000_000)
# => 20.0

# With dataclass inputs
income = IncomeStatement(revenue=400e6, net_income=30e6, ebit=40e6, ...)
balance = BalanceSheet(total_assets=300e6, total_equity=200e6, ...)
market = MarketData(market_cap=500e6, price=50.0)

z = altman_z_score(income=income, balance=balance, market=market)
# => AltmanResult(z=3.42, zone='safe', interpretation='...')

# Fetcher
from fin_ratios.fetchers.fmp import fetch_fmp
data = await fetch_fmp('AAPL', api_key='xxx', periods=4)
```

---

## Data Source Adapters

| Source | Cost | Key Required | Quality | Coverage |
|--------|------|-------------|---------|----------|
| Yahoo Finance | Free | No | Good | Global, delayed |
| SEC EDGAR | Free | No | Excellent | US public companies |
| Financial Modeling Prep (FMP) | Freemium | Yes | Excellent | Global |
| Alpha Vantage | Freemium | Yes | Good | Global |
| Polygon.io | Paid | Yes | Excellent | US, real-time |
| Simfin | Freemium | Yes | Good | US + EU |

Each fetcher maps source data to the standard `IncomeStatement | BalanceSheet | CashFlowStatement | MarketData` types.

---

## Implementation Phases

### Phase 1 — Foundation (TypeScript)
- [ ] Core types: `IncomeStatement`, `BalanceSheet`, `CashFlowStatement`, `MarketData`, `PriceHistory`
- [ ] Utils: `safeDivide`, `cagr`, `annualize`, `rollingWindow`
- [ ] All valuation ratios
- [ ] All profitability ratios
- [ ] All liquidity ratios
- [ ] All solvency ratios
- [ ] All efficiency ratios
- [ ] All cash flow ratios
- [ ] All growth ratios
- [ ] Unit tests for all above

### Phase 2 — Advanced (TypeScript)
- [ ] All risk/portfolio ratios
- [ ] Composite scores (Piotroski, Altman, Beneish, Montier, Ohlson)
- [ ] Intrinsic value models (DCF, DDM, Graham, EPV)
- [ ] Sector-specific ratios (Banking, Insurance, REIT, SaaS)

### Phase 3 — Fetchers
- [ ] SEC EDGAR adapter (free, US public companies)
- [ ] Yahoo Finance adapter (free, global)
- [ ] FMP adapter (freemium)
- [ ] Alpha Vantage adapter

### Phase 4 — Python Port
- [ ] Mirror all Phase 1+2 ratios in Python
- [ ] Python fetchers
- [ ] Publish to PyPI

### Phase 5 — Docs & DX
- [ ] Per-ratio documentation with formula, interpretation, benchmarks
- [ ] Industry benchmarks database
- [ ] Playground / examples
- [ ] Publish to npm as `fin-ratios`

---

## Competitive Differentiation

Most existing libraries (financialmodelingprep-sdk, yahoo-finance2, etc.) are **data fetchers**,
not ratio calculators. The few ratio libraries that exist:
- Only cover 10-20 ratios
- No composite scoring (Piotroski, Beneish, Altman)
- No risk/portfolio ratios
- No sector-specific ratios
- No intrinsic value models
- Python-only or JS-only

**fin-ratios** covers 120+ ratios across 11 categories with identical TS + Python APIs.
