# Contributing to fin-ratios

All contributions are welcome — new ratios, bug fixes, fetcher improvements, documentation.

## Quick start

```bash
# Clone the repository
git clone https://github.com/piyushgupta344/fin-ratios.git
cd fin-ratios

# Python setup
# IMPORTANT: hatchling requires README.md and LICENSE to exist in python/
# during editable install. Always run this copy step first.
cp README.md LICENSE python/
pip install -e "./python[dev]"

# Run Python tests
pytest python/tests/ -q --tb=short -m "not network"

# TypeScript setup
cd typescript && npm install

# Run TypeScript tests
npm test
```

## Local quality checks

Before opening a PR, run the same checks CI runs:

```bash
# Python: lint + format
ruff check python/fin_ratios/
ruff format --check python/fin_ratios/

# Python: auto-format (fix in place)
ruff format python/fin_ratios/

# Python: type check
mypy python/fin_ratios/ --ignore-missing-imports

# Python: tests (skip network-dependent tests)
pytest python/tests/ -q --tb=short -m "not network"

# TypeScript: type check
cd typescript && npx tsc --noEmit

# TypeScript: tests
cd typescript && npm test

# TypeScript: build
cd typescript && npm run build
```

## Adding a new ratio

### 1. Pick the right file

| Category | Python file | TypeScript file |
|----------|-------------|-----------------|
| Valuation | `ratios/valuation.py` | `ratios/valuation/` |
| Profitability | `ratios/profitability.py` | `ratios/profitability/` |
| Liquidity | `ratios/liquidity.py` | `ratios/liquidity/` |
| Solvency | `ratios/solvency.py` | `ratios/solvency/` |
| Efficiency | `ratios/efficiency.py` | `ratios/efficiency/` |
| Cash Flow | `ratios/cashflow.py` | `ratios/cashflow/` |
| Growth | `ratios/growth.py` | `ratios/growth/` |
| Risk / Portfolio | `ratios/risk.py` | `ratios/risk/` |
| Composite Scores | `ratios/composite.py` | `ratios/composite/` |
| SaaS | `ratios/sector/saas.py` | `ratios/sector/saas/` |
| REIT | `ratios/sector/reit.py` | `ratios/sector/reit/` |
| Banking | `ratios/sector/banking.py` | `ratios/sector/banking/` |
| Insurance | `ratios/sector/insurance.py` | `ratios/sector/insurance/` |

### 2. Write the function (Python pattern)

```python
def my_new_ratio(numerator: float, denominator: float) -> float | None:
    return safe_divide(numerator, denominator)

my_new_ratio.formula = "Numerator / Denominator"
my_new_ratio.description = "One-sentence explanation of what it measures."
```

Rules:
- **Return `None` on invalid inputs** — never `NaN`, never raise on divide-by-zero
- **Pure function** — no network calls, no file I/O, no global state
- **Named arguments** — `my_ratio(revenue=100, cost=60)` not `my_ratio(100, 60)`
- **Type-annotated** — full Python type hints

### 3. Export it

In `python/fin_ratios/__init__.py`, add your function to the appropriate import block.

### 4. Add the citation

Add an entry to `docs/CITATIONS.md` with:
- The original paper or industry source
- Formula with variable definitions
- Interpretation benchmarks (if known)

### 5. Write at least one test

```python
# python/tests/test_profitability.py
def test_my_new_ratio_basic():
    assert my_new_ratio(numerator=100, denominator=5) == 20.0

def test_my_new_ratio_zero_denominator():
    assert my_new_ratio(numerator=100, denominator=0) is None
```

### 6. Mirror in TypeScript

The TypeScript version should match the Python API 1:1 (snake_case → camelCase).

```typescript
export function myNewRatio({ numerator, denominator }: {
  numerator: number
  denominator: number
}): number | null {
  return safeDivide(numerator, denominator)
}
myNewRatio.formula = 'Numerator / Denominator'
myNewRatio.description = 'One-sentence explanation.'
```

## Testing

```bash
# Python
cd python
pytest tests/ -v

# TypeScript
cd typescript
npm test
```

## Commit style

```
feat: add Montier C-Score to composite ratios
fix: beneish_m_score returns None when cashFlowFromOps is missing
docs: add citation for Omega ratio
```

## Pull request process

1. Fork and create a branch from `main`
2. Run all local checks (lint, format, typecheck, tests)
3. Open a PR — CI will run automatically
4. A maintainer will review within a few days

## What we won't add

- Ratios that require proprietary data with no free alternative
- Macroeconomic indicators (not company-level ratios)
- Technical analysis indicators (RSI, MACD — out of scope)
- Functions that make network calls in the core module

## Questions?

Open a GitHub Discussion or file an issue with the `question` label.
