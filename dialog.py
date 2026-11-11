"""Conversation engine.

Every NPC answers the same topics through the same machinery. What changes is
the NPC's authored Lines and the player's state (trust, Awareness, evidence).
Adding a new NPC or mystery is content work, not code work.
"""
from __future__ import annotations

import ui


def first_match(lines, game, npc_id=None):
    """Return (index, Line) for the first Line whose When passes, else None."""
    for i, line in enumerate(lines):
        if line.when.check(game, npc_id):
            return i, line
    return None


def converse(game, npc):
    while True:
        ui.clear()
        game.header()
        hit = first_match(npc.intro, game, npc.id)
        if hit:
            ui.say_lines(hit[1].say)

        labels, actions = [], []
        for tid in game.player.topics:
            labels.append(f"Ask about {game.topics[tid].name}")
            actions.append(("topic", tid))
        if game.player.clues:
            labels.append("Show them something you have found")
            actions.append(("show", None))
        labels.append(f"Spend time with {npc.ref}")
        actions.append(("rapport", None))
        labels.append("Leave")
        actions.append(("leave", None))

        kind, arg = actions[ui.menu(labels)]
        if kind == "leave":
            return
        if kind == "topic":
            ask_topic(game, npc, arg)
        elif kind == "show":
            show_clue(game, npc)
        elif kind == "rapport":
            spend_time(game, npc)


def ask_topic(game, npc, topic_id):
    hit = first_match(npc.topics.get(topic_id, ()), game, npc.id)
    if hit is None:
        ui.say_lines(npc.deflect)
    else:
        index, line = hit
        ui.say_lines(line.say)
        game.apply_once(f"{npc.id}:{topic_id}:{index}", line.do, npc.id)
    ui.pause()


def show_clue(game, npc):
    ui.say()
    ui.say("Show them what?")
    ids = list(game.player.clues)
    labels = [game.clues[c].name for c in ids] + ["Never mind"]
    choice = ui.menu(labels)
    if choice == len(ids):
        return
    clue_id = ids[choice]
    hit = first_match(npc.reactions.get(clue_id, ()), game, npc.id)
    if hit is None:
        ui.say_lines(npc.default_reaction)
    else:
        index, line = hit
        ui.say_lines(line.say)
        game.apply_once(f"{npc.id}:show:{clue_id}:{index}", line.do, npc.id)
    ui.pause()


def spend_time(game, npc):
    p = game.player
    if p.rapport_day.get(npc.id) == p.day:
        ui.say_lines([f"You have already spent time with {npc.ref} today. "
                      "There is nothing more to share until tomorrow."])
        ui.pause()
        return
    p.rapport_day[npc.id] = p.day
    hit = first_match(npc.rapport, game, npc.id)
    if hit:
        ui.say_lines(hit[1].say)
        game.apply(hit[1].do, npc.id)        # repeatable on purpose: once per day
    else:
        ui.say_lines(["You pass some time. Nothing is said that matters."])
    game.tick(1)
    ui.pause()
