"""Phase 0 audit of betting-line and feature point-in-time availability.

Usage: python research/audit_point_in_time.py path/to/modeling_dataset.csv
Never upgrades a historical line to a verified executable quote.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED_QUOTE = ("bookmaker", "market", "selection", "line", "american_odds",
                  "quote_timestamp_utc", "kickoff_timestamp_utc")
POTENTIAL_LEAKAGE = {
    "closing_total": "Retrospective provider-ranked line, quote time not preserved",
    "line_provider": "Retrospective chosen-provider identifier; availability at decision time not demonstrated",
    "wind_mph": "Historical game weather observation, not pregame forecast",
    "temperature_f": "Historical game weather observation, not pregame forecast",
    "humidity": "Historical game weather observation, not pregame forecast",
    "precipitation": "Historical game weather observation, not pregame forecast",
    "snowfall": "Historical game weather observation, not pregame forecast",
    "dewpoint_f": "Historical game weather observation, not pregame forecast",
    "pressure": "Historical game weather observation, not pregame forecast",
    "wind_bin": "Derived from historical weather observations",
    "temp_bin": "Derived from historical weather observations",
}
def audit(path: Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    missing = [x for x in REQUIRED_QUOTE if x not in df.columns]
    actual = {k: {"present": k in df.columns,
                  "non_null": int(df[k].notna().sum()) if k in df else 0,
                  "risk": v} for k, v in POTENTIAL_LEAKAGE.items()}
    return {"rows": len(df), "quote_fields_missing": missing,
            "historical_quotes_executable": not missing,
            "feature_risks": actual,
            "conclusion": "No proof of executable historical betting prices" if missing else
                "Fields present; timestamps and quotes still require validation"}
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    s = json.dumps(audit(a.dataset), indent=2) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(s)
    print(s)
