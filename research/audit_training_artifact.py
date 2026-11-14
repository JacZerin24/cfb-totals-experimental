"""Audit the original GitHub Actions modeling_dataset.csv without altering it.

Usage:
  python research/audit_training_artifact.py /path/to/cfb-live-training-data.zip
  python research/audit_training_artifact.py /path/to/modeling_dataset.csv

Requires pandas. Prints JSON and optionally writes --output.
This audit does NOT establish historical quote or weather-forecast availability.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pandas as pd


def audit(path: Path) -> dict:
    raw = path.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            csv_bytes = archive.read("modeling_dataset.csv")
            member_hashes = {
                info.filename: hashlib.sha256(archive.read(info.filename)).hexdigest()
                for info in archive.infolist() if not info.is_dir()
            }
    else:
        csv_bytes = raw
        member_hashes = {"modeling_dataset.csv": hashlib.sha256(raw).hexdigest()}

    df = pd.read_csv(io.BytesIO(csv_bytes), low_memory=False)
    line = pd.to_numeric(df["closing_total"], errors="coerce").notna()
    score = pd.to_numeric(df["actual_total_points"], errors="coerce").notna()
    valid = line & score
    fbs = df["home_classification"].astype(str).str.lower().eq("fbs") & df["away_classification"].astype(str).str.lower().eq("fbs")
    residual = pd.to_numeric(df.loc[valid, "actual_total_points"], errors="coerce") - pd.to_numeric(df.loc[valid, "closing_total"], errors="coerce")
    mismatch = (~(residual - pd.to_numeric(df.loc[valid, "market_residual"], errors="coerce")).abs().le(1e-6)).sum()

    seasons = []
    for year, group in df.groupby("season"):
        group_fbs = group["home_classification"].astype(str).str.lower().eq("fbs") & group["away_classification"].astype(str).str.lower().eq("fbs")
        seasons.append({
            "season": int(year), "games": int(len(group)),
            "with_lines": int(group["closing_total"].notna().sum()),
            "fbs_vs_fbs_with_lines": int((group_fbs & group["closing_total"].notna()).sum()),
            "with_wind_observation": int(group["wind_mph"].notna().sum()),
        })
    return {
        "input_name": path.name, "input_sha256": hashlib.sha256(raw).hexdigest(),
        "member_sha256": member_hashes, "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "duplicate_game_ids": int(df["game_id"].duplicated().sum()),
        "with_lines": int(line.sum()), "with_scores_and_lines": int(valid.sum()),
        "without_lines": int((~line).sum()),
        "fbs_vs_fbs_with_lines": int((fbs & line).sum()),
        "with_wind_observation": int(df["wind_mph"].notna().sum()),
        "residual_mismatch": int(mismatch),
        "line_providers": {str(k): int(v) for k, v in df["line_provider"].fillna("MISSING").value_counts().items()},
        "season_coverage": seasons,
        "not_proven": ["quote timestamp", "book-specific executable price", "forecast available before kickoff", "feature lineage", "historical model replication"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.input)
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
