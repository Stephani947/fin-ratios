"""
Earnings Quality Score.

Quantifies how reliable and sustainable a company's reported earnings are.
High-quality earnings are predominantly cash-backed, derived from core
operations, and show no signs of aggressive accounting.

Signals
-------
1. Accruals Ratio          (30%) — (NI − CFO) / Avg Assets; Sloan (1996)
2. Cash Earnings Quality   (25%) — CFO / NI; Richardson et al. (2005)
3. Revenue Recognition     (20%) — Revenue growth vs AR growth spread
4. Gross Margin Stability  (15%) — stable margins signal genuine pricing
5. Asset Efficiency Trend  (10%) — declining asset turnover may signal
                                    capitalised costs or bloat

Score:  0–100
Rating: 'high' (75–100), 'medium' (50–74), 'low' (25–49), 'poor' (0–24)

References
----------
Sloan, R.G. (1996)        — Do Stock Prices Fully Reflect Information in
                            Accruals and Cash Flows? The Accounting Review.
Richardson et al. (2005)  — Accrual Reliability, Earnings Persistence and
                            Stock Prices. Journal of Accounting & Economics.
Novy-Marx, R. (2013)      — The Other Side of Value: The Gross Profitability
                            Premium. Journal of Financial Economics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


# ── Field registry ─────────────────────────────────────────────────────────────

_ZERO_FIELDS = frozenset(
    {
        "revenue",
        "gross_profit",
        "net_income",
        "total_assets",
        "operating_cash_flow",
        "accounts_receivable",
        "interest_expense",
        "income_tax_expense",
        "ebt",
        "ebit",
    }
)

_ALIASES: dict[str, list[str]] = {
    "operating_cash_flow": [
        "cash_from_operations",
        "cfo",
        "net_cash_from_operating_activities",
        "operating_activities",
    ],
    "accounts_receivable": [
        "net_receivables",
        "receivables",
        "trade_receivables",
        "accounts_receivable_net",
    ],
    "gross_profit": ["gross_income"],
    "ebit": ["operating_income"],
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


# ── Helpers ────────────────────────────────────────────────────────────────────


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


# ── Signal 1: Accruals Ratio ───────────────────────────────────────────────────


def _score_accruals(accs: list[_Acc]) -> tuple[float, list[str]]:
    """Lower accruals = more cash-backed earnings = higher quality."""
    ratios: list[float] = []
    for i, d in enumerate(accs):
        ni = d.net_income
        cfo = d.operating_cash_flow
        if ni == 0 and cfo == 0:
            continue
        avg_assets = (d.total_assets + accs[i - 1].total_assets) / 2.0 if i > 0 else d.total_assets
        if avg_assets <= 0:
            continue
        ratios.append((ni - cfo) / avg_assets)

    if not ratios:
        return 0.40, ["Accruals ratio: operating cash flow not available (neutral score)"]

    mean_accrual = _mean(ratios)
    # ≤ -0.05 → 1.0 (very cash-rich),  +0.10 → 0.0 (heavy accruals)
    level = _clamp(1.0 - (mean_accrual + 0.05) / 0.15, 0.0, 1.0)
    stability = max(0.0, 1.0 - _cv(ratios) * 1.0)
    score = _clamp(0.70 * level + 0.30 * stability, 0.0, 1.0)

    quality = (
        "cash-backed"
        if mean_accrual < 0.0
        else "modest accruals"
        if mean_accrual < 0.05
        else "high accruals"
    )
    return score, [
        f"Accruals ratio: mean {mean_accrual * 100:+.1f}% of assets  ({quality})",
        f"{'Earnings predominantly backed by cash flows' if mean_accrual < 0.02 else 'Elevated accruals — verify cash conversion'}",
    ]


# ── Signal 2: Cash Earnings Quality ───────────────────────────────────────────


def _score_cash_earnings(accs: list[_Acc]) -> tuple[float, list[str]]:
    """CFO/NI ratio — should consistently exceed 1.0."""
    ratios: list[float] = []
    for d in accs:
        ni = d.net_income
        cfo = d.operating_cash_flow
        if ni <= 0 or (ni == 0 and cfo == 0):
            continue
        if ni > 0:
            ratios.append(cfo / ni)

    if not ratios:
        return 0.40, ["Cash earnings quality: insufficient CFO/NI data (neutral score)"]

    mean_ratio = _mean(ratios)
    # 0.5× → 0.0,  1.5× → 1.0
    level = _clamp((mean_ratio - 0.5) / 1.0, 0.0, 1.0)
    stability = max(0.0, 1.0 - _cv(ratios) * 0.8)
    score = _clamp(0.65 * level + 0.35 * stability, 0.0, 1.0)

    above = sum(1 for r in ratios if r >= 1.0)
    quality = "excellent" if mean_ratio >= 1.2 else "good" if mean_ratio >= 0.9 else "weak"
    return score, [
        f"CFO/NI conversion: mean {mean_ratio:.2f}×  ({above}/{len(ratios)} years ≥ 1.0)",
        f"Cash earnings quality: {quality}",
    ]


# ── Signal 3: Revenue Recognition Quality ─────────────────────────────────────


def _score_revenue_recognition(accs: list[_Acc]) -> tuple[float, list[str]]:
    """Revenue growth should not consistently lag receivables growth."""
    spreads: list[float] = []
    for i in range(1, len(accs)):
        prev, curr = accs[i - 1], accs[i]
        if prev.revenue <= 0:
            continue
        rev_growth = (curr.revenue - prev.revenue) / prev.revenue
        ar_prev = prev.accounts_receivable
        ar_curr = curr.accounts_receivable
        if ar_prev > 0 and ar_curr > 0:
            ar_growth = (ar_curr - ar_prev) / ar_prev
            spreads.append(rev_growth - ar_growth)

    if not spreads:
        return 0.45, ["Revenue recognition: accounts receivable data unavailable (neutral score)"]

    mean_spread = _mean(spreads)
    # ≤ -0.15 → 0.0,  ≥ +0.10 → 1.0
    level = _clamp((mean_spread + 0.15) / 0.25, 0.0, 1.0)
    consistency = max(0.0, 1.0 - _cv(spreads) * 0.5)
    score = _clamp(0.65 * level + 0.35 * consistency, 0.0, 1.0)

    pos = sum(1 for s in spreads if s >= 0)
    quality = (
        "conservative" if mean_spread > 0.05 else "neutral" if mean_spread > -0.05 else "aggressive"
    )
    return score, [
        f"Revenue recognition: revenue-AR spread {mean_spread * 100:+.1f}%/yr  ({quality})",
        f"Revenue outpaced receivables in {pos}/{len(spreads)} periods",
    ]


# ── Signal 4: Gross Margin Stability ──────────────────────────────────────────


def _score_gross_margin_stability(accs: list[_Acc]) -> tuple[float, list[str]]:
    """Stable gross margins indicate genuine pricing, not accounting smoothing."""
    gm_series = [d.gross_profit / d.revenue for d in accs if d.revenue > 0 and d.gross_profit > 0]
    if len(gm_series) < 2:
        return 0.45, ["Gross margin stability: insufficient data (neutral score)"]

    mean_gm = _mean(gm_series)
    cv = _cv(gm_series)
    slope = _ols_slope(gm_series)
    stability = _clamp(1.0 - cv * 3.0, 0.0, 1.0)
    trend_adj = 0.08 if slope > 0.005 else (-0.08 if slope < -0.005 else 0.0)
    score = _clamp(stability + trend_adj, 0.0, 1.0)

    trend_lbl = "improving" if slope > 0.005 else ("eroding" if slope < -0.005 else "stable")
    quality = "high" if cv < 0.05 else "moderate" if cv < 0.15 else "low"
    return score, [
        f"Gross margin: mean {mean_gm * 100:.1f}%  stability {quality} (CV {cv:.3f})",
        f"Gross margin trend: {trend_lbl}",
    ]


# ── Signal 5: Asset Efficiency Trend ──────────────────────────────────────────


def _score_asset_efficiency(accs: list[_Acc]) -> tuple[float, list[str]]:
    """Declining asset turnover may signal capitalised expenses or bloat."""
    turnover = [d.revenue / d.total_assets for d in accs if d.total_assets > 0 and d.revenue > 0]
    if len(turnover) < 2:
        return 0.45, ["Asset efficiency: insufficient data (neutral score)"]

    slope = _ols_slope(turnover)
    mean_to = _mean(turnover)
    trend_score = _clamp(0.5 + slope * 5.0, 0.0, 1.0)
    level = _clamp((mean_to - 0.2) / 1.5, 0.0, 1.0)
    score = _clamp(0.50 * trend_score + 0.50 * level, 0.0, 1.0)

    direction = "improving" if slope > 0.02 else ("declining" if slope < -0.02 else "stable")
    return score, [
        f"Asset turnover: mean {mean_to:.2f}×  trend {direction}  (slope {slope:+.3f}/yr)",
    ]


# ── Result types ──────────────────────────────────────────────────────────────


@dataclass
class EarningsQualityComponents:
    accruals_ratio: float  # 0–1
    cash_earnings: float  # 0–1
    revenue_recognition: float  # 0–1
    gross_margin_stability: float  # 0–1
    asset_efficiency: float  # 0–1


@dataclass
class EarningsQualityScore:
    """Result of the Earnings Quality Score computation."""

    score: int  # 0–100
    rating: str  # 'high' | 'medium' | 'low' | 'poor'
    components: EarningsQualityComponents
    years_analyzed: int
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "high": "Earnings are predominantly cash-backed, consistently reported, "
            "and show no signs of manipulation.",
            "medium": "Earnings quality is adequate with some variability "
            "that warrants monitoring.",
            "low": "Elevated accruals or inconsistent cash conversion suggest "
            "earnings may not be fully reliable.",
            "poor": "Significant earnings quality concerns — high accruals, weak "
            "cash conversion, or aggressive revenue recognition.",
        }
        return (
            f"Earnings Quality Score: {self.score}/100 [{self.rating.upper()}]. "
            f"{descs.get(self.rating, '')}"
        )

    def table(self) -> str:
        w = 50
        sep = "─" * w
        return "\n".join(
            [
                f"Earnings Quality Score: {self.score}/100  [{self.rating.upper()}]",
                sep,
                f"{'Component':<32} {'Score':>7}  {'Weight':>6}",
                sep,
                f"{'Accruals Ratio':<32} {self.components.accruals_ratio * 100:>6.0f}%   {'30%':>6}",
                f"{'Cash Earnings Quality':<32} {self.components.cash_earnings * 100:>6.0f}%   {'25%':>6}",
                f"{'Revenue Recognition':<32} {self.components.revenue_recognition * 100:>6.0f}%   {'20%':>6}",
                f"{'Gross Margin Stability':<32} {self.components.gross_margin_stability * 100:>6.0f}%   {'15%':>6}",
                f"{'Asset Efficiency Trend':<32} {self.components.asset_efficiency * 100:>6.0f}%   {'10%':>6}",
                sep,
                f"{'Years of data analyzed':<32} {self.years_analyzed:>7}",
            ]
        )

    def _repr_html_(self) -> str:
        colours = {
            "high": "#1a7f37",
            "medium": "#0969da",
            "low": "#9a6700",
            "poor": "#cf222e",
        }
        c = colours.get(self.rating, "#57606a")
        rows = [
            ("Accruals Ratio", self.components.accruals_ratio, "30%"),
            ("Cash Earnings Quality", self.components.cash_earnings, "25%"),
            ("Revenue Recognition", self.components.revenue_recognition, "20%"),
            ("Gross Margin Stability", self.components.gross_margin_stability, "15%"),
            ("Asset Efficiency Trend", self.components.asset_efficiency, "10%"),
        ]
        row_html = "".join(
            f"<tr><td>{n}</td><td style='text-align:right'>{v * 100:.0f}%</td>"
            f"<td style='text-align:right;color:#57606a'>{wt}</td></tr>"
            for n, v, wt in rows
        )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:500px'>"
            f"<div style='font-size:1.1em;font-weight:bold;color:{c}'>"
            f"Earnings Quality: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.rating.upper()}]</span></div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Component</th>"
            f"<th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"{self.years_analyzed} years analyzed</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "rating": self.rating,
            "components": {
                "accruals_ratio": round(self.components.accruals_ratio, 4),
                "cash_earnings": round(self.components.cash_earnings, 4),
                "revenue_recognition": round(self.components.revenue_recognition, 4),
                "gross_margin_stability": round(self.components.gross_margin_stability, 4),
                "asset_efficiency": round(self.components.asset_efficiency, 4),
            },
            "years_analyzed": self.years_analyzed,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


# ── Public API ────────────────────────────────────────────────────────────────


def earnings_quality_score_from_series(
    annual_data: Sequence[Any],
) -> EarningsQualityScore:
    """Compute Earnings Quality Score from a sequence of annual financial records.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects with attributes).
        Must be in chronological order (oldest first). Minimum 2 years required.

    Returns
    -------
    EarningsQualityScore
        Dataclass with `.score` (0–100), `.rating`, `.components`, `.evidence`,
        `.table()`, `._repr_html_()`, and `.to_dict()`.
    """
    if len(annual_data) < 2:
        raise ValueError("earnings_quality_score requires at least 2 years of data.")

    accs = [_Acc(d) for d in annual_data]

    s_acc, ev_acc = _score_accruals(accs)
    s_cfe, ev_cfe = _score_cash_earnings(accs)
    s_rev, ev_rev = _score_revenue_recognition(accs)
    s_gms, ev_gms = _score_gross_margin_stability(accs)
    s_eff, ev_eff = _score_asset_efficiency(accs)

    raw = 0.30 * s_acc + 0.25 * s_cfe + 0.20 * s_rev + 0.15 * s_gms + 0.10 * s_eff
    score = round(_clamp(raw, 0.0, 1.0) * 100)
    rating = (
        "high" if score >= 75 else "medium" if score >= 50 else "low" if score >= 25 else "poor"
    )

    return EarningsQualityScore(
        score=score,
        rating=rating,
        components=EarningsQualityComponents(
            accruals_ratio=round(s_acc, 4),
            cash_earnings=round(s_cfe, 4),
            revenue_recognition=round(s_rev, 4),
            gross_margin_stability=round(s_gms, 4),
            asset_efficiency=round(s_eff, 4),
        ),
        years_analyzed=len(accs),
        evidence=ev_acc + ev_cfe + ev_rev + ev_gms + ev_eff,
    )


def earnings_quality_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
) -> EarningsQualityScore:
    """Fetch data and compute Earnings Quality Score for a ticker.

    Parameters
    ----------
    ticker : str   Stock ticker (e.g. 'AAPL')
    years  : int   Number of historical years (default 10)
    source : str   'yahoo' (default) or 'edgar'
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
    return earnings_quality_score_from_series(raw)
