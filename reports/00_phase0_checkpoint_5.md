# Phase 0 — Checkpoint 5: executed market coverage audit and parlay-ticket engine
Date: 2026-11-14. **Phase 0 remains OPEN.**

## Executed audit (original historical training ZIP)
Reopened original Actions artifact `14120803087` (`modeling_dataset.csv`) and ran a local independent coverage/lineage inspection using pandas 2.2.3. Reproducible source is `research/audit_market_coverage.py`.

- **26,843 games** from 2014–2025; **11,757 games with historical totals**; 11,757 parseable kickoff timestamps; 0 duplicate game IDs.
- **No quote timestamp fields** and **no under/over American odds or book-specific prices**. A kickoff timestamp is not a quote timestamp.
- **126 prior-season home/away feature columns**, but **zero `home_inseason_`/`away_inseason_` feature columns** in this archived training dataset. A separate advanced-inseason feature CSV exists in the artifact but is not merged into this modeling dataset. Do not claim it is included in the historical HGB backtest.
- Prior-feature coverage among lined games drops sharply after 2021 (see table); this is a possible cohort/feature distribution shift, not proof of leakage.
- Wind observation availability among lined games is ~96–99% across seasons, but observations have not been proven pregame-available.

## Historical season coverage
| Season | Games | With total | Total coverage | FBS-vs-FBS with total | Prior-feature coverage among lined games |
|---|---:|---:|---:|---:|---:|
| 2014 | 1542 | 721 | 46.76% | 721 | 98.20% |
| 2015 | 1491 | 724 | 48.56% | 724 | 99.31% |
| 2016 | 1502 | 719 | 47.87% | 719 | 100.00% |
| 2017 | 1505 | 745 | 49.50% | 736 | 98.66% |
| 2018 | 1511 | 812 | 53.74% | 733 | 99.51% |
| 2019 | 1577 | 841 | 53.33% | 734 | 100.00% |
| 2020 | 563 | 541 | 96.09% | 508 | 100.00% |
| 2021 | 2408 | 849 | 35.26% | 732 | 98.47% |
| 2022 | 3657 | 1413 | 38.64% | 734 | 59.73% |
| 2023 | 3595 | 1345 | 37.41% | 750 | 63.42% |
| 2024 | 3747 | 1503 | 40.11% | 752 | 56.62% |
| 2025 | 3745 | 1544 | 41.23% | 762 | 56.74% |

**Important:** overall line coverage percentages are not directly comparable across years because the universe of games in the dataset expands to include more FCS games after 2020. FBS-vs-FBS coverage is a more relevant historical comparison for General HGB. Prior-feature coverage measures any nonmissing home prior-stat column, not full completeness.

## Historical bookmaker/provider drift
The preferred historical provider changes materially:
- `teamrankings`: 2,211 lined games, 2014–2018
- `consensus`: 4,936, 2017–2023
- `DraftKings`: 2,123, 2023–2025
- `ESPN Bet`: 1,535, 2023–2025
- `William Hill (New Jersey)`: 500, 2021–2023
- `Bovada`: 370, 2021–2025

**Consequence:** `line_provider` is itself a model feature in historical HGB. Its category and market source change over time, potentially creating a regime/selection artifact. Audit performance and edge calibration by provider and year; consider a no-provider-feature sensitivity test.

## New parlay research infrastructure
Added `research/parlay_ticket_audit.py` with strict input schema and a conservative five-minute cross-leg quote age rule. It:
- Validates 2- or 3-leg ticket composition, game uniqueness, common bookmaker, positive consistent stake, and quotes preceding kickoff.
- Prices each leg using its actual American odds (if supplied).
- Settles full-game total unders/overs, including pushed legs at 1.0x payout, losses, and all-push refunds.
- Explicitly marks `quote_verified_executable=False` because a supplied quote record alone does not prove a sportsbook accepted a parlay or its maximum stake.
- Has synthetic unit tests in `tests/test_parlay_ticket_audit.py` for wins, losses, pushes, invalid odds, duplicate games, mixed books, and stale/postkickoff quotes.

**These parlay scripts and tests are committed, but have not been executed in GitHub Actions.** No actual historical parlay tickets were generated or validated because historical quote-level data is missing. Do not interpret this as confirmation of the historical +79.7% ROI.

## Outstanding Phase 0 gates
1. Execute source-aligned HGB replay under original scikit-learn 1.9.0 and reconcile per-game selections with the source audit.
2. Run no-provider and prior-feature-missingness sensitivity tests to distinguish model edge from provider-era effects.
3. Obtain or begin capturing bookmaker quote timestamps, sides, prices, and limits. If historical data cannot be sourced, historical returns must remain unexecutable proxy results.
4. Build a prospective, pre-kickoff parlay candidate ledger; only calculate executable ROI on verified ticket/price data.
5. Audit source advanced/in-season feature construction and game-level feature availability.

**Production repo unchanged. No wagers or live workflow dispatches.**
