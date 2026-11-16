# Phase 0 — Completed pinned robustness experiments
Date: 2026-11-16

## Verified CI
[Successful workflow run 43926032290](https://github.com/JacZerin24/cfb-totals-experimental/actions/runs/43926032290), job 133505616646. All steps passed, including **14 synthetic unit tests** and source HGB benchmark replication. Diagnostic artifact ID `14255881876` (30-day retention).

## Frozen HGB threshold: FBS vs FBS under, predicted residual <= -4, total >=56
All returns below assume flat -110 odds and exclude pushes from ROI denominator. **These are hypothetical, not verified executable bets.**

| Regime | Selected games | Wins | Losses | Graded | ROI |
|---|---:|---:|---:|---:|---:|
| Original source features | 651 | 376 | 267 | 643 | +11.6358% |
| No observed weather | 752 | 424 | 315 | 739 | +9.5338% |
| No provider feature | 682 | 386 | 289 | 675 | +9.1717% |
| No observed weather or provider | 729 | 413 | 308 | 721 | +9.3557% |
| Complete prior-stat eligibility | 497 | 291 | 200 | 491 | +13.1457% |

Complete-prior test **filters evaluation rows only**, with the original model trained on all available prior-season rows; it does not represent a separately trained complete-case model.

## Interpretation
Removing observed weather and `line_provider` leaves a positive historical association, but both may be retrospectively available. The original model has the highest full-cohort fixed-odds ROI among these variants. The complete-prior subset is smaller and selected on feature completeness, which may correlate with season and market availability. This is **not** evidence of a validated 50% annual ROI, executable parlay profits, or an untouched holdout.

The model has been evaluated and developed on overlapping historical years; these sensitivity checks are diagnostic rather than fresh out-of-sample confirmation. Source archived line data lacks timestamps and actual bookmaker prices. Historical results must remain labeled hypothetical.

## Phase 0 decision
**Predictive historical reproduction and basic robustness checks: PASSED.**
**Point-in-time quote/feature availability and executable profitability: NOT VALIDATED.**
Proceed with an authorized odds feed, prospective pre-kickoff immutable quote ledger and a frozen model-selection protocol. Do not label Phase 0 fully complete without these external data dependencies.
