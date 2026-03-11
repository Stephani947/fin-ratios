"""
Fair Value Range.

Synthesises multiple valuation methods into a bull/base/bear fair value
estimate. No single method is reliable in isolation — the composite range
reflects where multiple frameworks converge.

Methods
-------
1. DCF (2-stage)          — discounted cash flow with explicit + terminal stage
2. Graham Number          — Benjamin Graham's geometric mean intrinsic value
3. FCF Yield              — normalise free cash flow at a target yield
4. EV/EBITDA Multiple     — EBITDA × target multiple, bridge to equity value
5. Earnings Power Value   — no-growth intrinsic value: NOPAT / WACC

Output
------
FairValueRange:
  estimates    — per-method fair value per share
  base_value   — trimmed median across methods
  bull_value   — 75th percentile
  bear_value   — 25th percentile
  upside_pct   — (base / current_price − 1) × 100 if price provided

References
----------
Graham & Dodd (1934)      — Security Analysis
Koller et al. (2020)      — Valuation (7th ed.), McKinsey & Company
Greenwald et al. (2001)   — Value Investing: From Graham to Buffett
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _percentile(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    n = len(xs)
    idx = p / 100.0 * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (idx - lo)


def _trimmed_mean(xs: list[float]) -> float:
    """Mean after dropping min and max when len > 3."""
    if len(xs) <= 3:
        return sum(xs) / len(xs)
    xs = sorted(xs)[1:-1]
    return sum(xs) / len(xs)


# ── Per-method calculators ─────────────────────────────────────────────────────

def _dcf_value(
    fcf: float,
    growth_rate: float,
    terminal_growth: float,
    wacc: float,
    shares: float,
    years: int = 10,
) -> Optional[float]:
    if wacc <= terminal_growth or fcf <= 0 or shares <= 0:
        return None
    pv = 0.0
    cf = fcf
    for i in range(1, years + 1):
        cf *= (1 + growth_rate)
        pv += cf / (1 + wacc) ** i
    terminal = cf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv += terminal / (1 + wacc) ** years
    return pv / shares


def _graham_value(eps: float, bvps: float) -> Optional[float]:
    if eps <= 0 or bvps <= 0:
        return None
    return math.sqrt(22.5 * eps * bvps)


def _fcf_yield_value(
    fcf: float, shares: float, target_yield: float
) -> Optional[float]:
    if fcf <= 0 or shares <= 0 or target_yield <= 0:
        return None
    return (fcf / target_yield) / shares


def _ev_ebitda_value(
    ebitda: float,
    total_debt: float,
    cash: float,
    shares: float,
    multiple: float,
) -> Optional[float]:
    if ebitda <= 0 or shares <= 0:
        return None
    equity_value = ebitda * multiple - total_debt + cash
    return equity_value / shares if equity_value > 0 else None


def _epv_value(
    ebit: float,
    tax_rate: float,
    wacc: float,
    shares: float,
    cash: float = 0.0,
    total_debt: float = 0.0,
) -> Optional[float]:
    if ebit <= 0 or wacc <= 0 or shares <= 0:
        return None
    nopat = ebit * (1.0 - tax_rate)
    equity_value = nopat / wacc + cash - total_debt
    return equity_value / shares if equity_value > 0 else None


# ── Result type ────────────────────────────────────────────────────────────────

@dataclass
class FairValueRange:
    """Result of the Fair Value Range computation."""

    estimates: dict[str, float]    # per-method per-share values
    base_value: float              # trimmed median
    bull_value: float              # 75th percentile
    bear_value: float              # 25th percentile
    methods_used: int
    current_price: Optional[float] = None

    @property
    def upside_pct(self) -> Optional[float]:
        if self.current_price and self.current_price > 0:
            return (self.base_value / self.current_price - 1.0) * 100.0
        return None

    @property
    def margin_of_safety(self) -> Optional[float]:
        """Bear-case value vs current price."""
        if self.current_price and self.current_price > 0:
            return (self.bear_value / self.current_price - 1.0) * 100.0
        return None

    @property
    def interpretation(self) -> str:
        upside = self.upside_pct
        if upside is None:
            return (
                f"Fair value range: ${self.bear_value:.2f} – ${self.bull_value:.2f}  "
                f"(base ${self.base_value:.2f})"
            )
        stance = (
            "significantly undervalued" if upside > 30 else
            "undervalued"               if upside > 10 else
            "fairly valued"             if upside > -10 else
            "overvalued"                if upside > -25 else
            "significantly overvalued"
        )
        return (
            f"Fair value base ${self.base_value:.2f} vs current ${self.current_price:.2f} "
            f"({upside:+.1f}% upside) — {stance}"
        )

    def table(self) -> str:
        w = 50
        sep = "─" * w
        lines = [
            "Fair Value Range",
            sep,
            f"{'Method':<30} {'Value':>10}",
            sep,
        ]
        for method, val in sorted(self.estimates.items()):
            lines.append(f"  {method:<28} ${val:>9.2f}")
        lines += [
            sep,
            f"{'Bear (25th pct)':<30} ${self.bear_value:>9.2f}",
            f"{'Base (trimmed median)':<30} ${self.base_value:>9.2f}",
            f"{'Bull (75th pct)':<30} ${self.bull_value:>9.2f}",
        ]
        if self.current_price:
            lines += [
                sep,
                f"{'Current price':<30} ${self.current_price:>9.2f}",
                f"{'Upside (base)':<30} {self.upside_pct:>+9.1f}%",
                f"{'Margin of safety (bear)':<30} {self.margin_of_safety:>+9.1f}%",
            ]
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        upside = self.upside_pct
        color = (
            "#1a7f37" if upside and upside > 10 else
            "#9a6700" if upside and upside > -10 else
            "#cf222e" if upside else "#0969da"
        )
        rows = "".join(
            f"<tr><td style='padding:4px 8px'>{m}</td>"
            f"<td style='text-align:right;padding:4px 8px'>${v:.2f}</td></tr>"
            for m, v in sorted(self.estimates.items())
        )
        summary = (
            f"<tr style='font-weight:bold;border-top:1px solid #d0d7de'>"
            f"<td style='padding:4px 8px'>Bear / Base / Bull</td>"
            f"<td style='text-align:right;padding:4px 8px'>"
            f"${self.bear_value:.2f} / "
            f"<span style='color:{color}'>${self.base_value:.2f}</span> / "
            f"${self.bull_value:.2f}</td></tr>"
        )
        price_row = ""
        if self.current_price:
            price_row = (
                f"<tr><td style='padding:4px 8px;color:#57606a'>Current price</td>"
                f"<td style='text-align:right;padding:4px 8px;color:{color};font-weight:bold'>"
                f"${self.current_price:.2f} ({self.upside_pct:+.1f}%)</td></tr>"
            )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:480px'>"
            f"<div style='font-size:1.1em;font-weight:bold;margin-bottom:10px'>"
            f"Fair Value Range"
            f"<span style='font-size:0.75em;color:#57606a;margin-left:8px'>"
            f"({self.methods_used} methods)</span></div>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"{rows}{summary}{price_row}</table>"
            f"<div style='margin-top:10px;font-size:0.85em;color:#57606a'>"
            f"{self.interpretation}</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        d: dict = {
            "estimates":    {k: round(v, 2) for k, v in self.estimates.items()},
            "base_value":   round(self.base_value, 2),
            "bull_value":   round(self.bull_value, 2),
            "bear_value":   round(self.bear_value, 2),
            "methods_used": self.methods_used,
            "interpretation": self.interpretation,
        }
        if self.current_price is not None:
            d["current_price"]    = self.current_price
            d["upside_pct"]       = round(self.upside_pct or 0.0, 2)
            d["margin_of_safety"] = round(self.margin_of_safety or 0.0, 2)
        return d


# ── Public API ────────────────────────────────────────────────────────────────

def fair_value_range(
    *,
    # DCF inputs
    fcf: Optional[float] = None,
    shares: Optional[float] = None,
    growth_rate: float = 0.08,
    terminal_growth: float = 0.03,
    wacc: float = 0.09,
    dcf_years: int = 10,
    # Graham Number inputs
    eps: Optional[float] = None,
    bvps: Optional[float] = None,
    # FCF Yield inputs
    target_yield: float = 0.04,
    # EV/EBITDA inputs
    ebitda: Optional[float] = None,
    total_debt: float = 0.0,
    cash: float = 0.0,
    ev_ebitda_multiple: float = 12.0,
    # EPV inputs
    ebit: Optional[float] = None,
    tax_rate: float = 0.21,
    # Optional market context
    current_price: Optional[float] = None,
) -> FairValueRange:
    """Compute a composite fair value range from multiple valuation methods.

    All monetary inputs should be in the same currency unit (e.g. millions of
    dollars). `fcf`, `ebitda`, and `ebit` are total company values; `shares`
    converts them to per-share estimates.

    Parameters
    ----------
    fcf             : Free cash flow (total, not per-share)
    shares          : Diluted shares outstanding
    growth_rate     : Near-term FCF/earnings growth rate (default 8%)
    terminal_growth : Long-run terminal growth rate (default 3%)
    wacc            : Discount rate (default 9%)
    dcf_years       : DCF projection horizon (default 10)
    eps             : Earnings per share (for Graham Number)
    bvps            : Book value per share (for Graham Number)
    target_yield    : FCF yield to normalise at (default 4%)
    ebitda          : EBITDA (for EV/EBITDA method)
    total_debt      : Total debt (for EV/EBITDA bridge, default 0)
    cash            : Cash and equivalents (default 0)
    ev_ebitda_multiple : Target EV/EBITDA multiple (default 12×)
    ebit            : EBIT (for Earnings Power Value)
    tax_rate        : Effective tax rate (default 21%)
    current_price   : Current market price (enables upside/discount calculation)

    Returns
    -------
    FairValueRange
        Dataclass with per-method estimates, composite bear/base/bull range,
        `.table()`, `._repr_html_()`, `.to_dict()`, and `.interpretation`.

    Raises
    ------
    ValueError
        If no method can be computed from the provided inputs.

    Example
    -------
    >>> result = fair_value_range(
    ...     fcf=90e9, shares=15.5e9, growth_rate=0.07,
    ...     eps=6.10, bvps=4.00,
    ...     ebitda=120e9, total_debt=100e9, cash=60e9,
    ...     current_price=180.0,
    ... )
    >>> print(result.table())
    """
    estimates: dict[str, float] = {}

    if fcf and shares:
        v = _dcf_value(fcf, growth_rate, terminal_growth, wacc, shares, dcf_years)
        if v and v > 0:
            estimates["DCF (2-stage)"] = v

        v = _fcf_yield_value(fcf, shares, target_yield)
        if v and v > 0:
            estimates[f"FCF Yield ({target_yield*100:.0f}%)"] = v

    if eps and bvps:
        v = _graham_value(eps, bvps)
        if v and v > 0:
            estimates["Graham Number"] = v

    if ebitda and shares:
        v = _ev_ebitda_value(ebitda, total_debt, cash, shares, ev_ebitda_multiple)
        if v and v > 0:
            estimates[f"EV/EBITDA ({ev_ebitda_multiple:.0f}×)"] = v

    if ebit and shares:
        v = _epv_value(ebit, tax_rate, wacc, shares, cash, total_debt)
        if v and v > 0:
            estimates["Earnings Power Value"] = v

    if not estimates:
        raise ValueError(
            "No valuation methods could be computed. "
            "Provide at least one of: (fcf + shares), (eps + bvps), "
            "(ebitda + shares), or (ebit + shares)."
        )

    vals = list(estimates.values())
    return FairValueRange(
        estimates=estimates,
        base_value=round(_trimmed_mean(vals), 2),
        bull_value=round(_percentile(vals, 75), 2),
        bear_value=round(_percentile(vals, 25), 2),
        methods_used=len(estimates),
        current_price=current_price,
    )
