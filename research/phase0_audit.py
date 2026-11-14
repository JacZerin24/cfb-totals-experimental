"""Phase-0 deterministic audit of imported summary artifacts (standard library only).

Run: python -m research.phase0_audit
No network, betting, or production writes.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "reference" / "legacy" / "outputs"


def rows(path: str) -> list[dict]:
    with (REF / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row: dict, key: str) -> float:
    return float(row[key])


def check_settlement(row: dict, wins: str, losses: str, graded: str, hit: str,
                     roi: str, pushes: str | None = None, tolerance: float = 1e-8) -> None:
    w, l, g = (number(row, k) for k in (wins, losses, graded))
    p = number(row, pushes) if pushes else 0.0
    assert w + l == g, (row, "wins + losses != graded")
    assert abs(number(row, hit) - w / g) < tolerance, (row, "hit-rate mismatch")
    expected_roi = (w * (100 / 110) - l) / (g + p)
    assert abs(number(row, roi) - expected_roi) < tolerance, (row, "ROI mismatch")


def parlay_break_even(legs: int, leg_american: int = -110) -> float:
    decimal = 1 + 100 / abs(leg_american)
    return decimal ** (-legs)


def parlay_roi(win: int, loss: int, legs: int) -> float:
    n = win + loss
    return (win * ((1 + 100 / 110) ** legs - 1) - loss) / n


def main() -> None:
    fcs = rows("fcs_selected_screen_by_season.csv")
    for row in fcs:
        check_settlement(row, "wins", "losses", "graded", "hit_rate", "roi_per_1u", "pushes")
    fcs_w = sum(int(r["wins"]) for r in fcs)
    fcs_l = sum(int(r["losses"]) for r in fcs)
    assert (fcs_w, fcs_l) == (41, 32), (fcs_w, fcs_l)

    summary = rows("parlay_backtest_summary.csv")
    for row in summary:
        if not row.get("graded") or int(row["graded"]) == 0:
            continue
        legs = int(row["legs"])
        w, l, p = (int(row[k]) for k in ("wins", "losses", "pushes"))
        g = int(row["graded"])
        assert w + l == g
        assert abs(float(row["breakeven_hit_rate_at_minus_110_legs"]) - parlay_break_even(legs)) < 1e-10
        # A parlay with one or more pushes pays fewer winning legs, so the
        # simple full-odds formula only applies if there are no pushes.
        if p == 0:
            assert abs(float(row["roi_per_1u_parlay"]) - parlay_roi(w, l, legs)) < 1e-9

    by_year = rows("parlay_by_season.csv")
    for row in by_year:
        if int(row["graded"]) == 0:
            continue
        w, l, p, legs = (int(row[k]) for k in ("wins", "losses", "pushes", "legs"))
        assert w + l == int(row["graded"])
        if p == 0:
            assert abs(float(row["roi_per_1u_parlay"]) - parlay_roi(w, l, legs)) < 1e-9

    weekly = rows("weekly_card_backtest_summary.csv")
    for row in weekly:
        if int(row["graded"]) == 0:
            continue
        w, l, p, legs = (int(row[k]) for k in ("wins", "losses", "pushes", "legs"))
        assert w + l == int(row["graded"])
        if p == 0:
            assert abs(float(row["roi_per_card"]) - parlay_roi(w, l, legs)) < 1e-9

    high = next(r for r in summary if r["strategy"] == "hgb_under_3p5_high_total" and r["legs"] == "3")
    assert int(high["graded"]) == 5270
    assert int(high["wins"]) == 1386
    print(f"PASS: FCS historical 41-32; {len(summary)} parlay summaries, "
          f"{len(by_year)} parlay-season rows, {len(weekly)} weekly-card summaries checked.")
    print(f"High-total three-leg historical: {high['graded']} parlays; "
          f"ROI {float(high['roi_per_1u_parlay']):+.2%} (non-independent combinations).")
    print("LIMITATION: verifies arithmetic only; not odds timestamps, independent selections, "
          "historical input integrity, or executable prices.")


if __name__ == "__main__":
    main()
