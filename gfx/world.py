"""The overworld: tile map, zones, tile art.

The map is generated in code so there are no asset files. Tiles are drawn
procedurally and cached. Layout mirrors the location graph in content/locations.py:
dock - square - (store | church road).
"""
from __future__ import annotations

import math
import random

import pygame

from gfx.theme import TILE

MAP_W, MAP_H = 40, 30
WALKABLE = set(".rp,=")

# location id -> inclusive rectangles (x0, y0, x1, y1)
ZONES = {
    "ferry_dock": [(11, 21, 16, 24)],
    "landing_square": [(7, 11, 26, 16)],
    "general_store": [(21, 10, 26, 10)],
    "church_road": [(6, 2, 9, 10)],
}
ANCHORS = {
    "ferry_dock": (13, 22),
    "landing_square": (16, 13),
    "general_store": (24, 10),
    "church_road": (8, 5),
}
START_TILE = (13, 22)
NPC_SPOTS = {"ferryman": (15, 22), "old_woman": (17, 14)}
CROSS_SPOT = (8, 6)
SHACK_DOORS = {(11, 10): "horseshoe", (15, 10): "sticks", (19, 10): "shut"}


def _rect(grid, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            grid[y][x] = ch


def build_map(seed: int = 11):
    rng = random.Random(seed)
    g = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]
    _rect(g, 0, 22, MAP_W - 1, MAP_H - 1, "~")            # river
    _rect(g, 30, 17, 36, 20, "~")                          # pond
    for y in range(22):
        for x in range(MAP_W):
            if g[y][x] != ".":
                continue
            edge = x < 2 or x > MAP_W - 3 or y < 1
            roll = rng.random()
            if edge or roll < 0.13:
                g[y][x] = "T"
            elif roll < 0.23:
                g[y][x] = "r"
    # cleared and built areas overwrite scatter
    _rect(g, 7, 11, 26, 16, "p")                           # square
    _rect(g, 7, 0, 8, 10, ",")                             # church road
    _rect(g, 21, 10, 26, 10, "p")                          # store doorstep
    _rect(g, 11, 21, 16, 24, "=")                          # dock
    _rect(g, 13, 17, 14, 20, "=")                          # pier
    _rect(g, 22, 7, 27, 8, "R")                            # store roof
    _rect(g, 22, 9, 27, 9, "W")
    g[9][24] = "D"
    for c in (11, 15, 19):                                 # three shacks
        _rect(g, c - 1, 9, c + 1, 9, "R")
        _rect(g, c - 1, 10, c + 1, 10, "W")
        g[10][c] = "D"
    _rect(g, 5, 0, 10, 1, "F")                             # fog wall
    # dense cypress walls on both flanks: the only way north is through the square
    for y in range(2, 22):
        g[y][5] = "T"
        g[y][28] = "T"
    for y in range(0, 2):
        g[y][28] = "T"
    for y in range(11, 17):
        g[y][6] = "T"          # west edge of the square
    for y in range(10, 17):
        g[y][27] = "T"         # east edge of the square
    # keep a clear apron around the doorstep and shacks
    for x in range(10, 21):
        if g[11][x] != "p":
            g[11][x] = "p"
    return g


def zone_at(x: int, y: int):
    for loc, rects in ZONES.items():
        for x0, y0, x1, y1 in rects:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return loc
    return None


def walkable(grid, x: int, y: int) -> bool:
    return 0 <= x < MAP_W and 0 <= y < MAP_H and grid[y][x] in WALKABLE


# ------------------------------------------------------------------ tile art --
def _noise_surface(size, base, specks, rng, n=40, spread=14):
    s = pygame.Surface((size, size))
    s.fill(base)
    for _ in range(n):
        c = rng.choice(specks)
        s.set_at((rng.randrange(size), rng.randrange(size)), c)
        pygame.draw.circle(s, c, (rng.randrange(size), rng.randrange(size)), rng.choice((1, 1, 2)))
    return s


class Tiles:
    def __init__(self):
        rng = random.Random(5)
        T = TILE
        self.mud = [_noise_surface(T, (66, 62, 40), [(58, 54, 34), (76, 72, 46), (50, 56, 36)], rng)
                    for _ in range(4)]
        self.packed = [_noise_surface(T, (98, 84, 58), [(88, 74, 50), (110, 96, 68), (80, 70, 48)], rng, 30)
                       for _ in range(4)]
        self.path = [_noise_surface(T, (112, 96, 66), [(100, 86, 58), (124, 108, 78)], rng, 26)
                     for _ in range(2)]
        self.reeds = []
        for i in range(3):
            s = self.mud[i].copy()
            for _ in range(7):
                x = rng.randrange(4, T - 4)
                y = rng.randrange(14, T - 2)
                col = rng.choice([(92, 128, 70), (110, 142, 78), (78, 108, 60)])
                pygame.draw.line(s, col, (x, y), (x + rng.randint(-3, 3), y - rng.randint(8, 16)), 2)
            self.reeds.append(s)
        self.planks = []
        for i in range(2):
            s = pygame.Surface((T, T))
            s.fill((112, 82, 52))
            for row in range(0, T, 8):
                shade = rng.choice([(104, 76, 48), (120, 90, 58), (98, 72, 46)])
                pygame.draw.rect(s, shade, (0, row, T, 7))
                pygame.draw.line(s, (60, 42, 28), (0, row + 7), (T, row + 7))
                nx = rng.randrange(4, T - 4)
                pygame.draw.line(s, (70, 50, 32), (nx, row), (nx, row + 7))
            self.planks.append(s)
        self.water = []
        for f in range(4):
            s = pygame.Surface((T, T))
            s.fill((26, 46, 48))
            for k in range(3):
                y = 6 + k * 10
                off = f * 8 + k * 5
                pts = [(x, y + 2 * math.sin((x + off) / 5.0)) for x in range(0, T + 1, 2)]
                pygame.draw.lines(s, (44, 74, 74), False, pts, 1)
            self.water.append(s)
        self.roof = pygame.Surface((T, T))
        self.roof.fill((60, 46, 40))
        for row in range(0, T, 8):
            for col in range(-(row // 8 % 2) * 8, T, 16):
                pygame.draw.rect(self.roof, (74, 56, 46), (col, row, 15, 7), border_radius=2)
        self.wall = pygame.Surface((T, T))
        self.wall.fill((96, 76, 54))
        for col in range(0, T, 6):
            pygame.draw.line(self.wall, (76, 58, 40), (col, 0), (col, T))
        self.door = self.wall.copy()
        pygame.draw.rect(self.door, (50, 36, 28), (6, 4, T - 12, T - 4), border_radius=3)
        pygame.draw.circle(self.door, GOLD_DK, (T - 11, T // 2 + 2), 2)
        self.fogwall = pygame.Surface((T, T), pygame.SRCALPHA)
        self.fogwall.fill((170, 182, 172, 255))
        self.tree_bases = self.mud
        self._trees = {}

    def ground(self, ch, x, y):
        v = (x * 7 + y * 13) % 4
        if ch in ".T":
            return self.mud[v]
        if ch == "r":
            return self.reeds[v % 3]
        if ch == "p":
            return self.packed[v]
        if ch == ",":
            return self.path[v % 2]
        if ch == "=":
            return self.planks[(x + y) % 2]
        if ch == "~":
            return None
        if ch == "R":
            return self.roof
        if ch == "W":
            return self.wall
        if ch == "D":
            return self.door
        if ch == "F":
            return self.mud[v]
        return self.mud[0]

    def tree(self, variant: int):
        if variant in self._trees:
            return self._trees[variant]
        rng = random.Random(variant)
        w, h = 52, 76
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        # roots / knees
        for i in range(5):
            kx = rng.randrange(8, w - 8)
            pygame.draw.polygon(s, (52, 40, 30), [(kx, h - 3), (kx + 3, h - 12 - rng.randint(0, 6)), (kx + 6, h - 3)])
        pygame.draw.polygon(s, (66, 50, 36), [(20, h - 4), (24, 26), (30, 26), (34, h - 4)])
        for i in range(7):                                   # hanging canopy
            cx = rng.randint(10, w - 10)
            cy = rng.randint(6, 30)
            r = rng.randint(9, 15)
            col = rng.choice([(40, 70, 48), (48, 82, 54), (34, 60, 44)])
            pygame.draw.circle(s, col, (cx, cy), r)
        for i in range(9):                                   # moss strands
            mx = rng.randint(8, w - 8)
            pygame.draw.line(s, (112, 130, 104), (mx, 24), (mx + rng.randint(-2, 2), rng.randint(36, 52)), 1)
        self._trees[variant] = s
        return s


GOLD_DK = (190, 156, 70)
