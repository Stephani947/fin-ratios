# Quantitative Economic Moat Score

The first open-source, formula-based economic moat rating derived entirely from
financial statements. No analyst opinions. No qualitative judgement. Fully reproducible —
the same data always produces the same score.

---

## Background

Warren Buffett popularised the concept of an "economic moat" — a durable competitive
advantage that protects a business from rivals and allows it to sustain above-normal
returns on capital over time. Identifying moats is central to quality investing, but
the concept has historically resisted quantification.

Morningstar publishes moat ratings (Wide / Narrow / None) for thousands of stocks, but
their methodology is proprietary, analyst-assigned, and opaque. No open-source,
reproducible equivalent exists.

This implementation quantifies moat from five financial signals that have been shown in
academic literature to correlate with durable competitive advantage — all computable
directly from annual financial statements.

---

## How It Works

The score is a weighted combination of five signals, each scored 0–1:

```
MoatScore = 0.30 × ROIC_Persistence
          + 0.25 × Pricing_Power
          + 0.20 × Reinvestment_Quality
          + 0.15 × Operating_Leverage
          + 0.10 × CAP_Estimate

Final score = round(MoatScore × 100)  →  0–100
```

### Signal 1 — ROIC Persistence (weight: 30%)

The single strongest financial signal of a moat is sustained above-WACC returns on
invested capital. A company that earns 30% ROIC in one year might be lucky. One that
earns 30% ROIC for ten years in a row almost certainly has structural advantages.

**Formula:**
```
fraction_above = years where ROIC > WACC / total years
volatility_penalty = max(0, 1 − CV(ROIC) × 0.40)
score = fraction_above × volatility_penalty
```

Where CV is the coefficient of variation (std / |mean|). A high but volatile ROIC is
penalised — consistent above-WACC returns are stronger evidence of a moat than
occasional spikes.

**WACC estimation** (when not provided):
```
cost_equity = 4.5% + β × 5.5%   (CAPM; defaults to β=1 → 10%)
cost_debt   = interest_expense / total_debt × (1 − tax_rate)
WACC        = (equity/total_cap) × cost_equity + (debt/total_cap) × cost_debt
              clamped to [6%, 20%]
```

---

### Signal 2 — Pricing Power (weight: 25%)

A company with pricing power can raise prices without losing customers. This shows up
as consistently high gross margins with low year-over-year variance. Software companies
(70–80%+ gross margin) and luxury goods brands score highest; commodity producers and
low-margin retailers score lowest.

**Formula:**
```
level     = clamp((mean_gross_margin − 0.20) / 0.40, 0, 1)
             # 20% → 0.0,  60%+ → 1.0 (linear)
stability = max(0, 1 − CV(gross_margin) × 2.5)
             # Low CV = stable pricing control
trend_adj = clamp(OLS_slope(gross_margin_series) × 10, −0.1, +0.1)
score     = 0.60 × level + 0.40 × stability + trend_adj
```

---

### Signal 3 — Reinvestment Quality (weight: 20%)

How much incremental profit does the business generate per dollar reinvested? A high
incremental return on invested capital (ROIIC) means the business creates value every
time it ploughs money back in — a hallmark of compounders.

**Formula:**
```
net_reinvestment = (capex − depreciation) + Δworking_capital
ROIIC            = ΔEBIT / net_reinvestment   (per period)
score            = clamp(0.30 + mean(ROIIC) × 0.70, 0, 1)
```

**Capital-light detection:** When more than 50% of periods show negative net
reinvestment (i.e. the business grows without meaningful capital deployment), the
function checks whether EBIT is growing anyway. If mean EBIT growth > 5%, the score
is 0.82 — growing with no net reinvestment is itself a strong moat signal (think
software, marketplaces, or asset-light platforms).

---

### Signal 4 — Operating Leverage (weight: 15%)

A business with high fixed costs and low variable costs benefits enormously from
scale. As revenue grows, each incremental dollar flows through to profit at a higher
rate. This structural characteristic is a proxy for scale advantages and barriers to
entry (a new entrant must absorb the same fixed cost base with lower volume).

**Formula:**
```
DOL  = %ΔEBIT / %ΔRevenue   (per year, excluding flat revenue years)
level       = clamp((mean_DOL − 1.0) / 5.0, 0, 1)
consistency = max(0, 1 − CV(DOL) × 0.50)
score       = 0.65 × level + 0.35 × consistency
```

A DOL > 3 indicates a strongly fixed-cost structure. Consistency matters too — an
erratic DOL may reflect accounting noise rather than genuine operating leverage.

---

### Signal 5 — Competitive Advantage Period (weight: 10%)

The CAP is the number of years a company can be expected to sustain above-WACC
returns before competition erodes them back to the cost of capital. It translates
the raw ROIC data into a forward-looking time estimate.

**Formula:**
```
spread = mean_ROIC − WACC

If ROIC is declining (OLS slope < −0.005/yr):
    cap_years = spread / |slope|           # extrapolate to WACC
If ROIC is improving (slope > +0.005/yr):
    cap_years = spread × 80 + 5           # optimistic
If ROIC is stable:
    cap_years = spread × 60 / max(CV, 0.1)  # spread-to-volatility ratio

cap_score = min(cap_years / 20, 1.0)      # normalised: 20+ years → 1.0
```

---

## Score Interpretation

| Score | Width | Meaning |
|-------|-------|---------|
| 70–100 | **Wide** | Durable competitive advantage likely to persist 10+ years |
| 40–69 | **Narrow** | Real but limited or potentially fading advantage |
| 0–39 | **None** | No detectable financial signature of a durable moat |

These thresholds are calibrated so that companies with consistently high, stable ROIC
and strong pricing power (e.g. high-quality software, consumer staples, or dominant
platforms) score Wide, while commodity businesses, capital-intensive cyclicals, and
companies with inconsistent returns score None.

---

## Usage

### Python

```python
from fin_ratios import moat_score, moat_score_from_series

# ── Option 1: from a ticker (fetches 10Y via Yahoo Finance) ──────────────────
result = moat_score('AAPL', years=10)

print(result.score)               # 78
print(result.width)               # 'wide'
print(result.cap_estimate_years)  # 14.3
print(result.wacc_used)           # 0.0823

# ASCII table
print(result.table())
# Moat Score: 78/100  [WIDE]
# ──────────────────────────────────────────────
# Component                    Score    Weight
# ──────────────────────────────────────────────
# ROIC Persistence              91%       30%
# Pricing Power                 72%       25%
# Reinvestment Quality          82%       20%
# Operating Leverage            41%       15%
# CAP Estimate                14.3y      10%
# ──────────────────────────────────────────────
# WACC estimate used            8.2%
# Years of data analyzed          10

# Evidence strings
for e in result.evidence:
    print(' •', e)
# • ROIC exceeded WACC in 10/10 years (100%)
# • Mean ROIC 49.1%  vs  WACC 8.2%  (spread +40.9%)
# • ...

# In Jupyter — renders as color-coded HTML card automatically
result

# ── Option 2: from your own annual data ─────────────────────────────────────
annual_data = [
    {
        'year': 2020,
        'revenue': 274e9, 'gross_profit': 105e9, 'ebit': 66e9,
        'total_equity': 65e9, 'total_debt': 112e9, 'total_assets': 323e9,
        'cash': 38e9, 'capex': 7e9, 'depreciation': 11e9,
        'interest_expense': 2.9e9, 'income_tax_expense': 9.7e9,
        'current_assets': 143e9, 'current_liabilities': 105e9,
    },
    {
        'year': 2021,
        'revenue': 365e9, 'gross_profit': 153e9, 'ebit': 109e9,
        'total_equity': 63e9, 'total_debt': 122e9, 'total_assets': 351e9,
        'cash': 62e9, 'capex': 11e9, 'depreciation': 11e9,
        'interest_expense': 2.6e9, 'income_tax_expense': 14.5e9,
        'current_assets': 134e9, 'current_liabilities': 125e9,
    },
    # ... add more years (5–10 recommended)
]

result = moat_score_from_series(annual_data)
# Optionally override WACC:
result = moat_score_from_series(annual_data, wacc=0.09)

# ── Serialise ────────────────────────────────────────────────────────────────
import json
print(json.dumps(result.to_dict(), indent=2))
```

### TypeScript

```typescript
import { moatScore } from 'fin-ratios'
import type { AnnualFinancialData, MoatScoreResult } from 'fin-ratios'

const annualData: AnnualFinancialData[] = [
  {
    year: 2020,
    revenue: 274e9, grossProfit: 105e9, ebit: 66e9,
    totalEquity: 65e9, totalDebt: 112e9, totalAssets: 323e9,
    cash: 38e9, capex: 7e9, depreciation: 11e9,
    interestExpense: 2.9e9, incomeTaxExpense: 9.7e9,
    currentAssets: 143e9, currentLiabilities: 105e9,
  },
  {
    year: 2021,
    revenue: 365e9, grossProfit: 153e9, ebit: 109e9,
    totalEquity: 63e9, totalDebt: 122e9, totalAssets: 351e9,
    cash: 62e9, capex: 11e9, depreciation: 11e9,
    interestExpense: 2.6e9, incomeTaxExpense: 14.5e9,
    currentAssets: 134e9, currentLiabilities: 125e9,
  },
  // ... more years
]

const result: MoatScoreResult = moatScore(annualData)

console.log(result.score)            // 78
console.log(result.width)            // 'wide'
console.log(result.capEstimateYears) // 14.3
console.log(result.components)
// {
//   roicPersistence: 0.9100,
//   pricingPower: 0.7155,
//   reinvestmentQuality: 0.8200,
//   operatingLeverage: 0.4100,
//   capScore: 0.7150
// }

// Override WACC
const result2 = moatScore(annualData, { wacc: 0.09 })
```

---

## Input Fields

### Required (minimum viable)
| Field | Description |
|-------|-------------|
| `revenue` | Total revenue |
| `gross_profit` | Revenue minus COGS |
| `ebit` | Earnings before interest and tax |
| `total_equity` | Book value of shareholders' equity |
| `total_debt` | Total interest-bearing debt |
| `total_assets` | Total assets |

### Recommended (improve accuracy)
| Field | Used by |
|-------|---------|
| `cash` | WACC (net debt), ROIC (invested capital) |
| `capex` | Reinvestment Quality |
| `depreciation` | Reinvestment Quality |
| `current_assets` | Reinvestment Quality (ΔWC) |
| `current_liabilities` | Reinvestment Quality (ΔWC) |
| `interest_expense` | WACC cost of debt |
| `income_tax_expense` | WACC tax rate, ROIC tax rate |

Missing fields default to zero and are handled gracefully — the relevant signal will
either be skipped or fall back to a neutral score.

---

## Limitations

**Data quality is the binding constraint.** The score is only as good as the financial
data fed into it. Restated financials, non-recurring items, and aggressive accounting
will distort every signal — particularly ROIC and pricing power.

**Minimum 2 years required; 5–10 strongly recommended.** With fewer than 5 years, the
ROIC persistence signal has limited statistical power and the CAP estimate is
unreliable. The signal stabilises significantly around 7–10 years.

**WACC estimation is approximate.** The default CAPM uses β=1 and long-run averages
for the risk-free rate and equity risk premium. For unusual capital structures (very
high leverage, negative equity) or specific industries, override with `wacc=` to
provide a more accurate estimate.

**The score does not capture qualitative moat sources.** Network effects, brand
intangibles, regulatory licences, and switching costs are only visible in the financial
data to the extent they show up in ROIC and margins. A company early in building a
network moat may score lower than its true moat warrants.

**Sector-specific caution:**
- **Banks and insurance companies** — financial metrics work differently; ROIC and
  gross margin are not meaningful in the standard sense
- **Capital-intensive early-stage companies** — high reinvestment phases may
  temporarily suppress ROIC even for strong businesses
- **Holding companies and conglomerates** — consolidated financials may mask
  wide-moat subsidiaries within no-moat businesses

---

## References

- Mauboussin, M.J. & Johnson, P. (1997). *Competitive Advantage Period: The Neglected Value Driver.* Financial Management, 26(2).
- Greenwald, B. & Kahn, J. (2001). *Competition Demystified.* Portfolio/Penguin.
- Koller, T., Goedhart, M. & Wessels, D. (2020). *Valuation: Measuring and Managing the Value of Companies* (7th ed.). McKinsey & Company / Wiley.
- Mauboussin, M.J. (2006). *Common Errors in DCF Models.* Legg Mason Capital Management.
- Piotroski, J.D. (2000). Value Investing: The Use of Historical Financial Statement Information. *Journal of Accounting Research*, 38, 1–41.
