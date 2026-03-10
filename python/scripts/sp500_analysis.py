"""
S&P 500 Financial Ratio Analysis
=================================
Fetches real financial data for all S&P 500 companies via Yahoo Finance
and computes 30+ key ratios including Piotroski F-Score, Altman Z-Score,
and Beneish M-Score.

Usage:
    pip install yfinance pandas
    python scripts/sp500_analysis.py

Output:
    sp500_ratios.csv          — All ratios for all companies
    sp500_top_piotroski.csv   — Top 20 by Piotroski F-Score
    sp500_distressed.csv      — Companies in Altman distress zone
    sp500_manipulation.csv    — Companies flagged by Beneish M-Score

Runtime: ~30-45 minutes for all 503 companies (rate-limited).
Use --sample 50 for a quick 50-company test run.
"""
import sys
import time
import json
import argparse
import csv
from pathlib import Path
from typing import Optional

# Add parent to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Missing dependencies. Run: pip install yfinance pandas")
    sys.exit(1)

from fin_ratios import (
    pe, forward_pe, peg, pb, ps, p_fcf,
    enterprise_value, ev_ebitda, ev_ebit, ev_revenue,
    graham_number,
    gross_margin, operating_margin, ebitda_margin, net_profit_margin,
    roe, roa, roic, nopat as compute_nopat,
    invested_capital as compute_ic,
    current_ratio, quick_ratio, dso, dio, dpo, cash_conversion_cycle,
    debt_to_equity, net_debt_to_ebitda, interest_coverage_ratio,
    asset_turnover, inventory_turnover,
    free_cash_flow, fcf_yield, fcf_margin, fcf_conversion,
    revenue_growth,
    piotroski_f_score, altman_z_score, beneish_m_score,
)


def get_sp500_tickers() -> list[str]:
    """Fetch S&P 500 tickers from Wikipedia."""
    try:
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
            flavor="html5lib",
        )
        df = tables[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        print(f"Loaded {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers
    except Exception as e:
        print(f"Wikipedia fetch failed ({e}), using fallback list")
        # Hardcoded top-50 fallback
        return [
            "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "LLY",
            "AVGO", "TSLA", "JPM", "UNH", "V", "XOM", "MA", "JNJ", "HD",
            "PG", "COST", "ABBV", "MRK", "CVX", "WMT", "BAC", "KO", "NFLX",
            "PEP", "ORCL", "TMO", "ADBE", "AMD", "WFC", "CRM", "LIN", "TXN",
            "PM", "INTC", "RTX", "UNP", "NEE", "HON", "INTU", "AMAT", "SPGI",
            "GS", "CAT", "MS", "ISRG", "ELV", "BLK",
        ]


def fetch_ticker_data(ticker: str) -> Optional[dict]:
    """Fetch and parse all financial data for a single ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        if not info.get("marketCap"):
            return None

        # ── Basic market data ────────────────────────────────────────────
        price = float(info.get("currentPrice") or info.get("regularMarketPrice") or 0)
        market_cap = float(info.get("marketCap") or 0)
        ev = float(info.get("enterpriseValue") or 0)
        shares = float(info.get("sharesOutstanding") or 0)

        # ── Income statement (from info dict — fastest) ───────────────────
        revenue = float(info.get("totalRevenue") or 0)
        ebitda_val = float(info.get("ebitda") or 0)
        net_income = float(info.get("netIncomeToCommon") or 0)
        total_debt = float(info.get("totalDebt") or 0)
        cash = float(info.get("totalCash") or 0)
        ocf = float(info.get("operatingCashflow") or 0)
        capex_val = abs(float(info.get("capitalExpenditures") or 0))

        # ── Fetch full statements for composite scores ────────────────────
        inc_curr = inc_prior = bal_curr = bal_prior = cf_curr = {}

        try:
            income_stmt = stock.income_stmt
            if income_stmt is not None and not income_stmt.empty and len(income_stmt.columns) >= 2:
                c0, c1 = income_stmt.columns[0], income_stmt.columns[1]
                inc_curr = _parse_income(income_stmt, c0)
                inc_prior = _parse_income(income_stmt, c1)
        except Exception:
            pass

        try:
            bs = stock.balance_sheet
            if bs is not None and not bs.empty and len(bs.columns) >= 2:
                c0, c1 = bs.columns[0], bs.columns[1]
                bal_curr = _parse_balance(bs, c0)
                bal_prior = _parse_balance(bs, c1)
        except Exception:
            pass

        try:
            cf_stmt = stock.cash_flow
            if cf_stmt is not None and not cf_stmt.empty:
                cf_curr = _parse_cashflow(cf_stmt, cf_stmt.columns[0])
        except Exception:
            pass

        # ── Use full statements where available ───────────────────────────
        gross_profit = bal_curr.get("gross_profit") or inc_curr.get("gross_profit") or (
            revenue * float(info.get("grossMargins") or 0)
        )
        ebit_val = inc_curr.get("ebit") or (
            revenue * float(info.get("operatingMargins") or 0)
        )
        interest_exp = abs(inc_curr.get("interest_expense") or 0)
        if ocf == 0:
            ocf = cf_curr.get("ocf") or 0
        if capex_val == 0:
            capex_val = cf_curr.get("capex") or 0

        total_assets = bal_curr.get("total_assets") or 0
        current_assets = bal_curr.get("current_assets") or 0
        current_liab = bal_curr.get("current_liabilities") or 0
        total_liab = bal_curr.get("total_liabilities") or 0
        total_equity = bal_curr.get("total_equity") or 0
        retained_earnings = bal_curr.get("retained_earnings") or 0
        accounts_receivable = bal_curr.get("accounts_receivable") or 0
        inventory_val = bal_curr.get("inventory") or 0
        accounts_payable = bal_curr.get("accounts_payable") or 0
        long_term_debt = bal_curr.get("long_term_debt") or 0

        # Approximate ebit if missing
        if not ebit_val and ebitda_val:
            da = inc_curr.get("depreciation_amortization") or (ebitda_val * 0.15)
            ebit_val = ebitda_val - da

        # Effective tax rate (approximate)
        income_tax = inc_curr.get("income_tax") or 0
        ebt_val = inc_curr.get("ebt") or (ebit_val - interest_exp)
        tax_rate = (income_tax / ebt_val) if ebt_val > 0 else 0.21

        # ── Compute ratios ────────────────────────────────────────────────
        fcf_val = free_cash_flow(ocf, capex_val)
        nopat_val = compute_nopat(ebit_val, tax_rate) if ebit_val else 0
        ic_val = compute_ic(total_equity, total_debt, cash) if total_equity else 0
        cogs_val = inc_curr.get("cogs") or (revenue - gross_profit)
        wc = current_assets - current_liab

        # DSO / DIO / DPO
        dso_val = dso(accounts_receivable, revenue) if revenue else None
        dio_val = dio(inventory_val, cogs_val) if cogs_val else None
        dpo_val = dpo(accounts_payable, cogs_val) if cogs_val else None
        ccc_val = cash_conversion_cycle(dso_val or 0, dio_val or 0, dpo_val or 0) if all([dso_val, dio_val, dpo_val]) else None

        # Revenue growth (YoY)
        rev_prior = inc_prior.get("revenue") or 0
        rev_growth = revenue_growth(revenue, rev_prior) if rev_prior else None

        # Altman Z-Score
        altman = None
        if all([total_assets, total_liab, revenue, market_cap]):
            altman = altman_z_score(
                working_capital=wc,
                retained_earnings=retained_earnings,
                ebit=ebit_val,
                market_cap=market_cap,
                total_liabilities=total_liab,
                total_assets=total_assets,
                revenue=revenue,
            )

        # Piotroski F-Score
        piotroski = None
        if bal_curr and bal_prior and inc_curr:
            try:
                piotroski = piotroski_f_score(
                    current_net_income=net_income,
                    current_total_assets=total_assets,
                    current_operating_cf=ocf,
                    current_long_term_debt=long_term_debt,
                    current_current_assets=current_assets,
                    current_current_liabilities=current_liab,
                    current_shares_outstanding=shares,
                    current_gross_profit=gross_profit,
                    current_revenue=revenue,
                    prior_net_income=inc_prior.get("net_income") or 0,
                    prior_total_assets=bal_prior.get("total_assets") or 0,
                    prior_long_term_debt=bal_prior.get("long_term_debt") or 0,
                    prior_current_assets=bal_prior.get("current_assets") or 0,
                    prior_current_liabilities=bal_prior.get("current_liabilities") or 0,
                    prior_shares_outstanding=shares,  # Conservative — use same
                    prior_gross_profit=inc_prior.get("gross_profit") or 0,
                    prior_revenue=inc_prior.get("revenue") or 0,
                )
            except Exception:
                pass

        # Beneish M-Score
        beneish = None
        if inc_curr and inc_prior and bal_curr and bal_prior:
            try:
                beneish = beneish_m_score(
                    c_revenue=revenue,
                    c_accounts_receivable=accounts_receivable,
                    c_gross_profit=gross_profit,
                    c_total_assets=total_assets,
                    c_depreciation=inc_curr.get("depreciation_amortization") or 0,
                    c_pp_gross=bal_curr.get("net_ppe") or 0,
                    c_sga_expense=inc_curr.get("sga") or 0,
                    c_total_debt=total_debt,
                    c_net_income=net_income,
                    c_cash_from_ops=ocf,
                    p_revenue=inc_prior.get("revenue") or 0,
                    p_accounts_receivable=bal_prior.get("accounts_receivable") or 0,
                    p_gross_profit=inc_prior.get("gross_profit") or 0,
                    p_total_assets=bal_prior.get("total_assets") or 0,
                    p_depreciation=inc_prior.get("depreciation_amortization") or 0,
                    p_pp_gross=bal_prior.get("net_ppe") or 0,
                    p_sga_expense=inc_prior.get("sga") or 0,
                    p_total_debt=bal_prior.get("long_term_debt") or 0,
                )
            except Exception:
                pass

        # ── Assemble result row ───────────────────────────────────────────
        row = {
            "ticker": ticker,
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector") or "",
            "industry": info.get("industry") or "",
            "market_cap_b": round(market_cap / 1e9, 2),
            # Valuation
            "pe_ratio": _r(info.get("trailingPE")),
            "forward_pe": _r(info.get("forwardPE")),
            "pb_ratio": _r(info.get("priceToBook")),
            "ps_ratio": _r(info.get("priceToSalesTrailing12Months")),
            "ev_ebitda": _r(info.get("enterpriseToEbitda")),
            "ev_revenue": _r(info.get("enterpriseToRevenue")),
            "p_fcf": _r(p_fcf(market_cap, ocf, capex_val)),
            "fcf_yield_pct": _r(_pct(fcf_yield(fcf_val, market_cap))),
            "graham_number": _r(graham_number(
                float(info.get("trailingEps") or 0),
                (total_equity / shares) if shares else 0,
            )),
            # Profitability
            "gross_margin_pct": _r(_pct(info.get("grossMargins"))),
            "operating_margin_pct": _r(_pct(info.get("operatingMargins"))),
            "net_margin_pct": _r(_pct(info.get("profitMargins"))),
            "ebitda_margin_pct": _r(_pct(ebitda_margin(ebitda_val, revenue))),
            "roe_pct": _r(_pct(info.get("returnOnEquity"))),
            "roa_pct": _r(_pct(info.get("returnOnAssets"))),
            "roic_pct": _r(_pct(roic(nopat_val, ic_val))),
            # Liquidity
            "current_ratio_val": _r(info.get("currentRatio")),
            "quick_ratio_val": _r(info.get("quickRatio")),
            "dso_days": _r(dso_val),
            "dio_days": _r(dio_val),
            "dpo_days": _r(dpo_val),
            "ccc_days": _r(ccc_val),
            # Solvency
            "net_debt_ebitda": _r(net_debt_to_ebitda(total_debt, cash, ebitda_val)),
            "debt_equity": _r(info.get("debtToEquity")),
            "interest_coverage": _r(interest_coverage_ratio(ebit_val, interest_exp)),
            # Cash flow
            "fcf_margin_pct": _r(_pct(fcf_margin(fcf_val, revenue))),
            "fcf_conversion": _r(fcf_conversion(fcf_val, net_income)),
            "ocf_b": round(ocf / 1e9, 2),
            "fcf_b": round(fcf_val / 1e9, 2),
            # Growth
            "revenue_growth_pct": _r(_pct(rev_growth)),
            "earnings_growth_pct": _r(_pct(info.get("earningsGrowth"))),
            # Composite scores
            "piotroski_score": piotroski["score"] if piotroski else None,
            "piotroski_label": piotroski["recommendation"] if piotroski else None,
            "altman_z": altman["z_score"] if altman else None,
            "altman_zone": altman["zone"] if altman else None,
            "beneish_m": beneish["m_score"] if beneish else None,
            "beneish_manipulation": beneish["manipulation_likely"] if beneish else None,
            # Beta
            "beta": _r(info.get("beta")),
            "dividend_yield_pct": _r(_pct(info.get("dividendYield"))),
        }

        return row

    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def _parse_income(df, col) -> dict:
    return {
        "revenue": _row(df, col, ["Total Revenue", "Revenues"]),
        "gross_profit": _row(df, col, ["Gross Profit"]),
        "cogs": _row(df, col, ["Cost Of Revenue", "Cost of Revenue"]),
        "ebit": _row(df, col, ["EBIT", "Operating Income"]),
        "net_income": _row(df, col, ["Net Income"]),
        "interest_expense": abs(_row(df, col, ["Interest Expense"])),
        "income_tax": _row(df, col, ["Tax Provision", "Income Tax Expense"]),
        "ebt": _row(df, col, ["Pretax Income"]),
        "depreciation_amortization": _row(df, col, ["Reconciled Depreciation", "Depreciation"]),
        "sga": _row(df, col, ["Selling General Administrative", "SGA"]),
    }


def _parse_balance(df, col) -> dict:
    return {
        "total_assets": _row(df, col, ["Total Assets"]),
        "current_assets": _row(df, col, ["Current Assets", "Total Current Assets"]),
        "cash": _row(df, col, ["Cash And Cash Equivalents"]),
        "accounts_receivable": _row(df, col, ["Accounts Receivable", "Net Receivables"]),
        "inventory": _row(df, col, ["Inventory"]),
        "net_ppe": _row(df, col, ["Net PPE", "Property Plant And Equipment Net"]),
        "total_liabilities": _row(df, col, ["Total Liabilities Net Minority Interest", "Total Liabilities"]),
        "current_liabilities": _row(df, col, ["Current Liabilities", "Total Current Liabilities"]),
        "accounts_payable": _row(df, col, ["Accounts Payable"]),
        "long_term_debt": _row(df, col, ["Long Term Debt"]),
        "total_equity": _row(df, col, ["Stockholders Equity", "Total Stockholders Equity"]),
        "retained_earnings": _row(df, col, ["Retained Earnings"]),
    }


def _parse_cashflow(df, col) -> dict:
    return {
        "ocf": _row(df, col, ["Operating Cash Flow"]),
        "capex": abs(_row(df, col, ["Capital Expenditure", "Purchases Of PPE"])),
    }


def _row(df, col, keys) -> float:
    for k in keys:
        try:
            v = df.loc[k, col]
            if v is not None and v == v:  # not NaN
                return float(v)
        except (KeyError, TypeError):
            continue
    return 0.0


def _r(v) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
        return round(f, 4) if f == f else None
    except (TypeError, ValueError):
        return None


def _pct(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v) * 100
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description="Compute financial ratios for S&P 500")
    parser.add_argument("--sample", type=int, default=0,
                        help="Only process N tickers (0 = all)")
    parser.add_argument("--output-dir", default=".", help="Output directory for CSV files")
    parser.add_argument("--delay", type=float, default=0.3,
                        help="Delay between API calls in seconds")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("fin-ratios: S&P 500 Financial Analysis")
    print("=" * 60)

    tickers = get_sp500_tickers()
    if args.sample > 0:
        tickers = tickers[:args.sample]
        print(f"Sample mode: processing {args.sample} tickers")

    results = []
    errors = []
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        if i % 10 == 0:
            pct = (i / total) * 100
            print(f"Progress: {i}/{total} ({pct:.0f}%) — {ticker}")

        row = fetch_ticker_data(ticker)
        if row:
            if "error" in row:
                errors.append(row)
            else:
                results.append(row)
        time.sleep(args.delay)

    print(f"\nCompleted: {len(results)} successful, {len(errors)} errors")

    if not results:
        print("No results to save.")
        return

    # ── Save main results ─────────────────────────────────────────────────────
    df = pd.DataFrame(results)
    main_file = output_dir / "sp500_ratios.csv"
    df.to_csv(main_file, index=False)
    print(f"\nSaved: {main_file}")

    # ── Top Piotroski ─────────────────────────────────────────────────────────
    piotroski_df = df[df["piotroski_score"].notna()].sort_values(
        "piotroski_score", ascending=False
    ).head(20)
    piotroski_file = output_dir / "sp500_top_piotroski.csv"
    piotroski_df[["ticker", "company_name", "sector", "piotroski_score",
                  "piotroski_label", "pe_ratio", "roic_pct", "fcf_yield_pct",
                  "gross_margin_pct"]].to_csv(piotroski_file, index=False)
    print(f"Saved: {piotroski_file}")

    # ── Altman Distress Zone ──────────────────────────────────────────────────
    distress_df = df[df["altman_zone"] == "distress"].sort_values("altman_z")
    distress_file = output_dir / "sp500_distressed.csv"
    distress_df[["ticker", "company_name", "sector", "altman_z",
                 "altman_zone", "net_debt_ebitda", "interest_coverage",
                 "market_cap_b"]].to_csv(distress_file, index=False)
    print(f"Saved: {distress_file} ({len(distress_df)} companies)")

    # ── Beneish Manipulation Flags ────────────────────────────────────────────
    manipulation_df = df[df["beneish_manipulation"] == True].sort_values(
        "beneish_m", ascending=False
    )
    manipulation_file = output_dir / "sp500_manipulation_flags.csv"
    manipulation_df[["ticker", "company_name", "sector", "beneish_m",
                     "beneish_manipulation", "net_margin_pct",
                     "market_cap_b"]].to_csv(manipulation_file, index=False)
    print(f"Saved: {manipulation_file} ({len(manipulation_df)} flags)")

    # ── Summary statistics ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("S&P 500 Summary Statistics")
    print("=" * 60)
    numeric_cols = ["pe_ratio", "pb_ratio", "ev_ebitda", "gross_margin_pct",
                    "operating_margin_pct", "roe_pct", "roic_pct",
                    "net_debt_ebitda", "fcf_yield_pct", "piotroski_score"]
    summary = df[numeric_cols].describe().round(2)
    print(summary.to_string())

    print("\n--- By Piotroski Score ---")
    if "piotroski_score" in df.columns:
        pscore_dist = df["piotroski_score"].value_counts().sort_index()
        for score, count in pscore_dist.items():
            bar = "█" * (count // 5)
            print(f"  F-Score {score:2.0f}: {count:3d} companies {bar}")

    print("\n--- Altman Zone Distribution ---")
    if "altman_zone" in df.columns:
        zone_dist = df["altman_zone"].value_counts()
        for zone, count in zone_dist.items():
            print(f"  {zone:8s}: {count:3d} companies")

    print("\nDone! Check the output files for full results.")


if __name__ == "__main__":
    main()
