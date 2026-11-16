# Phase 0 robustness and prospective quote collection — 2026-11-16

## Work implemented
- `research/sensitivity_hgb.py`: original source HGB walk-forward with three additional frozen-threshold checks:
  - `no_provider`: remove `line_provider` feature, retaining observed weather.
  - `no_weather_no_provider`: remove `line_provider` and observed weather numeric/categorical features.
  - `complete_prior_only`: retain the source model trained on its full cohort but restrict **evaluation only** to FBS-vs-FBS games with all non-all-null prior-season numeric features. This is a cohort sensitivity analysis, not a refit on complete cases.
- `research/archive_odds.py`: validates and ingests supplied quote CSV into append-only, duplicate-safe SQLite under ignored `data/external/`. Requires source, source quote ID, observed timestamp, bookmaker, game ID, kickoff timestamp, full-game total market, under/over side, line and American odds. Optional provider quote timestamp and team names. No network scraping or bookmaker connection.
- `tests/test_archive_odds.py`: synthetic fixture tests for invalid quotes and idempotent import.
- `.github/workflows/phase0-repro.yml`: pinned original environment; includes robustness run and exports generated CSV diagnostics.

## Operational limitations
The odds archive does not contain any real observations until a licensed source or authorized data feed is connected. A timestamped quote does not guarantee a book accepted the wager or parlay. Do not run an automatic job that invents, backfills, or silently substitutes historical `closing_total` as executable odds.

## Quote CSV example (synthetic; do NOT use for actual ROI)
```csv
source,source_quote_id,observed_utc,bookmaker,game_id,kickoff_utc,market,side,line,american_odds,provider_quote_utc,home_team,away_team
fixture,example-1,2026-11-14T12:00:00Z,ExampleBook,synthetic-game-1,2026-11-14T18:00:00Z,game_total,under,56.5,-110,2026-11-14T11:59:00Z,Home,Away
```
Use `python research/archive_odds.py --input real_quotes.csv` only with genuine, permitted quote exports.

## Interpretation and next gate
Historical ROI remains a hypothetical -110 backtest. Sensitivity results test whether the model's historical association survives feature changes; they cannot validate executable sportsbook returns. Phase 0 remains open until point-in-time feature and quote provenance is established and independently evaluated.
