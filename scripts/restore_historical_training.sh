#!/usr/bin/env bash
# Phase-0 data acquisition. Run manually with authenticated gh CLI.
# Reads the source repository's existing Actions artifact; never dispatches a workflow.
set -euo pipefail
SOURCE_REPO="JacZerin24/cfb-weather-totals"
RUN_ID="43613392785"
ARTIFACT="cfb-live-training-data"
OUT="${1:-data/external/cfb-live-training-data}"
mkdir -p "$OUT"
command -v gh >/dev/null || { echo "Install GitHub CLI (gh)"; exit 2; }
gh auth status >/dev/null
gh run download "$RUN_ID" --repo "$SOURCE_REPO" --name "$ARTIFACT" --dir "$OUT"
test -s "$OUT/modeling_dataset.csv"
echo "Downloaded read-only source artifact to $OUT"
python research/audit_training_artifact.py "$OUT/modeling_dataset.csv" --output reports/generated_training_data_audit.json
echo "No files were modified in $SOURCE_REPO"
