# Protected Mystery Registry

This document is the authoritative registry of Swamp Magic's Protected Mysteries.

Charter rule 2: Protected Mysteries may not be resolved.
The Design Authority Document is canonical; this registry records its Protected
Mysteries as they exist in current project materials. It reconciles all prior
references in README.md, code comments, and documentation.

Amendment procedure: a Protected Mystery may only be added, retired, or
re-scoped by Design Authority decision, recorded in DECISIONS.md, then reflected
here. No other document may restate Protected Mystery rules; all other files
should reference this registry.

Status values: Protected (may never be answered), Unassigned (identifier
reserved, no content establishes it).

---

# PM-1

## Identifier
PM-1

## Mystery Name
Who burned the church?

## Boundary Statement
The identity of whoever started the church fire must never be established —
not by confirmation, not by accusation proven true, not by exclusion.

## Why It Is Protected
The fire is Ferry Landing's foundational wound. Every account of the town's
present turns on it, and every major NPC holds a different relationship to it.
Establishing a culprit collapses the living contradiction between accident and
intent into a single fact and ends the investigation the town is built around.

## Allowed Investigation Behavior
- NPCs may believe, claim, accuse, and dodge.
- Blame may shift between tellings ("Never the same someone twice").
- Stances such as accident, deliberate, doubts_accident, and blame_shifts may
  be voiced as opinion or suspicion.
- The player may form beliefs about who burned the church.
- Case assembly on the church fire question may gather evidence and testimony.

## Forbidden Resolution Behavior
- No NPC, clue, case text, or narrator voice may state or unambiguously imply
  who set the fire.
- No content may confirm or definitively exclude any accusation.
- Assembling a case never says which account of the fire is right.

---

# PM-2

## Identifier
PM-2

## Mystery Name
What did the Original Preacher learn?

## Boundary Statement
The specific knowledge the Original Preacher gained before he left must never
be revealed, specified, or made verifiable.

## Why It Is Protected
"Why did the Original Preacher leave?" is the project's first complete
investigation. Its engine is the gap between what the Preacher learned and what
anyone will say about it. Giving content to the knowledge pins every
interpretation to one answer and converts the question into a fetch quest for
a fact.

## Allowed Investigation Behavior
- NPCs may assert that he learned something.
- Awareness-gated lines may imply the learning mattered more than the fire.
- The preacher_knowledge topic exists precisely to be closed: deflection,
  warning, refusal.
- The player may form beliefs about what he learned.

## Forbidden Resolution Behavior
- No content may state what the knowledge was, where it came from, or what
  would verify it.
- No clue may decode or name the discovery.
- No case assembly, however complete, may reveal the learning.

---

# PM-3

## Identifier
PM-3

## Mystery Name
Is the Original Preacher innocent?

## Boundary Statement
The Original Preacher's guilt or innocence must never be established.

## Why It Is Protected
The Old Woman's admitted cover story — that he ran from guilt, told because
"the other answer is worse" — only functions while both answers remain open.
Resolving his innocence or guilt also resolves PM-2 by implication and ends
the town's oldest argument, which is itself a load-bearing piece of the
setting.

## Allowed Investigation Behavior
- NPCs may assert guilt ("Guilty men run") or doubt the common story.
- Different NPCs may weight guilt and innocence differently at different
  trust levels.
- The player may form a belief about his innocence.
- Missable information may lean, in character, in either direction.

## Forbidden Resolution Behavior
- No narrator voice, clue, or case text may confirm or exclude his guilt.
- No high-trust or high-Awareness line may settle the question, however
  kindly or indirectly phrased.

---

# PM-4

## Identifier
PM-4

## Mystery Name
What is the swamp?

## Boundary Statement
The true nature of the swamp must never be defined, explained, or systematized.

## Why It Is Protected
The swamp is the game's atmosphere made geography: the fog that thickens
toward Church Road, the green rim as the Eye opens, the sense that Ferry
Landing "is a consequence." Defining the swamp demystifies the setting's core
and retroactively converts its best moments from dread into exposition.

## Allowed Investigation Behavior
- Implication, metaphor, and partial observation.
- Awareness-gated environmental lines.
- Personal theories from NPCs, clearly held as theories.

## Forbidden Resolution Behavior
- No lore entry, testimony, or clue may state what the swamp is or how it
  works.
- No content may give the swamp a mechanism, an origin, or a rule set.

---

# PM-12

## Identifier
PM-12

## Mystery Name
Why do Ferry Landing's residents stay?

## Boundary Statement
The true reason the residents stay must never be given a single explanation.

## Why It Is Protected
The town's hold on people is its engine of dread: they arrive after loss, and
then they stay, and the strongest voice in town is "too tired to lie well"
about why. A revealed mechanism — a force, a curse, a practical cause —
converts that dread into a problem with a solution.

## Allowed Investigation Behavior
- Partial, personal, contradictory reasons offered by individual residents.
- Characters' own theories about themselves and each other.
- Content that treats the staying itself as the anomaly.

## Forbidden Resolution Behavior
- No single revealed mechanism, force, or explanation that accounts for why
  the residents stay.
- No content that confirms or denies any one resident's reason as the true one.

---

# PM-13

## Identifier
PM-13

## Mystery Name
Is there a ceiling to Awareness? (What happens at "full Awareness"?)

## Boundary Statement
Awareness has no defined ceiling. The Green Eye display topping out at five
pips is a user-interface limit; nothing special happens beyond it. No content
may define "full Awareness" or an Awareness endpoint.

## Why It Is Protected
Awareness replaces sanity and is a burden, not a power progression system. A
defined ceiling would make Awareness a track with a top, a top invites an
endpoint reward, and an endpoint reward converts the game's central cost into
a power fantasy.

## Allowed Investigation Behavior
- Scaling observations, interpretations, and burdens as Awareness rises.
- Continued fatigue and belonging costs at all levels.
- More of the same display (pips), never a new tier of meaning.

## Forbidden Resolution Behavior
- No defined threshold that grants revelations, transformations, answers, or
  an end state.
- No content that names, describes, or implies what maximum Awareness is or
  does.

---

# Unassigned Identifiers

PM-5 through PM-11 appear in no project material. They are reserved and
unassigned. They must not be used for new content without a Design Authority
decision recorded in DECISIONS.md.

---

# Reconciled References

- README.md, "Design Authority compliance (v1.0)" — listed PM-1, PM-2, PM-3,
  PM-4, PM-12, PM-13. All six are carried into this registry unchanged.
- content/npcs.py docstring — restated PM-1, PM-2, PM-4, PM-12 without numbers.
  This registry supersedes that restatement; the docstring should be updated
  to reference this file.
- content/cases.py comment — cited PM-1, PM-2, PM-3. Carried in unchanged.
- docs/PERSONAL_MYSTERIES.md and docs/CANON.md — cite PM boundaries
  consistent with this registry.
