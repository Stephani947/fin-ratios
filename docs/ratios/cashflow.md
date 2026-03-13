# Cash Flow Ratios

Cash flow ratios are among the most reliable financial metrics because cash is harder to manipulate than accrual-based earnings.

## Free Cash Flow

### `free_cash_flow`

```python
free_cash_flow(operating_cash_flow, capex) -> float | None
```

Formula: `OCF − CapEx`

---

### `fcf_margin`

```python
fcf_margin(fcf, revenue) -> float | None
```

Formula: `FCF / Revenue`. FCF margin > 15% is considered excellent.

---

### `fcf_yield`

```python
fcf_yield(fcf, market_cap) -> float | None
```

Formula: `FCF / Market Cap`. FCF yield > 5% is often considered attractive.

---

### `fcf_conversion`

```python
fcf_conversion(fcf, net_income) -> float | None
```

Formula: `FCF / Net Income`. Values close to 1.0 indicate earnings are cash-backed. >1.0 means cash exceeds earnings (often positive); <0.5 is a warning sign.

---

## Owner Earnings

### `owner_earnings`

```python
owner_earnings(net_income, depreciation, capex, working_capital_change=0) -> float | None
```

Formula: `Net Income + D&A − CapEx ± ΔWorking Capital`. Buffett's preferred measure of normalised cash generation.

---

## DCF-Related

### `dcf_2_stage`

```python
dcf_2_stage(
    fcf, growth_rate_stage1, growth_rate_stage2,
    wacc, stage1_years=5, terminal_growth=0.03
) -> float | None
```

See [Scenario DCF](../utils/scenario-dcf.md) for full documentation.

---

## TypeScript

```typescript
import { freeCashFlow, fcfMargin, fcfYield, fcfConversion } from 'fin-ratios'

freeCashFlow({ operatingCashFlow: 80e9, capex: 8e9 })    // 72e9
fcfMargin({ freeCashFlow: 72e9, revenue: 300e9 })         // 0.24
fcfYield({ freeCashFlow: 72e9, marketCap: 3e12 })         // 0.024
fcfConversion({ freeCashFlow: 72e9, netIncome: 65e9 })    // 1.108
```
