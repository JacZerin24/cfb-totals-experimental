# Phase 0 — Checkpoint 2: original training artifact recovered and audited
Date: 2026-11-14. **Status: partial; historical model/quote-level replication NOT passed.**

## Data provenance
- Source: `JacZerin24/cfb-weather-totals`, successful [Weekly CFB Weather Totals run 43613392785](https://github.com/JacZerin24/cfb-weather-totals/actions/runs/43613392785), artifact `cfb-live-training-data`, artifact ID `14120803087`, 4,788,556-byte ZIP.
- Artifact ZIP SHA-256: `3ddfe75ebfd34d2a3156d6c16993807fc2360f50adf4d3d33ea6da10cace9081`.
- `modeling_dataset.csv`: 14,628,617 bytes, SHA-256 `a2f5a61248afe895e39bde58c5d3f8e7d10ed490095418e45d69ff0bbc7b3678`.
- `team_prior_features.csv`: 592,023 bytes, SHA-256 `573770f9be1e2f5e87c8a4d762f4041c250d7785f7586e8bcfe844247dfa5c34`.
- `team_inseason_game_advanced_features.csv`: 3,357,101 bytes, SHA-256 `a70e0c990fbba0943477af7e054f657d23f27af9fb800f8ce5f22c6b46058c9a`.
- **Do not commit raw artifacts**: large, potentially licensed source data. Manual retrieval script: `scripts/restore_historical_training.sh`. Independent dataset audit: `research/audit_training_artifact.py`.

## Dataset integrity audit (actually executed on downloaded ZIP)
| Measure | Result |
|---|---:|
| Seasons | 2014–2025 |
| Games | 26,843 |
| Columns | 164 |
| Games with historical totals | 11,757 |
| Games without historical totals | 15,086 |
| FBS-vs-FBS games with totals | 8,605 |
| Games with wind observations | 18,882 |
| Duplicate game IDs | 0 |
| Scoring-residual calculation mismatches | 0 |
| Games with missing final points | 8 |

Historical line provider counts (all rows, including no-line): missing 15,086; consensus 4,936; teamrankings 2,211; DraftKings 2,123; ESPN Bet 1,535; William Hill (New Jersey) 500; Bovada 370; others smaller.

## Significant methodological problems discovered
### A. Historical game weather is not a pregame forecast
`src/pull_historical_weather.py` calls CFBD `/games/weather`; `src/build_dataset.py` merges the weather values into the training data. `src/model_bakeoff.py` includes `wind_mph`, `temperature_f`, `humidity`, `precipitation`, `snowfall`, `dewpoint_f`, `pressure`, and weather-derived bins as predictors. These are historical weather observations, not verified pregame forecasts. The walk-forward split by season does **not** prevent within-game information leakage when contemporaneous/realized weather is used to predict that same game's score. **Risk: historical performance may not be live-reproducible.** Do not claim that every observation was recorded after kickoff; availability timestamps are absent. The correct fix is point-in-time archived forecasts or an explicit no-weather baseline.

### B. Historical `closing_total` is not timestamp-verified
`src/build_dataset.py` selects a preferred provider's `over_under` from historical CFBD lines. It does not retain the original line timestamp, individual book price, or a time-specific quote. The selected provider-ranked line is named `closing_total` but is **not proven to be the closing quote, an early actionable quote, or available at a particular decision time**. Model inputs and selection rules depend on that line, so backtest/live comparability remains unresolved.

### C. Prior-season stats appear structurally shifted correctly, but are not yet independently reconciled
`src/build_team_features.py` pivots team season statistics and shifts the season by +1, so 2023 statistics are intended for 2024 games. This reduces one obvious leakage mechanism; verify provider completeness and that all advanced/in-season features are strictly lagged.

### D. Parlay ROI is not independent return evidence
Historical unconstrained combination enumeration repeats many legs across tickets. The +79.66% three-leg historical figure is a simulation over 5,270 overlapping combinations, not proof of achievable bankroll growth. Book-level price, parlay eligibility, limits, exposure, and independent season validation are outstanding.

## What has been independently reproduced so far
- Recovered the original training data and independently verified dataset structure and residual arithmetic.
- Recovered the Sept 22 `hgb-training-regime-audit` ZIP (artifact ID `10692902391`) and read the actual `hgb_fixed_threshold_grid.csv` record: edge >=4, total >=56, 2016–2025, 651 selected, 643 graded, 376–267, 8 pushes, ROI +11.6358%; recent 2022–2025 106–66, 2 pushes, ROI +17.6533%.
- Independently checked published parlay summary net-unit / graded ROI arithmetic and FCS historical summary arithmetic.
- **Not yet reproduced:** training HGB from original inputs and matching per-game predictions, actual ticket-level parlay replay, quote availability, leakage-free counterfactual baseline.

## Next critical experiment
Run the exact original HGB walk-forward twice on this artifact, keeping season folds and selection frozen: (1) published feature set, (2) only pregame-available features with **all weather observation columns/bins removed**. Compare historical by-season ROI, number of selected games, scoring residuals, and tail losses. This does not solve historical quote timing, so results remain diagnostic. Then obtain timestamped odds and archived forecast issuance records before any claims of executable edge.

**Gate: NOT PASSED.** No changes were made to the original production repo.
