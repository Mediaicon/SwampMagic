from location import Blocked, Location
from rules import Do, L, W

# Names marked PROVISIONAL are placeholders (Design Doc, Appendix A).

START_LOCATION = "ferry_dock"

# Shown in every location when the conditions pass. Costs of Awareness:
# obsession and outsider attention. "Outsider" is deliberately undefined (OQ-3).
GLOBAL_AMBIENT = (
    L("You catch yourself checking the edge of the fog for faces. There are none. "
      "You check again.", when=W(min_awareness=18, period_in=(2, 3))),
)

LOCATIONS = [
    Location(
        "ferry_dock", "Ferry Landing Dock",
        blurb=("The fog hangs low over the water.",
               "An old ferryman sits beside the dock."),
        npcs=("ferryman",),
        exits=("landing_square",),
        ambient=(
            L("The fog always seems thicker near the church road.", when=W(min_awareness=20)),
        ),
        look=(
            L("The dock creaks beneath your feet.",
              "A small settlement can be seen through the fog.",
              do=Do(awareness=3, topics=("the_fog",))),
            L("A handbill is nailed to one of the dock posts, nearly eaten by weather.",
              when=W(lacks_clues=("faded_handbill",)),
              do=Do(clues=("faded_handbill",))),
            L("Of all the rope on the dock, only the line nearest the water is new.",
              when=W(min_skills=(("perception", 2),))),
            L("The ferryman never seems to look directly at you.",
              "You are no longer sure the fog is moving with the wind.",
              when=W(min_awareness=10)),
        ),
    ),
    Location(
        # PROVISIONAL name. Flavor only; no tradition controls Ferry Landing.
        "landing_square", "Landing Square",
        blurb=("Mud, planks, and the habit of not looking at each other.",
               "A horseshoe hangs over one door. A row of notched sticks over another. "
               "A third door has nothing on it at all, and has been painted shut.",
               "An old woman sits on an upturned crate."),
        npcs=("old_woman",),
        exits=("ferry_dock", "general_store", "church_road"),
        look=(
            L("People cross the square without stopping. Nobody takes down what hangs "
              "over anyone else’s door."),
            L("Nobody here looks well rested. Nobody looks surprised by it.",
              when=W(min_awareness=10)),
        ),
    ),
    Location(
        "general_store", "General Store",
        blurb=("Shelves of lamp oil, nails, rope and salt.",
               "Prices are chalked on slates and change more often than the stock."),
        npcs=("storekeeper",),
        exits=("landing_square",),
        look=(
            L("Everything is priced. Very little is explained."),
            L("A stack of candles sits by the till, smaller than you would expect for a "
              "place this dark.", when=W(min_awareness=10)),
        ),
    ),
    Location(
        "church_road", "Church Road",
        blurb=("More path than road. Cypress knees crowd both edges.",
               "The fog is heavier here."),
        exits=("landing_square",),
        ambient=(
            L("It is thicker than it was at the dock. You are certain of it. "
              "You are not certain you should be.", when=W(min_awareness=20)),
        ),
        look=(
            L("Something dark lies in the weeds at the roadside.",
              when=W(lacks_clues=("rusted_iron_cross",)),
              do=Do(clues=("rusted_iron_cross",))),
            L("Boot prints around the cross. Not today’s. Not yesterday’s. A good many people "
              "have stood here and left it where it lay.",
              when=W(has_clues=("rusted_iron_cross",), min_skills=(("perception", 2),))),
            L("Past the cross the road goes on into the fog."),
        ),
        # PROTOTYPE EDGE: content beyond this point is not written yet.
        blocked=(Blocked("Follow the road into the fog",
                         "The road goes on. The fog goes with it. You find you have stopped "
                         "walking, and you are not ready to start again. Not today."),),
        can_rest=False,
    ),
]
