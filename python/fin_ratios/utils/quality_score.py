"""
Quality Factor Score.

Synthesises three complementary quality dimensions into a single score:
  1. Earnings Quality    (35%) — reliability of reported earnings
  2. Economic Moat       (35%) — durability of competitive advantage
  3. Capital Allocation  (30%) — effectiveness of management's capital use

Together these map to the academic Quality factor (QMJ — Quality Minus Junk),
institutionalised by Asness, Frazzini & Pedersen (2019), and the Buffett-style
"wonderful company at a fair price" framework.

Score:  0–100
Grade:  'exceptional' (80–100), 'strong' (60–79), 'moderate' (40–59),
        'weak' (20–39), 'poor' (0–19)

References
----------
Asness, Frazzini & Pedersen (2019) — Quality Minus Junk.
                                     Review of Accounting Studies.
Piotroski, J.D. (2000)             — Value Investing: The Use of Historical
                                     Financial Statement Information.
                                     Journal of Accounting Research.
Novy-Marx, R. (2013)               — The Other Side of Value.
                                     Journal of Financial Economics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .earnings_quality import earnings_quality_score_from_series, EarningsQualityScore
from .moat_score import moat_score_from_series, MoatScore
from .capital_allocation import capital_allocation_score_from_series, CapitalAllocationScore


@dataclass
class QualityComponents:
    earnings_quality: float    # 0–1
    moat: float                # 0–1
    capital_allocation: float  # 0–1


@dataclass
class QualityFactorScore:
    """Combined Quality Factor Score (Earnings Quality + Moat + Capital Allocation)."""

    score: int                       # 0–100
    grade: str                       # 'exceptional' | 'strong' | 'moderate' | 'weak' | 'poor'
    components: QualityComponents
    sub_scores: dict[str, Any]       # full sub-score objects for drill-down
    years_analyzed: int
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "exceptional": "Exceptional quality — highly reliable earnings, durable moat, "
                           "and disciplined capital allocation.",
            "strong":      "Strong quality profile with above-average scores across "
                           "all three dimensions.",
            "moderate":    "Moderate quality — solid in some areas but with notable gaps "
                           "in one or more dimensions.",
            "weak":        "Weak quality — significant concerns in earnings reliability, "
                           "competitive position, or capital allocation.",
            "poor":        "Poor quality across all dimensions — elevated risk profile.",
        }
        return (
            f"Quality Factor Score: {self.score}/100 [{self.grade.upper()}]. "
            f"{descs.get(self.grade, '')}"
        )

    def table(self) -> str:
        w = 52
        sep = "─" * w
        eq: EarningsQualityScore  = self.sub_scores.get("earnings_quality")   # type: ignore[assignment]
        ms: MoatScore             = self.sub_scores.get("moat")               # type: ignore[assignment]
        ca: CapitalAllocationScore = self.sub_scores.get("capital_allocation") # type: ignore[assignment]
        return "\n".join([
            f"Quality Factor Score: {self.score}/100  [{self.grade.upper()}]",
            sep,
            f"{'Dimension':<34} {'Score':>7}  {'Weight':>6}",
            sep,
            f"{'Earnings Quality':<34} {self.components.earnings_quality*100:>6.0f}%   {'35%':>6}"
            + (f"  [{eq.rating.upper()}]" if eq else ""),
            f"{'Economic Moat':<34} {self.components.moat*100:>6.0f}%   {'35%':>6}"
            + (f"  [{ms.width.upper()}]" if ms else ""),
            f"{'Capital Allocation':<34} {self.components.capital_allocation*100:>6.0f}%   {'30%':>6}"
            + (f"  [{ca.rating.upper()}]" if ca else ""),
            sep,
            f"{'Years of data analyzed':<34} {self.years_analyzed:>7}",
        ])

    def _repr_html_(self) -> str:
        grade_colors = {
            "exceptional": "#1a7f37", "strong":   "#0969da",
            "moderate":    "#9a6700", "weak":     "#cf222e",
            "poor":        "#8b1a1a",
        }
        c = grade_colors.get(self.grade, "#57606a")
        rows = [
            ("Earnings Quality",   self.components.earnings_quality,   "35%"),
            ("Economic Moat",      self.components.moat,               "35%"),
            ("Capital Allocation", self.components.capital_allocation, "30%"),
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
            f"Quality Factor: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.grade.upper()}]</span></div>"
            f"<table style='width:100%;border-collapse:collapse;margin-top:12px'>"
            f"<tr style='border-bottom:1px solid #d0d7de'>"
            f"<th style='text-align:left'>Dimension</th>"
            f"<th style='text-align:right'>Score</th>"
            f"<th style='text-align:right'>Weight</th></tr>"
            f"{row_html}</table>"
            f"<div style='margin-top:8px;color:#57606a;font-size:0.85em'>"
            f"{self.years_analyzed} years analyzed</div>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        eq = self.sub_scores.get("earnings_quality")
        ms = self.sub_scores.get("moat")
        ca = self.sub_scores.get("capital_allocation")
        return {
            "score": self.score,
            "grade": self.grade,
            "components": {
                "earnings_quality":   round(self.components.earnings_quality, 4),
                "moat":               round(self.components.moat, 4),
                "capital_allocation": round(self.components.capital_allocation, 4),
            },
            "sub_scores": {
                "earnings_quality":   eq.to_dict() if eq else None,
                "moat":               ms.to_dict() if ms else None,
                "capital_allocation": ca.to_dict() if ca else None,
            },
            "years_analyzed": self.years_analyzed,
            "evidence":       self.evidence,
            "interpretation": self.interpretation,
        }


# ── Public API ────────────────────────────────────────────────────────────────

def quality_score_from_series(
    annual_data: Sequence[Any],
    wacc: Optional[float] = None,
) -> QualityFactorScore:
    """Compute Quality Factor Score from a sequence of annual financial records.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects).
        Chronological order (oldest first). Minimum 2 years.
    wacc:
        Optional WACC override. If omitted, estimated from capital structure.

    Returns
    -------
    QualityFactorScore
        Composite score with drill-down into each dimension via `.sub_scores`.
    """
    if len(annual_data) < 2:
        raise ValueError("quality_score requires at least 2 years of data.")

    eq: EarningsQualityScore  = earnings_quality_score_from_series(annual_data)
    ms: MoatScore             = moat_score_from_series(annual_data, wacc=wacc)
    ca: CapitalAllocationScore = capital_allocation_score_from_series(annual_data, wacc=wacc)

    eq_norm = eq.score / 100.0
    ms_norm = ms.score / 100.0
    ca_norm = ca.score / 100.0

    raw = 0.35 * eq_norm + 0.35 * ms_norm + 0.30 * ca_norm
    score = round(raw * 100)

    grade = (
        "exceptional" if score >= 80 else
        "strong"      if score >= 60 else
        "moderate"    if score >= 40 else
        "weak"        if score >= 20 else
        "poor"
    )

    evidence = [
        f"Earnings Quality:   {eq.score}/100 [{eq.rating.upper()}]",
        f"Economic Moat:      {ms.score}/100 [{ms.width.upper()}]",
        f"Capital Allocation: {ca.score}/100 [{ca.rating.upper()}]",
    ]

    return QualityFactorScore(
        score=score,
        grade=grade,
        components=QualityComponents(
            earnings_quality=round(eq_norm, 4),
            moat=round(ms_norm, 4),
            capital_allocation=round(ca_norm, 4),
        ),
        sub_scores={
            "earnings_quality":   eq,
            "moat":               ms,
            "capital_allocation": ca,
        },
        years_analyzed=len(annual_data),
        evidence=evidence,
    )


def quality_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
    wacc: Optional[float] = None,
) -> QualityFactorScore:
    """Fetch data and compute Quality Factor Score for a ticker.

    Parameters
    ----------
    ticker : str   Stock ticker (e.g. 'AAPL')
    years  : int   Number of historical years (default 10)
    source : str   'yahoo' (default) or 'edgar'
    wacc   : float WACC override (optional)
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
    return quality_score_from_series(raw, wacc=wacc)
