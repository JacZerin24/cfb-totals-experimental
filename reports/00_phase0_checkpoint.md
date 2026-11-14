# Phase 0 — Replication and data audit: checkpoint 1
Date: 2026-11-14. **Status: partial, not completed.**

## Completed
1. Copied 7 additional parlay and model-validation files into `reference/legacy/`, for **24 total legacy reference files**. Original source repository was not modified.
2. Retrieved the actual historical HGB audit artifact ZIP from the successful [September 22 run](https://github.com/JacZerin24/cfb-weather-totals/actions/runs/35725584192) (artifact ID `10692902391`, `hgb-training-regime-audit`). ZIP contains `hgb_fixed_threshold_grid.csv`, `hgb_regime_diagnostics.csv`, `hgb_regime_audit.md`, `hgb_fixed_live_board.csv`, `hgb_fixed_live_screen_counts.csv`, `hgb_fixed_live_top_under.csv`. This ZIP is available from the source workflow; **not yet committed to the experimental repository**.
3. Verified historical fixed HGB threshold 4.0 / total 56.0 from the actual artifact: 651 games, 643 graded, 376–267 and 8 pushes, +11.6358% ROI, 2016–2025. Recent 2022–2025: 106–66 with 2 pushes, +17.6533% ROI.
4. Added `research/phase0_audit.py`, a read-only standard-library check of imported historical FCS and parlay summary arithmetic. Independently checked the **14 parlay strategy summaries, 111 season/strategy rows, and 7 weekly-card summary rows**: reported ROI equals net units divided by graded count; FCS historical 41–32 summary arithmetic also agrees.
5. Verified the source `src/parlay_backtest.py` prices each winning leg at -110 and reduces parlay payout when a leg pushes. Therefore reconstructing total parlay profit solely from the parlay-level win count **overstates** returns: a parlay can be labeled 'win' with one or more individual pushed legs. Leg-level reconstruction remains outstanding.

## Parlay findings that change research priorities
- **Unconstrained combinations**: HGB under edge 3.5 high-total, 3 legs, 5,270 graded combinations, 1,386 wins, 3,884 losses, **+79.66% reported ROI** (all historical). This includes overlapping tickets and is not an independently executable portfolio.
- **Weekly constrained cards**: same family, 2-leg top-1 nonoverlapping, 120 cards, 43–77, **+30.60% reported ROI**; 2-leg top-2 nonoverlapping, 211 cards, 74–137, **+27.82%**; 3-leg top-1 nonoverlapping, 103 cards, 18–85, **+21.59%**.
- These results do **not** prove the model achieves 50% ROI annually. They are potentially biased by historical closing-line selection, correlated same-week legs, repeated source games, selection among strategies, execution/limits, and training-era mismatch.
- The 3-leg high-total strategy's per-season ROI (2016–2024) is approximately: 2016 +27.46%, 2017 +22.01%, 2018 +27.73%, 2019 +0.08%, 2020 +15.16%, 2021 +165.27%, 2022 +122.92%, 2023 +158.44%, 2024 +118.74%. These are **overlapping combinations**, not independently bankrolled tickets.

## Mandatory audit checks before accepting any parlay ROI
- Rebuild each ticket from individual legs, game ID, week, timestamp, market side/line/price, pushes, and settlement rules; ensure no duplicate game or correlated same-game leg.
- Separate **all mathematically possible combinations** from a realistic capped-card strategy (max bets/week, max same-game/week exposure, total risk budget).
- Simulate same-week correlated outcomes; bootstrap by week and season, not by individual overlapping parlay ticket.
- Reprice each leg from actual available bookmaker quotes, and document whether a parlay was offered, maximum stake, and price at decision time.
- Include 2025/2026 forward holdouts and report worst-year ROI and drawdowns. Existing historical selections have been inspected and are not pristine holdouts.
- Test whether combining singles with parlays increases *risk-adjusted* expected profit rather than merely magnifying ROI variance.
- Ensure historical HGB training regime is pinned to `early_stopping=False` and original historical backtest inputs are recoverable.

## Current blocking inputs
- Full historical `modeling_dataset.csv` or equivalent original Actions training artifact; historical per-game forecasts and outcomes; timestamped historical odds; full parlay-leg ledger. Summary CSVs are insufficient to independently rerun model training or verify executable parlays.
- Original audit ZIP is accessible through source Actions, but it is **not** the full training dataset.
- Some imported code has transitive imports absent from the experimental repository. Do not claim it runs as a standalone project.

## Phase 0 exit status
**NOT PASSED.** Summary arithmetic checked and original HGB artifact located; full historical re-training, quote-level and parlay-leg reproduction, and leakage audit remain open. Do not promote any historical ROI into an actionable live strategy.
