# fin-ratios

**The most comprehensive open-source financial ratios library.**

136+ ratios · 10 institutional-grade scoring models · TypeScript + Python.
Caching, REST API, MCP server, React hooks, Pandas/Polars. Zero runtime core dependencies.

[![npm](https://img.shields.io/npm/v/fin-ratios)](https://npmjs.com/package/fin-ratios)
[![PyPI](https://img.shields.io/pypi/v/financial-ratios)](https://pypi.org/project/financial-ratios/)
[![PyPI downloads](https://img.shields.io/pypi/dm/financial-ratios)](https://pypi.org/project/financial-ratios/)
[![CI](https://github.com/piyushgupta344/fin-ratios/actions/workflows/ci.yml/badge.svg)](https://github.com/piyushgupta344/fin-ratios/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-piyushgupta344.github.io-blue)](https://piyushgupta344.github.io/fin-ratios/)
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
| **Economic Moat Score** (formula-based, open-source first) | ✅ | No |
| **Capital Allocation Quality Score** | ✅ | No |
| **Earnings Quality Score** (accruals, cash backing, stability) | ✅ | No |
| **Fair Value Range** (5-method bear/base/bull) | ✅ | No |
| **Quality Factor Score** (QMJ composite) | ✅ | No |
| **Portfolio Quality Aggregation** (weighted scoring) | ✅ | No |
| **Valuation Attractiveness Score** (earnings yield, FCF yield, EV/EBITDA) | ✅ | No |
| **Management Quality Score** (ROIC, margins, dilution, execution) | ✅ | No |
| **Dividend Safety Score** (FCF payout, debt, track record) | ✅ | No |
| **Investment Score** (grand synthesis of all models) | ✅ | No |
| Backtesting scoring strategies against historical data | ✅ | No |
| Batch compute all ratios from one object | ✅ | No |
| Historical ratio trends + linear regression | ✅ | No |
| Scenario DCF (bull/base/bear) | ✅ | No |
| Peer comparison with percentile ranking | ✅ | No |
| Sector benchmarks (11 GICS sectors + score distributions) | ✅ | No |
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

## What's New in v1.0.2

**v1.0.2 — Documentation site, full scoring suite, release automation**
- MkDocs Material documentation site at [piyushgupta344.github.io/fin-ratios](https://piyushgupta344.github.io/fin-ratios/)
- Polygon.io fetcher (Python + TypeScript)
- CLI `score` subcommand — full scoring dashboard in terminal
- 575 tests passing (410 Python × 5 versions + 165 TypeScript × 3 Node versions)
- Automated release pipeline with PyPI trusted publishing and npm provenance

**v0.8 — Valuation, Management, Dividend Safety & Investment Scores**
- `valuationAttractivenessScore()` / `valuation_attractiveness_score()` — 5-signal valuation model: earnings yield spread, FCF yield, EV/EBITDA, P/B, DCF upside. Score 0–100, rated attractive/fair/expensive/overvalued
- `managementQualityScoreFromSeries()` / `management_quality_score_from_series()` — 4-signal management quality: ROIC excellence, margin stability, shareholder orientation, revenue execution
- `dividendSafetyScoreFromSeries()` / `dividend_safety_score_from_series()` — 4-signal dividend safety: FCF payout, earnings payout, balance sheet strength, dividend growth track
- `investmentScoreFromSeries()` / `investment_score_from_series()` — grand synthesis of all scoring models into a single 0–100 investment score with letter grade (A+/A/B+/B/C/D/F) and conviction (strong buy to strong sell)

**v0.7 — Quality Factor Score + Portfolio Quality**
- `qualityScore()` / `quality_score()` — composite 0–100 score combining Earnings Quality (35%), Moat Score (35%), Capital Allocation (30%). Maps to the QMJ factor (Asness et al. 2019)
- `portfolioQuality()` / `portfolio_quality()` — weighted quality analysis across a portfolio of holdings
- 165-test TypeScript test suite covering all scoring utilities and core ratios
- Sector benchmarks expanded with score distributions for all 11 GICS sectors

**v0.6 — Fair Value Range**
- `fairValueRange()` / `fair_value_range()` — up to five valuation methods (DCF, Graham Number, FCF Yield, EV/EBITDA, EPV) returning bear (p25), base (trimmed mean), bull (p75) per-share estimates

**v0.5 — Earnings Quality Score**
- `earningsQualityScore()` / `earnings_quality_score()` — 5-signal framework: accruals ratio, cash earnings quality, revenue recognition, gross margin stability, asset efficiency trend

**v0.4 — Capital Allocation Quality Score**
- `capitalAllocationScore()` / `capital_allocation_score()` — 4-signal framework: value creation (ROIC vs WACC), FCF quality, reinvestment yield, payout discipline

**v0.3 — Quantitative Economic Moat Score**
- `moatScore()` / `moat_score()` — first open-source formula-based economic moat score derived entirely from financial statements. Five signals with academic grounding.

---

## Installation

```bash
# TypeScript / JavaScript
npm install fin-ratios

# Python (core only — zero dependencies)
pip install financial-ratios

# Python with data fetchers (yfinance, httpx, requests)
pip install "financial-ratios[fetchers]"

# Python with REST API server (FastAPI + uvicorn)
pip install "financial-ratios[api]"

# Python with MCP server for AI agents
pip install "financial-ratios[mcp]"

# Python with Pandas/Polars DataFrame integration
pip install "financial-ratios[pandas]"

# Python with everything
pip install "financial-ratios[all]"
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
```

### TypeScript — Scoring Utilities (v0.3–v0.7)

```typescript
import { moatScore, capitalAllocationScore, earningsQualityScore,
         fairValueRange, qualityScore, portfolioQuality } from 'fin-ratios'

// Economic Moat Score
const moat = moatScore(annualData)
// => { score: 68, width: 'wide', components: { roicPersistence: 72, ... } }

// Capital Allocation Score
const ca = capitalAllocationScore(annualData)
// => { score: 74, rating: 'good', components: { valueCreation: 81, ... } }

// Earnings Quality Score
const eq = earningsQualityScore(annualData)
// => { score: 66, rating: 'medium', components: { accrualsRatio: 58, ... } }

// Fair Value Range (bear / base / bull per share)
const fv = fairValueRange({
  fcf: 110e9, shares: 15.4e9, growthRate: 0.10, terminalGrowth: 0.03,
  wacc: 0.09, dcfYears: 10, eps: 6.5, bvps: 4.8, targetYield: 0.04,
  ebitda: 130e9, totalDebt: 120e9, cash: 62e9, evEbitdaMultiple: 20,
  ebit: 112e9, taxRate: 0.15, currentPrice: 185,
})
console.log(`Bear: $${fv.bear.toFixed(0)}  Base: $${fv.base.toFixed(0)}  Bull: $${fv.bull.toFixed(0)}`)
console.log(`Margin of safety: ${(fv.marginOfSafety! * 100).toFixed(1)}%`)

// Quality Factor Score (combines EQ + Moat + Capital Allocation)
const qs = qualityScore(annualData)
// => { score: 69, grade: 'strong', components: { earningsQuality: 0.66, ... } }

// Portfolio Quality
const portfolio = portfolioQuality([
  { ticker: 'AAPL', weight: 0.40, annualData: appleData },
  { ticker: 'MSFT', weight: 0.35, annualData: msftData },
  { ticker: 'GOOGL', weight: 0.25, annualData: googlData },
])
console.log(`Portfolio quality: ${portfolio.weightedScore.toFixed(0)}/100`)
console.log(`Top holding: ${portfolio.topHolding}`)
```

### TypeScript — Batch Compute
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

### TypeScript — Scenario DCF
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

### TypeScript — React Hooks
```typescript
import { useRatios, useHealthScore, useCompareRatios } from 'fin-ratios/hooks'
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'

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
```

### Python — Scoring Utilities (v0.3–v0.7)

```python
from fin_ratios import (
    moat_score_from_series, capital_allocation_score_from_series,
    earnings_quality_score_from_series,
    fair_value_range, quality_score_from_series,
    portfolio_quality_from_series,
)

# All *_from_series functions accept a list of annual dicts (oldest → newest)
annual_data = [
    {'revenue': 200e9, 'ebit': 40e9, 'total_assets': 300e9, 'total_equity': 80e9,
     'operating_cash_flow': 50e9, 'capex': 10e9, 'net_income': 30e9,
     'total_debt': 60e9, 'cash': 25e9, 'gross_profit': 90e9},
    # ... more years (oldest first) ...
]

# Economic Moat Score
moat = moat_score_from_series(annual_data)
print(f"Moat: {moat.score}/100 ({moat.width})")   # "Moat: 68/100 (wide)"
print(moat.table())

# Capital Allocation Score
ca = capital_allocation_score_from_series(annual_data)
print(f"Capital Allocation: {ca.score}/100 ({ca.rating})")  # "Capital Allocation: 74/100 (good)"

# Earnings Quality Score
eq = earnings_quality_score_from_series(annual_data)
print(f"Earnings Quality: {eq.score}/100 ({eq.rating})")   # "Earnings Quality: 66/100 (medium)"

# Fair Value Range
fv = fair_value_range(
    fcf=110e9, shares=15.4e9, growth_rate=0.10, terminal_growth=0.03,
    wacc=0.09, dcf_years=10, eps=6.50, bvps=4.80, target_yield=0.04,
    ebitda=130e9, total_debt=120e9, cash=62e9, ev_ebitda_multiple=20,
    ebit=112e9, tax_rate=0.15, current_price=185.0,
)
print(f"Bear: ${fv.bear:.0f}  Base: ${fv.base:.0f}  Bull: ${fv.bull:.0f}")
print(f"Margin of safety: {fv.margin_of_safety:.1%}")
print(fv.table())

# Quality Factor Score (EQ 35% + Moat 35% + Capital Allocation 30%)
qs = quality_score_from_series(annual_data)
print(f"Quality: {qs.score}/100 ({qs.grade})")  # "Quality: 69/100 (strong)"

# Portfolio Quality
holdings_data = {
    'AAPL':  (0.40, apple_annual_data),   # (weight, annual_data_list)
    'MSFT':  (0.35, msft_annual_data),
    'GOOGL': (0.25, googl_annual_data),
}
portfolio = portfolio_quality_from_series(holdings_data)
print(f"Portfolio quality score: {portfolio.weighted_score:.0f}/100")
for h in portfolio.holdings:
    print(f"  {h.ticker}: {h.quality_score:.0f}/100  (weight: {h.weight:.0%})")
```

### Python — Convenience Wrappers (auto-fetch)

All scoring utilities have a single-ticker wrapper that fetches data automatically:

```python
from fin_ratios import moat_score, capital_allocation_score, earnings_quality_score
from fin_ratios.utils import quality_score, portfolio_quality

# Fetches 10 years of data from Yahoo Finance automatically
moat = moat_score('AAPL')
ca   = capital_allocation_score('AAPL')
eq   = earnings_quality_score('AAPL')
qs   = quality_score('AAPL')

# Jupyter — renders as color-coded HTML table
moat   # _repr_html_() called automatically

# Portfolio (fetches each holding)
portfolio = portfolio_quality({'AAPL': 0.40, 'MSFT': 0.35, 'GOOGL': 0.25})
```

### Python — Batch Compute
```python
from fin_ratios.utils import compute_all
from fin_ratios.fetchers.yahoo import fetch_yahoo

data = fetch_yahoo('AAPL')
ratios = compute_all(data)

print(f"P/E:          {ratios['pe']:.1f}")
print(f"ROIC:         {ratios['roic']:.1%}")
print(f"Gross Margin: {ratios['gross_margin']:.1%}")
print(f"Altman Zone:  {ratios['altman_z']['zone']}")
```

### Python — Ratio History & Trends
```python
from fin_ratios.utils import ratio_history

history = ratio_history('AAPL', metrics=['roic', 'gross_margin', 'pe'], years=5)

print(history.trend('roic'))        # 'improving'
print(history.trend('gross_margin')) # 'stable'
print(f"ROIC CAGR: {history.cagr('roic'):.1%}")
print(history.table())
```

### Python — Scenario DCF
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

### Python — Sector Benchmarks & Percentile Ranking
```python
from fin_ratios.utils.benchmarks import sector_benchmarks, percentile_rank

b = sector_benchmarks("Technology")
print(b.roic_median)            # 0.20 (20%)
print(b.moat_score_median)      # 52
print(b.quality_score_median)   # 55

# Percentile rank a value against peers
rank = percentile_rank("Technology", "roic", 0.55)
print(f"ROIC of 55% is in the {rank:.0f}th percentile for Tech")  # => 97th

# Works with all new scoring metrics too
moat_rank = percentile_rank("Technology", "moat_score", 68)
print(f"Moat score of 68 is in the {moat_rank:.0f}th percentile")  # => 83rd
```

### Python — Caching
```python
from fin_ratios.cache import set_cache, invalidate, clear_cache

set_cache('memory')                    # in-process (default)
set_cache('disk', ttl_hours=24)        # JSON files in ~/.fin_ratios_cache/
set_cache('redis', ttl_hours=1, url='redis://localhost:6379')

# Fetchers use the cache automatically
from fin_ratios.fetchers.yahoo import fetch_yahoo
data = fetch_yahoo('AAPL')  # live fetch
data = fetch_yahoo('AAPL')  # served from cache

invalidate('AAPL')    # clear one ticker
clear_cache()         # clear everything
```

### Python — REST API
```bash
pip install "financial-ratios[api]"
fin-ratios api --port 8000
# OpenAPI docs at http://localhost:8000/docs
```

```
GET /ratios/{ticker}           — all 40+ ratios
GET /ratios/{ticker}/{ratio}   — single ratio
GET /health/{ticker}           — health score (0-100)
GET /history/{ticker}          — 5-year ratio trends
GET /peers/{ticker}            — peer comparison
GET /screen?tickers=AAPL,MSFT&roic_gt=0.15&pe_lt=30  — screening
```

### Python — MCP Server for AI Agents
```bash
pip install "financial-ratios[mcp]"
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
```
```typescript
import { fetchYahoo } from 'fin-ratios/fetchers/yahoo'
const data = await fetchYahoo('AAPL')
```

### SEC EDGAR (free, no API key, US companies only)
```python
from fin_ratios.fetchers.edgar import fetch_edgar
filings = fetch_edgar('AAPL', num_years=3)  # newest-first list
```
```typescript
import { fetchEdgar, fetchEdgarFlat } from 'fin-ratios/fetchers/edgar'
// fetchEdgarFlat returns oldest-first flat records, ready for scoring utilities
const annualData = await fetchEdgarFlat('AAPL')
```

### Financial Modeling Prep (free tier: 250 req/day)
```python
from fin_ratios.fetchers.fmp import fetch_fmp
data = fetch_fmp('AAPL', api_key='your_key', periods=4)
```

### SimFin (free tier: 500 req/day)
```python
from fin_ratios.fetchers.simfin import fetch_simfin, set_api_key
set_api_key('your_simfin_key')  # or SIMFIN_API_KEY env var
data = fetch_simfin('AAPL')
```

---

## S&P 500 Bulk Analysis

```bash
pip install "financial-ratios[fetchers]" pandas
cd python
python scripts/sp500_analysis.py              # All 503 companies (~30-45 min)
python scripts/sp500_analysis.py --sample 50  # Quick test with 50 companies
```

| Output file | Contents |
|-------------|----------|
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

### Scoring Models (v0.3–v0.7)
| Model | Signals | Output | Reference |
|-------|---------|--------|-----------|
| **Moat Score** (0–100) | ROIC persistence, pricing power, reinvestment quality, op. leverage, CAP | wide / narrow / none | Mauboussin & Johnson (1997) |
| **Capital Allocation Score** (0–100) | Value creation, FCF quality, reinvestment yield, payout discipline | excellent / good / fair / poor | Koller et al. (2020), Mauboussin (2012) |
| **Earnings Quality Score** (0–100) | Accruals ratio, cash earnings, revenue recognition, GM stability, asset efficiency | high / medium / low / poor | Sloan (1996), Richardson et al. (2005) |
| **Fair Value Range** | DCF, Graham Number, FCF Yield, EV/EBITDA, EPV | bear / base / bull per share | Graham & Dodd (1934), Koller et al. (2020) |
| **Quality Factor Score** (0–100) | EQ (35%) + Moat (35%) + Capital Allocation (30%) | exceptional → poor | Asness, Frazzini & Pedersen (2019) |
| **Portfolio Quality** | Weighted average across holdings | portfolio score + per-holding breakdown | — |

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

## Documentation

- [Quantitative Moat Score — methodology, signals, and usage](docs/MOAT_SCORE.md)
- [Academic Citations](docs/CITATIONS.md)
- [Changelog](CHANGELOG.md)

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
- Mauboussin & Johnson (1997) — Competitive Advantage Period (CAP)
- Sloan (1996) — Accruals anomaly, *Accounting Review*
- Richardson et al. (2005) — Accruals and future earnings, *Journal of Accounting & Economics*
- Novy-Marx (2013) — Gross profitability, *Journal of Financial Economics*
- Mauboussin (2012) — True measures of capital allocation success, *Harvard Business Review*
- Asness, Frazzini & Pedersen (2019) — Quality Minus Junk, *Review of Accounting Studies*

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
│   │   ├── utils/            # computeAll, scenarioDcf, cache, moatScore,
│   │   │                     # capitalAllocationScore, earningsQualityScore,
│   │   │                     # fairValueRange, qualityScore, portfolioQuality
│   │   └── __tests__/        # 165-test vitest suite
│   └── examples/
├── python/
│   ├── fin_ratios/
│   │   ├── ratios/           # Python port of all ratios
│   │   ├── fetchers/         # Yahoo, FMP, EDGAR, Alpha Vantage, SimFin
│   │   ├── utils/            # compute_all, trends, scenario_dcf, peers,
│   │   │                     # moat_score, capital_allocation, earnings_quality,
│   │   │                     # fair_value, quality_score, portfolio, benchmarks
│   │   ├── cache.py          # Memory / disk / Redis caching layer
│   │   ├── pandas_ext.py     # Pandas + Polars DataFrame integration
│   │   ├── notebook.py       # Jupyter rich display (RatioCard, ComparatorCard)
│   │   ├── api.py            # FastAPI REST server
│   │   ├── mcp_server.py     # MCP server for AI agents
│   │   └── cli.py            # fin-ratios CLI
│   ├── tests/                # 410-test pytest suite
│   ├── examples/
│   └── scripts/
│       └── sp500_analysis.py
├── docs/
│   ├── MOAT_SCORE.md         # Moat score methodology deep-dive
│   └── CITATIONS.md          # Full academic bibliography
└── CHANGELOG.md
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

## Security

See [SECURITY.md](SECURITY.md) to report vulnerabilities.

---

## License

MIT — use freely in commercial projects.

---

**Links:** [Docs](https://piyushgupta344.github.io/fin-ratios/) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [npm](https://npmjs.com/package/fin-ratios) · [PyPI](https://pypi.org/project/financial-ratios/)
