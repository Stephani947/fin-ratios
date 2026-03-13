"""
FastAPI REST API for fin-ratios.

Exposes all ratios as HTTP endpoints with automatic OpenAPI docs.

Usage:
    # Start the server
    fin-ratios api --port 8000

    # Or programmatically
    from fin_ratios.api import app
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

Endpoints:
    GET /ratios/{ticker}                  — all ratios for a ticker
    GET /ratios/{ticker}/{ratio}          — single ratio
    GET /health/{ticker}                  — health score
    GET /history/{ticker}                 — multi-year ratio trends
    GET /peers/{ticker}                   — peer comparison
    GET /screen                           — screen universe with filters
    GET /health                           — API health check
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:
    raise ImportError("FastAPI API requires additional packages: pip install 'fin-ratios[api]'")

from fin_ratios.utils.compute_all import compute_all


app = FastAPI(
    title="fin-ratios API",
    description=(
        "The most comprehensive financial ratios API. "
        "134+ ratios across valuation, profitability, risk, composite scores, and more."
    ),
    version="0.2.0",
    contact={
        "name": "Piyush Gupta",
        "url": "https://github.com/piyushgupta344/fin-ratios",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _fetch_data(ticker: str, source: str = "yahoo") -> Any:
    """Fetch most recent financials for a ticker."""
    t = ticker.upper()
    if source == "edgar":
        try:
            from fin_ratios.fetchers.edgar import fetch_edgar

            filings = fetch_edgar(t, num_years=1)
            if not filings:
                raise HTTPException(status_code=404, detail=f"No EDGAR data for {t}")
            return filings[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"EDGAR fetch failed: {e}")
    else:
        try:
            from fin_ratios.fetchers.yahoo import fetch_yahoo

            return fetch_yahoo(t)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Yahoo fetch failed: {e}")


def _clean(val: Any) -> Any:
    """Make a value JSON-serializable (replace nan/inf with null)."""
    import math

    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if isinstance(val, dict):
        return {k: _clean(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_clean(v) for v in val]
    return val


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/health", tags=["Meta"])
async def api_health() -> dict:
    """API liveness check."""
    return {"status": "ok", "version": "0.2.0"}


@app.get("/ratios/{ticker}", tags=["Ratios"])
async def get_all_ratios(
    ticker: str,
    source: str = Query("yahoo", description="Data source: 'yahoo' or 'edgar'"),
) -> JSONResponse:
    """
    Compute all applicable ratios for a ticker.

    Returns a flat dict with 40+ ratios. Complex scores (Altman, Piotroski)
    are nested dicts. Unavailable ratios return null.
    """
    data = _fetch_data(ticker, source)
    ratios = compute_all(data)
    return JSONResponse(content=_clean({"ticker": ticker.upper(), "ratios": ratios}))


@app.get("/ratios/{ticker}/{ratio}", tags=["Ratios"])
async def get_single_ratio(
    ticker: str,
    ratio: str,
    source: str = Query("yahoo", description="Data source"),
) -> JSONResponse:
    """Compute a single named ratio for a ticker."""
    data = _fetch_data(ticker, source)
    ratios = compute_all(data)
    if ratio not in ratios:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown ratio '{ratio}'. See /docs for available ratios.",
        )
    return JSONResponse(
        content=_clean(
            {
                "ticker": ticker.upper(),
                "ratio": ratio,
                "value": ratios[ratio],
            }
        )
    )


@app.get("/health/{ticker}", tags=["Health"])
async def get_health_score(
    ticker: str,
    source: str = Query("yahoo", description="Data source"),
) -> JSONResponse:
    """
    Compute the composite health score (0–100) for a ticker.

    Combines Piotroski, Altman, ROIC, margins, FCF quality, and debt metrics.
    """
    data = _fetch_data(ticker, source)
    ratios = compute_all(data)
    score = ratios.get("health_score")
    return JSONResponse(
        content=_clean(
            {
                "ticker": ticker.upper(),
                "health_score": score,
            }
        )
    )


@app.get("/history/{ticker}", tags=["Trends"])
async def get_ratio_history(
    ticker: str,
    metrics: str = Query(
        "roic,fcf_margin,gross_margin,net_margin",
        description="Comma-separated list of metrics",
    ),
    years: int = Query(5, ge=1, le=10, description="Number of annual periods"),
    source: str = Query("edgar", description="Data source: 'edgar' or 'yahoo'"),
) -> JSONResponse:
    """
    Fetch multi-year ratio history and trend analysis for a ticker.

    Returns per-year values, trend direction (improving/stable/deteriorating/volatile),
    and CAGR for each requested metric.
    """
    from fin_ratios.utils.trends import ratio_history

    metric_list = [m.strip() for m in metrics.split(",") if m.strip()]
    try:
        history = ratio_history(ticker, metrics=metric_list, years=years, source=source)  # type: ignore[arg-type]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return JSONResponse(content=_clean(history.to_dict()))


@app.get("/peers/{ticker}", tags=["Peers"])
async def get_peer_comparison(
    ticker: str,
    metrics: str = Query(
        "pe,pb,roic,gross_margin,net_margin,debt_to_equity",
        description="Comma-separated list of metrics",
    ),
    peers: Optional[str] = Query(None, description="Comma-separated peer tickers (optional)"),
    top_n: int = Query(5, ge=1, le=20),
    source: str = Query("edgar", description="Data source"),
) -> JSONResponse:
    """
    Compare a ticker against its peer group on selected metrics.

    Returns per-ticker values plus rank within the peer group.
    """
    from fin_ratios.utils.peers import compare_peers

    metric_list = [m.strip() for m in metrics.split(",") if m.strip()]
    peer_list = [p.strip() for p in peers.split(",")] if peers else None
    try:
        result = compare_peers(ticker, metric_list, peers=peer_list, top_n=top_n, source=source)  # type: ignore[arg-type]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return JSONResponse(content=_clean(result.to_dict()))


@app.get("/screen", tags=["Screening"])
async def screen_stocks(
    tickers: str = Query(..., description="Comma-separated list of tickers to screen"),
    pe_lt: Optional[float] = Query(None, description="P/E less than"),
    pe_gt: Optional[float] = Query(None, description="P/E greater than"),
    roic_gt: Optional[float] = Query(None, description="ROIC greater than (e.g. 0.15 = 15%)"),
    gross_margin_gt: Optional[float] = Query(None, description="Gross margin greater than"),
    debt_to_equity_lt: Optional[float] = Query(None, description="Debt/Equity less than"),
    current_ratio_gt: Optional[float] = Query(None, description="Current ratio greater than"),
    source: str = Query("yahoo", description="Data source"),
) -> JSONResponse:
    """
    Screen a list of tickers against ratio filters.

    Returns tickers that pass all specified filters, with their ratio values.
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    results = []
    for t in ticker_list:
        try:
            data = _fetch_data(t, source)
            ratios = compute_all(data)
        except HTTPException:
            continue
        except Exception:
            continue

        # Apply filters
        filters_passed = True
        if pe_lt is not None and (ratios.get("pe") is None or ratios["pe"] >= pe_lt):
            filters_passed = False
        if pe_gt is not None and (ratios.get("pe") is None or ratios["pe"] <= pe_gt):
            filters_passed = False
        if roic_gt is not None and (ratios.get("roic") is None or ratios["roic"] <= roic_gt):
            filters_passed = False
        if gross_margin_gt is not None and (
            ratios.get("gross_margin") is None or ratios["gross_margin"] <= gross_margin_gt
        ):
            filters_passed = False
        if debt_to_equity_lt is not None and (
            ratios.get("debt_to_equity") is None or ratios["debt_to_equity"] >= debt_to_equity_lt
        ):
            filters_passed = False
        if current_ratio_gt is not None and (
            ratios.get("current_ratio") is None or ratios["current_ratio"] <= current_ratio_gt
        ):
            filters_passed = False

        if filters_passed:
            results.append(
                {
                    "ticker": t,
                    "pe": ratios.get("pe"),
                    "roic": ratios.get("roic"),
                    "gross_margin": ratios.get("gross_margin"),
                    "debt_to_equity": ratios.get("debt_to_equity"),
                    "current_ratio": ratios.get("current_ratio"),
                    "health_score": ratios.get("health_score"),
                }
            )

    return JSONResponse(content=_clean({"results": results, "count": len(results)}))


# ── CLI entry ─────────────────────────────────────────────────────────────────


def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Start the FastAPI server (called from CLI)."""
    try:
        import uvicorn
    except ImportError:
        raise ImportError("API server requires uvicorn: pip install 'fin-ratios[api]'")
    uvicorn.run("fin_ratios.api:app", host=host, port=port, reload=reload)
