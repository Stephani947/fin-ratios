# Risk & Portfolio Ratios

Risk-adjusted performance metrics for single securities and portfolios.

!!! note
    All functions accept a list of periodic returns (e.g. monthly or daily). Pass `None` or an empty list and the function returns `None`.

## Return Metrics

### `sharpe_ratio`

```python
sharpe_ratio(returns, risk_free_rate=0.0) -> float | None
```

Formula: `(Avg Return − Rf) / Std Dev`. Returns `None` when standard deviation is zero.

---

### `sortino_ratio`

```python
sortino_ratio(returns, risk_free_rate=0.0, target=0.0) -> float | None
```

Like Sharpe but uses downside deviation only. Better for asymmetric return distributions.

---

### `calmar_ratio`

```python
calmar_ratio(returns) -> float | None
```

Formula: `Annualised Return / Max Drawdown`. Higher = better risk/reward for drawdown-averse investors.

---

### `omega_ratio`

```python
omega_ratio(returns, threshold=0.0) -> float | None
```

Probability-weighted ratio of gains to losses above/below a threshold.

---

## Risk Metrics

### `beta`

```python
beta(asset_returns, market_returns) -> float | None
```

Market sensitivity. `beta = 1` moves with market; `< 1` less volatile; `> 1` more volatile.

---

### `alpha`

```python
alpha(asset_returns, market_returns, risk_free_rate=0.0) -> float | None
```

Jensen's alpha — excess return above what CAPM predicts.

---

### `maximum_drawdown`

```python
maximum_drawdown(prices) -> float | None
```

Returns a **positive** decimal (e.g. `0.34` for a 34% peak-to-trough decline). Pass a list of prices, not returns.

---

### `historical_var`

```python
historical_var(returns, confidence=0.95) -> float | None
```

Value at Risk at given confidence level. Returns a **positive** loss value (e.g. `0.03` means 3% loss at the threshold).

---

### `conditional_var` — CVaR / Expected Shortfall

```python
conditional_var(returns, confidence=0.95) -> float | None
```

Expected loss beyond VaR threshold. Always ≥ `historical_var`.

---

### `ulcer_index`

```python
ulcer_index(prices) -> float | None
```

Measures drawdown depth and duration. Lower = smoother equity curve.

---

## TypeScript

```typescript
import { sharpeRatio, maximumDrawdown, historicalVaR } from 'fin-ratios'

// Monthly returns
const returns = [0.02, -0.01, 0.03, -0.005, 0.015, ...]

sharpeRatio({ returns, riskFreeRate: 0.0 })     // Sharpe ratio
maximumDrawdown({ prices: [100, 110, 95, 105] }) // 0.136 (positive)
historicalVaR({ returns, confidence: 0.95 })     // positive loss value
```
