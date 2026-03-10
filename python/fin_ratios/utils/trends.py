"""
Historical ratio trend analysis.

Fetches multi-year financials and computes how ratios trend over time.

Usage:
    from fin_ratios.utils.trends import ratio_history

    history = ratio_history('AAPL', metrics=['roic', 'fcf_margin', 'gross_margin'], years=5)
    print(history.table())
    # Year    roic    fcf_margin  gross_margin
    # 2020    0.282   0.212       0.398
    # 2021    0.449   0.263       0.418
    # 2022    0.562   0.250       0.433
    # 2023    0.564   0.268       0.441
    # 2024    0.583   0.271       0.453

    print(history.trend('roic'))   # 'improving'
    print(history.cagr('roic'))    # 0.198 (19.8% CAGR)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from fin_ratios._utils import safe_divide


TrendDirection = Literal["improving", "stable", "deteriorating", "volatile"]


@dataclass
class RatioHistory:
    ticker: str
    years: list[str]                          # e.g. ['2020','2021','2022','2023','2024']
    data: dict[str, dict[str, Optional[float]]]  # metric → {year → value}

    def trend(
        self,
        metric: str,
        min_periods: int = 3,
    ) -> TrendDirection:
        """
        Classify trend direction for a metric.

        Uses linear regression slope relative to mean value:
        - |slope/mean| > 5% per year → improving/deteriorating
        - otherwise → stable
        - R² < 0.4 → volatile
        """
        values = [self.data.get(metric, {}).get(yr) for yr in self.years]
        valid = [(i, v) for i, v in enumerate(values) if v is not None]
        if len(valid) < min_periods:
            return "stable"

        xs = [x for x, _ in valid]
        ys = [y for _, y in valid]
        n = len(xs)
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n

        ss_xx = sum((x - x_mean) ** 2 for x in xs)
        ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        if ss_xx == 0:
            return "stable"

        slope = ss_xy / ss_xx
        ss_yy = sum((y - y_mean) ** 2 for y in ys)
        if ss_yy == 0:
            return "stable"

        r_sq = (ss_xy ** 2) / (ss_xx * ss_yy)
        if r_sq < 0.35:
            return "volatile"

        rel_slope = slope / abs(y_mean) if y_mean else 0
        if rel_slope > 0.03:
            return "improving"
        if rel_slope < -0.03:
            return "deteriorating"
        return "stable"

    def cagr(self, metric: str) -> Optional[float]:
        """Compound annual growth rate for a metric over available years."""
        values = [self.data.get(metric, {}).get(yr) for yr in self.years]
        valid = [v for v in values if v is not None]
        if len(valid) < 2 or valid[0] == 0 or valid[0] is None:
            return None
        n = len(valid) - 1
        if valid[0] <= 0 or valid[-1] <= 0:
            return safe_divide(valid[-1] - valid[0], abs(valid[0]))
        return (valid[-1] / valid[0]) ** (1 / n) - 1

    def latest(self, metric: str) -> Optional[float]:
        """Most recent value for a metric."""
        for yr in reversed(self.years):
            v = self.data.get(metric, {}).get(yr)
            if v is not None:
                return v
        return None

    def table(self, fmt: str = "text") -> str:
        """
        Render a text or markdown table of all metrics across years.

        Args:
            fmt: 'text' or 'markdown'

        Returns:
            Formatted string table.
        """
        metrics = list(self.data.keys())
        col_w = 12

        header = "Year".ljust(6) + "".join(m[:col_w].ljust(col_w) for m in metrics)
        sep = "-" * len(header)
        rows = [header, sep]

        for yr in self.years:
            row = yr.ljust(6)
            for m in metrics:
                v = self.data[m].get(yr)
                if v is None:
                    cell = "N/A"
                elif abs(v) < 10:
                    cell = f"{v:.3f}"
                else:
                    cell = f"{v:.1f}"
                row += cell.ljust(col_w)
            rows.append(row)

        return "\n".join(rows)

    def to_dict(self) -> dict:
        """Export as plain nested dict (JSON-serializable)."""
        return {
            "ticker": self.ticker,
            "years": self.years,
            "data": self.data,
            "trends": {m: self.trend(m) for m in self.data},
            "cagrs": {m: self.cagr(m) for m in self.data},
        }

    def _repr_html_(self) -> str:
        """Jupyter notebook rich display."""
        trend_icons = {
            "improving": "↑", "deteriorating": "↓", "stable": "→", "volatile": "~"
        }
        trend_colors = {
            "improving": "#22c55e", "deteriorating": "#ef4444",
            "stable": "#94a3b8", "volatile": "#f59e0b"
        }
        metrics = list(self.data.keys())

        rows_html = ""
        for yr in self.years:
            cells = f"<td style='padding:6px 12px;font-weight:600'>{yr}</td>"
            for m in metrics:
                v = self.data[m].get(yr)
                cell = "—" if v is None else (f"{v*100:.1f}%" if abs(v) < 3 else f"{v:.2f}")
                cells += f"<td style='padding:6px 12px;text-align:right'>{cell}</td>"
            rows_html += f"<tr>{cells}</tr>"

        header_cells = "<th style='padding:6px 12px;text-align:left'>Year</th>"
        for m in metrics:
            t = self.trend(m)
            icon = trend_icons.get(t, "")
            color = trend_colors.get(t, "#94a3b8")
            header_cells += f"<th style='padding:6px 12px;text-align:right'>{m} <span style='color:{color}'>{icon}</span></th>"

        return f"""
        <div style='font-family:sans-serif;font-size:13px'>
          <p style='margin:0 0 6px;font-weight:700;color:#0f172a'>{self.ticker} — Ratio History</p>
          <table style='border-collapse:collapse;background:#f8fafc;border-radius:6px'>
            <thead><tr style='background:#e2e8f0'>{header_cells}</tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>"""


# ── Main function ─────────────────────────────────────────────────────────────

# Map of metric name → callable that takes a data accessor
_METRIC_FINDERS: dict[str, Any] = {}


def _build_metric_finders() -> None:
    """Lazily register metric finders to avoid circular imports at module load."""
    import fin_ratios as _fr
    global _METRIC_FINDERS
    _METRIC_FINDERS = {
        "pe":             lambda d: _fr.pe(market_cap=d.market_cap, net_income=d.net_income),
        "pb":             lambda d: _fr.pb(market_cap=d.market_cap, total_equity=d.total_equity),
        "ps":             lambda d: _fr.ps(market_cap=d.market_cap, revenue=d.revenue),
        "ev_ebitda":      lambda d: _fr.ev_ebitda(ev=d.enterprise_value or d.market_cap + d.total_debt - d.cash, ebitda=d.ebitda) if d.ebitda else None,
        "gross_margin":   lambda d: _fr.gross_margin(gross_profit=d.gross_profit, revenue=d.revenue),
        "operating_margin": lambda d: _fr.operating_margin(ebit=d.ebit, revenue=d.revenue),
        "net_margin":     lambda d: _fr.net_profit_margin(net_income=d.net_income, revenue=d.revenue),
        "ebitda_margin":  lambda d: _fr.ebitda_margin(ebitda=d.ebitda, revenue=d.revenue) if d.ebitda else None,
        "roe":            lambda d: _fr.roe(net_income=d.net_income, avg_total_equity=d.total_equity),
        "roa":            lambda d: _fr.roa(net_income=d.net_income, avg_total_assets=d.total_assets),
        "roic":           lambda d: _fr.roic(
                              nopat_value=_fr.nopat(ebit=d.ebit, tax_rate=0.21),
                              invested_capital=_fr.invested_capital(total_equity=d.total_equity, total_debt=d.total_debt, cash=d.cash)
                          ),
        "debt_to_equity": lambda d: _fr.debt_to_equity(total_debt=d.total_debt, total_equity=d.total_equity),
        "current_ratio":  lambda d: _fr.current_ratio(current_assets=d.current_assets, current_liabilities=d.current_liabilities),
        "interest_coverage": lambda d: _fr.interest_coverage_ratio(ebit=d.ebit, interest_expense=d.interest_expense),
        "fcf_margin":     lambda d: _fr.fcf_margin(
                              fcf=_fr.free_cash_flow(operating_cash_flow=d.operating_cash_flow, capex=d.capex),
                              revenue=d.revenue
                          ),
        "revenue":        lambda d: d.revenue,
        "net_income":     lambda d: d.net_income,
        "ebitda":         lambda d: d.ebitda,
    }


class _Acc:
    def __init__(self, obj: Any):
        self._o = obj
    def __getattr__(self, k: str) -> float:
        o = object.__getattribute__(self, '_o')
        if isinstance(o, dict):
            return o.get(k, 0.0) or 0.0
        return getattr(o, k, 0.0) or 0.0


def ratio_history(
    ticker: str,
    metrics: list[str],
    years: int = 5,
    source: Literal["edgar", "yahoo"] = "edgar",
) -> RatioHistory:
    """
    Fetch multi-year financials and compute ratio trends for a ticker.

    Args:
        ticker:  Stock ticker, e.g. 'AAPL'
        metrics: List of ratio names, e.g. ['roic', 'fcf_margin', 'gross_margin']
        years:   Number of annual periods (default: 5)
        source:  Data source — 'edgar' (recommended) or 'yahoo'

    Returns:
        RatioHistory object with per-year values and trend analysis.

    Example:
        h = ratio_history('MSFT', ['roic', 'net_margin', 'debt_to_equity'], years=5)
        print(h.trend('roic'))        # 'improving'
        print(h.cagr('net_margin'))   # 0.08
        print(h.table())
    """
    if not _METRIC_FINDERS:
        _build_metric_finders()

    unknown = [m for m in metrics if m not in _METRIC_FINDERS]
    if unknown:
        raise ValueError(f"Unknown metrics: {unknown}. Available: {sorted(_METRIC_FINDERS)}")

    filings: list[Any] = []
    year_labels: list[str] = []

    if source == "edgar":
        try:
            from fin_ratios.fetchers.edgar import fetch_edgar
            filings = fetch_edgar(ticker, num_years=years)
            year_labels = [f.fiscal_year for f in filings]
        except Exception as e:
            raise RuntimeError(f"EDGAR fetch failed for {ticker}: {e}")
    else:
        try:
            from fin_ratios.fetchers.yahoo import fetch_yahoo_history
            filings = fetch_yahoo_history(ticker, years=years)
            year_labels = [str(f.get("year", i)) for i, f in enumerate(filings)]
        except Exception as e:
            raise RuntimeError(f"Yahoo history fetch failed for {ticker}: {e}")

    data: dict[str, dict[str, Optional[float]]] = {m: {} for m in metrics}

    for i, (yr, filing) in enumerate(zip(year_labels, filings)):
        acc = _Acc(filing)
        for m in metrics:
            finder = _METRIC_FINDERS[m]
            try:
                val = finder(acc)
                data[m][yr] = float(val) if val is not None else None
            except Exception:
                data[m][yr] = None

    return RatioHistory(ticker=ticker, years=year_labels, data=data)
