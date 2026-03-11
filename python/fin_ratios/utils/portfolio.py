"""
Portfolio Quality Analysis.

Aggregates quality scores across a portfolio of holdings weighted by position
size. Provides a composite view of portfolio quality tilt without requiring
individual deep-dives into each company.

Usage
-----
    from fin_ratios.utils.portfolio import portfolio_quality

    holdings = {"AAPL": 0.30, "MSFT": 0.30, "JNJ": 0.20, "PG": 0.20}
    result = portfolio_quality(holdings, source="yahoo")
    print(result.table())
    print(result._repr_html_())   # rich Jupyter display

For bring-your-own-data use:

    from fin_ratios.utils.portfolio import portfolio_quality_from_series

    series_map = {
        "AAPL": (0.30, [...apple annual dicts...]),
        "MSFT": (0.30, [...msft annual dicts...]),
    }
    result = portfolio_quality_from_series(series_map)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .quality_score import quality_score, quality_score_from_series, QualityFactorScore


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class HoldingQuality:
    ticker: str
    weight: float                    # normalised weight (sum to 1.0)
    quality: Optional[QualityFactorScore]
    error: Optional[str] = None


@dataclass
class PortfolioQuality:
    """Portfolio-level quality analysis across all holdings."""

    holdings: list[HoldingQuality]
    weighted_quality_score: float        # 0–100 overall weighted average
    weighted_moat_score: float           # 0–100 moat dimension
    weighted_earnings_quality: float     # 0–100 earnings quality dimension
    weighted_capital_allocation: float   # 0–100 capital allocation dimension
    effective_weight: float              # fraction of portfolio successfully analysed
    errors: list[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        s = self.weighted_quality_score
        return (
            "exceptional" if s >= 80 else
            "strong"      if s >= 60 else
            "moderate"    if s >= 40 else
            "weak"        if s >= 20 else
            "poor"
        )

    def table(self) -> str:
        w = 72
        sep = "─" * w
        lines = [
            "Portfolio Quality Analysis",
            sep,
            f"{'Ticker':<8} {'Weight':>7}  {'Quality':>8}  {'Moat':>6}  {'EQ':>5}  {'CA':>5}  {'Grade'}",
            sep,
        ]
        for h in sorted(self.holdings, key=lambda x: -x.weight):
            if h.error or h.quality is None:
                lines.append(f"  {h.ticker:<6} {h.weight*100:>6.1f}%   ERROR: {h.error or 'unknown'}")
                continue
            q = h.quality
            moat_score  = q.sub_scores["moat"].score
            eq_score    = q.sub_scores["earnings_quality"].score
            ca_score    = q.sub_scores["capital_allocation"].score
            lines.append(
                f"  {h.ticker:<6} {h.weight*100:>6.1f}%  "
                f"{q.score:>8}  "
                f"{moat_score:>6}  "
                f"{eq_score:>5}  "
                f"{ca_score:>5}  "
                f"{q.grade}"
            )
        lines += [
            sep,
            f"{'Weighted Avg':<8} {self.effective_weight*100:>6.1f}%  "
            f"{self.weighted_quality_score:>8.0f}  "
            f"{self.weighted_moat_score:>6.0f}  "
            f"{self.weighted_earnings_quality:>5.0f}  "
            f"{self.weighted_capital_allocation:>5.0f}  "
            f"{self.grade.upper()}",
        ]
        if self.errors:
            lines += ["", "Errors:"] + [f"  • {e}" for e in self.errors]
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        grade_colors = {
            "exceptional": "#1a7f37", "strong":   "#0969da",
            "moderate":    "#9a6700", "weak":     "#cf222e",
            "poor":        "#8b1a1a",
        }
        c = grade_colors.get(self.grade, "#57606a")
        rows = ""
        for h in sorted(self.holdings, key=lambda x: -x.weight):
            if h.error or h.quality is None:
                rows += (
                    f"<tr><td>{h.ticker}</td><td>{h.weight*100:.1f}%</td>"
                    f"<td colspan='5' style='color:#cf222e'>Error: {h.error or 'unknown'}</td></tr>"
                )
                continue
            q = h.quality
            rows += (
                f"<tr>"
                f"<td style='padding:4px 8px'>{h.ticker}</td>"
                f"<td style='padding:4px 8px;text-align:right'>{h.weight*100:.1f}%</td>"
                f"<td style='padding:4px 8px;text-align:right'>{q.score}</td>"
                f"<td style='padding:4px 8px;text-align:right'>{q.sub_scores['moat'].score}</td>"
                f"<td style='padding:4px 8px;text-align:right'>{q.sub_scores['earnings_quality'].score}</td>"
                f"<td style='padding:4px 8px;text-align:right'>{q.sub_scores['capital_allocation'].score}</td>"
                f"<td style='padding:4px 8px'>{q.grade}</td>"
                f"</tr>"
            )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;padding:16px'>"
            f"<div style='font-size:1.1em;font-weight:bold;color:{c};margin-bottom:12px'>"
            f"Portfolio Quality: {self.weighted_quality_score:.0f}/100 [{self.grade.upper()}]"
            f"</div>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"<tr style='border-bottom:1px solid #d0d7de;color:#57606a;font-size:0.85em'>"
            f"<th style='text-align:left;padding:4px 8px'>Ticker</th>"
            f"<th style='text-align:right;padding:4px 8px'>Weight</th>"
            f"<th style='text-align:right;padding:4px 8px'>Quality</th>"
            f"<th style='text-align:right;padding:4px 8px'>Moat</th>"
            f"<th style='text-align:right;padding:4px 8px'>EQ</th>"
            f"<th style='text-align:right;padding:4px 8px'>CA</th>"
            f"<th style='text-align:left;padding:4px 8px'>Grade</th>"
            f"</tr>"
            f"{rows}"
            f"<tr style='border-top:1px solid #d0d7de;font-weight:bold'>"
            f"<td style='padding:4px 8px'>Weighted Avg</td>"
            f"<td style='padding:4px 8px;text-align:right'>{self.effective_weight*100:.0f}%</td>"
            f"<td style='padding:4px 8px;text-align:right'>{self.weighted_quality_score:.0f}</td>"
            f"<td style='padding:4px 8px;text-align:right'>{self.weighted_moat_score:.0f}</td>"
            f"<td style='padding:4px 8px;text-align:right'>{self.weighted_earnings_quality:.0f}</td>"
            f"<td style='padding:4px 8px;text-align:right'>{self.weighted_capital_allocation:.0f}</td>"
            f"<td style='padding:4px 8px'>{self.grade.upper()}</td>"
            f"</tr>"
            f"</table>"
            f"</div>"
        )

    def to_dict(self) -> dict:
        return {
            "weighted_quality_score":      round(self.weighted_quality_score, 1),
            "weighted_moat_score":         round(self.weighted_moat_score, 1),
            "weighted_earnings_quality":   round(self.weighted_earnings_quality, 1),
            "weighted_capital_allocation": round(self.weighted_capital_allocation, 1),
            "grade":                       self.grade,
            "effective_weight":            round(self.effective_weight, 4),
            "holdings": [
                {
                    "ticker":        h.ticker,
                    "weight":        h.weight,
                    "quality_score": h.quality.score if h.quality else None,
                    "grade":         h.quality.grade if h.quality else None,
                    "error":         h.error,
                }
                for h in self.holdings
            ],
            "errors": self.errors,
        }


# ── Internal aggregation helper ────────────────────────────────────────────────

def _aggregate(holding_results: list[HoldingQuality]) -> PortfolioQuality:
    successful = [h for h in holding_results if h.quality is not None]
    if not successful:
        raise RuntimeError("All holdings failed to compute. Check data and tickers.")

    eff_weight = sum(h.weight for h in successful)
    renorm = 1.0 / eff_weight if eff_weight > 0 else 1.0

    def _wavg(attr_path: str) -> float:
        total = 0.0
        for h in successful:
            obj: Any = h.quality
            for part in attr_path.split("."):
                obj = obj.sub_scores[part] if part in (obj.sub_scores if hasattr(obj, "sub_scores") else {}) else getattr(obj, part)
            total += h.weight * float(obj) * renorm
        return round(total, 1)

    wq  = sum(h.weight * h.quality.score * renorm for h in successful)                                          # type: ignore[union-attr]
    wm  = sum(h.weight * h.quality.sub_scores["moat"].score * renorm for h in successful)                       # type: ignore[union-attr]
    weq = sum(h.weight * h.quality.sub_scores["earnings_quality"].score * renorm for h in successful)           # type: ignore[union-attr]
    wca = sum(h.weight * h.quality.sub_scores["capital_allocation"].score * renorm for h in successful)         # type: ignore[union-attr]

    errors = [h.error for h in holding_results if h.error]

    return PortfolioQuality(
        holdings=holding_results,
        weighted_quality_score=round(wq, 1),
        weighted_moat_score=round(wm, 1),
        weighted_earnings_quality=round(weq, 1),
        weighted_capital_allocation=round(wca, 1),
        effective_weight=round(eff_weight, 4),
        errors=[e for e in errors if e],
    )


# ── Public API ────────────────────────────────────────────────────────────────

def portfolio_quality_from_series(
    holdings_data: dict[str, tuple[float, list[Any]]],
    wacc: Optional[float] = None,
) -> PortfolioQuality:
    """Compute portfolio quality scores from pre-loaded annual data.

    Parameters
    ----------
    holdings_data : dict[str, tuple[float, list]]
        Mapping of ``ticker → (weight, annual_data_list)``.
        Weights need not sum to 1 — they are normalised automatically.
    wacc : float, optional
        WACC override applied to all holdings.

    Returns
    -------
    PortfolioQuality
    """
    if not holdings_data:
        raise ValueError("holdings_data must be a non-empty dict.")

    total_weight = sum(w for w, _ in holdings_data.values())
    if total_weight <= 0:
        raise ValueError("Sum of holding weights must be positive.")

    results: list[HoldingQuality] = []
    for ticker, (raw_weight, annual_data) in holdings_data.items():
        norm_weight = raw_weight / total_weight
        try:
            qs = quality_score_from_series(annual_data, wacc=wacc)
            results.append(HoldingQuality(ticker=ticker, weight=norm_weight, quality=qs))
        except Exception as exc:
            results.append(HoldingQuality(
                ticker=ticker, weight=norm_weight, quality=None, error=str(exc)
            ))

    return _aggregate(results)


def portfolio_quality(
    holdings: dict[str, float],
    years: int = 10,
    source: str = "yahoo",
    wacc: Optional[float] = None,
) -> PortfolioQuality:
    """Fetch data and compute portfolio quality scores across all holdings.

    Parameters
    ----------
    holdings : dict[str, float]
        Mapping of ``ticker → portfolio weight``. Weights are normalised
        automatically so they need not sum to 1.
    years : int
        Historical years to fetch per holding (default 10).
    source : str
        Data source: 'yahoo' (default) or 'edgar'.
    wacc : float, optional
        WACC override applied uniformly to all holdings.

    Returns
    -------
    PortfolioQuality
        Weighted aggregate quality scores with per-holding breakdown.

    Example
    -------
    >>> result = portfolio_quality({"AAPL": 0.25, "MSFT": 0.25, "JNJ": 0.25, "PG": 0.25})
    >>> print(result.table())
    """
    if not holdings:
        raise ValueError("holdings must be a non-empty dict.")

    total_weight = sum(holdings.values())
    if total_weight <= 0:
        raise ValueError("Sum of holding weights must be positive.")

    norm = {t: w / total_weight for t, w in holdings.items()}
    results: list[HoldingQuality] = []

    for ticker, weight in norm.items():
        try:
            qs = quality_score(ticker, years=years, source=source, wacc=wacc)
            results.append(HoldingQuality(ticker=ticker, weight=weight, quality=qs))
        except Exception as exc:
            results.append(HoldingQuality(
                ticker=ticker, weight=weight, quality=None, error=str(exc)
            ))

    return _aggregate(results)
