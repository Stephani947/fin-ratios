# fin-ratios

**The most comprehensive open-source financial ratios library.**

136+ ratios across 13 categories. TypeScript + Python with identical APIs.
Caching, batch compute, REST API, MCP server for AI agents, React hooks,
and Pandas/Polars integration. Zero runtime dependencies in the core.
Formula transparency on every function.

[![npm](https://img.shields.io/npm/v/fin-ratios)](https://npmjs.com/package/fin-ratios)
[![PyPI](https://img.shields.io/pypi/v/fin-ratios)](https://pypi.org/project/fin-ratios/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why fin-ratios?

Existing libraries either fetch data or compute 10–20 basic ratios.
**fin-ratios** does both and goes much further:

| Feature | fin-ratios | Competitors |
|---------|-----------|-------------|
| Ratio count | **136+** | 10–30 |
| Composite scores (Piotroski, Beneish, Altman, Montier, Shiller) | ✅ | Rarely |
| Risk/portfolio ratios (Sharpe, CVaR, Omega) | ✅ | No |
| SaaS metrics (Rule of 40, NRR, Burn Multiple) | ✅ | No |
| REIT / Banking / Insurance ratios | ✅ | No |
| Intrinsic value models (DCF, Reverse DCF, Graham) | ✅ | No |
| Batch compute all ratios from one object | ✅ | No |
| Historical ratio trends + linear regression | ✅ | No |
| Scenario DCF (bull/base/bear) | ✅ | No |
| Peer comparison with percentile ranking | ✅ | No |
| Caching layer (memory/disk/Redis) | ✅ | No |
| Pandas + Polars DataFrame integration | ✅ | No |
| Jupyter notebook rich display | ✅ | No |
| FastAPI REST API (6 endpoints) | ✅ | No |
| MCP server for AI agents (Claude Desktop) | ✅ | No |
| React hooks (`useRatios`, `useHealthScore`) | ✅ | No |
| Formula on every function | ✅ | No |
| Academic citations for every ratio | ✅ | No |
| TypeScript + Python | ✅ | Usually one |
| Zero core dependencies | ✅ | Usually no |

---

## What's New in v0.2

- **`compute_all(data)`** — compute all 40+ ratios from a single data object in one call
- **`ratio_history(ticker, metrics, years=5)`** — multi-year trends with linear regression (improving/stable/deteriorating)
- **`scenario_dcf(base_fcf, shares, scenarios)`** — bull/base/bear intrinsic value analysis
- **`compare_peers(ticker, metrics)`** — peer comparison with built-in sector maps and percentile ranks
- **Caching layer** — memory, disk (JSON), and Redis backends with TTL; `@cached(namespace)` decorator
- **Pandas/Polars integration** — `ratios_from_df(df)` with 24+ column alias variants
- **Jupyter notebook display** — color-coded `RatioCard` and `ComparatorCard` rich HTML
- **FastAPI REST API** — `fin-ratios api --port 8000`, OpenAPI docs at `/docs`
- **MCP Server** — `fin-ratios serve` for Claude Desktop (6 AI agent tools)
- **SimFin fetcher** — free structured financial data (500 req/day free tier)
- **Montier C-Score** — 6-signal earnings quality score (Montier 2008)
- **Shiller CAPE** — cyclically adjusted P/E with CPI adjustment (Shiller 2000)
- **TypeScript** — `computeAll()`, `scenarioDcf()`, `montierCScore()`, in-memory cache, React hooks

---

## Installation

```bash
# TypeScript / JavaScript
npm install fin-ratios

# Python (core only — zero dependencies)
pip install fin-ratios

# Python with data fetchers (yfinance, httpx, requests)
pip install "fin-ratios[fetchers]"

# Python with REST API server (FastAPI + uvicorn)
pip install "fin-ratios[api]"

# Python with MCP server for AI agents
pip install "fin-ratios[mcp]"

# Python with Pandas/Polars DataFrame integration
pip install "fin-ratios[pandas]"

# Python with everything
pip install "fin-ratios[all]"
```

---

## Quick Start

### TypeScript — Core Ratios
```typescript
import {
  pe, evEbitda, peg, pb,
  roic, nopat, investedCapital,
  sharpeRatio, conditionalVaR,
  piotroskiFScore, altmanZScore, beneishMScore,
  ruleOf40, netRevenueRetention, burnMultiple,
  dcf2Stage, reverseDcf, grahamNumber,
} from 'fin-ratios'

// Valuation
const peRatio = pe({ marketCap: 3_000_000_000_000, netIncome: 100_000_000_000 })
// => 30

const ev = evEbitda({ enterpriseValue: 3_060_000_000_000, ebitda: 130_000_000_000 })
// => 23.5

// Access formula on any function
console.log(pe.formula)        // "Market Capitalization / Net Income"
console.log(evEbitda.formula)  // "Enterprise Value / EBITDA"

// ROIC (value creation test)
const ic = investedCapital({ totalEquity: 74e9, totalDebt: 110e9, cash: 62e9 })
const nopatVal = nopat({ ebit: 120e9, taxRate: 0.15 })
const roicVal = roic({ nopat: nopatVal, investedCapital: ic })
// => 0.99 (99% ROIC)

// DCF Valuation
const dcf = dcf2Stage({
  baseFcf: 5_000_000_000,
  growthRate: 0.20,
  years: 10,
  terminalGrowthRate: 0.03,
  wacc: 0.10,
  netDebt: -10_000_000_000,
  sharesOutstanding: 1_000_000_000,
})
console.log(`Intrinsic value: $${dcf?.intrinsicValuePerShare?.toFixed(2)}`)

// Piotroski F-Score (0-9)
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
```

### TypeScript — Batch Compute (v0.2)
```typescript
import { computeAll } from 'fin-ratios'
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'

const data = await fetchYahoo('AAPL')
const ratios = computeAll(data)

console.log(ratios.pe)           // 28.3
console.log(ratios.roic)         // 0.55
console.log(ratios.grossMargin)  // 0.433
console.log(ratios.altmanZ?.zone) // 'safe'
console.log(ratios.piotroski?.score) // 7
```

### TypeScript — Scenario DCF (v0.2)
```typescript
import { scenarioDcf } from 'fin-ratios'

const result = scenarioDcf({
  baseFcf: 100e9,
  sharesOutstanding: 15.7e9,
  currentPrice: 185,
  scenarios: {
    bear: { growthRate: 0.05, wacc: 0.12, terminalGrowth: 0.02, years: 10 },
    base: { growthRate: 0.10, wacc: 0.10, terminalGrowth: 0.03, years: 10 },
    bull: { growthRate: 0.18, wacc: 0.09, terminalGrowth: 0.04, years: 10 },
  },
})
console.log(result.base.intrinsicValuePerShare)  // 198.4
console.log(result.base.upsidePct)              // 0.074 (7.4% upside)
```

### TypeScript — React Hooks (v0.2)
```typescript
import { useRatios, useHealthScore, useCompareRatios } from 'fin-ratios/hooks'
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'

// Fetch and compute all ratios
function StockCard({ ticker }: { ticker: string }) {
  const { data, loading, error } = useRatios(ticker, fetchYahoo)
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  return (
    <div>
      <div>P/E: {data?.pe?.toFixed(1)}</div>
      <div>ROIC: {(data?.roic ?? 0 * 100).toFixed(1)}%</div>
      <div>Gross Margin: {(data?.grossMargin ?? 0 * 100).toFixed(1)}%</div>
    </div>
  )
}

// Compare multiple tickers
function PeerTable({ tickers }: { tickers: string[] }) {
  const { data } = useCompareRatios(tickers, fetchYahoo)
  return (
    <table>
      {tickers.map(t => (
        <tr key={t}>
          <td>{t}</td>
          <td>{data?.[t]?.pe?.toFixed(1)}</td>
          <td>{data?.[t]?.roic?.toFixed(2)}</td>
        </tr>
      ))}
    </table>
  )
}
```

---

### Python — Core Ratios
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

# Access formula and description
print(pe.formula)     # "Market Capitalization / Net Income"
print(pe.description) # "How much investors pay per $1 of earnings."

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

### Python — Batch Compute (v0.2)
```python
from fin_ratios.utils import compute_all
from fin_ratios.fetchers.yahoo import fetch_yahoo

data = fetch_yahoo('AAPL')
ratios = compute_all(data)

print(f"P/E:          {ratios['pe']:.1f}")
print(f"ROIC:         {ratios['roic']:.1%}")
print(f"Gross Margin: {ratios['gross_margin']:.1%}")
print(f"Current:      {ratios['current_ratio']:.2f}")
print(f"Altman Zone:  {ratios['altman_z']['zone']}")
# Also works with plain dicts or any object with attributes
ratios2 = compute_all({
    'revenue': 400e9, 'net_income': 100e9,
    'total_assets': 350e9, 'total_equity': 74e9,
    'market_cap': 3e12, ...
})
```

### Python — Ratio History & Trends (v0.2)
```python
from fin_ratios.utils import ratio_history

history = ratio_history('AAPL', metrics=['roic', 'gross_margin', 'pe'], years=5)

# Trend direction via linear regression
print(history.trend('roic'))        # 'improving'
print(history.trend('gross_margin')) # 'stable'

# CAGR
print(f"ROIC CAGR: {history.cagr('roic'):.1%}")

# ASCII table
print(history.table())
# Year    roic    gross_margin   pe
# 2020    0.56    0.38           28.4
# 2021    0.61    0.42           31.2
# ...

# In Jupyter — renders as color-coded HTML table
history  # _repr_html_() called automatically
```

### Python — Scenario DCF (v0.2)
```python
from fin_ratios.utils import scenario_dcf

result = scenario_dcf(
    base_fcf=100e9,
    shares_outstanding=15.7e9,
    current_price=185.0,
    scenarios={
        'bear': {'growth_rate': 0.05, 'wacc': 0.12, 'terminal_growth': 0.02, 'years': 10},
        'base': {'growth_rate': 0.10, 'wacc': 0.10, 'terminal_growth': 0.03, 'years': 10},
        'bull': {'growth_rate': 0.18, 'wacc': 0.09, 'terminal_growth': 0.04, 'years': 10},
    },
)

print(result.table())
# Scenario  IV/Share  Upside
# bear      $142.30   -23.1%
# base      $198.40   +7.2%
# bull      $287.60   +55.5%
```

### Python — Peer Comparison (v0.2)
```python
from fin_ratios.utils import compare_peers

comp = compare_peers('AAPL', metrics=['roic', 'gross_margin', 'pe'])

print(comp.rank('roic'))        # 1  (best among peers)
print(comp.percentile('roic'))  # 0.95

# In Jupyter — color-coded HTML table with rank superscripts
comp  # _repr_html_() called automatically
```

### Python — Pandas Integration (v0.2)
```python
from fin_ratios.pandas_ext import ratios_from_df, check_columns
import pandas as pd

df = pd.DataFrame({
    'ticker': ['AAPL', 'MSFT', 'GOOGL'],
    'market_cap': [3e12, 2.5e12, 1.8e12],
    'net_income': [100e9, 88e9, 73e9],
    'revenue':    [400e9, 220e9, 305e9],
    'gross_profit': [172e9, 152e9, 174e9],
    'ebit':       [120e9, 108e9, 84e9],
    'total_assets': [350e9, 510e9, 400e9],
    'total_equity': [74e9, 206e9, 283e9],
})

# Compute selected ratios
result = ratios_from_df(df, ratios=['pe', 'gross_margin', 'roe', 'roa'])

# Debug column resolution
print(check_columns(df))
# {'resolved': {'market_cap': 'market_cap', ...}, 'missing': ['operating_cash_flow'], ...}

# Works with Polars DataFrames too
import polars as pl
result = ratios_from_df(pl.from_pandas(df), ratios=['pe', 'roic'])
```

### Python — Caching (v0.2)
```python
from fin_ratios.cache import set_cache, invalidate, clear_cache, cache_stats

# Configure cache backend
set_cache('memory')                    # in-process (default)
set_cache('disk', ttl_hours=24)        # JSON files in ~/.fin_ratios_cache/
set_cache('redis', ttl_hours=1, url='redis://localhost:6379')

# Fetchers automatically use the cache — no code change needed
from fin_ratios.fetchers.yahoo import fetch_yahoo
data = fetch_yahoo('AAPL')  # live fetch
data = fetch_yahoo('AAPL')  # served from cache

# Cache management
invalidate('AAPL')    # clear one ticker
clear_cache()         # clear everything
print(cache_stats())  # {'hits': 12, 'misses': 3, 'entries': 8}
```

### Python — Jupyter Notebook (v0.2)
```python
from fin_ratios.notebook import RatioCard, ComparatorCard, display_ratios

# Single-ticker color-coded card
RatioCard('AAPL', {
    'pe': 28.3, 'roic': 0.55, 'gross_margin': 0.433,
    'current_ratio': 1.07, 'debt_to_equity': 1.49,
})

# Side-by-side comparison
ComparatorCard(
    ticker_ratios={'AAPL': {...}, 'MSFT': {...}, 'GOOGL': {...}},
    metrics=['pe', 'roic', 'gross_margin', 'current_ratio'],
)
```

### Python — REST API (v0.2)
```bash
# Install with API extras
pip install "fin-ratios[api]"

# Start server
fin-ratios api --port 8000

# OpenAPI docs at http://localhost:8000/docs
```

```python
# Available endpoints:
# GET /ratios/{ticker}           — all 40+ ratios
# GET /ratios/{ticker}/{ratio}   — single ratio
# GET /health/{ticker}           — health score (0-100)
# GET /history/{ticker}          — 5-year ratio trends
# GET /peers/{ticker}            — peer comparison
# GET /screen?tickers=AAPL,MSFT&roic_gt=0.15&pe_lt=30  — screening
```

### Python — MCP Server for AI Agents (v0.2)
```bash
# Install with MCP extras
pip install "fin-ratios[mcp]"

# Start MCP server (stdio transport — use with Claude Desktop)
fin-ratios serve
```

Add to your Claude Desktop `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fin-ratios": {
      "command": "fin-ratios",
      "args": ["serve"]
    }
  }
}
```

Available tools for Claude:
- `analyze_ticker` — all ratios for a ticker
- `health_score` — financial health score (0–100)
- `ratio_history` — multi-year trends
- `compare_peers` — peer comparison
- `screen_stocks` — filter by ratio thresholds
- `compute_ratio` — compute a specific ratio from raw inputs

---

## Data Fetchers (Optional)

Fetchers are separate optional modules — zero network code in the core.

### Yahoo Finance (free, no API key)
```python
from fin_ratios.fetchers.yahoo import fetch_yahoo

data = fetch_yahoo('AAPL')
print(f"P/E: {pe(data.market_cap, data.net_income):.1f}")
```

```typescript
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'
const data = await fetchYahoo('AAPL')
```

### SEC EDGAR (free, no API key, US companies only)
```python
from fin_ratios.fetchers.edgar import fetch_edgar

filings = fetch_edgar('AAPL', num_years=3)
for f in filings:
    print(f"{f.fiscal_year}: Revenue ${f.revenue/1e9:.1f}B")
```

### SimFin (free tier: 500 req/day) — New in v0.2
```python
from fin_ratios.fetchers.simfin import fetch_simfin, set_api_key

set_api_key('your_simfin_key')  # or SIMFIN_API_KEY env var
data = fetch_simfin('AAPL')
```

### Financial Modeling Prep (free tier: 250 req/day)
```python
from fin_ratios.fetchers.fmp import fetch_fmp
data = fetch_fmp('AAPL', api_key='your_key', periods=4)
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
pip install "fin-ratios[fetchers]" pandas
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
Ulcer Index, Upside Capture, Downside Capture, R-Squared

### Composite Scores (7)
| Score | What it detects | Reference |
|-------|----------------|-----------|
| **Piotroski F-Score** (0–9) | Financial strength | Piotroski (2000) |
| **Altman Z-Score** | Bankruptcy probability | Altman (1968) |
| **Beneish M-Score** | Earnings manipulation | Beneish (1999) |
| **Ohlson O-Score** | Bankruptcy probability (logistic) | Ohlson (1980) |
| **Greenblatt Magic Formula** | Value + Quality ranking | Greenblatt (2005) |
| **Montier C-Score** (0–6) | Earnings quality signals | Montier (2008) |
| **Shiller CAPE** | Cyclically adjusted P/E | Shiller (2000) |

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
5. **Zero core deps** — only fetchers/api/mcp have external dependencies
6. **Strict TypeScript** — `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`
7. **Transparent caching** — opt-in cache layer; fetchers unchanged
8. **Batch-first** — `compute_all()` / `computeAll()` for single-call analysis

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
- Montier (2008) — C-Score earnings quality, *Société Générale Cross Asset Research*
- Shiller (2000) — CAPE cyclically adjusted P/E, *Irrational Exuberance*

---

## Project Structure

```
fin-ratios/
├── typescript/
│   ├── src/
│   │   ├── ratios/           # 136+ ratio functions
│   │   ├── fetchers/         # Yahoo, FMP, EDGAR, Alpha Vantage
│   │   ├── hooks/            # React hooks (useRatios, useHealthScore, ...)
│   │   ├── types/            # IncomeStatement, BalanceSheet, MarketData, etc.
│   │   └── utils/            # computeAll, scenarioDcf, cache, safeDivide
│   └── examples/             # Runnable TypeScript examples
├── python/
│   ├── fin_ratios/
│   │   ├── ratios/           # Python port of all ratios
│   │   ├── fetchers/         # Yahoo, FMP, EDGAR, Alpha Vantage, SimFin
│   │   ├── utils/            # compute_all, trends, scenario_dcf, peers, health_score
│   │   ├── cache.py          # Memory / disk / Redis caching layer
│   │   ├── pandas_ext.py     # Pandas + Polars DataFrame integration
│   │   ├── notebook.py       # Jupyter rich display (RatioCard, ComparatorCard)
│   │   ├── api.py            # FastAPI REST server
│   │   ├── mcp_server.py     # MCP server for AI agents
│   │   └── cli.py            # fin-ratios CLI
│   ├── examples/             # Runnable Python examples
│   └── scripts/
│       └── sp500_analysis.py # S&P 500 bulk computation
├── docs/
│   └── CITATIONS.md          # Full academic bibliography
└── CHANGELOG.md              # Version history
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
