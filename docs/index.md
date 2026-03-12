# fin-ratios

**The most comprehensive open-source financial ratios library.**

136+ ratios · 10 institutional-grade scoring models · TypeScript + Python.

[![npm](https://img.shields.io/npm/v/fin-ratios)](https://npmjs.com/package/fin-ratios)
[![PyPI](https://img.shields.io/pypi/v/financial-ratios)](https://pypi.org/project/financial-ratios/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/piyushgupta344/fin-ratios/blob/main/LICENSE)
[![CI](https://github.com/piyushgupta344/fin-ratios/actions/workflows/ci.yml/badge.svg)](https://github.com/piyushgupta344/fin-ratios/actions/workflows/ci.yml)

---

## What is fin-ratios?

**fin-ratios** is a zero-dependency library that computes financial ratios and institutional-grade scoring models from raw financial statement data. It ships identical APIs for both TypeScript and Python.

Unlike existing libraries that either fetch data (without analysis) or compute a handful of basic ratios, fin-ratios provides:

=== "Python"

    ```python
    from fin_ratios.utils.investment_score import investment_score_from_series
    from fin_ratios.fetchers.edgar import fetch_edgar

    # Fetch 7 years of annual data from SEC EDGAR (free, no key)
    annual_data = fetch_edgar('AAPL', num_years=7)

    # Grand synthesis: Moat + Quality + Valuation + Management → Investment Score
    score = investment_score_from_series(
        annual_data,
        pe_ratio=22.0,
        ev_ebitda=14.0,
    )
    print(f"{score.score}/100  [{score.grade}]  {score.conviction}")
    # → 74/100  [B+]  buy
    ```

=== "TypeScript"

    ```typescript
    import { investmentScoreFromSeries } from 'fin-ratios'
    import { fetchEdgarNormalized } from 'fin-ratios/fetchers/edgar'

    // Fetch from SEC EDGAR (free, no key)
    const annualData = await fetchEdgarNormalized('AAPL', { numYears: 7 })

    // Full investment score
    const score = investmentScoreFromSeries(annualData, {
      peRatio: 22.0,
      evEbitda: 14.0,
    })
    console.log(`${score.score}/100 [${score.grade}] ${score.conviction}`)
    // → 74/100 [B+] buy
    ```

---

## Scoring Models

| Model | Signals | Output | Reference |
|-------|---------|--------|-----------|
| [Economic Moat](scoring/moat.md) | ROIC persistence, pricing power, reinvestment quality | 0–100, wide/narrow/none | Buffett, Mauboussin |
| [Capital Allocation](scoring/capital-allocation.md) | ROIC vs WACC, FCF quality, reinvestment yield | 0–100, excellent–poor | McKinsey Valuation |
| [Earnings Quality](scoring/earnings-quality.md) | Accruals ratio, cash backing, stability | 0–100, high–poor | Sloan (1996), Richardson (2005) |
| [Quality Factor](scoring/quality-factor.md) | EQ + Moat + CA weighted composite | 0–100, A–F grade | Asness et al. (2019) |
| [Valuation Attractiveness](scoring/valuation.md) | Earnings yield, FCF yield, EV/EBITDA, P/B, DCF upside | 0–100, attractive–overvalued | Damodaran (2012) |
| [Management Quality](scoring/management.md) | ROIC trend, margin stability, dilution, execution | 0–100, excellent–poor | Mauboussin (2012) |
| [Dividend Safety](scoring/dividend-safety.md) | FCF payout, earnings payout, debt load, track record | 0–100, safe–danger | Siegel (2014) |
| [Investment Score](scoring/investment.md) | Grand synthesis of all models | 0–100, A+–F, strong buy–sell | — |

---

## Quick Navigation

<div class="grid cards" markdown>

-   :material-lightning-bolt: **[Quick Start](quickstart.md)**

    Install and run your first analysis in under 2 minutes.

-   :material-chart-line: **[Scoring Models](scoring/index.md)**

    Institutional-grade scores from raw financial data.

-   :material-calculator: **[Ratio Reference](ratios/valuation.md)**

    136+ ratios with formulas and academic citations.

-   :material-database: **[Data Fetchers](fetchers/yahoo.md)**

    Yahoo Finance, SEC EDGAR, FMP, Polygon, AlphaVantage, SimFin.

-   :material-console: **[CLI Reference](cli.md)**

    `fin-ratios AAPL`, `fin-ratios score AAPL`, `fin-ratios serve`.

-   :material-language-typescript: **[TypeScript API](typescript.md)**

    Identical API in TypeScript with full type safety.

</div>
