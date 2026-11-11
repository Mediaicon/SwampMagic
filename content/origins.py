"""PROVISIONAL origin content. Names, contacts and mysteries are placeholders.

Each personal mystery follows Design Doc ch. 10: it starts small and personal and
may later connect to larger truths. None of them says what Ferry Landing, the
swamp, or the church fire really are. They are not answered here.
"""
from origin import Origin

ORIGINS = [
    Origin(
        "investigator", "Investigator", "You find people for a living.",
        "You trust paper first and people second, and you are usually right about both.",
        {"perception": 2, "rapport": 1, "lore": 0, "resolve": 1},
        "An old client who still answers your letters.",
        "The Missing Client",
        "A client hired you to find someone last seen heading for Ferry Landing.",
    ),
    Origin(
        "federal_agent", "Federal Agent", "You were sent. You were not told everything.",
        "You were taught that every institution has a file, and every file has a page missing.",
        {"perception": 1, "rapport": 1, "lore": 0, "resolve": 2},
        "A supervisor who stopped returning calls.",
        "The Misdirected Payments",
        "A routine audit traced payments to Ferry Landing. Your superiors told you to close the file.",
        start_topics=("church_fire",),
    ),
    Origin(
        "deputy", "Deputy", "You wear a badge that stops mattering at the water.",
        "You know everyone’s name and what they would rather you forgot.",
        {"perception": 1, "rapport": 2, "lore": 0, "resolve": 1},
        "A retired sheriff who knows where things were buried, in the usual sense.",
        "The Unclaimed Report",
        "A missing-persons report sat in your desk for three years with a Ferry Landing postmark. "
        "Nobody wanted it.",
        start_topics=("new_preacher",),
    ),
    Origin(
        "smuggler", "Smuggler", "You know the back way into every place.",
        "You read people by what they will not ask you to carry.",
        {"perception": 1, "rapport": 2, "lore": 0, "resolve": 1},
        "A broker who owes you one favor and has said so out loud.",
        "The Shipment That Wasn’t",
        "A shipment you were paid to deliver never arrived. The buyer swears it did.",
    ),
    Origin(
        "swamp_native", "Swamp Native", "You grew up on this water.",
        "You know how things are said here. You also know how they are not said.",
        {"perception": 2, "rapport": 0, "lore": 1, "resolve": 1},
        "A cousin who left, and sometimes writes.",
        "The Letter That Stopped",
        "Someone in your family came to Ferry Landing and stopped writing.",
        start_topics=("the_fog",),
    ),
    Origin(
        "gang_operator", "Gang Operator", "You collect what is owed.",
        "You respect anyone who stays calm while owing something.",
        {"perception": 1, "rapport": 1, "lore": 0, "resolve": 2},
        "A lieutenant who would follow you anywhere and is not sure why.",
        "The Collection",
        "Someone from your crew came here to collect a debt and never came back.",
    ),
    Origin(
        "occult_researcher", "Occult Researcher", "You read what other people avoid.",
        "You have always believed understanding was the safe thing to want.",
        {"perception": 1, "rapport": 0, "lore": 3, "resolve": 0},
        "A librarian who copies things for you and does not ask what for.",
        "The Crossed-Out Date",
        "Your notes point here, to a name and a date that someone crossed out.",
        start_topics=("iron_and_fire",),
    ),
]
