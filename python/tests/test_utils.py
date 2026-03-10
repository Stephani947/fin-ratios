"""Tests for utility modules: benchmarks, health_score, screening."""

import pytest
from fin_ratios.utils.benchmarks import sector_benchmarks, percentile_rank, available_sectors
from fin_ratios.utils.health_score import health_score
from fin_ratios.utils.screening import screen, rank


# ── Benchmarks ────────────────────────────────────────────────────────────────

def test_sector_benchmarks_technology():
    b = sector_benchmarks("Technology")
    assert b.sector == "Technology"
    assert b.pe_median is not None
    assert b.pe_median > 0
    assert b.roic_median is not None

def test_sector_benchmarks_fallback():
    b = sector_benchmarks("UnknownSector")
    # Should fall back to S&P 500
    assert b.pe_median is not None

def test_available_sectors_non_empty():
    sectors = available_sectors()
    assert len(sectors) >= 8
    assert "Technology" in sectors
    assert "Healthcare" in sectors

def test_percentile_rank_median_is_50():
    # The median value should be at ~50th percentile
    b = sector_benchmarks("Technology")
    pct = percentile_rank("Technology", "pe", b.pe_median)
    assert 45 <= pct <= 55  # near 50th

def test_percentile_rank_above_p75():
    # Value well above p75 should be > 75
    pct = percentile_rank("Technology", "roic", 0.50)  # very high ROIC
    assert pct > 75

def test_percentile_rank_below_p25():
    # Value well below p25 should be < 25
    pct = percentile_rank("Technology", "roic", 0.02)  # very low ROIC
    assert pct < 25

def test_percentile_rank_unknown_metric():
    # Unknown metric falls back to 50
    pct = percentile_rank("Technology", "nonexistent_metric", 100)
    assert pct == 50.0


# ── Health Score ──────────────────────────────────────────────────────────────

def test_health_score_excellent():
    result = health_score(
        piotroski_score=9,
        altman_z=5.0,
        roic=0.35,
        wacc=0.09,
        net_margin=0.25,
        gross_margin=0.70,
        roe=0.40,
        fcf_conversion=1.05,
        fcf_margin=0.22,
        revenue_growth=0.20,
        debt_to_equity=0.30,
        current_ratio=3.5,
        interest_coverage=15.0,
    )
    assert result.score >= 85
    assert result.grade in ("A+", "A")

def test_health_score_distressed():
    result = health_score(
        piotroski_score=1,
        altman_z=1.0,
        roic=-0.05,
        wacc=0.10,
        net_margin=-0.10,
        roe=-0.15,
        fcf_conversion=0.2,
        revenue_growth=-0.15,
        debt_to_equity=4.0,
        current_ratio=0.8,
        interest_coverage=0.9,
    )
    assert result.score <= 35
    assert result.grade in ("D", "F")

def test_health_score_range():
    result = health_score(piotroski_score=5, altman_z=2.5, roic=0.12)
    assert 0 <= result.score <= 100

def test_health_score_grade_exists():
    result = health_score(piotroski_score=7, net_margin=0.15)
    assert result.grade in ("A+", "A", "B+", "B", "C+", "C", "D", "F")

def test_health_score_breakdown():
    result = health_score(piotroski_score=8, roic=0.25, net_margin=0.18)
    assert "piotroski" in result.breakdown
    assert "value_creation" in result.breakdown

def test_health_score_no_data():
    # Should return something reasonable even with no data
    result = health_score()
    assert result.score == pytest.approx(50.0)

def test_health_score_manipulation_penalty():
    clean = health_score(piotroski_score=7, net_margin=0.15, beneish_m=-3.0)
    suspicious = health_score(piotroski_score=7, net_margin=0.15, beneish_m=-1.5)
    assert clean.score > suspicious.score


# ── Screening ─────────────────────────────────────────────────────────────────

UNIVERSE = [
    {"ticker": "AAPL", "pe": 28.0, "roic": 0.55, "piotroski_score": 8, "ev_ebitda": 22.0},
    {"ticker": "IBM",  "pe": 15.0, "roic": 0.08, "piotroski_score": 4, "ev_ebitda": 10.0},
    {"ticker": "NVDA", "pe": 55.0, "roic": 0.45, "piotroski_score": 7, "ev_ebitda": 45.0},
    {"ticker": "F",    "pe":  8.0, "roic": 0.04, "piotroski_score": 3, "ev_ebitda":  5.0},
    {"ticker": "MSFT", "pe": 32.0, "roic": 0.30, "piotroski_score": 7, "ev_ebitda": 28.0},
]


def test_screen_single_filter():
    results = screen(UNIVERSE, {"pe": "< 20"})
    tickers = {r["ticker"] for r in results}
    assert "IBM" in tickers
    assert "F" in tickers
    assert "NVDA" not in tickers

def test_screen_multiple_filters():
    results = screen(UNIVERSE, {"pe": "< 35", "roic": "> 0.20"})
    tickers = {r["ticker"] for r in results}
    assert "AAPL" in tickers
    assert "MSFT" in tickers
    assert "IBM" not in tickers
    assert "F" not in tickers

def test_screen_no_matches():
    results = screen(UNIVERSE, {"pe": "< 5"})
    assert results == []

def test_screen_all_match():
    results = screen(UNIVERSE, {"pe": "> 0"})
    assert len(results) == len(UNIVERSE)

def test_screen_gte():
    results = screen(UNIVERSE, {"piotroski_score": ">= 7"})
    tickers = {r["ticker"] for r in results}
    assert "AAPL" in tickers
    assert "NVDA" in tickers
    assert "MSFT" in tickers
    assert "IBM" not in tickers

def test_screen_missing_metric():
    universe = [{"ticker": "X"}, {"ticker": "Y", "pe": 20}]
    results = screen(universe, {"pe": "< 30"})
    assert len(results) == 1
    assert results[0]["ticker"] == "Y"

def test_screen_invalid_expression():
    with pytest.raises(ValueError):
        screen(UNIVERSE, {"pe": "20"})  # missing operator


# ── Rank ──────────────────────────────────────────────────────────────────────

def test_rank_single_metric():
    import copy
    universe = copy.deepcopy(UNIVERSE)
    ranked = rank(universe, metrics=["roic"], ascending=[False])
    # Highest ROIC first
    assert ranked[0]["ticker"] == "AAPL"

def test_rank_greenblatt():
    import copy
    universe = copy.deepcopy(UNIVERSE)
    ranked = rank(
        universe,
        metrics=["ev_ebitda", "roic"],
        ascending=[True, False],
        top_n=3,
    )
    assert len(ranked) == 3
    # Combined rank is sorted ascending (best first)
    assert ranked[0]["_combined_rank"] <= ranked[1]["_combined_rank"]

def test_rank_top_n():
    import copy
    universe = copy.deepcopy(UNIVERSE)
    ranked = rank(universe, metrics=["pe"], ascending=[True], top_n=2)
    assert len(ranked) == 2
