from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Blocked:
    """An exit that exists but cannot be used yet."""
    label: str
    text: str


@dataclass(frozen=True)
class Location:
    id: str
    name: str
    blurb: tuple                 # always shown
    npcs: tuple = ()
    exits: tuple = ()            # location ids
    ambient: tuple = ()          # Lines shown passively when conditions pass
    look: tuple = ()             # Lines shown by "Look around" (costs time)
    blocked: tuple = ()          # Blocked(...)
    can_rest: bool = True
