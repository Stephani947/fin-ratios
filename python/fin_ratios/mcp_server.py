"""
MCP (Model Context Protocol) server for fin-ratios.

Exposes financial analysis tools that AI agents (Claude, etc.) can call
directly as structured tool calls via the MCP protocol.

Usage:
    # Start the server (stdio transport for Claude Desktop)
    fin-ratios serve

    # Or with SSE transport (for web-based agents)
    fin-ratios serve --transport sse --port 3333

    # Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):
    {
      "mcpServers": {
        "fin-ratios": {
          "command": "fin-ratios",
          "args": ["serve"]
        }
      }
    }

Tools exposed:
    analyze_ticker      — Full ratio analysis for a ticker
    health_score        — Composite financial health score
    ratio_history       — Multi-year trend analysis
    compare_peers       — Peer group comparison
    screen_stocks       — Filter universe by ratio thresholds
    compute_ratio       — Compute a single named ratio from raw inputs
"""

from __future__ import annotations

import json
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.types as types
except ImportError:
    raise ImportError("MCP server requires the mcp package: pip install 'fin-ratios[mcp]'")


_server = Server("fin-ratios")


# ── Tool definitions ──────────────────────────────────────────────────────────


@_server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="analyze_ticker",
            description=(
                "Compute all 40+ financial ratios for a stock ticker. "
                "Returns valuation, profitability, cash flow, liquidity, solvency, "
                "efficiency, composite scores, and a health score."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g. 'AAPL', 'MSFT')",
                    },
                    "source": {
                        "type": "string",
                        "enum": ["yahoo", "edgar"],
                        "default": "yahoo",
                        "description": "Data source for financials",
                    },
                },
                "required": ["ticker"],
            },
        ),
        types.Tool(
            name="health_score",
            description=(
                "Compute a composite financial health score (0-100) for a ticker. "
                "Combines Piotroski F-Score, Altman Z-Score, ROIC, profitability, "
                "FCF quality, and debt metrics into a single grade."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "source": {"type": "string", "enum": ["yahoo", "edgar"], "default": "yahoo"},
                },
                "required": ["ticker"],
            },
        ),
        types.Tool(
            name="ratio_history",
            description=(
                "Fetch multi-year ratio history and trend analysis for a ticker. "
                "Returns per-year values, trend direction (improving/stable/deteriorating), "
                "and CAGR for each metric."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Metrics to compute. Available: pe, pb, ps, ev_ebitda, "
                            "gross_margin, operating_margin, net_margin, ebitda_margin, "
                            "roe, roa, roic, debt_to_equity, current_ratio, "
                            "interest_coverage, fcf_margin, revenue, net_income, ebitda"
                        ),
                    },
                    "years": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Number of annual periods to fetch",
                    },
                    "source": {"type": "string", "enum": ["edgar", "yahoo"], "default": "edgar"},
                },
                "required": ["ticker", "metrics"],
            },
        ),
        types.Tool(
            name="compare_peers",
            description=(
                "Compare a ticker against its peer group on selected financial metrics. "
                "Returns per-ticker values with rank within the peer group."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Metrics to compare (e.g. ['pe', 'roic', 'gross_margin'])",
                    },
                    "peers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Explicit peer ticker list. If omitted, uses built-in sector map.",
                    },
                    "top_n": {
                        "type": "integer",
                        "default": 5,
                        "description": "Max number of peers to include",
                    },
                    "source": {"type": "string", "enum": ["edgar", "yahoo"], "default": "edgar"},
                },
                "required": ["ticker", "metrics"],
            },
        ),
        types.Tool(
            name="screen_stocks",
            description=(
                "Screen a list of tickers using ratio filters. "
                "Returns tickers that pass all filters with their ratio values."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tickers to screen",
                    },
                    "filters": {
                        "type": "object",
                        "description": (
                            "Dict of filter conditions. Keys are 'metric__op' where op is "
                            "'lt', 'gt', 'lte', 'gte'. E.g. {'pe__lt': 20, 'roic__gt': 0.15}"
                        ),
                    },
                    "source": {"type": "string", "enum": ["yahoo", "edgar"], "default": "yahoo"},
                },
                "required": ["tickers"],
            },
        ),
        types.Tool(
            name="compute_ratio",
            description=(
                "Compute a single named financial ratio from raw input values. "
                "Useful when you already have the financial data and just need the formula applied."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ratio": {
                        "type": "string",
                        "description": (
                            "Ratio name. Examples: 'gross_margin', 'roic', 'pe', "
                            "'current_ratio', 'debt_to_equity', 'fcf_margin'"
                        ),
                    },
                    "inputs": {
                        "type": "object",
                        "description": (
                            "Raw financial values needed for the ratio. "
                            "E.g. for gross_margin: {'gross_profit': 170e9, 'revenue': 400e9}"
                        ),
                    },
                },
                "required": ["ratio", "inputs"],
            },
        ),
    ]


# ── Tool handlers ─────────────────────────────────────────────────────────────


@_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    try:
        if name == "analyze_ticker":
            result = await _handle_analyze_ticker(arguments)
        elif name == "health_score":
            result = await _handle_health_score(arguments)
        elif name == "ratio_history":
            result = await _handle_ratio_history(arguments)
        elif name == "compare_peers":
            result = await _handle_compare_peers(arguments)
        elif name == "screen_stocks":
            result = await _handle_screen_stocks(arguments)
        elif name == "compute_ratio":
            result = await _handle_compute_ratio(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        result = {"error": str(e), "tool": name}

    return [types.TextContent(type="text", text=json.dumps(result, default=str, indent=2))]


async def _handle_analyze_ticker(args: dict) -> dict:
    ticker = args["ticker"].upper()
    source = args.get("source", "yahoo")
    data = _fetch(ticker, source)
    from fin_ratios.utils.compute_all import compute_all

    ratios = compute_all(data)
    return {"ticker": ticker, "ratios": _clean(ratios)}


async def _handle_health_score(args: dict) -> dict:
    ticker = args["ticker"].upper()
    source = args.get("source", "yahoo")
    data = _fetch(ticker, source)
    from fin_ratios.utils.compute_all import compute_all

    ratios = compute_all(data)
    return {"ticker": ticker, "health_score": _clean(ratios.get("health_score"))}


async def _handle_ratio_history(args: dict) -> dict:
    from fin_ratios.utils.trends import ratio_history

    ticker = args["ticker"].upper()
    metrics = args["metrics"]
    years = int(args.get("years", 5))
    source = args.get("source", "edgar")
    history = ratio_history(ticker, metrics=metrics, years=years, source=source)  # type: ignore[arg-type]
    return _clean(history.to_dict())


async def _handle_compare_peers(args: dict) -> dict:
    from fin_ratios.utils.peers import compare_peers

    ticker = args["ticker"].upper()
    metrics = args["metrics"]
    peers = args.get("peers")
    top_n = int(args.get("top_n", 5))
    source = args.get("source", "edgar")
    result = compare_peers(ticker, metrics, peers=peers, top_n=top_n, source=source)  # type: ignore[arg-type]
    return _clean(result.to_dict())


async def _handle_screen_stocks(args: dict) -> dict:
    from fin_ratios.utils.compute_all import compute_all

    tickers = [t.upper() for t in args.get("tickers", [])]
    filters: dict = args.get("filters", {})
    source = args.get("source", "yahoo")

    passed = []
    for t in tickers:
        try:
            data = _fetch(t, source)
            ratios = compute_all(data)
        except Exception:
            continue

        ok = True
        for key, threshold in filters.items():
            parts = key.rsplit("__", 1)
            metric = parts[0]
            op = parts[1] if len(parts) == 2 else "gt"
            val = ratios.get(metric)
            if val is None:
                ok = False
                break
            if isinstance(val, dict):
                continue
            try:
                fval = float(val)
                thr = float(threshold)
                if op == "lt" and not (fval < thr):
                    ok = False
                elif op == "lte" and not (fval <= thr):
                    ok = False
                elif op == "gt" and not (fval > thr):
                    ok = False
                elif op == "gte" and not (fval >= thr):
                    ok = False
            except (TypeError, ValueError):
                ok = False
            if not ok:
                break

        if ok:
            passed.append(
                {
                    "ticker": t,
                    **{
                        k: _clean(ratios.get(k))
                        for k in [
                            "pe",
                            "pb",
                            "roic",
                            "gross_margin",
                            "net_margin",
                            "debt_to_equity",
                            "current_ratio",
                            "health_score",
                        ]
                    },
                }
            )

    return {"results": passed, "count": len(passed)}


async def _handle_compute_ratio(args: dict) -> dict:
    import fin_ratios as _fr

    ratio_name = args["ratio"]
    inputs = args.get("inputs", {})

    # Map common ratio names to functions
    _dispatch: dict[str, Any] = {
        "gross_margin": lambda: _fr.gross_margin(**_pick(inputs, ["gross_profit", "revenue"])),
        "operating_margin": lambda: _fr.operating_margin(**_pick(inputs, ["ebit", "revenue"])),
        "net_margin": lambda: _fr.net_profit_margin(**_pick(inputs, ["net_income", "revenue"])),
        "roe": lambda: _fr.roe(
            net_income=inputs.get("net_income", 0),
            avg_total_equity=inputs.get("total_equity", inputs.get("avg_total_equity", 0)),
        ),
        "roa": lambda: _fr.roa(
            net_income=inputs.get("net_income", 0),
            avg_total_assets=inputs.get("total_assets", inputs.get("avg_total_assets", 0)),
        ),
        "current_ratio": lambda: _fr.current_ratio(
            **_pick(inputs, ["current_assets", "current_liabilities"])
        ),
        "debt_to_equity": lambda: _fr.debt_to_equity(
            **_pick(inputs, ["total_debt", "total_equity"])
        ),
        "pe": lambda: _fr.pe(**_pick(inputs, ["market_cap", "net_income"])),
        "pb": lambda: _fr.pb(**_pick(inputs, ["market_cap", "total_equity"])),
        "ps": lambda: _fr.ps(**_pick(inputs, ["market_cap", "revenue"])),
        "fcf_margin": lambda: _fr.fcf_margin(**_pick(inputs, ["free_cash_flow", "revenue"])),
        "interest_coverage": lambda: _fr.interest_coverage_ratio(
            **_pick(inputs, ["ebit", "interest_expense"])
        ),
    }

    fn = _dispatch.get(ratio_name)
    if fn is None:
        return {
            "error": f"Ratio '{ratio_name}' not supported in direct compute. Use analyze_ticker instead."
        }

    try:
        value = fn()
        return {"ratio": ratio_name, "value": _clean(value), "inputs": inputs}
    except Exception as e:
        return {"error": str(e), "ratio": ratio_name}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _fetch(ticker: str, source: str) -> Any:
    if source == "edgar":
        from fin_ratios.fetchers.edgar import fetch_edgar

        filings = fetch_edgar(ticker, num_years=1)
        if not filings:
            raise RuntimeError(f"No EDGAR data for {ticker}")
        return filings[0]
    else:
        from fin_ratios.fetchers.yahoo import fetch_yahoo

        return fetch_yahoo(ticker)


def _clean(val: Any) -> Any:
    import math

    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(val, 6)
    if isinstance(val, dict):
        return {k: _clean(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_clean(v) for v in val]
    return val


def _pick(d: dict, keys: list[str]) -> dict:
    return {k: float(d[k]) for k in keys if k in d}


# ── Entry point ────────────────────────────────────────────────────────────────


def run_server() -> None:
    """Start the MCP server (called from CLI `fin-ratios serve`)."""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def _main() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await _server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="fin-ratios",
                    server_version="0.2.0",
                    capabilities=_server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(_main())
