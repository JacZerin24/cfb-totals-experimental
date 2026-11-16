"""Tests use fabricated quotes only."""
import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from research.archive_odds import ingest, validate

def sample():
    return dict(source="fixture",source_quote_id="id-1",
                observed_utc="2026-11-14T12:00:00Z",bookmaker="ExampleBook",
                game_id="game-1",kickoff_utc="2026-11-14T18:00:00Z",
                market="game_total",side="under",line="56.5",american_odds="-110",
                provider_quote_utc="2026-11-14T11:59:00Z",home_team="Home",
                away_team="Away")

class ArchiveTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(sample())["side"],"under")
    def test_missing_quote(self):
        r=sample();r["american_odds"]=""
        with self.assertRaises(ValueError):validate(r)
    def test_post_kickoff(self):
        r=sample();r["observed_utc"]="2026-11-14T19:00:00Z"
        with self.assertRaises(ValueError):validate(r)
    def test_future_provider_quote(self):
        r=sample();r["provider_quote_utc"]="2026-11-14T13:00:00Z"
        with self.assertRaises(ValueError):validate(r)
    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as t:
            csv_path=Path(t)/"quotes.csv"; db=Path(t)/"archive.sqlite"
            with csv_path.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=list(sample()))
                writer.writeheader();writer.writerow(sample())
            self.assertEqual(ingest(csv_path,db),(1,0))
            self.assertEqual(ingest(csv_path,db),(0,1))
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM odds_quotes").fetchone()[0],1)

if __name__=="__main__":unittest.main()
