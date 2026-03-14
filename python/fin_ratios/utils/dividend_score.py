"""
Dividend Safety Score.

Assesses the sustainability of a company's dividend based on cash flow
coverage, earnings payout ratio, balance sheet strength, and dividend
growth track record. Non-payers receive a special 'non-payer' designation
rather than being penalised.

Score:  0–100
Rating: 'safe' (≥70), 'adequate' (45–69), 'risky' (20–44), 'danger' (<20)
Special: 'non-payer' when the company has not paid dividends in any year
         analysed (score=50, is_dividend_payer=False).

Signals
-------
1. FCF Payout Ratio     (35%) — dividends / free cash flow
2. Earnings Payout Ratio (25%) — dividends / net income
3. Balance Sheet Strength (25%) — net debt / EBITDA
4. Dividend Growth Track  (15%) — consecutive years of dividend maintenance

References
----------
Siegel, J.J. (2014) — Stocks for the Long Run (5th ed.), McGraw-Hill
Dividend Aristocrats methodology — S&P Dow Jones Indices
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence


# ── Field registry ─────────────────────────────────────────────────────────────

_ZERO_FIELDS = frozenset(
    {
        "revenue",
        "ebit",
        "net_income",
        "total_assets",
        "total_equity",
        "total_debt",
        "cash",
        "capex",
        "depreciation",
        "interest_expense",
        "income_tax_expense",
        "operating_cash_flow",
        "dividends_paid",
        "current_assets",
        "current_liabilities",
        "ebt",
    }
)

_ALIASES: dict[str, list[str]] = {
    "ebit": ["operating_income"],
    "total_debt": ["long_term_debt"],
    "depreciation": ["depreciation_amortization"],
    "dividends_paid": ["dividends", "dividend_payments", "dividends_and_other_cash_distributions"],
    "operating_cash_flow": [
        "cash_from_operations",
        "cfo",
        "net_cash_from_operating_activities",
        "operating_activities",
    ],
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


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ── FCF helper ─────────────────────────────────────────────────────────────────


def _year_fcf(d: _Acc) -> float:
    """FCF = OCF - capex, falling back to NOPAT-based if OCF unavailable."""
    ocf = d.operating_cash_flow
    capex = d.capex
    if ocf > 0:
        return ocf - capex
    # NOPAT-based fallback
    ebit = d.ebit
    if ebit <= 0:
        return 0.0
    ebt = d.ebt
    tax = d.income_tax_expense
    tax_rate = _clamp(tax / ebt, 0.0, 0.50) if ebt > 0 and tax > 0 else 0.21
    nopat = ebit * (1.0 - tax_rate)
    return nopat + d.depreciation - capex


# ── Signal 1: FCF Payout Ratio ────────────────────────────────────────────────


def _score_fcf_payout(accs: list[_Acc]) -> tuple[float, list[str]]:
    ratios: list[float] = []
    for d in accs:
        div = d.dividends_paid
        if div <= 0:
            continue
        fcf = _year_fcf(d)
        if fcf <= 0:
            ratios.append(2.0)  # penalised: paying dividends from negative FCF
        else:
            ratios.append(div / fcf)

    if not ratios:
        return 0.50, ["FCF payout ratio: no dividend payments found (neutral score)"]

    mean_ratio = _mean(ratios)
    if mean_ratio < 0.40:
        score = 1.0
    elif mean_ratio < 0.60:
        score = 0.75
    elif mean_ratio < 0.80:
        score = 0.45
    elif mean_ratio <= 1.00:
        score = 0.15
    else:
        score = 0.0

    quality = (
        "very safe"
        if mean_ratio < 0.40
        else "safe"
        if mean_ratio < 0.60
        else "moderate"
        if mean_ratio < 0.80
        else "stretched"
        if mean_ratio <= 1.00
        else "unsustainable"
    )
    return score, [
        f"FCF payout ratio: mean {mean_ratio * 100:.0f}%  [{quality}]",
    ]


# ── Signal 2: Earnings Payout Ratio ───────────────────────────────────────────


def _score_earnings_payout(accs: list[_Acc]) -> tuple[float, list[str]]:
    ratios: list[float] = []
    for d in accs:
        div = d.dividends_paid
        ni = d.net_income
        if div <= 0:
            continue
        if ni <= 0:
            ratios.append(2.0)
        else:
            ratios.append(div / ni)

    if not ratios:
        return 0.50, ["Earnings payout ratio: no dividend payments found (neutral score)"]

    mean_ratio = _mean(ratios)
    if mean_ratio < 0.35:
        score = 1.0
    elif mean_ratio < 0.55:
        score = 0.75
    elif mean_ratio < 0.75:
        score = 0.45
    elif mean_ratio <= 1.00:
        score = 0.20
    else:
        score = 0.0

    quality = (
        "conservative"
        if mean_ratio < 0.35
        else "moderate"
        if mean_ratio < 0.55
        else "elevated"
        if mean_ratio < 0.75
        else "high"
        if mean_ratio <= 1.00
        else "exceeds earnings"
    )
    return score, [
        f"Earnings payout ratio: mean {mean_ratio * 100:.0f}%  [{quality}]",
    ]


# ── Signal 3: Balance Sheet Strength ──────────────────────────────────────────


def _score_balance_sheet(accs: list[_Acc]) -> tuple[float, list[str]]:
    d = accs[-1]  # most recent year
    total_debt = d.total_debt
    cash = d.cash
    net_debt = total_debt - cash

    ebit = d.ebit
    depreciation = d.depreciation
    ebitda = ebit + depreciation if ebit > 0 else 0.0

    if ebitda <= 0:
        # Fall back: use net income + tax + interest + depreciation approximation
        ni = d.net_income
        tax = d.income_tax_expense
        interest = d.interest_expense
        ebitda = ni + tax + interest + depreciation
        if ebitda <= 0:
            return 0.30, ["Balance sheet strength: unable to compute EBITDA (conservative score)"]

    nd_ebitda = net_debt / ebitda

    if nd_ebitda < 0:
        score = 1.0
        quality = "net cash position"
    elif nd_ebitda <= 1.0:
        score = 0.85
        quality = "minimal leverage"
    elif nd_ebitda <= 2.0:
        score = 0.65
        quality = "modest leverage"
    elif nd_ebitda <= 3.0:
        score = 0.40
        quality = "moderate leverage"
    elif nd_ebitda <= 4.0:
        score = 0.20
        quality = "high leverage"
    else:
        score = 0.05
        quality = "very high leverage"

    return score, [
        f"Net debt / EBITDA: {nd_ebitda:.1f}x  [{quality}]  "
        f"(net debt {net_debt / 1e9:.1f}B, EBITDA {ebitda / 1e9:.1f}B)",
    ]


# ── Signal 4: Dividend Growth Track ───────────────────────────────────────────


def _score_dividend_growth_track(accs: list[_Acc]) -> tuple[float, list[str]]:
    divs = [d.dividends_paid for d in accs]

    # Count consecutive years (most recent first) where div >= prior year
    streak = 0
    for i in range(len(divs) - 1, 0, -1):
        if divs[i] >= divs[i - 1] and divs[i] > 0:
            streak += 1
        else:
            break

    if streak >= 10:
        score = 1.0
    elif streak >= 7:
        score = 0.75
    elif streak >= 4:
        score = 0.55
    elif streak >= 2:
        score = 0.35
    elif streak >= 1:
        score = 0.15
    else:
        score = 0.0

    track = (
        "aristocrat-level"
        if streak >= 10
        else "strong track record"
        if streak >= 7
        else "growing dividend"
        if streak >= 4
        else "short track record"
        if streak >= 2
        else "limited history"
        if streak >= 1
        else "dividend cut or freeze detected"
    )
    return score, [
        f"Dividend growth track: {streak} consecutive years maintained  [{track}]",
    ]


# ── Result types ───────────────────────────────────────────────────────────────


@dataclass
class DividendComponents:
    fcf_payout_ratio: float  # 0–1
    earnings_payout_ratio: float  # 0–1
    balance_sheet_strength: float  # 0–1
    dividend_growth_track: float  # 0–1


@dataclass
class DividendSafetyScore:
    """Result of the Dividend Safety Score computation."""

    score: int  # 0–100
    rating: str  # 'safe' | 'adequate' | 'risky' | 'danger' | 'non-payer'
    components: DividendComponents
    years_analyzed: int
    is_dividend_payer: bool
    evidence: list[str] = field(default_factory=list)

    @property
    def interpretation(self) -> str:
        descs = {
            "safe": "Dividend is well-covered by free cash flow and earnings, supported "
            "by a strong balance sheet and a consistent growth track record.",
            "adequate": "Dividend is reasonably covered with moderate payout ratios and "
            "adequate balance sheet headroom.",
            "risky": "Dividend coverage is thin — high payout ratios or elevated leverage "
            "increase the risk of a cut in a downturn.",
            "danger": "Dividend appears unsustainable — payout ratios exceed cash flows "
            "or the balance sheet is severely strained.",
            "non-payer": "Company does not currently pay a dividend. "
            "Neutral score assigned for composite scoring purposes.",
        }
        return (
            f"Dividend Safety Score: {self.score}/100 [{self.rating.upper()}]. "
            f"{descs.get(self.rating, '')}"
        )

    def table(self) -> str:
        w = 52
        sep = "─" * w
        payer_note = "" if self.is_dividend_payer else "  [non-payer]"
        return "\n".join(
            [
                f"Dividend Safety Score: {self.score}/100  [{self.rating.upper()}]{payer_note}",
                sep,
                f"{'Component':<34} {'Score':>7}  {'Weight':>6}",
                sep,
                f"{'FCF Payout Ratio':<34} {self.components.fcf_payout_ratio * 100:>6.0f}%   {'35%':>6}",
                f"{'Earnings Payout Ratio':<34} {self.components.earnings_payout_ratio * 100:>6.0f}%   {'25%':>6}",
                f"{'Balance Sheet Strength':<34} {self.components.balance_sheet_strength * 100:>6.0f}%   {'25%':>6}",
                f"{'Dividend Growth Track':<34} {self.components.dividend_growth_track * 100:>6.0f}%   {'15%':>6}",
                sep,
                f"{'Years of data analyzed':<34} {self.years_analyzed:>7}",
            ]
        )

    def _repr_html_(self) -> str:
        colours = {
            "safe": "#1a7f37",
            "adequate": "#0969da",
            "risky": "#9a6700",
            "danger": "#cf222e",
            "non-payer": "#57606a",
        }
        c = colours.get(self.rating, "#57606a")
        rows = [
            ("FCF Payout Ratio", self.components.fcf_payout_ratio, "35%"),
            ("Earnings Payout Ratio", self.components.earnings_payout_ratio, "25%"),
            ("Balance Sheet Strength", self.components.balance_sheet_strength, "25%"),
            ("Dividend Growth Track", self.components.dividend_growth_track, "15%"),
        ]
        row_html = "".join(
            f"<tr><td>{n}</td><td style='text-align:right'>{v * 100:.0f}%</td>"
            f"<td style='text-align:right;color:#57606a'>{wt}</td></tr>"
            for n, v, wt in rows
        )
        payer_badge = (
            ""
            if self.is_dividend_payer
            else "<span style='margin-left:8px;font-size:0.75em;color:#57606a'>[non-payer]</span>"
        )
        return (
            f"<div style='font-family:monospace;border:1px solid #d0d7de;border-radius:6px;"
            f"padding:16px;max-width:500px'>"
            f"<div style='font-size:1.1em;font-weight:bold;color:{c}'>"
            f"Dividend Safety: {self.score}/100 "
            f"<span style='font-size:0.9em'>[{self.rating.upper()}]</span>{payer_badge}</div>"
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
                "fcf_payout_ratio": round(self.components.fcf_payout_ratio, 4),
                "earnings_payout_ratio": round(self.components.earnings_payout_ratio, 4),
                "balance_sheet_strength": round(self.components.balance_sheet_strength, 4),
                "dividend_growth_track": round(self.components.dividend_growth_track, 4),
            },
            "years_analyzed": self.years_analyzed,
            "is_dividend_payer": self.is_dividend_payer,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
        }


# ── Public API ─────────────────────────────────────────────────────────────────


def dividend_safety_score_from_series(
    annual_data: Sequence[Any],
) -> DividendSafetyScore:
    """Compute Dividend Safety Score from a sequence of annual financial records.

    Parameters
    ----------
    annual_data:
        Sequence of annual records (dicts, dataclasses, or objects with attributes).
        Must be in chronological order (oldest first). Minimum 2 years required.

    Returns
    -------
    DividendSafetyScore
        Dataclass with ``.score`` (0–100), ``.rating``, ``.components``,
        ``.is_dividend_payer``, ``.evidence``, ``.table()``,
        ``._repr_html_()``, and ``.to_dict()``.

    Notes
    -----
    If no dividends are recorded in any year, the score is set to 50 and
    ``rating`` is ``'non-payer'``, ``is_dividend_payer`` is ``False``.
    """
    if len(annual_data) < 2:
        raise ValueError("dividend_safety_score requires at least 2 years of data.")

    accs = [_Acc(d) for d in annual_data]

    # Check if company is a dividend payer
    total_divs = sum(d.dividends_paid for d in accs)
    if total_divs <= 0:
        return DividendSafetyScore(
            score=50,
            rating="non-payer",
            components=DividendComponents(
                fcf_payout_ratio=0.50,
                earnings_payout_ratio=0.50,
                balance_sheet_strength=0.50,
                dividend_growth_track=0.50,
            ),
            years_analyzed=len(accs),
            is_dividend_payer=False,
            evidence=["Company has not paid dividends in the analyzed period."],
        )

    s_fcf, ev_fcf = _score_fcf_payout(accs)
    s_eps, ev_eps = _score_earnings_payout(accs)
    s_bs, ev_bs = _score_balance_sheet(accs)
    s_dgt, ev_dgt = _score_dividend_growth_track(accs)

    raw = 0.35 * s_fcf + 0.25 * s_eps + 0.25 * s_bs + 0.15 * s_dgt
    score = round(_clamp(raw, 0.0, 1.0) * 100)

    rating = (
        "safe"
        if score >= 70
        else "adequate"
        if score >= 45
        else "risky"
        if score >= 20
        else "danger"
    )

    return DividendSafetyScore(
        score=score,
        rating=rating,
        components=DividendComponents(
            fcf_payout_ratio=round(s_fcf, 4),
            earnings_payout_ratio=round(s_eps, 4),
            balance_sheet_strength=round(s_bs, 4),
            dividend_growth_track=round(s_dgt, 4),
        ),
        years_analyzed=len(accs),
        is_dividend_payer=True,
        evidence=ev_fcf + ev_eps + ev_bs + ev_dgt,
    )


def dividend_safety_score(
    ticker: str,
    years: int = 10,
    source: str = "yahoo",
) -> DividendSafetyScore:
    """Fetch data and compute Dividend Safety Score for a ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'JNJ').
    years : int
        Number of years of historical data to fetch (default 10).
    source : str
        Data source: 'yahoo' (default) or 'edgar'.
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
    return dividend_safety_score_from_series(raw)


dividend_safety_score.formula = (  # type: ignore[attr-defined]
    "0.35*FCFPayoutRatio + 0.25*EarningsPayoutRatio + 0.25*BalanceSheetStrength + 0.15*DividendGrowthTrack"
)
dividend_safety_score.description = (  # type: ignore[attr-defined]
    "Dividend safety score 0–100. Safe ≥70, Adequate 45–69, Risky 20–44, Danger <20. "
    "Non-payers receive score=50 with rating='non-payer'."
)
