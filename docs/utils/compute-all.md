# Batch Compute

Computes all applicable ratios from a single data object in one call.

## Usage

```python
from fin_ratios.utils.compute_all import compute_all

data = {
    'revenue': 300e9,
    'gross_profit': 120e9,
    'ebit': 75e9,
    'net_income': 65e9,
    'operating_cash_flow': 80e9,
    'capex': 8e9,
    'total_assets': 300e9,
    'total_equity': 62e9,
    'total_debt': 90e9,
    'cash': 30e9,
    'current_assets': 110e9,
    'current_liabilities': 75e9,
    'depreciation': 12e9,
    'income_tax_expense': 16e9,
    'ebt': 77e9,
    'market_cap': 3e12,
}

# Optional: prior year data unlocks Piotroski, growth rates, etc.
prior = {'revenue': 275e9, 'gross_profit': 106e9, ...}

ratios = compute_all(data, prior=prior)

print(ratios['pe'])             # 46.15
print(ratios['gross_margin'])   # 0.40
print(ratios['roic'])           # 0.14
print(ratios['fcf_margin'])     # 0.24
print(ratios['current_ratio'])  # 1.47
```

## What's Computed

`compute_all` returns a flat dict with 40+ ratio keys:

**Valuation**: `pe`, `pb`, `ps`, `p_fcf`, `ev_ebitda`, `ev_revenue`
**Profitability**: `gross_margin`, `operating_margin`, `net_profit_margin`, `ebitda_margin`, `roe`, `roa`, `roic`
**Liquidity**: `current_ratio`, `quick_ratio`, `cash_ratio`
**Solvency**: `debt_to_equity`, `net_debt_to_ebitda`, `interest_coverage_ratio`
**Cash Flow**: `free_cash_flow`, `fcf_margin`, `fcf_yield`, `fcf_conversion`
**Growth** (requires `prior`): `revenue_growth`, `eps_growth`
**Composite** (requires `prior`): `piotroski_score`, `altman_z_score`
**Health Score**: `health_score` (0–100)

## Notes

- Unknown or missing fields are gracefully skipped — no exception raised
- Returns `None` for any ratio where required inputs are absent
- Accepts dicts, dataclasses, or any object with matching attributes
