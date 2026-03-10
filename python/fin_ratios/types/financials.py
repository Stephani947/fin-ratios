"""Core financial statement types."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IncomeStatement:
    revenue: float
    gross_profit: float
    cogs: float
    ebit: float
    ebitda: float
    net_income: float
    interest_expense: float
    income_tax_expense: float
    ebt: float
    depreciation_and_amortization: float
    shares_outstanding: float
    shares_outstanding_diluted: Optional[float] = None
    eps: Optional[float] = None
    eps_diluted: Optional[float] = None
    research_and_development: Optional[float] = None
    sga_expense: Optional[float] = None
    period: Optional[str] = None


@dataclass
class BalanceSheet:
    # Assets
    total_assets: float
    current_assets: float
    cash: float
    accounts_receivable: float
    inventory: float
    net_ppe: float
    retained_earnings: float
    # Liabilities
    total_liabilities: float
    current_liabilities: float
    accounts_payable: float
    long_term_debt: float
    total_debt: float
    # Equity
    total_equity: float
    # Optional
    short_term_investments: Optional[float] = None
    short_term_debt: Optional[float] = None
    goodwill: Optional[float] = None
    intangible_assets: Optional[float] = None
    shares_outstanding: Optional[float] = None
    period: Optional[str] = None


@dataclass
class CashFlowStatement:
    operating_cash_flow: float
    capex: float
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    net_change_in_cash: Optional[float] = None
    stock_based_compensation: Optional[float] = None
    dividends_paid: Optional[float] = None
    debt_repayments: Optional[float] = None
    debt_issuance: Optional[float] = None
    depreciation_and_amortization: Optional[float] = None
    period: Optional[str] = None


@dataclass
class FinancialStatements:
    income: IncomeStatement
    balance: BalanceSheet
    cash_flow: CashFlowStatement
