"""Inspect source training artifact coverage and market/feature availability.

Usage: python research/audit_market_coverage.py path/to/modeling_dataset.csv
This is a structural audit; it cannot infer missing quote timestamps.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def audit(path: Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    quoted = df[df["closing_total"].notna()].copy()
    quoted["kickoff_utc"] = pd.to_datetime(quoted["start_date"], utc=True, errors="coerce")
    prior = [c for c in df if c.startswith("home_prior_")]
    years = []
    for season, games in df.groupby("season"):
        lines = games[games["closing_total"].notna()]
        both_fbs = lines["home_classification"].astype(str).str.lower().eq("fbs") & lines["away_classification"].astype(str).str.lower().eq("fbs")
        years.append({
            "season": int(season), "games": int(len(games)),
            "games_with_total": int(len(lines)),
            "line_coverage_pct": round(100 * len(lines) / len(games), 2),
            "fbs_vs_fbs_with_total": int(both_fbs.sum()),
            "wind_observation_coverage_pct": round(100 * lines["wind_mph"].notna().mean(), 2),
            "prior_feature_coverage_pct": round(100 * lines[prior].notna().any(axis=1).mean(), 2) if prior else 0,
        })
    providers = quoted.groupby("line_provider", dropna=False).agg(
        games=("game_id", "count"), earliest=("season", "min"), latest=("season", "max")
    ).sort_values("games", ascending=False).reset_index()
    return {
        "rows": int(len(df)), "games_with_total": int(len(quoted)),
        "with_parseable_kickoff": int(quoted["kickoff_utc"].notna().sum()),
        "duplicate_game_ids": int(df["game_id"].duplicated().sum()),
        "prior_feature_columns": len([c for c in df if c.startswith(("home_prior_", "away_prior_"))]),
        "inseason_feature_columns": len([c for c in df if c.startswith(("home_inseason_", "away_inseason_"))]),
        "quote_timestamp_columns": [c for c in df if "quote" in c.lower() or "odds_timestamp" in c.lower() or "line_timestamp" in c.lower()],
        "bookmaker_price_columns": [c for c in df if "american_odds" in c.lower() or "under_price" in c.lower() or "over_price" in c.lower()],
        "by_season": years,
        "line_providers": providers.to_dict("records"),
        "conclusion": "Historical total points exist, but bookmaker quote time, price and executable parlay availability are not demonstrated.",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = json.dumps(audit(args.dataset), indent=2, default=str) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)
    print(result)
