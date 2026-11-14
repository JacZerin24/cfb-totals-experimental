"""Point-in-time parlay ticket validator and settlement engine.

Input: CSV with ticket_id,game_id,bookmaker,quote_utc,kickoff_utc,
american_odds,line,side,actual_total,market,stake.
All legs in a ticket must be quoted at the same book before kickoff;
no repeated game within a ticket. Does not prove a book accepted the parlay.
"""
from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {"ticket_id", "game_id", "bookmaker", "quote_utc", "kickoff_utc",
            "american_odds", "line", "side", "actual_total", "market", "stake"}


def parse_time(value: str) -> datetime:
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("Timezone required for all quote and kickoff timestamps")
    return t.astimezone(timezone.utc)


def decimal_odds(american: float) -> float:
    if american == 0 or -100 < american < 100:
        raise ValueError("Invalid American odds; expected <= -100 or >= +100")
    return 1 + (american / 100 if american > 0 else 100 / abs(american))


def settle_leg(row: dict) -> str:
    total, line = float(row["actual_total"]), float(row["line"])
    side = row["side"].strip().lower()
    if side not in {"under", "over"}:
        raise ValueError(f"Unsupported side {side!r}")
    if total == line:
        return "push"
    won = total < line if side == "under" else total > line
    return "win" if won else "loss"


def settle_ticket(legs: list[dict]) -> dict:
    if not 2 <= len(legs) <= 3:
        raise ValueError("Research engine accepts 2- or 3-leg parlays only")
    games = [x["game_id"] for x in legs]
    if len(set(games)) != len(games):
        raise ValueError("Repeated game in same ticket")
    books = {x["bookmaker"] for x in legs}
    if len(books) != 1:
        raise ValueError("Mixed-book parlay not executable")
    stakes = {float(x["stake"]) for x in legs}
    if len(stakes) != 1 or min(stakes) <= 0:
        raise ValueError("Stake must be positive and identical across legs")
    if any(x["market"].strip().lower() != "game_total" for x in legs):
        raise ValueError("Only full-game total markets supported")
    times = [parse_time(x["quote_utc"]) for x in legs]
    if any(parse_time(x["quote_utc"]) >= parse_time(x["kickoff_utc"]) for x in legs):
        raise ValueError("Quote must precede kickoff")
    # One ticket decision time: all quoted legs must still be available then.
    # Without quote-expiry snapshots, availability cannot be proven; enforce
    # a conservative maximum quote age as an explicit research assumption.
    decision = max(times)
    if any((decision - t).total_seconds() > 300 for t in times):
        raise ValueError("Quotes differ by more than five minutes")
    status = [settle_leg(x) for x in legs]
    stake = stakes.pop()
    if "loss" in status:
        profit = -stake
        result = "loss"
    elif all(s == "push" for s in status):
        profit = 0.0
        result = "push"
    else:
        multiplier = 1.0
        for row, outcome in zip(legs, status):
            if outcome == "win":
                multiplier *= decimal_odds(float(row["american_odds"]))
        profit = stake * (multiplier - 1)
        result = "win"
    return {"ticket_id": legs[0]["ticket_id"], "bookmaker": next(iter(books)),
            "legs": len(legs), "wins": status.count("win"), "pushes": status.count("push"),
            "result": result, "stake": stake, "profit": round(profit, 8),
            "decision_utc": decision.isoformat(),
            "quote_verified_executable": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    with args.csv.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing fields: {sorted(missing)}")
        rows = list(reader)
    groups = {}
    for row in rows:
        groups.setdefault(row["ticket_id"], []).append(row)
    result = [settle_ticket(legs) for legs in groups.values()]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(result[0]) if result else [])
            if result:
                writer.writeheader()
                writer.writerows(result)
    print(json.dumps({"tickets": len(result), "settled": result,
                      "warning": "Quote timestamps and prices supplied by input; executable parlay acceptance and limits NOT proven."}, indent=2))


if __name__ == "__main__":
    main()
