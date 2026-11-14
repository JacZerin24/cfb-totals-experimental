# Phase 0 — Checkpoint 3: executed historical weather-feature ablation
Date: 2026-11-14. **Phase 0 remains OPEN.**

## What was run
Using the original recovered `cfb-live-training-data` artifact (see [data audit](00_phase0_training_data_audit.md)), trained HGB walk-forward by season (2016–2025) with the historical model's 250 iterations, learning rate 0.04, L2 0.5, leaf minimum 35, random seed 42, and `early_stopping=False`. Compared (A) original-style feature set and (B) the same feature set **excluding historical observed weather**: wind, temperature, humidity, precipitation, snowfall, dewpoint, pressure, wind-bin, temp-bin. Selected FBS-vs-FBS unders with predicted market residual <= -4 and historical total >= 56. Assumed -110 payout.

Execution environment: Python 3.13, pandas 2.2.3, scikit-learn **1.8.0** (source pinned scikit-learn **1.9.0**). Code is in `research/weather_ablation.py`, results in `reports/phase0_weather_ablation_by_season.csv`.

## Results
| Cohort | Selections | W-L-P | Win % graded | Net ROI graded | Positive years |
|---|---:|---:|---:|---:|---:|
| Original-style features (diagnostic reproduction) | 651 | 378-263-10 | 58.97% | +12.58% | 8 / 10 |
| No observed weather | 664 | 389-269-6 | 59.12% | +12.86% | 9 / 10 |
| Published Sept 22 source artifact (different environment) | 651 | 376-267-8 | 58.48% | +11.64% | 10 / 10 |

**Interpretation:** removing observed weather did not destroy the historical association in this diagnostic; this **does not establish** the feature set is pregame-valid, that the odds were executable, or that the ROI is real. The model's underlying line provider and historical quote timing remain unverified. The original-style diagnostic differs from the published artifact by 2 additional wins, 4 fewer losses, and 2 additional pushes even though selection count is the same; likely model/library version or preprocessing differences, but root cause not yet verified. Do not conflate the diagnostic with exact replication.

## Critical next tests
1. Pin the source environment to Python 3.11 / scikit-learn 1.9.0 / pandas 3.0.5, then compare per-game predictions against the original September 22 audit artifact. Reproduce exactly or document why.
2. Re-run no-observed-weather ablation in the pinned environment.
3. Independently audit source `/games/weather` records' issue times and replace with archived forecasts available before each betting decision.
4. Obtain historical bookmaker snapshots with quote timestamps and actual odds; compare source `closing_total` with genuine book quotes. Until then, historical ROI remains **non-executable**.
5. Rebuild a capped, nonoverlapping weekly parlay ticket ledger with per-leg pushes, bookmaker prices, and correlation-aware uncertainty; do not infer annual 50% ROI from overlapping combinations.

**No changes to production or wagering systems.**
