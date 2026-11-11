from __future__ import annotations

from dataclasses import dataclass

from rules import Do, NOTHING


@dataclass(frozen=True)
class Clue:
    id: str
    name: str
    kind: str                    # "physical" | "document"
    description: str
    details: tuple = ()          # ((When, text), ...)  revealed by Awareness etc.
    bears_on: tuple = ()         # Question ids it *may* be relevant to. Never says how.
    do: Do = NOTHING             # effects when found
