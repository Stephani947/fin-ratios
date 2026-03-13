# Composite Scores

Academic multi-factor models that combine several financial ratios into a single score.

## Piotroski F-Score

```python
piotroski_f_score(current, prior) -> dict
```

Nine-point scoring system for financial health. Score ≥ 7 is considered strong; ≤ 3 is weak.

```python
from fin_ratios import piotroski_f_score

result = piotroski_f_score(
    current={
        'roa': 0.08, 'operating_cash_flow': 80e9, 'net_income': 65e9,
        'total_assets': 300e9, 'long_term_debt': 80e9, 'current_ratio': 1.5,
        'shares_outstanding': 15e9, 'gross_margin': 0.38, 'asset_turnover': 0.97,
    },
    prior={
        'roa': 0.07, 'total_assets': 310e9, 'long_term_debt': 88e9,
        'current_ratio': 1.4, 'shares_outstanding': 15.5e9,
        'gross_margin': 0.37, 'asset_turnover': 0.89,
    },
)
print(result['score'])  # 0–9
```

**TypeScript**: `piotroski({ current: {...}, prior: {...} })` — uses nested `current`/`prior` structure.

---

## Altman Z-Score

```python
altman_z_score(
    working_capital, retained_earnings, ebit,
    market_cap, revenue, total_assets, total_liabilities
) -> dict
```

Bankruptcy probability model. Z > 2.99 = safe zone; 1.81–2.99 = grey zone; < 1.81 = distress.

```python
from fin_ratios import altman_z_score

result = altman_z_score(
    working_capital=40e9, retained_earnings=200e9, ebit=70e9,
    market_cap=3e12, revenue=300e9,
    total_assets=300e9, total_liabilities=238e9,
)
print(result['z_score'])
print(result['zone'])   # 'safe' | 'grey' | 'distress'
```

**TypeScript**: `altmanZScore(...)` — result key is `r.z` (not `r.zScore`).

---

## Beneish M-Score

```python
beneish_m_score(current, prior) -> dict
```

Earnings manipulation detection. M-Score > −1.78 suggests possible manipulation.

```python
result = beneish_m_score(current={...}, prior={...})
print(result['m_score'])
print(result['manipulator'])  # True / False
```

---

## Magic Formula

```python
magic_formula(earnings_yield, return_on_capital) -> dict
```

Greenblatt's ranking formula combining earnings yield and return on capital.

---

## Montier C-Score

```python
montier_c_score(current, prior) -> dict
```

Six-point creative accounting detection score. Score ≥ 4 warrants scrutiny.

---

## Ohlson O-Score

```python
ohlson_o_score(...) -> dict
```

Logistic regression bankruptcy model. Returns `probability` (0–1) and `bankrupt` (True/False).

---

## Shiller CAPE

```python
shiller_cape(price, avg_10yr_earnings) -> float | None
```

Cyclically adjusted P/E ratio. Historically, CAPE > 30 has signalled elevated valuations.

---

## TypeScript

```typescript
import { altmanZScore, piotroski } from 'fin-ratios'

const z = altmanZScore({
  workingCapital: 40e9, retainedEarnings: 200e9, ebit: 70e9,
  marketCap: 3e12, revenue: 300e9,
  totalAssets: 300e9, totalLiabilities: 238e9,
})
console.log(z.z)    // numeric Z-score
console.log(z.zone) // 'safe' | 'grey' | 'distress'
```
