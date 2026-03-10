"""
Composite multi-factor scoring systems.

These are the rarest and most valuable ratios — entire academic papers
encapsulated into single scores.

References:
- Piotroski, J.D. (2000). Value Investing: The Use of Historical Financial Statement
  Information to Separate Winners from Losers. Journal of Accounting Research, 38, 1–41.
- Altman, E.I. (1968). Financial Ratios, Discriminant Analysis and the Prediction of
  Corporate Bankruptcy. The Journal of Finance, 23(4), 589–609.
- Beneish, M.D. (1999). The Detection of Earnings Manipulation.
  Financial Analysts Journal, 55(5), 24–36.
- Greenblatt, J. (2005). The Little Book That Beats the Market. Wiley.
- Ohlson, J.A. (1980). Financial Ratios and the Probabilistic Prediction of Bankruptcy.
  Journal of Accounting Research, 18(1), 109–131.
"""
from __future__ import annotations
import math
from typing import Optional
from fin_ratios._utils import safe_divide


# ── Piotroski F-Score ─────────────────────────────────────────────────────────

def piotroski_f_score(
    current_net_income: float,
    current_total_assets: float,
    current_operating_cf: float,
    current_long_term_debt: float,
    current_current_assets: float,
    current_current_liabilities: float,
    current_shares_outstanding: float,
    current_gross_profit: float,
    current_revenue: float,
    prior_net_income: float,
    prior_total_assets: float,
    prior_long_term_debt: float,
    prior_current_assets: float,
    prior_current_liabilities: float,
    prior_shares_outstanding: float,
    prior_gross_profit: float,
    prior_revenue: float,
) -> dict:
    """
    Piotroski F-Score (0–9).

    9 binary signals across 3 groups:
    PROFITABILITY (F1-F4):
      F1: ROA > 0 (positive return on assets)
      F2: Operating Cash Flow > 0
      F3: ROA improved year-over-year
      F4: Accruals: Operating CF > Net Income (cash earnings quality)

    LEVERAGE / LIQUIDITY / DILUTION (F5-F7):
      F5: Long-term leverage decreased
      F6: Current ratio improved
      F7: No new share issuance (no dilution)

    OPERATING EFFICIENCY (F8-F9):
      F8: Gross margin improved
      F9: Asset turnover improved

    Interpretation:
      8-9: Strong — high probability of positive returns (Piotroski showed ~23% outperformance)
      0-2: Weak — candidate for short selling
      3-7: Neutral / mixed signals

    Reference: Piotroski, J.D. (2000). Value Investing: The Use of Historical Financial
               Statement Information to Separate Winners from Losers.
               Journal of Accounting Research, 38(Supplement), 1–41.
    """
    # Compute ratios
    roa_c = safe_divide(current_net_income, current_total_assets) or 0
    roa_p = safe_divide(prior_net_income, prior_total_assets) or 0
    lev_c = safe_divide(current_long_term_debt, current_total_assets) or 0
    lev_p = safe_divide(prior_long_term_debt, prior_total_assets) or 0
    cr_c = safe_divide(current_current_assets, current_current_liabilities) or 0
    cr_p = safe_divide(prior_current_assets, prior_current_liabilities) or 0
    gm_c = safe_divide(current_gross_profit, current_revenue) or 0
    gm_p = safe_divide(prior_gross_profit, prior_revenue) or 0
    at_c = safe_divide(current_revenue, current_total_assets) or 0
    at_p = safe_divide(prior_revenue, prior_total_assets) or 0

    signals = {
        # Profitability
        "f1_roa_positive": roa_c > 0,
        "f2_ocf_positive": current_operating_cf > 0,
        "f3_roa_improving": roa_c > roa_p,
        "f4_accruals_quality": current_operating_cf > current_net_income,
        # Leverage / Liquidity / Dilution
        "f5_lower_leverage": lev_c < lev_p,
        "f6_higher_liquidity": cr_c > cr_p,
        "f7_no_dilution": current_shares_outstanding <= prior_shares_outstanding,
        # Operating Efficiency
        "f8_higher_gross_margin": gm_c > gm_p,
        "f9_higher_asset_turnover": at_c > at_p,
    }

    score = sum(1 for v in signals.values() if v)

    if score >= 8:
        interpretation = f"Strong ({score}/9): High financial strength — potential outperformer"
    elif score >= 6:
        interpretation = f"Good ({score}/9): Healthy fundamentals"
    elif score >= 4:
        interpretation = f"Neutral ({score}/9): Mixed signals — further analysis needed"
    else:
        interpretation = f"Weak ({score}/9): Multiple red flags — high financial risk"

    return {
        "score": score,
        "signals": signals,
        "interpretation": interpretation,
        "recommendation": "buy" if score >= 8 else ("short" if score <= 2 else "neutral"),
    }

piotroski_f_score.formula = "9 binary signals: Profitability (4) + Leverage/Liquidity (3) + Efficiency (2)"  # type: ignore[attr-defined]
piotroski_f_score.description = "F-Score 0-9. >= 8 = strong buy signal. <= 2 = short candidate."  # type: ignore[attr-defined]


# ── Altman Z-Score ────────────────────────────────────────────────────────────

def altman_z_score(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    total_assets: float,
    revenue: float,
) -> Optional[dict]:
    """
    Altman Z-Score (Public Manufacturing Companies).

    Formula: Z = 1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5

    Variables:
      X1 = Working Capital / Total Assets (liquidity)
      X2 = Retained Earnings / Total Assets (cumulative profitability / age)
      X3 = EBIT / Total Assets (operating efficiency)
      X4 = Market Cap / Total Liabilities (solvency / market perception)
      X5 = Revenue / Total Assets (asset efficiency)

    Zones:
      Z > 2.99 → Safe Zone (low bankruptcy risk)
      1.81 < Z < 2.99 → Grey Zone (uncertain)
      Z < 1.81 → Distress Zone (high bankruptcy probability)

    Note: Z' model (private) uses Book Value instead of Market Cap for X4.

    Reference: Altman, E.I. (1968). Financial Ratios, Discriminant Analysis and the
               Prediction of Corporate Bankruptcy. Journal of Finance, 23(4), 589–609.
    Accuracy: ~72% for 2-year prediction in original study; widely validated since.
    """
    if total_assets == 0 or total_liabilities == 0:
        return None

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = revenue / total_assets

    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    if z > 2.99:
        zone, risk = "safe", "Low"
    elif z > 1.81:
        zone, risk = "grey", "Moderate"
    else:
        zone, risk = "distress", "High"

    return {
        "z_score": round(z, 3),
        "zone": zone,
        "bankruptcy_risk": risk,
        "x1_working_capital": round(x1, 4),
        "x2_retained_earnings": round(x2, 4),
        "x3_ebit": round(x3, 4),
        "x4_market_vs_liabilities": round(x4, 4),
        "x5_revenue": round(x5, 4),
        "interpretation": f"Z-Score {z:.2f}: {zone.title()} zone — {risk} bankruptcy risk",
    }

altman_z_score.formula = "1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5"  # type: ignore[attr-defined]
altman_z_score.description = "Bankruptcy predictor. Safe > 2.99, Distress < 1.81."  # type: ignore[attr-defined]


# ── Beneish M-Score ───────────────────────────────────────────────────────────

def beneish_m_score(
    # Current year
    c_revenue: float,
    c_accounts_receivable: float,
    c_gross_profit: float,
    c_total_assets: float,
    c_depreciation: float,
    c_pp_gross: float,
    c_sga_expense: float,
    c_total_debt: float,
    c_net_income: float,
    c_cash_from_ops: float,
    # Prior year
    p_revenue: float,
    p_accounts_receivable: float,
    p_gross_profit: float,
    p_total_assets: float,
    p_depreciation: float,
    p_pp_gross: float,
    p_sga_expense: float,
    p_total_debt: float,
) -> Optional[dict]:
    """
    Beneish M-Score (8-variable earnings manipulation detection model).

    Formula:
      M = -4.84 + 0.920×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI
          + 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI

    Variables:
      DSRI  = Days Sales Receivable Index (receivables growing faster than sales → manipulation)
      GMI   = Gross Margin Index (deteriorating margins → pressure to manipulate)
      AQI   = Asset Quality Index (increasing non-productive assets → channel stuffing)
      SGI   = Sales Growth Index (high growth → incentive to maintain via manipulation)
      DEPI  = Depreciation Index (lowering depreciation → boosting reported income)
      SGAI  = SG&A Expense Index (rising overhead vs sales → efficiency concerns)
      TATA  = Total Accruals to Total Assets (high accruals = low earnings quality)
      LVGI  = Leverage Index (increasing debt → pressure to manage earnings)

    Threshold: M-Score > -2.22 suggests LIKELY manipulation.
    Accuracy: ~76% correctly identified manipulators in Beneish's sample.

    Reference: Beneish, M.D. (1999). The Detection of Earnings Manipulation.
               Financial Analysts Journal, 55(5), 24–36.
    """
    if p_revenue == 0 or p_total_assets == 0:
        return None

    # DSRI: Days Sales Receivable Index
    dsri_num = safe_divide(c_accounts_receivable, c_revenue)
    dsri_den = safe_divide(p_accounts_receivable, p_revenue)
    dsri = safe_divide(dsri_num, dsri_den)

    # GMI: Gross Margin Index (prior / current — deterioration raises score)
    gmi_num = safe_divide(p_gross_profit, p_revenue)
    gmi_den = safe_divide(c_gross_profit, c_revenue)
    gmi = safe_divide(gmi_num, gmi_den)

    # AQI: Asset Quality Index
    aqi_c = (1 - (c_accounts_receivable + c_pp_gross) / c_total_assets) if c_total_assets else None
    aqi_p = (1 - (p_accounts_receivable + p_pp_gross) / p_total_assets) if p_total_assets else None
    aqi = safe_divide(aqi_c, aqi_p)

    # SGI: Sales Growth Index
    sgi = safe_divide(c_revenue, p_revenue)

    # DEPI: Depreciation Index (prior / current — slowing depreciation raises score)
    depi_c = safe_divide(c_depreciation, c_depreciation + c_pp_gross)
    depi_p = safe_divide(p_depreciation, p_depreciation + p_pp_gross)
    depi = safe_divide(depi_p, depi_c)

    # SGAI: SG&A Expense Index
    sgai_num = safe_divide(c_sga_expense, c_revenue)
    sgai_den = safe_divide(p_sga_expense, p_revenue)
    sgai = safe_divide(sgai_num, sgai_den)

    # TATA: Total Accruals to Total Assets (accruals = NI - CFO)
    tata = safe_divide(c_net_income - c_cash_from_ops, c_total_assets)

    # LVGI: Leverage Index
    lvgi_c = safe_divide(c_total_debt, c_total_assets)
    lvgi_p = safe_divide(p_total_debt, p_total_assets)
    lvgi = safe_divide(lvgi_c, lvgi_p)

    if any(v is None for v in [dsri, gmi, aqi, sgi, depi, sgai, tata, lvgi]):
        return None

    m = (-4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi  # type: ignore
         + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)  # type: ignore

    manipulation_likely = m > -2.22

    return {
        "m_score": round(m, 3),
        "manipulation_likely": manipulation_likely,
        "threshold": -2.22,
        "variables": {
            "dsri": round(dsri, 3),  # type: ignore
            "gmi": round(gmi, 3),    # type: ignore
            "aqi": round(aqi, 3),    # type: ignore
            "sgi": round(sgi, 3),    # type: ignore
            "depi": round(depi, 3),  # type: ignore
            "sgai": round(sgai, 3),  # type: ignore
            "tata": round(tata, 4),  # type: ignore
            "lvgi": round(lvgi, 3),  # type: ignore
        },
        "interpretation": (
            f"M-Score {m:.2f} > -2.22: ⚠ POSSIBLE EARNINGS MANIPULATION"
            if manipulation_likely
            else f"M-Score {m:.2f} ≤ -2.22: No strong sign of manipulation"
        ),
    }

beneish_m_score.formula = "-4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI + 0.115×DEPI - 0.172×SGAI + 4.679×TATA - 0.327×LVGI"  # type: ignore[attr-defined]
beneish_m_score.description = "Earnings manipulation detector. M > -2.22 = possible manipulation."  # type: ignore[attr-defined]


# ── Greenblatt Magic Formula ──────────────────────────────────────────────────

def magic_formula(
    ebit: float,
    net_working_capital: float,
    net_fixed_assets: float,
    enterprise_value: float,
) -> dict:
    """
    Greenblatt Magic Formula.

    Two-factor ranking system: buy companies with high ROIC AND high earnings yield.

    ROIC = EBIT / (Net Working Capital + Net Fixed Assets)
    Earnings Yield = EBIT / Enterprise Value

    Strategy: Rank all companies by both metrics, sum the ranks, buy the top 20-30.
    Backtested annual return: ~30.8% from 1988-2004 vs S&P 500 ~12.4%.

    Reference: Greenblatt, J. (2005). The Little Book That Beats the Market. Wiley.
    Note: Tangible capital = NWC + Net Fixed Assets (excludes goodwill intentionally).
    """
    tangible_capital = net_working_capital + net_fixed_assets
    roic = safe_divide(ebit, tangible_capital)
    earnings_yield = safe_divide(ebit, enterprise_value)
    return {
        "roic": roic,
        "earnings_yield": earnings_yield,
        "roic_pct": (roic * 100) if roic is not None else None,
        "earnings_yield_pct": (earnings_yield * 100) if earnings_yield is not None else None,
        "formula_score": (
            "Rank by ROIC + Rank by Earnings Yield (lower combined rank = buy)"
        ),
    }

magic_formula.formula = "ROIC = EBIT / Tangible Capital;  Earnings Yield = EBIT / EV"  # type: ignore[attr-defined]
magic_formula.description = "Greenblatt's 2-factor system: high ROIC + high earnings yield = buy."  # type: ignore[attr-defined]


# ── Ohlson O-Score ────────────────────────────────────────────────────────────

def ohlson_o_score(
    total_assets: float,
    total_liabilities: float,
    current_assets: float,
    current_liabilities: float,
    net_income: float,
    prior_net_income: float,
    operating_cash_flow: float,
    working_capital: float,
    gnp_index: float = 1.0,
) -> Optional[dict]:
    """
    Ohlson O-Score (Logistic Regression Bankruptcy Model).

    Outputs a probability of bankruptcy (0.0–1.0).
    Unlike Altman's linear discriminant, uses logistic regression → direct probability.

    Formula:
      T = -1.32 - 0.407×SIZE + 6.03×TLTA - 1.43×WCTA + 0.0757×CLCA
          - 1.72×OENEG - 2.37×NITA - 1.83×FUTL + 0.285×INTWO - 0.521×CHIN

    Variables:
      SIZE  = log(Total Assets / GNP index)
      TLTA  = Total Liabilities / Total Assets
      WCTA  = Working Capital / Total Assets
      CLCA  = Current Liabilities / Current Assets
      OENEG = 1 if total liabilities > total assets, else 0
      NITA  = Net Income / Total Assets
      FUTL  = Operating Cash Flow / Total Liabilities
      INTWO = 1 if net income was negative last 2 years, else 0
      CHIN  = (NI_t - NI_t-1) / (|NI_t| + |NI_t-1|)

    Threshold: O > 0.5 → high bankruptcy risk

    Reference: Ohlson, J.A. (1980). Financial Ratios and the Probabilistic Prediction
               of Bankruptcy. Journal of Accounting Research, 18(1), 109–131.
    """
    if total_assets <= 0:
        return None

    size = math.log(total_assets / gnp_index)
    tlta = total_liabilities / total_assets
    wcta = working_capital / total_assets
    clca = safe_divide(current_liabilities, current_assets) or 0
    oeneg = 1 if total_liabilities > total_assets else 0
    nita = net_income / total_assets
    futl = safe_divide(operating_cash_flow, total_liabilities) or 0
    intwo = 1 if net_income < 0 and prior_net_income < 0 else 0
    denom = abs(net_income) + abs(prior_net_income)
    chin = safe_divide(net_income - prior_net_income, denom) or 0

    t = (-1.32 - 0.407 * size + 6.03 * tlta - 1.43 * wcta + 0.0757 * clca
         - 1.72 * oeneg - 2.37 * nita - 1.83 * futl + 0.285 * intwo - 0.521 * chin)

    probability = 1 / (1 + math.exp(-t))

    return {
        "o_score": round(t, 3),
        "bankruptcy_probability": round(probability, 4),
        "bankruptcy_probability_pct": round(probability * 100, 2),
        "high_risk": probability > 0.5,
        "interpretation": (
            f"Bankruptcy probability: {probability * 100:.1f}% — "
            + ("HIGH RISK" if probability > 0.5 else "Low risk")
        ),
    }

ohlson_o_score.formula = "Logistic regression of 9 financial variables → P(bankruptcy)"  # type: ignore[attr-defined]
ohlson_o_score.description = "Outputs bankruptcy probability 0-1. > 0.5 = high risk."  # type: ignore[attr-defined]
