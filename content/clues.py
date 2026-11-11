from clues import Clue
from rules import Do, W

CLUES = [
    Clue(
        "faded_handbill", "Faded Handbill", "document",
        "Nailed to a dock post and nearly eaten by weather. Most of the ink is gone. "
        "What remains is a name, the Original Preacher, and a smear where a date used to be.",
        do=Do(topics=("original_preacher",), awareness=1),
    ),
    Clue(
        "rusted_iron_cross", "Rusted Iron Cross", "physical",
        "A small iron cross lying in the weeds beside the road, rusted through at the joint. "
        "The rust is old. It was not left here recently. Whether it was placed or dropped, "
        "the iron will not say.",
        details=(
            (W(min_awareness=12),
             "Beside it, a shallow groove in the dirt, the same shape. Another cross stood here "
             "once. Someone took that one and left this one."),
            (W(min_skills=(("perception", 3),)),
             "The break at the joint is clean, not ragged. Rust alone does not do that."),
            (W(min_skills=(("lore", 2),)),
             "The joint is hammered, not cast. Whoever made this meant it to outlast the "
             "people who set it here."),
        ),
        bears_on=("preacher_reason",),
        do=Do(topics=("iron_and_fire",), awareness=1),
    ),
    Clue(
        "candle_ledger", "The Church Candle Ledger", "document",
        "Page after page of candle sales to the church, by the case, every month. Then the "
        "entries stop being regular. The last one is not in the storekeeper’s handwriting.",
        bears_on=("preacher_reason", "church_fire_cause"),
        do=Do(awareness=1),
    ),
]
