"""
Batch compute all applicable ratios from a single data object.

Usage:
    from fin_ratios.utils.compute_all import compute_all
    from fin_ratios.fetchers.yahoo import fetch_yahoo

    data = fetch_yahoo('AAPL')
    ratios = compute_all(data)
    print(ratios['pe'])           # 28.3
    print(ratios['roic'])         # 0.55
    print(ratios['piotroski'])    # {'score': 8, 'interpretation': ...}
"""

from __future__ import annotations

from typing import Any, Optional

from fin_ratios._utils import safe_divide
import fin_ratios as _fr


def compute_all(data: Any, prior: Optional[Any] = None) -> dict[str, Any]:
    """
    Compute all applicable ratios from a fetched data object.

    Args:
        data:  Any object with financial attributes (YahooFinancialData,
               FmpFinancialData, etc.) or a plain dict.
        prior: Optional prior-period data for ratios that need year-over-year
               comparison (Piotroski, Beneish, growth ratios).

    Returns:
        Flat dict of ratio name → value. Complex ratios (Piotroski, Altman, etc.)
        are nested dicts. Returns None for unavailable or divide-by-zero cases.

    Example:
        data = fetch_yahoo('AAPL')
        r = compute_all(data)
        # r['pe'] = 28.3
        # r['altman_z'] = {'z_score': 4.8, 'zone': 'safe', ...}
        # r['piotroski'] = {'score': 8, ...}
    """
    d = _DataAccessor(data)
    result: dict[str, Any] = {}

    # ── Valuation ─────────────────────────────────────────────────────────────
    result["pe"] = _fr.pe(market_cap=d.market_cap, net_income=d.net_income)
    result["pb"] = _fr.pb(market_cap=d.market_cap, total_equity=d.total_equity)
    result["ps"] = _fr.ps(market_cap=d.market_cap, revenue=d.revenue)
    result["peg"] = (
        _fr.peg(pe_ratio=result["pe"], eps_growth_rate_pct=d.eps_growth_pct)
        if result["pe"] and d.eps_growth_pct
        else None
    )

    fcf = _fr.free_cash_flow(operating_cash_flow=d.operating_cash_flow, capex=d.capex)
    result["free_cash_flow"] = fcf
    result["p_fcf"] = (
        _fr.p_fcf(market_cap=d.market_cap, operating_cash_flow=d.operating_cash_flow, capex=d.capex)
        if d.operating_cash_flow
        else None
    )

    ev = d.enterprise_value or (d.market_cap + d.total_debt - d.cash)
    result["enterprise_value"] = ev
    result["ev_ebitda"] = _fr.ev_ebitda(ev=ev, ebitda=d.ebitda) if d.ebitda else None
    result["ev_ebit"] = _fr.ev_ebit(ev=ev, ebit=d.ebit) if d.ebit else None
    result["ev_revenue"] = _fr.ev_revenue(ev=ev, revenue=d.revenue) if d.revenue else None
    result["ev_fcf"] = _fr.ev_fcf(ev=ev, free_cash_flow=fcf) if fcf else None
    result["tobin_q"] = _fr.tobin_q(
        market_cap=d.market_cap, total_debt=d.total_debt, total_assets=d.total_assets
    )
    result["graham_number"] = (
        _fr.graham_number(
            eps=safe_divide(d.net_income, d.shares_outstanding),
            book_value_per_share=safe_divide(d.total_equity, d.shares_outstanding),
        )
        if d.shares_outstanding
        else None
    )

    # ── Profitability ─────────────────────────────────────────────────────────
    result["gross_margin"] = _fr.gross_margin(gross_profit=d.gross_profit, revenue=d.revenue)
    result["operating_margin"] = _fr.operating_margin(ebit=d.ebit, revenue=d.revenue)
    result["net_margin"] = _fr.net_profit_margin(net_income=d.net_income, revenue=d.revenue)
    result["ebitda_margin"] = (
        _fr.ebitda_margin(ebitda=d.ebitda, revenue=d.revenue) if d.ebitda else None
    )
    result["roe"] = _fr.roe(net_income=d.net_income, avg_total_equity=d.total_equity)
    result["roa"] = _fr.roa(net_income=d.net_income, avg_total_assets=d.total_assets)
    result["roce"] = _fr.roce(
        ebit=d.ebit, total_assets=d.total_assets, current_liabilities=d.current_liabilities
    )

    tax_rate = safe_divide(d.income_tax_expense, d.ebt) if d.ebt else 0.21
    nopat_val = _fr.nopat(ebit=d.ebit, tax_rate=min(max(tax_rate or 0, 0), 0.5))
    ic_val = _fr.invested_capital(total_equity=d.total_equity, total_debt=d.total_debt, cash=d.cash)
    result["nopat"] = nopat_val
    result["invested_capital"] = ic_val
    result["roic"] = _fr.roic(nopat_value=nopat_val, invested_capital=ic_val)

    # ── Cash Flow ─────────────────────────────────────────────────────────────
    result["fcf_margin"] = _fr.fcf_margin(fcf=fcf, revenue=d.revenue) if fcf else None
    result["fcf_conversion"] = _fr.fcf_conversion(fcf=fcf, net_income=d.net_income) if fcf else None
    result["ocf_to_sales"] = _fr.ocf_to_sales(
        operating_cash_flow=d.operating_cash_flow, revenue=d.revenue
    )
    result["capex_to_revenue"] = _fr.capex_to_revenue(capex=d.capex, revenue=d.revenue)
    result["fcf_yield"] = _fr.fcf_yield(fcf=fcf, market_cap=d.market_cap) if fcf else None

    # ── Liquidity ─────────────────────────────────────────────────────────────
    result["current_ratio"] = _fr.current_ratio(
        current_assets=d.current_assets, current_liabilities=d.current_liabilities
    )
    result["quick_ratio"] = _fr.quick_ratio(
        cash=d.cash,
        short_term_investments=0,
        accounts_receivable=d.accounts_receivable,
        current_liabilities=d.current_liabilities,
    )
    result["dso"] = _fr.dso(accounts_receivable=d.accounts_receivable, revenue=d.revenue)
    result["dio"] = _fr.dio(inventory=d.inventory, cogs=d.cogs) if d.cogs else None
    result["dpo"] = _fr.dpo(accounts_payable=d.accounts_payable, cogs=d.cogs) if d.cogs else None

    dso_v, dio_v, dpo_v = result["dso"], result["dio"], result["dpo"]
    result["cash_conversion_cycle"] = (
        _fr.cash_conversion_cycle(dso_days=dso_v, dio_days=dio_v or 0, dpo_days=dpo_v or 0)
        if dso_v is not None
        else None
    )

    # ── Solvency ──────────────────────────────────────────────────────────────
    result["debt_to_equity"] = _fr.debt_to_equity(
        total_debt=d.total_debt, total_equity=d.total_equity
    )
    result["net_debt_to_equity"] = _fr.net_debt_to_equity(
        total_debt=d.total_debt, cash=d.cash, total_equity=d.total_equity
    )
    result["net_debt_to_ebitda"] = (
        _fr.net_debt_to_ebitda(total_debt=d.total_debt, cash=d.cash, ebitda=d.ebitda)
        if d.ebitda
        else None
    )
    result["debt_to_assets"] = _fr.debt_to_assets(
        total_debt=d.total_debt, total_assets=d.total_assets
    )
    result["interest_coverage"] = _fr.interest_coverage_ratio(
        ebit=d.ebit, interest_expense=d.interest_expense
    )
    result["equity_multiplier"] = _fr.equity_multiplier(
        total_assets=d.total_assets, total_equity=d.total_equity
    )

    # ── Efficiency ────────────────────────────────────────────────────────────
    result["asset_turnover"] = _fr.asset_turnover(
        revenue=d.revenue, avg_total_assets=d.total_assets
    )
    result["receivables_turnover"] = _fr.receivables_turnover(
        revenue=d.revenue, avg_accounts_receivable=d.accounts_receivable
    )
    result["inventory_turnover"] = (
        _fr.inventory_turnover(cogs=d.cogs, avg_inventory=d.inventory) if d.cogs else None
    )
    result["payables_turnover"] = (
        _fr.payables_turnover(cogs=d.cogs, avg_accounts_payable=d.accounts_payable)
        if d.cogs
        else None
    )

    # ── Composite Scores ──────────────────────────────────────────────────────
    try:
        altman = _fr.altman_z_score(
            working_capital=d.current_assets - d.current_liabilities,
            retained_earnings=d.retained_earnings,
            ebit=d.ebit,
            market_cap=d.market_cap,
            total_liabilities=d.total_liabilities,
            total_assets=d.total_assets,
            revenue=d.revenue,
        )
        result["altman_z"] = altman
    except Exception:
        result["altman_z"] = None

    # Prior-period ratios (Piotroski, Beneish, growth)
    if prior is not None:
        p = _DataAccessor(prior)
        try:
            result["piotroski"] = _fr.piotroski_f_score(
                current_net_income=d.net_income,
                current_total_assets=d.total_assets,
                current_operating_cf=d.operating_cash_flow,
                current_long_term_debt=d.long_term_debt,
                current_current_assets=d.current_assets,
                current_current_liabilities=d.current_liabilities,
                current_shares_outstanding=d.shares_outstanding,
                current_gross_profit=d.gross_profit,
                current_revenue=d.revenue,
                prior_net_income=p.net_income,
                prior_total_assets=p.total_assets,
                prior_long_term_debt=p.long_term_debt,
                prior_current_assets=p.current_assets,
                prior_current_liabilities=p.current_liabilities,
                prior_shares_outstanding=p.shares_outstanding,
                prior_gross_profit=p.gross_profit,
                prior_revenue=p.revenue,
            )
        except Exception:
            result["piotroski"] = None

        try:
            from fin_ratios.ratios.composite import montier_c_score

            result["montier_c"] = montier_c_score(
                current_net_income=d.net_income,
                current_operating_cash_flow=d.operating_cash_flow,
                current_accounts_receivable=d.accounts_receivable,
                current_revenue=d.revenue,
                current_inventory=d.inventory,
                current_cogs=d.cogs or d.revenue - d.gross_profit,
                current_cash=d.cash,
                current_total_assets=d.total_assets,
                current_long_term_debt=d.long_term_debt,
                current_gross_profit=d.gross_profit,
                prior_accounts_receivable=p.accounts_receivable,
                prior_revenue=p.revenue,
                prior_inventory=p.inventory,
                prior_cogs=p.cogs or p.revenue - p.gross_profit,
                prior_cash=p.cash,
                prior_total_assets=p.total_assets,
                prior_long_term_debt=p.long_term_debt,
                prior_gross_profit=p.gross_profit,
            )
        except Exception:
            result["montier_c"] = None

        try:
            result["revenue_growth"] = _fr.revenue_growth(
                current_revenue=d.revenue, prior_revenue=p.revenue
            )
        except Exception:
            result["revenue_growth"] = None

    # ── Health Score ──────────────────────────────────────────────────────────
    try:
        from fin_ratios.utils.health_score import health_score

        piotroski_score_val = result.get("piotroski", {})
        piotroski_int = (
            piotroski_score_val.get("score") if isinstance(piotroski_score_val, dict) else None
        )
        altman_z_val = result.get("altman_z", {})
        altman_z_float = altman_z_val.get("z_score") if isinstance(altman_z_val, dict) else None
        result["health_score"] = health_score(
            piotroski_score=piotroski_int,
            altman_z=altman_z_float,
            roic=result.get("roic"),
            net_margin=result.get("net_margin"),
            gross_margin=result.get("gross_margin"),
            fcf_conversion=result.get("fcf_conversion"),
            fcf_margin=result.get("fcf_margin"),
            debt_to_equity=result.get("debt_to_equity"),
            current_ratio=result.get("current_ratio"),
            interest_coverage=result.get("interest_coverage"),
        )
    except Exception:
        result["health_score"] = None

    return result


class _DataAccessor:
    """Uniform attribute access for any data object or dict."""

    def __init__(self, data: Any):
        self._data = data

    def __getattr__(self, name: str) -> float:
        d = object.__getattribute__(self, "_data")
        if isinstance(d, dict):
            return d.get(name, 0.0) or 0.0
        return getattr(d, name, 0.0) or 0.0
