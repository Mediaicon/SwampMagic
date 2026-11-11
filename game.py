"""The Game object: state + rules + the location loop.

Everything player-visible that is *authored* lives in content/. Everything that
is *mechanical* lives here.
"""
from __future__ import annotations

import json
import os

import awareness
import config
import dialog
import journal
import ui
from player import Player
from rules import Do

SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")


class Game:
    def __init__(self, content, player=None, debug=False):
        self.c = content
        self.topics = content.topics
        self.npcs = content.npcs
        self.locations = content.locations
        self.clues = content.clues
        self.questions = content.questions
        self.cases = content.cases
        self.debug = debug
        self.player = player or self.new_player()
        self.show_journal = lambda: journal.show(self)   # GUI replaces this

    def new_player(self) -> Player:
        p = Player(location=self.c.start_location)
        p.topics = list(self.c.start_topics)
        p.visited = [self.c.start_location]
        return p

    # ------------------------------------------------------------- trust ----
    def raw_trust(self, npc_id: str) -> int:
        return self.player.trust.get(npc_id, 0)

    def belonging_penalty(self, npc_id: str) -> int:
        """Awareness makes ordinary life harder to belong to (Design Doc ch. 8)."""
        if not self.npcs[npc_id].ordinary:
            return 0
        return self.player.awareness // config.BELONGING_STEP + len(self.player.assembled)

    def effective_trust(self, npc_id: str) -> int:
        penalty = self.belonging_penalty(npc_id)
        if self.player.fatigue >= config.WORN_AT:
            penalty += 1
        bonus = self.player.skills.get("rapport", 0) // 2     # Rapport: people open up sooner
        return self.raw_trust(npc_id) - penalty + bonus

    def change_trust(self, npc_id: str, delta: int):
        t = self.raw_trust(npc_id) + delta
        self.player.trust[npc_id] = max(0, min(config.TRUST_MAX, t))

    # -------------------------------------------------- awareness / body ----
    def gain_awareness(self, n: int):
        self.player.awareness = max(0, self.player.awareness + n)

    def change_fatigue(self, n: int):
        self.player.fatigue = max(0, min(config.FATIGUE_MAX, self.player.fatigue + n))

    # ------------------------------------------------------ discoveries ----
    def learn_topic(self, topic_id: str):
        if topic_id in self.player.topics:
            return
        self.player.topics.append(topic_id)
        ui.block("NEW TOPIC DISCOVERED", self.topics[topic_id].name)

    def add_clue(self, clue_id: str):
        if clue_id in self.player.clues:
            return
        clue = self.clues[clue_id]
        self.player.clues.append(clue_id)
        ui.block("CLUE FOUND", clue.name)
        ui.say(clue.description)
        ui.say()
        self.apply(clue.do)

    def add_note(self, text: str):
        if text not in self.player.notes:
            self.player.notes.append(text)

    def add_claim(self, npc_id: str, claim):
        p = self.player
        if any(c["npc"] == npc_id and c["question"] == claim.question and c["stance"] == claim.stance
               for c in p.claims):
            return
        entry = {"npc": npc_id, "question": claim.question, "stance": claim.stance,
                 "text": claim.text, "day": p.day}
        p.claims.append(entry)
        question = self.questions[claim.question]
        for other in p.claims[:-1]:
            if other["question"] == claim.question and question.conflict(other["stance"], claim.stance):
                cid = "|".join(sorted([f"{other['npc']}:{other['stance']}", f"{npc_id}:{claim.stance}"]))
                cid = f"{claim.question}|{cid}"
                if cid not in p.noticed:
                    p.noticed.add(cid)
                    ui.block("JOURNAL UPDATED", "Two accounts do not agree.")
                    self.gain_awareness(config.GAIN_CONTRADICTION)

    def contradictions(self):
        out, claims = [], self.player.claims
        for i, a in enumerate(claims):
            for b in claims[i + 1:]:
                if a["question"] == b["question"] and \
                        self.questions[a["question"]].conflict(a["stance"], b["stance"]):
                    out.append((a, b))
        return out

    def check_cases(self):
        import investigation
        p = self.player
        for case in self.cases.values():
            if case.id in p.assembled:
                continue
            if investigation.status(self, case).complete:
                p.assembled.append(case.id)
                ui.block("JOURNAL UPDATED", case.title)
                ui.say_lines(case.assembled)
                self.gain_awareness(config.GAIN_CASE_ASSEMBLED)
                self.change_fatigue(1)

    # ----------------------------------------------------------- effects ----
    def apply(self, do: Do, npc_id=None):
        for t in do.topics:
            self.learn_topic(t)
        for c in do.clues:
            self.add_clue(c)
        self.player.flags.update(do.flags)
        if do.trust and npc_id:
            self.change_trust(npc_id, do.trust)
        if do.awareness:
            self.gain_awareness(do.awareness)
        if do.fatigue:
            self.change_fatigue(do.fatigue)
        if do.note:
            self.add_note(do.note)
        if do.claim and npc_id:
            self.add_claim(npc_id, do.claim)
        self.check_cases()

    def apply_once(self, key: str, do: Do, npc_id=None) -> bool:
        """Effects fire the first time only, so nothing can be farmed."""
        if key in self.player.seen:
            return False
        self.player.seen.add(key)
        self.apply(do, npc_id)
        return True

    # -------------------------------------------------------------- time ----
    def tick(self, n: int = 1):
        p = self.player
        for _ in range(n):
            p.period += 1
            if p.period >= len(config.PERIODS):
                p.period = 0
                p.day += 1
            if p.period == config.NIGHT and p.skills.get("resolve", 0) < 3:
                self.change_fatigue(1)      # staying awake through the night costs

    # ------------------------------------------------------------ screens ----
    def header(self):
        if ui.HUD:                  # graphical front-end draws its own HUD
            return
        p = self.player
        loc = self.locations[p.location]
        ui.rule("=")
        ui.say("SWAMP MAGIC")
        ui.rule("=")
        ui.say(f"Location: {loc.name:<30} Day {p.day}, {config.PERIODS[p.period]}")
        parts = []
        if config.SHOW_AWARENESS_NUMBER:
            parts.append(f"Awareness: {p.awareness}")
        parts.append(f"Green Eye: {awareness.eye(p.awareness)}")
        parts.append(f"Condition: {awareness.fatigue_label(p.fatigue)}")
        ui.say("   ".join(parts))
        ui.rule("=")
        ui.say()

    def scene(self):
        loc = self.locations[self.player.location]
        ui.clear()
        self.header()
        ui.say(loc.name.upper())
        ui.rule("-", 40)
        for text in loc.blurb:
            ui.say(text)
        shown = []
        for i, line in enumerate(loc.ambient):
            if line.when.check(self):
                shown.append((f"amb:{loc.id}:{i}", line))
        for i, line in enumerate(self.c.global_ambient):
            if line.when.check(self):
                shown.append((f"gamb:{i}", line))
        for key, line in shown:
            for text in line.say:
                ui.say(text)
            self.apply_once(key, line.do)
        ui.say()

    # ----------------------------------------------------------- actions ----
    def look(self):
        loc = self.locations[self.player.location]
        shown = False
        ui.say()
        for i, line in enumerate(loc.look):
            if line.when.check(self):
                shown = True
                ui.say_lines(line.say)
                self.apply_once(f"look:{loc.id}:{i}", line.do)
        if not shown:
            ui.say("You look again. Nothing new.")
        self.tick(1)
        ui.pause()

    def travel(self):
        loc = self.locations[self.player.location]
        labels = [self.locations[e].name for e in loc.exits] + [b.label for b in loc.blocked] + ["Stay"]
        ui.say()
        ui.say("Where to?")
        choice = ui.menu(labels)
        if choice == len(labels) - 1:
            return
        if choice >= len(loc.exits):
            ui.say_lines([loc.blocked[choice - len(loc.exits)].text])
            ui.pause()
            return
        dest = loc.exits[choice]
        self.player.location = dest
        if dest not in self.player.visited:
            self.player.visited.append(dest)
        self.tick(1)
        self.save()

    def rest(self):
        p = self.player
        loc = self.locations[p.location]
        if not loc.can_rest:
            ui.say_lines(["Not here."])
            ui.pause()
            return
        if p.period < 2 and p.fatigue < 3:
            ui.say_lines(["You are not tired enough to sleep."])
            ui.pause()
            return
        if p.awareness < 10:
            ui.say_lines(["You find a dry place out of the fog and sleep."])
            self.change_fatigue(-3)
        elif p.awareness < 20:
            ui.say_lines(["You find a dry place out of the fog. You sleep badly,",
                          "in pieces, and wake before you are finished."])
            self.change_fatigue(-1 - (1 if p.skills.get("resolve", 0) >= 2 else 0))
        else:
            ui.say_lines(["You lie still and wait for morning.",
                          "You are not sure you slept. You are not sure you didn't."])
            self.change_fatigue(0 if p.skills.get("resolve", 0) >= 3 else 1)
        p.day += 1
        p.period = 0
        self.save()
        ui.pause()

    def system_menu(self):
        ui.say()
        choice = ui.menu(["Save", "Save and quit", "Quit without saving", "Back"])
        if choice == 0:
            self.save()
            ui.say("Saved.")
            ui.pause()
        elif choice == 1:
            self.save()
            raise ui.QuitGame()
        elif choice == 2:
            raise ui.QuitGame()

    # -------------------------------------------------------------- save ----
    def save(self, slot: str = config.SAVE_SLOT):
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(os.path.join(SAVE_DIR, f"{slot}.json"), "w", encoding="utf-8") as f:
            json.dump(self.player.to_dict(), f, indent=2)

    @staticmethod
    def load_player(slot: str = config.SAVE_SLOT):
        path = os.path.join(SAVE_DIR, f"{slot}.json")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return Player.from_dict(json.load(f))

    # ------------------------------------------------------------- visit ----
    def visit(self):
        """Interact with the current location without travelling (graphical front-end).
        Returns when the player chooses Leave."""
        while True:
            self.scene()
            loc = self.locations[self.player.location]
            labels, handlers = [], []
            for nid in loc.npcs:
                npc = self.npcs[nid]
                labels.append(f"Talk to {npc.ref}")
                handlers.append(lambda n=npc: dialog.converse(self, n))
            labels += ["Look around", "Open your journal", "Rest", "Leave"]
            handlers += [self.look, self.show_journal, self.rest, None]
            handler = handlers[ui.menu(labels)]
            if handler is None:
                return
            handler()

    def start_new(self, player: Player):
        """Begin with a created character."""
        self.player = player
        if not player.location:
            player.location = self.c.start_location
        if player.location not in player.visited:
            player.visited.append(player.location)

    # --------------------------------------------------------------- run ----
    def run(self):
        try:
            while True:
                self.scene()
                loc = self.locations[self.player.location]
                labels, handlers = [], []
                for nid in loc.npcs:
                    npc = self.npcs[nid]
                    labels.append(f"Talk to {npc.ref}")
                    handlers.append(lambda n=npc: dialog.converse(self, n))
                for label, fn in (("Look around", self.look),
                                  ("Journal", lambda: journal.show(self)),
                                  ("Travel", self.travel),
                                  ("Rest", self.rest),
                                  ("Menu", self.system_menu)):
                    labels.append(label)
                    handlers.append(fn)
                if self.debug:
                    labels.append("[debug]")
                    handlers.append(self.debug_console)
                handlers[ui.menu(labels)]()
        except ui.QuitGame:
            return

    def debug_console(self):
        p = self.player
        ui.say("debug: awareness N | trust NPC N | topic ID | clue ID | tick N | "
               "flag NAME | goto LOC | state | done")
        while True:
            parts = ui.ask("debug> ").split()
            if not parts or parts[0] == "done":
                return
            cmd, args = parts[0], parts[1:]
            try:
                if cmd == "awareness":
                    p.awareness = int(args[0])
                elif cmd == "trust":
                    p.trust[args[0]] = int(args[1])
                elif cmd == "topic":
                    self.learn_topic(args[0])
                elif cmd == "clue":
                    self.add_clue(args[0])
                elif cmd == "tick":
                    self.tick(int(args[0]))
                elif cmd == "flag":
                    p.flags.add(args[0])
                elif cmd == "goto":
                    p.location = args[0]
                elif cmd == "state":
                    ui.say(json.dumps(p.to_dict(), indent=1))
                else:
                    ui.say("unknown command")
            except (IndexError, KeyError, ValueError) as e:
                ui.say(f"debug error: {e!r}")
