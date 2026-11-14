# CFB Totals Experimental — Research Master Plan
**Created:** 2026-11-14  
**Status:** research only; no betting advice, production deployment, or automatic wagers.

## Mission and target
Discover, validate, and monitor **repeatable positive expected value** in college-football totals, team totals, and related markets, maximizing risk-adjusted profit subject to executable pricing, limits, and data integrity. **50%+ annual ROI with many bets is a stretch hypothesis, not an achievable guarantee or an acceptance criterion.** At -110, 50% flat-stake ROI requires 78.57% wins. Never fabricate an edge, select models by in-sample ROI, or claim certainty.

## Independence and guardrails
- **Source of truth:** `JacZerin24/cfb-weather-totals` remains unchanged. This repo is isolated and research-only. Do not add scheduled production jobs, publish betting picks, or place bets.
- `reference/legacy/` holds copied **snapshots of selected source code and summary artifacts** for provenance, not a runnable fork. Relative imports, dependencies, historical training datasets, archived odds, and weather records are not fully copied. Do not present it as reproducible until all required inputs and lineage are verified.
- Maintain an immutable manifest with source commit SHA, acquisition timestamp, file checksum, data license, event/market timestamps, provider, timezone, missingness, and transformations. Never commit API keys, personal account data, or licensed datasets without permission.
- Preserve original source snapshots; research output lives under `research/` and `reports/`. Never edit the 2026 production ledger or reinterpret a losing game after kickoff.
- Pre-register hypotheses and primary success metrics *before* examining holdout results. Keep 2026 prospective outcomes as a quarantined final test.

## Phases and exit criteria
### Phase 0 — Provenance, replication, and data audit (first)
1. Inventory 2016–2025 FBS and 2023–2025 FCS sources, team identities, odds provider snapshots, opening/closing totals, weather forecasts/observations, kickoff shifts, and data licenses.
2. Obtain original modeling_dataset.csv from the source workflow artifact, plus historic price snapshots, when authorized and available. Build hash-based manifests and stable game IDs. Do not reconstruct historical bettable lines from final scores or current prices.
3. Re-run historical General HGB with **pinned early_stopping=False** and its actual 2026 threshold (edge >=4, total >=56, FBS-vs-FBS). Replicate FCS-only HGB (edge >=7.5, total >=56, FCS-vs-FCS). Check exact feature definitions and fit years.
4. Replicate 2026 ledger: 25 settled as of Nov 14 (13–12 overall); General 6–7 including one FBS-vs-FCS, apples-to-apples FBS-vs-FBS 6–6; FCS 7–5. Keep exclusions and pending separate.
5. Produce data-quality report: duplicate IDs, stale odds, market changes, timestamp leaks, weather issuance times, provider gaps, line availability, postponements, missing or imputed features, and survivorship bias.
**Gate:** All results reproduce to tolerance, no unresolved leakage, executable line coverage documented, original production unchanged.

### Phase 1 — Failure-mode diagnosis
- Calculate residual `actual_total - bet_line`, forecast residual `predicted_total - bet_line`, and signed error `actual - predicted` by season, league, total band, edge band, offense style, tempo, provider, weather, and game time.
- Quantify tail failures (+20/+30/+40 points over line), reliability diagrams, Brier score, log loss, calibration slope/intercept, and uncertainty intervals. Compare the 2026 Nov 7 three extreme losses with the *historical conditional distribution*, not an assumed normal distribution.
- Audit 2026 CLV coverage; do not infer market validation from missing closes.
- Test whether weather is incremental beyond team/market features, and whether forecast quality at decision time matters.
**Gate:** Publish falsifiable root-cause hypotheses, with baseline and uncertainty; no ad hoc threshold changes based on 2026.

### Phase 2 — Independent model families
- **Market-first baseline:** no-vig implied market probabilities, consensus totals, book dispersion, opener-to-decision movement, timing, stale-line filters.
- **Scoring distribution:** possessions × pace × per-drive points; explosive-play, turnover, field position, red-zone, special teams, overtime and blowout dynamics; negative-binomial/mixture and simulation alternatives.
- **Predictive challengers:** regularized GLM/GAM, hierarchical Bayesian, gradient boosting, quantile/distributional boosting, and calibrated ensembles. Include simple market-only and market-plus-team baselines.
- **Team totals:** separately test home/away team total markets and asymmetric pricing; availability, vig, correlated outcomes, and liquidity must be measured.
- **FCS specialist:** account for sparse data, mismatched opponents, venue, low-liquidity odds and delayed injury/roster data; compare with FBS.
- **Weather interactions:** wind * pass rate / air yards, gust direction relative to field, rain intensity, wet-bulb/heat, surface, dome/roof, storm uncertainty; only point-in-time forecasts, not realized weather as a betting feature.
- **Opportunity detection:** independent quote-level opportunities across books, limits, time-to-kickoff, bookmaker disagreement, and price execution; do not assume displayed odds are fillable.\n- **Parlay portfolio research:** compare straight wagers with two-/three-leg and mixed portfolios using actual book prices, leg-level pushes, capped tickets per week, correlated outcomes, per-week exposure and capacity. Treat historical all-combinations ROI as descriptive only, not independently executable returns.
**Gate:** Each challenger must beat market-only and existing HGB baselines on calibration and out-of-sample expected value, not just fitted ROI.

### Phase 3 — Strict validation
- Nested, expanding-window walk-forward by season; train only on past seasons, tune only within training folds; reserve 2025 as a locked historical holdout if it was not already consulted during model selection (otherwise acquire a genuinely unseen future holdout).
- 2026 remains prospective validation; do not use 2026 to tune and then call it an independent test.
- Freeze selection rules: min edge after vig and uncertainty, min available quote count, stale-price cutoff, max stake/market, minimum sample, price range, line timing.
- Publish every candidate, trial, parameter, and outcome; correct for multiple comparisons and winner's curse. Compare performance under transaction costs, worse fills, missing lines, and reduced limits.
- Evaluate **by season**: n, wins, pushes, units, ROI, CLV, expected log growth, drawdown, worst-year ROI, calibration, and 95% confidence intervals. Report losing years prominently. Cluster uncertainty by week/team where relevant.
- Run permutation tests and bootstrap confidence intervals; require robustness to nearby thresholds and independent providers.
**Gate:** Independent out-of-sample performance with positive estimated EV and credible uncertainty, not merely a high backtest ROI.

### Phase 4 — Prospective shadow deployment
- Log every candidate and quote before kickoff with UTC timestamps, model/data hashes, predicted probability, market odds, available limits, rejection reason, and weather issuance metadata.
- Lock rules, collect open/close prices, grade results and audit voids/pushes. Include every eligible game and missed opportunity to avoid cherry-picking.
- Shadow for at least one complete season and enough plays for useful confidence bounds before claiming a durable edge.
- No auto-betting, stake recommendations, or live deployment without separate explicit approval.

## Research scorecard and portfolio controls
Primary: **net realized ROI at actually available odds**, per-season and pooled, with confidence bounds; **positive expected value net of vig**, and out-of-sample calibration. Secondary: number of qualified bets, positive seasons, CLV, max drawdown, market coverage, execution fill rate, correlation among bets, and capacity under limits. Track FBS totals, FCS totals, team totals, and parlay portfolios separately before combining; avoid falsely multiplying independent bet counts or overlapping parlay tickets. An ambitious 50% ROI should be displayed as a stretch benchmark only. A model with 50% historical ROI but fragile validation **fails**.

## Milestone deliverables
- M0: `reports/00_data_provenance.md` and verified reproducibility package.
- M1: `reports/01_baseline_replication.md` with exact historical vs 2026 cohorts.
- M2: `reports/02_calibration_and_tail_risk.md` and diagnostic plots.
- M3: `reports/03_market_opportunity_and_team_totals.md` including executable odds.
- M4: `reports/04_walk_forward_model_bakeoff.md` with leakage-safe tuning.
- M5: `reports/05_prospective_shadow_protocol.md` and frozen evaluation rules.

## Initial hypotheses to preregister
H1: Historical General HGB edge is partly due to model regime or historical line timing rather than stable predictive skill.
H2: General HGB selected unders systematically underestimate the upper tail for high-tempo/explosive offenses.
H3: FCS-only performance is more robust, but market availability/limits reduce realizable profit.
H4: Team-total prices contain asymmetric inefficiencies that survive vig and executable quote constraints.
H5: Forecast weather adds incremental value only through matchup-specific interactions and near-kickoff timing.
H6: Multi-book quote dispersion offers more durable value than increasing complexity of point-total predictions.

## Data acquisition backlog
Required: versioned modeling dataset; original historic odds and line timestamps; season/team/venue IDs; play-by-play or drive-level historical data; forecast weather issuance archives; observed weather for diagnostics only; team totals and book-specific market snapshots; price/limit metadata; injury/roster availability; closing-line benchmarks.
Check provider terms, access, coverage, costs, and historical availability before designing a test. If an input is unavailable, report the limitation and do not substitute future information.

## Immediate next actions
1. Capture source commit SHA and snapshot checksums for all imported reference files.
2. Acquire full original training artifact and historical odds with verifiable timestamps.
3. Write independent baseline replication and deterministic unit tests.
4. Run calibration and tail-risk audit, focusing on the 2026 three 30+-point misses.
5. Draft team-total and market-timing feasibility report before training additional models.
