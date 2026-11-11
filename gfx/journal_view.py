"""The journal as a physical object: parchment, tabs, pinned cards, red thread."""
from __future__ import annotations

import random

import pygame

import config
import investigation
import journal as console_journal
from gfx import sprites, theme as T

TABS = ("Topics", "Accounts", "Evidence", "Cases", "Notes")
PAGE = pygame.Rect(36, 70, T.SCREEN_W - 72, T.SCREEN_H - 102)
PAD = 30


def _paper():
    s = pygame.Surface(PAGE.size)
    s.fill(T.PAPER)
    rng = random.Random(9)
    for _ in range(2600):
        c = rng.choice([T.PAPER_DARK, (236, 222, 188), (214, 196, 160)])
        s.set_at((rng.randrange(PAGE.w), rng.randrange(PAGE.h)), c)
    for i in range(26):                                     # darkened edges
        a = (26 - i) * 3
        pygame.draw.rect(s, (max(0, 226 - a), max(0, 210 - a), max(0, 174 - a)), (i, i, PAGE.w - 2 * i, PAGE.h - 2 * i), 1)
    pygame.draw.line(s, T.PAPER_EDGE, (PAGE.w // 2, 8), (PAGE.w // 2, PAGE.h - 8), 1)
    return s


class JournalView:
    def __init__(self, app, game):
        self.app, self.game = app, game
        self.tab = 0
        self.scroll = 0
        self.paper = _paper()
        self.buttons = []
        self.content_h = 0

    # ----------------------------------------------------------------- tabs --
    def _tabs(self, s):
        self.tab_rects = []
        x = PAGE.x + 10
        for i, name in enumerate(TABS):
            w = T.font(18, True).size(name)[0] + 34
            r = pygame.Rect(x, PAGE.y - 36 + (6 if i != self.tab else 0), w, 40)
            col = T.PAPER if i == self.tab else (160, 134, 96)
            pygame.draw.rect(s, col, r, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(s, T.PAPER_EDGE, r, 2, border_top_left_radius=8, border_top_right_radius=8)
            T.text(s, name, (r.centerx, r.y + 9), 18, T.INK, bold=(i == self.tab), center=True)
            self.tab_rects.append(r)
            x += w + 6

    # ------------------------------------------------------------- contents --
    def _topics(self, s, x, y, w):
        for tid in self.game.player.topics:
            t = self.game.topics[tid]
            T.text(s, t.name, (x, y), 22, T.INK, bold=True)
            y = T.paragraph(s, t.blurb, x + 14, y + 28, w - 20, 17, T.INK_SOFT) + 12
        return y

    def _accounts(self, s, x, y, w):
        g, p = self.game, self.game.player
        rects = {}
        any_claims = False
        for q in g.questions.values():
            claims = [c for c in p.claims if c["question"] == q.id]
            if not claims:
                continue
            any_claims = True
            T.text(s, q.text, (x, y), 22, T.INK, bold=True)
            y += 34
            for c in claims:
                cw = min(560, w - 70)
                h = T.paragraph_height(c["text"], 17, cw - 30) + 22
                r = pygame.Rect(x + 8, y, cw, h)
                pygame.draw.rect(s, (240, 230, 196), r, border_radius=4)
                pygame.draw.rect(s, T.PAPER_EDGE, r, 1, border_radius=4)
                pygame.draw.circle(s, T.RED, (r.x + 12, r.y + 12), 5)
                T.paragraph(s, c["text"], r.x + 26, r.y + 10, cw - 40, 17, T.INK)
                rects[(c["npc"], c["question"], c["stance"])] = r
                y += h + 12
            y += 10
        for a, b in g.contradictions():
            ra = rects.get((a["npc"], a["question"], a["stance"]))
            rb = rects.get((b["npc"], b["question"], b["stance"]))
            if not ra or not rb:
                continue
            xr = max(ra.right, rb.right) + 26
            pa, pb = (ra.right, ra.centery), (rb.right, rb.centery)
            pygame.draw.lines(s, T.RED, False, [pa, (xr, pa[1]), (xr, pb[1]), pb], 3)
            mid = (xr + 14, (pa[1] + pb[1]) // 2)
            T.text(s, "≠", (xr + 8, mid[1] - 14), 28, T.RED, bold=True)
            who = (f"{g.npcs[a['npc']].name}, twice" if a["npc"] == b["npc"]
                   else f"{g.npcs[a['npc']].name} / {g.npcs[b['npc']].name}")
            T.text(s, who, (xr + 40, mid[1] - 8), 14, T.RED, italic=True)
        if not any_claims:
            T.text(s, "Nothing yet. People will tell you things. Not all of them will agree.", (x, y), 18, T.INK_SOFT, italic=True)
            y += 30
        return y

    def _evidence(self, s, x, y, w):
        g, p = self.game, self.game.player
        if not p.clues:
            T.text(s, "Nothing yet.", (x, y), 18, T.INK_SOFT, italic=True)
            return y + 30
        for cid in p.clues:
            clue = g.clues[cid]
            icon = sprites.clue_icon(cid, clue.kind)
            body_w = w - 90
            h = 30
            parts = [(clue.description, T.INK)]
            for when, text in clue.details:
                if when.check(g):
                    parts.append((text, (110, 40, 30)))
            if clue.bears_on:
                parts.append(("May bear on: " + "; ".join(g.questions[q].text for q in clue.bears_on), T.INK_SOFT))
            for text, _ in parts:
                h += T.paragraph_height(text, 16, body_w) + 4
            card = pygame.Rect(x, y, w, max(h, 70))
            pygame.draw.rect(s, (240, 230, 196), card, border_radius=4)
            pygame.draw.rect(s, T.PAPER_EDGE, card, 1, border_radius=4)
            s.blit(icon, (card.x + 10, card.y + 10))
            T.text(s, f"{clue.name}", (card.x + 80, card.y + 6), 20, T.INK, bold=True)
            T.text(s, clue.kind, (card.right - 12 - T.font(14).size(clue.kind)[0], card.y + 10), 14, T.INK_SOFT, italic=True)
            yy = card.y + 32
            for text, col in parts:
                yy = T.paragraph(s, text, card.x + 80, yy, body_w, 16, col, gap=3) + 4
            y = card.bottom + 14
        return y

    def _cases(self, s, x, y, w):
        g, p = self.game, self.game.player
        self.buttons = []
        for case in g.cases.values():
            done = case.id in p.assembled
            T.text(s, case.title, (x, y), 22, T.INK, bold=True)
            tag = "ASSEMBLED" if done else "OPEN"
            T.text(s, tag, (x + w - T.font(15, True).size(tag)[0] - 8, y + 6), 15, T.RED if done else T.INK_SOFT, bold=True)
            y += 36
            if not done and config.SHOW_CASE_CHECKLIST:
                st = investigation.status(g, case)
                for ok, label in ((st.sources >= st.need_sources, f"Accounts from different people ({min(st.sources, st.need_sources)}/{st.need_sources})"),
                                  (st.physical >= st.need_physical, f"Physical evidence ({min(st.physical, st.need_physical)}/{st.need_physical})")):
                    box = pygame.Rect(x + 12, y + 3, 16, 16)
                    pygame.draw.rect(s, T.INK_SOFT, box, 2)
                    if ok:
                        pygame.draw.line(s, T.INK, (box.x + 3, box.y + 8), (box.x + 7, box.y + 13), 3)
                        pygame.draw.line(s, T.INK, (box.x + 7, box.y + 13), (box.x + 14, box.y + 2), 3)
                    T.text(s, label, (x + 38, y), 17, T.INK)
                    y += 26
            if done:
                belief = p.beliefs.get(case.id)
                if belief:
                    y = T.paragraph(s, "Your belief: " + belief["text"], x + 12, y, w - 30, 18, (110, 40, 30), gap=3) + 8
                r = pygame.Rect(x + 12, y + 4, 300, 36)
                self.buttons.append((r, case))
                pygame.draw.rect(s, (214, 196, 150), r, border_radius=6)
                pygame.draw.rect(s, T.INK, r, 2, border_radius=6)
                T.text(s, "Settle on a belief…", (r.centerx, r.y + 7), 18, T.INK, center=True)
                y = r.bottom + 12
            y += 22
        return y

    def _notes(self, s, x, y, w):
        p = self.game.player
        if p.personal:
            T.text(s, "Your own question", (x, y), 22, T.INK, bold=True)
            title, _, body = p.personal.partition(": ")
            T.text(s, title, (x + 14, y + 30), 19, (110, 40, 30), bold=True)
            y = T.paragraph(s, body, x + 14, y + 56, w - 30, 17, T.INK) + 20
        T.text(s, "Notes", (x, y), 22, T.INK, bold=True)
        y += 32
        if not p.notes:
            T.text(s, "Nothing written yet.", (x + 14, y), 17, T.INK_SOFT, italic=True)
            y += 28
        for n in p.notes:
            y = T.paragraph(s, "• " + n, x + 14, y, w - 30, 17, T.INK) + 6
        return y

    # ------------------------------------------------------------------ loop --
    def draw(self):
        s = self.app.screen
        s.fill((30, 24, 18))
        self._tabs(s)
        s.blit(self.paper, PAGE.topleft)
        pygame.draw.rect(s, T.PAPER_EDGE, PAGE, 3)
        view = pygame.Rect(PAGE.x + PAD, PAGE.y + PAD - 6, PAGE.w - PAD * 2, PAGE.h - PAD * 2 + 6)
        clip = s.get_clip()
        s.set_clip(view)
        self.buttons = []
        fn = (self._topics, self._accounts, self._evidence, self._cases, self._notes)[self.tab]
        self.scroll = max(0, min(self.scroll, max(0, self.content_h - view.h)))
        end = fn(s, view.x, view.y - self.scroll, view.w - 40)
        self.content_h = end - (view.y - self.scroll)
        # buttons live in screen coordinates already (drawn with the offset)
        s.set_clip(clip)
        T.text(s, "Esc / J to close   -   wheel or arrows to scroll", (T.SCREEN_W // 2, T.SCREEN_H - 26), 14, (170, 150, 120), center=True)
        T.text(s, f"Day {self.game.player.day}", (T.SCREEN_W - 40 - 60, 34), 18, (210, 190, 150))

    def run(self):
        self.app.bg_fn = self.draw
        try:
            while True:
                self.app.t = pygame.time.get_ticks() / 1000
                self.draw()
                pygame.display.flip()
                self.app.clock.tick(60)
                for ev in self.app.events():
                    if ev.type == pygame.KEYDOWN:
                        if ev.key in (pygame.K_ESCAPE, pygame.K_j):
                            return
                        if ev.key == pygame.K_DOWN:
                            self.scroll += 60
                        if ev.key == pygame.K_UP:
                            self.scroll -= 60
                        if ev.key == pygame.K_RIGHT:
                            self.tab = (self.tab + 1) % len(TABS); self.scroll = 0
                        if ev.key == pygame.K_LEFT:
                            self.tab = (self.tab - 1) % len(TABS); self.scroll = 0
                    elif ev.type == pygame.MOUSEWHEEL:
                        self.scroll -= ev.y * 50
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        for i, r in enumerate(self.tab_rects):
                            if r.collidepoint(ev.pos):
                                self.tab, self.scroll = i, 0
                        for r, case in self.buttons:
                            if r.collidepoint(ev.pos):
                                console_journal.form_belief(self.game, case)
        finally:
            self.app.bg_fn = None
