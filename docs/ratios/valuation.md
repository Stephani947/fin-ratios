# Valuation Ratios

Measures the market price of a stock relative to its fundamentals.

## Price-Based Ratios

### `pe` — Price / Earnings

```python
pe(market_cap, net_income) -> float | None
```

Formula: `Market Cap / Net Income`

```python
from fin_ratios import pe
pe(market_cap=3e12, net_income=1e11)  # 30.0
```

---

### `forward_pe` — Forward P/E

```python
forward_pe(market_cap, forward_earnings) -> float | None
```

Formula: `Market Cap / Forward Earnings`

---

### `peg` — Price/Earnings to Growth

```python
peg(pe_ratio, eps_growth_rate_pct) -> float | None
```

Formula: `P/E Ratio / EPS Growth Rate (%)`. PEG < 1 is often considered undervalued.

---

### `pb` — Price / Book

```python
pb(market_cap, total_equity) -> float | None
```

Formula: `Market Cap / Book Value of Equity`

---

### `ps` — Price / Sales

```python
ps(market_cap, revenue) -> float | None
```

Formula: `Market Cap / Revenue`

---

### `p_fcf` — Price / Free Cash Flow

```python
p_fcf(market_cap, operating_cash_flow, capex) -> float | None
```

Formula: `Market Cap / (OCF − CapEx)`

---

## Enterprise Value Ratios

### `enterprise_value`

```python
enterprise_value(market_cap, total_debt, cash, minority_interest=0, preferred_stock=0) -> float
```

Formula: `Market Cap + Total Debt − Cash + Minority Interest + Preferred Stock`

---

### `ev_ebitda`

```python
ev_ebitda(ev, ebitda) -> float | None
```

Formula: `Enterprise Value / EBITDA`. <8x is cheap; >20x is expensive.

---

### `ev_ebit`

```python
ev_ebit(ev, ebit) -> float | None
```

---

### `ev_revenue`

```python
ev_revenue(ev, revenue) -> float | None
```

---

### `ev_fcf`

```python
ev_fcf(ev, free_cash_flow) -> float | None
```

---

## Intrinsic Value

### `graham_number`

```python
graham_number(eps, book_value_per_share) -> float | None
```

Formula: `√(22.5 × EPS × Book Value per Share)`. Benjamin Graham's fair-value estimate for defensive investors.

---

### `graham_intrinsic_value`

```python
graham_intrinsic_value(eps, growth_rate_pct, risk_free_rate=0.044) -> float | None
```

Formula: `EPS × (8.5 + 2g) × 4.4 / AAA_yield`

---

### `tobin_q`

```python
tobin_q(market_cap, total_liabilities, total_assets) -> float | None
```

Formula: `(Market Cap + Total Liabilities) / Total Assets`. Q > 1 suggests the market values assets above replacement cost.

---

## DCF Models

See [Valuation DCF](../utils/scenario-dcf.md) for `dcf_2_stage`, `gordon_growth_model`, and `reverse_dcf`.

## TypeScript

All ratios use camelCase: `pe`, `forwardPe`, `peg`, `pb`, `ps`, `pFcf`, `enterpriseValue`, `evEbitda`, `evEbit`, `evRevenue`, `evFcf`, `grahamNumber`, `grahamIntrinsicValue`, `tobinQ`.

```typescript
import { pe, pb, evEbitda, grahamNumber } from 'fin-ratios'

pe({ marketCap: 3e12, netIncome: 1e11 })        // 30.0
pb({ marketCap: 3e12, totalEquity: 3e11 })       // 10.0
evEbitda({ enterpriseValue: 2.5e12, ebitda: 1e11 }) // 25.0
```
