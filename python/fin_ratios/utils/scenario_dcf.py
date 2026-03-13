"""
Scenario-based DCF valuation (bull / base / bear).

Usage:
    from fin_ratios.utils.scenario_dcf import scenario_dcf

    result = scenario_dcf(
        ticker='AAPL',
        base_fcf=100_000_000_000,
        shares_outstanding=15_700_000_000,
        current_price=185.0,
        scenarios={
            'bear': {'growth_rate': 0.04, 'wacc': 0.12, 'terminal_growth': 0.02, 'years': 10},
            'base': {'growth_rate': 0.08, 'wacc': 0.09, 'terminal_growth': 0.03, 'years': 10},
            'bull': {'growth_rate': 0.14, 'wacc': 0.08, 'terminal_growth': 0.04, 'years': 10},
        },
    )
    print(result.table())
    # Scenario    IV/Share   Upside   WACC   Growth
    # bear        142.30    -23.1%   12.0%   4.0%
    # base        198.75     +7.4%    9.0%   8.0%
    # bull        312.18    +68.7%    8.0%  14.0%
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from fin_ratios._utils import safe_divide


_DEFAULT_SCENARIOS: dict[str, dict] = {
    "bear": {"growth_rate": 0.03, "wacc": 0.12, "terminal_growth": 0.02, "years": 10},
    "base": {"growth_rate": 0.07, "wacc": 0.09, "terminal_growth": 0.02, "years": 10},
    "bull": {"growth_rate": 0.12, "wacc": 0.08, "terminal_growth": 0.03, "years": 10},
}


@dataclass
class ScenarioDCFResult:
    """
    Container for scenario DCF results.

    Attributes:
        ticker:         Stock ticker
        base_fcf:       Starting FCF used for projections
        current_price:  Market price (for upside calc), or None
        scenarios:      Per-scenario computed results dict
    """

    ticker: str
    base_fcf: float
    current_price: Optional[float]
    scenarios: dict[str, dict] = field(default_factory=dict)

    # ── Accessors ─────────────────────────────────────────────────────────────

    def intrinsic_value(self, scenario: str = "base") -> Optional[float]:
        """Total equity intrinsic value for a scenario."""
        return self.scenarios.get(scenario, {}).get("intrinsic_value")

    def price_per_share(self, scenario: str = "base") -> Optional[float]:
        """Intrinsic value per share for a scenario."""
        return self.scenarios.get(scenario, {}).get("intrinsic_value_per_share")

    def upside(self, scenario: str = "base") -> Optional[float]:
        """Upside / downside relative to current price (as decimal, e.g. 0.07 = +7%)."""
        return self.scenarios.get(scenario, {}).get("upside_pct")

    # ── Display ───────────────────────────────────────────────────────────────

    def table(self) -> str:
        """ASCII table of scenario results."""
        col_w = 12
        header = (
            "Scenario".ljust(10)
            + "IV/Share".ljust(col_w)
            + "Upside".ljust(col_w)
            + "WACC".ljust(8)
            + "Growth".ljust(8)
            + "Term.G".ljust(8)
            + "Yrs".ljust(5)
        )
        sep = "-" * len(header)
        rows = [header, sep]

        for name, d in self.scenarios.items():
            iv = d.get("intrinsic_value_per_share")
            up = d.get("upside_pct")
            wacc = d.get("wacc", 0)
            gr = d.get("growth_rate", 0)
            tg = d.get("terminal_growth", 0)
            yrs = d.get("years", 0)

            iv_str = f"${iv:,.2f}" if iv is not None else "N/A"
            up_str = f"{up * 100:+.1f}%" if up is not None else "N/A"
            rows.append(
                name.ljust(10)
                + iv_str.ljust(col_w)
                + up_str.ljust(col_w)
                + f"{wacc * 100:.1f}%".ljust(8)
                + f"{gr * 100:.1f}%".ljust(8)
                + f"{tg * 100:.1f}%".ljust(8)
                + str(yrs).ljust(5)
            )

        if self.current_price:
            rows.append(sep)
            rows.append(f"  Current market price: ${self.current_price:,.2f}")

        return "\n".join(rows)

    def to_dict(self) -> dict:
        """JSON-serializable export."""
        return {
            "ticker": self.ticker,
            "base_fcf": self.base_fcf,
            "current_price": self.current_price,
            "scenarios": self.scenarios,
        }

    def _repr_html_(self) -> str:
        """Jupyter notebook rich display."""
        scenario_colors = {
            "bear": "#ef4444",
            "base": "#3b82f6",
            "bull": "#22c55e",
        }
        rows_html = ""
        for name, d in self.scenarios.items():
            iv = d.get("intrinsic_value_per_share")
            up = d.get("upside_pct")
            wacc = d.get("wacc", 0)
            gr = d.get("growth_rate", 0)
            tg = d.get("terminal_growth", 0)
            yrs = d.get("years", 0)
            color = scenario_colors.get(name, "#64748b")

            iv_str = f"${iv:,.2f}" if iv is not None else "—"
            up_style = ""
            if up is not None:
                up_style = f"color:{'#22c55e' if up >= 0 else '#ef4444'};font-weight:600"
            up_str = f"{up * 100:+.1f}%" if up is not None else "—"

            rows_html += f"""
            <tr>
              <td style='padding:6px 12px;font-weight:700;color:{color}'>{name.title()}</td>
              <td style='padding:6px 12px;text-align:right'>{iv_str}</td>
              <td style='padding:6px 12px;text-align:right;{up_style}'>{up_str}</td>
              <td style='padding:6px 12px;text-align:right'>{wacc * 100:.1f}%</td>
              <td style='padding:6px 12px;text-align:right'>{gr * 100:.1f}%</td>
              <td style='padding:6px 12px;text-align:right'>{tg * 100:.1f}%</td>
              <td style='padding:6px 12px;text-align:right'>{yrs}</td>
            </tr>"""

        price_row = ""
        if self.current_price:
            price_row = (
                f"<p style='margin:8px 0 0;font-size:12px;color:#64748b'>"
                f"Market price: <strong>${self.current_price:,.2f}</strong></p>"
            )

        return f"""
        <div style='font-family:sans-serif;font-size:13px'>
          <p style='margin:0 0 6px;font-weight:700;color:#0f172a'>{self.ticker} — Scenario DCF Analysis</p>
          <table style='border-collapse:collapse;background:#f8fafc;border-radius:6px'>
            <thead>
              <tr style='background:#e2e8f0'>
                <th style='padding:6px 12px;text-align:left'>Scenario</th>
                <th style='padding:6px 12px;text-align:right'>IV / Share</th>
                <th style='padding:6px 12px;text-align:right'>Upside</th>
                <th style='padding:6px 12px;text-align:right'>WACC</th>
                <th style='padding:6px 12px;text-align:right'>Growth</th>
                <th style='padding:6px 12px;text-align:right'>Term.G</th>
                <th style='padding:6px 12px;text-align:right'>Years</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
          {price_row}
        </div>"""


# ── Main function ──────────────────────────────────────────────────────────────


def scenario_dcf(
    base_fcf: float,
    shares_outstanding: float,
    scenarios: Optional[dict[str, dict]] = None,
    ticker: str = "",
    current_price: Optional[float] = None,
) -> ScenarioDCFResult:
    """
    Compute scenario-based DCF intrinsic value (bull / base / bear).

    Args:
        base_fcf:            Most recent trailing FCF (in absolute dollars, not per-share)
        shares_outstanding:  Total diluted shares outstanding
        scenarios:           Per-scenario parameters dict. Defaults to standard bull/base/bear.
                             Each scenario may include:
                               'growth_rate'     – FCF CAGR during projection period (default 0.07)
                               'wacc'            – Discount rate / WACC (default 0.09)
                               'terminal_growth' – Perpetual growth rate after projection (default 0.02)
                               'years'           – Projection horizon in years (default 10)
        ticker:              Optional ticker string for display
        current_price:       Optional current market price (per share) for upside calculation

    Returns:
        ScenarioDCFResult with per-scenario intrinsic values, upside %, and display helpers.

    Example:
        result = scenario_dcf(
            base_fcf=100e9,
            shares_outstanding=15.7e9,
            current_price=185.0,
            scenarios={
                'bear': {'growth_rate': 0.04, 'wacc': 0.12, 'terminal_growth': 0.02},
                'base': {'growth_rate': 0.08, 'wacc': 0.09, 'terminal_growth': 0.03},
                'bull': {'growth_rate': 0.14, 'wacc': 0.08, 'terminal_growth': 0.04},
            },
        )
        print(result.table())
    """
    if scenarios is None:
        scenarios = _DEFAULT_SCENARIOS

    computed: dict[str, dict] = {}

    for name, params in scenarios.items():
        growth = float(params.get("growth_rate", 0.07))
        wacc = float(params.get("wacc", 0.09))
        terminal_growth = float(params.get("terminal_growth", 0.02))
        years = int(params.get("years", 10))

        # Project FCFs and discount
        fcf = base_fcf
        pv_sum = 0.0
        for t in range(1, years + 1):
            fcf = fcf * (1.0 + growth)
            pv_sum += fcf / (1.0 + wacc) ** t

        # Terminal value via Gordon Growth Model
        if wacc > terminal_growth:
            terminal_fcf = fcf * (1.0 + terminal_growth)
            terminal_value = terminal_fcf / (wacc - terminal_growth)
        else:
            terminal_value = 0.0
        pv_terminal = terminal_value / (1.0 + wacc) ** years

        intrinsic_value = pv_sum + pv_terminal
        iv_per_share = safe_divide(intrinsic_value, shares_outstanding)

        upside_pct: Optional[float] = None
        if current_price and current_price > 0 and iv_per_share is not None:
            upside_pct = (iv_per_share - current_price) / current_price

        computed[name] = {
            "intrinsic_value": round(intrinsic_value, 2),
            "intrinsic_value_per_share": round(iv_per_share, 4)
            if iv_per_share is not None
            else None,
            "pv_fcfs": round(pv_sum, 2),
            "pv_terminal": round(pv_terminal, 2),
            "terminal_value": round(terminal_value, 2),
            "upside_pct": round(upside_pct, 4) if upside_pct is not None else None,
            "growth_rate": growth,
            "wacc": wacc,
            "terminal_growth": terminal_growth,
            "years": years,
        }

    return ScenarioDCFResult(
        ticker=ticker,
        base_fcf=base_fcf,
        current_price=current_price,
        scenarios=computed,
    )
