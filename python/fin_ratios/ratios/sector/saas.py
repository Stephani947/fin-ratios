"""SaaS and subscription business metrics."""
from __future__ import annotations
from typing import Optional
from fin_ratios._utils import safe_divide


def rule_of_40(revenue_growth_rate_pct: float, fcf_margin_pct: float) -> float:
    """
    Rule of 40.
    Formula: Revenue Growth Rate (%) + FCF Margin (%)
    > 40: Healthy balance of growth and profitability
    > 60: World-class SaaS
    Reference: Introduce by Brad Feld (2015), popularized by McKinsey & Bessemer.
    """
    return revenue_growth_rate_pct + fcf_margin_pct

rule_of_40.formula = "Revenue Growth Rate % + FCF Margin %"  # type: ignore[attr-defined]
rule_of_40.description = "> 40 = healthy SaaS. > 60 = world-class."  # type: ignore[attr-defined]


def magic_number(
    current_quarter_revenue: float,
    prior_quarter_revenue: float,
    prior_quarter_sm_spend: float,
) -> Optional[float]:
    """
    Magic Number (SaaS Go-to-Market Efficiency).
    Formula: (Current Q Revenue - Prior Q Revenue) × 4 / Prior Q S&M Spend
    > 0.75: Efficient — good time to increase S&M spend
    > 1.0: Exceptional — pedal to the metal on S&M
    < 0.5: Inefficient — fix funnel before adding spend
    Reference: Widely used in SaaS venture capital; attributed to Suster/Bessemer.
    """
    net_new_arr_annualized = (current_quarter_revenue - prior_quarter_revenue) * 4
    return safe_divide(net_new_arr_annualized, prior_quarter_sm_spend)

magic_number.formula = "(Current Q Revenue - Prior Q Revenue) × 4 / Prior Q S&M Spend"  # type: ignore[attr-defined]
magic_number.description = "> 0.75 = efficient. > 1.0 = exceptional GTM efficiency."  # type: ignore[attr-defined]


def net_revenue_retention(
    beginning_arr: float,
    expansion: float,
    churn: float,
    contraction: float,
) -> Optional[float]:
    """
    Net Revenue Retention (NRR) / Net Dollar Retention (NDR).
    Formula: (Beginning ARR + Expansion - Churn - Contraction) / Beginning ARR
    > 100%: Existing customers generate MORE revenue over time (net expansion)
    < 100%: Revenue is declining from existing base even without new customers
    Benchmark: Top SaaS: 120-140% (Snowflake, Datadog); Median: ~105%; < 100% = problem
    """
    return safe_divide(
        beginning_arr + expansion - churn - contraction,
        beginning_arr,
    )

net_revenue_retention.formula = "(Beginning ARR + Expansion - Churn - Contraction) / Beginning ARR"  # type: ignore[attr-defined]
net_revenue_retention.description = "> 100% = existing customers expand. Elite SaaS: 120-140%."  # type: ignore[attr-defined]


def gross_revenue_retention(
    beginning_arr: float,
    churn: float,
    contraction: float,
) -> Optional[float]:
    """
    Gross Revenue Retention (GRR).
    Formula: (Beginning ARR - Churn - Contraction) / Beginning ARR
    Best case = 100% (no losses at all). Expansion not included.
    Benchmark: Good SaaS > 90%; Enterprise SaaS > 95%
    """
    return safe_divide(beginning_arr - churn - contraction, beginning_arr)

gross_revenue_retention.formula = "(Beginning ARR - Churn - Contraction) / Beginning ARR"  # type: ignore[attr-defined]
gross_revenue_retention.description = "Retention without expansion. Max = 100%. > 90% is good."  # type: ignore[attr-defined]


def customer_acquisition_cost(
    sales_and_marketing_spend: float,
    new_customers_acquired: float,
) -> Optional[float]:
    """
    Customer Acquisition Cost (CAC).
    Formula: S&M Spend / New Customers Acquired
    """
    return safe_divide(sales_and_marketing_spend, new_customers_acquired)

customer_acquisition_cost.formula = "Sales & Marketing Spend / New Customers Acquired"  # type: ignore[attr-defined]
customer_acquisition_cost.description = "Cost to acquire one new customer."  # type: ignore[attr-defined]


def customer_lifetime_value(
    avg_monthly_revenue_per_customer: float,
    gross_margin: float,
    monthly_churn_rate: float,
) -> Optional[float]:
    """
    Customer Lifetime Value (LTV / CLV).
    Formula: (Avg Monthly Revenue × Gross Margin) / Monthly Churn Rate
    """
    if monthly_churn_rate <= 0:
        return None
    return safe_divide(avg_monthly_revenue_per_customer * gross_margin, monthly_churn_rate)

customer_lifetime_value.formula = "(Avg Monthly Revenue × Gross Margin) / Monthly Churn Rate"  # type: ignore[attr-defined]
customer_lifetime_value.description = "Expected gross profit per customer over their lifetime."  # type: ignore[attr-defined]


def ltv_cac_ratio(ltv: float, cac: float) -> Optional[float]:
    """
    LTV/CAC Ratio.
    > 3x: Healthy — worth acquiring customers
    < 1x: Losing money on every customer acquired
    Benchmark: Best-in-class SaaS: 5-10x+
    """
    return safe_divide(ltv, cac)

ltv_cac_ratio.formula = "Customer LTV / Customer Acquisition Cost"  # type: ignore[attr-defined]
ltv_cac_ratio.description = "> 3x is healthy. < 1x = losing money per customer."  # type: ignore[attr-defined]


def cac_payback_period(
    cac: float,
    avg_monthly_revenue_per_customer: float,
    gross_margin_pct: float,
) -> Optional[float]:
    """
    CAC Payback Period (months).
    Formula: CAC / (Avg Monthly Revenue × Gross Margin %)
    Benchmark: < 12 months = excellent; 12-24 = acceptable; > 24 = concerning
    """
    monthly_margin = avg_monthly_revenue_per_customer * gross_margin_pct
    return safe_divide(cac, monthly_margin)

cac_payback_period.formula = "CAC / (Avg Monthly Revenue × Gross Margin %)"  # type: ignore[attr-defined]
cac_payback_period.description = "Months to recoup customer acquisition cost. < 12 is excellent."  # type: ignore[attr-defined]


def burn_multiple(net_burn_rate: float, net_new_arr: float) -> Optional[float]:
    """
    Burn Multiple.
    Formula: Net Cash Burn / Net New ARR
    How much cash burned per $1 of new ARR added.
    < 1x: Excellent (burning less than generating)
    1-1.5x: Good
    > 2x: Concerning
    > 4x: Unsustainable
    Reference: Bessemer Venture Partners State of the Cloud report.
    """
    return safe_divide(net_burn_rate, net_new_arr)

burn_multiple.formula = "Net Burn Rate / Net New ARR"  # type: ignore[attr-defined]
burn_multiple.description = "Cash spent per $1 of new ARR. < 1 = excellent, > 2 = concerning."  # type: ignore[attr-defined]


def saas_quick_ratio(
    new_mrr: float,
    expansion_mrr: float,
    churned_mrr: float,
    contraction_mrr: float,
) -> Optional[float]:
    """
    SaaS Quick Ratio (Mamoon Hamid / Social Capital).
    Formula: (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
    > 4: Excellent growth efficiency
    2-4: Good
    1-2: Mediocre
    < 1: Shrinking
    Reference: Hamid, M. (2015). The SaaS Quick Ratio. Social Capital blog.
    """
    gained = new_mrr + expansion_mrr
    lost = churned_mrr + contraction_mrr
    return safe_divide(gained, lost)

saas_quick_ratio.formula = "(New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)"  # type: ignore[attr-defined]
saas_quick_ratio.description = "Growth efficiency. > 4 = excellent. < 1 = shrinking."  # type: ignore[attr-defined]


def arr_per_fte(arr: float, full_time_employees: float) -> Optional[float]:
    """
    ARR per Full-Time Employee.
    Benchmark: > $200K = world-class; $100-200K = good; < $100K = room for improvement
    """
    return safe_divide(arr, full_time_employees)

arr_per_fte.formula = "ARR / Full-Time Employees"  # type: ignore[attr-defined]
arr_per_fte.description = "Revenue productivity per employee. > $200K is world-class."  # type: ignore[attr-defined]
