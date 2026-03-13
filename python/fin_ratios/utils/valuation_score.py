"""
Valuation Attractiveness Score.

Measures how attractively priced a company is relative to its fundamentals.
Aggregates five valuation signals — earnings yield, FCF yield, EV/EBITDA,
price-to-book, and DCF upside — into a single score.

Score:  0–100 (higher = more attractive / cheaper)
Rating: 'attractive' (≥65), 'fair' (40–64), 'expensive' (20–39), 'overvalued' (<20)

Signals with weights
--------------------
1. Earnings Yield Spread   (25%) — EY vs risk-free rate
2. FCF Yield               (25%) — free cash flow / market cap
3. EV/EBITDA               (20%) — enterprise value multiple
4. P/B Ratio               (15%) — price-to-book
5. DCF Upside              (15%) — margin of safety to intrinsic value

References
----------
Damodaran, A. (2012)   — Investment Valuation (3rd ed.), Wiley Finance
Greenblatt, J. (2010)  — The Little Book That Still Beats the Market
Shiller, R.J. (2000)   — Irrational Exuberance, Princeton University Press
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Helpers ────────────────────────────────────────────────────────────────────


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _lerp(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    """Linearly interpolate y from x, clamped to [y0, y1] (or [y1, y0])."""
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    t = max(0.0, min(1.0, t))
    return y0 + t * (y1 - y0)


# ── Signal scorers ─────────────────────────────────────────────────────────────


def _score_earnings_yield(
    pe_ratio: Optional[float],
    earnings_yield_pct: Optional[float],
    risk_free_rate: float,
) -> tuple[float, list[str]]:
    if earnings_yield_pct is not None:
        ey = earnings_yield_pct / 100.0
    elif pe_ratio is not None and pe_ratio > 0:
        ey = 1.0 / pe_ratio
    else:
        return 0.50, ["Earnings yield: no P/E or earnings yield provided (neutral score)"]

    excess = ey - risk_free_rate
    score = _lerp(excess, -0.04, 0.04, 0.0, 1.0)
    quality = "attractive" if excess > 0.02 else "fair" if excess > -0.01 else "expensive"
    return score, [
        f"Earnings yield: {ey * 100:.2f}%  vs  risk-free {risk_free_rate * 100:.2f}%  "
        f"(excess {excess * 100:+.2f}%)  [{quality}]",
    ]


def _score_fcf_yield(
    p_fcf: Optional[float],
    fcf_yield_pct: Optional[float],
) -> tuple[float, list[str]]:
    if fcf_yield_pct is not None:
        fy = fcf_yield_pct / 100.0
    elif p_fcf is not None and p_fcf > 0:
        fy = 1.0 / p_fcf
    else:
        return 0.50, ["FCF yield: no P/FCF or FCF yield provided (neutral score)"]

    if fy < 0.02:
        score = _lerp(fy, -0.02, 0.02, 0.0, 0.3)
    elif fy < 0.05:
        score = _lerp(fy, 0.02, 0.05, 0.3, 0.7)
    else:
        score = _lerp(fy, 0.05, 0.08, 0.7, 1.0)

    quality = "high" if fy >= 0.06 else "moderate" if fy >= 0.03 else "low"
    return score, [
        f"FCF yield: {fy * 100:.2f}%  [{quality}]",
    ]


def _score_ev_ebitda(ev_ebitda_ratio: Optional[float]) -> tuple[float, list[str]]:
    if ev_ebitda_ratio is None:
        return 0.50, ["EV/EBITDA: not provided (neutral score)"]

    ev = ev_ebitda_ratio
    if ev <= 0:
        return 0.20, [f"EV/EBITDA: {ev:.1f}x  (negative/zero — distressed or heavily indebted)"]

    if ev <= 12:
        score = _lerp(ev, 5.0, 12.0, 1.0, 0.6)
    elif ev <= 20:
        score = _lerp(ev, 12.0, 20.0, 0.6, 0.2)
    else:
        score = _lerp(ev, 20.0, 30.0, 0.2, 0.05)

    quality = "cheap" if ev < 10 else "reasonable" if ev < 16 else "elevated"
    return score, [
        f"EV/EBITDA: {ev:.1f}x  [{quality}]",
    ]


def _score_pb_ratio(pb_ratio: Optional[float]) -> tuple[float, list[str]]:
    if pb_ratio is None:
        return 0.50, ["P/B ratio: not provided (neutral score)"]

    pb = pb_ratio
    if pb <= 0:
        return 0.15, [f"P/B ratio: {pb:.2f}x  (negative book value — high leverage risk)"]

    if pb < 2.0:
        score = _lerp(pb, 0.5, 2.0, 1.0, 0.65)
    elif pb < 4.0:
        score = _lerp(pb, 2.0, 4.0, 0.65, 0.3)
    else:
        score = _lerp(pb, 4.0, 8.0, 0.3, 0.05)

    quality = (
        "deep value"
        if pb < 1.0
        else "value"
        if pb < 2.0
        else "growth premium"
        if pb < 5.0
        else "expensive"
    )
    return score, [
        f"P/B ratio: {pb:.2f}x  [{quality}]",
    ]


def _score_dcf_upside(dcf_upside_pct: Optional[float]) -> tuple[float, list[str]]:
    if dcf_upside_pct is None:
        return 0.50, ["DCF upside: not provided (neutral score)"]

    u = dcf_upside_pct / 100.0
    if u < 0.0:
        score = _lerp(u, -0.5, 0.0, 0.0, 0.3)
    elif u < 0.3:
        score = _lerp(u, 0.0, 0.3, 0.3, 0.75)
    else:
        score = _lerp(u, 0.3, 0.6, 0.75, 1.0)

    quality = (
        "large margin of safety"
        if u >= 0.40
        else "moderate upside"
        if u >= 0.15
        else "fairly valued"
        if u >= -0.05
        else "overvalued vs DCF"
    )
    return score, [
        f"DCF upside: {u * 100:+.1f}%  [{quality}]",
    ]


# ── Result types ───────────────────────────────────────────────────────────────


@dataclass
class ValuationComponents:
    earnings_yield: float  # 0–1
    fcf_yield: float  # 0–1
    ev_ebitda: float  # 0–1
    pb_ratio: float  # 0–1
    dcf_upside: float  # 0–1


@dataclass
class ValuationScore:
    """Result of the Valuation Attractiveness Score computation."""

    score: int  # 0–100
    rating: str  # 'attractive' | 'fair' | 'expensive' | 'overvalued'
    components: ValuationComponents
    risk_free_rate: float
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "attractive": "Valuation is attractive across multiple metrics — multiple signals "
            "suggest a meaningful margin of safety relative to intrinsic value.",
            "fair": "Valuation is roughly in line with fundamentals — neither a bargain "
            "nor significantly overpriced.",
            "expensive": "Valuation is above fair value on most measures — limited upside "
            "and elevated downside risk.",
            "overvalued": "Significantly overvalued by multiple metrics — risk/reward is "
            "unfavourable at current prices.",
        }
        return (
            f"Valuation Attractiveness Score: {self.score}/100 [{self.rating.upper()}]. "
            f"{descs.get(self.rating, '')}"
        )

    def table(self) -> str:
        w = 52
        sep = "─" * w
        return "\n".join(
            [
                f"Valuation Attractiveness Score: {self.score}/100  [{self.rating.upper()}]",
                sep,
                f"{'Component':<32} {'Score':>7}  {'Weight':>6}",
                sep,
                f"{'Earnings Yield Spread':<32} {self.components.earnings_yield * 100:>6.0f}%   {'25%':>6}",
                f"{'FCF Yield':<32} {self.components.fcf_yield * 100:>6.0f}%   {'25%':>6}",
                f"{'EV/EBITDA':<32} {self.components.ev_ebitda * 100:>6.0f}%   {'20%':>6}",
                f"{'P/B Ratio':<32} {self.components.pb_ratio * 100:>6.0f}%   {'15%':>6}",
                f"{'DCF Upside':<32} {self.components.dcf_upside * 100:>6.0f}%   {'15%':>6}",
                sep,
                f"{'Risk-free rate used':<32} {self.risk_free_rate * 100:>6.1f}%",
            ]
        )

    def _repr_html_(self) -> str:
        colours = {
            "attractive": "#1a7f37",
            "fair": "#0969da",
            "expensive": "#9a6700",
            "overvalued": "#cf222e",
        }
        c = colours.get(self.rating, "#57606a")
        rows = [
            ("Earnings Yield Spread", self.components.earnings_yield, "25%"),
            ("FCF Yield", self.components.fcf_yield, "25%"),
            ("EV/EBITDA", self.components.ev_ebitda, "20%"),
            ("P/B Ratio", self.components.pb_ratio, "15%"),
            ("DCF Upside", self.components.dcf_upside, "15%"),
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
            f"Valuation Attractiveness: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.rating.upper()}]</span></div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Component</th>"
            f"<th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"Risk-free rate: {self.risk_free_rate * 100:.1f}%</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "rating": self.rating,
            "components": {
                "earnings_yield": round(self.components.earnings_yield, 4),
                "fcf_yield": round(self.components.fcf_yield, 4),
                "ev_ebitda": round(self.components.ev_ebitda, 4),
                "pb_ratio": round(self.components.pb_ratio, 4),
                "dcf_upside": round(self.components.dcf_upside, 4),
            },
            "risk_free_rate": round(self.risk_free_rate, 4),
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


# ── Public API ─────────────────────────────────────────────────────────────────


def valuation_attractiveness_score(
    pe_ratio: Optional[float] = None,
    ev_ebitda: Optional[float] = None,
    p_fcf: Optional[float] = None,
    pb_ratio: Optional[float] = None,
    fcf_yield_pct: Optional[float] = None,
    earnings_yield_pct: Optional[float] = None,
    dcf_upside_pct: Optional[float] = None,
    risk_free_rate: float = 0.045,
) -> ValuationScore:
    """Compute Valuation Attractiveness Score from point-in-time valuation metrics.

    Parameters
    ----------
    pe_ratio : float, optional
        Price-to-earnings ratio (e.g. 20.0).  Used to derive earnings yield
        when ``earnings_yield_pct`` is not provided.
    ev_ebitda : float, optional
        Enterprise value to EBITDA multiple (e.g. 14.0).
    p_fcf : float, optional
        Price-to-free-cash-flow ratio (e.g. 22.0).  Used to derive FCF yield
        when ``fcf_yield_pct`` is not provided.
    pb_ratio : float, optional
        Price-to-book ratio (e.g. 3.5).
    fcf_yield_pct : float, optional
        Free cash flow yield as a percentage (e.g. 4.5 for 4.5%).
        Overrides ``p_fcf`` when provided.
    earnings_yield_pct : float, optional
        Earnings yield as a percentage (e.g. 5.0 for 5.0%).
        Overrides ``pe_ratio`` when provided.
    dcf_upside_pct : float, optional
        Percentage upside to DCF intrinsic value (e.g. 25.0 for 25% upside,
        -10.0 for 10% downside).
    risk_free_rate : float
        Current risk-free rate as a decimal (default 0.045 = 4.5%).

    Returns
    -------
    ValuationScore
        Dataclass with ``.score`` (0–100), ``.rating``, ``.components``,
        ``.evidence``, ``.table()``, ``._repr_html_()``, and ``.to_dict()``.

    Notes
    -----
    Missing signals default to a neutral 0.50 component score.  At least two
    signals should be provided for a meaningful result.
    """
    s_ey, ev_ey = _score_earnings_yield(pe_ratio, earnings_yield_pct, risk_free_rate)
    s_fy, ev_fy = _score_fcf_yield(p_fcf, fcf_yield_pct)
    s_ev, ev_ev = _score_ev_ebitda(ev_ebitda)
    s_pb, ev_pb = _score_pb_ratio(pb_ratio)
    s_dc, ev_dc = _score_dcf_upside(dcf_upside_pct)

    raw = 0.25 * s_ey + 0.25 * s_fy + 0.20 * s_ev + 0.15 * s_pb + 0.15 * s_dc
    score = round(_clamp(raw, 0.0, 1.0) * 100)

    rating = (
        "attractive"
        if score >= 65
        else "fair"
        if score >= 40
        else "expensive"
        if score >= 20
        else "overvalued"
    )

    return ValuationScore(
        score=score,
        rating=rating,
        components=ValuationComponents(
            earnings_yield=round(s_ey, 4),
            fcf_yield=round(s_fy, 4),
            ev_ebitda=round(s_ev, 4),
            pb_ratio=round(s_pb, 4),
            dcf_upside=round(s_dc, 4),
        ),
        risk_free_rate=risk_free_rate,
        evidence=ev_ey + ev_fy + ev_ev + ev_pb + ev_dc,
    )


def valuation_score(
    ticker: str,
    source: str = "yahoo",
) -> ValuationScore:
    """Fetch current valuation metrics for a ticker and compute the Valuation Attractiveness Score.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL').
    source : str
        Data source: 'yahoo' (default).  Currently only Yahoo Finance is
        supported for point-in-time valuation metrics.

    Returns
    -------
    ValuationScore

    Raises
    ------
    ValueError
        If no usable valuation data can be retrieved for the ticker.
    RuntimeError
        If the data fetch itself fails.

    Notes
    -----
    For full control over inputs — or to avoid the network dependency — call
    :func:`valuation_attractiveness_score` directly with your own metrics.
    """
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError(
            "yfinance is required for valuation_score().\n"
            "Install with: pip install yfinance  (or: pip install 'financial-ratios[fetchers]')"
        ) from exc

    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch data for {ticker!r}: {exc}") from exc

    def _f(key: str) -> Optional[float]:
        val = info.get(key)
        if val is None:
            return None
        try:
            v = float(val)
            return v if v == v else None  # filter NaN
        except (TypeError, ValueError):
            return None

    pe = _f("trailingPE") or _f("forwardPE")
    pb = _f("priceToBook")
    ev_eb = _f("enterpriseToEbitda")
    fcf_y = _f("freeCashflow")
    mkt_cap = _f("marketCap")

    fcf_yield_pct: Optional[float] = None
    if fcf_y is not None and mkt_cap is not None and mkt_cap > 0:
        fcf_yield_pct = (fcf_y / mkt_cap) * 100.0

    if pe is None and pb is None and ev_eb is None and fcf_yield_pct is None:
        raise ValueError(
            f"No usable valuation data found for {ticker!r}. "
            "Provide metrics directly via valuation_attractiveness_score()."
        )

    return valuation_attractiveness_score(
        pe_ratio=pe,
        ev_ebitda=ev_eb,
        pb_ratio=pb,
        fcf_yield_pct=fcf_yield_pct,
    )


valuation_attractiveness_score.formula = (  # type: ignore[attr-defined]
    "0.25*EarningsYieldSpread + 0.25*FCFYield + 0.20*EV/EBITDA + 0.15*P/B + 0.15*DCFUpside"
)
valuation_attractiveness_score.description = (  # type: ignore[attr-defined]
    "Valuation attractiveness score 0–100. "
    "Attractive ≥65, Fair 40–64, Expensive 20–39, Overvalued <20."
)
