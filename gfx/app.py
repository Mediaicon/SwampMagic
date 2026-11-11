"""Window, main loop and screen flow."""
from __future__ import annotations

import math
import os
import sys

import pygame

import content as content_module
import ui
from game import Game
from gfx import creator, overworld, sheet, theme as T
from gfx.backend import TextPanel
from gfx.journal_view import JournalView


class App:
    def __init__(self, headless=False):
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        pygame.init()
        pygame.display.set_caption("Swamp Magic")
        self.screen = pygame.display.set_mode((T.SCREEN_W, T.SCREEN_H))
        self.clock = pygame.time.Clock()
        self.t = 0.0
        self.bg_fn = None
        self.content = content_module.load()

    # ----------------------------------------------------------------- plumbing
    def events(self):
        out = []
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                raise ui.QuitGame()
            out.append(ev)
        return out

    def draw_background(self):
        self.t = pygame.time.get_ticks() / 1000
        if self.bg_fn:
            self.bg_fn()
        else:
            self.screen.fill((14, 18, 14))

    # -------------------------------------------------------------------- title
    def title(self):
        saved = Game.load_player()
        labels = ["New game"] + (["Continue"] if saved else []) + ["Quit"]
        rects = []
        while True:
            self.t = pygame.time.get_ticks() / 1000
            s = self.screen
            s.fill((12, 16, 14))
            for i in range(9):                                       # drifting fog bands
                y = 60 + i * 66 + math.sin(self.t * 0.3 + i) * 14
                band = pygame.Surface((T.SCREEN_W, 46), pygame.SRCALPHA)
                band.fill((*T.FOG, 14 + (i % 3) * 5))
                s.blit(band, (int(math.sin(self.t * 0.15 + i * 2) * 40) - 20, int(y)))
            for i in range(14):                                      # cypress silhouettes
                x = i * 80 + 20
                h = 160 + (i * 37) % 90
                pygame.draw.rect(s, (18, 24, 20), (x, T.SCREEN_H - h, 10, h))
                pygame.draw.circle(s, (20, 30, 24), (x + 5, T.SCREEN_H - h), 34 + (i * 11) % 18)
            pips = int((self.t * 0.4) % 6)
            T.eye(s, (T.SCREEN_W // 2, 130), 170, min(pips, 5), 5, self.t)
            T.text(s, "SWAMP MAGIC", (T.SCREEN_W // 2, 190), 62, T.GOLD, bold=True, center=True)
            T.text(s, "Last stop before the grave.", (T.SCREEN_W // 2, 270), 20, T.TEXT_DIM, italic=True, center=True)
            rects, mx_my = [], pygame.mouse.get_pos()
            for i, label in enumerate(labels):
                r = pygame.Rect(T.SCREEN_W // 2 - 140, 340 + i * 62, 280, 50)
                rects.append(r)
                T.button(s, r, label, r.collidepoint(mx_my), size=22)
            pygame.display.flip()
            self.clock.tick(60)
            for ev in self.events():
                choice = None
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    for r, lab in zip(rects, labels):
                        if r.collidepoint(ev.pos):
                            choice = lab
                elif ev.type == pygame.KEYDOWN:
                    if pygame.K_1 <= ev.key <= pygame.K_9 and ev.key - pygame.K_1 < len(labels):
                        choice = labels[ev.key - pygame.K_1]
                if choice == "Quit":
                    return
                if choice == "New game":
                    player = creator.Creator(self, self.content).run()
                    if player:
                        self.play(Game(self.content, player=player), fresh=True)
                    break
                if choice == "Continue":
                    self.play(Game(self.content, player=saved), fresh=False)
                    saved = Game.load_player()
                    labels = ["New game"] + (["Continue"] if saved else []) + ["Quit"]
                    break

    # --------------------------------------------------------------------- play
    def play(self, game: Game, fresh: bool):
        panel = TextPanel(self)
        panel.install()
        ov = overworld.Overworld(self, game)
        self.bg_fn = lambda: ov.draw_scene()
        game.show_journal = lambda: JournalView(self, game).run()
        try:
            if fresh:
                self._intro(game)
            self._loop(game, ov)
        except ui.QuitGame:
            pass
        finally:
            self.bg_fn = None
            panel.uninstall()

    def _intro(self, game):
        p = game.player
        ui.clear()
        ui.say_lines([
            "You step onto the dock at Ferry Landing. The fog hangs low over the water, "
            "and an old ferryman sits beside it, watching.",
            "You did not come here for the reason most people come here. You came with a question of your own:",
            p.personal.replace(": ", ".  ", 1) if p.personal else "You came for your own reasons.",
        ])
        ui.pause()
        ov_toast = "Arrow keys / WASD to walk.  E to interact."
        self._pending_toast = ov_toast

    def _loop(self, game, ov):
        toast = getattr(self, "_pending_toast", None)
        if toast:
            ov.say_toast(toast, 6)
            self._pending_toast = None
        keys_dir = {pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
                    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0)}
        last = pygame.time.get_ticks()
        while True:
            now = pygame.time.get_ticks()
            dt = min(0.05, (now - last) / 1000)
            last = now
            self.t = now / 1000
            for ev in self.events():
                if ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                        ov.interact()
                    elif ev.key == pygame.K_j:
                        game.show_journal()
                    elif ev.key == pygame.K_c:
                        sheet.sheet_screen(self, game)
                    elif ev.key == pygame.K_m:
                        overworld.map_screen(self, ov)
                    elif ev.key == pygame.K_ESCAPE:
                        game.system_menu()
            if ov.move is None:
                pressed = pygame.key.get_pressed()
                for key, d in keys_dir.items():
                    if pressed[key]:
                        ov.try_step(*d)
                        break
            ov.update(dt)
            ov.draw_scene()
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        try:
            self.title()
        except ui.QuitGame:
            pass
        finally:
            pygame.quit()


def main(argv=None):
    App().run()
    return 0
