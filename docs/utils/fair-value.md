# Fair Value Range

Computes a bear/base/bull intrinsic value range using five complementary valuation methods.

## Usage

```python
from fin_ratios.utils.fair_value import fair_value_range

result = fair_value_range(
    annual_data=annual_data,           # list of annual dicts (oldest first)
    current_price=185.0,               # current stock price
    shares_outstanding=15.5e9,
    market_cap=2.87e12,
    wacc=0.09,
    pe_ratio=28.0,                     # optional; used in relative valuation
    ev_ebitda=18.0,                    # optional
)

print(result.bear)   # per-share bear case
print(result.base)   # per-share base case
print(result.bull)   # per-share bull case

print(result.base_upside_pct)  # % upside vs current_price
print(result.margin_of_safety) # % discount to base case

print(result.table())
```

## Methods Used

| Method | Description |
|--------|-------------|
| DCF 2-Stage | Bear/base/bull growth rate scenarios |
| Gordon Growth Model | Dividend discount (if dividends paid) |
| EV/EBITDA Multiple | Sector-relative multiple valuation |
| P/E Multiple | Earnings-based peer multiple |
| Graham Number | Conservative defensive value |

## Output: `FairValueRange`

```python
@dataclass
class FairValueRange:
    bear: float
    base: float
    bull: float
    current_price: Optional[float]
    base_upside_pct: Optional[float]
    margin_of_safety: Optional[float]
    method_detail: dict   # per-method breakdown
```
