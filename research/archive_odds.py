"""Append-only, timestamped prospective full-game totals quote archive.

Input CSV columns:
source,source_quote_id,observed_utc,bookmaker,game_id,kickoff_utc,
market,side,line,american_odds
Optional: provider_quote_utc,home_team,away_team.
Run: python research/archive_odds.py --input quotes.csv --database data/external/odds.sqlite

Only ingests supplied quotes. Never scrapes, invents prices, or overwrites history.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import sqlite3
from pathlib import Path

FIELDS = ("source","source_quote_id","observed_utc","bookmaker","game_id",
          "kickoff_utc","market","side","line","american_odds")
OPTIONAL = ("provider_quote_utc","home_team","away_team")
ALL = FIELDS + OPTIONAL

def utc(value: str) -> str:
    if not value:
        raise ValueError("Timestamp missing")
    x = dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    if x.tzinfo is None:
        raise ValueError("Timestamp must include UTC offset")
    return x.astimezone(dt.timezone.utc).isoformat()

def validate(row: dict) -> dict:
    for col in FIELDS:
        if not str(row.get(col,"")).strip():
            raise ValueError("Missing required field: " + col)
    x = {k:str(row.get(k,"")).strip() for k in ALL}
    x["observed_utc"] = utc(x["observed_utc"])
    x["kickoff_utc"] = utc(x["kickoff_utc"])
    if x["provider_quote_utc"]:
        x["provider_quote_utc"] = utc(x["provider_quote_utc"])
        if x["provider_quote_utc"] > x["observed_utc"]:
            raise ValueError("Provider quote time after observed time")
    if x["observed_utc"] >= x["kickoff_utc"]:
        raise ValueError("Quote observed at or after kickoff")
    if x["market"] != "game_total" or x["side"].lower() not in ("under","over"):
        raise ValueError("Only game_total under/over supported")
    x["side"] = x["side"].lower()
    if not 0 < float(x["line"]) < 200:
        raise ValueError("Invalid total")
    odds = float(x["american_odds"])
    if not (odds <= -100 or odds >= 100):
        raise ValueError("Invalid American odds")
    return x

def ingest(path: Path, database: Path) -> tuple[int,int]:
    with path.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError("Missing columns: "+str(set(FIELDS)-set(reader.fieldnames or [])))
        records=[validate(row) for row in reader]
    database.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(database)
    try:
        con.execute("""CREATE TABLE IF NOT EXISTS odds_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL, source_quote_id TEXT NOT NULL,
            observed_utc TEXT NOT NULL, bookmaker TEXT NOT NULL,
            game_id TEXT NOT NULL, kickoff_utc TEXT NOT NULL,
            market TEXT NOT NULL, side TEXT NOT NULL,
            line TEXT NOT NULL, american_odds TEXT NOT NULL,
            provider_quote_utc TEXT, home_team TEXT, away_team TEXT,
            UNIQUE(source,source_quote_id,observed_utc,bookmaker,game_id,market,side,line,american_odds)
        )""")
        before=con.total_changes
        with con:
            con.executemany("""INSERT OR IGNORE INTO odds_quotes
            (source,source_quote_id,observed_utc,bookmaker,game_id,kickoff_utc,
             market,side,line,american_odds,provider_quote_utc,home_team,away_team)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
             [tuple(x[k] for k in ALL) for x in records])
        inserted=con.total_changes-before
        return inserted,len(records)-inserted
    finally:
        con.close()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--database",type=Path,default=Path("data/external/odds.sqlite"))
    a=p.parse_args()
    inserted,duplicate=ingest(a.input,a.database)
    print(f"Archived {inserted} quotes; skipped {duplicate} duplicate rows")
