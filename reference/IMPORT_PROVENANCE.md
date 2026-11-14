# Import provenance — 2026-11-14

Source repository: https://github.com/JacZerin24/cfb-weather-totals
Source main SHA observed after import: `d9501b777ed4dfe1c25994a74082d874340d6557` (2026-11-14 07:44:30 UTC). This is **not** asserted to be the exact SHA for every imported file: individual fetches occurred over several commits, and per-file SHA/checksum verification remains a required task.

Destination: https://github.com/JacZerin24/cfb-totals-experimental

17 source files copied under `reference/legacy/`, retaining their original relative paths. They include:
- `src/`: hgb_regime_audit.py, model_bakeoff.py, fcs_model.py, fcs_research.py, weekly_card_backtest.py, prospective_ledger.py, validate_model_edges.py, build_dataset.py, inseason_features.py, utils.py
- `config/`: prospective_protocol_2026.yml
- `outputs/`: fcs_research_summary.md, fcs_selected_screen_by_season.csv, weekly_card_backtest_by_season.csv, prospective/2026/summary.csv
- `documentation/`: HGB_TRAINING_REGIME_AUDIT.md
- `requirements.txt`

**Excluded intentionally:** secrets, live workflow schedules, production deployments, original historical training artifact, all original odds/weather archives, original snapshot corpus, and non-relevant NFL code.

**Reproducibility limitation:** The snapshot is an annotated starting point, not a fully runnable fork. Imported scripts may require additional modules or datasets and should not be executed as-is. The baseline report references original GitHub Actions logs for historical General HGB numbers, which are not stored here.

**Next:** Pin the source SHA for each file, compute cryptographic checksums, obtain and validate data licenses, and reproduce historical results in a self-contained research pipeline.
