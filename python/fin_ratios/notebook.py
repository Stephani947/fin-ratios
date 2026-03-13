"""
Jupyter notebook rich display helpers.

Wraps plain dict results (from compute_all, health_score, etc.) in
HTML-renderable objects for a polished notebook experience.

Usage:
    from fin_ratios.notebook import display_ratios, RatioCard

    data = fetch_yahoo('AAPL')
    ratios = compute_all(data)
    display_ratios('AAPL', ratios)        # renders HTML table in Jupyter

    card = RatioCard('AAPL', ratios)
    card                                  # auto-renders in Jupyter cell
"""

from __future__ import annotations

from typing import Any, Optional


# ── Color palette ─────────────────────────────────────────────────────────────

_GREEN = "#22c55e"
_AMBER = "#f59e0b"
_RED = "#ef4444"
_BLUE = "#3b82f6"
_SLATE = "#64748b"
_LIGHT = "#f8fafc"
_BORDER = "#e2e8f0"

# Sections to render and their display order
_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Valuation",
        ["pe", "pb", "ps", "peg", "ev_ebitda", "ev_ebit", "p_fcf", "tobin_q", "graham_number"],
    ),
    (
        "Profitability",
        [
            "gross_margin",
            "operating_margin",
            "net_margin",
            "ebitda_margin",
            "roe",
            "roa",
            "roic",
            "roce",
        ],
    ),
    (
        "Cash Flow",
        ["fcf_margin", "fcf_conversion", "ocf_to_sales", "fcf_yield", "capex_to_revenue"],
    ),
    ("Liquidity", ["current_ratio", "quick_ratio", "dso", "dio", "dpo", "cash_conversion_cycle"]),
    (
        "Solvency",
        [
            "debt_to_equity",
            "net_debt_to_equity",
            "net_debt_to_ebitda",
            "interest_coverage",
            "debt_to_assets",
        ],
    ),
    ("Efficiency", ["asset_turnover", "receivables_turnover", "inventory_turnover"]),
    ("Composite", ["altman_z", "piotroski", "health_score"]),
]

# fmt: thresholds for color-coding (good_min, bad_max)
_THRESHOLDS: dict[str, tuple[Optional[float], Optional[float]]] = {
    "pe": (None, 30),  # lower = better (cheap); red > 30
    "pb": (None, 5),
    "ps": (None, 8),
    "peg": (None, 1.5),
    "ev_ebitda": (None, 20),
    "gross_margin": (0.40, 0.20),  # green >= 40%, red < 20%
    "operating_margin": (0.20, 0.05),
    "net_margin": (0.15, 0.02),
    "ebitda_margin": (0.25, 0.08),
    "roe": (0.15, 0.05),
    "roa": (0.10, 0.02),
    "roic": (0.15, 0.05),
    "roce": (0.15, 0.05),
    "fcf_margin": (0.15, 0.03),
    "fcf_conversion": (0.90, 0.50),
    "current_ratio": (2.00, 1.00),
    "quick_ratio": (1.50, 0.80),
    "interest_coverage": (5.0, 1.50),
    "debt_to_equity": (None, 1.00),  # lower = better
    "net_debt_to_ebitda": (None, 3.00),
}


def _color(key: str, value: Any) -> str:
    """Return a color based on whether the value is in a good/bad range."""
    if not isinstance(value, (int, float)):
        return _SLATE
    thresh = _THRESHOLDS.get(key)
    if thresh is None:
        return _SLATE
    good, bad = thresh

    # Metrics where lower is better (no good_min threshold)
    if good is None and bad is not None:
        if value <= bad * 0.6:
            return _GREEN
        if value <= bad:
            return _AMBER
        return _RED

    # Metrics where higher is better
    if good is not None and bad is not None:
        if value >= good:
            return _GREEN
        if value >= bad:
            return _AMBER
        return _RED

    return _SLATE


def _fmt(key: str, value: Any) -> str:
    """Format a ratio value for display."""
    if value is None:
        return "—"
    if isinstance(value, dict):
        # Nested (Altman, Piotroski, etc.) — show key metric
        if "z_score" in value:
            return f"{value['z_score']:.2f} ({value.get('zone', '')})"
        if "score" in value:
            return f"{value['score']}/9"
        if "score" in value:
            return f"{value['score']:.0f}/100"
        return "—"
    if isinstance(value, float):
        if abs(value) < 10:
            return f"{value * 100:.1f}%"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _nested_value(value: Any) -> Any:
    """Extract the primary numeric value from a nested dict result."""
    if isinstance(value, dict):
        for k in ("z_score", "score", "bankruptcy_probability"):
            if k in value:
                return value[k]
    return value


class RatioCard:
    """
    A Jupyter-renderable card showing all computed ratios for a ticker.

    Renders as a styled HTML table in Jupyter; falls back to text in terminal.

    Example:
        data = fetch_yahoo('AAPL')
        ratios = compute_all(data)
        card = RatioCard('AAPL', ratios)
        display(card)   # or just: card
    """

    def __init__(self, ticker: str, ratios: dict[str, Any], subtitle: str = ""):
        self.ticker = ticker
        self.ratios = ratios
        self.subtitle = subtitle

    def __repr__(self) -> str:
        lines = [f"{self.ticker} Financial Ratios"]
        lines.append("=" * 40)
        for section, keys in _SECTIONS:
            section_lines = []
            for k in keys:
                v = self.ratios.get(k)
                if v is not None:
                    section_lines.append(f"  {k:<22} {_fmt(k, v)}")
            if section_lines:
                lines.append(f"\n{section}")
                lines.extend(section_lines)
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        sections_html = ""
        for section, keys in _SECTIONS:
            rows = ""
            for k in keys:
                v = self.ratios.get(k)
                if v is None:
                    continue
                num_v = _nested_value(v)
                color = _color(k, num_v)
                val_str = _fmt(k, v)
                rows += f"""
                <tr>
                  <td style='padding:4px 12px;color:{_SLATE};font-size:12px'>{k}</td>
                  <td style='padding:4px 12px;text-align:right;font-weight:600;color:{color}'>{val_str}</td>
                </tr>"""
            if rows:
                sections_html += f"""
                <tr style='background:{_BORDER}'>
                  <td colspan='2' style='padding:4px 12px;font-size:11px;font-weight:700;
                                          color:#475569;letter-spacing:0.05em;
                                          text-transform:uppercase'>{section}</td>
                </tr>{rows}"""

        health = self.ratios.get("health_score")
        health_html = ""
        if isinstance(health, dict):
            s = health.get("score", 0)
            grade = health.get("grade", "")
            bar_color = _GREEN if s >= 70 else (_AMBER if s >= 40 else _RED)
            health_html = f"""
            <div style='margin-top:10px;padding:10px 12px;background:{_LIGHT};border-radius:6px;
                         border-left:4px solid {bar_color}'>
              <span style='font-weight:700;font-size:14px;color:{bar_color}'>{s}/100</span>
              <span style='margin-left:8px;color:{_SLATE}'>{grade}</span>
              <div style='margin-top:6px;background:{_BORDER};border-radius:4px;height:8px'>
                <div style='background:{bar_color};width:{s}%;height:8px;border-radius:4px'></div>
              </div>
            </div>"""

        subtitle_html = ""
        if self.subtitle:
            subtitle_html = (
                f"<p style='margin:0 0 8px;color:{_SLATE};font-size:12px'>{self.subtitle}</p>"
            )

        return f"""
        <div style='font-family:sans-serif;font-size:13px;max-width:480px'>
          <p style='margin:0 0 2px;font-weight:700;font-size:16px;color:#0f172a'>{self.ticker}</p>
          {subtitle_html}
          <table style='border-collapse:collapse;width:100%;background:{_LIGHT};border-radius:6px;overflow:hidden'>
            {sections_html}
          </table>
          {health_html}
        </div>"""


class ComparatorCard:
    """
    Side-by-side Jupyter display for multiple tickers.

    Example:
        from fin_ratios.notebook import ComparatorCard
        cards = {t: compute_all(fetch_yahoo(t)) for t in ['AAPL', 'MSFT', 'GOOGL']}
        ComparatorCard(cards, metrics=['pe', 'roic', 'gross_margin'])
    """

    def __init__(
        self,
        ticker_ratios: dict[str, dict[str, Any]],
        metrics: Optional[list[str]] = None,
    ):
        self.ticker_ratios = ticker_ratios
        self.metrics = metrics or [
            "pe",
            "pb",
            "ps",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "roe",
            "roic",
            "fcf_margin",
            "current_ratio",
            "debt_to_equity",
            "interest_coverage",
        ]

    def __repr__(self) -> str:
        tickers = list(self.ticker_ratios)
        col = 14
        header = "Metric".ljust(22) + "".join(t.ljust(col) for t in tickers)
        lines = [header, "-" * len(header)]
        for m in self.metrics:
            row = m.ljust(22)
            for t in tickers:
                v = self.ticker_ratios[t].get(m)
                row += _fmt(m, v).ljust(col)
            lines.append(row)
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        tickers = list(self.ticker_ratios)
        header_cells = "<th style='padding:6px 12px;text-align:left'>Metric</th>"
        for t in tickers:
            header_cells += f"<th style='padding:6px 12px;text-align:right'>{t}</th>"

        rows_html = ""
        for m in self.metrics:
            cells = f"<td style='padding:5px 12px;color:{_SLATE}'>{m}</td>"
            for t in tickers:
                v = self.ticker_ratios[t].get(m)
                num_v = _nested_value(v)
                color = _color(m, num_v)
                val_str = _fmt(m, v)
                cells += f"<td style='padding:5px 12px;text-align:right;font-weight:600;color:{color}'>{val_str}</td>"
            rows_html += f"<tr>{cells}</tr>"

        return f"""
        <div style='font-family:sans-serif;font-size:13px'>
          <table style='border-collapse:collapse;background:{_LIGHT};border-radius:6px'>
            <thead><tr style='background:{_BORDER}'>{header_cells}</tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>"""


# ── Convenience function ───────────────────────────────────────────────────────


def display_ratios(
    ticker: str,
    ratios: dict[str, Any],
    subtitle: str = "",
) -> RatioCard:
    """
    Create a display-ready RatioCard.

    In a Jupyter notebook, simply returning this object will render the HTML.
    Outside of Jupyter, calling repr() gives a text table.

    Example:
        ratios = compute_all(fetch_yahoo('AAPL'))
        display_ratios('AAPL', ratios)
    """
    return RatioCard(ticker=ticker, ratios=ratios, subtitle=subtitle)
