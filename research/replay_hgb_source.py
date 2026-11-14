"""Phase 0: source-aligned HGB replay and weather ablation.

Run from experimental repo:
  python -m pip install -r reference/legacy/requirements.txt
  python research/replay_hgb_source.py data/external/cfb-live-training-data/modeling_dataset.csv

This deliberately imports the *original* model_bakeoff, deep_research,
and hgb_regime_audit code rather than hand-recreating their preprocessing.
Output is diagnostic until historical quote timestamps are verified.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "reference" / "legacy" / "src"
WEATHER_NUM = {"wind_mph", "temperature_f", "humidity", "precipitation", "snowfall", "dewpoint_f", "pressure"}
WEATHER_CAT = {"wind_bin", "temp_bin"}


def load_source_modules():
    # Create a virtual src package rooted in reference/legacy/src so
    # relative imports resolve without installing a production package.
    spec = importlib.util.spec_from_file_location("src", LEGACY / "__init__.py",
                                                  submodule_search_locations=[str(LEGACY)])
    if spec is None or spec.loader is None:
        raise RuntimeError("Missing reference/legacy/src/__init__.py; import it from source first")
    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)
    from src.deep_research import prep
    from src.model_bakeoff import feature_lists, prep_features
    from src.hgb_regime_audit import walk_forward, grade
    return prep, feature_lists, prep_features, walk_forward, grade


def run(dataset: Path, output: Path):
    prep, feature_lists, prep_features, walk_forward, grade = load_source_modules()
    df = prep(pd.read_csv(dataset, low_memory=False))
    nums, cats = feature_lists(df)
    df = prep_features(df, cats)
    output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    for regime in ("source_exact", "no_observed_weather"):
        ns = nums if regime == "source_exact" else [c for c in nums if c not in WEATHER_NUM]
        cs = cats if regime == "source_exact" else [c for c in cats if c not in WEATHER_CAT]
        predictions, diagnostics = walk_forward(df, ns, cs, regime, False)
        if predictions.empty:
            raise RuntimeError("No walk-forward predictions produced")
        predictions["season"] = pd.to_numeric(predictions["season"], errors="coerce")
        fbs = predictions[predictions["fbs_vs_fbs"].astype(bool)]
        for season, group in fbs.groupby("season"):
            eligible = group[(group["closing_total"] >= 56) & (group["pred_market_residual"] <= -4)]
            score = grade(eligible)
            results.append({"regime": regime, "season": int(season), **score})
        pred_cols = [c for c in ["game_id", "season", "closing_total", "actual_total_points",
                                 "pred_market_residual", "fbs_vs_fbs"] if c in predictions]
        predictions[pred_cols].to_csv(output.parent / f"generated_{regime}_predictions.csv", index=False)
        diagnostics.to_csv(output.parent / f"generated_{regime}_diagnostics.csv", index=False)
    frame = pd.DataFrame(results)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    print(json.dumps({"sklearn": sklearn.__version__, "pandas": pd.__version__,
                      "results": frame.groupby("regime")[["games", "graded", "wins", "losses", "pushes", "net_units"]].sum().to_dict("index")}, indent=2))
    return frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/generated_source_replay.csv")
    args = parser.parse_args()
    run(args.dataset, args.output)
