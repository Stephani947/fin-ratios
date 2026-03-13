# FastAPI REST Server

fin-ratios includes a built-in FastAPI server exposing all ratios and scoring models via HTTP.

## Installation

```bash
pip install "financial-ratios[api,fetchers]"
```

## Start the Server

```bash
fin-ratios api --port 8000
# → Uvicorn running on http://0.0.0.0:8000
```

Or programmatically:

```python
from fin_ratios.api import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host='0.0.0.0', port=8000)
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/ratios` | Compute individual ratios |
| `POST` | `/score/quality` | Quality Factor Score |
| `POST` | `/score/investment` | Investment Score |
| `POST` | `/score/moat` | Economic Moat Score |
| `POST` | `/score/valuation` | Valuation Attractiveness Score |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/openapi.json` | OpenAPI schema |

## Example: Compute Ratios

```bash
curl -X POST http://localhost:8000/ratios \
  -H "Content-Type: application/json" \
  -d '{
    "ratios": ["pe", "pb", "roe", "roic"],
    "data": {
      "market_cap": 3000000000000,
      "net_income": 100000000000,
      "total_equity": 62000000000,
      "total_assets": 353000000000,
      "nopat_value": 85000000000,
      "invested_capital": 650000000000
    }
  }'
```

## Example: Investment Score

```bash
curl -X POST http://localhost:8000/score/investment \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "source": "edgar",
    "years": 7,
    "pe_ratio": 28.0
  }'
```

## CORS

The server runs with CORS disabled by default (local use). For production:

```python
from fin_ratios.api import create_app
from fastapi.middleware.cors import CORSMiddleware

app = create_app()
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```
