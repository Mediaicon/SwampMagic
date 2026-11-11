"""Routes the engine's console calls (ui.say / ui.menu / ...) into an on-screen text panel.

The engine never knows it is running in a window. dialog.py, game.py and journal.py
keep calling ui.*; installing this backend swaps those functions for versions that
draw a panel over whatever screen is underneath, and block until the player chooses.
"""
from __future__ import annotations

import pygame

import ui
from gfx import theme as T

PANEL_RECT = pygame.Rect(18, 18, T.VIEW_W - 36, T.SCREEN_H - 36)


class TextPanel:
    def __init__(self, app):
        self.app = app
        self.entries = []        # ("text", str) | ("banner", title, body) | ("gap",)
        self.scroll = 0
        self._orig = {}

    # --------------------------------------------------------- ui replacements
    def install(self):
        for name in ("clear", "say", "say_lines", "rule", "block", "ask", "pause", "menu"):
            self._orig[name] = getattr(ui, name)
        ui.clear = self.clear
        ui.say = self.say
        ui.say_lines = self.say_lines
        ui.rule = lambda *a, **k: None
        ui.block = self.block
        ui.ask = self.ask
        ui.pause = self.pause
        ui.menu = self.menu
        ui.HUD = True

    def uninstall(self):
        for name, fn in self._orig.items():
            setattr(ui, name, fn)
        ui.HUD = False

    def clear(self):
        self.entries = []
        self.scroll = 0

    def say(self, text=""):
        if text:
            self.entries.append(("text", text))
        else:
            self.entries.append(("gap",))

    def say_lines(self, lines):
        self.entries.append(("gap",))
        for line in lines:
            self.entries.append(("text", line))
            self.entries.append(("gap",))

    def block(self, title, body=""):
        self.entries.append(("banner", title, body))

    # ------------------------------------------------------------- drawing ----
    def _layout(self, width):
        rows, y = [], 0
        for e in self.entries:
            if e[0] == "text":
                h = T.paragraph_height(e[1], 19, width)
                rows.append((y, e, h))
                y += h + 4
            elif e[0] == "banner":
                h = 54 if e[2] else 36
                rows.append((y, e, h))
                y += h + 8
            else:
                y += 8
        return rows, y

    def draw(self, surf, choices=None, hover=-1, prompt=None):
        r = PANEL_RECT
        T.panel(surf, r, alpha=240)
        pad = 22
        text_w = r.w - pad * 2
        choices = choices or []
        row_h = 34
        choice_h = len(choices) * row_h + (12 if choices else 0)
        if prompt and not choices:
            choice_h = 40
        area = pygame.Rect(r.x + pad, r.y + pad, text_w, r.h - pad * 2 - choice_h)
        rows, total = self._layout(text_w)
        self.scroll = max(0, min(self.scroll, max(0, total - area.h)))
        clip = surf.get_clip()
        surf.set_clip(area)
        offset = 0 if total <= area.h else max(0, total - area.h) - self.scroll
        for y, e, h in rows:
            yy = area.y + y - offset
            if e[0] == "text":
                col = T.TEXT
                T.paragraph(surf, e[1], area.x, yy, text_w, 19, col)
            else:
                b = pygame.Rect(area.x, yy, text_w, h)
                pygame.draw.rect(surf, (54, 44, 20), b, border_radius=6)
                pygame.draw.rect(surf, T.GOLD, b, 2, border_radius=6)
                T.text(surf, e[1], (b.x + 14, b.y + 6), 17, T.GOLD, bold=True)
                if e[2]:
                    T.text(surf, e[2], (b.x + 14, b.y + 27), 18, T.TEXT)
        surf.set_clip(clip)
        if total > area.h:
            T.text(surf, "mouse wheel / PgUp / PgDn to scroll", (area.right - 250, area.y - 16), 12, T.TEXT_DIM)
        rects = []
        y0 = r.bottom - pad - len(choices) * row_h
        for i, label in enumerate(choices):
            br = pygame.Rect(r.x + pad, y0 + i * row_h, text_w, row_h - 4)
            rects.append(br)
            on = i == hover
            pygame.draw.rect(surf, (54, 74, 54) if on else (30, 40, 30), br, border_radius=6)
            pygame.draw.rect(surf, T.GOLD if on else T.PANEL_EDGE, br, 2, border_radius=6)
            T.text(surf, f"{i + 1}", (br.x + 12, br.y + 6), 17, T.GOLD, bold=True)
            T.text(surf, label, (br.x + 40, br.y + 6), 18, T.TEXT)
        if prompt and not choices:
            T.text(surf, prompt, (r.centerx, r.bottom - pad - 24), 16, T.TEXT_DIM, center=True)
        return rects

    # --------------------------------------------------------------- input ----
    def _frame(self, choices=None, prompt=None):
        mx, my = pygame.mouse.get_pos()
        self.app.draw_background()
        dim = pygame.Surface((T.VIEW_W, T.SCREEN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 120))
        self.app.screen.blit(dim, (0, 0))
        hover = -1
        rects = self.draw(self.app.screen, choices, prompt=prompt)
        for i, br in enumerate(rects):
            if br.collidepoint(mx, my):
                hover = i
        if hover >= 0:
            rects = self.draw(self.app.screen, choices, hover=hover, prompt=prompt)
        pygame.display.flip()
        self.app.clock.tick(60)
        return rects

    def menu(self, labels, prompt="> "):
        while True:
            rects = self._frame(labels)
            for ev in self.app.events():
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    for i, br in enumerate(rects):
                        if br.collidepoint(ev.pos):
                            return i
                elif ev.type == pygame.MOUSEWHEEL:
                    self.scroll += ev.y * 40
                elif ev.type == pygame.KEYDOWN:
                    if pygame.K_1 <= ev.key <= pygame.K_9:
                        i = ev.key - pygame.K_1
                        if i < len(labels):
                            return i
                    elif ev.key == pygame.K_PAGEUP:
                        self.scroll += 200
                    elif ev.key == pygame.K_PAGEDOWN:
                        self.scroll -= 200

    def pause(self):
        while True:
            self._frame(prompt="Press any key to continue")
            for ev in self.app.events():
                if ev.type == pygame.KEYDOWN and ev.key not in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                    return
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    return
                if ev.type == pygame.MOUSEWHEEL:
                    self.scroll += ev.y * 40
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_PAGEUP:
                    self.scroll += 200
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_PAGEDOWN:
                    self.scroll -= 200

    def ask(self, prompt="> "):
        raise ui.QuitGame()      # free-text input is not used by the graphical front-end
