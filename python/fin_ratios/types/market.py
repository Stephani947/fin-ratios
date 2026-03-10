"""Market and price data types."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketData:
    price: float
    market_cap: float
    shares_outstanding: Optional[float] = None
    enterprise_value: Optional[float] = None
    forward_eps: Optional[float] = None
    trailing_eps: Optional[float] = None
    dividend_per_share: Optional[float] = None
    high_52_week: Optional[float] = None
    low_52_week: Optional[float] = None
    ticker: Optional[str] = None
    as_of: Optional[str] = None


@dataclass
class PricePoint:
    date: str
    close: float
    volume: Optional[float] = None
