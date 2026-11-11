"""Tunable numbers and switches. Nothing in this file is lore."""

# --- Display -----------------------------------------------------------------
SHOW_AWARENESS_NUMBER = True    # False = Green Eye only (closer to the design doc)
SHOW_CASE_CHECKLIST = True      # prototype scaffolding; consider removing later

# --- Time --------------------------------------------------------------------
PERIODS = ("Morning", "Afternoon", "Evening", "Night")
NIGHT = 3                       # index into PERIODS

# --- Green Eye ---------------------------------------------------------------
# One pip opens per threshold. This is a *display* limit only. It is NOT a
# statement about what the highest Awareness means (Design Doc PM-13).
EYE_THRESHOLDS = (5, 10, 20, 30, 45)
EYE_OPEN, EYE_SHUT = "o", "-"

# --- Fatigue (the "exhaustion" cost of Awareness) -----------------------------
FATIGUE_MAX = 10
FATIGUE_LABELS = ((0, "Rested"), (3, "Tired"), (6, "Worn"), (9, "Hollow"))
WORN_AT = 6                     # at/after this, everyone trusts you a little less

# --- Belonging (the *greatest* cost of Awareness, Design Doc ch. 8) ------------
# "Ordinary" NPCs lose effective trust in you as Awareness rises, and again for
# every investigation you assemble.
BELONGING_STEP = 10

# --- Awareness rewards ---------------------------------------------------------
GAIN_CONTRADICTION = 1
GAIN_CASE_ASSEMBLED = 3

# --- Misc ------------------------------------------------------------------
TRUST_MAX = 10
SAVE_SLOT = "autosave"
