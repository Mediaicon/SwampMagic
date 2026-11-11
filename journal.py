"""The journal: topics, accounts, contradictions, evidence, cases, beliefs.

The journal records what was *said* and what was *found*. It never records what
is *true*.
"""
from __future__ import annotations

import config
import investigation
import ui


def show(game):
    while True:
        ui.clear()
        render(game)
        p = game.player
        labels = [f"Settle on a belief: {game.cases[cid].title}" for cid in p.assembled]
        labels.append("Back")
        choice = ui.menu(labels)
        if choice == len(labels) - 1:
            return
        form_belief(game, game.cases[p.assembled[choice]])


def render(game):
    p = game.player
    ui.rule("=", 40)
    ui.say(f"JOURNAL                         Day {p.day}")
    ui.rule("=", 40)

    if p.personal:
        ui.say()
        ui.say("YOUR OWN QUESTION")
        ui.say(f"  {p.personal}")
    ui.say()
    ui.say("TOPICS")
    for tid in p.topics:
        t = game.topics[tid]
        ui.say(f"  - {t.name}: {t.blurb}")

    ui.say()
    ui.say("ACCOUNTS")
    any_claims = False
    for q in game.questions.values():
        claims = [c for c in p.claims if c["question"] == q.id]
        if not claims:
            continue
        any_claims = True
        ui.say(f"  {q.text}")
        for c in claims:
            ui.say(f"    - {c['text']}")
        for a, b in game.contradictions():
            if a["question"] == q.id:
                ui.say(f"    ! {_who(game, a, b)} do not agree.")
    if not any_claims:
        ui.say("  Nothing yet.")

    ui.say()
    ui.say("EVIDENCE")
    if not p.clues:
        ui.say("  Nothing yet.")
    for cid in p.clues:
        clue = game.clues[cid]
        ui.say(f"  - {clue.name} ({clue.kind})")
        ui.say(f"      {clue.description}")
        for when, text in clue.details:
            if when.check(game):
                ui.say(f"      {text}")
        if clue.bears_on:
            qs = "; ".join(game.questions[q].text for q in clue.bears_on)
            ui.say(f"      May bear on: {qs}")

    ui.say()
    ui.say("CASES")
    if not game.cases:
        ui.say("  None.")
    for case in game.cases.values():
        state = "Assembled" if case.id in p.assembled else "Open"
        ui.say(f"  {case.title}  [{state}]")
        if config.SHOW_CASE_CHECKLIST and case.id not in p.assembled:
            st = investigation.status(game, case)
            ui.say(f"    [{'x' if st.sources >= st.need_sources else ' '}] "
                   f"Accounts from different people ({min(st.sources, st.need_sources)}/{st.need_sources})")
            ui.say(f"    [{'x' if st.physical >= st.need_physical else ' '}] "
                   f"Physical evidence ({min(st.physical, st.need_physical)}/{st.need_physical})")
        belief = p.beliefs.get(case.id)
        if belief:
            ui.say(f"    Your belief: {belief['text']}")

    if p.notes:
        ui.say()
        ui.say("NOTES")
        for n in p.notes:
            ui.say(f"  - {n}")
    ui.say()


def _who(game, a, b) -> str:
    if a["npc"] == b["npc"]:
        return f"{game.npcs[a['npc']].name}'s two statements"
    return f"{game.npcs[a['npc']].name} and {game.npcs[b['npc']].ref}"


def form_belief(game, case):
    """The player commits to a belief. The game never says whether it is right."""
    p = game.player
    seen, options = set(), []
    for c in p.claims:
        if c["question"] == case.question and c["stance"] not in seen:
            seen.add(c["stance"])
            options.append(("stance", c))
    labels = [f"Lean toward this: {c['text']}" for _, c in options]
    labels += ["Believe none of them. Not yet.", "Stop asking.", "Back"]

    ui.clear()
    ui.say(case.title)
    ui.say()
    choice = ui.menu(labels)
    if choice == len(labels) - 1:
        return

    p.flags.discard("stopped_asking")
    if choice < len(options):
        c = options[choice][1]
        p.beliefs[case.id] = {"kind": "stance", "stance": c["stance"], "text": c["text"], "day": p.day}
    elif choice == len(options):
        p.beliefs[case.id] = {"kind": "none", "stance": None,
                              "text": "None of the accounts is enough.", "day": p.day}
    else:
        p.flags.add("stopped_asking")
        p.beliefs[case.id] = {"kind": "stop", "stance": None,
                              "text": "You are no longer sure the answer should be found.", "day": p.day}

    ui.say_lines(["The journal keeps what you believed.",
                  "It does not keep whether you were right."])
    ui.pause()
