import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"research"))
from convert_oddspapi_quotes import convert

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.catalog=[{"marketId":"m1","marketType":"totals","period":"result","marketName":"Total (incl. overtime)","handicap":56.5}]
        self.fixture=[{"fixtureId":"f1","startTime":"2026-11-21T20:00:00Z","participant1Name":"A","participant2Name":"B","bookmakerOdds":{"bet365":{"markets":{"m1":{"marketActive":True,"outcomes":{"over":{"players":{"0":{"active":True,"price":-110}}},"under":{"players":{"0":{"active":True,"price":-115}}}}}}}}}}]
    def test_two_sides(self):
        rows,stats=convert(self.catalog,self.fixture,"2026-11-21T15:00:00Z")
        self.assertEqual(len(rows),2)
        self.assertEqual({r["side"] for r in rows},{"over","under"})
        self.assertEqual(stats["accepted"],2)
    def test_ambiguous_outcome_rejected(self):
        self.fixture[0]["bookmakerOdds"]["bet365"]["markets"]["m1"]["outcomes"]={"1":{"players":{"0":{"active":True,"price":-110}}}}
        rows,stats=convert(self.catalog,self.fixture,"2026-11-21T15:00:00Z")
        self.assertFalse(rows)
        self.assertEqual(stats["ambiguous_outcomes"],1)
    def test_post_kickoff_rejected(self):
        rows,stats=convert(self.catalog,self.fixture,"2026-11-21T21:00:00Z")
        self.assertFalse(rows)
        self.assertEqual(stats["invalid"],2)
    def test_team_total_rejected(self):
        self.catalog[0]["marketName"]="Team Total"
        rows,_=convert(self.catalog,self.fixture,"2026-11-21T15:00:00Z")
        self.assertFalse(rows)

if __name__=="__main__":unittest.main()
