# MCP Server (Claude / AI Agents)

fin-ratios ships an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes all scoring models as tools for AI agents, including Claude Desktop.

## Installation

```bash
pip install "financial-ratios[mcp,fetchers]"
```

## Start the Server

```bash
fin-ratios serve
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fin-ratios": {
      "command": "fin-ratios",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Desktop. You can now ask:

> "What is Apple's investment score based on the last 7 years of EDGAR data?"

> "Compare the moat scores of AAPL, MSFT, and GOOGL."

> "What is the fair value range for Microsoft at a 9% WACC?"

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `investment_score` | Full investment score from ticker + source |
| `quality_score` | Quality Factor Score |
| `moat_score` | Economic Moat Score |
| `valuation_score` | Valuation Attractiveness Score |
| `compute_ratios` | Compute individual ratios from data |
| `fetch_annual_data` | Fetch annual financials from any supported source |

## Programmatic Usage

```python
from fin_ratios.mcp_server import create_mcp_server

server = create_mcp_server()
# Use with any MCP-compatible client
```
