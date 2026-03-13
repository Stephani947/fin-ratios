# Solvency Ratios

Measures a company's ability to meet long-term obligations and survive financial stress.

## Leverage Ratios

### `debt_to_equity`

```python
debt_to_equity(total_debt, total_equity) -> float | None
```

Formula: `Total Debt / Total Equity`

---

### `net_debt_to_equity`

```python
net_debt_to_equity(total_debt, cash, total_equity) -> float | None
```

Formula: `(Total Debt − Cash) / Total Equity`

---

### `net_debt_to_ebitda`

```python
net_debt_to_ebitda(total_debt, cash, ebitda) -> float | None
```

Formula: `(Total Debt − Cash) / EBITDA`. <2x considered safe; >4x is high leverage.

---

### `debt_to_assets`

```python
debt_to_assets(total_debt, total_assets) -> float | None
```

Formula: `Total Debt / Total Assets`

---

### `debt_to_capital`

```python
debt_to_capital(total_debt, total_equity) -> float | None
```

Formula: `Total Debt / (Total Debt + Total Equity)`

---

### `equity_multiplier`

```python
equity_multiplier(total_assets, total_equity) -> float | None
```

Formula: `Total Assets / Total Equity`. The leverage factor in DuPont decomposition.

---

## Coverage Ratios

### `interest_coverage_ratio`

```python
interest_coverage_ratio(ebit, interest_expense) -> float | None
```

Formula: `EBIT / Interest Expense`. ICR > 3x is generally healthy; <1.5x is distress territory.

---

### `ebitda_coverage_ratio`

```python
ebitda_coverage_ratio(ebitda, interest_expense) -> float | None
```

Formula: `EBITDA / Interest Expense`. More lenient than ICR; commonly used by lenders.

---

### `debt_service_coverage_ratio`

```python
debt_service_coverage_ratio(net_operating_income, total_debt_service) -> float | None
```

Formula: `Net Operating Income / Total Debt Service (principal + interest)`. DSCR > 1.25x is typical bank covenant.

---

## TypeScript

```typescript
import { debtToEquity, netDebtToEbitda, interestCoverageRatio } from 'fin-ratios'

debtToEquity({ totalDebt: 90e9, totalEquity: 60e9 })      // 1.5
netDebtToEbitda({ totalDebt: 90e9, cash: 30e9, ebitda: 80e9 })  // 0.75
interestCoverageRatio({ ebit: 70e9, interestExpense: 5e9 })     // 14.0
```
