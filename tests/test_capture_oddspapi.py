import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"research"))
from capture_oddspapi import append_encrypted
class EncryptionTests(unittest.TestCase):
    def test_encrypted_append_and_idempotence(self):
        row=dict(source="OddsPapi",source_quote_id="q1",observed_utc="2026-11-21T15:00:00+00:00",
                 bookmaker="bet365",game_id="fixture1",kickoff_utc="2026-11-21T20:00:00+00:00",
                 market="game_total",side="under",line="55.5",american_odds="-110",
                 provider_quote_utc="",home_team="A",away_team="B")
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.assertEqual(append_encrypted([row],root,"synthetic-only-test-key"),1)
            self.assertEqual(append_encrypted([row],root,"synthetic-only-test-key"),0)
            blob=(root/"2026-11-21.enc").read_bytes()
            self.assertNotIn(b"bet365",blob)
            self.assertNotIn(b"-110",blob)
            with self.assertRaises(Exception):
                append_encrypted([row],root,"wrong-key")
if __name__=="__main__":unittest.main()
