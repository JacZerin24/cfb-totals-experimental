# Baseline audit — initial research findings
Date: 2026-11-14. **Descriptive audit only; not a completed independent replication.**

## Verified 2026 production ledger
As of Nov 14, original `outputs/prospective/2026` official summary: 28 qualifiers; 25 settled, 13–12 (52.0%, -0.1818 units, -0.73% ROI at -110); 1 excluded postponed; 2 pending.
- General HGB: 6–7 (46.15%, -11.89% ROI). One General game is FBS-versus-FCS (Texas Southern @ Florida Atlantic), so **comparable FBS-vs-FBS General: 6–6 (50.0%)**.
- FCS-only HGB: 7–5 (58.33%, +11.36% ROI).

## Historical reference baselines
**General HGB**: September 22 2026 successful audit run [35725584192](https://github.com/JacZerin24/cfb-weather-totals/actions/runs/35725584192), `early_stopping=False`, FBS-vs-FBS under, edge >=4, total >=56:
- 2016–2025: 651 selected; 643 graded, 376–267 with 8 pushes; 58.48% win rate and +11.64% flat-stake ROI.
- 2022–2025: 174 selected; 172 graded, 106–66 with 2 pushes; 61.63% win rate and +17.65% ROI.
- 2025: 29–? actually 16–13 on 29 graded; 55.17% and +5.33% ROI.
The FBS 2026 6–6 result is not a statistically significant deviation from the historical 58.48% rate; 12 plays cannot distinguish regime change from chance. Note historical selection uses historical `closing_total`, so it is **not necessarily a bettable early-line benchmark**.
**FCS-only HGB**: 2023–2025 selected-screen-by-season archive, edge >=7.5, total >=56, FCS-vs-FCS. 2023 8–7, 2024 17–14, 2025 16–11; combined 41–32, 56.16%, ~+7.22% ROI. Live 2026 7–5 is consistent with historical.
**Caution:** 2025 and 2026 have been repeatedly inspected during prior development, so they cannot be retroactively treated as pristine model-selection holdouts.

## 2026 prediction calibration diagnostic
From the official graded entries, 25 settled:
- Mean predicted points relative to archived line: -7.76.
- Mean actual points relative to archived line: +3.22.
- Mean signed error (actual minus predicted): +10.98.
- 13 wins averaged 12.04 points below line; 12 losses averaged 19.75 points above line.
- 6 of 12 losses exceeded line by 20+; 3 by 30+.
- General 13 plays: mean signed error +11.64; comparable FBS-vs-FBS 12 plays: +10.83.
- FCS 12 plays: mean signed error +10.28.
**Interpretation:** strong selection-conditioned under-forecast bias; whether abnormal requires exact historical conditional-error distributions under matching model and bet-line timestamps.

## November 7–8 three largest misses
- Youngstown State @ Murray State: 97 points vs 62.5, +34.5 above line; model predicted residual -10.04, signed error +44.54.
- Boise State @ Colorado State: 102 vs 68.5, +33.5; predicted -7.68, error +41.18.
- West Virginia @ Texas Tech: 101 vs 65.5, +35.5; predicted -5.92, error +41.42.
All five weekly qualifiers: mean predicted residual -7.68 vs mean actual residual +17.10, signed error +24.78. **Do not claim statistical anomaly until historical tail frequency is computed.**

## Initial data risks to investigate
1. Historical General model backtests use `closing_total` while live decisions occur before kickoff: possible unrealistic line timing and backtest/live comparability gap.
2. Only 10 of 25 live settled entries have closing-line validation; do not equate apparent predicted edge with independently validated market value.
3. General FBS-vs-FCS classification mismatch in the naive historical comparison.
4. HGB training regime previously differed due to scikit-learn auto early stopping; use the corrected fixed regime and freeze it in every historical replication.
5. Strong negative forecast residuals may be regression-to-the-mean / selection effects; calibrate probability distribution, not raw mean edge alone.

## Research verdict
No evidence yet supports 50%+ yearly ROI at scale. The current results justify further study of market timing, predictive upper tails, FCS execution quality, and team totals. The next scientific deliverable is **reproducing historical and 2026 scoring-error distributions on identical eligible cohorts and decision-time prices**.
