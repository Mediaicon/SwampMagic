"""Character sheet."""
from __future__ import annotations

import pygame

import awareness
import config
from gfx import sprites, theme as T
from gfx.overworld import eye_pips
from origin import CREATION_MAX_RANK, SKILLS

STANDING = ((0, "Wary"), (1, "Guarded"), (3, "Open"), (6, "Trusting"))


def standing_word(t: int) -> str:
    w = STANDING[0][1]
    for threshold, word in STANDING:
        if t >= threshold:
            w = word
    return w


def sheet_screen(app, game):
    p = game.player
    origin = game.c.origins.get(p.origin)
    pal = sprites.palette(p.origin)
    port = sprites.portrait(190, pal)
    while True:
        app.t = pygame.time.get_ticks() / 1000
        s = app.screen
        s.fill((14, 18, 14))
        T.panel(s, (28, 24, T.SCREEN_W - 56, T.SCREEN_H - 48), alpha=255)
        s.blit(port, (56, 56))
        T.text(s, p.name or "Stranger", (270, 56), 34, T.GOLD, bold=True)
        if origin:
            T.text(s, origin.name, (272, 100), 20, T.TEXT, italic=True)
            T.paragraph(s, origin.tagline, 272, 130, 330, 17, T.TEXT_DIM)
            T.paragraph(s, origin.perspective, 272, 176, 330, 16, T.TEXT_DIM)
        # eye
        T.eye(s, (790, 120), 220, eye_pips(p.awareness), len(config.EYE_THRESHOLDS), app.t)
        if config.SHOW_AWARENESS_NUMBER:
            T.text(s, f"Awareness {p.awareness}", (790, 190), 17, T.TEXT_DIM, center=True)
        T.text(s, f"Condition: {awareness.fatigue_label(p.fatigue)}", (790, 216), 17, T.TEXT, center=True)
        # skills
        y = 276
        T.text(s, "SKILLS", (56, y), 18, T.GOLD, bold=True)
        y += 30
        for sk in SKILLS:
            rank = p.skills.get(sk.id, 0)
            T.text(s, sk.name, (56, y), 19, T.TEXT)
            T.pips(s, 190, y + 4, rank, CREATION_MAX_RANK + 2 if rank > CREATION_MAX_RANK else CREATION_MAX_RANK)
            T.paragraph(s, sk.blurb, 320, y - 2, 300, 14, T.TEXT_DIM, gap=1)
            y += 34
        # standing
        T.text(s, "STANDING", (56, y + 14), 18, T.GOLD, bold=True)
        y += 44
        met = [n for n in game.npcs.values()
               if p.trust.get(n.id, 0) > 0 or p.rapport_day.get(n.id) or any(c["npc"] == n.id for c in p.claims)]
        if not met:
            T.text(s, "You have not yet been trusted by anyone here.", (56, y), 16, T.TEXT_DIM, italic=True)
        for n in met:
            T.text(s, n.name, (56, y), 17, T.TEXT)
            T.text(s, standing_word(p.trust.get(n.id, 0)), (250, y), 17, T.GREEN)
            y += 26
        # own question
        box = pygame.Rect(640, 276, 320, 292)
        T.panel(s, box, fill=(34, 30, 20), edge=T.GOLD, alpha=255)
        T.text(s, "YOUR OWN QUESTION", (box.x + 16, box.y + 14), 16, T.GOLD, bold=True)
        if p.personal:
            title, _, body = p.personal.partition(": ")
            T.text(s, title, (box.x + 16, box.y + 44), 20, T.TEXT, bold=True)
            T.paragraph(s, body, box.x + 16, box.y + 76, box.w - 32, 17, T.TEXT_DIM)
        T.text(s, "C or Esc to close", (T.SCREEN_W // 2, T.SCREEN_H - 40), 15, T.TEXT_DIM, center=True)
        pygame.display.flip()
        app.clock.tick(60)
        for ev in app.events():
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_c, pygame.K_RETURN):
                return
            if ev.type == pygame.MOUSEBUTTONDOWN:
                return
