# CFB Totals Experimental

**Independent, research-only laboratory** for college football totals, team totals, market timing, and weather-related pricing inefficiencies.

**Source production repository:** [cfb-weather-totals](https://github.com/JacZerin24/cfb-weather-totals). This experimental repository does **not** modify, deploy, or replace the source system.

## Start here
Read the [comprehensive research plan](RESEARCH_PLAN.md). It defines the project goals, prioritized hypotheses, required data, leakage safeguards, historical walk-forward testing, calibration diagnostics, and prospective validation gates.

## Current state (November 14, 2026)
- Bootstrapped a **selective, static snapshot** of 24 source files under [reference/legacy](reference/legacy): modeling and verification code, FCS historical summaries, historical weekly and parlay results, frozen 2026 protocol, and 2026 prospective summary.
- These files are **reference artifacts, not a complete runnable copy**. Historical training datasets, archived odds, all transitive code dependencies, and original GitHub Actions artifacts have not yet been imported.
- No production GitHub Actions, automatic wagers, sportsbook integrations, or live prediction workflows are installed.
- The original repository and its frozen 2026 prospective ledger remain untouched.

## Guiding principle
A 50%+ annual ROI with many playable bets is an **aspirational stress-test**, not a promise. At -110, that would require about a 78.6% win rate. The system will prioritize honest, point-in-time, executable out-of-sample performance rather than optimized backtests.

**Phase 0 progress:** [Original training artifact audit](reports/00_phase0_training_data_audit.md) and [executed historical weather ablation](reports/00_phase0_weather_ablation.md). The training dataset has been recovered, but exact environment replication and historical executable odds are still outstanding. [Earlier parlay checkpoint](reports/00_phase0_checkpoint.md).\n\n## Research workstreams
1. Data lineage and independent reproduction.
2. Historical-to-2026 calibration and extreme-miss diagnosis.
3. Market-first and probabilistic possession-based totals models.
4. FCS and team-total market research.
5. Weather-by-matchup interaction models.
6. Strict walk-forward validation, bookmaker price realism, and prospective shadow tracking.

**Next blockers:** reproduce historical results with the source's pinned scikit-learn environment and acquire historical timestamped sportsbook quotes and archived pregame forecasts. The historical training artifact is recovered and independently audited.
