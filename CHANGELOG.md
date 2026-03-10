# Changelog

All notable changes to fin-ratios are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.0] — 2026-03-10

### Added

**Caching layer** (`fin_ratios.cache`)
- Memory, disk (JSON), and Redis backends with configurable TTL
- `set_cache('disk', ttl_hours=24)` — global configuration
- `@cached(namespace)` decorator for transparent fetcher cemoization
- `invalidate(ticker)`, `clear_cache()`, `cache_stats()`

**Batch compute** (`fin_ratios.utils.compute_all`)
- `compute_all(data, prior=None)` — computes all 40+ ratios from any data object
- Uniform `_DataAccessor` handles dicts, dataclasses, and any object with attributes
- Automatically includes health score; Piotroski/Montier C-Score when `prior` provided

**Historical ratio trends** (`fin_ratios.utils.trends`)
- `ratio_history(ticker, metrics, years=5, source='edgar')` → `RatioHistory`
- `.trend(metric)` — linear regression → `improving | stable | deteriorating | volatile`
- `.cagr(metric)`, `.table()`, `.to_dict()`, `._repr_html_()` (Jupyter rich display)

**Scenario DCF** (`fin_ratios.utils.scenario_dcf`)
- `scenario_dcf(base_fcf, shares, scenarios={bear/base/bull})` → `ScenarioDCFResult`
- Per-scenario intrinsic value per share, upside %, PV breakdown
- ASCII + HTML tables; `to_dict()` for JSON serialization

**Peer comparison** (`fin_ratios.utils.peers`)
- `compare_peers(ticker, metrics, peers=None)` → `PeerComparison`
- Built-in sector peer map for 20+ major tickers
- `.rank(metric)`, `.percentile(metric)`, `.table()`, `._repr_html_()`

**Pandas/Polars integration** (`fin_ratios.pandas_ext`)
- `ratios_from_df(df, ratios=None, groupby=None, inplace=False)`
- Column alias resolution (case-insensitive, 24+ common column name variants)
- `check_columns(df)` — debug helper for column mapping
- Works with both `pandas.DataFrame` and `polars.DataFrame`

**Jupyter notebook display** (`fin_ratios.notebook`)
- `RatioCard(ticker, ratios)` — color-coded single-ticker HTML card
- `ComparatorCard(ticker_ratios, metrics)` — side-by-side multi-ticker comparison
- `display_ratios(ticker, ratios)` — convenience wrapper

**SimFin fetcher** (`fin_ratios.fetchers.simfin`)
- Free structured financial data (500 req/day free tier)
- `fetch_simfin(ticker, api_key=...)` → standardized `SimFinData`
- `set_api_key(key)` or `SIMFIN_API_KEY` env var

**FastAPI REST API** (`fin_ratios.api`)
- `fin-ratios api --port 8000` CLI command
- `GET /ratios/{ticker}` — all ratios
- `GET /ratios/{ticker}/{ratio}` — single ratio
- `GET /health/{ticker}` — health score
- `GET /history/{ticker}` — multi-year trends
- `GET /peers/{ticker}` — peer comparison
- `GET /screen?tickers=AAPL,MSFT&roic_gt=0.15` — screening
- OpenAPI docs at `/docs`

**MCP Server** (`fin_ratios.mcp_server`)
- `fin-ratios serve` — starts MCP server (stdio transport for Claude Desktop)
- Tools: `analyze_ticker`, `health_score`, `ratio_history`, `compare_peers`,
  `screen_stocks`, `compute_ratio`

**New composite ratios**
- `montier_c_score()` — 6-signal earnings quality score (Montier 2008)
- `shiller_cape()` — Cyclically adjusted P/E with optional CPI adjustment (Shiller 2000)

**TypeScript additions**
- `computeAll(data)` — batch ratio computation from `FinancialData` object
- `scenarioDcf(input)` — scenario DCF (bull/base/bear)
- `setCache/cached/clearCache/cacheStats` — in-memory caching with TTL
- `montierCScore()` — Montier C-Score in TypeScript
- `fin-ratios/hooks` sub-path: `useRatios`, `useRatio`, `useHealthScore`,
  `useScenarioDcf`, `useCompareRatios` React hooks

**Optional dependency groups** (`pyproject.toml`)
- `pip install 'fin-ratios[api]'` — FastAPI + uvicorn
- `pip install 'fin-ratios[mcp]'` — MCP server
- `pip install 'fin-ratios[pandas]'` — Pandas integration
- `pip install 'fin-ratios[all]'` — everything

### Fixed
- CLI: Fixed `roe`/`roa`/`roic`/`ev_ebitda` argument names to match actual function signatures
- `compute_all`: Fixed `p_fcf`, `fcf_margin`, `fcf_conversion`, `fcf_yield`, efficiency function argument names

---

## [Unreleased]

---

## [0.1.0] — Initial Release

### Added

**Core library (134+ ratios)**
- Valuation (18): P/E, P/B, P/S, P/FCF, EV/EBITDA, EV/EBIT, EV/Revenue, EV/FCF,
  EV/IC, Tobin's Q, Graham Number, Graham Intrinsic Value, 2-Stage DCF, Reverse DCF,
  Gordon Growth DDM, Earnings Power Value, Forward P/E, PEG
- Profitability (15): Gross Margin, Operating Margin, EBITDA Margin, Net Margin,
  NOPAT Margin, ROE, ROA, ROIC, ROCE, ROTE, DuPont 3-Factor, Invested Capital,
  Revenue/Employee, Profit/Employee, NOPAT
- Liquidity (9): Current, Quick, Cash, OCF Ratios; DSO, DIO, DPO, CCC, DIR
- Solvency (9): D/E, Net D/E, Net Debt/EBITDA, Debt/Assets, Debt/Capital,
  Interest Coverage, EBITDA Coverage, DSCR, Equity Multiplier
- Efficiency (8): Asset Turnover, Fixed Asset Turnover, Inventory Turnover,
  Receivables Turnover, Payables Turnover, Working Capital Turnover,
  Capital Turnover, Operating Leverage
- Cash Flow (11): FCF, Levered FCF, Unlevered FCF (FCFF), Owner Earnings,
  FCF Yield, FCF Margin, FCF Conversion, OCF/Sales, Capex/Revenue,
  Capex/Depreciation, Cash Return on Assets
- Growth (8): Revenue YoY, Revenue CAGR, EPS Growth, EBITDA Growth,
  FCF Growth, Book Value Growth, Dividend Growth, EPV
- Risk / Portfolio (18): Beta, Jensen's Alpha, Sharpe, Sortino, Treynor, Calmar,
  Information Ratio, Omega, Maximum Drawdown, Tracking Error, Historical VaR,
  Parametric VaR, CVaR/ES, Ulcer Index, Upside Capture, Downside Capture, R-Squared
- Composite Scores (5): Piotroski F-Score, Altman Z-Score, Beneish M-Score,
  Ohlson O-Score, Greenblatt Magic Formula
- SaaS / Tech (11): Rule of 40, NRR, GRR, Magic Number, LTV/CAC, CAC Payback,
  Burn Multiple, SaaS Quick Ratio, ARR/FTE, Customer LTV, CAC
- REIT (7): FFO, AFFO, P/FFO, P/AFFO, NOI, Cap Rate, Occupancy Rate
- Banking (8): NIM, Efficiency Ratio, Loan/Deposit, NPL Ratio, Provision Coverage,
  Tier 1 Capital, CET1 Ratio, Tangible BVPS
- Insurance (5): Loss Ratio, Expense Ratio, Combined Ratio, Underwriting Margin, P/S

**Data fetchers (optional)**
- Yahoo Finance (free, no key) — Python + TypeScript
- SEC EDGAR XBRL (free, no key) — Python
- Financial Modeling Prep (freemium) — Python + TypeScript
- Alpha Vantage (freemium) — Python

**S&P 500 bulk analysis script**
- Fetches all 503 companies, computes 30+ ratios, outputs 4 CSV files
- Piotroski top-20, Altman distressed companies, Beneish manipulation flags

**Examples (runnable, no API key)**
- Python: valuation, composite scores, risk/portfolio, SaaS metrics
- TypeScript: composite scores

**Documentation**
- Full academic bibliography (`docs/CITATIONS.md`)
- Comprehensive GitHub README with Quick Start guides
- Formula and description on every function
