"""
Management Quality Score.

Evaluates the quality of management's operational execution across four
dimensions: capital efficiency (ROIC vs hurdle rate), margin discipline,
shareholder orientation (buybacks vs dilution), and revenue growth execution.

Score:  0–100
Rating: 'excellent' (≥75), 'good' (50–74), 'fair' (25–49), 'poor' (<25)

Signals
-------
1. ROIC Excellence         (35%) — mean ROIC vs hurdle rate, trend, consistency
2. Margin Stability & Growth (25%) — operating margin level, stability, OLS trend
3. Shareholder Orientation (25%) — share count trend (buybacks vs dilution)
4. Revenue Execution       (15%) — growth consistency and mean growth rate

References
----------
Mauboussin, M.J. (2012) — The True Measures of Success, HBR
Koller, Goedhart & Wessels (2020) — Valuation (7th ed.), McKinsey & Company
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .._utils import safe_divide


# ── Field registry ─────────────────────────────────────────────────────────────

_ZERO_FIELDS = frozenset({
    "revenue", "ebit", "total_assets", "total_equity", "total_debt", "cash",
    "capex", "depreciation", "interest_expense", "income_tax_expense",
    "current_assets", "current_liabilities", "shares_outstanding",
    "dividends_paid", "ebt",
})

_ALIASES: dict[str, list[str]] = {
    "ebit":             ["operating_income"],
    "total_debt":       ["long_term_debt"],
    "depreciation":     ["depreciation_amortization"],
    "shares_outstanding": ["diluted_shares", "weighted_avg_shares", "common_shares_outstanding"],
    "dividends_paid":   ["dividends", "dividend_payments", "dividends_and_other_cash_distributions"],
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


# ── Statistical helpers ────────────────────────────────────────────────────────

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


def _lerp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y0
    t = _clamp((x - x0) / (x1 - x0), 0.0, 1.0)
    return y0 + t * (y1 - y0)


# ── WACC/ROIC helpers ──────────────────────────────────────────────────────────

def _estimate_hurdle(accs: list[_Acc], provided: Optional[float]) -> float:
    if provided is not None:
        return provided
    return 0.10


def _year_roic(d: _Acc) -> Optional[float]:
    ebit = d.ebit
    ic = d.total_equity + d.total_debt - d.cash
    if ic <= 0:
        return None
    ebt = d.ebt
    tax = d.income_tax_expense
    tax_rate = _clamp(tax / ebt, 0.0, 0.50) if ebt > 0 and tax > 0 else 0.21
    return ebit * (1.0 - tax_rate) / ic


# ── Signal 1: ROIC Excellence ─────────────────────────────────────────────────

def _score_roic_excellence(
    accs: list[_Acc], hurdle: float
) -> tuple[float, list[str]]:
    roic_vals = [r for a in accs if (r := _year_roic(a)) is not None]
    if not roic_vals:
        return 0.40, ["ROIC excellence: insufficient data (neutral score)"]

    mean_roic = _mean(roic_vals)
    slope = _ols_slope(roic_vals)
    consistency = max(0.0, 1.0 - _cv(roic_vals) * 0.5)

    # Level: 5% ROIC → 0.0, 30% ROIC → 1.0
    level = _clamp((mean_roic - 0.05) / 0.25, 0.0, 1.0)
    trend_adj = 0.10 if slope > 0.01 else (-0.10 if slope < -0.01 else 0.0)
    score = _clamp(0.60 * level + 0.40 * consistency + trend_adj, 0.0, 1.0)

    above = sum(1 for r in roic_vals if r > hurdle)
    direction = "improving" if slope > 0.01 else ("declining" if slope < -0.01 else "stable")
    return score, [
        f"ROIC excellence: mean ROIC {mean_roic*100:.1f}%  vs  hurdle {hurdle*100:.1f}%  "
        f"({above}/{len(roic_vals)} years above hurdle)",
        f"ROIC trend: {direction}  (OLS {slope*100:+.2f}%/yr)  consistency {consistency:.0%}",
    ]


# ── Signal 2: Margin Stability & Growth ───────────────────────────────────────

def _score_margin_stability(accs: list[_Acc]) -> tuple[float, list[str]]:
    margins = [
        d.ebit / d.revenue
        for d in accs
        if d.revenue > 0 and d.ebit != 0
    ]
    if not margins:
        return 0.40, ["Margin stability: insufficient data (neutral score)"]

    mean_margin = _mean(margins)
    slope = _ols_slope(margins)
    stability = max(0.0, 1.0 - _cv(margins) * 1.5)

    level = _lerp(mean_margin, 0.0, 0.30, 0.0, 1.0)
    trend_adj = 0.10 if slope > 0.005 else (-0.10 if slope < -0.005 else 0.0)
    # normalise trend_adj to [0, 1] contribution
    trend_adj_normalized = _clamp(0.5 + trend_adj * 5.0, 0.0, 1.0)
    score = _clamp(
        0.50 * level + 0.35 * stability + 0.15 * trend_adj_normalized,
        0.0, 1.0,
    )

    direction = "expanding" if slope > 0.005 else ("contracting" if slope < -0.005 else "stable")
    quality = (
        "high-margin" if mean_margin >= 0.20 else
        "moderate-margin" if mean_margin >= 0.10 else
        "low-margin"
    )
    return score, [
        f"Operating margin: mean {mean_margin*100:.1f}%  [{quality}]  stability {stability:.0%}",
        f"Margin trend: {direction}  (OLS {slope*100:+.3f}%/yr)",
    ]


# ── Signal 3: Shareholder Orientation ─────────────────────────────────────────

def _score_shareholder_orientation(accs: list[_Acc]) -> tuple[float, list[str]]:
    share_vals = [d.shares_outstanding for d in accs if d.shares_outstanding > 0]
    if len(share_vals) < 2:
        return 0.50, ["Shareholder orientation: shares outstanding data unavailable (neutral score)"]

    first_shares = share_vals[0]
    slope = _ols_slope(share_vals)

    # slope_pct: annual change as fraction of first year shares
    slope_pct = slope / first_shares if first_shares > 0 else 0.0

    # Declining shares = higher score (buybacks); dilution = lower score
    score = _clamp(0.5 - slope_pct * 5.0, 0.0, 1.0)

    total_change_pct = (share_vals[-1] - share_vals[0]) / share_vals[0] if share_vals[0] > 0 else 0.0
    orientation = (
        "consistent buybacks" if slope_pct < -0.02 else
        "modest buybacks" if slope_pct < 0.0 else
        "stable share count" if slope_pct < 0.01 else
        "modest dilution" if slope_pct < 0.03 else
        "significant dilution"
    )
    return score, [
        f"Share count trend: {orientation}  "
        f"(total change {total_change_pct*100:+.1f}% over {len(share_vals)} years)",
    ]


# ── Signal 4: Revenue Execution ───────────────────────────────────────────────

def _score_revenue_execution(accs: list[_Acc]) -> tuple[float, list[str]]:
    growths: list[float] = []
    for i in range(1, len(accs)):
        prev_rev = accs[i - 1].revenue
        curr_rev = accs[i].revenue
        if prev_rev > 0:
            growths.append((curr_rev - prev_rev) / prev_rev)

    if not growths:
        return 0.40, ["Revenue execution: insufficient data (neutral score)"]

    mean_growth = _mean(growths)
    consistency = max(0.0, 1.0 - _cv(growths) * 0.8) if len(growths) >= 3 else 0.5
    level = _lerp(mean_growth, -0.05, 0.20, 0.0, 1.0)
    score = _clamp(0.55 * level + 0.45 * consistency, 0.0, 1.0)

    quality = (
        "strong growth" if mean_growth >= 0.12 else
        "moderate growth" if mean_growth >= 0.05 else
        "stagnant" if mean_growth >= 0.0 else
        "declining revenue"
    )
    pos = sum(1 for g in growths if g > 0)
    return score, [
        f"Revenue growth: mean {mean_growth*100:.1f}%/yr  [{quality}]  "
        f"({pos}/{len(growths)} periods positive)  consistency {consistency:.0%}",
    ]


# ── Result types ───────────────────────────────────────────────────────────────

@dataclass
class ManagementComponents:
    roic_excellence: float           # 0–1
    margin_stability: float          # 0–1
    shareholder_orientation: float   # 0–1
    revenue_execution: float         # 0–1


@dataclass
class ManagementScore:
    """Result of the Management Quality Score computation."""

    score: int                            # 0–100
    rating: str                           # 'excellent' | 'good' | 'fair' | 'poor'
    components: ManagementComponents
    hurdle_rate_used: float
    years_analyzed: int
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "excellent": "Management demonstrates exceptional operational execution — "
                         "high ROIC, expanding margins, shareholder-friendly capital returns, "
                         "and consistent revenue growth.",
            "good":      "Solid management quality with above-average capital returns and "
                         "reliable execution across most dimensions.",
            "fair":      "Mixed management quality — strength in some areas but inconsistency "
                         "or underperformance in others.",
            "poor":      "Weak management execution — below-hurdle returns, margin pressure, "
                         "dilution, or erratic growth.",
        }
        return (
            f"Management Quality Score: {self.score}/100 [{self.rating.upper()}]. "
            f"{descs.get(self.rating, '')}"
        )

    def table(self) -> str:
        w = 52
        sep = "─" * w
        return "\n".join([
            f"Management Quality Score: {self.score}/100  [{self.rating.upper()}]",
            sep,
            f"{'Component':<34} {'Score':>7}  {'Weight':>6}",
            sep,
            f"{'ROIC Excellence':<34} {self.components.roic_excellence*100:>6.0f}%   {'35%':>6}",
            f"{'Margin Stability & Growth':<34} {self.components.margin_stability*100:>6.0f}%   {'25%':>6}",
            f"{'Shareholder Orientation':<34} {self.components.shareholder_orientation*100:>6.0f}%   {'25%':>6}",
            f"{'Revenue Execution':<34} {self.components.revenue_execution*100:>6.0f}%   {'15%':>6}",
            sep,
            f"{'Hurdle rate used':<34} {self.hurdle_rate_used*100:>6.1f}%",
            f"{'Years of data analyzed':<34} {self.years_analyzed:>7}",
        ])

    def _repr_html_(self) -> str:
        colours = {
            "excellent": "#1a7f37", "good": "#0969da",
            "fair":      "#9a6700", "poor": "#cf222e",
        }
        c = colours.get(self.rating, "#57606a")
        rows = [
            ("ROIC Excellence",          self.components.roic_excellence,          "35%"),
            ("Margin Stability & Growth", self.components.margin_stability,         "25%"),
            ("Shareholder Orientation",   self.components.shareholder_orientation,  "25%"),
            ("Revenue Execution",         self.components.revenue_execution,        "15%"),
        ]
        row_html = "".join(
            f"<tr><td>{n}</td><td style='text-align:right'>{v*100:.0f}%</td>"
            f"<td style='text-align:right;color:#57606a'>{wt}</td></tr>"
            for n, v, wt in rows
        )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:500px'>"
            f"<div style='font-size:1.1em;font-weight:bold;color:{c}'>"
            f"Management Quality: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.rating.upper()}]</span></div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Component</th>"
            f"<th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"Hurdle rate: {self.hurdle_rate_used*100:.1f}% | {self.years_analyzed} years</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "score":  self.score,
            "rating": self.rating,
            "components": {
                "roic_excellence":          round(self.components.roic_excellence, 4),
                "margin_stability":         round(self.components.margin_stability, 4),
                "shareholder_orientation":  round(self.components.shareholder_orientation, 4),
                "revenue_execution":        round(self.components.revenue_execution, 4),
            },
            "hurdle_rate_used": round(self.hurdle_rate_used, 4),
            "years_analyzed":   self.years_analyzed,
            "evidence":         self.evidence,
            "interpretation":   self.interpretation,
        }


# ── Public API ─────────────────────────────────────────────────────────────────

def management_quality_score_from_series(
    annual_data: Sequence[Any],
    hurdle_rate: Optional[float] = None,
) -> ManagementScore:
    """Compute Management Quality Score from a sequence of annual financial records.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects with attributes).
        Must be in chronological order (oldest first). Minimum 3 years required.
    hurdle_rate:
        Optional required rate of return override (default 0.10 = 10%).

    Returns
    -------
    ManagementScore
        Dataclass with ``.score`` (0–100), ``.rating``, ``.components``,
        ``.evidence``, ``.table()``, ``._repr_html_()``, and ``.to_dict()``.
    """
    if len(annual_data) < 3:
        raise ValueError("management_quality_score requires at least 3 years of data.")

    accs = [_Acc(d) for d in annual_data]
    hurdle = _estimate_hurdle(accs, hurdle_rate)

    s_roic, ev_roic = _score_roic_excellence(accs, hurdle)
    s_margin, ev_margin = _score_margin_stability(accs)
    s_share, ev_share = _score_shareholder_orientation(accs)
    s_rev, ev_rev = _score_revenue_execution(accs)

    raw = (
        0.35 * s_roic
        + 0.25 * s_margin
        + 0.25 * s_share
        + 0.15 * s_rev
    )
    score = round(_clamp(raw, 0.0, 1.0) * 100)

    rating = (
        "excellent" if score >= 75 else
        "good"      if score >= 50 else
        "fair"      if score >= 25 else
        "poor"
    )

    return ManagementScore(
        score=score,
        rating=rating,
        components=ManagementComponents(
            roic_excellence=round(s_roic, 4),
            margin_stability=round(s_margin, 4),
            shareholder_orientation=round(s_share, 4),
            revenue_execution=round(s_rev, 4),
        ),
        hurdle_rate_used=hurdle,
        years_analyzed=len(accs),
        evidence=ev_roic + ev_margin + ev_share + ev_rev,
    )


def management_quality_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
    hurdle_rate: Optional[float] = None,
) -> ManagementScore:
    """Fetch data and compute Management Quality Score for a ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL').
    years : int
        Number of years of historical data to fetch (default 10).
    source : str
        Data source: 'yahoo' (default) or 'edgar'.
    hurdle_rate : float, optional
        Override for required rate of return (default 0.10 = 10%).
    """
    try:
        if source == "edgar":
            from ..fetchers.edgar import fetch_edgar
            raw = fetch_edgar(ticker, years=years)
        else:
            from ..fetchers.yahoo import fetch_yahoo_annual
            raw = fetch_yahoo_annual(ticker, years=years)
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch data for {ticker!r}: {exc}") from exc
    return management_quality_score_from_series(raw, hurdle_rate=hurdle_rate)


management_quality_score.formula = (  # type: ignore[attr-defined]
    "0.35*ROICExcellence + 0.25*MarginStability + 0.25*ShareholderOrientation + 0.15*RevenueExecution"
)
management_quality_score.description = (  # type: ignore[attr-defined]
    "Management quality score 0–100 based on ROIC vs hurdle rate, margin discipline, "
    "share count trend, and revenue growth consistency. Excellent ≥75, Good 50–74, Fair 25–49, Poor <25."
)
