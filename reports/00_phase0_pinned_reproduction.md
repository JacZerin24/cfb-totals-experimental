# Phase 0 — Pinned-environment reproduction results
Date: 2026-11-14

## Completed GitHub Actions execution
Successful [Phase 0 reproducibility audit run 43639836744](https://github.com/JacZerin24/cfb-totals-experimental/actions/runs/43639836744), job 132584725302. Research-only workflow `.github/workflows/phase0-repro.yml`; all steps completed successfully. Nine synthetic unit tests passed.

Environment: Python 3.13.18, pandas **3.0.5**, scikit-learn **1.9.0**, installed directly from original source requirements. Original training dataset restored from source run 43613392785. Diagnostic output artifact `phase0-repro-results`, artifact ID `14130524474` (30-day retention).

## Source-aligned historical HGB comparison
Walk-forward 2016–2025, FBS-vs-FBS unders, predicted residual <= -4, historical total >=56, `early_stopping=False`, fixed -110 assumed odds.

| Cohort | Selected | Graded | Wins | Losses | Pushes | Net units | ROI / graded |
|---|---:|---:|---:|---:|---:|---:|---:|
| Source-exact features | 651 | 643 | 376 | 267 | 8 | +74.81818 | **+11.6358%** |
| Without observed weather and derived bins | 752 | 739 | 424 | 315 | 13 | +70.45455 | **+9.5338%** |
| Published original Sept 22 audit | 651 | 643 | 376 | 267 | 8 | +74.81818 | **+11.6358%** |

**Aggregate exact match**: published original HGB totals and ROI reproduced exactly in pinned source environment. Game-level identity matching against the original Sept 22 predictions is **not established** because original archived per-game walk-forward predictions were not included in that audit artifact. The current run exported new per-game predictions for independent inspection.

**Correction to prior checkpoint:** the earlier scikit-learn 1.8 ablation (+12.86%, 664 selections) was a diagnostic with non-identical preprocessing; the source-aligned pinned-environment weather-free result is **+9.53%, 752 selections**. Use the pinned result going forward.

## Data and execution validation
- Training artifact restored successfully. Data structure, season/provider coverage and residual integrity audits ran successfully.
- Historical line data lacks book-specific quote timestamps, under/over American prices, verified limits and parlay acceptance. The historical ROI is a *fixed-odds proxy*, not proven executable.
- The original feature set uses game-weather observations; removing them reduces the modeled historical ROI but does not eliminate it. Weather-free is not automatically point-in-time valid because historical lines and some other features remain unaudited.
- Parlay ticket validator passed nine synthetic unit tests, including leg pushes, stale quotes, duplicate game IDs and mixed bookmakers. **No historical tickets were verified against actual sportsbook quotes.**
- Model cohort and provider distribution shift remain open issues; original source dataset contains no merged in-season features.

## Phase 0 gate status
**Partial pass:** source aggregate reproduction and data integrity checks PASS.
**Open / blocked:** quote-level executable odds; verified pregame feature timestamps; historical per-game prediction comparison to an original immutable snapshot; historical bookmaker acceptance and limits; realistic historical parlay reconstruction; provider-era sensitivity analysis.

Therefore **Phase 0 cannot be honestly declared complete**. A reproducible historical prediction is not equivalent to a validated profitable wagering strategy.

## Immediate next actions
1. Acquire properly licensed, point-in-time bookmaker historical odds with timestamps, side, line, price and venue/book, or begin a prospective quote archive and mark earlier years as unexecutable proxy backtests.
2. Test no-provider feature and historical feature-missingness sensitivity on the same pinned source pipeline.
3. Add game-level cohort checksums and compare archived published game selections where such archives can be recovered.
4. Validate parlay portfolios using actual quote-level legs and capped weekly exposure, with week/season-block bootstrap.
5. Freeze a prospective validation protocol that distinguishes model calibration, hypothetical fixed-price ROI, and executable odds-based ROI.

**Original production repo unchanged. No wagers placed.**
