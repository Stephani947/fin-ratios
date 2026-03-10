"""
Peer group comparison and ranking.

Fetches financials for a set of peer tickers and ranks them by
the requested metrics relative to the subject company.

Usage:
    from fin_ratios.utils.peers import compare_peers

    result = compare_peers(
        'AAPL',
        metrics=['pe', 'roic', 'fcf_margin', 'gross_margin'],
        peers=['MSFT', 'GOOGL', 'META'],
    )
    print(result.table())
    print(result.rank('roic'))        # {'AAPL': 1, 'MSFT': 2, ...}
    print(result.percentile('pe'))    # {'AAPL': 0.75, ...}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional


# ── Static peer map (industry-level groupings) ────────────────────────────────
# Can be overridden by passing `peers=` explicitly.

_PEER_MAP: dict[str, list[str]] = {
    # Big Tech
    "AAPL": ["MSFT", "GOOGL", "META", "AMZN", "NVDA"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL", "SAP"],
    "GOOGL": ["META", "MSFT", "AAPL", "SNAP", "PINS"],
    "GOOG":  ["META", "MSFT", "AAPL", "SNAP", "PINS"],
    "META":  ["GOOGL", "SNAP", "PINS", "TWTR", "RDDT"],
    "AMZN":  ["MSFT", "GOOGL", "BABA", "JD",   "EBAY"],
    "NVDA":  ["AMD",  "INTC",  "QCOM", "AVGO", "TSM"],
    "AMD":   ["NVDA", "INTC",  "QCOM", "AVGO", "ARM"],
    # Financials
    "JPM":   ["BAC",  "WFC",   "GS",   "MS",   "C"],
    "BAC":   ["JPM",  "WFC",   "C",    "GS",   "USB"],
    "GS":    ["MS",   "JPM",   "BLK",  "SCHW", "AXP"],
    # Healthcare
    "JNJ":   ["PFE",  "ABBV",  "MRK",  "LLY",  "BMY"],
    "PFE":   ["JNJ",  "ABBV",  "MRK",  "AZN",  "GILD"],
    "LLY":   ["JNJ",  "PFE",   "ABBV", "NVO",  "MRK"],
    # Energy
    "XOM":   ["CVX",  "COP",   "BP",   "SHEL", "TTE"],
    "CVX":   ["XOM",  "COP",   "BP",   "SHEL", "PXD"],
    # Consumer
    "AMZN":  ["WMT",  "TGT",   "COST", "HD",   "LOW"],
    "WMT":   ["COST", "TGT",   "AMZN", "HD",   "KR"],
    # SaaS
    "CRM":   ["MSFT", "ORCL",  "NOW",  "WDAY", "SAP"],
    "NOW":   ["CRM",  "WDAY",  "MSFT", "ORCL", "ADBE"],
    "TSLA":  ["F",    "GM",    "TM",   "RIVN",  "NIO"],
}


# ── Higher-is-better flag per metric (for rank direction) ─────────────────────

_HIGHER_IS_BETTER: set[str] = {
    "roic", "roe", "roa", "roce",
    "gross_margin", "operating_margin", "net_margin", "ebitda_margin", "fcf_margin",
    "revenue_growth", "fcf_growth", "eps_growth",
    "current_ratio", "quick_ratio", "interest_coverage",
    "fcf_conversion", "ocf_to_sales",
    "free_cash_flow", "revenue", "net_income", "ebitda",
}
_LOWER_IS_BETTER: set[str] = {
    "pe", "pb", "ps", "ev_ebitda", "peg",
    "debt_to_equity", "net_debt_to_equity", "net_debt_to_ebitda",
    "debt_to_assets",
}


@dataclass
class PeerComparison:
    """
    Results of a peer comparison query.

    Attributes:
        ticker:  Subject ticker
        peers:   All tickers in comparison (subject + peers)
        metrics: Metrics computed
        data:    {ticker: {metric: value}}
        errors:  Fetch errors per ticker (if any)
    """

    ticker: str
    peers: list[str]
    metrics: list[str]
    data: dict[str, dict[str, Optional[float]]] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def rank(self, metric: str) -> dict[str, Optional[int]]:
        """
        Rank all tickers by metric (1 = best).
        Direction: higher-is-better for profitability/efficiency; lower for valuation.
        """
        reverse = metric not in _LOWER_IS_BETTER
        scores: list[tuple[str, float]] = [
            (t, v)
            for t in self.peers
            if (v := self.data.get(t, {}).get(metric)) is not None
        ]
        scores.sort(key=lambda x: x[1], reverse=reverse)
        return {t: i + 1 for i, (t, _) in enumerate(scores)}

    def percentile(self, metric: str) -> dict[str, Optional[float]]:
        """
        Percentile rank of each ticker for a metric (1.0 = best in group).
        """
        ranks = self.rank(metric)
        n = len(ranks)
        if n == 0:
            return {}
        return {t: 1.0 - (r - 1) / n for t, r in ranks.items()}

    def subject_rank(self, metric: str) -> Optional[int]:
        """Rank of the subject ticker for a metric."""
        return self.rank(metric).get(self.ticker)

    def table(self) -> str:
        """ASCII text table."""
        col_w = 12
        header = "Ticker".ljust(8) + "".join(m[:col_w].ljust(col_w) for m in self.metrics)
        sep = "-" * len(header)
        rows = [header, sep]

        # Subject first, then sorted peers
        tickers = [self.ticker] + [t for t in self.peers if t != self.ticker]
        for t in tickers:
            row = t.ljust(8)
            marker = " *" if t == self.ticker else ""
            for m in self.metrics:
                v = self.data.get(t, {}).get(m)
                if v is None:
                    cell = "N/A"
                elif abs(v) < 10:
                    cell = f"{v:.3f}"
                else:
                    cell = f"{v:.1f}"
                row += cell.ljust(col_w)
            rows.append(row + marker)
        rows.append(sep)
        rows.append(f"  * = {self.ticker} (subject)")
        return "\n".join(rows)

    def to_dict(self) -> dict:
        """JSON-serializable export."""
        return {
            "ticker": self.ticker,
            "peers": self.peers,
            "metrics": self.metrics,
            "data": self.data,
            "ranks": {m: self.rank(m) for m in self.metrics},
            "errors": self.errors,
        }

    def _repr_html_(self) -> str:
        """Jupyter rich display."""
        ranks_by_metric = {m: self.rank(m) for m in self.metrics}
        tickers = [self.ticker] + [t for t in self.peers if t != self.ticker]

        def _rank_color(rank: Optional[int], n: int) -> str:
            if rank is None:
                return "#94a3b8"
            pct = 1 - (rank - 1) / max(n, 1)
            if pct >= 0.75:
                return "#22c55e"
            if pct >= 0.40:
                return "#f59e0b"
            return "#ef4444"

        n = len(tickers)
        header_cells = "<th style='padding:6px 12px;text-align:left'>Ticker</th>"
        for m in self.metrics:
            header_cells += f"<th style='padding:6px 12px;text-align:right'>{m}</th>"

        rows_html = ""
        for t in tickers:
            is_subject = t == self.ticker
            bg = "#eff6ff" if is_subject else ""
            fw = "700" if is_subject else "400"
            cells = f"<td style='padding:6px 12px;font-weight:{fw};background:{bg}'>{t}</td>"
            for m in self.metrics:
                v = self.data.get(t, {}).get(m)
                cell = "—" if v is None else (f"{v*100:.1f}%" if abs(v) < 3 else f"{v:.2f}")
                rank = ranks_by_metric[m].get(t)
                color = _rank_color(rank, n)
                rank_str = f"<sup style='color:{color};margin-left:3px'>#{rank}</sup>" if rank else ""
                cells += f"<td style='padding:6px 12px;text-align:right;background:{bg}'>{cell}{rank_str}</td>"
            rows_html += f"<tr>{cells}</tr>"

        return f"""
        <div style='font-family:sans-serif;font-size:13px'>
          <p style='margin:0 0 6px;font-weight:700;color:#0f172a'>{self.ticker} — Peer Comparison</p>
          <table style='border-collapse:collapse;background:#f8fafc;border-radius:6px'>
            <thead><tr style='background:#e2e8f0'>{header_cells}</tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
          <p style='margin:6px 0 0;font-size:11px;color:#94a3b8'>
            Rank superscripts: <span style='color:#22c55e'>green</span>=top quartile
            <span style='color:#f59e0b;margin-left:6px'>amber</span>=middle
            <span style='color:#ef4444;margin-left:6px'>red</span>=bottom
          </p>
        </div>"""


# ── Main function ──────────────────────────────────────────────────────────────

def compare_peers(
    ticker: str,
    metrics: list[str],
    peers: Optional[list[str]] = None,
    top_n: int = 5,
    source: Literal["edgar", "yahoo"] = "edgar",
) -> PeerComparison:
    """
    Fetch and compare a ticker against its peer group.

    Args:
        ticker:   Subject ticker, e.g. 'AAPL'
        metrics:  Metrics to compare, e.g. ['pe', 'roic', 'fcf_margin']
        peers:    Explicit peer list. If None, uses built-in sector map.
        top_n:    Max number of peers to include (default 5)
        source:   Data source — 'edgar' or 'yahoo'

    Returns:
        PeerComparison with per-ticker values, ranks, and display helpers.

    Example:
        result = compare_peers('AAPL', ['pe', 'roic', 'gross_margin'])
        print(result.table())
    """
    from fin_ratios.utils.trends import _build_metric_finders, _METRIC_FINDERS, _Acc

    if not _METRIC_FINDERS:
        _build_metric_finders()

    unknown = [m for m in metrics if m not in _METRIC_FINDERS]
    if unknown:
        raise ValueError(f"Unknown metrics: {unknown}. Available: {sorted(_METRIC_FINDERS)}")

    # Resolve peer list
    if peers is None:
        peers = _PEER_MAP.get(ticker.upper(), [])[:top_n]
    else:
        peers = list(peers[:top_n])

    all_tickers = [ticker] + [p for p in peers if p != ticker]

    data: dict[str, dict[str, Optional[float]]] = {}
    errors: dict[str, str] = {}

    for t in all_tickers:
        try:
            filing = _fetch_one(t, source)
            acc = _Acc(filing)
            data[t] = {}
            for m in metrics:
                finder = _METRIC_FINDERS[m]
                try:
                    val = finder(acc)
                    data[t][m] = float(val) if val is not None else None
                except Exception:
                    data[t][m] = None
        except Exception as exc:
            errors[t] = str(exc)
            data[t] = {m: None for m in metrics}

    return PeerComparison(
        ticker=ticker,
        peers=all_tickers,
        metrics=metrics,
        data=data,
        errors=errors,
    )


def _fetch_one(ticker: str, source: str) -> Any:
    """Fetch the most recent annual filing for a ticker."""
    if source == "edgar":
        from fin_ratios.fetchers.edgar import fetch_edgar
        filings = fetch_edgar(ticker, num_years=1)
        if not filings:
            raise RuntimeError(f"No EDGAR filings found for {ticker}")
        return filings[0]
    else:
        from fin_ratios.fetchers.yahoo import fetch_yahoo
        return fetch_yahoo(ticker)
