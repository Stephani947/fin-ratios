"""
Investment Score.

Grand synthesis of quality and valuation dimensions into a single investment
conviction score. Combines five sub-scores — moat, capital allocation, earnings
quality, management quality, and (optionally) valuation attractiveness — using
research-backed weights.

Score:  0–100
Grade:  'A+' (≥90), 'A' (80–89), 'B+' (70–79), 'B' (60–69),
        'C' (45–59), 'D' (25–44), 'F' (<25)
Conviction: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'

Weights (with valuation)
------------------------
  Moat Score              : 25%
  Capital Allocation      : 20%
  Earnings Quality        : 20%
  Management Quality      : 15%
  Valuation Attractiveness: 20%

When valuation is omitted, weights are redistributed proportionally across
the four quality dimensions. Dividend safety, if provided, contributes a
capped ±5-point adjustment to the final score.

References
----------
Buffett, W. (1977–2023)         — Berkshire Hathaway Partnership & Annual Letters
Greenblatt, J. (2010)           — The Little Book That Still Beats the Market
Asness, Frazzini & Pedersen (2019) — Quality Minus Junk, Review of Accounting Studies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .moat_score import moat_score_from_series, MoatScore
from .capital_allocation import capital_allocation_score_from_series, CapitalAllocationScore
from .earnings_quality import earnings_quality_score_from_series, EarningsQualityScore
from .management_score import management_quality_score_from_series, ManagementScore
from .valuation_score import valuation_attractiveness_score, ValuationScore
from .dividend_score import dividend_safety_score_from_series, DividendSafetyScore


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ── Result types ───────────────────────────────────────────────────────────────


@dataclass
class InvestmentComponents:
    moat: Optional[int]  # 0–100 or None
    capital_allocation: Optional[int]  # 0–100 or None
    earnings_quality: Optional[int]  # 0–100 or None
    management: Optional[int]  # 0–100 or None
    valuation: Optional[int]  # 0–100 or None
    dividend_safety: Optional[int]  # 0–100 or None


@dataclass
class InvestmentScore:
    """Result of the Investment Score computation."""

    score: int  # 0–100
    grade: str  # 'A+' | 'A' | 'B+' | 'B' | 'C' | 'D' | 'F'
    conviction: str  # 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
    components: InvestmentComponents
    years_analyzed: int
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "A+": "Exceptional investment candidate — highest quality with favourable "
            "valuation. Rare combination warranting strong conviction.",
            "A": "High-quality business, well-priced. Strong long-term compounding "
            "potential across all dimensions.",
            "B+": "Above-average quality with reasonable valuation. Solid candidate "
            "for a long-term portfolio.",
            "B": "Good quality business, fairly valued. Suitable for patient investors.",
            "C": "Mixed profile — quality or valuation concerns limit upside. "
            "Requires close monitoring.",
            "D": "Below-average on quality and/or significantly overvalued. "
            "Risk/reward is unfavourable.",
            "F": "Poor quality and/or grossly overvalued. Significant downside risk.",
        }
        return (
            f"Investment Score: {self.score}/100 [{self.grade}] — {self.conviction.replace('_', ' ').title()}. "
            f"{descs.get(self.grade, '')}"
        )

    def table(self) -> str:
        w = 54
        sep = "─" * w

        def _fmt(v: Optional[int]) -> str:
            return f"{v:>5}" if v is not None else "  N/A"

        rows = [
            ("Moat Score", self.components.moat, "25%"),
            ("Capital Allocation", self.components.capital_allocation, "20%"),
            ("Earnings Quality", self.components.earnings_quality, "20%"),
            ("Management Quality", self.components.management, "15%"),
            ("Valuation Attractiveness", self.components.valuation, "20%"),
        ]
        lines = [
            f"Investment Score: {self.score}/100  [{self.grade}]  ({self.conviction})",
            sep,
            f"{'Component':<34} {'Score':>5}  {'Weight':>6}",
            sep,
        ]
        for name, val, wt in rows:
            lines.append(f"{name:<34} {_fmt(val)}/100  {wt:>6}")
        if self.components.dividend_safety is not None:
            lines.append(
                f"{'Dividend Safety (adjustment)':<34} {_fmt(self.components.dividend_safety)}/100"
            )
        lines += [
            sep,
            f"{'Years of data analyzed':<34} {self.years_analyzed:>7}",
        ]
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        grade_colours = {
            "A+": "#1a7f37",
            "A": "#1a7f37",
            "B+": "#0969da",
            "B": "#0969da",
            "C": "#9a6700",
            "D": "#cf222e",
            "F": "#8b1a1a",
        }
        conviction_colours = {
            "strong_buy": "#1a7f37",
            "buy": "#0969da",
            "hold": "#9a6700",
            "sell": "#cf222e",
            "strong_sell": "#8b1a1a",
        }
        gc = grade_colours.get(self.grade, "#57606a")
        cc = conviction_colours.get(self.conviction, "#57606a")

        def _fmt(v: Optional[int]) -> str:
            return f"{v}" if v is not None else "N/A"

        rows = [
            ("Moat Score", self.components.moat, "25%"),
            ("Capital Allocation", self.components.capital_allocation, "20%"),
            ("Earnings Quality", self.components.earnings_quality, "20%"),
            ("Management Quality", self.components.management, "15%"),
            ("Valuation Attractiveness", self.components.valuation, "20%"),
        ]
        row_html = "".join(
            f"<tr><td>{n}</td>"
            f"<td style='text-align:right'>{_fmt(v)}/100</td>"
            f"<td style='text-align:right;color:#57606a'>{wt}</td></tr>"
            for n, v, wt in rows
        )
        div_row = ""
        if self.components.dividend_safety is not None:
            div_row = (
                f"<tr style='color:#57606a;font-size:0.9em'>"
                f"<td>Dividend Safety (adj.)</td>"
                f"<td style='text-align:right'>{_fmt(self.components.dividend_safety)}/100</td>"
                f"<td></td></tr>"
            )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:520px'>"
            f"<div style='font-size:1.2em;font-weight:bold;color:{gc}'>"
            f"Investment Score: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.grade}]</span></div>"
            f"<div style='margin-top:4px;font-size:0.9em;font-weight:600;color:{cc}'>"
            f"{self.conviction.replace('_', ' ').upper()}</div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Component</th>"
            f"<th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}{div_row}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"{self.years_analyzed} years analyzed</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "grade": self.grade,
            "conviction": self.conviction,
            "components": {
                "moat": self.components.moat,
                "capital_allocation": self.components.capital_allocation,
                "earnings_quality": self.components.earnings_quality,
                "management": self.components.management,
                "valuation": self.components.valuation,
                "dividend_safety": self.components.dividend_safety,
            },
            "years_analyzed": self.years_analyzed,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


# ── Scoring helpers ────────────────────────────────────────────────────────────


def _grade(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 45:
        return "C"
    if score >= 25:
        return "D"
    return "F"


def _conviction(score: int) -> str:
    if score >= 90:
        return "strong_buy"
    if score >= 70:
        return "buy"
    if score >= 45:
        return "hold"
    if score >= 25:
        return "sell"
    return "strong_sell"


def _combine(
    moat_s: int,
    ca_s: int,
    eq_s: int,
    mgmt_s: int,
    val_s: Optional[int],
    div_s: Optional[int],
) -> int:
    """Compute weighted composite score with optional valuation and dividend adjustment."""
    if val_s is not None:
        raw = 0.25 * moat_s + 0.20 * ca_s + 0.20 * eq_s + 0.15 * mgmt_s + 0.20 * val_s
    else:
        # Redistribute valuation weight proportionally across four quality signals
        # Original weights: 25, 20, 20, 15 → sum = 80; scale to 100
        raw = (
            (25 / 80) * 100 * moat_s / 100
            + (20 / 80) * 100 * ca_s / 100
            + (20 / 80) * 100 * eq_s / 100
            + (15 / 80) * 100 * mgmt_s / 100
        )

    score = _clamp(raw, 0.0, 100.0)

    # Dividend safety: small adjustment capped at ±5 points
    if div_s is not None:
        adj = (div_s - 50) / 50.0 * 5.0  # maps 0→-5, 50→0, 100→+5
        score = _clamp(score + adj, 0.0, 100.0)

    return round(score)


# ── Public API ─────────────────────────────────────────────────────────────────


def investment_score_from_scores(
    moat_score: int,
    capital_allocation_score: int,
    earnings_quality_score: int,
    management_score: int,
    valuation_score: Optional[int] = None,
    dividend_safety_score: Optional[int] = None,
) -> InvestmentScore:
    """Compute Investment Score from pre-computed sub-scores.

    Parameters
    ----------
    moat_score : int
        Moat score 0–100.
    capital_allocation_score : int
        Capital allocation score 0–100.
    earnings_quality_score : int
        Earnings quality score 0–100.
    management_score : int
        Management quality score 0–100.
    valuation_score : int, optional
        Valuation attractiveness score 0–100.  If omitted, valuation weight
        is redistributed across quality dimensions.
    dividend_safety_score : int, optional
        Dividend safety score 0–100.  Used as a small ±5-point adjustment.

    Returns
    -------
    InvestmentScore
    """
    score = _combine(
        moat_score,
        capital_allocation_score,
        earnings_quality_score,
        management_score,
        valuation_score,
        dividend_safety_score,
    )
    evidence = [
        f"Moat:               {moat_score}/100",
        f"Capital Allocation: {capital_allocation_score}/100",
        f"Earnings Quality:   {earnings_quality_score}/100",
        f"Management:         {management_score}/100",
    ]
    if valuation_score is not None:
        evidence.append(f"Valuation:          {valuation_score}/100")
    if dividend_safety_score is not None:
        evidence.append(f"Dividend Safety:    {dividend_safety_score}/100  (±5pt adjustment)")

    return InvestmentScore(
        score=score,
        grade=_grade(score),
        conviction=_conviction(score),
        components=InvestmentComponents(
            moat=moat_score,
            capital_allocation=capital_allocation_score,
            earnings_quality=earnings_quality_score,
            management=management_score,
            valuation=valuation_score,
            dividend_safety=dividend_safety_score,
        ),
        years_analyzed=0,
        evidence=evidence,
    )


def investment_score_from_series(
    annual_data: Sequence[Any],
    pe_ratio: Optional[float] = None,
    ev_ebitda: Optional[float] = None,
    p_fcf: Optional[float] = None,
    pb_ratio: Optional[float] = None,
    fcf_yield_pct: Optional[float] = None,
    dcf_upside_pct: Optional[float] = None,
    risk_free_rate: float = 0.045,
    wacc: Optional[float] = None,
) -> InvestmentScore:
    """Compute Investment Score from a sequence of annual financial records.

    Internally computes all five sub-scores (moat, capital allocation, earnings
    quality, management, dividend safety) from the time-series data, plus an
    optional valuation score from the point-in-time valuation parameters.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects with attributes).
        Chronological order (oldest first). Minimum 3 years required.
    pe_ratio : float, optional
        Current P/E ratio for valuation scoring.
    ev_ebitda : float, optional
        Current EV/EBITDA multiple.
    p_fcf : float, optional
        Current price-to-FCF ratio.
    pb_ratio : float, optional
        Current price-to-book ratio.
    fcf_yield_pct : float, optional
        Current FCF yield as a percentage.
    dcf_upside_pct : float, optional
        Percentage upside to DCF intrinsic value.
    risk_free_rate : float
        Current risk-free rate (default 0.045).
    wacc : float, optional
        WACC override for quality sub-score computations.

    Returns
    -------
    InvestmentScore
    """
    if len(annual_data) < 3:
        raise ValueError("investment_score_from_series requires at least 3 years of data.")

    ms: MoatScore = moat_score_from_series(annual_data, wacc=wacc)
    ca: CapitalAllocationScore = capital_allocation_score_from_series(annual_data, wacc=wacc)
    eq: EarningsQualityScore = earnings_quality_score_from_series(annual_data)

    try:
        mgmt: ManagementScore = management_quality_score_from_series(annual_data)
    except ValueError:
        # management requires 3+ years; use a neutral fallback if somehow short
        mgmt_score_val: int = 50
        mgmt_evidence: list[str] = ["Management: insufficient data for full computation"]
        mgmt = None  # type: ignore[assignment]
    else:
        mgmt_score_val = mgmt.score
        mgmt_evidence = [f"Management: {mgmt.score}/100 [{mgmt.rating.upper()}]"]

    div: DividendSafetyScore = dividend_safety_score_from_series(annual_data)

    # Valuation score (optional)
    val_score_obj: Optional[ValuationScore] = None
    val_score_val: Optional[int] = None
    if any(
        v is not None for v in [pe_ratio, ev_ebitda, p_fcf, pb_ratio, fcf_yield_pct, dcf_upside_pct]
    ):
        val_score_obj = valuation_attractiveness_score(
            pe_ratio=pe_ratio,
            ev_ebitda=ev_ebitda,
            p_fcf=p_fcf,
            pb_ratio=pb_ratio,
            fcf_yield_pct=fcf_yield_pct,
            dcf_upside_pct=dcf_upside_pct,
            risk_free_rate=risk_free_rate,
        )
        val_score_val = val_score_obj.score

    score = _combine(
        ms.score,
        ca.score,
        eq.score,
        mgmt_score_val,
        val_score_val,
        div.score if div.is_dividend_payer else None,
    )

    evidence = [
        f"Moat:               {ms.score}/100 [{ms.width.upper()}]",
        f"Capital Allocation: {ca.score}/100 [{ca.rating.upper()}]",
        f"Earnings Quality:   {eq.score}/100 [{eq.rating.upper()}]",
    ] + mgmt_evidence
    if val_score_obj is not None:
        evidence.append(
            f"Valuation:          {val_score_obj.score}/100 [{val_score_obj.rating.upper()}]"
        )
    if div.is_dividend_payer:
        evidence.append(
            f"Dividend Safety:    {div.score}/100 [{div.rating.upper()}]  (±5pt adjustment)"
        )
    else:
        evidence.append("Dividend Safety:    non-payer (no adjustment)")

    return InvestmentScore(
        score=score,
        grade=_grade(score),
        conviction=_conviction(score),
        components=InvestmentComponents(
            moat=ms.score,
            capital_allocation=ca.score,
            earnings_quality=eq.score,
            management=mgmt_score_val,
            valuation=val_score_val,
            dividend_safety=div.score if div.is_dividend_payer else None,
        ),
        years_analyzed=len(annual_data),
        evidence=evidence,
    )


def investment_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
    **kwargs: Any,
) -> InvestmentScore:
    """Fetch data and compute Investment Score for a ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL').
    years : int
        Number of years of historical data to fetch (default 10).
    source : str
        Data source: 'yahoo' (default) or 'edgar'.
    **kwargs
        Additional keyword arguments forwarded to
        :func:`investment_score_from_series` (e.g. ``pe_ratio``,
        ``ev_ebitda``, ``wacc``, ``risk_free_rate``).
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
    return investment_score_from_series(raw, **kwargs)


investment_score.formula = (  # type: ignore[attr-defined]
    "0.25*Moat + 0.20*CapitalAllocation + 0.20*EarningsQuality + "
    "0.15*ManagementQuality + 0.20*ValuationAttractiveness"
)
investment_score.description = (  # type: ignore[attr-defined]
    "Grand-synthesis investment score 0–100. "
    "Grades: A+(≥90), A(80–89), B+(70–79), B(60–69), C(45–59), D(25–44), F(<25). "
    "Conviction: strong_buy/buy/hold/sell/strong_sell."
)
