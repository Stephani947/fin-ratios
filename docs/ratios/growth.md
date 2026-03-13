# Growth Ratios

Measures the rate at which a company is expanding its business.

## Revenue

### `revenue_growth`

```python
revenue_growth(revenue_current, revenue_prior) -> float | None
```

Formula: `(Current − Prior) / |Prior|`. Returns decimal (e.g. `0.12` for 12%).

---

### `revenue_cagr` — Compound Annual Growth Rate

```python
revenue_cagr(revenue_start, revenue_end, years) -> float | None
```

Formula: `(revenue_end / revenue_start) ^ (1 / years) − 1`

---

## Earnings

### `eps_growth`

```python
eps_growth(eps_current, eps_prior) -> float | None
```

Formula: `(EPS_current − EPS_prior) / |EPS_prior|`

---

### `cagr` — Generic CAGR

```python
cagr(start_value, end_value, years) -> float | None
```

General-purpose compounded growth rate for any metric.

---

## Intrinsic Value via Growth

### `epv` — Earnings Power Value

```python
epv(normalized_earnings, cost_of_capital) -> float | None
```

Formula: `Earnings / Cost of Capital`. Value under zero-growth assumption (Greenwald, 2004).

---

## TypeScript

```typescript
import { revenueGrowth, revenueCAGR, epsGrowth } from 'fin-ratios'

revenueGrowth({ revenueCurrent: 294e9, revenuePrior: 275e9 })   // 0.069
revenueCAGR({ revenueStart: 200e9, revenueEnd: 294e9, years: 4 })  // 0.101
```
