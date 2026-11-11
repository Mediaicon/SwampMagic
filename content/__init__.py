"""Content loader + validator. Run `python main.py --check` to validate content."""
from __future__ import annotations

from dataclasses import dataclass

from rules import Line, NOTHING

from .cases import CASES, QUESTIONS
from .clues import CLUES
from .locations import GLOBAL_AMBIENT, LOCATIONS, START_LOCATION
from .npcs import NPCS
from .origins import ORIGINS
from .topics import START_TOPICS, TOPICS


@dataclass
class Content:
    topics: dict
    npcs: dict
    locations: dict
    clues: dict
    questions: dict
    cases: dict
    start_location: str
    start_topics: tuple
    global_ambient: tuple
    origins: dict


def load() -> Content:
    return Content(
        topics={t.id: t for t in TOPICS},
        npcs={n.id: n for n in NPCS},
        locations={l.id: l for l in LOCATIONS},
        clues={c.id: c for c in CLUES},
        questions={q.id: q for q in QUESTIONS},
        cases={c.id: c for c in CASES},
        start_location=START_LOCATION,
        start_topics=START_TOPICS,
        global_ambient=GLOBAL_AMBIENT,
        origins={o.id: o for o in ORIGINS},
    )


def _lines(c: Content):
    for n in c.npcs.values():
        yield from n.intro
        yield from n.rapport
        for group in list(n.topics.values()) + list(n.reactions.values()):
            yield from group
    for loc in c.locations.values():
        yield from loc.ambient
        yield from loc.look
    yield from c.global_ambient
    for clue in c.clues.values():
        for when, _ in clue.details:
            yield Line(("",), when, NOTHING)
        yield Line(("",), do=clue.do)


def validate(c: Content) -> list:
    """Return a list of human-readable problems. Empty list = content is consistent."""
    errs = []
    for n in c.npcs.values():
        for tid in n.topics:
            if tid not in c.topics:
                errs.append(f"NPC {n.id}: unknown topic '{tid}'")
        for cid in n.reactions:
            if cid not in c.clues:
                errs.append(f"NPC {n.id}: reaction to unknown clue '{cid}'")
    for loc in c.locations.values():
        for e in loc.exits:
            if e not in c.locations:
                errs.append(f"Location {loc.id}: unknown exit '{e}'")
            elif loc.id not in c.locations[e].exits:
                errs.append(f"Location {loc.id}: exit '{e}' is one-way")
        for nid in loc.npcs:
            if nid not in c.npcs:
                errs.append(f"Location {loc.id}: unknown NPC '{nid}'")
    if c.start_location not in c.locations:
        errs.append("start_location does not exist")
    for t in c.start_topics:
        if t not in c.topics:
            errs.append(f"start topic '{t}' does not exist")
    for clue in c.clues.values():
        for q in clue.bears_on:
            if q not in c.questions:
                errs.append(f"Clue {clue.id}: unknown question '{q}'")
    for case in c.cases.values():
        if case.question not in c.questions:
            errs.append(f"Case {case.id}: unknown question '{case.question}'")
    from origin import CREATION_MAX_RANK, SKILL_IDS
    for o in c.origins.values():
        if set(o.skills) != set(SKILL_IDS):
            errs.append(f"Origin {o.id}: skills must be exactly {SKILL_IDS}")
        if any(v > CREATION_MAX_RANK - 1 for v in o.skills.values()):
            errs.append(f"Origin {o.id}: base rank too high (leave room for creation points)")
        for t in o.start_topics:
            if t not in c.topics:
                errs.append(f"Origin {o.id}: unknown start topic '{t}'")
    for line in _lines(c):
        w, d = line.when, line.do
        for t in list(w.has_topics) + list(d.topics):
            if t not in c.topics:
                errs.append(f"unknown topic '{t}'")
        for cl in list(w.has_clues) + list(w.lacks_clues) + list(d.clues):
            if cl not in c.clues:
                errs.append(f"unknown clue '{cl}'")
        for skill, _ in w.min_skills:
            if skill not in SKILL_IDS:
                errs.append(f"unknown skill '{skill}'")
        for npc, _ in w.npc_trust:
            if npc not in c.npcs:
                errs.append(f"unknown npc '{npc}' in When.npc_trust")
        if d.claim:
            if d.claim.question not in c.questions:
                errs.append(f"claim uses unknown question '{d.claim.question}'")
            else:
                q = c.questions[d.claim.question]
                stances = {s for pair in q.conflicts for s in pair}
                # (stances not in any conflict pair are fine; just informational)
    return sorted(set(errs))
