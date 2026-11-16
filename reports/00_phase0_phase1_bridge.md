# Phase 0 / Phase 1 bridge — sensitivity and prospective quote collection

Updated 2026-11-16.

## Work implemented
- `research/sensitivity_hgb.py`: source HGB walk-forward at the already frozen threshold (predicted residual <= -4, total >=56) for (a) no `line_provider`, (b) neither provider nor observed-weather features, and (c) complete-prior-stat eligibility. The complete-prior test uses the original fitted model and filters only evaluation rows. The output reports individual seasons; do not optimize thresholds using these same seasons.
- `research/archive_odds.py`: append-only SQLite quote archive; only imports explicitly supplied, real, time-stamped quotes, never synthetic fallback data. It is a **collector/validator**, not an API connector, scheduled collector, or live odds feed.
- `tests/test_archive_odds.py`: tests invalid, post-kickoff and future-provider timestamps, and duplicate-safe imports.
- `.github/workflows/phase0-repro.yml`: original dependency pins, all unit tests, restored training data, original HGB replay, and new sensitivity experiments.

## Validated constraints
- Original HGB aggregate replication in prior pinned run: 651 selections, 376 wins, 267 losses, 8 pushes, +11.64% ROI at assumed -110.
- Original archived training data lacks timestamped bookmaker quotes and actual side prices, so these remain **hypothetical historical returns**.
- Actual historical sportsbook execution, parlay eligibility and wager limits cannot be reconstructed from that dataset alone.
- No current licensed sportsbook API connection has been supplied. Do not scrape odds or fabricate historical prices.

## Required next decisions
1. Review the latest robustness CI artifact, including year-by-year and provider-era results.
2. Connect an authorized quote source (API/export) that provides provider quote time or reliable collection time, bookmaker, market, side, line, and odds. Record terms/licensing and source provenance.
3. Run the quote archive on real observations, initially as a non-production manual ingest. Only then consider a scheduled collection cadence, subject to feed limits and permissions.
4. Compare prospectively logged selections against the prices **observed before kickoff**, with predefined wager assumptions, weekly exposure caps and independently logged settled outcomes.
5. If no appropriate odds source can be acquired, close Phase 0 as **historical modeling baseline established; executable profitability unvalidated**, rather than misrepresenting the latter as proven.

No production changes, betting transactions, or market-data purchases authorized.
