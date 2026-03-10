"""
fin-ratios CLI — instant terminal analysis for any stock ticker.

Usage:
    fin-ratios AAPL
    fin-ratios MSFT --full
    fin-ratios NVDA --json
    fin-ratios AAPL MSFT GOOGL --compare
    python -m fin_ratios AAPL
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# ── helpers ───────────────────────────────────────────────────────────────────

def _color(text: str, code: str) -> str:
    """Wrap text in ANSI color if stdout is a terminal."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

def _green(t: str) -> str: return _color(t, "32")
def _red(t: str)  -> str: return _color(t, "31")
def _yellow(t: str) -> str: return _color(t, "33")
def _bold(t: str)  -> str: return _color(t, "1")
def _dim(t: str)   -> str: return _color(t, "2")
def _cyan(t: str)  -> str: return _color(t, "36")

def _fmt(val: float | None, pct: bool = False, mult: bool = False,
         decimals: int = 2, prefix: str = "") -> str:
    if val is None:
        return _dim("N/A")
    if pct:
        return f"{prefix}{val * 100:.{decimals}f}%"
    if mult:
        return f"{prefix}{val:.{decimals}f}x"
    return f"{prefix}{val:.{decimals}f}"

def _traffic_light(val: float | None, good_above: float | None = None,
                   warn_above: float | None = None,
                   good_below: float | None = None,
                   warn_below: float | None = None) -> str:
    """Return green/yellow/red dot based on thresholds."""
    if val is None:
        return _dim("•")
    if good_above is not None and val >= good_above:
        return _green("●")
    if good_below is not None and val <= good_below:
        return _green("●")
    if warn_above is not None and val >= warn_above:
        return _yellow("●")
    if warn_below is not None and val <= warn_below:
        return _yellow("●")
    return _red("●")

def _row(label: str, value: str, indicator: str = "", width: int = 30) -> str:
    label_padded = label.ljust(width)
    return f"  {label_padded} {value:<14} {indicator}"

def _section(title: str, width: int = 56) -> str:
    bar = "─" * width
    return f"\n{_bold(_cyan(title))}\n{_dim(bar)}"

def _big_number(n: float) -> str:
    if abs(n) >= 1e12:
        return f"${n / 1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"${n / 1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n / 1e6:.2f}M"
    return f"${n:.0f}"


# ── main analysis ─────────────────────────────────────────────────────────────

def analyze(ticker: str, full: bool = False) -> dict[str, Any]:
    """Fetch data and compute all ratios. Returns a dict for JSON output."""
    try:
        from fin_ratios.fetchers.yahoo import fetch_yahoo
    except ImportError:
        print(_red("ERROR: fetchers not installed. Run: pip install 'fin-ratios[fetchers]'"))
        sys.exit(1)

    print(_dim(f"  Fetching {ticker} from Yahoo Finance..."), end="\r")

    try:
        d = fetch_yahoo(ticker)
    except Exception as e:
        print(_red(f"ERROR: Could not fetch data for {ticker}: {e}"))
        sys.exit(1)

    from fin_ratios import (
        pe, forward_pe, pb, ps, p_fcf, ev_ebitda, ev_ebit,
        gross_margin, operating_margin, net_profit_margin, ebitda_margin,
        roe, roa, roic, roce,
        nopat, invested_capital,
        free_cash_flow, fcf_margin, fcf_conversion,
        current_ratio, quick_ratio,
        debt_to_equity, net_debt_to_ebitda, interest_coverage_ratio,
        asset_turnover, revenue_growth,
        piotroski_f_score, altman_z_score, beneish_m_score,
        graham_number,
    )

    inc = d.income
    bal = d.balance
    cf = d.cashflow
    mkt = d.market_data

    # ── compute all ratios ────────────────────────────────────────────────────

    pe_val         = pe(market_cap=mkt.market_cap, net_income=inc.net_income)
    fwd_pe_val     = forward_pe(price=mkt.price, forward_eps=mkt.forward_eps) if mkt.forward_eps else None
    pb_val         = pb(market_cap=mkt.market_cap, total_equity=bal.total_equity)
    ps_val         = ps(market_cap=mkt.market_cap, revenue=inc.revenue)

    fcf_val        = free_cash_flow(operating_cash_flow=cf.operating_cash_flow, capex=cf.capex)
    p_fcf_val      = p_fcf(market_cap=mkt.market_cap, free_cash_flow=fcf_val) if fcf_val else None
    ev_val         = mkt.enterprise_value or (mkt.market_cap + bal.total_debt - bal.cash)
    ev_ebitda_val  = ev_ebitda(enterprise_value=ev_val, ebitda=inc.ebitda) if inc.ebitda else None
    ev_ebit_val    = ev_ebit(enterprise_value=ev_val, ebit=inc.ebit) if inc.ebit else None

    gm_val         = gross_margin(gross_profit=inc.gross_profit, revenue=inc.revenue)
    om_val         = operating_margin(ebit=inc.ebit, revenue=inc.revenue)
    nm_val         = net_profit_margin(net_income=inc.net_income, revenue=inc.revenue)
    em_val         = ebitda_margin(ebitda=inc.ebitda, revenue=inc.revenue) if inc.ebitda else None
    roe_val        = roe(net_income=inc.net_income, total_equity=bal.total_equity)
    roa_val        = roa(net_income=inc.net_income, total_assets=bal.total_assets)
    ic_val         = invested_capital(total_equity=bal.total_equity, total_debt=bal.total_debt, cash=bal.cash)
    nopat_val      = nopat(ebit=inc.ebit, tax_rate=(inc.income_tax_expense / inc.ebt) if inc.ebt else 0.21)
    roic_val       = roic(nopat=nopat_val, invested_capital=ic_val) if nopat_val and ic_val else None
    roce_val       = roce(ebit=inc.ebit, total_assets=bal.total_assets, current_liabilities=bal.current_liabilities)

    fcf_margin_val = fcf_margin(free_cash_flow=fcf_val, revenue=inc.revenue) if fcf_val else None
    fcf_conv_val   = fcf_conversion(free_cash_flow=fcf_val, net_income=inc.net_income) if fcf_val else None

    curr_val       = current_ratio(current_assets=bal.current_assets, current_liabilities=bal.current_liabilities)
    quick_val      = quick_ratio(cash=bal.cash, short_term_investments=bal.short_term_investments or 0,
                                  accounts_receivable=bal.accounts_receivable,
                                  current_liabilities=bal.current_liabilities)
    de_val         = debt_to_equity(total_debt=bal.total_debt, total_equity=bal.total_equity)
    nd_ebitda_val  = net_debt_to_ebitda(total_debt=bal.total_debt, cash=bal.cash, ebitda=inc.ebitda) if inc.ebitda else None
    icr_val        = interest_coverage_ratio(ebit=inc.ebit, interest_expense=inc.interest_expense)

    at_val         = asset_turnover(revenue=inc.revenue, total_assets=bal.total_assets)

    gn_val         = graham_number(
        eps=inc.eps or (inc.net_income / bal.shares_outstanding if bal.shares_outstanding else None),
        book_value_per_share=bal.total_equity / bal.shares_outstanding if bal.shares_outstanding else None,
    ) if bal.shares_outstanding else None

    # ── composite scores (need prior year data — use estimates where missing) ─
    piotroski_val = None
    altman_val    = None
    beneish_val   = None

    try:
        altman_val = altman_z_score(
            working_capital=bal.current_assets - bal.current_liabilities,
            retained_earnings=bal.retained_earnings,
            ebit=inc.ebit,
            market_cap=mkt.market_cap,
            total_liabilities=bal.total_liabilities,
            total_assets=bal.total_assets,
            revenue=inc.revenue,
        )
    except Exception:
        pass

    result: dict[str, Any] = {
        "ticker": ticker.upper(),
        "name": getattr(mkt, "name", ticker.upper()),
        "price": mkt.price,
        "market_cap": mkt.market_cap,
        "enterprise_value": ev_val,
        "valuation": {
            "pe": pe_val, "forward_pe": fwd_pe_val, "pb": pb_val,
            "ps": ps_val, "p_fcf": p_fcf_val,
            "ev_ebitda": ev_ebitda_val, "ev_ebit": ev_ebit_val,
            "graham_number": gn_val,
        },
        "profitability": {
            "gross_margin": gm_val, "operating_margin": om_val,
            "net_margin": nm_val, "ebitda_margin": em_val,
            "roe": roe_val, "roa": roa_val, "roic": roic_val, "roce": roce_val,
        },
        "cash_flow": {
            "free_cash_flow": fcf_val, "fcf_margin": fcf_margin_val,
            "fcf_conversion": fcf_conv_val,
            "operating_cash_flow": cf.operating_cash_flow,
        },
        "liquidity": {"current_ratio": curr_val, "quick_ratio": quick_val},
        "solvency": {
            "debt_to_equity": de_val, "net_debt_ebitda": nd_ebitda_val,
            "interest_coverage": icr_val,
        },
        "efficiency": {"asset_turnover": at_val},
        "composite": {
            "altman_z": altman_val,
            "piotroski": piotroski_val,
            "beneish": beneish_val,
        },
    }
    return result


# ── display ───────────────────────────────────────────────────────────────────

def display(ticker: str, data: dict[str, Any], full: bool = False) -> None:
    v   = data["valuation"]
    pro = data["profitability"]
    cf  = data["cash_flow"]
    liq = data["liquidity"]
    sol = data["solvency"]
    eff = data["efficiency"]
    com = data["composite"]

    print()
    name_str = data.get("name") or ticker.upper()
    print(_bold(f"  {name_str} ({_cyan(ticker.upper())})"))
    price_str = f"${data['price']:.2f}" if data["price"] else "N/A"
    mc_str    = _big_number(data["market_cap"]) if data["market_cap"] else "N/A"
    ev_str    = _big_number(data["enterprise_value"]) if data["enterprise_value"] else "N/A"
    print(f"  Price: {_bold(price_str)}   Market Cap: {_bold(mc_str)}   EV: {_bold(ev_str)}")

    # ── Valuation ─────────────────────────────────────────────────────────────
    print(_section("VALUATION"))
    pe_ind  = _traffic_light(v["pe"], warn_below=10, good_below=20, warn_above=30)
    print(_row("P/E (trailing)",       _fmt(v["pe"]), pe_ind))
    if v["forward_pe"]:
        print(_row("P/E (forward)",    _fmt(v["forward_pe"])))
    pb_ind  = _traffic_light(v["pb"], good_below=1.5, warn_below=3)
    print(_row("P/B",                  _fmt(v["pb"]), pb_ind))
    print(_row("P/S",                  _fmt(v["ps"])))
    print(_row("P/FCF",                _fmt(v["p_fcf"])))
    print(_row("EV/EBITDA",            _fmt(v["ev_ebitda"])))
    print(_row("EV/EBIT",              _fmt(v["ev_ebit"])))
    if v["graham_number"]:
        gn = v["graham_number"]
        price = data["price"]
        margin = (1 - price / gn) if gn and price else None
        gn_ind = _green("●") if margin and margin > 0.2 else (_yellow("●") if margin and margin > 0 else _red("●"))
        margin_str = f"  ({_fmt(margin, pct=True)} margin of safety)" if margin else ""
        print(_row("Graham Number", f"${gn:.2f}{margin_str}", gn_ind))

    # ── Profitability ─────────────────────────────────────────────────────────
    print(_section("PROFITABILITY"))
    print(_row("Gross Margin",         _fmt(pro["gross_margin"], pct=True),
               _traffic_light(pro["gross_margin"], good_above=0.40, warn_above=0.20)))
    print(_row("Operating Margin",     _fmt(pro["operating_margin"], pct=True),
               _traffic_light(pro["operating_margin"], good_above=0.15, warn_above=0.05)))
    print(_row("Net Margin",           _fmt(pro["net_margin"], pct=True),
               _traffic_light(pro["net_margin"], good_above=0.10, warn_above=0.03)))
    if pro["ebitda_margin"]:
        print(_row("EBITDA Margin",    _fmt(pro["ebitda_margin"], pct=True)))
    print(_row("ROE",                  _fmt(pro["roe"], pct=True),
               _traffic_light(pro["roe"], good_above=0.15, warn_above=0.10)))
    print(_row("ROA",                  _fmt(pro["roa"], pct=True),
               _traffic_light(pro["roa"], good_above=0.10, warn_above=0.05)))
    if pro["roic"]:
        print(_row("ROIC",             _fmt(pro["roic"], pct=True),
                   _traffic_light(pro["roic"], good_above=0.15, warn_above=0.08)))
    if pro["roce"]:
        print(_row("ROCE",             _fmt(pro["roce"], pct=True)))

    # ── Cash Flow ─────────────────────────────────────────────────────────────
    print(_section("CASH FLOW"))
    ocf_str = _big_number(cf["operating_cash_flow"]) if cf["operating_cash_flow"] else "N/A"
    print(_row("Operating Cash Flow",  ocf_str))
    fcf_str = _big_number(cf["free_cash_flow"]) if cf["free_cash_flow"] else "N/A"
    fcf_ind = _traffic_light(cf["free_cash_flow"], good_above=0.0)
    print(_row("Free Cash Flow",       fcf_str, fcf_ind))
    print(_row("FCF Margin",           _fmt(cf["fcf_margin"], pct=True),
               _traffic_light(cf["fcf_margin"], good_above=0.10, warn_above=0.05)))
    print(_row("FCF Conversion",       _fmt(cf["fcf_conversion"], mult=True),
               _traffic_light(cf["fcf_conversion"], good_above=0.8, warn_above=0.5)))

    # ── Balance Sheet Health ──────────────────────────────────────────────────
    print(_section("BALANCE SHEET HEALTH"))
    print(_row("Current Ratio",        _fmt(liq["current_ratio"], mult=True),
               _traffic_light(liq["current_ratio"], good_above=2.0, warn_above=1.0)))
    print(_row("Quick Ratio",          _fmt(liq["quick_ratio"], mult=True),
               _traffic_light(liq["quick_ratio"], good_above=1.5, warn_above=1.0)))
    print(_row("Debt / Equity",        _fmt(sol["debt_to_equity"], mult=True),
               _traffic_light(sol["debt_to_equity"], good_below=0.5, warn_below=1.0)))
    if sol["net_debt_ebitda"]:
        print(_row("Net Debt / EBITDA",_fmt(sol["net_debt_ebitda"], mult=True),
                   _traffic_light(sol["net_debt_ebitda"], good_below=1.0, warn_below=2.5)))
    if sol["interest_coverage"]:
        print(_row("Interest Coverage",_fmt(sol["interest_coverage"], mult=True),
                   _traffic_light(sol["interest_coverage"], good_above=5.0, warn_above=2.0)))

    # ── Composite Scores ──────────────────────────────────────────────────────
    print(_section("COMPOSITE SCORES"))
    az = com["altman_z"]
    if az:
        zone_color = _green if az["zone"] == "safe" else (_yellow if az["zone"] == "grey" else _red)
        zone_icon  = "● Safe" if az["zone"] == "safe" else ("● Grey Zone" if az["zone"] == "grey" else "● Distress")
        print(_row("Altman Z-Score",  f"{az['z']:.2f}  {zone_color(zone_icon)}"))

    pf = com["piotroski"]
    if pf:
        score_color = _green if pf["score"] >= 7 else (_yellow if pf["score"] >= 4 else _red)
        print(_row("Piotroski F-Score", score_color(f"{pf['score']}/9") + f"  {pf['interpretation']}"))

    bm = com["beneish"]
    if bm:
        flag = _red("FLAGGED") if bm["manipulation_likely"] else _green("Clean")
        print(_row("Beneish M-Score", f"{bm['m_score']:.2f}  {flag}"))

    if not any([az, pf, bm]):
        print(_dim("  (Install fetchers and run with --full for composite scores)"))

    print()
    print(_dim("  Legend: ● Good  ● Caution  ● Concern   (thresholds are general guidelines)"))
    print()


# ── comparison mode ───────────────────────────────────────────────────────────

def display_comparison(tickers: list[str], datasets: list[dict[str, Any]]) -> None:
    COL = 14
    header = "  " + "Metric".ljust(26)
    for d in datasets:
        header += d["ticker"].upper().rjust(COL)
    print(_bold(header))
    print(_dim("  " + "─" * (26 + COL * len(datasets))))

    def row(label: str, key_path: list[str]) -> None:
        line = "  " + label.ljust(26)
        for d in datasets:
            val = d
            for k in key_path:
                val = val.get(k) if isinstance(val, dict) else None
            if val is None:
                line += _dim("N/A").rjust(COL + 9)
            elif isinstance(val, float):
                pct = "margin" in label.lower() or "roe" in label.lower() or "roa" in label.lower() or "roic" in label.lower()
                txt = f"{val * 100:.1f}%" if pct else f"{val:.2f}"
                line += txt.rjust(COL)
            else:
                line += str(val).rjust(COL)
        print(line)

    print(_bold("\n  Valuation"))
    row("P/E",          ["valuation", "pe"])
    row("EV/EBITDA",    ["valuation", "ev_ebitda"])
    row("P/B",          ["valuation", "pb"])
    row("P/FCF",        ["valuation", "p_fcf"])

    print(_bold("\n  Profitability"))
    row("Gross Margin %",   ["profitability", "gross_margin"])
    row("Operating Margin %",["profitability", "operating_margin"])
    row("Net Margin %",     ["profitability", "net_margin"])
    row("ROE %",            ["profitability", "roe"])
    row("ROIC %",           ["profitability", "roic"])

    print(_bold("\n  Cash Flow"))
    row("FCF Margin %",     ["cash_flow", "fcf_margin"])
    row("FCF Conversion",   ["cash_flow", "fcf_conversion"])

    print(_bold("\n  Balance Sheet"))
    row("Current Ratio",    ["liquidity", "current_ratio"])
    row("D/E",              ["solvency", "debt_to_equity"])
    row("Net Debt/EBITDA",  ["solvency", "net_debt_ebitda"])
    print()


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fin-ratios",
        description="Instant financial ratio analysis for any stock ticker.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fin-ratios AAPL
  fin-ratios MSFT --full
  fin-ratios NVDA --json
  fin-ratios AAPL MSFT GOOGL --compare
        """,
    )
    parser.add_argument("tickers", nargs="+", help="Stock ticker(s), e.g. AAPL MSFT GOOGL")
    parser.add_argument("--full",    action="store_true", help="Show all ratios including composite scores")
    parser.add_argument("--json",    action="store_true", help="Output raw JSON instead of table")
    parser.add_argument("--compare", action="store_true", help="Side-by-side comparison of multiple tickers")
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers]

    if args.compare or len(tickers) > 1:
        datasets = []
        for t in tickers:
            print(_dim(f"  Fetching {t}..."), end="\r", flush=True)
            datasets.append(analyze(t, full=args.full))
        print(" " * 40, end="\r")  # clear line
        display_comparison(tickers, datasets)
        return

    ticker = tickers[0]
    data = analyze(ticker, full=args.full)

    if args.json:
        def _serialize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            return obj
        print(json.dumps(_serialize(data), indent=2, default=str))
        return

    print(" " * 40, end="\r")  # clear fetching line
    display(ticker, data, full=args.full)


if __name__ == "__main__":
    main()
