"""Headless tests for the pygame front-end (SDL dummy driver, no window)."""
import os
import sys
import tempfile
import unittest
from collections import deque
from unittest import mock

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

import character
import content
import game as game_module
import ui
from origin import CREATION_MAX_RANK, CREATION_POINTS, SKILL_IDS

game_module.SAVE_DIR = tempfile.mkdtemp()

from game import Game
from gfx import overworld, sheet, world
from gfx.app import App
from gfx.backend import TextPanel
from gfx.journal_view import JournalView


class CharacterRules(unittest.TestCase):
    def setUp(self):
        self.c = content.load()

    def test_every_origin_is_valid_and_leaves_room_to_grow(self):
        for o in self.c.origins.values():
            self.assertEqual(set(o.skills), set(SKILL_IDS))
            self.assertTrue(all(v <= CREATION_MAX_RANK - 1 for v in o.skills.values()))

    def test_point_buy(self):
        o = self.c.origins["occult_researcher"]            # lore 3
        a = {"lore": 1}
        self.assertFalse(character.can_add(o, a, "lore"))   # would exceed max rank
        self.assertTrue(character.can_add(o, a, "rapport"))
        a.update({"rapport": 2})
        self.assertEqual(character.points_left(a), 0)
        self.assertTrue(character.valid(o, a))
        self.assertFalse(character.can_add(o, a, "perception"))

    def test_build_player(self):
        o = self.c.origins["deputy"]
        p = character.build_player("  Matt ", o, {"resolve": 3}, "ferry_dock", self.c.start_topics)
        self.assertEqual(p.name, "Matt")
        self.assertEqual(p.skills["resolve"], 4)
        self.assertIn("new_preacher", p.topics)
        self.assertIn("ferry_landing", p.topics)
        self.assertEqual(character.build_player("", o, {}, "x", ()).name, "Stranger")

    def test_skills_change_play_without_touching_awareness(self):
        g = Game(content.load())
        g.player.trust["ferryman"] = 2
        self.assertEqual(g.effective_trust("ferryman"), 2)
        g.player.skills["rapport"] = 2
        self.assertEqual(g.effective_trust("ferryman"), 3)
        self.assertEqual(g.player.awareness, 0)
        g.player.skills["perception"] = 2
        from rules import W
        self.assertTrue(W(min_skills=(("perception", 2),)).check(g))
        self.assertFalse(W(min_skills=(("perception", 3),)).check(g))

    def test_resolve_softens_sleeplessness(self):
        import contextlib, io
        g = Game(content.load())
        g.player.awareness, g.player.period, g.player.skills = 25, 3, {"resolve": 3}
        with contextlib.redirect_stdout(io.StringIO()), mock.patch("ui.pause", lambda: None):
            g.rest()
        self.assertEqual(g.player.fatigue, 0)


class WorldTests(unittest.TestCase):
    def setUp(self):
        self.grid = world.build_map()
        self.c = content.load()

    def test_every_location_has_a_reachable_zone(self):
        seen, q = {world.START_TILE}, deque([world.START_TILE])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and world.walkable(self.grid, *n):
                    seen.add(n)
                    q.append(n)
        for loc in self.c.locations:
            self.assertIn(loc, world.ZONES, f"{loc} has no zone")
            self.assertIn(loc, world.ANCHORS)
            self.assertTrue(any(world.zone_at(*t) == loc for t in seen), f"{loc} unreachable on foot")
            self.assertEqual(world.zone_at(*world.ANCHORS[loc]), loc)
            self.assertTrue(world.walkable(self.grid, *world.ANCHORS[loc]))
        self.assertEqual(world.zone_at(*world.START_TILE), "ferry_dock")

    def test_church_road_is_only_reachable_through_the_square(self):
        # the walkable route from the dock to the road must cross the square zone
        seen, q = {world.START_TILE}, deque([world.START_TILE])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n in seen or not world.walkable(self.grid, *n):
                    continue
                if world.zone_at(*n) == "landing_square":
                    continue                       # forbid the square
                seen.add(n)
                q.append(n)
        self.assertFalse(any(world.zone_at(*t) == "church_road" for t in seen))


class GuiSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = App(headless=True)

    def make(self, origin="investigator"):
        c = self.app.content
        p = character.build_player("Matt", c.origins[origin], {"perception": 3}, "ferry_dock", c.start_topics)
        g = Game(c, player=p)
        return g, overworld.Overworld(self.app, g)

    def test_all_screens_render_in_every_time_of_day(self):
        g, ov = self.make()
        g.player.clues += ["rusted_iron_cross", "faded_handbill"]
        for period in range(4):
            g.player.period = period
            for aw in (0, 12, 30, 60):
                g.player.awareness = aw
                ov.draw_scene()
        jv = JournalView(self.app, g)
        for i in range(5):
            jv.tab = i
            jv.draw()
        self.app.draw_background()

    def test_walking_into_a_new_zone_travels_and_opens_the_location(self):
        g, ov = self.make()
        panel = TextPanel(self.app)
        visits = []
        with mock.patch.object(Game, "visit", lambda self: visits.append(self.player.location)):
            ov.x, ov.y = 13, 17                      # pier, one tile south of the square
            ov.try_step(0, -1)
            for _ in range(30):
                ov.update(0.05)
        self.assertEqual(visits, ["landing_square"])
        self.assertEqual(g.player.period, 1)         # one stop = one period
        self.assertIn("landing_square", g.player.visited)

    def test_fast_travel_costs_one_period_per_stop(self):
        g, ov = self.make()
        g.player.visited += ["landing_square", "church_road"]
        with mock.patch.object(Game, "visit", lambda self: None):
            overworld._fast_travel(ov, (g.locations["church_road"], None, True))
        self.assertEqual(g.player.location, "church_road")
        self.assertEqual(g.player.period, 2)
        self.assertEqual((ov.x, ov.y), world.ANCHORS["church_road"])

    def test_church_road_fog_blocks_with_the_authored_text(self):
        g, ov = self.make()
        g.player.location = "church_road"
        ov.x, ov.y = 8, 2
        said = []
        with mock.patch("ui.say_lines", lambda lines: said.extend(lines)), mock.patch("ui.pause", lambda: None):
            ov.try_step(0, -1)
            ov.try_step(0, -1)
        self.assertTrue(any("not ready to start again" in s for s in said))
        self.assertEqual((ov.x, ov.y), (8, 2))

    def test_text_panel_routes_engine_output_and_restores_console(self):
        panel = TextPanel(self.app)
        orig = ui.say
        panel.install()
        try:
            ui.say_lines(["A line."])
            ui.block("NEW TOPIC DISCOVERED", "X")
            self.assertTrue(ui.HUD)
            kinds = [e[0] for e in panel.entries]
            self.assertIn("banner", kinds)
            self.assertIn("text", kinds)
        finally:
            panel.uninstall()
        self.assertIs(ui.say, orig)
        self.assertFalse(ui.HUD)

    def test_text_panel_menu_by_keyboard(self):
        g, ov = self.make()
        panel = TextPanel(self.app)
        panel.install()
        self.app.bg_fn = lambda: ov.draw_scene()
        try:
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2, mod=0, unicode="2"))
            self.assertEqual(ui.menu(["one", "two", "three"]), 1)
        finally:
            panel.uninstall()
            self.app.bg_fn = None

    def test_visit_loop_runs_conversation_through_the_panel(self):
        g, ov = self.make()
        panel = TextPanel(self.app)
        panel.install()
        self.app.bg_fn = lambda: ov.draw_scene()
        picks = iter(["Talk to the ferryman", "Ask about Ferry Landing", "Leave", "Leave"])

        def fake_menu(labels, prompt="> "):
            want = next(picks)
            return next(i for i, l in enumerate(labels) if want in l)
        try:
            with mock.patch("ui.menu", fake_menu), mock.patch("ui.pause", lambda: None):
                g.visit()
        finally:
            panel.uninstall()
            self.app.bg_fn = None
        self.assertTrue(any(c["npc"] == "ferryman" for c in g.player.claims))

    def test_save_includes_character_and_position(self):
        g, ov = self.make("swamp_native")
        g.player.pos = [14, 20]
        g.save("gui")
        p = Game.load_player("gui")
        self.assertEqual((p.name, p.origin, p.pos), ("Matt", "swamp_native", [14, 20]))
        self.assertEqual(p.skills, g.player.skills)


if __name__ == "__main__":
    unittest.main()
