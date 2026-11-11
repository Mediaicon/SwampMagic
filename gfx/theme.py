"""Colours, fonts and small drawing helpers shared by every screen."""
from __future__ import annotations

import functools
import math

import pygame

SCREEN_W, SCREEN_H = 1024, 640
SIDEBAR_W = 256
VIEW_W = SCREEN_W - SIDEBAR_W          # 768 -> 24 tiles
VIEW_H = SCREEN_H                      # 640 -> 20 tiles
TILE = 32

INK = (38, 28, 20)
INK_SOFT = (84, 66, 48)
PAPER = (226, 210, 174)
PAPER_DARK = (204, 186, 148)
PAPER_EDGE = (150, 124, 88)
PANEL = (22, 26, 22)
PANEL_EDGE = (92, 108, 80)
TEXT = (222, 224, 206)
TEXT_DIM = (150, 156, 138)
GOLD = (222, 188, 96)
GREEN = (96, 196, 110)
RED = (176, 52, 44)
FOG = (178, 190, 178)

_SERIF = ["georgia", "palatinolinotype", "garamond", "timesnewroman", "dejavuserif", "serif"]
_SANS = ["segoeui", "calibri", "dejavusans", "arial", "sans"]


@functools.lru_cache(maxsize=None)
def font(size: int, bold: bool = False, serif: bool = True, italic: bool = False):
    f = pygame.font.SysFont(_SERIF if serif else _SANS, size, bold=bold, italic=italic)
    return f


@functools.lru_cache(maxsize=4096)
def _wrap(text: str, size: int, bold: bool, serif: bool, width: int):
    f = font(size, bold, serif)
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            trial = (line + " " + w).strip()
            if f.size(trial)[0] <= width or not line:
                line = trial
            else:
                out.append(line)
                line = w
        out.append(line)
    return tuple(out)


def wrap(text, size, width, bold=False, serif=True):
    return _wrap(text, size, bold, serif, width)


def text(surf, s, pos, size=18, color=TEXT, bold=False, serif=True, italic=False, center=False):
    img = font(size, bold, serif, italic).render(s, True, color)
    r = img.get_rect()
    if center:
        r.midtop = pos
    else:
        r.topleft = pos
    surf.blit(img, r)
    return r


def paragraph(surf, s, x, y, width, size=18, color=TEXT, bold=False, serif=True, gap=3):
    """Draw wrapped text; return the y below it."""
    f = font(size, bold, serif)
    for line in wrap(s, size, width, bold, serif):
        surf.blit(f.render(line, True, color), (x, y))
        y += f.get_linesize() + gap - 2
    return y


def paragraph_height(s, size, width, bold=False, serif=True, gap=3):
    return len(wrap(s, size, width, bold, serif)) * (font(size, bold, serif).get_linesize() + gap - 2)


def panel(surf, rect, fill=PANEL, edge=PANEL_EDGE, alpha=235, radius=8, width=2):
    r = pygame.Rect(rect)
    layer = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(layer, (*fill, alpha), layer.get_rect(), border_radius=radius)
    pygame.draw.rect(layer, (*edge, 255), layer.get_rect(), width, border_radius=radius)
    surf.blit(layer, r.topleft)


def button(surf, rect, label, hover=False, size=18, enabled=True):
    r = pygame.Rect(rect)
    fill = (52, 70, 52) if hover and enabled else (34, 44, 34)
    edge = GOLD if hover and enabled else PANEL_EDGE
    pygame.draw.rect(surf, fill, r, border_radius=6)
    pygame.draw.rect(surf, edge, r, 2, border_radius=6)
    col = TEXT if enabled else TEXT_DIM
    text(surf, label, (r.centerx, r.y + (r.h - font(size).get_linesize()) // 2), size, col, center=True)


def pips(surf, x, y, filled, total, extra=0, size=12, gap=4, col=GREEN, extra_col=GOLD, empty=(60, 66, 58)):
    """A row of skill pips: `filled` solid, `extra` highlighted, rest hollow."""
    for i in range(total):
        r = pygame.Rect(x + i * (size + gap), y, size, size)
        if i < filled:
            pygame.draw.rect(surf, col, r, border_radius=3)
        elif i < filled + extra:
            pygame.draw.rect(surf, extra_col, r, border_radius=3)
        else:
            pygame.draw.rect(surf, empty, r, 2, border_radius=3)


def eye(surf, center, width, open_pips, total=5, t=0.0, bg=None):
    """The Green Eye. Opens a little per pip. Never labelled, never explained."""
    cx, cy = center
    w = width
    h = int(w * (0.04 + 0.44 * open_pips / total))
    n = 28
    top = [(cx - w // 2 + w * i / n, cy - h * math.sin(math.pi * i / n)) for i in range(n + 1)]
    bot = [(cx + w // 2 - w * i / n, cy + h * 0.8 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    poly = top + bot
    box = pygame.Rect(cx - w // 2 - 4, cy - w // 2, w + 8, w)
    mask = pygame.Surface(box.size, pygame.SRCALPHA)
    local = [(x - box.x, y - box.y) for x, y in poly]
    pygame.draw.polygon(mask, (235, 228, 200, 255), local)
    if open_pips > 0:
        iris = pygame.Surface(box.size, pygame.SRCALPHA)
        wob = math.sin(t * 0.9) * w * 0.03
        ic = (box.w // 2 + wob, box.h // 2)
        pygame.draw.circle(iris, (70, 190, 96, 255), ic, int(w * 0.17))
        pygame.draw.circle(iris, (30, 110, 58, 255), ic, int(w * 0.17), 3)
        pygame.draw.circle(iris, (10, 24, 14, 255), ic, int(w * 0.07))
        iris.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        mask.blit(iris, (0, 0))
    surf.blit(mask, box.topleft)
    pygame.draw.lines(surf, (20, 30, 20), True, poly, 2)
