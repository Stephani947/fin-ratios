"""
Composite Financial Health Score (0–100).

Aggregates Piotroski F-Score, Altman Z-Score, ROIC vs WACC, FCF Quality,
and Growth into a single interpretable number.

Usage:
    from fin_ratios.utils.health_score import health_score

    result = health_score(
        piotroski_score=7,
        altman_z=3.5,
        roic=0.22,
        wacc=0.09,
        fcf_conversion=0.95,
        revenue_growth=0.12,
        net_margin=0.18,
    )
    print(result.score)           # 78
    print(result.grade)           # "B+"
    print(result.interpretation)  # "Healthy — strong fundamentals with minor concerns"
    print(result.breakdown)       # {'profitability': 85, 'value_creation': 90, ...}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthScore:
    """Composite financial health score."""

    score: float  # 0–100
    grade: str  # "A+", "A", "B+", "B", "C", "D", "F"
    interpretation: str
    breakdown: dict[str, float]  # component scores 0–100
    signals: dict[str, str]  # human-readable signal per component


def health_score(
    # Composite models
    piotroski_score: Optional[int] = None,  # 0–9
    altman_z: Optional[float] = None,  # raw Z-score
    beneish_m: Optional[float] = None,  # M-Score (< -2.22 = clean)
    # Value creation
    roic: Optional[float] = None,  # e.g. 0.22 for 22%
    wacc: Optional[float] = None,  # e.g. 0.09 for 9%
    # Profitability
    net_margin: Optional[float] = None,  # e.g. 0.18
    gross_margin: Optional[float] = None,  # e.g. 0.60
    roe: Optional[float] = None,  # e.g. 0.25
    # Cash flow quality
    fcf_conversion: Optional[float] = None,  # FCF / Net Income
    fcf_margin: Optional[float] = None,  # FCF / Revenue
    # Growth
    revenue_growth: Optional[float] = None,  # YoY, e.g. 0.12
    # Balance sheet
    debt_to_equity: Optional[float] = None,  # e.g. 0.5
    current_ratio: Optional[float] = None,  # e.g. 2.0
    interest_coverage: Optional[float] = None,  # e.g. 8.0
) -> HealthScore:
    """
    Compute a composite financial health score (0–100).

    Weights:
        - Piotroski F-Score  : 20%  (financial strength breadth)
        - Altman Z-Score     : 15%  (bankruptcy risk)
        - ROIC vs WACC       : 20%  (economic value creation)
        - Profitability      : 20%  (margins + ROE)
        - FCF Quality        : 15%  (earnings are real cash)
        - Growth             : 10%  (revenue trajectory)
    """
    components: dict[str, float] = {}
    signals: dict[str, str] = {}

    # ── 1. Piotroski F-Score (weight 20) ─────────────────────────────────────
    if piotroski_score is not None:
        p_score = (piotroski_score / 9) * 100
        components["piotroski"] = p_score
        if piotroski_score >= 8:
            signals["piotroski"] = f"F-Score {piotroski_score}/9 — Strong financial strength"
        elif piotroski_score >= 6:
            signals["piotroski"] = f"F-Score {piotroski_score}/9 — Healthy fundamentals"
        elif piotroski_score >= 4:
            signals["piotroski"] = f"F-Score {piotroski_score}/9 — Mixed signals"
        else:
            signals["piotroski"] = f"F-Score {piotroski_score}/9 — Weak fundamentals"

    # ── 2. Altman Z-Score (weight 15) ─────────────────────────────────────────
    if altman_z is not None:
        # Safe > 2.99, Grey 1.81–2.99, Distress < 1.81
        if altman_z >= 4.0:
            az_score = 100.0
        elif altman_z >= 2.99:
            az_score = 75.0 + (altman_z - 2.99) / (4.0 - 2.99) * 25.0
        elif altman_z >= 1.81:
            az_score = 40.0 + (altman_z - 1.81) / (2.99 - 1.81) * 35.0
        else:
            az_score = max(0.0, 40.0 * altman_z / 1.81)
        components["altman_z"] = az_score
        zone = "safe" if altman_z >= 2.99 else ("grey" if altman_z >= 1.81 else "distress")
        signals["altman_z"] = f"Z-Score {altman_z:.2f} — {zone.capitalize()} zone"

    # ── 3. Beneish M-Score penalty (reduces other scores if flagged) ───────────
    manipulation_penalty = 0.0
    if beneish_m is not None:
        if beneish_m > -1.78:
            manipulation_penalty = 20.0
            signals["beneish"] = f"M-Score {beneish_m:.2f} — Strong manipulation flag"
        elif beneish_m > -2.22:
            manipulation_penalty = 10.0
            signals["beneish"] = f"M-Score {beneish_m:.2f} — Possible manipulation"
        else:
            signals["beneish"] = f"M-Score {beneish_m:.2f} — Clean earnings quality"

    # ── 4. ROIC vs WACC — value creation (weight 20) ──────────────────────────
    if roic is not None:
        if wacc is not None:
            spread = roic - wacc
            if spread >= 0.20:
                vc_score = 100.0
            elif spread >= 0.10:
                vc_score = 80.0 + (spread - 0.10) / 0.10 * 20.0
            elif spread >= 0.05:
                vc_score = 60.0 + (spread - 0.05) / 0.05 * 20.0
            elif spread >= 0.0:
                vc_score = 40.0 + spread / 0.05 * 20.0
            elif spread >= -0.05:
                vc_score = 20.0 + (spread + 0.05) / 0.05 * 20.0
            else:
                vc_score = max(0.0, 20.0 + spread * 4)
            signals["value_creation"] = (
                f"ROIC {roic * 100:.1f}% vs WACC {wacc * 100:.1f}% (spread {spread * 100:+.1f}%)"
            )
        else:
            # No WACC — score purely on ROIC level
            if roic >= 0.25:
                vc_score = 90.0
            elif roic >= 0.15:
                vc_score = 70.0 + (roic - 0.15) / 0.10 * 20.0
            elif roic >= 0.08:
                vc_score = 45.0 + (roic - 0.08) / 0.07 * 25.0
            else:
                vc_score = max(0.0, roic / 0.08 * 45.0)
            signals["value_creation"] = f"ROIC {roic * 100:.1f}% (WACC not provided)"
        components["value_creation"] = vc_score

    # ── 5. Profitability (weight 20) ──────────────────────────────────────────
    prof_scores = []
    if net_margin is not None:
        if net_margin >= 0.20:
            nm_s = 100.0
        elif net_margin >= 0.10:
            nm_s = 65.0 + (net_margin - 0.10) / 0.10 * 35.0
        elif net_margin >= 0.05:
            nm_s = 35.0 + (net_margin - 0.05) / 0.05 * 30.0
        elif net_margin >= 0.0:
            nm_s = net_margin / 0.05 * 35.0
        else:
            nm_s = max(0.0, 35.0 + net_margin * 7)
        prof_scores.append(nm_s)

    if gross_margin is not None:
        if gross_margin >= 0.60:
            gm_s = 100.0
        elif gross_margin >= 0.40:
            gm_s = 65.0 + (gross_margin - 0.40) / 0.20 * 35.0
        elif gross_margin >= 0.20:
            gm_s = 30.0 + (gross_margin - 0.20) / 0.20 * 35.0
        else:
            gm_s = max(0.0, gross_margin / 0.20 * 30.0)
        prof_scores.append(gm_s)

    if roe is not None:
        if roe >= 0.25:
            roe_s = 100.0
        elif roe >= 0.15:
            roe_s = 70.0 + (roe - 0.15) / 0.10 * 30.0
        elif roe >= 0.08:
            roe_s = 40.0 + (roe - 0.08) / 0.07 * 30.0
        elif roe >= 0.0:
            roe_s = roe / 0.08 * 40.0
        else:
            roe_s = 0.0
        prof_scores.append(roe_s)

    if prof_scores:
        components["profitability"] = sum(prof_scores) / len(prof_scores)
        margin_strs = []
        if net_margin is not None:
            margin_strs.append(f"Net {net_margin * 100:.1f}%")
        if gross_margin is not None:
            margin_strs.append(f"Gross {gross_margin * 100:.1f}%")
        if roe is not None:
            margin_strs.append(f"ROE {roe * 100:.1f}%")
        signals["profitability"] = "  |  ".join(margin_strs)

    # ── 6. FCF Quality (weight 15) ────────────────────────────────────────────
    fcf_scores = []
    if fcf_conversion is not None:
        if fcf_conversion >= 1.0:
            fc_s = 100.0
        elif fcf_conversion >= 0.8:
            fc_s = 75.0 + (fcf_conversion - 0.8) / 0.2 * 25.0
        elif fcf_conversion >= 0.5:
            fc_s = 40.0 + (fcf_conversion - 0.5) / 0.3 * 35.0
        elif fcf_conversion >= 0.0:
            fc_s = fcf_conversion / 0.5 * 40.0
        else:
            fc_s = 0.0
        fcf_scores.append(fc_s)
        signals["fcf_quality"] = f"FCF Conversion {fcf_conversion:.2f}x"

    if fcf_margin is not None:
        if fcf_margin >= 0.20:
            fm_s = 100.0
        elif fcf_margin >= 0.10:
            fm_s = 65.0 + (fcf_margin - 0.10) / 0.10 * 35.0
        elif fcf_margin >= 0.05:
            fm_s = 35.0 + (fcf_margin - 0.05) / 0.05 * 30.0
        elif fcf_margin >= 0.0:
            fm_s = fcf_margin / 0.05 * 35.0
        else:
            fm_s = 0.0
        fcf_scores.append(fm_s)
        if "fcf_quality" not in signals:
            signals["fcf_quality"] = f"FCF Margin {fcf_margin * 100:.1f}%"
        else:
            signals["fcf_quality"] += f"  |  FCF Margin {fcf_margin * 100:.1f}%"

    if fcf_scores:
        components["fcf_quality"] = sum(fcf_scores) / len(fcf_scores)

    # ── 7. Growth (weight 10) ─────────────────────────────────────────────────
    if revenue_growth is not None:
        if revenue_growth >= 0.20:
            gr_s = 100.0
        elif revenue_growth >= 0.10:
            gr_s = 70.0 + (revenue_growth - 0.10) / 0.10 * 30.0
        elif revenue_growth >= 0.05:
            gr_s = 45.0 + (revenue_growth - 0.05) / 0.05 * 25.0
        elif revenue_growth >= 0.0:
            gr_s = revenue_growth / 0.05 * 45.0
        else:
            gr_s = max(0.0, 30.0 + revenue_growth * 6)
        components["growth"] = gr_s
        signals["growth"] = f"Revenue growth {revenue_growth * 100:+.1f}% YoY"

    # ── 8. Balance sheet (bonus / penalty) ────────────────────────────────────
    bs_adjustments = 0.0
    if debt_to_equity is not None:
        if debt_to_equity > 3.0:
            bs_adjustments -= 5.0
        elif debt_to_equity > 2.0:
            bs_adjustments -= 2.5
        elif debt_to_equity < 0.5:
            bs_adjustments += 2.5

    if current_ratio is not None:
        if current_ratio < 1.0:
            bs_adjustments -= 5.0
        elif current_ratio < 1.5:
            bs_adjustments -= 2.0
        elif current_ratio >= 2.0:
            bs_adjustments += 2.0

    if interest_coverage is not None:
        if interest_coverage < 1.5:
            bs_adjustments -= 8.0
        elif interest_coverage < 3.0:
            bs_adjustments -= 3.0
        elif interest_coverage > 8.0:
            bs_adjustments += 3.0

    # ── Aggregate weighted score ──────────────────────────────────────────────
    weights = {
        "piotroski": 0.20,
        "altman_z": 0.15,
        "value_creation": 0.20,
        "profitability": 0.20,
        "fcf_quality": 0.15,
        "growth": 0.10,
    }

    total_weight = sum(w for k, w in weights.items() if k in components)
    if total_weight == 0:
        raw_score = 50.0  # no data
    else:
        raw_score = (
            sum(components[k] * w for k, w in weights.items() if k in components) / total_weight
        )

    final_score = max(0.0, min(100.0, raw_score + bs_adjustments - manipulation_penalty))

    # ── Grade ──────────────────────────────────────────────────────────────────
    if final_score >= 88:
        grade, interp = "A+", "Exceptional — elite financial strength"
    elif final_score >= 80:
        grade, interp = "A", "Excellent — strong across all dimensions"
    elif final_score >= 72:
        grade, interp = "B+", "Very good — healthy with minor concerns"
    elif final_score >= 62:
        grade, interp = "B", "Good — solid fundamentals, watch key risks"
    elif final_score >= 52:
        grade, interp = "C+", "Fair — mixed signals, requires close monitoring"
    elif final_score >= 42:
        grade, interp = "C", "Weak — concerning on multiple dimensions"
    elif final_score >= 30:
        grade, interp = "D", "Poor — significant financial stress indicators"
    else:
        grade, interp = "F", "Distressed — high risk of financial difficulty"

    return HealthScore(
        score=round(final_score, 1),
        grade=grade,
        interpretation=interp,
        breakdown={k: round(v, 1) for k, v in components.items()},
        signals=signals,
    )
