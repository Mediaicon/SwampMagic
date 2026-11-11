"""Questions, Cases and evidence.

A Question is something NPCs make Claims about. Authors declare which stances
conflict, so contradiction tracking is explicit, never guessed.

A Case is a Question the player can *assemble*. Assembling never produces the
answer (Design Doc ch. 10A: do not mark a conclusion correct on the player's
behalf). It only unlocks the player's ability to commit to a belief.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    conflicts: tuple = ()        # ((stance_a, stance_b), ...)

    def conflict(self, a: str, b: str) -> bool:
        return any({a, b} == set(pair) for pair in self.conflicts)


@dataclass(frozen=True)
class Case:
    id: str
    question: str                # Question id
    title: str
    min_sources: int = 2
    min_physical: int = 1
    assembled: tuple = ()        # text shown when the case first comes together


@dataclass
class CaseStatus:
    sources: int
    physical: int
    need_sources: int
    need_physical: int

    @property
    def complete(self) -> bool:
        return self.sources >= self.need_sources and self.physical >= self.need_physical


def status(game, case: Case) -> CaseStatus:
    p = game.player
    npcs = {c["npc"] for c in p.claims if c["question"] == case.question}
    physical = [
        cid for cid in p.clues
        if game.clues[cid].kind == "physical" and case.question in game.clues[cid].bears_on
    ]
    return CaseStatus(len(npcs), len(physical), case.min_sources, case.min_physical)
