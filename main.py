"""
FatPitch Engine - Main Entry Point
Run: python main.py --demo
"""

import argparse
from screener import EquityMetrics, screen_equity, Classification


DEMO_UNIVERSE = [
    EquityMetrics(
        ticker="KO", name="Coca-Cola Co",
        pe_ratio=24.1, pb_ratio=10.2, roic_5yr_avg=19.8, roce=18.5,
        fcf_conversion=0.91, current_ratio=1.1, lt_debt_to_nca=1.3,
        eps_positive_years=10, piotroski_f_score=7, altman_z_score=3.4,
        revenue_growth_yoy=0.04, insider_ownership_pct=0.3, margin_of_safety_pct=5,
    ),
    EquityMetrics(
        ticker="EXAMPLE_DEEP", name="Example Deep Research Co",
        pe_ratio=11.2, pb_ratio=1.1, roic_5yr_avg=16.2, roce=15.8,
        fcf_conversion=0.84, current_ratio=2.4, lt_debt_to_nca=0.6,
        eps_positive_years=10, piotroski_f_score=7, altman_z_score=3.1,
        revenue_growth_yoy=0.06, insider_ownership_pct=8.0, margin_of_safety_pct=22,
    ),
    EquityMetrics(
        ticker="EXAMPLE_FATPITCH", name="Example Fat Pitch Co",
        pe_ratio=9.8, pb_ratio=0.9, roic_5yr_avg=22.1, roce=19.4,
        fcf_conversion=0.93, current_ratio=2.8, lt_debt_to_nca=0.4,
        eps_positive_years=10, piotroski_f_score=8, altman_z_score=4.2,
        revenue_growth_yoy=0.08, insider_ownership_pct=18.5, margin_of_safety_pct=42,
    ),
    EquityMetrics(
        ticker="TRAP_CO", name="Value Trap Corp",
        pe_ratio=7.1, pb_ratio=0.6, roic_5yr_avg=4.2, roce=3.1,
        fcf_conversion=0.31, current_ratio=0.9, lt_debt_to_nca=2.1,
        eps_positive_years=6, piotroski_f_score=3, altman_z_score=1.2,
        revenue_growth_yoy=-0.12, insider_ownership_pct=1.0, margin_of_safety_pct=0,
    ),
]

COLOR = {
    Classification.REJECT:       "\033[91m",  # red
    Classification.WATCHLIST:    "\033[93m",  # yellow
    Classification.DEEP_RESEARCH:"\033[94m",  # blue
    Classification.FAT_PITCH:    "\033[92m",  # green
}
RESET = "\033[0m"


def run_demo():
    print("\n" + "="*60)
    print("  FatPitch Engine - Value Investing Screener (Demo Mode)")
    print("  Philosophy: Graham / Buffett / Munger / Smith / Pabrai")
    print("  'No Called Strikes' - reject aggressively")
    print("="*60 + "\n")

    results = [screen_equity(m) for m in DEMO_UNIVERSE]
    fat_pitches = [r for r in results if r.classification == Classification.FAT_PITCH]

    for r in results:
        c = COLOR.get(r.classification, "")
        print(f"{c}[{r.classification.value}]{RESET}  {r.ticker}  (score: {r.score}/100)")
        print(f"  {r.rationale}")
        if r.flags:
            for f in r.flags:
                print(f"  \033[91m! {f}{RESET}")
        print()

    print("-"*60)
    if fat_pitches:
        print(f"\033[92mFat Pitches found: {len(fat_pitches)}{RESET}")
        for fp in fat_pitches:
            print(f"  -> {fp.ticker}: {fp.rationale}")
    else:
        print("\033[93mNo Fat Pitch opportunities found. No Called Strikes.\033[0m")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FatPitch Value Investing Screener")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        print("Use --demo to run with sample data.")
        print("Full pipeline requires .env with EODHD_API_KEY, FMP_API_KEY, DATABASE_URL, OPENAI_API_KEY")
