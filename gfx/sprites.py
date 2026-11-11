"""Procedural people and props."""
from __future__ import annotations

import math

import pygame

SKIN = (214, 170, 130)

PALETTES = {
    "investigator": {"shirt": (92, 98, 110), "trim": (160, 150, 120), "hair": (60, 44, 34), "hat": None},
    "federal_agent": {"shirt": (34, 38, 52), "trim": (200, 200, 205), "hair": (30, 26, 24), "hat": None},
    "deputy": {"shirt": (120, 100, 62), "trim": (214, 186, 90), "hair": (70, 52, 36), "hat": (92, 74, 46)},
    "smuggler": {"shirt": (70, 56, 48), "trim": (150, 70, 52), "hair": (40, 30, 26), "hat": (40, 36, 34)},
    "swamp_native": {"shirt": (76, 104, 74), "trim": (180, 156, 100), "hair": (30, 24, 20), "hat": None},
    "gang_operator": {"shirt": (110, 36, 36), "trim": (30, 30, 30), "hair": (24, 22, 22), "hat": None},
    "occult_researcher": {"shirt": (82, 62, 100), "trim": (200, 184, 120), "hair": (150, 140, 130), "hat": None},
    "default": {"shirt": (96, 96, 96), "trim": (180, 180, 180), "hair": (60, 50, 40), "hat": None},
}


def palette(origin_id: str):
    return PALETTES.get(origin_id, PALETTES["default"])


def person(surf, x, y, pal, facing=(0, 1), step=0.0, shadow=True):
    """Draw a small figure with feet at (x, y)."""
    bob = int(math.sin(step * 2) * 1.5)
    if shadow:
        sh = pygame.Surface((22, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
        surf.blit(sh, (x - 11, y - 4))
    leg = int(math.sin(step * 2) * 3)
    pygame.draw.rect(surf, (40, 34, 30), (x - 6, y - 10, 4, 10 + (leg if leg > 0 else 0)))
    pygame.draw.rect(surf, (40, 34, 30), (x + 2, y - 10, 4, 10 + (-leg if leg < 0 else 0)))
    body = pygame.Rect(x - 8, y - 26 + bob, 16, 17)
    pygame.draw.rect(surf, pal["shirt"], body, border_radius=4)
    pygame.draw.rect(surf, pal["trim"], (x - 8, y - 14 + bob, 16, 3))
    head = (x, y - 32 + bob)
    pygame.draw.circle(surf, SKIN, head, 7)
    if facing[1] >= 0:
        pygame.draw.circle(surf, pal["hair"], (head[0], head[1] - 3), 7, draw_top_left=True, draw_top_right=True)
    else:
        pygame.draw.circle(surf, pal["hair"], head, 7)
    if facing[1] > 0:
        pygame.draw.circle(surf, (30, 24, 20), (x - 3, y - 32 + bob), 1)
        pygame.draw.circle(surf, (30, 24, 20), (x + 3, y - 32 + bob), 1)
    if pal.get("hat"):
        pygame.draw.ellipse(surf, pal["hat"], (x - 10, y - 41 + bob, 20, 7))
        pygame.draw.rect(surf, pal["hat"], (x - 6, y - 46 + bob, 12, 8), border_radius=3)


def ferryman(surf, x, y, t):
    """Sits at the dock edge, watching the water."""
    pal = {"shirt": (70, 78, 70), "trim": (120, 110, 84), "hair": (180, 180, 176), "hat": (60, 52, 40)}
    person(surf, x, y, pal, (0, -1), step=0, shadow=True)
    pygame.draw.line(surf, (90, 66, 44), (x + 12, y - 46), (x + 12, y + 2), 3)       # pole


def old_woman(surf, x, y, t):
    crate = pygame.Rect(x - 12, y - 12, 24, 14)
    pygame.draw.rect(surf, (106, 80, 52), crate)
    pygame.draw.rect(surf, (70, 52, 34), crate, 2)
    pal = {"shirt": (110, 84, 96), "trim": (180, 170, 150), "hair": (214, 212, 208), "hat": None}
    person(surf, x, y - 8, pal, (0, 1), step=0, shadow=False)
    pygame.draw.circle(surf, (150, 80, 100), (x, y - 44), 8, draw_top_left=True, draw_top_right=True)  # scarf


def iron_cross(surf, x, y):
    col, dark = (118, 78, 52), (78, 52, 36)
    pygame.draw.rect(surf, col, (x - 2, y - 14, 4, 16))
    pygame.draw.rect(surf, col, (x - 8, y - 10, 16, 4))
    pygame.draw.rect(surf, dark, (x - 2, y - 14, 4, 16), 1)
    pygame.draw.rect(surf, dark, (x - 8, y - 10, 16, 4), 1)


def door_mark(surf, rect, kind):
    """Decorations over the three shack doors in Landing Square. Flavour only."""
    x, y, w, h = rect
    cx = x + w // 2
    if kind == "horseshoe":
        pygame.draw.arc(surf, (170, 172, 176), (cx - 7, y + 3, 14, 14), math.pi, 2 * math.pi, 3)
        pygame.draw.line(surf, (170, 172, 176), (cx - 7, y + 10), (cx - 7, y + 4), 3)
        pygame.draw.line(surf, (170, 172, 176), (cx + 6, y + 10), (cx + 6, y + 4), 3)
    elif kind == "sticks":
        for i in range(5):
            xx = cx - 10 + i * 5
            pygame.draw.line(surf, (190, 170, 120), (xx, y + 3), (xx, y + 17), 2)
            for n in range(3):
                pygame.draw.line(surf, (60, 44, 30), (xx - 2, y + 6 + n * 4), (xx + 2, y + 6 + n * 4), 1)
    elif kind == "shut":
        pygame.draw.rect(surf, (150, 150, 140), (x + 4, y + 6, w - 8, 5))
        pygame.draw.rect(surf, (150, 150, 140), (x + 4, y + 16, w - 8, 5))


def portrait(size, pal, name_initial=""):
    """A bust for the character sheet and creator."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(s, (30, 36, 30), s.get_rect(), border_radius=10)
    pygame.draw.rect(s, (92, 108, 80), s.get_rect(), 3, border_radius=10)
    cx = size // 2
    pygame.draw.ellipse(s, pal["shirt"], (cx - size * 0.30, size * 0.62, size * 0.60, size * 0.50))
    pygame.draw.rect(s, pal["trim"], (cx - size * 0.10, size * 0.62, size * 0.20, size * 0.08))
    pygame.draw.rect(s, SKIN, (cx - size * 0.07, size * 0.52, size * 0.14, size * 0.14))
    pygame.draw.circle(s, SKIN, (cx, int(size * 0.40)), int(size * 0.20))
    pygame.draw.circle(s, pal["hair"], (cx, int(size * 0.37)), int(size * 0.20), draw_top_left=True, draw_top_right=True)
    for dx in (-0.07, 0.07):
        pygame.draw.circle(s, (30, 24, 20), (int(cx + size * dx), int(size * 0.42)), max(2, size // 40))
    if pal.get("hat"):
        pygame.draw.ellipse(s, pal["hat"], (cx - size * 0.28, size * 0.17, size * 0.56, size * 0.12))
        pygame.draw.rect(s, pal["hat"], (cx - size * 0.16, size * 0.07, size * 0.32, size * 0.14), border_radius=6)
    return s


# ----- journal evidence icons --------------------------------------------------
def clue_icon(clue_id: str, kind: str, size=56):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(s, (236, 228, 204), s.get_rect(), border_radius=4)
    pygame.draw.rect(s, (150, 124, 88), s.get_rect(), 2, border_radius=4)
    cx, cy = size // 2, size // 2
    if clue_id == "rusted_iron_cross":
        pygame.draw.rect(s, (120, 70, 44), (cx - 3, cy - 18, 6, 36))
        pygame.draw.rect(s, (120, 70, 44), (cx - 13, cy - 10, 26, 6))
    elif clue_id == "candle_ledger":
        pygame.draw.rect(s, (96, 64, 44), (cx - 16, cy - 14, 32, 28), border_radius=3)
        for i in range(4):
            pygame.draw.line(s, (214, 196, 150), (cx - 10, cy - 8 + i * 6), (cx + 10, cy - 8 + i * 6), 2)
    elif clue_id == "faded_handbill":
        pygame.draw.rect(s, (200, 188, 150), (cx - 14, cy - 18, 28, 36))
        pygame.draw.line(s, (120, 100, 80), (cx - 9, cy - 10), (cx + 6, cy - 10), 2)
        pygame.draw.line(s, (170, 150, 120), (cx - 9, cy), (cx + 9, cy), 1)
    else:
        pygame.draw.circle(s, (120, 100, 80), (cx, cy), 14, 3)
    return s
