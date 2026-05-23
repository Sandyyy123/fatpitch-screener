"""
FatPitch Screener - Graham/Buffett/Munger/Pabrai Equity Screening Engine
Classifies equities into: REJECT | WATCHLIST | DEEP_RESEARCH | FAT_PITCH
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Classification(str, Enum):
    REJECT = "REJECT"
    WATCHLIST = "WATCHLIST"
    DEEP_RESEARCH = "DEEP_RESEARCH"
    FAT_PITCH = "FAT_PITCH"


@dataclass
class EquityMetrics:
    ticker: str
    name: str
    # Valuation
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    # Quality
    roic_5yr_avg: Optional[float] = None
    roce: Optional[float] = None
    fcf_conversion: Optional[float] = None  # FCF / Net Income
    gross_margin_trend: Optional[str] = None  # "improving", "stable", "declining"
    # Safety
    current_ratio: Optional[float] = None
    lt_debt_to_nca: Optional[float] = None
    eps_positive_years: Optional[int] = None  # out of last 10
    # Value trap detection
    piotroski_f_score: Optional[int] = None  # 0-9
    altman_z_score: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None  # 2-year average
    # Pabrai layer
    insider_ownership_pct: Optional[float] = None
    margin_of_safety_pct: Optional[float] = None  # vs intrinsic value estimate


@dataclass
class ScreeningResult:
    ticker: str
    classification: Classification
    score: int           # 0-100
    passed_filters: list[str]
    failed_filters: list[str]
    flags: list[str]     # value trap or warning signals
    rationale: str


def screen_equity(m: EquityMetrics) -> ScreeningResult:
    """
    Apply Graham/Buffett/Munger/Smith/Pabrai filters.
    Philosophy: reject aggressively. Fat Pitch = extremely rare.
    """
    passed, failed, flags = [], [], []
    score = 0

    # --- GRAHAM QUANTITATIVE GATES ---
    if m.pe_ratio is not None:
        if m.pe_ratio < 15:
            passed.append(f"P/E {m.pe_ratio:.1f} < 15 (Graham)")
            score += 12
        else:
            failed.append(f"P/E {m.pe_ratio:.1f} >= 15 (Graham gate failed)")

    if m.pb_ratio is not None:
        if m.pb_ratio < 1.5:
            passed.append(f"P/B {m.pb_ratio:.2f} < 1.5 (Graham)")
            score += 10
        else:
            failed.append(f"P/B {m.pb_ratio:.2f} >= 1.5")

    if m.current_ratio is not None:
        if m.current_ratio > 2.0:
            passed.append(f"Current ratio {m.current_ratio:.1f} > 2.0 (defensive)")
            score += 8
        else:
            failed.append(f"Current ratio {m.current_ratio:.1f} < 2.0 (liquidity risk)")

    if m.lt_debt_to_nca is not None:
        if m.lt_debt_to_nca < 1.0:
            passed.append(f"LT Debt/NCA {m.lt_debt_to_nca:.2f} < 1.0")
            score += 8
        else:
            failed.append(f"LT Debt/NCA {m.lt_debt_to_nca:.2f} >= 1.0 (over-levered)")

    if m.eps_positive_years is not None:
        if m.eps_positive_years >= 9:
            passed.append(f"EPS positive {m.eps_positive_years}/10 years")
            score += 10
        else:
            failed.append(f"EPS positive only {m.eps_positive_years}/10 years")

    # --- BUFFETT / TERRY SMITH QUALITY GATES ---
    if m.roic_5yr_avg is not None:
        if m.roic_5yr_avg > 15:
            passed.append(f"ROIC 5yr avg {m.roic_5yr_avg:.1f}% > 15% (Buffett moat)")
            score += 14
        else:
            failed.append(f"ROIC 5yr avg {m.roic_5yr_avg:.1f}% < 15%")

    if m.roce is not None:
        if m.roce > 15:
            passed.append(f"ROCE {m.roce:.1f}% > 15% (Terry Smith)")
            score += 10
        else:
            failed.append(f"ROCE {m.roce:.1f}% < 15%")

    if m.fcf_conversion is not None:
        if m.fcf_conversion > 0.80:
            passed.append(f"FCF conversion {m.fcf_conversion:.0%} > 80%")
            score += 8
        else:
            failed.append(f"FCF conversion {m.fcf_conversion:.0%} < 80%")

    # --- VALUE TRAP DETECTION ---
    if m.piotroski_f_score is not None:
        if m.piotroski_f_score >= 7:
            passed.append(f"Piotroski F-Score {m.piotroski_f_score}/9 (healthy)")
            score += 10
        elif m.piotroski_f_score < 5:
            flags.append(f"TRAP: Piotroski F-Score {m.piotroski_f_score}/9 - weak fundamentals")
            score -= 15

    if m.altman_z_score is not None:
        if m.altman_z_score > 2.99:
            passed.append(f"Altman Z {m.altman_z_score:.2f} - safe zone")
            score += 8
        elif m.altman_z_score < 1.81:
            flags.append(f"TRAP: Altman Z {m.altman_z_score:.2f} - distress zone")
            score -= 20

    if m.revenue_growth_yoy is not None and m.revenue_growth_yoy < -0.05:
        flags.append(f"TRAP: Revenue declining {m.revenue_growth_yoy:.1%} YoY")
        score -= 10

    # --- PABRAI SELECTIVITY LAYER ---
    if m.insider_ownership_pct is not None and m.insider_ownership_pct > 10:
        passed.append(f"Insider ownership {m.insider_ownership_pct:.1f}% (skin in game)")
        score += 8

    if m.margin_of_safety_pct is not None and m.margin_of_safety_pct > 30:
        passed.append(f"Margin of safety {m.margin_of_safety_pct:.0f}% vs intrinsic value")
        score += 12

    # --- CLASSIFY ---
    has_trap_flags = any("TRAP" in f for f in flags)
    hard_fails = len(failed)

    if has_trap_flags or hard_fails >= 4 or score < 20:
        classification = Classification.REJECT
        rationale = f"Hard gate failures ({hard_fails}) or value trap signals. Capital preservation first."
    elif hard_fails >= 2 or score < 45:
        classification = Classification.WATCHLIST
        rationale = "Passes some filters. Monitor for improved valuation or fundamentals."
    elif score >= 75 and hard_fails == 0 and not has_trap_flags:
        classification = Classification.FAT_PITCH
        rationale = "Rare: passes ALL filters with asymmetric upside. High conviction."
    else:
        classification = Classification.DEEP_RESEARCH
        rationale = "Passes quantitative screens. Requires qualitative deep-dive before acting."

    return ScreeningResult(
        ticker=m.ticker,
        classification=classification,
        score=max(0, min(100, score)),
        passed_filters=passed,
        failed_filters=failed,
        flags=flags,
        rationale=rationale,
    )
