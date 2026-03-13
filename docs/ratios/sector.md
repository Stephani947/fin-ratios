# Sector Ratios

Specialised ratios for industries where standard metrics are insufficient.

## SaaS / Software

Import: `from fin_ratios.ratios.sector.saas import *`

### `rule_of_40`

```python
rule_of_40(revenue_growth_pct, profit_margin_pct) -> float | None
```

Formula: `Revenue Growth % + Profit Margin %`. Rule of 40: healthy SaaS companies score ≥ 40.

### `net_revenue_retention` (NRR)

```python
net_revenue_retention(beginning_arr, expansions, contractions, churn) -> float | None
```

Formula: `(Beginning ARR + Expansions − Contractions − Churn) / Beginning ARR`. NRR > 120% indicates product-led growth.

### `magic_number`

```python
magic_number(net_new_arr, sales_and_marketing_expense) -> float | None
```

Formula: `Net New ARR / S&M Spend`. >0.75 is efficient; >1.0 is excellent.

### `ltv_cac`

```python
ltv_cac(ltv, cac) -> float | None
```

Formula: `LTV / CAC`. >3x is healthy.

### `burn_multiple`

```python
burn_multiple(net_burn, net_new_arr) -> float | None
```

Formula: `Net Burn / Net New ARR`. Lower is more efficient; >2x warrants attention.

---

## REIT

Import: `from fin_ratios.ratios.sector.reit import *`

### `funds_from_operations` (FFO)

```python
funds_from_operations(net_income, depreciation, gains_on_sale=0) -> float | None
```

Formula: `Net Income + Depreciation − Gains on Property Sales`. NAREIT standard.

### `adjusted_ffo` (AFFO)

```python
adjusted_ffo(ffo, capex_maintenance, straight_line_rent=0) -> float | None
```

FFO adjusted for maintenance CapEx and non-cash items.

### `price_to_ffo`

```python
price_to_ffo(market_cap, ffo) -> float | None
```

REIT equivalent of P/E ratio.

### `cap_rate`

```python
cap_rate(noi, property_value) -> float | None
```

Formula: `NOI / Property Value`. Higher cap rate = higher yield but potentially higher risk.

### `net_operating_income` (NOI)

```python
net_operating_income(revenue, operating_expenses) -> float | None
```

### `occupancy_rate`

```python
occupancy_rate(occupied_units, total_units) -> float | None
```

---

## Banking

Import: `from fin_ratios.ratios.sector.banking import *`

### `net_interest_margin` (NIM)

```python
net_interest_margin(net_interest_income, avg_earning_assets) -> float | None
```

### `efficiency_ratio`

```python
efficiency_ratio(non_interest_expense, net_revenue) -> float | None
```

Lower is better. Well-run banks target <55%.

### `non_performing_loan_ratio` (NPL)

```python
non_performing_loan_ratio(non_performing_loans, total_loans) -> float | None
```

### `tier1_capital_ratio`

```python
tier1_capital_ratio(tier1_capital, risk_weighted_assets) -> float | None
```

### `cet1_ratio`

```python
cet1_ratio(common_equity_tier1, risk_weighted_assets) -> float | None
```

Regulatory minimum: 4.5% (Basel III). Well-capitalised: >10%.

---

## Insurance

Import: `from fin_ratios.ratios.sector.insurance import *`

### `loss_ratio`

```python
loss_ratio(claims_paid, premiums_earned) -> float | None
```

Formula: `Claims / Premiums`. <60% is excellent; >100% means underwriting losses.

### `expense_ratio`

```python
expense_ratio(underwriting_expenses, premiums_written) -> float | None
```

### `combined_ratio`

```python
combined_ratio(loss_ratio, expense_ratio) -> float | None
```

Formula: `Loss Ratio + Expense Ratio`. <100% = underwriting profit; >100% = loss.

---

## TypeScript

```typescript
import { ruleOf40, netRevenueRetention } from 'fin-ratios'
import { fundsFromOperations, capRate } from 'fin-ratios'

ruleOf40({ revenueGrowthPct: 35, profitMarginPct: 12 })  // 47 (healthy)
capRate({ noi: 5e6, propertyValue: 70e6 })               // 0.071
```
