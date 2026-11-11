from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NPC:
    id: str
    name: str                    # "The ferryman"
    ref: str                     # "the ferryman"  (mid-sentence form)
    ordinary: bool = False       # True = loses trust as the player's Awareness grows
    intro: tuple = ()            # Lines; first match is shown when conversation opens
    topics: dict = field(default_factory=dict)      # topic_id -> tuple[Line]
    deflect: tuple = ("They have nothing to say about that.",)
    rapport: tuple = ()          # Lines for "Spend time with ..."
    reactions: dict = field(default_factory=dict)   # clue_id -> tuple[Line]
    default_reaction: tuple = ("They look at it, then at you.",)
