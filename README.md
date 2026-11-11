# Swamp Magic (prototype)

Python 3.9+, standard library only.

    pip install -r requirements.txt     (pygame, only for the graphical version)
    python main_gui.py          graphical version: character creator, walkable map, journal
    python main.py              console version (same engine, no pygame needed)
    python main.py --debug      adds a [debug] console (set awareness/trust, grant clues...)
    python main.py --no-clear   don't clear the screen (IDE consoles, logs)
    python main.py --check      validate content and exit
    python -m unittest discover -s tests

## Graphical front-end (pygame)

Controls: arrows / WASD walk, **E** interact, **J** journal, **C** character, **M** map and fast
travel, **Esc** menu. In dialogue: click a choice or press its number; wheel / PgUp / PgDn scroll.

* **Character creator** (`gfx/creator.py`): name, one of the seven canon Origins, then 3 skill
  points (max rank 4). Rules are pure logic in `character.py`.
* **Overworld** (`gfx/overworld.py`, `gfx/world.py`): a 40x30 tile map generated in code (no art
  files). Stepping into a place's zone travels there (one time period per stop) and opens the same
  location menu as the console game. Fast travel from the map screen costs one period per stop.
  The map's geography mirrors the location graph: the only way north is through Landing Square.
* **Journal** (`gfx/journal_view.py`): parchment tabs. Contradictions appear as red thread between
  note cards. Evidence cards show details your Awareness/skills unlock.
* **Character sheet** (`gfx/sheet.py`): portrait, skills, Green Eye, condition, "standing" with
  people (words, not numbers), and your own question.
* **How it plugs in:** `gfx/backend.py` swaps the engine's `ui.say/menu/pause/...` for an
  on-screen text panel, so dialogue, journal and game logic are unchanged and shared with the console.

Atmosphere is state-driven: time-of-day tint, fog that thickens toward Church Road once Awareness
is high (the visual twin of the dock's hidden observation), and a faint green rim as the Eye opens.
None of it is labelled.

## Layout

| File | Role |
|---|---|
| `rules.py` | `When` (condition), `Do` (effect), `Claim`, `Line`, `L()` shorthand. The only language content uses. |
| `game.py` | Engine: trust, Awareness, fatigue, time, effects, contradiction detection, location loop, save/load |
| `dialog.py` | Conversation engine: topics, show-evidence, spend-time |
| `journal.py` | Journal rendering + "settle on a belief" |
| `investigation.py` | `Question` (with declared conflicting stances), `Case`, evidence status |
| `awareness.py` | Green Eye + fatigue labels |
| `npc.py` `location.py` `clues.py` `topics.py` `player.py` | Data classes |
| `content/` | **All authored material.** topics, npcs, locations, clues, cases |
| `config.py` | Every tunable number |
| `ui.py` | All console I/O (swap this to change front-ends) |
| `origin.py`, `character.py`, `content/origins.py` | Origins, skills, character-creation rules |
| `gfx/` | pygame front-end: `app`, `creator`, `overworld`, `world`, `journal_view`, `sheet`, `backend`, `sprites`, `theme` |
| `main_gui.py` | Graphical entry point |

## Adding content (no engine changes)

* **New topic:** add a `Topic` in `content/topics.py`; reveal it with `Do(topics=("id",))` from any Line or clue.
* **New NPC:** add an `NPC` in `content/npcs.py`, list its id in a `Location.npcs`. Lines are checked top to bottom, first `When` that passes wins: put the most specific first.
* **New contradiction:** give two NPCs a `Claim` with the same `question` and declare the clashing stances in `Question.conflicts`.
* **New investigation:** add a `Question` + `Case` in `content/cases.py`, tag clues with `bears_on`.
* Run `python main.py --check` after editing; it catches typo'd ids.

## Mapping to Copilot's milestones

1. Investigation engine: topics, topic discovery ("NEW TOPIC DISCOVERED"), contradiction tracking
2. World: `Location` + travel (graph; Church Road is reachable only via Landing Square)
3. Investigation: clues/evidence, first Case "Why did the Original Preacher leave?"
4. Awareness: hidden checks, Green Eye (`(oo---)` at 15, never explained)
5. Trust: per-NPC trust, locked information, "Spend time" rapport (once per day)

Extras: time of day + fatigue, belonging cost, save/load, content validator, tests.

## Origins and skills (prototype layer)

Origins come from Design Doc ch. 9 (backgrounds, not classes). Their taglines, contacts and
personal mysteries are **provisional**. Skills are *not* in the Design Doc:

| Skill | Effect |
|---|---|
| Perception | Unlocks extra mundane observation lines and clue details |
| Rapport | +1 effective trust with everyone per 2 ranks |
| Lore | Unlocks recognition lines and clue details |
| Resolve | Softens the fatigue costs of sleeplessness |

None can answer a Protected Mystery, and none replaces Awareness. Origins give no Awareness and
lock nothing out. Change or remove skills freely; they live in `origin.py` plus `When(min_skills=...)`.

## Design Authority compliance (v1.0)

* **Awareness is a burden, not a power.** Benefits: hidden observation lines, clue details.
  Costs: fatigue/poor sleep, and *belonging*: "ordinary" NPCs lose effective trust by 1 per 10
  Awareness and 1 per assembled case (can re-lock information you already had access to).
* **Protected mysteries are never answered.** No NPC says who burned the church (PM-1), what the
  Preacher learned (PM-2), whether he is innocent (PM-3), what the swamp is (PM-4), or why Ferry
  Landing's residents stay (PM-12). Assembling a case never says which account is right.
* **Awareness has no defined ceiling.** The Green Eye display tops out at 5 pips as a UI limit;
  nothing special happens beyond it (PM-13). Don't add content that defines "full Awareness".
* **Ferry Landing residents are tired, not enlightened.** The ferryman has the strongest "I know
  more than I say" lines; the old woman admits her version of the story is cover.
* **Provisional names:** `Landing Square`, the old woman, the ferryman, the storekeeper.
