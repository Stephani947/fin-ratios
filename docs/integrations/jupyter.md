# Jupyter Notebooks

fin-ratios provides rich HTML display for Jupyter environments through the `notebook` module.

## Installation

```bash
pip install "financial-ratios[fetchers]"
# Run in Jupyter Lab or Jupyter Notebook
```

## RatioCard

Display a formatted card for a single company's ratios:

```python
from fin_ratios.notebook import RatioCard, display_ratios
from fin_ratios.fetchers.edgar import fetch_edgar
from fin_ratios.utils.investment_score import investment_score_from_series

annual_data = fetch_edgar('AAPL', num_years=7)
score = investment_score_from_series(annual_data, pe_ratio=28.0)

# Rich HTML display
RatioCard(ticker='AAPL', score=score)
```

## ComparatorCard

Side-by-side comparison of multiple companies:

```python
from fin_ratios.notebook import ComparatorCard

scores = {
    'AAPL': investment_score_from_series(fetch_edgar('AAPL', num_years=5), pe_ratio=28),
    'MSFT': investment_score_from_series(fetch_edgar('MSFT', num_years=5), pe_ratio=33),
    'GOOGL': investment_score_from_series(fetch_edgar('GOOGL', num_years=5), pe_ratio=24),
}

ComparatorCard(scores)
```

## display_ratios

Quick tabular display of individual ratio values:

```python
from fin_ratios.notebook import display_ratios
import fin_ratios as fr

data = {'market_cap': 3e12, 'net_income': 1e11, 'revenue': 3e11, 'total_equity': 6e10}

display_ratios(data, ratios=['pe', 'ps', 'roe'])
```

## Scoring Objects in Jupyter

All scoring result objects implement `_repr_html_()` for automatic display:

```python
from fin_ratios.utils.quality_score import quality_score_from_series

score = quality_score_from_series(annual_data)
score  # renders as HTML table in Jupyter
```

This works for: `MoatScore`, `CapitalAllocationScore`, `EarningsQualityScore`, `QualityFactorScore`, `ValuationScore`, `ManagementScore`, `DividendSafetyScore`, `InvestmentScore`.
