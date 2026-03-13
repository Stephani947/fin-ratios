# Efficiency Ratios

Measures how effectively a company uses its assets to generate revenue.

## Asset Utilisation

### `asset_turnover`

```python
asset_turnover(revenue, avg_total_assets) -> float | None
```

Formula: `Revenue / Avg. Total Assets`. Higher = more revenue per dollar of assets.

!!! note
    Pass **average** assets for accuracy. If only one period is available, pass the ending balance.

---

### `fixed_asset_turnover`

```python
fixed_asset_turnover(revenue, avg_net_ppe) -> float | None
```

Formula: `Revenue / Avg. Net PP&E`

---

### `equity_turnover`

```python
equity_turnover(revenue, avg_total_equity) -> float | None
```

Formula: `Revenue / Avg. Total Equity`

---

## Inventory

### `inventory_turnover`

```python
inventory_turnover(cogs, avg_inventory) -> float | None
```

Formula: `COGS / Avg. Inventory`. Higher = faster inventory turns.

---

## Operating Leverage

### `operating_leverage`

```python
operating_leverage(pct_change_ebit, pct_change_revenue) -> float | None
```

Formula: `% Change in EBIT / % Change in Revenue`. DOL > 1 means profits amplify revenue moves.

---

### `revenue_per_unit_cost`

```python
revenue_per_unit_cost(revenue, total_opex) -> float | None
```

Formula: `Revenue / Total Operating Expenses`

---

## TypeScript

```typescript
import { assetTurnover, inventoryTurnover, operatingLeverage } from 'fin-ratios'

assetTurnover({ revenue: 300e9, avgTotalAssets: 310e9 })     // 0.97
inventoryTurnover({ cogs: 180e9, avgInventory: 6e9 })        // 30.0
```
