"""
Quantitative Economic Moat Score.

Scores a company's competitive moat from 0–100 using five financial signals
derived entirely from multi-year financial statements — no analyst opinions,
no qualitative inputs, fully reproducible.

Signals
-------
1. ROIC Persistence     — fraction of years ROIC > WACC, penalised for volatility
2. Pricing Power        — gross margin level × stability (low CV = pricing control)
3. Reinvestment Quality — incremental return on invested capital (ΔEBIT / net reinvestment)
4. Operating Leverage   — degree of operating leverage (fixed-cost structure proxy)
5. CAP Estimate         — statistical projection of competitive advantage period

Weights:  30 / 25 / 20 / 15 / 10

Width Classification
--------------------
  wide    70–100   Durable multi-decade advantage
  narrow  40–69    Real but limited or potentially fading advantage
  none    0–39     No detectable financial signature of a durable moat

Minimum data: 2 years (3+ recommended, 5–10 for robust CAP estimate).

References
----------
Mauboussin & Johnson (1997) — Competitive Advantage Period, CSFB
Greenwald & Kahn (2001)     — Competition Demystified, Portfolio/Penguin
Koller, Goedhart & Wessels (2020) — Valuation (7th ed.), McKinsey & Company
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from .._utils import safe_divide


# ── Data accessor ─────────────────────────────────────────────────────────────

_ZERO_FIELDS = frozenset({
    "revenue", "gross_profit", "ebit", "net_income", "total_assets",
    "total_equity", "total_debt", "cash", "capex", "depreciation",
    "operating_cash_flow", "interest_expense", "income_tax_expense",
    "current_assets", "current_liabilities", "ebt",
})

# Fallback aliases: if the primary key is missing, try these in order
_ALIASES: dict[str, list[str]] = {
    "ebit":         ["operating_income"],
    "total_debt":   ["long_term_debt"],
    "depreciation": ["depreciation_amortization"],
    "ebt":          [],  # computed on the fly from ebit - interest_expense
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

        # Try aliases
        for alias in _ALIASES.get(name, []):
            val = self._raw(alias)
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                return float(val)

        # Computed fallbacks
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
    """Coefficient of variation. Returns 1.0 if mean is near zero."""
    m = _mean(xs)
    return _std(xs) / abs(m) if abs(m) > 1e-9 else 1.0


def _ols_slope(ys: list[float]) -> float:
    """OLS slope of y=ys over x=0,1,...,n-1."""
    n = len(ys)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2.0
    y_mean = _mean(ys)
    ss_xx = sum((i - x_mean) ** 2 for i in range(n))
    ss_xy = sum((i - x_mean) * (ys[i] - y_mean) for i in range(n))
    return ss_xy / ss_xx if ss_xx else 0.0


# ── Per-year ROIC ─────────────────────────────────────────────────────────────

def _year_roic(d: _Acc) -> Optional[float]:
    ebit = d.ebit
    ic = d.total_equity + d.total_debt - d.cash
    if ic <= 0 or ebit <= 0:
        return None
    ebt = d.ebt
    tax = d.income_tax_expense
    if ebt > 0 and tax > 0:
        tax_rate = min(max(tax / ebt, 0.0), 0.50)
    else:
        tax_rate = 0.21
    nopat = ebit * (1.0 - tax_rate)
    return nopat / ic


# ── WACC estimation ───────────────────────────────────────────────────────────

def _estimate_wacc(accs: list[_Acc], provided: Optional[float]) -> float:
    if provided is not None:
        return provided

    d = accs[-1]  # most recent year
    equity = d.total_equity
    debt = d.total_debt
    total_cap = equity + debt
    if total_cap <= 0:
        return 0.09

    we = equity / total_cap
    wd = debt / total_cap

    # Cost of equity via CAPM (default beta=1, risk-free=4.5%, ERP=5.5%)
    cost_equity = 0.045 + 1.0 * 0.055  # 10.0%

    # Cost of debt: interest / debt, after-tax
    interest = d.interest_expense
    pre_cost_debt = (interest / debt) if (interest > 0 and debt > 0) else 0.05
    pre_cost_debt = min(pre_cost_debt, 0.15)

    ebt = d.ebt
    tax = d.income_tax_expense
    tax_rate = min(max(safe_divide(tax, ebt) or 0.21, 0.0), 0.40) if ebt > 0 else 0.21
    cost_debt = pre_cost_debt * (1.0 - tax_rate)

    wacc = we * cost_equity + wd * cost_debt
    return max(min(wacc, 0.20), 0.06)  # clamp to [6%, 20%]


# ── Five signal scorers ───────────────────────────────────────────────────────

def _score_roic_persistence(
    roic_series: list[float], wacc: float
) -> tuple[float, list[str]]:
    if not roic_series:
        return 0.0, ["Insufficient data to compute ROIC series"]

    above = sum(1 for r in roic_series if r > wacc)
    pct_above = above / len(roic_series)
    cv = _cv(roic_series)
    mean_roic = _mean(roic_series)
    spread = mean_roic - wacc

    # High fraction above WACC, penalised for volatility
    stability = max(0.0, 1.0 - cv * 0.40)
    score = pct_above * stability

    ev = [
        f"ROIC exceeded WACC in {above}/{len(roic_series)} years ({pct_above:.0%})",
        f"Mean ROIC {mean_roic:.1%}  vs  WACC {wacc:.1%}  (spread {spread:+.1%})",
        f"ROIC volatility (CV): {cv:.2f} — "
        f"{'highly stable' if cv < 0.15 else 'stable' if cv < 0.30 else 'volatile'}",
    ]
    return min(max(score, 0.0), 1.0), ev


def _score_pricing_power(gm_series: list[float]) -> tuple[float, list[str]]:
    if not gm_series:
        return 0.50, ["Gross margin unavailable — pricing power assumed neutral"]

    mean_gm = _mean(gm_series)
    cv = _cv(gm_series)
    slope = _ols_slope(gm_series)

    # Level: 60%+ → 1.0, 20% → 0.0 (linear interpolation)
    level = min(max((mean_gm - 0.20) / 0.40, 0.0), 1.0)
    # Stability: lower CV = better pricing control
    stability = max(0.0, 1.0 - cv * 2.5)
    # Small trend adjustment (±10% max)
    trend_adj = max(min(slope * 10.0, 0.10), -0.10)

    score = 0.60 * level + 0.40 * stability + trend_adj
    trend_lbl = (
        "improving" if slope > 0.005
        else "declining" if slope < -0.005
        else "stable"
    )
    ev = [
        f"Mean gross margin {mean_gm:.1%} over {len(gm_series)} years",
        f"Gross margin CV {cv:.3f} — "
        f"{'excellent stability' if cv < 0.05 else 'moderate' if cv < 0.15 else 'high variability'}",
        f"Gross margin trend: {trend_lbl}",
    ]
    return min(max(score, 0.0), 1.0), ev


def _score_reinvestment_quality(accs: list[_Acc]) -> tuple[float, list[str]]:
    if len(accs) < 2:
        return 0.50, ["Insufficient data for reinvestment quality — assumed neutral"]

    roiic_vals: list[float] = []
    negative_count = 0
    for i in range(1, len(accs)):
        prev, curr = accs[i - 1], accs[i]
        delta_ebit = curr.ebit - prev.ebit

        net_reinvest = (
            (curr.capex - curr.depreciation)
            + (curr.current_assets - curr.current_liabilities)
            - (prev.current_assets - prev.current_liabilities)
        )
        if net_reinvest > 1e6:
            roiic = delta_ebit / net_reinvest
            roiic_vals.append(max(min(roiic, 5.0), -1.0))
        else:
            negative_count += 1

    total_periods = len(accs) - 1
    # Capital-light if: no positive reinvestment periods, OR majority are negative
    capital_light = (not roiic_vals) or (negative_count / total_periods > 0.50)

    if capital_light:
        ebit_growth = [
            accs[i].ebit / accs[i - 1].ebit - 1.0
            for i in range(1, len(accs))
            if accs[i - 1].ebit > 0
        ]
        if ebit_growth and _mean(ebit_growth) > 0.05:
            return 0.82, [
                "Capital-light model: EBIT growing with minimal net reinvestment",
                "Low reinvestment requirement is a strong moat signal",
            ]
        return 0.50, ["Reinvestment quality indeterminate (limited reinvestment data)"]

    mean_roiic = _mean(roiic_vals)
    # Normalize: 0% ROIIC → 0.30, 50% → 0.65, 100%+ → 1.0
    score = min(max(0.30 + mean_roiic * 0.70, 0.0), 1.0)
    ev = [
        f"Mean incremental ROIC (ROIIC): {mean_roiic:.1%}",
        f"Based on {len(roiic_vals)} reinvestment period(s)",
        f"{'Excellent capital reinvestment efficiency' if mean_roiic > 0.50 else 'Adequate reinvestment returns' if mean_roiic > 0.15 else 'Low incremental returns on reinvestment'}",
    ]
    return score, ev


def _score_operating_leverage(accs: list[_Acc]) -> tuple[float, list[str]]:
    if len(accs) < 2:
        return 0.50, ["Insufficient data for operating leverage"]

    dol_vals: list[float] = []
    for i in range(1, len(accs)):
        prev, curr = accs[i - 1], accs[i]
        if prev.revenue <= 0 or abs(prev.ebit) < 1e5:
            continue
        pct_rev = (curr.revenue - prev.revenue) / prev.revenue
        pct_ebit = (curr.ebit - prev.ebit) / abs(prev.ebit)
        if abs(pct_rev) > 0.005:
            dol = pct_ebit / pct_rev
            if 0.0 < dol < 25.0:
                dol_vals.append(dol)

    if not dol_vals:
        return 0.40, ["Operating leverage indeterminate (insufficient revenue variance)"]

    mean_dol = _mean(dol_vals)
    cv_dol = _cv(dol_vals)
    level = min(max((mean_dol - 1.0) / 5.0, 0.0), 1.0)
    consistency = max(0.0, 1.0 - cv_dol * 0.50)
    score = 0.65 * level + 0.35 * consistency

    quality = (
        "High fixed-cost structure — strong scale advantages"
        if mean_dol > 3.0
        else "Moderate operating leverage"
        if mean_dol > 1.5
        else "Variable cost structure — limited scale advantage"
    )
    ev = [
        f"Mean degree of operating leverage (DOL): {mean_dol:.2f}×",
        f"DOL consistency: {consistency:.0%}",
        quality,
    ]
    return min(max(score, 0.0), 1.0), ev


def _score_cap(
    roic_series: list[float], wacc: float
) -> tuple[float, float, list[str]]:
    """Returns (cap_score 0–1, cap_years, evidence)."""
    if not roic_series:
        return 0.30, 5.0, ["Insufficient data for CAP estimate"]

    mean_roic = _mean(roic_series)
    spread = mean_roic - wacc

    if spread <= 0:
        return 0.0, 0.0, [
            f"ROIC {mean_roic:.1%} ≤ WACC {wacc:.1%}: no competitive advantage detected"
        ]

    slope = _ols_slope(roic_series)  # change per year

    if slope < -0.005:
        # Declining ROIC — extrapolate to WACC
        cap_years = min(max(spread / abs(slope), 0.0), 30.0)
        direction = "declining"
    elif slope > 0.005:
        # Improving — optimistic estimate
        cap_years = min(spread * 80.0 + 5.0, 30.0)
        direction = "improving"
    else:
        # Stable — use spread / volatility
        cv = _cv(roic_series)
        cap_years = min(max(spread * 60.0 / max(cv, 0.10), 3.0), 25.0)
        direction = "stable"

    cap_score = min(cap_years / 20.0, 1.0)
    ev = [
        f"Estimated competitive advantage period: {cap_years:.1f} years",
        f"ROIC trend: {direction} (slope {slope:+.3f}/yr)",
        f"ROIC spread above WACC: {spread:+.1%}",
    ]
    return cap_score, cap_years, ev


# ── Output types ──────────────────────────────────────────────────────────────

@dataclass
class MoatComponents:
    roic_persistence: float      # 0–1
    pricing_power: float         # 0–1
    reinvestment_quality: float  # 0–1
    operating_leverage: float    # 0–1
    cap_score: float             # 0–1 (normalised CAP)


@dataclass
class MoatScore:
    """
    Quantitative economic moat score.

    Attributes
    ----------
    score               : int    0–100 overall score
    width               : str    'wide' | 'narrow' | 'none'
    components          : MoatComponents  per-signal scores
    cap_estimate_years  : float  projected years of above-normal returns
    wacc_used           : float  WACC used in the analysis
    years_analyzed      : int    number of annual data points
    evidence            : list   human-readable supporting observations
    interpretation      : str    one-line summary
    """

    score: int
    width: str
    components: MoatComponents
    cap_estimate_years: float
    wacc_used: float
    years_analyzed: int
    evidence: list[str]
    interpretation: str

    def table(self) -> str:
        w = 46
        lines = [
            f"Moat Score: {self.score}/100  [{self.width.upper()}]",
            "─" * w,
            f"{'Component':<28}{'Score':>8}  {'Weight':>6}",
            "─" * w,
            f"{'ROIC Persistence':<28}{self.components.roic_persistence:>8.0%}  {'30%':>6}",
            f"{'Pricing Power':<28}{self.components.pricing_power:>8.0%}  {'25%':>6}",
            f"{'Reinvestment Quality':<28}{self.components.reinvestment_quality:>8.0%}  {'20%':>6}",
            f"{'Operating Leverage':<28}{self.components.operating_leverage:>8.0%}  {'15%':>6}",
            f"{'CAP Estimate':<28}{self.cap_estimate_years:>6.1f}y  {'10%':>6}",
            "─" * w,
            f"{'WACC estimate used':<28}{self.wacc_used:>8.1%}",
            f"{'Years of data analyzed':<28}{self.years_analyzed:>8}",
            "",
            self.interpretation,
            "",
            "Evidence:",
        ]
        for e in self.evidence:
            lines.append(f"  • {e}")
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        color = {
            "wide": "#2e7d32", "narrow": "#f57c00", "none": "#c62828"
        }.get(self.width, "#555")
        badge = (
            f'<span style="background:{color};color:#fff;padding:2px 12px;'
            f'border-radius:12px;font-size:12px;font-weight:600">'
            f'{self.width.upper()}</span>'
        )

        def bar(val: float) -> str:
            pct = int(val * 100)
            bg = "#2e7d32" if pct >= 70 else "#f57c00" if pct >= 40 else "#c62828"
            return (
                f'<div style="display:inline-flex;align-items:center;gap:6px">'
                f'<div style="background:#eee;border-radius:4px;height:8px;'
                f'width:100px;overflow:hidden">'
                f'<div style="background:{bg};width:{pct}%;height:100%"></div>'
                f'</div>'
                f'<span style="font-size:11px;color:#555">{pct}%</span>'
                f'</div>'
            )

        rows = [
            ("ROIC Persistence",    self.components.roic_persistence,    "30%"),
            ("Pricing Power",       self.components.pricing_power,       "25%"),
            ("Reinvestment Quality",self.components.reinvestment_quality,"20%"),
            ("Operating Leverage",  self.components.operating_leverage,  "15%"),
            (f"CAP ({self.cap_estimate_years:.1f}y)", self.components.cap_score, "10%"),
        ]
        tr = "".join(
            f'<tr>'
            f'<td style="padding:5px 8px;font-size:13px">{name}</td>'
            f'<td style="padding:5px 8px">{bar(s)}</td>'
            f'<td style="padding:5px 8px;color:#aaa;font-size:11px">{w}</td>'
            f'</tr>'
            for name, s, w in rows
        )
        ev_items = "".join(f"<li>{e}</li>" for e in self.evidence)
        return (
            f'<div style="font-family:sans-serif;border:1px solid #e0e0e0;'
            f'border-radius:10px;padding:18px;max-width:560px">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:flex-start;margin-bottom:14px">'
            f'<div>'
            f'<span style="font-size:36px;font-weight:700">{self.score}</span>'
            f'<span style="font-size:16px;color:#888"> /100</span>'
            f'<div style="font-size:11px;color:#aaa;margin-top:2px">'
            f'{self.years_analyzed} years of data · WACC {self.wacc_used:.1%}</div>'
            f'</div>'
            f'{badge}'
            f'</div>'
            f'<table style="width:100%;border-collapse:collapse">{tr}</table>'
            f'<div style="margin-top:10px;font-size:12px;color:#444;'
            f'border-top:1px solid #f0f0f0;padding-top:8px">'
            f'<em>{self.interpretation}</em>'
            f'</div>'
            f'<div style="margin-top:8px;font-size:11px;color:#777">'
            f'<ul style="margin:4px 0;padding-left:16px">{ev_items}</ul>'
            f'</div>'
            f'</div>'
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "width": self.width,
            "components": {
                "roic_persistence":    round(self.components.roic_persistence, 4),
                "pricing_power":       round(self.components.pricing_power, 4),
                "reinvestment_quality":round(self.components.reinvestment_quality, 4),
                "operating_leverage":  round(self.components.operating_leverage, 4),
                "cap_score":           round(self.components.cap_score, 4),
            },
            "cap_estimate_years": round(self.cap_estimate_years, 1),
            "wacc_used":          round(self.wacc_used, 4),
            "years_analyzed":     self.years_analyzed,
            "evidence":           self.evidence,
            "interpretation":     self.interpretation,
        }


# ── Weights ───────────────────────────────────────────────────────────────────

_W = {
    "roic_persistence":    0.30,
    "pricing_power":       0.25,
    "reinvestment_quality":0.20,
    "operating_leverage":  0.15,
    "cap":                 0.10,
}


# ── Public API ────────────────────────────────────────────────────────────────

def moat_score_from_series(
    annual_data: Sequence[Any],
    wacc: Optional[float] = None,
) -> MoatScore:
    """
    Compute a quantitative economic moat score from a sequence of annual data.

    Parameters
    ----------
    annual_data : sequence of dicts, dataclasses, or attribute objects.
                  Must be ordered chronologically (oldest first).
                  Minimum 2 years; 5–10 years recommended for accuracy.
    wacc        : optional WACC override (e.g. 0.09 for 9%). When omitted,
                  estimated from the most recent year's capital structure.

    Returns
    -------
    MoatScore

    Required fields per year (minimum):
        revenue, gross_profit, ebit, total_equity, total_debt, total_assets

    Recommended additional fields (improve signal accuracy):
        cash, capex, depreciation, current_assets, current_liabilities,
        interest_expense, income_tax_expense

    Example
    -------
    >>> data = [
    ...     {'year': 2020, 'revenue': 274e9, 'gross_profit': 105e9, 'ebit': 66e9,
    ...      'total_equity': 65e9, 'total_debt': 112e9, 'total_assets': 323e9,
    ...      'cash': 38e9, 'capex': 7e9, 'depreciation': 11e9},
    ...     {'year': 2021, 'revenue': 365e9, 'gross_profit': 153e9, 'ebit': 109e9,
    ...      'total_equity': 63e9, 'total_debt': 122e9, 'total_assets': 351e9,
    ...      'cash': 62e9, 'capex': 11e9, 'depreciation': 11e9},
    ...     # ... more years
    ... ]
    >>> result = moat_score_from_series(data)
    >>> print(result.score, result.width)
    82 wide
    """
    if len(annual_data) < 2:
        raise ValueError(
            "moat_score_from_series requires at least 2 years of data (3–10 recommended)."
        )

    accs = [_Acc(d) for d in annual_data]
    est_wacc = _estimate_wacc(accs, wacc)

    # Build time series
    roic_series = [r for a in accs if (r := _year_roic(a)) is not None]
    gm_series = [
        safe_divide(a.gross_profit, a.revenue) or 0.0
        for a in accs
        if a.revenue > 0
    ]

    # Score each signal
    s_rp, ev_rp = _score_roic_persistence(roic_series, est_wacc)
    s_pp, ev_pp = _score_pricing_power(gm_series)
    s_rq, ev_rq = _score_reinvestment_quality(accs)
    s_ol, ev_ol = _score_operating_leverage(accs)
    s_cp, cap_years, ev_cp = _score_cap(roic_series, est_wacc)

    raw = (
        _W["roic_persistence"]     * s_rp
        + _W["pricing_power"]      * s_pp
        + _W["reinvestment_quality"] * s_rq
        + _W["operating_leverage"] * s_ol
        + _W["cap"]                * s_cp
    )
    score = int(round(min(max(raw * 100, 0), 100)))
    width = "wide" if score >= 70 else "narrow" if score >= 40 else "none"

    _desc = {
        "wide":   "Durable competitive advantage likely to persist for 10+ years",
        "narrow": "Real but limited or potentially fading competitive advantage",
        "none":   "No detectable financial signature of a durable economic moat",
    }
    interpretation = f"Score {score}/100: {_desc[width]}"

    return MoatScore(
        score=score,
        width=width,
        components=MoatComponents(
            roic_persistence=round(s_rp, 4),
            pricing_power=round(s_pp, 4),
            reinvestment_quality=round(s_rq, 4),
            operating_leverage=round(s_ol, 4),
            cap_score=round(s_cp, 4),
        ),
        cap_estimate_years=round(cap_years, 1),
        wacc_used=round(est_wacc, 4),
        years_analyzed=len(accs),
        evidence=ev_rp + ev_pp + ev_rq + ev_ol + ev_cp,
        interpretation=interpretation,
    )


def moat_score(
    ticker: str,
    years: int = 10,
    wacc: Optional[float] = None,
    source: str = "yahoo",
) -> MoatScore:
    """
    Fetch multi-year financial data and compute a quantitative moat score.

    Parameters
    ----------
    ticker : str   Stock ticker (e.g. 'AAPL')
    years  : int   Number of historical years (default 10; min 3)
    wacc   : float WACC override (e.g. 0.09). If None, estimated from data.
    source : str   'yahoo' (default) or 'edgar'

    Returns
    -------
    MoatScore

    Example
    -------
    >>> result = moat_score('AAPL', years=10)
    >>> print(result.score)   # 82
    >>> print(result.width)   # 'wide'
    >>> print(result.table())
    """
    if source == "edgar":
        from ..fetchers.edgar import fetch_edgar
        filings = fetch_edgar(ticker, num_years=years)
        if len(filings) < 2:
            raise ValueError(
                f"Insufficient EDGAR filings for {ticker} "
                f"(got {len(filings)}, need 2+). "
                "Try source='yahoo' or provide data directly via moat_score_from_series()."
            )
        # fetch_edgar returns newest-first; reverse to oldest-first
        return moat_score_from_series(list(reversed(filings)), wacc=wacc)

    # source == 'yahoo' (default)
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError(
            "yfinance is required for source='yahoo'.\n"
            "Install with: pip install yfinance  (or: pip install 'fin-ratios[fetchers]')"
        ) from exc

    t = yf.Ticker(ticker)
    income_stmt = t.income_stmt
    balance     = t.balance_sheet
    cashflow    = t.cashflow

    def _get(df: Any, *keys: str, col: Any) -> float:
        for k in keys:
            try:
                v = df.loc[k, col]
                if v is not None and not (isinstance(v, float) and math.isnan(v)):
                    return float(v)
            except (KeyError, TypeError):
                pass
        return 0.0

    cols = income_stmt.columns.tolist()[:years]   # newest first
    annual = []
    for col in reversed(cols):  # process oldest-first
        annual.append({
            "revenue":     _get(income_stmt, "Total Revenue", col=col),
            "gross_profit":_get(income_stmt, "Gross Profit", col=col),
            "ebit":        _get(income_stmt, "EBIT", "Operating Income", col=col),
            "net_income":  _get(income_stmt, "Net Income", col=col),
            "ebt":         _get(income_stmt, "Pretax Income", col=col),
            "income_tax_expense": _get(income_stmt, "Tax Provision", col=col),
            "interest_expense":   _get(income_stmt, "Interest Expense", col=col),
            "total_assets":       _get(balance, "Total Assets", col=col),
            "total_equity":       _get(
                balance,
                "Stockholders Equity",
                "Total Equity Gross Minority Interest",
                col=col,
            ),
            "total_debt":  _get(balance, "Total Debt", "Long Term Debt", col=col),
            "cash":        _get(
                balance,
                "Cash And Cash Equivalents",
                "Cash Cash Equivalents And Short Term Investments",
                col=col,
            ),
            "current_assets":      _get(balance, "Current Assets", col=col),
            "current_liabilities": _get(balance, "Current Liabilities", col=col),
            "capex":       abs(_get(cashflow, "Capital Expenditure", col=col)),
            "depreciation":abs(_get(
                cashflow,
                "Depreciation And Amortization",
                "Depreciation",
                col=col,
            )),
        })

    if len(annual) < 2:
        raise ValueError(
            f"Insufficient historical data from Yahoo Finance for {ticker}."
        )

    return moat_score_from_series(annual, wacc=wacc)


moat_score.formula = (  # type: ignore[attr-defined]
    "Weighted(ROIC Persistence, Pricing Power, Reinvestment Quality, "
    "Operating Leverage, CAP Estimate)"
)
moat_score.description = (  # type: ignore[attr-defined]
    "Quantitative economic moat score 0–100 derived from multi-year financial "
    "statements. Wide ≥70, Narrow 40–69, None <40."
)
