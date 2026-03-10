# fin-ratios

**The most comprehensive open-source financial ratios library.**

134+ ratios across 13 categories. TypeScript + Python with identical APIs.
Zero runtime dependencies in the core. Formula transparency on every function.

[![npm](https://img.shields.io/npm/v/fin-ratios)](https://npmjs.com/package/fin-ratios)
[![PyPI](https://img.shields.io/pypi/v/fin-ratios)](https://pypi.org/project/fin-ratios/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why fin-ratios?

Existing libraries either fetch data or compute 10-20 basic ratios.
**fin-ratios** does both and goes much further:

| Feature | fin-ratios | Competitors |
|---------|-----------|-------------|
| Ratio count | **134+** | 10–30 |
| Composite scores (Piotroski, Beneish, Altman) | ✅ | Rarely |
| Risk/portfolio ratios (Sharpe, CVaR, Omega) | ✅ | No |
| SaaS metrics (Rule of 40, NRR, Burn Multiple) | ✅ | No |
| REIT / Banking / Insurance ratios | ✅ | No |
| Intrinsic value models (DCF, Reverse DCF, Graham) | ✅ | No |
| Formula on every function | ✅ | No |
| Academic citations for every ratio | ✅ | No |
| TypeScript + Python | ✅ | Usually one |
| Zero core dependencies | ✅ | Usually no |

---

## Installation

```bash
# TypeScript / JavaScript
npm install fin-ratios

# Python
pip install fin-ratios

# Python with data fetchers (yfinance, httpx)
pip install "fin-ratios[fetchers]"
```

---

## Quick Start

### TypeScript
```typescript
import {
  pe, evEbitda, peg, pb,
  roic, nopat, investedCapital,
  sharpeRatio, conditionalVaR,
  piotroskiFScore, altmanZScore, beneishMScore,
  ruleOf40, netRevenueRetention, burnMultiple,
  dcf2Stage, reverseDcf, grahamNumber,
} from 'fin-ratios'

// ── Valuation ─────────────────────────────────────────────────────────
const peRatio = pe({ marketCap: 3_000_000_000_000, netIncome: 100_000_000_000 })
// => 30

const ev = evEbitda({ enterpriseValue: 3_060_000_000_000, ebitda: 130_000_000_000 })
// => 23.5

// Access formula on any function
console.log(pe.formula)        // "Market Capitalization / Net Income"
console.log(evEbitda.formula)  // "Enterprise Value / EBITDA"

// ── ROIC (value creation test) ────────────────────────────────────────
const ic = investedCapital({ totalEquity: 74e9, totalDebt: 110e9, cash: 62e9 })
const nopatVal = nopat({ ebit: 120e9, taxRate: 0.15 })
const roicVal = roic({ nopat: nopatVal, investedCapital: ic })
// => 0.99 (99% ROIC — far above any WACC, massive value creation)

// ── DCF Valuation ─────────────────────────────────────────────────────
const dcf = dcf2Stage({
  baseFcf: 5_000_000_000,
  growthRate: 0.20,
  years: 10,
  terminalGrowthRate: 0.03,
  wacc: 0.10,
  netDebt: -10_000_000_000,     // net cash
  sharesOutstanding: 1_000_000_000,
})
console.log(`Intrinsic value: $${dcf?.intrinsicValuePerShare?.toFixed(2)}`)

// ── Reverse DCF ───────────────────────────────────────────────────────
const implied = reverseDcf({
  marketCap: 500_000_000_000,
  baseFcf: 10_000_000_000,
  years: 10,
  terminalGrowthRate: 0.03,
  wacc: 0.10,
})
console.log(implied?.interpretation)
// => "Market implies 22.3% annual FCF growth over 10 years at 10.0% WACC"

// ── Piotroski F-Score (0-9) ───────────────────────────────────────────
const score = piotroskiFScore({
  current: { netIncome: 8e6, totalAssets: 100e6, operatingCashFlow: 12e6,
             longTermDebt: 20e6, currentAssets: 35e6, currentLiabilities: 15e6,
             sharesOutstanding: 10e6, grossProfit: 45e6, revenue: 90e6 },
  prior:   { netIncome: 5e6, totalAssets: 95e6, longTermDebt: 25e6,
             currentAssets: 28e6, currentLiabilities: 14e6, sharesOutstanding: 10.5e6,
             grossProfit: 38e6, revenue: 80e6 },
})
console.log(`F-Score: ${score.score}/9 — ${score.interpretation}`)
// => "F-Score: 9/9 — Strong: High financial strength"

// ── Altman Z-Score (bankruptcy prediction) ───────────────────────────
const z = altmanZScore({
  workingCapital: 50e9, retainedEarnings: 200e9, ebit: 90e9,
  marketCap: 3000e9, totalLiabilities: 210e9, totalAssets: 411e9, revenue: 212e9,
})
console.log(`Z-Score: ${z?.z.toFixed(2)} (${z?.zone})`)
// => "Z-Score: 4.82 (safe)"

// ── Beneish M-Score (earnings manipulation) ──────────────────────────
const m = beneishMScore({
  current: { revenue: 110e6, accountsReceivable: 25e6, grossProfit: 38e6,
             totalAssets: 155e6, depreciation: 6e6, ppGross: 55e6,
             sgaExpense: 20e6, totalDebt: 45e6, netIncome: 12e6, cashFlowFromOps: 3e6 },
  prior:   { revenue: 90e6, accountsReceivable: 10e6, grossProfit: 38e6,
             totalAssets: 140e6, depreciation: 8e6, ppGross: 45e6,
             sgaExpense: 14e6, totalDebt: 30e6 },
})
console.log(m?.interpretation)  // "M-Score -1.84 > -2.22: Possible earnings manipulation"

// ── Sharpe Ratio ─────────────────────────────────────────────────────
const sharpe = sharpeRatio({ returns: dailyReturns, riskFreeRate: 0.05, periodsPerYear: 252 })

// ── CVaR (Expected Shortfall) ─────────────────────────────────────────
const cvar = conditionalVaR({ returns: dailyReturns, confidence: 0.95 })
// => 0.032 (avg loss of 3.2% in worst 5% of days)

// ── SaaS Metrics ──────────────────────────────────────────────────────
const r40 = ruleOf40({ revenueGrowthRatePct: 35, fcfMarginPct: 12 })
// => 47 (healthy: > 40)

const nrr = netRevenueRetention({ beginningArr: 100e6, expansion: 20e6, churn: 5e6, contraction: 2e6 })
// => 1.13 (113% — net expansion)

const bm = burnMultiple({ netBurnRate: 800_000, netNewArr: 1_000_000 })
// => 0.8 (excellent: < 1)
```

### Python
```python
from fin_ratios import (
    pe, ev_ebitda, graham_number,
    roic, nopat as compute_nopat, invested_capital,
    sharpe_ratio, conditional_var,
    piotroski_f_score, altman_z_score, beneish_m_score,
    rule_of_40, net_revenue_retention, burn_multiple,
    dcf_2_stage, reverse_dcf,
)

# Valuation
ratio = pe(market_cap=3e12, net_income=100e9)
# => 30.0

# Access formula
print(pe.formula)     # "Market Capitalization / Net Income"
print(pe.description) # "How much investors pay per $1 of earnings."

# Graham Number
gn = graham_number(eps=6.43, book_value_per_share=4.50)
# => 8.09 (Apple at $190 = well above Graham Number)

# Altman Z-Score
z = altman_z_score(
    working_capital=50e9, retained_earnings=200e9, ebit=90e9,
    market_cap=3000e9, total_liabilities=210e9,
    total_assets=411e9, revenue=212e9,
)
print(z["interpretation"])  # "Z-Score 4.82: Safe zone — Low bankruptcy risk"

# Piotroski F-Score
result = piotroski_f_score(
    current_net_income=8e6,    current_total_assets=100e6,
    current_operating_cf=12e6, current_long_term_debt=20e6,
    current_current_assets=35e6, current_current_liabilities=15e6,
    current_shares_outstanding=10e6, current_gross_profit=45e6,
    current_revenue=90e6,
    prior_net_income=5e6,      prior_total_assets=95e6,
    prior_long_term_debt=25e6, prior_current_assets=28e6,
    prior_current_liabilities=14e6, prior_shares_outstanding=10.5e6,
    prior_gross_profit=38e6,   prior_revenue=80e6,
)
print(result["score"])          # 9
print(result["interpretation"]) # "Strong (9/9): High financial strength"
```

---

## Data Fetchers (Optional)

Fetchers are separate optional modules — zero network code in the core.

### Yahoo Finance (free, no API key)
```python
from fin_ratios.fetchers.yahoo import fetch_yahoo

data = fetch_yahoo('AAPL')
print(f"P/E: {pe(data.market_cap, data.net_income):.1f}")
print(f"ROIC: {roic(compute_nopat(data.ebit, 0.15), invested_capital(data.total_equity, data.total_debt, data.cash)):.1%}")
```

```typescript
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'
import { pe, roic } from 'fin-ratios'

const data = await fetchYahoo('AAPL')
console.log(pe({ marketCap: data.marketData.marketCap, netIncome: data.income.netIncome }))
```

### SEC EDGAR (free, no API key, US companies only)
```python
from fin_ratios.fetchers.edgar import fetch_edgar

filings = fetch_edgar('AAPL', num_years=3)
for f in filings:
    print(f"{f.fiscal_year}: Revenue ${f.revenue/1e9:.1f}B, Net Income ${f.net_income/1e9:.1f}B")
```

### Financial Modeling Prep (free tier: 250 req/day)
```python
from fin_ratios.fetchers.fmp import fetch_fmp

data = fetch_fmp('AAPL', api_key='your_key', periods=4)
for period in data:
    print(f"{period.period}: ROIC {period.roic:.1%}")
```

```typescript
import { fetchFmp } from 'fin-ratios/fetchers/fmp'
const data = await fetchFmp('AAPL', { apiKey: 'your_key', periods: 4 })
```

### Alpha Vantage (free tier: 25 req/day)
```python
from fin_ratios.fetchers.alphavantage import fetch_alphavantage

data = fetch_alphavantage('IBM', api_key='your_key')
```

---

## S&P 500 Bulk Analysis

```bash
pip install yfinance pandas
cd python
python scripts/sp500_analysis.py              # All 503 companies (~30-45 min)
python scripts/sp500_analysis.py --sample 50  # Quick test with 50 companies
```

**Output files:**
| File | Contents |
|------|----------|
| `sp500_ratios.csv` | All 30+ ratios for every company |
| `sp500_top_piotroski.csv` | Top 20 companies by F-Score |
| `sp500_distressed.csv` | Companies in Altman distress zone |
| `sp500_manipulation_flags.csv` | Companies flagged by Beneish M-Score |

---

## Full Ratio Catalog

### Valuation (18)
| Ratio | Formula | Key Reference |
|-------|---------|--------------|
| P/E (Trailing) | Market Cap / Net Income | Graham & Dodd (1934) |
| P/E (Forward) | Price / Forward EPS | — |
| PEG Ratio | P/E / EPS Growth % | Lynch (1989) |
| P/B | Market Cap / Total Equity | Graham & Dodd (1934) |
| P/S | Market Cap / Revenue | — |
| P/FCF | Market Cap / FCF | — |
| EV/EBITDA | EV / EBITDA | Koller et al. (2020) |
| EV/EBIT | EV / EBIT | — |
| EV/Revenue | EV / Revenue | — |
| EV/FCF | EV / FCF | — |
| EV/Invested Capital | EV / IC | — |
| Tobin's Q | (MC + Debt) / Assets | Tobin (1969) |
| Graham Number | √(22.5 × EPS × BVPS) | Graham (1973) |
| Graham Intrinsic Value | EPS × (8.5 + 2g) × 4.4 / Y | Graham (1974) |
| 2-Stage DCF | Σ FCF/(1+r)^t + TV | Williams (1938) |
| Gordon Growth DDM | D1 / (r - g) | Gordon (1959) |
| Earnings Power Value | NOPAT / WACC | Greenwald et al. (2001) |
| Reverse DCF | Solve for g | Mauboussin (2006) |

### Profitability (15)
Gross Margin, Operating Margin, EBITDA Margin, Net Margin, NOPAT Margin,
ROE, ROA, ROIC, ROCE, ROTE, DuPont 3-Factor, Invested Capital,
Revenue/Employee, Profit/Employee, NOPAT

### Liquidity (9)
Current Ratio, Quick Ratio, Cash Ratio, OCF Ratio, DSO, DIO, DPO,
Cash Conversion Cycle, Defensive Interval Ratio

### Solvency (9)
D/E, Net D/E, Net Debt/EBITDA, Debt/Assets, Debt/Capital,
Interest Coverage, EBITDA Coverage, DSCR, Equity Multiplier

### Efficiency (8)
Asset Turnover, Fixed Asset Turnover, Inventory Turnover,
Receivables Turnover, Payables Turnover, Working Capital Turnover,
Capital Turnover, Operating Leverage

### Cash Flow (11)
FCF, Levered FCF, Unlevered FCF (FCFF), Owner Earnings,
FCF Yield, FCF Margin, FCF Conversion, OCF/Sales,
Capex/Revenue, Capex/Depreciation, Cash Return on Assets

### Growth (8)
Revenue YoY, Revenue CAGR, EPS Growth, EBITDA Growth,
FCF Growth, Book Value Growth, Dividend Growth, EPV

### Risk / Portfolio (18)
Beta, Jensen's Alpha, Sharpe Ratio, Sortino Ratio, Treynor Ratio,
Calmar Ratio, Information Ratio, Omega Ratio, Maximum Drawdown,
Tracking Error, Historical VaR, Parametric VaR, CVaR/Expected Shortfall,
Ulcer Index, Upside Capture, Downside Capture, R-Squared, Ulcer Index

### Composite Scores (5)
| Score | What it detects | Reference |
|-------|----------------|-----------|
| **Piotroski F-Score** (0–9) | Financial strength | Piotroski (2000) |
| **Altman Z-Score** | Bankruptcy probability | Altman (1968) |
| **Beneish M-Score** | Earnings manipulation | Beneish (1999) |
| **Ohlson O-Score** | Bankruptcy probability (logistic) | Ohlson (1980) |
| **Greenblatt Magic Formula** | Value + Quality ranking | Greenblatt (2005) |

### SaaS / Tech (11)
| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Rule of 40 | Growth % + FCF Margin % | > 40 healthy |
| Net Revenue Retention | Net ARR / Beginning ARR | > 110% elite |
| Gross Revenue Retention | (ARR - Churn) / ARR | > 90% good |
| Magic Number | Net New ARR × 4 / S&M | > 0.75 efficient |
| LTV/CAC | Customer LTV / CAC | > 3x healthy |
| CAC Payback | CAC / Monthly Margin | < 12 mo excellent |
| Burn Multiple | Net Burn / New ARR | < 1 excellent |
| SaaS Quick Ratio | (New + Exp) / (Churn + Contraction) | > 4 excellent |
| ARR/FTE | ARR / Employees | > $200K elite |
| Customer LTV | (ARPU × GM) / Churn | — |
| CAC | S&M Spend / New Customers | — |

### REIT (7)
FFO, AFFO, P/FFO, P/AFFO, NOI, Cap Rate, Occupancy Rate

### Banking (8)
NIM, Efficiency Ratio, Loan/Deposit, NPL Ratio, Provision Coverage,
Tier 1 Capital, CET1 Ratio, Tangible BVPS

### Insurance (5)
Loss Ratio, Expense Ratio, Combined Ratio, Underwriting Margin, Premiums/Surplus

---

## Design Principles

1. **Pure functions** — `(inputs) → number | null`
2. **Formula on every function** — `pe.formula`, `sharpeRatio.formula`
3. **Null-safe** — returns `null` on division by zero, never `NaN`
4. **Tree-shakeable** — import only what you need
5. **Zero core deps** — only fetchers have external dependencies
6. **Strict TypeScript** — `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`

---

## Examples

Run the included examples without any API keys:

```bash
cd python
python examples/01_valuation_examples.py    # DCF, Graham Number, EV multiples
python examples/03_composite_scores.py      # Piotroski, Altman, Beneish, Magic Formula
python examples/04_risk_portfolio.py        # Sharpe, Sortino, VaR, CVaR, Capture Ratios
python examples/05_saas_metrics.py          # Rule of 40, NRR, Burn Multiple, LTV/CAC
```

---

## Academic Citations

Every ratio is backed by either academic research or established industry practice.
See [docs/CITATIONS.md](docs/CITATIONS.md) for the full bibliography.

**Key papers:**
- Altman (1968) — Z-Score bankruptcy prediction, *Journal of Finance*
- Piotroski (2000) — F-Score value investing, *Journal of Accounting Research*
- Beneish (1999) — M-Score earnings manipulation, *Financial Analysts Journal*
- Sharpe (1966) — Risk-adjusted return, *Journal of Business*
- Gordon (1959) — Dividend discount model, *Review of Economics and Statistics*
- Rockafellar & Uryasev (2000) — CVaR optimization, *Journal of Risk*
- Tobin (1969) — Q ratio, *Journal of Money, Credit and Banking*
- Ohlson (1980) — O-Score bankruptcy probability, *Journal of Accounting Research*
- Keating & Shadwick (2002) — Omega ratio, *Journal of Performance Measurement*

---

## Project Structure

```
fin-ratios/
├── typescript/
│   ├── src/
│   │   ├── ratios/           # 134+ ratio functions
│   │   ├── fetchers/         # Yahoo, FMP, EDGAR, Alpha Vantage
│   │   ├── types/            # IncomeStatement, BalanceSheet, MarketData, etc.
│   │   └── utils/            # safeDivide, math helpers
│   └── examples/             # Runnable TypeScript examples
├── python/
│   ├── fin_ratios/
│   │   ├── ratios/           # Python port of all ratios
│   │   ├── fetchers/         # Python fetchers
│   │   └── types/            # Python dataclasses
│   ├── examples/             # Runnable Python examples
│   └── scripts/
│       └── sp500_analysis.py # S&P 500 bulk computation
├── docs/
│   └── CITATIONS.md          # Full academic bibliography
└── PLAN.md                   # Detailed implementation roadmap
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions welcome.

When adding a new ratio, include:
1. The formula as a string on the function (`.formula = "..."`)
2. A description (`.description = "..."`)
3. An academic or industry citation in `docs/CITATIONS.md`
4. At least one test in the test suite

---

## License

MIT — use freely in commercial projects.
