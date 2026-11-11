"""Origins and skills.

Design Doc ch. 9: Origins are BACKGROUNDS, not classes. They provide perspective,
contacts, skills and initial mysteries. They do not determine destiny, lock out any
tradition or ending, and carry no power that stands in for a class.

Skills are NOT in the Design Doc. They are a prototype layer (small on purpose):
they change what you can *notice*, how fast people *open up*, what you can
*recognise*, and how well you *endure*. None of them is Awareness, and none can
answer a Protected Mystery.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    blurb: str


SKILLS = (
    Skill("perception", "Perception", "Notice what is physically there."),
    Skill("rapport", "Rapport", "People open up sooner."),
    Skill("lore", "Lore", "Recognise old things, and what people mean by them."),
    Skill("resolve", "Resolve", "Endure the cost of staying awake."),
)
SKILL_IDS = tuple(s.id for s in SKILLS)

CREATION_POINTS = 3
CREATION_MAX_RANK = 4


@dataclass(frozen=True)
class Origin:
    id: str
    name: str
    tagline: str
    perspective: str
    skills: dict                 # base ranks
    contact: str                 # PROVISIONAL role label, not a named character
    mystery_title: str           # the personal mystery (Design Doc ch. 10)
    mystery_text: str
    start_topics: tuple = ()
