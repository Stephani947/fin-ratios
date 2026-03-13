# Liquidity Ratios

Measures a company's ability to meet short-term obligations.

## Coverage Ratios

### `current_ratio`

```python
current_ratio(current_assets, current_liabilities) -> float | None
```

Formula: `Current Assets / Current Liabilities`. Healthy range: 1.5–3.0.

---

### `quick_ratio`

```python
quick_ratio(cash, short_term_investments, accounts_receivable, current_liabilities) -> float | None
```

Formula: `(Cash + ST Investments + Receivables) / Current Liabilities`. Excludes inventory.

---

### `cash_ratio`

```python
cash_ratio(cash, short_term_investments, current_liabilities) -> float | None
```

Formula: `(Cash + ST Investments) / Current Liabilities`. Most conservative liquidity measure.

---

### `operating_cash_flow_ratio`

```python
operating_cash_flow_ratio(operating_cash_flow, current_liabilities) -> float | None
```

Formula: `OCF / Current Liabilities`. Uses actual cash generation rather than accrual-based balances.

---

### `defensive_interval_ratio`

```python
defensive_interval_ratio(cash, short_term_investments, accounts_receivable, daily_operating_expenses) -> float | None
```

Formula: `(Cash + ST Investments + Receivables) / Daily Operating Expenses`. Days the company can operate without additional revenue.

---

## Working Capital Cycle

### `dso` — Days Sales Outstanding

```python
dso(accounts_receivable, revenue, days=365) -> float | None
```

Formula: `Accounts Receivable / Revenue × Days`. Lower is faster collection.

---

### `dio` — Days Inventory Outstanding

```python
dio(inventory, cogs, days=365) -> float | None
```

Formula: `Inventory / COGS × Days`. Lower means inventory turns faster.

---

### `dpo` — Days Payable Outstanding

```python
dpo(accounts_payable, cogs, days=365) -> float | None
```

Formula: `Accounts Payable / COGS × Days`. Higher means longer to pay suppliers.

---

### `cash_conversion_cycle`

```python
cash_conversion_cycle(dso_days, dio_days, dpo_days) -> float | None
```

Formula: `DSO + DIO − DPO`. Negative CCC (e.g. Amazon, Costco) means suppliers fund operations.

---

## TypeScript

```typescript
import { currentRatio, quickRatio, cashConversionCycle } from 'fin-ratios'

currentRatio({ currentAssets: 120e9, currentLiabilities: 80e9 })  // 1.5

quickRatio({
  cash: 30e9,
  shortTermInvestments: 10e9,
  accountsReceivable: 20e9,
  currentLiabilities: 80e9,
})  // 0.75

cashConversionCycle({ dso: 45, dio: 60, dpo: 30 })  // 75
```
