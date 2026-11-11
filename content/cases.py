from investigation import Case, Question

QUESTIONS = [
    Question("ferry_landing_nature", "What is Ferry Landing?",
             conflicts=(("consequence", "no_hidden_meaning"),
                        ("arrive_after_loss", "no_hidden_meaning"))),
    Question("preacher_reason", "Why did the Original Preacher leave?",
             conflicts=(("left_out_of_guilt", "not_what_people_think"),
                        ("left_out_of_guilt", "learned_something"),
                        ("left_out_of_guilt", "guilt_story_is_cover"))),
    Question("church_fire_cause", "What started the church fire?",
             conflicts=(("accident", "deliberate"),
                        ("accident", "doubts_accident"))),
]

# NOTE: assembling a case never says which account is right. The Design Doc
# protects PM-1 (who burned the church), PM-2 (what the preacher discovered) and
# PM-3 (is the Original Preacher innocent).
CASES = [
    Case(
        "preacher_departure", "preacher_reason", "Why did the Original Preacher leave?",
        min_sources=2, min_physical=1,
        assembled=(
            "You have enough now to see the shape of it: what people say, what they "
            "will not say, and what was left behind.",
            "It does not add up to one story.",
            "You could stop here.",
        ),
    ),
]
