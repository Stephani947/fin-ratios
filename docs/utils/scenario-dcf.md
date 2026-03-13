# Scenario DCF

Three-scenario discounted cash flow model that produces a range of intrinsic value estimates.

## Usage

```python
from fin_ratios.utils.scenario_dcf import scenario_dcf

result = scenario_dcf(
    base_fcf=72e9,        # starting free cash flow
    shares=15.5e9,        # diluted shares outstanding
    scenarios={
        'bear': {'growth': 0.04, 'wacc': 0.12, 'terminal_growth': 0.02},
        'base': {'growth': 0.08, 'wacc': 0.10, 'terminal_growth': 0.03},
        'bull': {'growth': 0.14, 'wacc': 0.09, 'terminal_growth': 0.04},
    },
    stage1_years=5,
)

print(result.bear_value_per_share)  # e.g. $145
print(result.base_value_per_share)  # e.g. $195
print(result.bull_value_per_share)  # e.g. $270

# With current price for margin of safety
result = scenario_dcf(..., current_price=185)
print(result.bear_upside_pct)       # -21.6%
print(result.base_upside_pct)       # +5.4%
print(result.bull_upside_pct)       # +45.9%
```

## Output: `ScenarioDCFResult`

```python
@dataclass
class ScenarioDCFResult:
    bear_value_per_share: float
    base_value_per_share: float
    bull_value_per_share: float
    bear_upside_pct: Optional[float]
    base_upside_pct: Optional[float]
    bull_upside_pct: Optional[float]
    scenario_details: dict   # PV breakdown per scenario
```

## Individual DCF Functions

```python
from fin_ratios.ratios.valuation_dcf import dcf_2_stage, gordon_growth_model, reverse_dcf

# 2-stage DCF
intrinsic = dcf_2_stage(
    fcf=72e9, growth_stage1=0.10, growth_stage2=0.04,
    wacc=0.10, stage1_years=5, terminal_growth=0.03,
)

# Gordon Growth Model (dividend discount)
value = gordon_growth_model(
    dividend=0.96, growth_rate=0.06, cost_of_equity=0.09
)

# Reverse DCF: what growth rate is the current price pricing in?
implied_growth = reverse_dcf(
    market_cap=3e12, fcf=72e9, wacc=0.10,
    terminal_growth=0.03, stage1_years=5,
)
```
