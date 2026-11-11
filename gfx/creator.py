"""Character creator: name -> origin -> skills -> confirm.

Origins are backgrounds, not classes (Design Doc ch. 9). Skills are a small prototype
layer on top. Neither decides what the player may believe or where the story goes.
"""
from __future__ import annotations

import pygame

import character
import ui
from gfx import sprites, theme as T
from origin import CREATION_MAX_RANK, CREATION_POINTS, SKILLS

STEPS = ("Name", "Origin", "Skills", "Arrive")


class Creator:
    def __init__(self, app, content):
        self.app, self.c = app, content
        self.origins = list(content.origins.values())
        self.step = 0
        self.name = ""
        self.sel = 0
        self.alloc = {}
        self.hot = []            # [(rect, callback)] rebuilt every frame

    @property
    def origin(self):
        return self.origins[self.sel]

    # ---------------------------------------------------------------- chrome --
    def _frame(self):
        s = self.app.screen
        s.fill((14, 18, 14))
        for i in range(0, T.SCREEN_H, 4):                            # faint fog banding
            a = 8 + int(6 * ((i * 0.013 + self.app.t * 0.2) % 1))
            pygame.draw.line(s, (20 + a, 26 + a, 22 + a), (0, i), (T.SCREEN_W, i))
        T.text(s, "WHO ARE YOU?", (40, 26), 30, T.GOLD, bold=True)
        x = 40
        for i, name in enumerate(STEPS):
            col = T.GOLD if i == self.step else (T.TEXT if i < self.step else T.TEXT_DIM)
            r = T.text(s, f"{i + 1}. {name}", (x, 70), 17, col, bold=(i == self.step))
            x = r.right + 28
        pygame.draw.line(s, T.PANEL_EDGE, (40, 98), (T.SCREEN_W - 40, 98))
        self.hot = []

    def _btn(self, rect, label, cb, enabled=True):
        mx, my = pygame.mouse.get_pos()
        T.button(self.app.screen, rect, label, pygame.Rect(rect).collidepoint(mx, my), enabled=enabled)
        if enabled:
            self.hot.append((pygame.Rect(rect), cb))

    def _nav(self, can_next=True, next_label="Next"):
        if self.step > 0:
            self._btn((40, T.SCREEN_H - 62, 130, 40), "Back", self.back)
        self._btn((T.SCREEN_W - 230, T.SCREEN_H - 62, 190, 40), next_label, self.forward, can_next)

    def back(self):
        self.step = max(0, self.step - 1)

    def forward(self):
        if self.step == 0 and not self.name.strip():
            self.name = "Stranger"
        if self.step == len(STEPS) - 1:
            self.done = True
        else:
            self.step += 1

    # ----------------------------------------------------------------- steps --
    def _name(self):
        s = self.app.screen
        T.text(s, "What do people call you?", (T.SCREEN_W // 2, 190), 28, T.TEXT, center=True)
        box = pygame.Rect(T.SCREEN_W // 2 - 240, 250, 480, 56)
        T.panel(s, box, fill=(28, 34, 28), edge=T.GOLD, alpha=255)
        blink = "|" if int(self.app.t * 2) % 2 == 0 else ""
        shown = self.name + blink if self.name or blink else "Stranger"
        T.text(s, shown if self.name or blink else "Stranger", (box.centerx, box.y + 12), 28, T.TEXT if self.name else T.TEXT_DIM, center=True)
        T.text(s, "Type a name. Leave it empty to arrive as a Stranger.", (T.SCREEN_W // 2, 330), 16, T.TEXT_DIM, center=True)
        self._nav()

    def _origin(self):
        s = self.app.screen
        mx, my = pygame.mouse.get_pos()
        for i, o in enumerate(self.origins):
            r = pygame.Rect(40, 114 + i * 56, 250, 50)
            on = i == self.sel
            hover = r.collidepoint(mx, my)
            T.panel(s, r, fill=(52, 70, 52) if on else ((38, 50, 38) if hover else (26, 32, 26)),
                    edge=T.GOLD if on else T.PANEL_EDGE, alpha=255)
            T.text(s, o.name, (r.x + 14, r.y + 13), 19, T.GOLD if on else T.TEXT, bold=on)
            self.hot.append((r, lambda i=i: setattr(self, "sel", i)))
        o = self.origin
        box = pygame.Rect(316, 114, T.SCREEN_W - 356, T.SCREEN_H - 200)
        T.panel(s, box, alpha=255)
        s.blit(sprites.portrait(120, sprites.palette(o.id)), (box.x + 20, box.y + 20))
        T.text(s, o.name, (box.x + 160, box.y + 22), 30, T.GOLD, bold=True)
        T.paragraph(s, o.tagline, box.x + 160, box.y + 64, box.w - 180, 19, T.TEXT, serif=True)
        y = T.paragraph(s, o.perspective, box.x + 160, box.y + 96, box.w - 180, 17, T.TEXT_DIM)
        y = max(y, box.y + 150) + 12
        T.text(s, "STARTING SKILLS", (box.x + 20, y), 15, T.GOLD, bold=True)
        sx, sy = box.x + 20, y + 26
        for k, sk in enumerate(SKILLS):
            col, row = k % 2, k // 2
            T.text(s, sk.name, (sx + col * 250, sy + row * 30), 17, T.TEXT)
            T.pips(s, sx + col * 250 + 110, sy + row * 30 + 4, o.skills.get(sk.id, 0), CREATION_MAX_RANK)
        y = sy + 76
        T.text(s, "CONTACT (placeholder)", (box.x + 20, y), 15, T.GOLD, bold=True)
        y = T.paragraph(s, o.contact, box.x + 20, y + 24, box.w - 40, 16, T.TEXT_DIM) + 8
        T.text(s, "YOUR OWN QUESTION", (box.x + 20, y), 15, T.GOLD, bold=True)
        T.text(s, o.mystery_title, (box.x + 20, y + 24), 19, T.TEXT, bold=True)
        T.paragraph(s, o.mystery_text, box.x + 20, y + 50, box.w - 40, 16, T.TEXT_DIM)
        self._nav()

    def _skills(self):
        s = self.app.screen
        o = self.origin
        left = character.points_left(self.alloc)
        T.text(s, "Spend your points.", (40, 118), 26, T.TEXT)
        T.text(s, f"{left} point{'s' if left != 1 else ''} left", (40, 154), 19, T.GOLD if left else T.GREEN)
        T.text(s, "Origins shape where you start, not where you end up. Skills change what you can "
                  "notice and how people respond. None of them is Awareness.",
               (40, 184), 15, T.TEXT_DIM)
        final = character.final_skills(o, self.alloc)
        for k, sk in enumerate(SKILLS):
            y = 240 + k * 76
            r = pygame.Rect(40, y, T.SCREEN_W - 80, 66)
            T.panel(s, r, fill=(26, 32, 26), alpha=255)
            T.text(s, sk.name, (r.x + 18, r.y + 8), 22, T.TEXT, bold=True)
            T.text(s, sk.blurb, (r.x + 18, r.y + 38), 15, T.TEXT_DIM)
            T.pips(s, r.x + 400, r.y + 22, o.skills.get(sk.id, 0), CREATION_MAX_RANK,
                   extra=self.alloc.get(sk.id, 0), size=20, gap=6)
            self._btn((r.right - 120, r.y + 14, 40, 38), "-", lambda sid=sk.id: self.adjust(sid, -1),
                      character.can_remove(self.alloc, sk.id))
            self._btn((r.right - 66, r.y + 14, 40, 38), "+", lambda sid=sk.id: self.adjust(sid, +1),
                      character.can_add(o, self.alloc, sk.id))
            T.text(s, str(final[sk.id]), (r.x + 360, r.y + 18), 24, T.GOLD, bold=True)
        self._nav(can_next=character.valid(o, self.alloc))

    def adjust(self, skill, d):
        o = self.origin
        if d > 0 and character.can_add(o, self.alloc, skill):
            self.alloc[skill] = self.alloc.get(skill, 0) + 1
        elif d < 0 and character.can_remove(self.alloc, skill):
            self.alloc[skill] -= 1

    def _arrive(self):
        s = self.app.screen
        o = self.origin
        final = character.final_skills(o, self.alloc)
        s.blit(sprites.portrait(200, sprites.palette(o.id)), (60, 130))
        T.text(s, self.name.strip() or "Stranger", (300, 130), 36, T.GOLD, bold=True)
        T.text(s, o.name, (302, 176), 21, T.TEXT, italic=True)
        for k, sk in enumerate(SKILLS):
            T.text(s, sk.name, (302, 226 + k * 30), 18, T.TEXT)
            T.pips(s, 440, 230 + k * 30, final[sk.id], CREATION_MAX_RANK)
        T.text(s, o.mystery_title, (60, 372), 22, T.TEXT, bold=True)
        T.paragraph(s, o.mystery_text, 60, 404, T.SCREEN_W - 120, 19, T.TEXT_DIM)
        T.text(s, "The ferry has gone. The fog is low over the water.", (60, 480), 20, T.TEXT, italic=True)
        self._nav(True, "Step onto the dock")

    # ------------------------------------------------------------------ loop --
    def run(self):
        """Return a Player, or None if the player backs out to the title."""
        self.done = False
        while not self.done:
            self.app.t = pygame.time.get_ticks() / 1000
            self._frame()
            (self._name, self._origin, self._skills, self._arrive)[self.step]()
            pygame.display.flip()
            self.app.clock.tick(60)
            for ev in self.app.events():
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    for r, cb in self.hot:
                        if r.collidepoint(ev.pos):
                            cb()
                            break
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        if self.step == 0:
                            return None
                        self.back()
                    elif self.step == 0:
                        if ev.key == pygame.K_BACKSPACE:
                            self.name = self.name[:-1]
                        elif ev.key == pygame.K_RETURN:
                            self.forward()
                        elif ev.unicode and ev.unicode.isprintable() and len(self.name) < 20:
                            self.name += ev.unicode
                    elif self.step == 1:
                        if ev.key == pygame.K_DOWN:
                            self.sel = (self.sel + 1) % len(self.origins)
                        elif ev.key == pygame.K_UP:
                            self.sel = (self.sel - 1) % len(self.origins)
                        elif ev.key == pygame.K_RETURN:
                            self.alloc = {}
                            self.forward()
                    elif ev.key == pygame.K_RETURN and (self.step != 2 or character.valid(self.origin, self.alloc)):
                        self.forward()
        return character.build_player(self.name, self.origin, self.alloc,
                                      self.c.start_location, self.c.start_topics)
