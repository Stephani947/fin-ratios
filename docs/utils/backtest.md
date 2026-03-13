# Backtesting

Simulate a quality-based investment strategy over historical data to evaluate its performance.

## Usage

```python
from fin_ratios.utils.backtest import backtest_quality_strategy, summarize_backtest

# companies: list of (ticker, annual_data) tuples
companies = [
    ('AAPL', fetch_edgar('AAPL', num_years=10)),
    ('MSFT', fetch_edgar('MSFT', num_years=10)),
    ('GOOGL', fetch_edgar('GOOGL', num_years=10)),
    # ...
]

result = backtest_quality_strategy(
    companies=companies,
    threshold=60,          # minimum quality score to "invest"
    score_fn='quality',    # quality | moat | capital_allocation | earnings_quality | management
    wacc=0.09,
)

print(summarize_backtest(result))
# Strategy CAGR:    14.2%
# Benchmark CAGR:   10.8%
# Excess CAGR:       3.4%
# Sharpe:            0.94
# Max Drawdown:     18.3%
# Hit Rate:         67.5%
```

## Output: `BacktestResult`

```python
@dataclass
class BacktestResult:
    strategy_cagr: float
    benchmark_cagr: float
    excess_cagr: float
    strategy_sharpe: float
    max_drawdown: float
    hit_rate: float
    annual_results: list[dict]   # year-by-year detail
    threshold: int
    score_fn_name: str
    years: int
```

## Notes

- Revenue growth is used as the return proxy (actual stock prices not required)
- The benchmark is the equal-weighted average return of all companies
- Results reflect the quality of the financial data, not actual trading performance
- Use this to validate whether high-quality companies outperform in your dataset, not for live trading decisions
