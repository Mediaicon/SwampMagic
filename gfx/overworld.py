"""Walkable overworld + HUD + fast-travel map."""
from __future__ import annotations

import math
import random
from collections import deque

import pygame

import awareness
import config
import ui
from gfx import sprites, theme as T, world

STEP_TIME = 0.14          # seconds per tile


def graph_distance(game, a: str, b: str) -> int:
    if a == b:
        return 0
    seen, q = {a}, deque([(a, 0)])
    while q:
        node, d = q.popleft()
        for nxt in game.locations[node].exits:
            if nxt == b:
                return d + 1
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, d + 1))
    return 99


def eye_pips(aw: int) -> int:
    return sum(1 for t in config.EYE_THRESHOLDS if aw >= t)


class Overworld:
    def __init__(self, app, game):
        self.app, self.game = app, game
        self.grid = world.build_map()
        self.tiles = world.Tiles()
        p = game.player
        if not p.pos:
            p.pos = list(world.START_TILE)
        self.x, self.y = p.pos
        self.facing = (0, 1)
        self.move = None                       # (from, to, progress)
        self.step_phase = 0.0
        self.toast, self.toast_until = "", 0.0
        self.fog_noise = self._make_noise()
        self.vignette = None

    # ------------------------------------------------------------------ misc --
    def _make_noise(self):
        rng = random.Random(3)
        return [[rng.random() for _ in range(world.MAP_H)] for _ in range(world.MAP_W)]

    def say_toast(self, s, secs=2.2):
        self.toast, self.toast_until = s, self.app.t + secs

    @property
    def pixel_pos(self):
        if self.move:
            (x0, y0), (x1, y1), pr = self.move
            return x0 + (x1 - x0) * pr, y0 + (y1 - y0) * pr
        return float(self.x), float(self.y)

    # --------------------------------------------------------------- drawing --
    def draw_scene(self, surf=None, frame=True):
        """Draw the world viewport. Also used as the backdrop for dialogue panels."""
        surf = surf or self.app.screen
        px, py = self.pixel_pos
        cam_x = max(0, min(world.MAP_W * T.TILE - T.VIEW_W, px * T.TILE + T.TILE / 2 - T.VIEW_W / 2))
        cam_y = max(0, min(world.MAP_H * T.TILE - T.VIEW_H, py * T.TILE + T.TILE / 2 - T.VIEW_H / 2))
        cx, cy = int(cam_x), int(cam_y)
        view = pygame.Surface((T.VIEW_W, T.VIEW_H))
        t = self.app.t
        wf = int(t * 2.5) % 4
        x0, y0 = cx // T.TILE, cy // T.TILE
        x1 = min(world.MAP_W, x0 + T.VIEW_W // T.TILE + 2)
        y1 = min(world.MAP_H, y0 + T.VIEW_H // T.TILE + 2)
        for ty in range(y0, y1):
            for tx in range(x0, x1):
                ch = self.grid[ty][tx]
                img = self.tiles.water[wf] if ch == "~" else self.tiles.ground(ch, tx, ty)
                view.blit(img, (tx * T.TILE - cx, ty * T.TILE - cy))
        # door decoration + store sign
        for (dx, dy), kind in world.SHACK_DOORS.items():
            if x0 - 1 <= dx <= x1:
                sprites.door_mark(view, (dx * T.TILE - cx + 6, dy * T.TILE - cy + 4, T.TILE - 12, T.TILE - 4), kind)
        sx, sy = 24 * T.TILE - cx, 9 * T.TILE - cy
        T.text(view, "STORE", (sx + 16, sy - 24), 13, (214, 190, 120), bold=True, center=True)
        # y-sorted objects
        objs = []
        for ty in range(max(0, y0 - 2), min(world.MAP_H, y1 + 3)):
            for tx in range(max(0, x0 - 1), min(world.MAP_W, x1 + 1)):
                if self.grid[ty][tx] == "T":
                    objs.append(((ty + 1) * T.TILE, "tree", tx, ty))
        for nid, (nx, ny) in world.NPC_SPOTS.items():
            objs.append(((ny + 1) * T.TILE - 2, nid, nx, ny))
        if "rusted_iron_cross" in self.game.player.clues:
            objs.append((world.CROSS_SPOT[1] * T.TILE + 20, "cross", *world.CROSS_SPOT))
        objs.append((py * T.TILE + T.TILE - 2, "player", px, py))
        objs.sort(key=lambda o: o[0])
        for _, kind, ox, oy in objs:
            if kind == "tree":
                s = self.tiles.tree((ox * 31 + oy * 17) % 5)
                view.blit(s, (ox * T.TILE - cx - 10, oy * T.TILE - cy + T.TILE - s.get_height() + 2))
            elif kind == "ferryman":
                sprites.ferryman(view, int(ox * T.TILE - cx + 16), int(oy * T.TILE - cy + 30), t)
            elif kind == "old_woman":
                sprites.old_woman(view, int(ox * T.TILE - cx + 16), int(oy * T.TILE - cy + 30), t)
            elif kind == "cross":
                sprites.iron_cross(view, int(ox * T.TILE - cx + 16), int(oy * T.TILE - cy + 30))
            else:
                pal = sprites.palette(self.game.player.origin)
                sprites.person(view, int(ox * T.TILE - cx + 16), int(oy * T.TILE - cy + 30), pal,
                               self.facing, self.step_phase)
        self._atmosphere(view, cx, cy, t)
        if frame:
            surf.blit(view, (0, 0))
            self._toast(surf)
            self.draw_hud(surf)
        else:
            surf.blit(view, (0, 0))

    def _atmosphere(self, view, cx, cy, t):
        p = self.game.player
        # fog: gentle everywhere, thicker toward the church road once Awareness is high
        x0, y0 = cx // T.TILE, cy // T.TILE
        x1 = min(world.MAP_W, x0 + T.VIEW_W // T.TILE + 2)
        y1 = min(world.MAP_H, y0 + T.VIEW_H // T.TILE + 2)
        small = pygame.Surface((x1 - x0, y1 - y0), pygame.SRCALPHA)
        for ty in range(y0, y1):
            for tx in range(x0, x1):
                n = self.fog_noise[(tx + int(t * 0.4)) % world.MAP_W][ty]
                a = 22 + n * 26
                if ty < 11:
                    a += (11 - ty) * 5                      # the road runs into the fog
                if p.awareness >= 20 and tx < 12 and ty < 12:
                    a += 26                                 # matches the dock's hidden observation
                if self.grid[ty][tx] == "~":
                    a += 14
                if self.grid[ty][tx] == "F":
                    a = 215
                small.set_at((tx - x0, ty - y0), (*T.FOG, min(225, int(a))))
        fog = pygame.transform.smoothscale(small, ((x1 - x0) * T.TILE, (y1 - y0) * T.TILE))
        view.blit(fog, (x0 * T.TILE - cx, y0 * T.TILE - cy))
        tint = {0: (255, 236, 200, 22), 1: (255, 255, 255, 0), 2: (255, 150, 70, 52), 3: (8, 18, 48, 130)}[p.period]
        if tint[3]:
            layer = pygame.Surface(view.get_size(), pygame.SRCALPHA)
            layer.fill(tint)
            view.blit(layer, (0, 0))
        pips = eye_pips(p.awareness)                          # a faint green rim as the Eye opens
        if pips:
            if self.vignette is None or self.vignette[0] != pips:
                v = pygame.Surface((T.VIEW_W, T.VIEW_H), pygame.SRCALPHA)
                for i in range(30):
                    a = int((30 - i) * pips * 0.5)
                    pygame.draw.rect(v, (40, 160, 80, a), (i, i, T.VIEW_W - 2 * i, T.VIEW_H - 2 * i), 1)
                self.vignette = (pips, v)
            view.blit(self.vignette[1], (0, 0))

    def _toast(self, surf):
        if self.app.t < self.toast_until and self.toast:
            r = T.font(18).size(self.toast)
            box = pygame.Rect(T.VIEW_W // 2 - r[0] // 2 - 14, 18, r[0] + 28, 34)
            T.panel(surf, box, alpha=220)
            T.text(surf, self.toast, (box.centerx, box.y + 6), 18, T.TEXT, center=True)

    # ------------------------------------------------------------------- HUD --
    def draw_hud(self, surf):
        p = self.game.player
        x0 = T.VIEW_W
        pygame.draw.rect(surf, (18, 22, 18), (x0, 0, T.SIDEBAR_W, T.SCREEN_H))
        pygame.draw.line(surf, T.PANEL_EDGE, (x0, 0), (x0, T.SCREEN_H), 2)
        y = 14
        T.text(surf, p.name or "Stranger", (x0 + 16, y), 22, T.GOLD, bold=True)
        origin = self.game.c.origins.get(p.origin)
        if origin:
            T.text(surf, origin.name, (x0 + 16, y + 26), 15, T.TEXT_DIM, italic=True)
        y += 56
        loc = self.game.locations[p.location]
        T.text(surf, loc.name, (x0 + 16, y), 17, T.TEXT)
        T.text(surf, f"Day {p.day}   {config.PERIODS[p.period]}", (x0 + 16, y + 22), 16, T.TEXT_DIM)
        self._clock(surf, x0 + T.SIDEBAR_W - 44, y + 12, p.period)
        y += 58
        pygame.draw.line(surf, T.PANEL_EDGE, (x0 + 14, y), (x0 + T.SIDEBAR_W - 14, y))
        y += 14
        T.eye(surf, (x0 + T.SIDEBAR_W // 2, y + 44), 150, eye_pips(p.awareness), len(config.EYE_THRESHOLDS), self.app.t)
        y += 96
        if config.SHOW_AWARENESS_NUMBER:
            T.text(surf, f"Awareness {p.awareness}", (x0 + T.SIDEBAR_W // 2, y), 16, T.TEXT_DIM, center=True)
        y += 30
        T.text(surf, "Condition", (x0 + 16, y), 15, T.TEXT_DIM)
        T.text(surf, awareness.fatigue_label(p.fatigue), (x0 + T.SIDEBAR_W - 16 - T.font(17).size(awareness.fatigue_label(p.fatigue))[0], y - 1), 17, T.TEXT)
        y += 24
        bar = pygame.Rect(x0 + 16, y, T.SIDEBAR_W - 32, 8)
        pygame.draw.rect(surf, (44, 50, 44), bar, border_radius=4)
        fill = bar.copy()
        fill.w = int(bar.w * p.fatigue / config.FATIGUE_MAX)
        pygame.draw.rect(surf, (150, 120, 60), fill, border_radius=4)
        y += 30
        pygame.draw.line(surf, T.PANEL_EDGE, (x0 + 14, y), (x0 + T.SIDEBAR_W - 14, y))
        y += 14
        hints = [("E", "Interact"), ("J", "Journal"), ("C", "Character"), ("M", "Map / travel"), ("Esc", "Menu")]
        for key, label in hints:
            kr = pygame.Rect(x0 + 16, y, 38, 24)
            pygame.draw.rect(surf, (36, 46, 36), kr, border_radius=5)
            pygame.draw.rect(surf, T.PANEL_EDGE, kr, 1, border_radius=5)
            T.text(surf, key, (kr.centerx, kr.y + 3), 14, T.GOLD, bold=True, center=True)
            T.text(surf, label, (x0 + 64, y + 3), 15, T.TEXT)
            y += 30
        here = world.zone_at(self.x, self.y)
        if here == p.location:
            T.text(surf, "Press E here", (x0 + T.SIDEBAR_W // 2, T.SCREEN_H - 30), 15, T.GREEN, center=True)

    def _clock(self, surf, cx, cy, period):
        if period == config.NIGHT:
            pygame.draw.circle(surf, (210, 214, 226), (cx, cy), 12)
            pygame.draw.circle(surf, (18, 22, 18), (cx + 6, cy - 3), 11)
        else:
            col = [(236, 214, 140), (250, 232, 120), (240, 150, 70)][period]
            pygame.draw.circle(surf, col, (cx, cy), 11)
            for a in range(0, 360, 45):
                r = math.radians(a)
                pygame.draw.line(surf, col, (cx + math.cos(r) * 15, cy + math.sin(r) * 15),
                                 (cx + math.cos(r) * 19, cy + math.sin(r) * 19), 2)

    # -------------------------------------------------------------- movement --
    def try_step(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        self.facing = (dx, dy)
        if 0 <= nx < world.MAP_W and 0 <= ny < world.MAP_H and self.grid[ny][nx] == "F":
            self._bump_fog()
            return
        if world.walkable(self.grid, nx, ny):
            self.move = ((self.x, self.y), (nx, ny), 0.0)

    def _bump_fog(self):
        loc = self.game.locations[self.game.player.location]
        if loc.blocked:
            ui.say_lines([loc.blocked[0].text])
            ui.pause()

    def update(self, dt):
        self.step_phase += dt * 9 if self.move else 0
        if self.move:
            a, b, pr = self.move
            pr += dt / STEP_TIME
            if pr >= 1.0:
                self.x, self.y = b
                self.move = None
                self.game.player.pos = [self.x, self.y]
                self._arrived()
            else:
                self.move = (a, b, pr)

    def _arrived(self):
        zone = world.zone_at(self.x, self.y)
        p = self.game.player
        if zone and zone != p.location:
            self.enter(zone)

    def enter(self, loc_id, hops=None):
        g, p = self.game, self.game.player
        hops = graph_distance(g, p.location, loc_id) if hops is None else hops
        p.location = loc_id
        if loc_id not in p.visited:
            p.visited.append(loc_id)
        g.tick(max(1, hops))
        g.save()
        self.say_toast(g.locations[loc_id].name)
        g.visit()

    def interact(self):
        zone = world.zone_at(self.x, self.y)
        if zone == self.game.player.location:
            self.game.visit()
        else:
            self.say_toast("Nothing here.")


# --------------------------------------------------------------- fast travel --
def map_screen(app, ov):
    """Whole-map overview. Click a visited place (or press its number) to travel."""
    game, p = ov.game, ov.game.player
    scale = 14
    mw, mh = world.MAP_W * scale, world.MAP_H * scale
    mini = pygame.Surface((mw, mh))
    colors = {".": (66, 62, 40), "r": (78, 98, 56), "p": (98, 84, 58), ",": (112, 96, 66), "=": (112, 82, 52),
              "~": (26, 46, 48), "T": (36, 62, 42), "R": (60, 46, 40), "W": (96, 76, 54), "D": (50, 36, 28),
              "F": (170, 182, 172)}
    for y in range(world.MAP_H):
        for x in range(world.MAP_W):
            pygame.draw.rect(mini, colors.get(ov.grid[y][x], (0, 0, 0)), (x * scale, y * scale, scale, scale))
    visible = [l for l in game.locations.values()
               if l.id in p.visited or any(l.id in game.locations[v].exits for v in p.visited)]
    while True:
        app.t = pygame.time.get_ticks() / 1000
        app.screen.fill((14, 18, 14))
        T.text(app.screen, "THE REGION", (24, 18), 26, T.GOLD, bold=True)
        origin = pygame.Rect(24, 62, mw, mh)
        app.screen.blit(mini, origin.topleft)
        fog = pygame.Surface((mw, mh), pygame.SRCALPHA)
        fog.fill((170, 182, 172, 40))
        app.screen.blit(fog, origin.topleft)
        pygame.draw.rect(app.screen, T.PANEL_EDGE, origin, 2)
        marks = []
        for i, loc in enumerate(visible):
            ax, ay = world.ANCHORS[loc.id]
            pos = (origin.x + ax * scale + scale // 2, origin.y + ay * scale + scale // 2)
            known = loc.id in p.visited
            marks.append((loc, pos, known))
            col = T.GOLD if known else T.TEXT_DIM
            pygame.draw.circle(app.screen, (14, 18, 14), pos, 11)
            pygame.draw.circle(app.screen, col, pos, 11, 2)
            T.text(app.screen, str(i + 1) if known else "?", (pos[0], pos[1] - 9), 15, col, bold=True, center=True)
            if loc.id == p.location:
                pygame.draw.circle(app.screen, T.GREEN, pos, 16, 2)
        # you are here
        pxx, pyy = ov.x, ov.y
        pygame.draw.circle(app.screen, (240, 240, 240), (origin.x + pxx * scale + 5, origin.y + pyy * scale + 5), 4)
        # list
        lx = origin.right + 24
        T.text(app.screen, "Travel", (lx, 62), 20, T.TEXT)
        T.text(app.screen, "White dot: you", (24, 62 + mh + 10), 14, T.TEXT_DIM)
        y = 96
        rects = []
        mx, my = pygame.mouse.get_pos()
        for i, (loc, pos, known) in enumerate(marks):
            r = pygame.Rect(lx, y, T.SCREEN_W - lx - 20, 54)
            rects.append(r)
            hops = graph_distance(game, p.location, loc.id)
            hover = r.collidepoint(mx, my)
            T.panel(app.screen, r, fill=(40, 56, 40) if hover and known else (24, 30, 24), edge=T.GOLD if hover and known else T.PANEL_EDGE, alpha=255)
            label = loc.name if known else "Unexplored"
            T.text(app.screen, f"{i + 1}. {label}", (r.x + 12, r.y + 6), 17, T.TEXT if known else T.TEXT_DIM)
            sub = "You are here" if loc.id == p.location else (f"{hops} stop{'s' if hops != 1 else ''}" if known else "Reachable on foot")
            T.text(app.screen, sub, (r.x + 12, r.y + 29), 14, T.TEXT_DIM)
            y += 62
        T.text(app.screen, "Click a place or press its number.   Esc to close.", (24, T.SCREEN_H - 30), 15, T.TEXT_DIM)
        pygame.display.flip()
        app.clock.tick(60)
        for ev in app.events():
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_m):
                    return
                if pygame.K_1 <= ev.key <= pygame.K_9 and ev.key - pygame.K_1 < len(marks):
                    if _fast_travel(ov, marks[ev.key - pygame.K_1]):
                        return
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for r, m in zip(rects, marks):
                    if r.collidepoint(ev.pos) and _fast_travel(ov, m):
                        return


def _fast_travel(ov, mark) -> bool:
    loc, _, known = mark
    p = ov.game.player
    if not known or loc.id == p.location:
        return False
    hops = graph_distance(ov.game, p.location, loc.id)
    ov.x, ov.y = world.ANCHORS[loc.id]
    ov.move = None
    p.pos = [ov.x, ov.y]
    ov.enter(loc.id, hops)
    return True
