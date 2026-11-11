"""The small rule language every piece of content is written in.

    When  - a condition  ("is this line available right now?")
    Do    - an effect    ("what happens the first time the player sees it?")
    Claim - a statement an NPC makes about an investigation Question
    Line  - some text + When + Do. Dialogue, observations, rapport, reactions
            and clue details are all Lines.

Content authors only ever use these. The engine (game.py) interprets them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class When:
    min_awareness: Optional[int] = None
    max_awareness: Optional[int] = None
    min_trust: Optional[int] = None      # effective trust with the speaking NPC
    max_trust: Optional[int] = None
    npc_trust: tuple = ()                # ((npc_id, minimum), ...)
    has_clues: tuple = ()
    lacks_clues: tuple = ()
    has_topics: tuple = ()
    flags: tuple = ()
    not_flags: tuple = ()
    min_day: Optional[int] = None
    period_in: tuple = ()                # indexes into config.PERIODS
    min_skills: tuple = ()               # ((skill_id, minimum_rank), ...)

    def check(self, game, npc_id=None) -> bool:
        p = game.player
        if self.min_awareness is not None and p.awareness < self.min_awareness:
            return False
        if self.max_awareness is not None and p.awareness > self.max_awareness:
            return False
        if self.min_trust is not None or self.max_trust is not None:
            if npc_id is None:
                return False
            t = game.effective_trust(npc_id)
            if self.min_trust is not None and t < self.min_trust:
                return False
            if self.max_trust is not None and t > self.max_trust:
                return False
        for npc, minimum in self.npc_trust:
            if game.effective_trust(npc) < minimum:
                return False
        if any(c not in p.clues for c in self.has_clues):
            return False
        if any(c in p.clues for c in self.lacks_clues):
            return False
        if any(t not in p.topics for t in self.has_topics):
            return False
        if any(f not in p.flags for f in self.flags):
            return False
        if any(f in p.flags for f in self.not_flags):
            return False
        if self.min_day is not None and p.day < self.min_day:
            return False
        if self.period_in and p.period not in self.period_in:
            return False
        if any(p.skills.get(s, 0) < n for s, n in self.min_skills):
            return False
        return True


@dataclass(frozen=True)
class Claim:
    question: str      # id of a Question (investigation.py)
    stance: str        # author-defined label; Questions declare which conflict
    text: str          # journal wording, third person: "The ferryman said ..."


@dataclass(frozen=True)
class Do:
    topics: tuple = ()
    clues: tuple = ()
    flags: tuple = ()
    awareness: int = 0
    trust: int = 0         # with the NPC who is speaking
    fatigue: int = 0
    note: Optional[str] = None
    claim: Optional[Claim] = None


@dataclass(frozen=True)
class Line:
    say: tuple
    when: When = When()
    do: Do = Do()


ALWAYS = When()
NOTHING = Do()
W = When


def L(*say, when=ALWAYS, do=NOTHING) -> Line:
    """Shorthand: L('text', 'more text', when=W(...), do=Do(...))"""
    return Line(tuple(say), when, do)
