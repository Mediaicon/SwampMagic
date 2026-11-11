import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import content
import dialog
import game as game_module
import ui
from game import Game
from player import Player

ui.CLEAR_SCREEN = False
game_module.SAVE_DIR = tempfile.mkdtemp()   # tests never touch real saves


def new_game():
    return Game(content.load())


def run_quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), mock.patch("ui.pause", lambda: None):
        fn(*a, **k)
    return buf.getvalue()


def ask(game, npc_id, topic_id):
    return run_quiet(dialog.ask_topic, game, game.npcs[npc_id], topic_id)


class Script:
    """Drive ui.menu by label substring: the next scripted choice picks the first
    menu label that contains it."""
    def __init__(self, choices):
        self.choices = list(choices)

    def __call__(self, labels, prompt="> "):
        if not self.choices:
            raise ui.QuitGame()
        want = self.choices.pop(0)
        for i, label in enumerate(labels):
            if want.lower() in label.lower():
                return i
        raise AssertionError(f"'{want}' not in menu {labels}")


class ContentTests(unittest.TestCase):
    def test_content_validates(self):
        self.assertEqual(content.validate(content.load()), [])


class TopicTests(unittest.TestCase):
    def test_topic_discovery_is_global(self):
        g = new_game()
        self.assertNotIn("original_preacher", g.player.topics)
        out = run_quiet(g.learn_topic, "original_preacher")
        self.assertIn("NEW TOPIC DISCOVERED", out)
        self.assertIn("original_preacher", g.player.topics)
        # every NPC can now be asked, each answers differently
        a = ask(g, "storekeeper", "original_preacher")
        b = ask(g, "old_woman", "original_preacher")
        self.assertNotEqual(a, b)

    def test_looking_around_the_dock_reveals_the_preacher(self):
        g = new_game()
        run_quiet(g.look)
        self.assertIn("original_preacher", g.player.topics)
        self.assertIn("faded_handbill", g.player.clues)


class TrustTests(unittest.TestCase):
    def setUp(self):
        self.g = new_game()
        self.g.learn_topic = mock.Mock(wraps=self.g.learn_topic)
        run_quiet(self.g.learn_topic, "original_preacher")

    def test_low_trust_locks_information(self):
        out = ask(self.g, "ferryman", "original_preacher")
        self.assertIn("Don’t concern yourself", out)
        self.assertEqual(self.g.player.claims, [])

    def test_trust_unlocks_tiers(self):
        self.g.player.trust["ferryman"] = 1
        self.assertIn("nobody asks why he left", ask(self.g, "ferryman", "original_preacher"))
        self.g.player.trust["ferryman"] = 3
        self.assertIn("something he learned", ask(self.g, "ferryman", "original_preacher"))
        self.assertIn("preacher_knowledge", self.g.player.topics)

    def test_rapport_once_per_day(self):
        npc = self.g.npcs["ferryman"]
        run_quiet(dialog.spend_time, self.g, npc)
        self.assertEqual(self.g.raw_trust("ferryman"), 1)
        out = run_quiet(dialog.spend_time, self.g, npc)
        self.assertIn("already spent time", out)
        self.assertEqual(self.g.raw_trust("ferryman"), 1)
        self.g.player.day += 1
        run_quiet(dialog.spend_time, self.g, npc)
        self.assertEqual(self.g.raw_trust("ferryman"), 2)

    def test_effects_cannot_be_farmed(self):
        self.g.player.trust["ferryman"] = 3
        for _ in range(3):
            ask(self.g, "ferryman", "original_preacher")
        self.assertEqual(self.g.player.awareness, 2)  # +2 once, not +6

    def test_belonging_penalty_hits_ordinary_npcs_only(self):
        g = self.g
        g.player.trust.update({"storekeeper": 3, "ferryman": 3})
        self.assertEqual(g.effective_trust("storekeeper"), 3)
        g.player.awareness = 20
        self.assertEqual(g.effective_trust("storekeeper"), 1)
        self.assertEqual(g.effective_trust("ferryman"), 3)

    def test_high_awareness_can_relock_an_ordinary_npc(self):
        g = self.g
        g.player.trust["storekeeper"] = 3
        g.player.awareness = 30           # penalty 3 -> effective 0
        ask(g, "storekeeper", "original_preacher")
        self.assertNotIn("candle_ledger", g.player.clues)


class AwarenessTests(unittest.TestCase):
    def test_hidden_checks(self):
        g = new_game()
        low = run_quiet(g.scene)
        self.assertNotIn("thicker near the church road", low)
        g.player.awareness = 20
        high = run_quiet(g.scene)
        self.assertIn("thicker near the church road", high)

    def test_green_eye_matches_design_example(self):
        import awareness
        self.assertEqual(awareness.eye(0), "(-----)")
        self.assertEqual(awareness.eye(15), "(oo---)")

    def test_resting_gets_worse_as_awareness_grows(self):
        g = new_game()
        g.player.fatigue = 5
        g.player.period = 3
        run_quiet(g.rest)
        self.assertEqual(g.player.fatigue, 2)
        g.player.awareness, g.player.period = 25, 3
        run_quiet(g.rest)
        self.assertEqual(g.player.fatigue, 3)

    def test_clue_details_depend_on_awareness(self):
        import journal
        g = new_game()
        run_quiet(g.add_clue, "rusted_iron_cross")
        self.assertNotIn("groove", run_quiet(journal.render, g))
        g.player.awareness = 12
        self.assertIn("groove", run_quiet(journal.render, g))


class InvestigationTests(unittest.TestCase):
    def setUp(self):
        self.g = new_game()
        run_quiet(self.g.learn_topic, "original_preacher")
        self.g.player.trust["ferryman"] = 1

    def test_contradiction_is_noticed_and_rewarded_once(self):
        g = self.g
        ask(g, "storekeeper", "ferry_landing")
        g.player.awareness = 10
        out = ask(g, "ferryman", "ferry_landing")
        self.assertIn("Two accounts do not agree", out)
        self.assertEqual(len(g.contradictions()), 1)
        self.assertEqual(g.player.awareness, 11)
        ask(g, "ferryman", "ferry_landing")
        self.assertEqual(g.player.awareness, 11)

    def test_same_person_can_contradict_themselves(self):
        g = self.g
        g.player.trust["storekeeper"] = 3
        run_quiet(g.learn_topic, "church_fire")
        ask(g, "storekeeper", "church_fire")      # trust>=3 gives the doubtful line
        g.player.trust["storekeeper"] = 0
        ask(g, "storekeeper", "church_fire")      # now the sensible-story line
        self.assertEqual(len(g.contradictions()), 1)

    def test_case_needs_accounts_and_physical_evidence(self):
        g = self.g
        ask(g, "storekeeper", "original_preacher")
        ask(g, "ferryman", "original_preacher")
        self.assertNotIn("preacher_departure", g.player.assembled)
        out = run_quiet(g.add_clue, "rusted_iron_cross")
        self.assertIn("preacher_departure", g.player.assembled)
        self.assertIn("You could stop here.", out)

    def test_case_never_declares_an_answer(self):
        import journal
        g = self.g
        ask(g, "storekeeper", "original_preacher")
        ask(g, "ferryman", "original_preacher")
        run_quiet(g.add_clue, "rusted_iron_cross")
        with mock.patch("ui.menu", Script(["Settle", "Believe none"])), \
             contextlib.redirect_stdout(io.StringIO()), mock.patch("ui.pause", lambda: None), \
             self.assertRaises(ui.QuitGame):
            journal.show(g)  # choose belief, then QuitGame from the empty script
        belief = g.player.beliefs["preacher_departure"]
        self.assertEqual(belief["kind"], "none")

    def test_assembling_costs_belonging_and_can_be_abandoned(self):
        g = self.g
        g.player.trust["storekeeper"] = 3
        before = g.effective_trust("storekeeper")
        g.player.assembled.append("preacher_departure")
        self.assertEqual(g.effective_trust("storekeeper"), before - 1)


class SaveTests(unittest.TestCase):
    def test_roundtrip(self):
        g = new_game()
        run_quiet(g.look)
        g.player.trust["ferryman"] = 2
        g.player.flags.add("stopped_asking")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(game_module, "SAVE_DIR", d):
            g.save("t")
            p = Game.load_player("t")
        self.assertEqual(p.to_dict(), g.player.to_dict())
        self.assertIsInstance(p.flags, set)


class PlaythroughSmoke(unittest.TestCase):
    def test_scripted_session(self):
        g = new_game()
        script = Script([
            "Look around",                       # dock: handbill + topics
            "Talk to the ferryman", "Ask about Ferry Landing", "Spend time", "Leave",
            "Travel", "Landing Square",
            "Talk to the old woman", "Ask about Ferry Landing", "Leave",
            "Travel", "Church Road",
            "Look around",                       # iron cross
            "Journal", "Back",
            "Travel", "Follow the road",
            "Menu", "Quit without saving",
        ])
        with mock.patch("ui.menu", script), mock.patch("ui.pause", lambda: None), \
             contextlib.redirect_stdout(io.StringIO()), \
             mock.patch.object(game_module, "SAVE_DIR", tempfile.mkdtemp()):
            g.run()
        self.assertEqual(g.player.location, "church_road")
        self.assertIn("rusted_iron_cross", g.player.clues)
        self.assertEqual(script.choices, [])


if __name__ == "__main__":
    unittest.main()
