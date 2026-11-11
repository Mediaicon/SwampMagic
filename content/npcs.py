"""NPC dialogue. Lines are checked top to bottom; the FIRST whose When passes wins,
so put the most specific (highest trust / Awareness) first.

Protected mysteries stay unanswered here. Nobody says who burned the church, what
the Original Preacher learned, what the swamp is, or why Ferry Landing's residents
stay. NPCs may believe, claim, accuse, and dodge.
"""
from npc import NPC
from rules import Claim, Do, L, W

# ------------------------------------------------------------------ ferryman --
FERRYMAN = NPC(
    id="ferryman", name="The ferryman", ref="the ferryman",
    intro=(
        L("The ferryman watches the water. He does not look at you.", when=W(min_awareness=10)),
        L("The ferryman watches the water."),
    ),
    topics={
        "ferry_landing": (
            L("“What I’m about to tell you, you didn’t get from me.”",
              "“Nobody comes here on purpose. They come after. After a church. After a family. "
              "After a name.”",
              "“And then they stay.”",
              "“Don’t ask me why. I’m too tired to lie well.”",
              when=W(min_trust=3),
              do=Do(awareness=1, claim=Claim(
                  "ferry_landing_nature", "arrive_after_loss",
                  "The ferryman said people arrive after losing something, and then stay. "
                  "He would not say why."))),
            L("“You still think Ferry Landing is a place.”",
              "“It is a consequence.”",
              when=W(min_awareness=10),
              do=Do(claim=Claim(
                  "ferry_landing_nature", "consequence",
                  "The ferryman described Ferry Landing as a consequence."))),
            L("“Ferry Landing takes anybody nobody else wants.”",
              do=Do(claim=Claim(
                  "ferry_landing_nature", "takes_the_unwanted",
                  "The ferryman said Ferry Landing takes anybody nobody else wants."))),
        ),
        "original_preacher": (
            L("“What I’m about to tell you, I’ve told no one who asked.”",
              "“Everybody wants to know why he left. Nobody asks what he knew when he did.”",
              "“A man can run from a fire. He can’t run from something he learned.”",
              when=W(min_trust=3),
              do=Do(awareness=2, topics=("preacher_knowledge",), claim=Claim(
                  "preacher_reason", "learned_something",
                  "The ferryman suggested the Original Preacher left because of something "
                  "he learned."))),
            L("“Folks ask about him.”",
              "“Funny thing is nobody asks why he left.”",
              when=W(min_trust=1),
              do=Do(claim=Claim(
                  "preacher_reason", "reason_unasked",
                  "The ferryman suggested the Original Preacher left for a reason nobody asks "
                  "about."))),
            L("“Don’t concern yourself with that.”"),
        ),
        "church_fire": (
            L("“The church burned. That much everybody agrees on.”",
              "“Past that, folks have a favorite someone to blame. Never the same someone twice.”",
              do=Do(claim=Claim(
                  "church_fire_cause", "blame_shifts",
                  "The ferryman said people blame someone different for the church fire "
                  "every time."))),
        ),
        "iron_and_fire": (
            L("He studies you.", "“You’ve read about it. Reading’s the cheap part.”",
              when=W(min_skills=(("lore", 2),))),
            L("“Up the road they’ll tell you iron and fire keep you safe.”",
              "“It does. I’ll say that for it.”",
              "“It also costs. Same as everything.”"),
        ),
        "the_fog": (
            L("“Most people stop noticing it after the first year.”",
              "“You noticed it on day one. That’s not a compliment.”",
              when=W(min_awareness=10)),
            L("“Fog’s fog. You stop seeing it.”"),
        ),
        "new_preacher": (
            L("“Folks up the road sleep easy. I’ll give him that.”"),
        ),
        "preacher_knowledge": (
            L("“Don’t.”", "“I mean it kindly.”"),
        ),
    },
    deflect=("He says nothing, and the water fills the silence.",),
    rapport=(
        L("He moves over to make room, without being asked.",
          "He has done this before, for someone else.",
          when=W(min_awareness=15), do=Do(trust=1)),
        L("You sit beside him. Neither of you speaks. It is almost companionable.",
          when=W(min_trust=3)),
        L("You sit on the dock beside him. He says nothing for a long time.",
          "“Most people fill the quiet,” he says at last. “You didn’t.”",
          do=Do(trust=1)),
    ),
    reactions={
        "rusted_iron_cross": (
            L("He looks at the cross for a long moment.",
              "“Somebody put that down on purpose.”",
              "“Or couldn’t carry it any more.”",
              do=Do(trust=1)),
        ),
        "candle_ledger": (L("“Candles. Folks light them for their own reasons.”"),),
        "faded_handbill": (
            L("“That’s been there longer than I have.”",
              "“Nobody takes it down. Nobody reads it.”"),
        ),
    },
    default_reaction=("He glances at it, then back at the water.",),
)

# ---------------------------------------------------------------- storekeeper --
STOREKEEPER = NPC(
    id="storekeeper", name="The storekeeper", ref="the storekeeper", ordinary=True,
    intro=(
        L("The storekeeper looks up, relieved and suspicious in equal parts.",
          when=W(flags=("stopped_asking",))),
        L("The storekeeper studies you a moment longer than he used to.",
          when=W(min_awareness=15)),
        L("The storekeeper studies you carefully."),
    ),
    topics={
        "ferry_landing": (
            L("“Don’t let the ferryman fill your head.”",
              "“Some people need mysteries to survive.”",
              do=Do(claim=Claim(
                  "ferry_landing_nature", "no_hidden_meaning",
                  "The storekeeper believes the ferryman sees meaning everywhere."))),
        ),
        "original_preacher": (
            L("He glances at the door, then at you.",
              "“Come round the counter.”",
              "He opens a ledger and turns it toward you. “Church bought candles by the "
              "case. Every month. Look at the end.”",
              when=W(min_trust=3),
              do=Do(clues=("candle_ledger",))),
            L("“You’ve been asking everyone that.”",
              "“I’d stop, if I were you. I’m not saying why.”",
              when=W(min_awareness=15)),
            L("“The Original Preacher?”",
              "“Most people think he ran.”",
              "“Most people are lazy thinkers.”",
              "“After the fire, anyway. That part nobody argues.”",
              do=Do(topics=("church_fire",), claim=Claim(
                  "preacher_reason", "not_what_people_think",
                  "The storekeeper does not believe the Original Preacher left for the "
                  "reason most people think."))),
        ),
        "church_fire": (
            L("He lowers his voice.",
              "“I sold candles to that church for years.”",
              "“Candles don’t usually burn churches. Not in all the years I sold them.”",
              "“...Forget I said that.”",
              when=W(min_trust=3),
              do=Do(claim=Claim(
                  "church_fire_cause", "doubts_accident",
                  "The storekeeper let slip that he doubts candles burned the church."))),
            L("“Church burned. Candles, dry timber, a bad night.”",
              "“That’s the sensible story.”",
              do=Do(claim=Claim(
                  "church_fire_cause", "accident",
                  "The storekeeper believes the church fire was an accident."))),
        ),
        "iron_and_fire": (
            L("“I sell iron nails and lamp oil.”", "“Make of that what you like.”"),
        ),
        "the_fog": (
            L("“Weather. Don’t give it a name.”", "“Names are bad for business.”"),
        ),
        "new_preacher": (
            L("“His rules work. That’s the trouble with them.”",
              "“His people pay on time, too.”"),
        ),
        "preacher_knowledge": (
            L("“You’re not asking like a customer anymore.”",
              "“I’d like you to be a customer.”",
              when=W(min_awareness=15)),
            L("“That’s not a question you ask in a shop.”"),
        ),
    },
    deflect=("“Can’t help you there.”",),
    rapport=(
        L("You offer to help. He is polite about declining.",
          "Polite is not the same as close.",
          when=W(min_awareness=15)),
        L("You help him restack lamp oil. He pretends not to notice you doing it. "
          "Both of you notice.",
          do=Do(trust=1)),
    ),
    reactions={
        "rusted_iron_cross": (
            L("“Rust. It’s iron. That’s what iron does.”",
              "“...Where did you find it?”",
              "He asked that too quickly."),
        ),
        "candle_ledger": (
            L("“I showed you that once. Don’t make me regret it.”"),
        ),
        "faded_handbill": (
            L("“That old thing. Somebody should take it down.”", "“Nobody does.”"),
        ),
    },
    default_reaction=("“Not something I sell.”",),
)

# ------------------------------------------------- old woman (PROVISIONAL role) --
OLD_WOMAN = NPC(
    id="old_woman", name="The old woman", ref="the old woman",
    intro=(
        L("The old woman is already looking at you when you arrive.", when=W(min_awareness=10)),
        L("The old woman watches you the way people watch weather."),
    ),
    topics={
        "ferry_landing": (
            L("“Everyone here lost something.”",
              "“Don’t ask what. It’s rude, and you’ll get lies.”",
              "“Up the road they say the New Preacher keeps us all safe.”",
              "“Safe is a word with a price on it.”",
              do=Do(topics=("new_preacher",), claim=Claim(
                  "ferry_landing_nature", "arrive_after_loss",
                  "The old woman said everyone in Ferry Landing lost something before arriving."))),
        ),
        "original_preacher": (
            L("“I told you he ran from guilt. I tell everyone that.”",
              "“I tell it because the other answer is worse.”",
              when=W(min_trust=3),
              do=Do(awareness=2, topics=("preacher_knowledge",), claim=Claim(
                  "preacher_reason", "guilt_story_is_cover",
                  "The old woman admitted the guilt story is one she tells because the other "
                  "answer is worse."))),
            L("“Guilty men run. That’s all there is to it.”",
              "“Don’t make it a story.”",
              "“Stories are how things get worse.”",
              do=Do(claim=Claim(
                  "preacher_reason", "left_out_of_guilt",
                  "The old woman is certain the Original Preacher ran because he was guilty."))),
        ),
        "church_fire": (
            L("“Somebody struck a match.”",
              "“Fires like that don’t start themselves.”",
              do=Do(claim=Claim(
                  "church_fire_cause", "deliberate",
                  "The old woman is certain someone set the church fire on purpose."))),
        ),
        "iron_and_fire": (
            L("“It works. Don’t make that face.”",
              "“Everything that works costs something.”"),
        ),
        "the_fog": (
            L("“Some days I think it’s thicker toward the church road.”",
              "“Some days I think I’m old.”",
              when=W(min_awareness=15)),
            L("“It’s fog, child.”"),
        ),
        "new_preacher": (
            L("“Safe.”", "“He keeps them safe. I’ll never say he doesn’t.”"),
        ),
        "preacher_knowledge": (
            L("“Ask me again in a year.”", "“I won’t answer then either.”",
              when=W(min_trust=3)),
            L("“If I knew that, I’d sleep worse than I already do.”"),
        ),
    },
    deflect=("She waves a hand as if clearing smoke.",),
    rapport=(
        L("She says nothing. Eventually she pats the ground beside her.",
          when=W(min_trust=3)),
        L("You sit near her crate. She names three people who pass.",
          "“That one lost a daughter. That one lost a name. That one lost nothing, "
          "which is worse.”",
          do=Do(trust=1)),
    ),
    reactions={
        "rusted_iron_cross": (
            L("“Put it away.”", "“Not because it’s dangerous. Because it’s heavy.”"),
        ),
        "candle_ledger": (
            L("“Whose hand is the last entry in?”",
              "She asks it as though she has asked it before."),
        ),
        "faded_handbill": (
            L("“Oh, that. Don’t read what’s missing. It’s worse than what’s there.”"),
        ),
    },
    default_reaction=("She looks at it a moment too long, then away.",),
)

NPCS = [FERRYMAN, STOREKEEPER, OLD_WOMAN]
