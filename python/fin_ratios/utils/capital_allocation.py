"""
Capital Allocation Quality Score.

Measures how effectively management deploys the capital entrusted to it.
A company that consistently earns above-WACC returns, converts NOPAT to FCF
efficiently, grows assets proportionally with revenue, and handles shareholder
distributions with discipline scores highest.

Signals
-------
1. Value Creation     (35%) — ROIC vs WACC spread level and trend
2. FCF Quality        (25%) — NOPAT-to-FCF conversion rate and consistency
3. Reinvestment Yield (25%) — incremental revenue per dollar of incremental assets
4. Payout Discipline  (15%) — dividend FCF coverage; FCF retention vs ROIC logic

Score: 0–100
Rating: 'excellent' (75–100), 'good' (50–74), 'fair' (25–49), 'poor' (0–24)

References
----------
Koller, Goedhart & Wessels (2020) — Valuation (7th ed.), McKinsey & Company
Mauboussin, M.J. (2012) — The True Measures of Success, HBR
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


# ── Field registry ────────────────────────────────────────────────────────────

_ZERO_FIELDS = frozenset(
    {
        "revenue",
        "ebit",
        "total_assets",
        "total_equity",
        "total_debt",
        "cash",
        "capex",
        "depreciation",
        "interest_expense",
        "income_tax_expense",
        "current_assets",
        "current_liabilities",
        "dividends_paid",
        "ebt",
    }
)

_ALIASES: dict[str, list[str]] = {
    "ebit": ["operating_income"],
    "total_debt": ["long_term_debt"],
    "depreciation": ["depreciation_amortization"],
    "dividends_paid": ["dividends", "dividend_payments", "dividends_and_other_cash_distributions"],
}


class _Acc:
    """Uniform attribute access for dicts, dataclasses, and arbitrary objects."""

    def __init__(self, src: Any) -> None:
        object.__setattr__(self, "_src", src)

    def _raw(self, name: str) -> Any:
        src = object.__getattribute__(self, "_src")
        if isinstance(src, dict):
            return src.get(name)
        return getattr(src, name, None)

    def __getattr__(self, name: str) -> float:
        val = self._raw(name)
        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            return float(val)
        for alias in _ALIASES.get(name, []):
            val = self._raw(alias)
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                return float(val)
        if name == "ebt":
            ebit = self._raw("ebit") or self._raw("operating_income") or 0.0
            interest = self._raw("interest_expense") or 0.0
            if ebit or interest:
                return float(ebit) - float(interest)
        if name in _ZERO_FIELDS:
            return 0.0
        raise AttributeError(name)


# ── Statistical helpers ───────────────────────────────────────────────────────


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _cv(xs: list[float]) -> float:
    m = _mean(xs)
    return _std(xs) / abs(m) if abs(m) > 1e-9 else 1.0


def _ols_slope(ys: list[float]) -> float:
    n = len(ys)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = _mean(ys)
    ss_xx = sum((i - x_mean) ** 2 for i in range(n))
    ss_xy = sum((i - x_mean) * (ys[i] - y_mean) for i in range(n))
    return ss_xy / ss_xx if ss_xx else 0.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ── WACC estimation ───────────────────────────────────────────────────────────


def _estimate_wacc(accs: list[_Acc], provided: Optional[float]) -> float:
    if provided is not None:
        return provided
    d = accs[-1]
    equity = d.total_equity
    debt = d.total_debt
    cash = d.cash
    total_cap = equity + debt - cash
    if total_cap <= 0:
        return 0.10
    cost_equity = 0.045 + 1.0 * 0.055  # CAPM: rf=4.5%, beta=1, ERP=5.5%
    interest = d.interest_expense
    if debt > 0 and interest > 0:
        pre_tax_cod = _clamp(interest / debt, 0.02, 0.15)
        ebt = d.ebt
        tax = d.income_tax_expense
        tax_rate = _clamp(tax / ebt, 0.0, 0.40) if ebt > 0 and tax > 0 else 0.21
        cost_debt = pre_tax_cod * (1.0 - tax_rate)
    else:
        cost_debt = 0.04
    w_e = _clamp(equity / total_cap, 0.0, 1.0)
    w_d = 1.0 - w_e
    return _clamp(w_e * cost_equity + w_d * cost_debt, 0.06, 0.20)


# ── ROIC per year ─────────────────────────────────────────────────────────────


def _year_roic(d: _Acc) -> Optional[float]:
    ebit = d.ebit
    ic = d.total_equity + d.total_debt - d.cash
    if ic <= 0:
        return None
    ebt = d.ebt
    tax = d.income_tax_expense
    tax_rate = _clamp(tax / ebt, 0.0, 0.50) if ebt > 0 and tax > 0 else 0.21
    return ebit * (1.0 - tax_rate) / ic


# ── Signal 1: Value Creation (ROIC vs WACC) ───────────────────────────────────


def _score_value_creation(accs: list[_Acc], wacc: float) -> tuple[float, list[str]]:
    roic_vals = [r for a in accs if (r := _year_roic(a)) is not None]
    if not roic_vals:
        return 0.30, ["Value creation: insufficient ROIC data (neutral score)"]

    spreads = [r - wacc for r in roic_vals]
    mean_spread = _mean(spreads)
    slope = _ols_slope(spreads)

    # Level: spread from -5% → 0.0, +20% → 1.0
    level = _clamp((mean_spread + 0.05) / 0.25, 0.0, 1.0)
    trend_adj = 0.10 if slope > 0.01 else (-0.10 if slope < -0.01 else 0.0)
    consistency = max(0.0, 1.0 - _cv(spreads) * 0.5)
    score = _clamp(0.60 * level + 0.40 * consistency + trend_adj, 0.0, 1.0)

    pos = sum(1 for s in spreads if s > 0)
    direction = "improving" if slope > 0.01 else ("declining" if slope < -0.01 else "stable")
    return score, [
        f"Value creation: mean ROIC-WACC spread {mean_spread * 100:+.1f}%  "
        f"({pos}/{len(spreads)} years positive)",
        f"Spread trend: {direction}  (OLS {slope * 100:+.2f}%/yr)",
    ]


# ── Signal 2: FCF Quality ─────────────────────────────────────────────────────


def _score_fcf_quality(accs: list[_Acc]) -> tuple[float, list[str]]:
    conversions: list[float] = []
    for d in accs:
        ebit = d.ebit
        if ebit <= 0:
            continue
        ebt = d.ebt
        tax = d.income_tax_expense
        tax_rate = _clamp(tax / ebt, 0.0, 0.50) if ebt > 0 and tax > 0 else 0.21
        nopat = ebit * (1.0 - tax_rate)
        if nopat <= 0:
            continue
        fcf = nopat + d.depreciation - d.capex
        conversions.append(fcf / nopat)

    if not conversions:
        return 0.40, ["FCF quality: insufficient data (neutral score)"]

    mean_conv = _mean(conversions)
    level = _clamp(mean_conv / 1.2, 0.0, 1.0)
    stability = max(0.0, 1.0 - _cv(conversions) * 1.5)
    score = _clamp(0.65 * level + 0.35 * stability, 0.0, 1.0)

    quality = (
        "capital-light"
        if mean_conv >= 1.0
        else ("capital-heavy" if mean_conv < 0.5 else "moderate")
    )
    return score, [
        f"FCF quality: mean NOPAT-to-FCF conversion {mean_conv * 100:.0f}%  ({quality})",
    ]


# ── Signal 3: Reinvestment Yield ──────────────────────────────────────────────


def _score_reinvestment_yield(accs: list[_Acc]) -> tuple[float, list[str]]:
    incremental_yields: list[float] = []
    for i in range(1, len(accs)):
        prev, curr = accs[i - 1], accs[i]
        delta_assets = curr.total_assets - prev.total_assets
        delta_revenue = curr.revenue - prev.revenue
        if delta_assets > 1e6:
            incremental_yields.append(delta_revenue / delta_assets)

    if not incremental_yields:
        return 0.40, ["Reinvestment yield: insufficient data (neutral score)"]

    mean_yield = _mean(incremental_yields)
    # -0.2 → 0.0, 1.5 → 1.0
    level = _clamp((mean_yield + 0.2) / 1.7, 0.0, 1.0)
    consistency = max(0.0, 1.0 - _cv(incremental_yields) * 0.5)
    score = _clamp(0.65 * level + 0.35 * consistency, 0.0, 1.0)

    pos = sum(1 for y in incremental_yields if y > 0)
    return score, [
        f"Reinvestment yield: mean incremental revenue/asset {mean_yield:.2f}x  "
        f"({pos}/{len(incremental_yields)} periods productive)",
    ]


# ── Signal 4: Payout Discipline ───────────────────────────────────────────────


def _score_payout_discipline(accs: list[_Acc], wacc: float) -> tuple[float, list[str]]:
    fcf_coverage_vals: list[float] = []

    for d in accs:
        ebit = d.ebit
        if ebit <= 0:
            continue
        ebt = d.ebt
        tax = d.income_tax_expense
        tax_rate = _clamp(tax / ebt, 0.0, 0.50) if ebt > 0 and tax > 0 else 0.21
        nopat = ebit * (1.0 - tax_rate)
        fcf = nopat + d.depreciation - d.capex
        dividends = d.dividends_paid
        if dividends > 0:
            fcf_coverage_vals.append(fcf / dividends if fcf > 0 else 0.0)

    if fcf_coverage_vals:
        mean_cov = _mean(fcf_coverage_vals)
        # 0.5x → 0.0, 2.5x → 1.0
        score = _clamp((mean_cov - 0.5) / 2.0, 0.0, 1.0)
        health = "healthy" if mean_cov >= 2.0 else ("tight" if mean_cov >= 1.0 else "stressed")
        return score, [
            f"Payout discipline: mean FCF/dividend coverage {mean_cov:.1f}x  ({health})",
        ]

    # No dividend data: use FCF retention logic (reinvesting vs WACC)
    roic_vals = [r for a in accs if (r := _year_roic(a)) is not None]
    mean_roic = _mean(roic_vals) if roic_vals else wacc
    if mean_roic > wacc * 1.2:
        return 0.70, ["Payout discipline: retaining FCF in above-WACC business (good reinvestment)"]
    if mean_roic <= wacc:
        return 0.35, ["Payout discipline: retaining FCF despite below-WACC returns (concerning)"]
    return 0.50, ["Payout discipline: no dividend data available (neutral score)"]


# ── Result types ─────────────────────────────────────────────────────────────


@dataclass
class CapitalAllocationComponents:
    value_creation: float  # 0–1
    fcf_quality: float  # 0–1
    reinvestment_yield: float  # 0–1
    payout_discipline: float  # 0–1


@dataclass
class CapitalAllocationScore:
    """Result of the Capital Allocation Quality Score computation."""

    score: int  # 0–100
    rating: str  # 'excellent' | 'good' | 'fair' | 'poor'
    components: CapitalAllocationComponents
    wacc_used: float
    years_analyzed: int
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "excellent": "Management allocates capital with high discipline — consistent value creation, "
            "strong FCF conversion, and efficient reinvestment.",
            "good": "Solid capital allocation with above-average returns and reasonable reinvestment efficiency.",
            "fair": "Mixed capital allocation — some value creation but inconsistency or inefficient deployment.",
            "poor": "Weak capital allocation — below-WACC returns, poor FCF conversion, or inefficient reinvestment.",
        }
        return f"Capital Allocation Score: {self.score}/100 [{self.rating.upper()}]. {descs.get(self.rating, '')}"

    def table(self) -> str:
        w = 48
        sep = "─" * w
        return "\n".join(
            [
                f"Capital Allocation Score: {self.score}/100  [{self.rating.upper()}]",
                sep,
                f"{'Component':<30} {'Score':>7}  {'Weight':>6}",
                sep,
                f"{'Value Creation':<30} {self.components.value_creation * 100:>6.0f}%   {'35%':>6}",
                f"{'FCF Quality':<30} {self.components.fcf_quality * 100:>6.0f}%   {'25%':>6}",
                f"{'Reinvestment Yield':<30} {self.components.reinvestment_yield * 100:>6.0f}%   {'25%':>6}",
                f"{'Payout Discipline':<30} {self.components.payout_discipline * 100:>6.0f}%   {'15%':>6}",
                sep,
                f"{'WACC estimate used':<30} {self.wacc_used * 100:>6.1f}%",
                f"{'Years of data analyzed':<30} {self.years_analyzed:>7}",
            ]
        )

    def _repr_html_(self) -> str:
        colours = {
            "excellent": "#1a7f37",
            "good": "#0969da",
            "fair": "#9a6700",
            "poor": "#cf222e",
        }
        c = colours.get(self.rating, "#57606a")
        rows = [
            ("Value Creation", self.components.value_creation, "35%"),
            ("FCF Quality", self.components.fcf_quality, "25%"),
            ("Reinvestment Yield", self.components.reinvestment_yield, "25%"),
            ("Payout Discipline", self.components.payout_discipline, "15%"),
        ]
        row_html = "".join(
            f"<tr><td>{n}</td><td style='text-align:right'>{v * 100:.0f}%</td>"
            f"<td style='text-align:right;color:#57606a'>{w}</td></tr>"
            for n, v, w in rows
        )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:480px'>"
            f"<div style='font-size:1.1em;font-weight:bold;color:{c}'>"
            f"Capital Allocation: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.rating.upper()}]</span></div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Component</th><th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"WACC: {self.wacc_used * 100:.1f}% | {self.years_analyzed} years</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "rating": self.rating,
            "components": {
                "value_creation": round(self.components.value_creation, 4),
                "fcf_quality": round(self.components.fcf_quality, 4),
                "reinvestment_yield": round(self.components.reinvestment_yield, 4),
                "payout_discipline": round(self.components.payout_discipline, 4),
            },
            "wacc_used": round(self.wacc_used, 4),
            "years_analyzed": self.years_analyzed,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


# ── Public API ────────────────────────────────────────────────────────────────


def capital_allocation_score_from_series(
    annual_data: Sequence[Any],
    wacc: Optional[float] = None,
) -> CapitalAllocationScore:
    """Compute Capital Allocation Score from a sequence of annual financial records.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects with attributes).
        Must be in chronological order (oldest first). Minimum 2 years required.
    wacc:
        Optional override for WACC. If omitted, estimated from capital structure.

    Returns
    -------
    CapitalAllocationScore
        Dataclass with `.score` (0–100), `.rating`, `.components`, `.evidence`,
        `.table()`, `._repr_html_()`, and `.to_dict()`.
    """
    if len(annual_data) < 2:
        raise ValueError("capital_allocation_score requires at least 2 years of data.")

    accs = [_Acc(d) for d in annual_data]
    wacc_val = _estimate_wacc(accs, wacc)

    vc_score, vc_ev = _score_value_creation(accs, wacc_val)
    fcf_score, fcf_ev = _score_fcf_quality(accs)
    ri_score, ri_ev = _score_reinvestment_yield(accs)
    pd_score, pd_ev = _score_payout_discipline(accs, wacc_val)

    raw = 0.35 * vc_score + 0.25 * fcf_score + 0.25 * ri_score + 0.15 * pd_score
    score = round(_clamp(raw, 0.0, 1.0) * 100)

    rating = (
        "excellent" if score >= 75 else "good" if score >= 50 else "fair" if score >= 25 else "poor"
    )

    return CapitalAllocationScore(
        score=score,
        rating=rating,
        components=CapitalAllocationComponents(
            value_creation=round(vc_score, 4),
            fcf_quality=round(fcf_score, 4),
            reinvestment_yield=round(ri_score, 4),
            payout_discipline=round(pd_score, 4),
        ),
        wacc_used=wacc_val,
        years_analyzed=len(accs),
        evidence=vc_ev + fcf_ev + ri_ev + pd_ev,
    )


def capital_allocation_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
    wacc: Optional[float] = None,
) -> CapitalAllocationScore:
    """Compute Capital Allocation Score by fetching data for a ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL').
    years : int
        Number of years of historical data to fetch (default 10).
    source : str
        Data source: 'yahoo' (default) or 'edgar'.
    wacc : float, optional
        Override WACC estimate.
    """
    try:
        if source == "edgar":
            from ..fetchers.edgar import fetch_edgar

            raw = fetch_edgar(ticker, num_years=years)
        else:
            from ..fetchers.yahoo import fetch_yahoo

            raw = [fetch_yahoo(ticker)]
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch data for {ticker!r}: {exc}") from exc
    return capital_allocation_score_from_series(raw, wacc=wacc)
