"""Synthetic unit tests; no betting history or live odds are assumed."""
import unittest
from research.parlay_ticket_audit import decimal_odds, settle_ticket


def leg(game, result, *, book="BookA", odds="-110", side="under", line="55.5",
        quote="2026-10-01T15:00:00Z", kickoff="2026-10-01T18:00:00Z"):
    return dict(ticket_id="synthetic-1", game_id=game, bookmaker=book,
                quote_utc=quote, kickoff_utc=kickoff, american_odds=odds,
                line=line, side=side, actual_total=str(result),
                market="game_total", stake="1")


class TicketTests(unittest.TestCase):
    def test_odds(self):
        self.assertAlmostEqual(decimal_odds(-110), 1 + 100 / 110)
        self.assertAlmostEqual(decimal_odds(150), 2.5)

    def test_two_leg_win(self):
        out = settle_ticket([leg("1", 50), leg("2", 49)])
        self.assertEqual(out["result"], "win")
        self.assertAlmostEqual(out["profit"], (1 + 100 / 110)**2 - 1)
        self.assertFalse(out["quote_verified_executable"])

    def test_loss(self):
        self.assertEqual(settle_ticket([leg("1", 60), leg("2", 50)])["profit"], -1)

    def test_push_reduces_odds(self):
        out = settle_ticket([leg("1", 55.5), leg("2", 50)])
        self.assertEqual(out["pushes"], 1)
        self.assertAlmostEqual(out["profit"], 100 / 110)

    def test_all_push(self):
        self.assertEqual(settle_ticket([leg("1", 55.5), leg("2", 55.5)])["profit"], 0)

    def test_repeated_game_rejected(self):
        with self.assertRaises(ValueError):
            settle_ticket([leg("1", 50), leg("1", 51)])

    def test_mixed_book_rejected(self):
        with self.assertRaises(ValueError):
            settle_ticket([leg("1", 50), leg("2", 50, book="BookB")])

    def test_postkickoff_quote_rejected(self):
        with self.assertRaises(ValueError):
            settle_ticket([leg("1", 50, quote="2026-10-01T19:00:00Z"), leg("2", 50)])

    def test_stale_quote_rejected(self):
        with self.assertRaises(ValueError):
            settle_ticket([leg("1", 50), leg("2", 50, quote="2026-10-01T15:10:00Z")])


if __name__ == "__main__":
    unittest.main()
