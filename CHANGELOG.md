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

## [0.3.0] — 2026-03-11

### Added

**Quantitative Economic Moat Score** (`fin_ratios.utils.moat_score`)
- First open-source, formula-based economic moat score derived entirely from financial statements
- Five weighted signals: ROIC Persistence (30%), Pricing Power (25%), Reinvestment Quality (20%), Operating Leverage (15%), CAP Estimate (10%)
- `moat_score_from_series(annual_data, wacc=None)` — compute from any sequence of annual dicts/objects
- `moat_score(ticker, years=10, source='yahoo')` — convenience wrapper that fetches multi-year data
- `MoatScore` dataclass: `score` (0–100), `width` ('wide'/'narrow'/'none'), `components`, `cap_estimate_years`, `evidence`, `.table()`, `._repr_html_()`, `.to_dict()`
- Capital-light detection: triggers when majority of reinvestment periods are negative (asset-light moat signal)
- WACC auto-estimation from capital structure (CAPM cost of equity + after-tax cost of debt)
- Accepts any object with financial attributes — dict, dataclass, fetcher output
- TypeScript: `moatScore(annualData, options?)` → `MoatScoreResult`
- 27 new tests; total suite: 221 passed, 5 skipped

**References:** Mauboussin & Johnson (1997), Greenwald & Kahn (2001), Koller et al. (2020)

---

## [0.4.0] — 2026-03-11

### Added

**Capital Allocation Quality Score** (`fin_ratios.utils.capital_allocation`)
- Quantitative framework measuring how effectively management deploys capital
- Four weighted signals: Value Creation / ROIC vs WACC (35%), FCF Quality (25%), Reinvestment Yield (25%), Payout Discipline (15%)
- `capital_allocation_score_from_series(annual_data, wacc=None)` — compute from any sequence of annual dicts/objects (oldest-first)
- `capital_allocation_score(ticker, years=10, source='yahoo')` — convenience wrapper that fetches multi-year data
- `CapitalAllocationScore` dataclass: `score` (0–100), `rating` ('excellent'/'good'/'fair'/'poor'), `components`, `wacc_used`, `years_analyzed`, `evidence`, `.table()`, `._repr_html_()`, `.to_dict()`, `.interpretation`
- WACC auto-estimation from capital structure (CAPM cost of equity + after-tax cost of debt), clamped [6%, 20%]
- Alias resolution for common field name variants (`operating_income` → `ebit`, `long_term_debt` → `total_debt`, etc.)
- Accepts any object with financial attributes — dict, dataclass, fetcher output
- TypeScript: `capitalAllocationScore(annualData, options?)` → `CapitalAllocationResult`
- 20 new tests; total suite: 241 passed, 5 skipped

**References:** Koller, Goedhart & Wessels (2020) — Valuation (7th ed.), McKinsey & Company; Mauboussin (2012) — The True Measures of Success, HBR

---

## [0.7.0] — 2026-03-11

### Added

**Quality Factor Score** (`fin_ratios.utils.quality_score`)
- Composite 0–100 score combining Earnings Quality (35%), Moat Score (35%), and Capital Allocation (30%)
- Maps to the QMJ (Quality Minus Junk) factor — Asness, Frazzini & Pedersen (2019)
- `quality_score_from_series(annual_data, wacc=None)` — compute from list of annual dicts/objects
- `quality_score(ticker, years=10, source='yahoo')` — fetches multi-year data and computes score
- `QualityFactorScore` dataclass: `score` (0–100), `grade` ('exceptional'/'strong'/'moderate'/'weak'/'poor'), `components`, `sub_scores` (full sub-score objects for drill-down), `.table()`, `._repr_html_()`, `.to_dict()`
- TypeScript: `qualityScore(annualData, options?)` → `QualityFactorResult`

**Portfolio Quality Aggregation** (`fin_ratios.utils.portfolio`)
- `portfolio_quality_from_series(holdings_data: dict[str, tuple[float, list]], wacc=None)` — weighted quality analysis from pre-loaded data
- `portfolio_quality(holdings: dict[str, float], years=10, source='yahoo', wacc=None)` — fetches data and scores each holding
- `PortfolioQuality` dataclass: weighted portfolio score, per-holding `HoldingQuality` results, top/bottom holding rankings, diversification notes
- Robust error handling: failed holdings excluded from weighted average with errors reported
- TypeScript: `portfolioQuality(holdings: HoldingInput[], options?)` → `PortfolioQualityResult`

**TypeScript test suite** (`typescript/src/__tests__/`)
- 89 tests across 6 test files covering all major scoring utilities and core ratios
- `ratios.test.ts` — 38 tests covering valuation, profitability, liquidity, solvency, cash flow, growth, risk, composite
- `capital-allocation.test.ts` — 9 tests
- `earnings-quality.test.ts` — 8 tests
- `moat-score.test.ts` — 8 tests
- `fair-value.test.ts` — 10 tests
- `quality-score.test.ts` — 16 tests (includes portfolioQuality)

**Sector benchmarks expansion** (`fin_ratios.utils.benchmarks`)
- Added moat score, capital allocation score, earnings quality score, and quality factor score distributions (p25/p50/p75) for all 11 GICS sectors + S&P 500 broad market
- `SectorBenchmarks` dataclass now includes `moat_score_median`, `capital_allocation_median`, `earnings_quality_median`, `quality_score_median`
- `percentile_rank()` now works with all four new score metrics

**References:** Asness, Frazzini & Pedersen (2019) — Quality Minus Junk, *Review of Accounting Studies*

---

## [0.6.0] — 2026-03-11

### Added

**Fair Value Range** (`fin_ratios.utils.fair_value`)
- Multi-method intrinsic value estimator using up to five approaches simultaneously
- Methods: 2-Stage DCF, Graham Number, FCF Yield Target, EV/EBITDA Comps, Earnings Power Value
- Returns bear (p25), base (trimmed mean), and bull (p75) per-share value ranges
- `fair_value_range(*, fcf, shares, growth_rate, ...)` — flexible keyword-only API; raises `ValueError` only if zero methods can compute
- `FairValueRange` dataclass: `bear`, `base`, `bull` per-share values; `upside_pct` and `margin_of_safety` when current price provided; `.table()`, `._repr_html_()`, `.to_dict()`
- TypeScript: `fairValueRange(options: FairValueOptions)` → `FairValueRange`

**References:** Graham & Dodd (1934), Koller, Goedhart & Wessels (2020)

---

## [0.5.0] — 2026-03-11

### Added

**Earnings Quality Score** (`fin_ratios.utils.earnings_quality`)
- Five-signal quantitative earnings quality framework
- Signals: Accruals Ratio (30%), Cash Earnings Quality (25%), Revenue Recognition (20%), Gross Margin Stability (15%), Asset Efficiency Trend (10%)
- `earnings_quality_score_from_series(annual_data)` — compute from list of annual dicts/objects (oldest-first)
- `earnings_quality_score(ticker, years=10, source='yahoo')` — convenience wrapper with auto data fetch
- `EarningsQualityScore` dataclass: `score` (0–100), `rating` ('high'/'medium'/'low'/'poor'), `components`, `years_analyzed`, `evidence`, `.table()`, `._repr_html_()`, `.to_dict()`, `.interpretation`
- Accepts any object with financial attributes — dict, dataclass, fetcher output
- TypeScript: `earningsQualityScore(annualData, options?)` → `EarningsQualityResult`
- 16 new Python tests; TypeScript test suite

**References:** Sloan (1996) — accrual anomaly; Richardson et al. (2005); Novy-Marx (2013) — gross profitability

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
