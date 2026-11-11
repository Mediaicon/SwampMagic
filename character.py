"""Character creation rules (pure logic, no graphics)."""
from __future__ import annotations

from origin import CREATION_MAX_RANK, CREATION_POINTS, SKILL_IDS
from player import Player


def points_left(allocation: dict) -> int:
    return CREATION_POINTS - sum(allocation.get(s, 0) for s in SKILL_IDS)


def final_skills(origin, allocation: dict) -> dict:
    return {s: origin.skills.get(s, 0) + allocation.get(s, 0) for s in SKILL_IDS}


def can_add(origin, allocation: dict, skill: str) -> bool:
    return (points_left(allocation) > 0
            and final_skills(origin, allocation)[skill] < CREATION_MAX_RANK)


def can_remove(allocation: dict, skill: str) -> bool:
    return allocation.get(skill, 0) > 0


def valid(origin, allocation: dict) -> bool:
    return (points_left(allocation) == 0
            and all(allocation.get(s, 0) >= 0 for s in SKILL_IDS)
            and all(v <= CREATION_MAX_RANK for v in final_skills(origin, allocation).values()))


def build_player(name: str, origin, allocation: dict, start_location: str, base_topics) -> Player:
    p = Player(location=start_location)
    p.name = name.strip() or "Stranger"
    p.origin = origin.id
    p.skills = final_skills(origin, allocation)
    p.personal = f"{origin.mystery_title}: {origin.mystery_text}"
    p.topics = list(base_topics) + [t for t in origin.start_topics if t not in base_topics]
    p.visited = [start_location]
    return p
