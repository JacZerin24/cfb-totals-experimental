"""Run frozen HGB robustness comparisons using imported original model code."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from replay_hgb_source import load_source_modules, WEATHER_NUM, WEATHER_CAT

def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--output", type=Path, default=Path("reports/generated_sensitivity.csv"))
    a = p.parse_args()
    prep, feature_lists, prep_features, walk_forward, grade = load_source_modules()
    df = prep(pd.read_csv(a.dataset, low_memory=False))
    nums, cats = feature_lists(df)
    df = prep_features(df, cats)
    prior = [c for c in nums if c.startswith(("home_prior_", "away_prior_"))]
    configs = {
        "no_provider": (nums, [c for c in cats if c != "line_provider"]),
        "no_weather_no_provider": ([c for c in nums if c not in WEATHER_NUM],
                                  [c for c in cats if c not in WEATHER_CAT and c != "line_provider"]),
        "complete_prior_only": (nums, cats),
    }
    rows = []
    for regime, (ns, cs) in configs.items():
        pred, diagnostics = walk_forward(df, ns, cs, regime, False)
        if pred.empty:
            raise RuntimeError("Empty walk-forward predictions")
        fbs = pred[pred.fbs_vs_fbs.astype(bool)].copy()
        if regime == "complete_prior_only":
            if not prior:
                raise RuntimeError("No prior feature columns")
            fbs = fbs[fbs[prior].notna().all(axis=1)]
        for year, cohort in fbs.groupby("season"):
            eligible = cohort[(cohort.closing_total >= 56) & (cohort.pred_market_residual <= -4)]
            rows.append(dict(regime=regime, season=int(year), **grade(eligible)))
        a.output.parent.mkdir(parents=True, exist_ok=True)
        pred[[c for c in ("game_id","season","line_provider","closing_total",
                          "actual_total_points","pred_market_residual","fbs_vs_fbs") if c in pred]].to_csv(
                              a.output.parent / ("generated_" + regime + "_predictions.csv"), index=False)
        diagnostics.to_csv(a.output.parent / ("generated_" + regime + "_diagnostics.csv"), index=False)
    out = pd.DataFrame(rows)
    out.to_csv(a.output, index=False)
    for name, group in out.groupby("regime"):
        wins, losses = group.wins.sum(), group.losses.sum()
        print(name, "games", group.games.sum(), "W-L", wins, losses,
              "ROI", round((wins * 100 / 110 - losses) / (wins + losses), 6) if wins + losses else None)

if __name__ == "__main__":
    main()
