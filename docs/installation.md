# Installation

## Python

```bash
# Core library (zero runtime dependencies)
pip install financial-ratios

# With data fetchers (Yahoo Finance, httpx)
pip install "financial-ratios[fetchers]"

# With REST API (FastAPI + uvicorn)
pip install "financial-ratios[api]"

# With MCP server for AI agents (Claude Desktop)
pip install "financial-ratios[mcp]"

# With Pandas/Polars DataFrame integration
pip install "financial-ratios[pandas]"

# Everything
pip install "financial-ratios[all]"
```

**Requires Python ≥ 3.9**

## TypeScript / JavaScript

```bash
npm install fin-ratios
# or
yarn add fin-ratios
# or
pnpm add fin-ratios
```

**Requires Node.js ≥ 18**

## Verify Installation

=== "Python"

    ```python
    import fin_ratios
    print(fin_ratios.__version__)
    # → 0.9.x

    from fin_ratios import pe
    result = pe(market_cap=3_000_000_000_000, net_income=100_000_000_000)
    print(result)  # → 30.0
    ```

=== "TypeScript"

    ```typescript
    import { pe } from 'fin-ratios'
    const result = pe({ marketCap: 3e12, netIncome: 1e11 })
    console.log(result)  // → 30
    ```

## Zero Dependencies (Core)

The core ratio functions have **no runtime dependencies** in either Python or TypeScript. You only need to install extras if you want:

| Feature | Python extra | TypeScript |
|---------|-------------|------------|
| Data fetchers | `[fetchers]` | built-in (uses `fetch`) |
| REST API | `[api]` | — |
| MCP server | `[mcp]` | — |
| DataFrame integration | `[pandas]` | — |

## Development Setup

```bash
git clone https://github.com/piyushgupta344/fin-ratios
cd fin-ratios

# Python
pip install -e "./python[dev]"
pytest python/tests/

# TypeScript
cd typescript && npm install
npm test
```
