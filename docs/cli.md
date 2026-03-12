# CLI Reference

The `fin-ratios` CLI provides instant terminal analysis for any US stock ticker.

## Commands

### Ratio Analysis

```bash
fin-ratios AAPL                       # ratio dashboard
fin-ratios AAPL --full                # include all composite scores
fin-ratios AAPL --json                # raw JSON output
fin-ratios AAPL MSFT GOOGL --compare  # side-by-side comparison
```

### Scoring Dashboard

```bash
fin-ratios score AAPL                 # full scoring models
fin-ratios score AAPL --source edgar  # use EDGAR (default, free)
fin-ratios score AAPL --years 10      # 10 years of data
fin-ratios score AAPL --json          # JSON output
```

**Output:**
```
  APPLE INC (AAPL)  —  Investment Scorecard
  ──────────────────────────────────────────────────

  INVESTMENT SCORE
  Score                      74/100  [B+]
  Conviction                       BUY

  COMPONENT SCORES
  Economic Moat               78/100  [WIDE]        ●
  Capital Allocation          71/100  [GOOD]        ●
  Earnings Quality            82/100  [HIGH]        ●
  Management Quality          68/100  [GOOD]        ●
  Valuation Attractiveness    45/100  [FAIR]        ●
  Dividend Safety             86/100  [SAFE]        ●
  Quality Factor              76/100  [A]           ●
```

### Server Commands

```bash
fin-ratios api --port 8000            # start FastAPI REST server
fin-ratios api --host 0.0.0.0         # bind to all interfaces
fin-ratios serve                      # start MCP server for AI agents
```

## Installation

```bash
pip install "financial-ratios[fetchers]"
```

## Output Indicators

| Symbol | Meaning |
|--------|---------|
| ● (green) | Score ≥ 70 (strong) |
| ● (yellow) | Score 45–69 (moderate) |
| ● (red) | Score < 45 (weak) |
