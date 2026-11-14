# Phase 0 — Checkpoint 4: source-aligned replay and point-in-time gates
Date: 2026-11-14. **Status: verification scripts committed; exact replay has NOT been executed in the pinned environment.**

## Completed this checkpoint
1. Imported the exact source `src/deep_research.py` and `src/__init__.py` into `reference/legacy/src/` so original preprocessing and HGB model code can be imported without rewriting.
2. Committed `research/replay_hgb_source.py`. This invokes the original `prep`, `feature_lists`, `prep_features`, `walk_forward`, and `grade` functions, and exports game-level predictions and season-level summaries for the original feature set and no-observed-weather ablation.
3. Committed `research/audit_point_in_time.py`, which fails the executable-quote gate when the necessary bookmaker, selection, odds and quote/kickoff timestamps are absent. It also inventories features whose historical availability has not been established.
4. Reopened original `src/build_dataset.py`: the historical `closing_total` is selected by ranking `provider` names and taking the first available `over_under` for each game; no quote timestamps or book-specific prices are preserved. This is a **confirmed data-lineage limitation**, not merely a theoretical concern.
5. No production workflows were changed, no bets were placed, and no historical ROI was promoted to a validated live result.

## Exact replay instructions
From the experimental repository, with original training artifact restored:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r reference/legacy/requirements.txt
bash scripts/restore_historical_training.sh
python research/audit_point_in_time.py data/external/cfb-live-training-data/modeling_dataset.csv --output reports/generated_point_in_time_audit.json
python research/replay_hgb_source.py data/external/cfb-live-training-data/modeling_dataset.csv
```
Compare `reports/generated_source_exact_predictions.csv` against the Sept 22 original audit artifact and compare the season-level summary to the published 376–267, 8 pushes. **The previous diagnostic (378–263, 10 pushes) is not an exact replay** and may reflect different library versions or subtle preprocessing differences. Do not claim an exact match before the above execution and per-game reconciliation.

## Outstanding hard blockers
- Exact original-environment run and game-level reconciliation not yet executed.
- The dataset contains historical provider-selected totals, **not timestamped, priced executable quotes**. This prevents validating actual betting profitability and the feasibility of parlay tickets.
- No verified pregame weather forecast issuance records.
- No independent leg-level historical parlay ticket ledger with quote time, book, odds, pushes and maximum exposures.
- The 2025 and 2026 data have already been examined in model development, so they are not pristine model-selection holdouts.

## Next decisions
A. Run exact source replay and report game-level disagreements (not just total W-L).
B. Audit in-season team statistics and Elo to confirm each feature was known before the selection time.
C. Source point-in-time sportsbook quote archives; if unavailable, label 2016–2025 ROI **unexecutable historical proxy** and use prospective quote collection instead.
D. Reconstruct limited weekly parlay portfolios only after quote-level eligibility is established. Never infer 50% annual ROI from enumerating overlapping combinations.

**Phase 0 exit gate: NOT PASSED.**
