from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Player:
    awareness: int = 0
    fatigue: int = 0
    day: int = 1
    period: int = 0
    location: str = ""
    name: str = ""
    origin: str = ""
    personal: str = ""          # the player's own opening question (journal)
    skills: dict = field(default_factory=dict)   # skill_id -> rank
    pos: list = field(default_factory=list)      # overworld tile [x, y] (graphics front-end)

    trust: dict = field(default_factory=dict)         # npc_id -> int
    topics: list = field(default_factory=list)        # topic ids, discovery order
    clues: list = field(default_factory=list)         # clue ids, discovery order
    claims: list = field(default_factory=list)        # {npc, question, stance, text, day}
    notes: list = field(default_factory=list)
    beliefs: dict = field(default_factory=dict)       # case_id -> {kind, stance, text, day}
    assembled: list = field(default_factory=list)     # case ids
    visited: list = field(default_factory=list)       # location ids
    rapport_day: dict = field(default_factory=dict)   # npc_id -> day of last visit

    flags: set = field(default_factory=set)
    seen: set = field(default_factory=set)            # one-time effect keys
    noticed: set = field(default_factory=set)         # contradiction ids already noticed

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        for key in ("flags", "seen", "noticed"):
            d[key] = sorted(d[key])
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        p = cls()
        for key, value in d.items():
            if key in ("flags", "seen", "noticed"):
                value = set(value)
            if hasattr(p, key):
                setattr(p, key, value)
        return p
