# FatPitch Screener

Graham / Buffett / Munger / Terry Smith / Pabrai-inspired equity screening engine.

**Philosophy:** Capital preservation first. Extreme selectivity. "No Called Strikes" - it is perfectly acceptable for the output to be "No compelling opportunities found."

## Architecture

```
EODHD / FMP APIs
       |
       v
PostgreSQL (financial statements, ratios, universe)
       |
       v
Screening Engine (screener.py)
  - Graham quantitative gates
  - Buffett / Terry Smith quality filters
  - Piotroski F-Score (value trap detection)
  - Altman Z-Score (distress detection)
  - Pabrai selectivity layer
       |
       v
Classification: REJECT | WATCHLIST | DEEP_RESEARCH | FAT_PITCH
       |
       v
Weekly PDF Report + Email (OpenAI narrative)
```

## Classification

| Tier | Meaning | Expected frequency |
|------|---------|-------------------|
| REJECT | Fails any hard gate | ~90% of universe |
| WATCHLIST | Mostly passes, price not right yet | ~7% |
| DEEP RESEARCH | Passes all quant filters | ~2-3% |
| FAT PITCH | Rare, high-conviction asymmetric opportunity | < 1% |

## Quick Start (Demo Mode)

```bash
pip install -r requirements.txt
python main.py --demo
```

## Full Pipeline Setup

Copy `.env.example` to `.env` and fill in:

```
EODHD_API_KEY=your_key
FMP_API_KEY=your_key
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=your_key
REPORT_EMAIL=you@example.com
```

## Filters Implemented

**Graham gates:** P/E < 15, P/B < 1.5, current ratio > 2, LT debt/NCA < 1, EPS positive 9/10 years

**Quality (Buffett/Smith):** ROIC 5yr avg > 15%, ROCE > 15%, FCF conversion > 80%

**Value trap detection:** Piotroski F-Score (flags < 5), Altman Z-Score (flags < 1.81), revenue decline detection

**Pabrai selectivity:** Insider ownership, margin of safety vs intrinsic value estimate

## Author

Dr. Sandeep Grover | https://groverautomationhub.lovable.app/portfolio
