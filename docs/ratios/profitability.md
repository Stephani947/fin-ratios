# Profitability Ratios

Measures how efficiently a company generates profit from its resources.

## Margin Ratios

### `gross_margin`

```python
gross_margin(gross_profit, revenue) -> float | None
```

Formula: `Gross Profit / Revenue`

---

### `operating_margin`

```python
operating_margin(ebit, revenue) -> float | None
```

Formula: `EBIT / Revenue`

---

### `ebitda_margin`

```python
ebitda_margin(ebitda, revenue) -> float | None
```

Formula: `EBITDA / Revenue`

---

### `net_profit_margin`

```python
net_profit_margin(net_income, revenue) -> float | None
```

Formula: `Net Income / Revenue`

---

## Return Ratios

### `roe` — Return on Equity

```python
roe(net_income, avg_total_equity) -> float | None
```

Formula: `Net Income / Avg. Shareholders' Equity`

!!! warning
    Pass **average** equity (beginning + ending / 2), not ending-period equity.

---

### `roa` — Return on Assets

```python
roa(net_income, avg_total_assets) -> float | None
```

Formula: `Net Income / Avg. Total Assets`

---

### `roic` — Return on Invested Capital

```python
roic(nopat_value, invested_capital) -> float | None
```

Formula: `NOPAT / Invested Capital`

---

### `roce` — Return on Capital Employed

```python
roce(ebit, capital_employed) -> float | None
```

Formula: `EBIT / (Total Assets − Current Liabilities)`

---

### `rote` — Return on Tangible Equity

```python
rote(net_income, avg_tangible_equity) -> float | None
```

---

### `nopat` — Net Operating Profit After Tax

```python
nopat(ebit, tax_rate) -> float | None
```

Formula: `EBIT × (1 − Tax Rate)`

---

### `invested_capital`

```python
invested_capital(total_equity, total_debt, cash) -> float
```

Formula: `Total Equity + Total Debt − Cash`

---

## Decomposition

### `du_pont_3` — 3-Factor DuPont

```python
du_pont_3(net_income, revenue, avg_total_assets, avg_total_equity) -> dict
```

Returns: `{'net_margin': ..., 'asset_turnover': ..., 'leverage': ..., 'roe': ...}`

---

## Productivity

### `revenue_per_employee`

```python
revenue_per_employee(revenue, headcount) -> float | None
```

### `profit_per_employee`

```python
profit_per_employee(net_income, headcount) -> float | None
```

---

## TypeScript

```typescript
import { roe, roic, grossMargin, duPont3 } from 'fin-ratios'

roe({ netIncome: 65e9, avgTotalEquity: 60e9 })          // 1.083
roic({ nopat: 70e9, investedCapital: 500e9 })            // 0.14
grossMargin({ grossProfit: 120e9, revenue: 300e9 })      // 0.40
```
