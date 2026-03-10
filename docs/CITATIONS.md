# Citations and Academic References

All formulas in fin-ratios are grounded in published academic research or
established industry practice. This document provides:
1. The original paper for each composite/model-based ratio
2. Industry sources for practitioner ratios
3. Interpretation benchmarks

---

## Composite Scoring Models

### Piotroski F-Score
**Citation:** Piotroski, J.D. (2000). Value Investing: The Use of Historical Financial Statement
Information to Separate Winners from Losers. *Journal of Accounting Research*, 38(Supplement), 1–41.

**Summary:** Tested on high book-to-market stocks from 1976–1996. Buying F-Score ≥ 8 and shorting
F-Score ≤ 2 produced 23% annual hedge returns. The score uses 9 binary signals across profitability,
leverage/liquidity, and operating efficiency.

**Interpretation:**
| Score | Meaning |
|-------|---------|
| 8–9 | Strong — high probability of price appreciation |
| 6–7 | Good — healthy fundamentals |
| 3–5 | Neutral — mixed signals |
| 0–2 | Weak — short-selling candidate |

---

### Altman Z-Score
**Citation:** Altman, E.I. (1968). Financial Ratios, Discriminant Analysis and the Prediction of
Corporate Bankruptcy. *The Journal of Finance*, 23(4), 589–609.

**Formula:** Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5

**Variables:**
- X1 = Working Capital / Total Assets
- X2 = Retained Earnings / Total Assets
- X3 = EBIT / Total Assets
- X4 = Market Cap / Total Liabilities (or Book Equity for Z')
- X5 = Revenue / Total Assets

**Variants:**
- **Z (1968):** Public manufacturing companies. Thresholds: Safe > 2.99, Distress < 1.81
- **Z' (1983):** Private companies (uses book equity for X4). Safe > 2.9, Distress < 1.23
- **Z'' (1995):** Non-manufacturing / emerging markets. Safe > 2.6, Distress < 1.1

**Accuracy:** ~72% correct classification in original sample; widely validated in subsequent research.

**Note:** Altman (2013) revisited the model and found it still performs well, though its accuracy
has declined somewhat as capital markets have evolved. Best used as one input, not the sole criterion.

---

### Beneish M-Score
**Citation:** Beneish, M.D. (1999). The Detection of Earnings Manipulation.
*Financial Analysts Journal*, 55(5), 24–36.

**Formula:** M = -4.84 + 0.920×DSRI + 0.528×GMI + 0.404×AQI + 0.892×SGI
                   + 0.115×DEPI − 0.172×SGAI + 4.679×TATA − 0.327×LVGI

**Threshold:** M > −2.22 suggests earnings manipulation is likely.

**Historical accuracy:** ~76% correctly identified manipulators; false positive rate ~17%.

**Famous application:** The model flagged Enron's financials well before the 2001 scandal.
Researchers at Cornell University published this finding.

**Variable guide:**
| Variable | What it measures | Red flag direction |
|----------|-----------------|-------------------|
| DSRI | Receivables growing faster than sales | > 1.0 |
| GMI | Gross margin deteriorating | > 1.0 |
| AQI | Non-productive assets increasing | > 1.0 |
| SGI | Sales growth (incentive to maintain via manipulation) | > 1.0 |
| DEPI | Depreciation slowing (boosting earnings) | > 1.0 |
| SGAI | SG&A expenses rising faster than sales | > 1.0 |
| TATA | High accruals (NI >> OCF) | > 0 |
| LVGI | Leverage increasing | > 1.0 |

---

### Ohlson O-Score
**Citation:** Ohlson, J.A. (1980). Financial Ratios and the Probabilistic Prediction of Bankruptcy.
*Journal of Accounting Research*, 18(1), 109–131.

**Advantage over Altman:** Returns a probability (0–1) via logistic regression, not just a zone.
Doesn't require market data (uses only book values).

**Variables:** SIZE (log of assets), TLTA, WCTA, CLCA, OENEG, NITA, FUTL, INTWO, CHIN

---

### Greenblatt Magic Formula
**Citation:** Greenblatt, J. (2005). *The Little Book That Beats the Market*. John Wiley & Sons.

**Formula:** Rank all stocks by (1) ROIC and (2) Earnings Yield (EBIT/EV).
Sum the ranks. Buy the 20–30 stocks with the lowest combined rank.

**Backtested performance (1988–2004):** ~30.8% annualized vs S&P 500 ~12.4%
(Greenblatt's own study, sample survivorship bias noted)

**Key insight:** Uses TANGIBLE capital only (excludes goodwill) to avoid penalizing
companies that grew organically vs through acquisition.

---

## Risk and Portfolio Ratios

### Sharpe Ratio
**Citation:** Sharpe, W.F. (1966). Mutual Fund Performance. *Journal of Business*, 39(1), 119–138.
**Updated:** Sharpe, W.F. (1994). The Sharpe Ratio. *Journal of Portfolio Management*, 21(1), 49–58.

**Formula:** (Rp − Rf) / σp

**Benchmarks:**
| Sharpe | Interpretation |
|--------|---------------|
| > 2.0 | Excellent (rare) |
| 1.0–2.0 | Good |
| 0.5–1.0 | Acceptable |
| < 0.5 | Poor |

**Limitation:** Assumes normally distributed returns. Penalizes both upside AND downside volatility equally.
Use Sortino Ratio when return distributions are asymmetric.

---

### Sortino Ratio
**Citation:** Sortino, F.A., & van der Meer, R. (1991). Downside Risk.
*Journal of Portfolio Management*, 17(4), 27–31.

**Formula:** (Rp − Rf) / Downside Deviation

**Advantage:** Only penalizes downside volatility (harmful volatility).
Upside surprises are not penalized — more appropriate for asymmetric return strategies.

---

### Treynor Ratio
**Citation:** Treynor, J.L. (1965). How to Rate Management of Investment Funds.
*Harvard Business Review*, 43(1), 63–75.

**Formula:** (Rp − Rf) / β

**Use case:** Compare managers who hold DIVERSIFIED portfolios (systematic risk only).
Sharpe is better for evaluating portfolios in isolation.

---

### Jensen's Alpha
**Citation:** Jensen, M.C. (1968). The Performance of Mutual Funds in the Period 1945–1964.
*Journal of Finance*, 23(2), 389–416.

**Formula:** α = Rp − [Rf + β(Rm − Rf)]

**Interpretation:** Positive alpha = outperformance attributable to skill (after adjusting for market risk).

---

### Calmar Ratio
**Citation:** Young, T.W. (1991). Calmar Ratio: A Smoother Tool. *Futures Magazine*, October.

**Formula:** Annualized Return / Maximum Drawdown

**Use case:** Widely used in managed futures / CTA (commodity trading advisor) evaluation.
Benchmarks: > 0.5 acceptable; > 1.0 good; > 3.0 excellent.

---

### Omega Ratio
**Citation:** Keating, C., & Shadwick, W.F. (2002). A Universal Performance Measure.
*Journal of Performance Measurement*, 6(3), 59–84.

**Formula:** Σ gains above threshold / Σ losses below threshold

**Key advantage:** Makes NO distributional assumptions. Automatically captures all higher moments
(skewness, kurtosis). Omega > 1 means more gain than loss relative to threshold.

---

### Value at Risk (VaR) and CVaR
**VaR Citation:** Jorion, P. (2001). *Value at Risk* (2nd ed.). McGraw-Hill.
**CVaR Citation:** Rockafellar, R.T., & Uryasev, S. (2000). Optimization of Conditional Value-at-Risk.
*Journal of Risk*, 2(3), 21–41.

**VaR types implemented:**
1. **Historical VaR:** Non-parametric, uses empirical percentile
2. **Parametric VaR:** Assumes normal distribution (fast but unrealistic for fat tails)
3. **CVaR/Expected Shortfall:** Average loss in worst scenarios — better tail risk measure

**CVaR advantage over VaR:** VaR only tells you the loss threshold at a confidence level.
CVaR tells you the average loss BEYOND that threshold. Regulators increasingly prefer CVaR.

---

### Ulcer Index
**Citation:** Martin, P., & McCann, B. (1989). *The Investor's Guide to Fidelity Funds*. John Wiley.

**Formula:** √(mean(drawdown_pct²))

**Measures:** Both depth AND duration of drawdowns (unlike max drawdown which only captures depth).
Martin Ratio = (Return − Rf) / Ulcer Index

---

## Valuation and Intrinsic Value

### Discounted Cash Flow (DCF)
**Origin:** Williams, J.B. (1938). *The Theory of Investment Value*. Harvard University Press.

**Modern references:**
- Damodaran, A. (2012). *Investment Valuation* (3rd ed.). Wiley.
- Koller, T., Goedhart, M., & Wessels, D. (2020). *Valuation* (7th ed.). Wiley/McKinsey.

**Terminal Value methods implemented:** Gordon Growth Model perpetuity.

---

### Gordon Growth Model (DDM)
**Citation:** Gordon, M.J. (1959). Dividends, Earnings, and Stock Prices.
*Review of Economics and Statistics*, 41(2), 99–105.

**Formula:** P = D1 / (r − g)

**Valid only when r > g.** Break down for firms growing faster than discount rate.

---

### Graham Number and Intrinsic Value
**Citation:** Graham, B. (1973). *The Intelligent Investor* (4th ed.). Harper & Row.
**Revised formula (1974):** Graham, B. (1974). *The Intelligent Investor* (Revised ed.). Ch. 11.

**Graham Number:** sqrt(22.5 × EPS × BVPS)
Represents maximum price a "defensive investor" should pay.
22.5 = 15 (max P/E) × 1.5 (max P/B) from Graham's criteria.

**Revised Intrinsic Value:** V* = EPS × (8.5 + 2g) × 4.4 / Y
Where 4.4 = AAA bond yield in 1962 when formula was derived.

---

### Earnings Power Value (EPV)
**Citation:** Greenwald, B., Kahn, J., Sonkin, P., & van Biema, M. (2001).
*Value Investing: From Graham to Buffett and Beyond*. Wiley.

**Formula:** NOPAT / WACC

Assumes zero growth — the most conservative intrinsic value estimate.
EPV > Book Value = good franchise (growth creates value).
EPV < Book Value = value destroyer.

---

### Tobin's Q
**Citation:** Tobin, J. (1969). A General Equilibrium Approach to Monetary Theory.
*Journal of Money, Credit and Banking*, 1(1), 15–29.

**Formula:** (Market Cap + Debt) / Total Assets

**Interpretation:** Q > 1: market values firm above replacement cost of assets (implies growth potential or franchise value).
Q < 1: trading below replacement cost.

---

## Profitability Ratios

### DuPont Analysis (3-Factor and 5-Factor)
**Origin:** Developed by Donaldson Brown at E.I. du Pont de Nemours and Company, 1920.
**Academic reference:** Soliman, M.T. (2008). The Use of DuPont Analysis by Market Participants.
*The Accounting Review*, 83(3), 823–853.

**3-Factor:** ROE = Net Margin × Asset Turnover × Equity Multiplier
**5-Factor:** ROE = (NI/EBT) × (EBT/EBIT) × (EBIT/Sales) × (Sales/Assets) × (Assets/Equity)

---

### Return on Invested Capital (ROIC)
**Key reference:** Koller, T., Goedhart, M., & Wessels, D. (2020). *Valuation* (7th ed.). Wiley/McKinsey.

ROIC vs WACC is the fundamental value creation test:
- ROIC > WACC: Each dollar of reinvestment creates value
- ROIC < WACC: Each dollar of reinvestment destroys value

---

## Liquidity Ratios

### Cash Conversion Cycle
**Citation:** Richards, V.D., & Laughlin, E.J. (1980). A Cash Conversion Cycle Approach to
Liquidity Analysis. *Financial Management*, 9(1), 32–38.

**Formula:** DSO + DIO − DPO

Negative CCC (Amazon, Costco) = customers pay before suppliers must be paid = free working capital float.

---

## Solvency Ratios

### Debt Service Coverage Ratio (DSCR)
**Industry standard:** Used by commercial banks (typically require DSCR > 1.25x for real estate).
Basel III frameworks use similar coverage metrics for leverage assessment.

---

## Sector-Specific Ratios

### Piotroski for Banks (Modifications)
Banks use Tier 1 Capital Ratio, NIM, and NPL ratio instead of standard Piotroski signals.
**Reference:** Altman, E.I., & Saunders, A. (1998). Credit Risk Measurement: Developments over the
Last 20 Years. *Journal of Banking & Finance*, 21(11-12), 1721–1742.

---

### REIT: FFO (Funds From Operations)
**Standard setter:** NAREIT (National Association of Real Estate Investment Trusts).
*Funds from Operations White Paper* (revised 2018).

FFO = Net Income + Depreciation & Amortization − Gains on Sale of Properties.
AFFO (Adjusted FFO) is considered a better proxy for distributable cash.

---

### SaaS: Rule of 40
**Origin:** Popularized by Brad Feld (2015): "The SaaS Rule of 40" — *feld.com*
**Academic study:** McKinsey & Company (2021). *The Rule of 40 for Software Companies*

> 40: Healthy balance of growth and profitability
> 60: World-class

---

### SaaS: Magic Number
**Origin:** Mark Suster, GRP Partners. Also used by Bessemer Venture Partners in State of the Cloud.

Formula: (Current Q Revenue − Prior Q Revenue) × 4 / Prior Q S&M Spend
> 0.75: Worth accelerating S&M investment
> 1.0: Exceptional GTM efficiency

---

### SaaS: Burn Multiple
**Origin:** Bessemer Venture Partners (2021). *State of the Cloud*
Popularized by David Sacks (2020): "The Burn Multiple" — *sacks.substack.com*

< 1x: Excellent | 1–1.5x: Good | 2–3x: Suspect | > 4x: Unsustainable

---

## General Textbook References

These cover the full spectrum of financial ratios:

1. **Damodaran, A. (2012).** *Investment Valuation* (3rd ed.). Wiley.
   - The definitive textbook on valuation. Covers DCF, multiples, and options.

2. **Penman, S.H. (2013).** *Financial Statement Analysis and Security Valuation* (5th ed.). McGraw-Hill.
   - Excellent on accounting quality, accruals, and profitability analysis.

3. **Koller, T., Goedhart, M., & Wessels, D. (2020).** *Valuation* (7th ed.). Wiley/McKinsey & Company.
   - The practitioner standard for corporate valuation. ROIC framework.

4. **Graham, B., & Dodd, D. (1934).** *Security Analysis*. McGraw-Hill.
   - The foundation of value investing. P/B, earnings yield, margin of safety.

5. **Graham, B. (1973).** *The Intelligent Investor* (4th ed.). Harper & Row.
   - Graham Number, intrinsic value formula.

6. **Greenwald, B., Kahn, J., Sonkin, P., & van Biema, M. (2001).**
   *Value Investing: From Graham to Buffett and Beyond*. Wiley.
   - EPV, franchise value, reproduction value.

7. **Greenblatt, J. (2005).** *The Little Book That Beats the Market*. Wiley.
   - Magic Formula: ROIC + Earnings Yield.

8. **Grinold, R.C., & Kahn, R.N. (1999).** *Active Portfolio Management* (2nd ed.). McGraw-Hill.
   - Information ratio, fundamental law of active management.

9. **Jorion, P. (2001).** *Value at Risk* (2nd ed.). McGraw-Hill.
   - The standard reference for VaR methodology.

10. **Fabozzi, F.J., & Drake, P.P. (2009).** *Finance: Capital Markets, Financial Management,
    and Investment Management*. Wiley.
    - Comprehensive reference for all traditional financial ratios.
