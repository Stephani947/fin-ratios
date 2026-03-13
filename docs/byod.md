# Bring Your Own Data

All scoring and ratio functions accept plain Python dicts, dataclasses, or any object with matching attributes. No fetcher is required.

## Data Shape

Each annual record should contain as many of the fields below as are available. All fields are optional — functions return `None` when required inputs are missing.

### Python field names (snake\_case)

| Field | Description |
|-------|-------------|
| `revenue` | Total revenue / net sales |
| `gross_profit` | Revenue minus COGS |
| `ebit` | Operating income (EBIT) |
| `ebitda` | EBIT + D&A |
| `net_income` | Net income attributable to shareholders |
| `operating_cash_flow` | Cash from operations |
| `capex` | Capital expenditures (positive number) |
| `free_cash_flow` | OCF − capex (auto-computed if omitted) |
| `total_assets` | Total assets |
| `total_equity` | Shareholders' equity |
| `total_debt` | Short + long term debt |
| `cash` | Cash and cash equivalents |
| `short_term_investments` | Marketable securities |
| `accounts_receivable` | Trade receivables |
| `inventory` | Inventory balance |
| `accounts_payable` | Trade payables |
| `current_assets` | Total current assets |
| `current_liabilities` | Total current liabilities |
| `depreciation` | D&A charged in the period |
| `income_tax_expense` | Income taxes paid / accrued |
| `ebt` | Earnings before taxes |
| `interest_expense` | Interest charges |
| `shares_outstanding` | Diluted shares outstanding |
| `dividends_paid` | Cash dividends (positive number) |
| `buybacks` | Share repurchases (positive number) |
| `r_and_d` | Research & development expense |
| `invested_capital` | IC override (else computed from equity + debt − cash) |

### TypeScript field names (camelCase)

Same names in camelCase: `revenue`, `grossProfit`, `ebit`, `ebitda`, `netIncome`, `operatingCashFlow`, `capex`, `totalAssets`, `totalEquity`, `totalDebt`, `cash`, `accountsReceivable`, `inventory`, `accountsPayable`, `currentAssets`, `currentLiabilities`, `depreciation`, `incomeTaxExpense`, `ebt`, `interestExpense`, `sharesOutstanding`, `dividendsPaid`, `buybacks`, `rAndD`.

## Minimal Example

=== "Python"

    ```python
    from fin_ratios.utils.investment_score import investment_score_from_series

    # Provide oldest year first
    annual_data = [
        {
            "revenue": 260e9, "gross_profit": 100e9, "ebit": 63e9,
            "net_income": 55e9, "operating_cash_flow": 70e9,
            "total_assets": 320e9, "total_equity": 65e9,
            "total_debt": 95e9, "cash": 35e9, "capex": 8e9,
            "depreciation": 11e9, "income_tax_expense": 14e9, "ebt": 69e9,
        },
        {
            "revenue": 275e9, "gross_profit": 106e9, "ebit": 67e9,
            "net_income": 57e9, "operating_cash_flow": 73e9,
            "total_assets": 310e9, "total_equity": 60e9,
            "total_debt": 98e9, "cash": 33e9, "capex": 9e9,
            "depreciation": 12e9, "income_tax_expense": 15e9, "ebt": 71e9,
        },
        {
            "revenue": 294e9, "gross_profit": 114e9, "ebit": 73e9,
            "net_income": 62e9, "operating_cash_flow": 80e9,
            "total_assets": 300e9, "total_equity": 62e9,
            "total_debt": 90e9, "cash": 30e9, "capex": 8e9,
            "depreciation": 12e9, "income_tax_expense": 16e9, "ebt": 77e9,
        },
    ]

    score = investment_score_from_series(annual_data, pe_ratio=18.0)
    print(f"{score.score}/100  [{score.grade}]  {score.conviction}")
    ```

=== "TypeScript"

    ```typescript
    import { investmentScoreFromSeries } from 'fin-ratios'

    // Oldest year first
    const annualData = [
      {
        revenue: 260e9, grossProfit: 100e9, ebit: 63e9,
        netIncome: 55e9, operatingCashFlow: 70e9,
        totalAssets: 320e9, totalEquity: 65e9,
        totalDebt: 95e9, cash: 35e9, capex: 8e9,
        depreciation: 11e9, incomeTaxExpense: 14e9, ebt: 69e9,
      },
      // ... more years
    ]

    const score = investmentScoreFromSeries(annualData, { peRatio: 18.0 })
    console.log(`${score.score}/100 [${score.grade}] ${score.conviction}`)
    ```

## Using Dataclasses

```python
from dataclasses import dataclass
from fin_ratios.utils.quality_score import quality_score_from_series

@dataclass
class AnnualReport:
    revenue: float
    ebit: float
    net_income: float
    operating_cash_flow: float
    total_assets: float
    total_equity: float
    total_debt: float
    cash: float
    capex: float
    depreciation: float
    income_tax_expense: float
    ebt: float

annual_data = [
    AnnualReport(revenue=300e9, ebit=75e9, net_income=65e9, ...),
    # ...
]

quality = quality_score_from_series(annual_data)
```

## Individual Ratios

For individual ratio functions, pass values directly:

```python
import fin_ratios as fr

# All ratios accept keyword arguments
pe  = fr.pe(market_cap=3e12, net_income=1e11)          # 30.0
roe = fr.roe(net_income=65e9, avg_total_equity=60e9)   # 1.08
fcf = fr.free_cash_flow(operating_cash_flow=80e9, capex=8e9)  # 72e9
```

## Ordering Convention

**Always pass `annual_data` oldest-first** (ascending chronological order). All `*_from_series` functions expect index 0 to be the oldest year.

```python
# Correct — oldest to newest
annual_data = [year_2020, year_2021, year_2022, year_2023]

# Wrong — newest first
annual_data = [year_2023, year_2022, year_2021, year_2020]
```

Fetchers from SEC EDGAR return data newest-first; reverse before passing to scoring utilities, or use the `fetch_edgar` helper which handles this automatically.
