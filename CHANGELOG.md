# Changelog

All notable changes to fin-ratios are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- CLI tool: `fin-ratios AAPL` — instant terminal analysis with live Yahoo Finance data
- Composite Health Score (0–100) combining Piotroski, Altman, ROIC, FCF quality
- Industry benchmarks and percentile ranking by sector
- Stock screening API: `screen(universe, filters)`
- GitHub Actions CI for Python 3.9–3.12 and Node 18–22
- Full pytest test suite for Python
- Full vitest test suite for TypeScript

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
