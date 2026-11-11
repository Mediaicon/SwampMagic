"""SWAMP MAGIC - prototype entry point.

    python main.py             play
    python main.py --debug     adds a debug console to the location menu
    python main.py --no-clear  don't clear the screen (useful for logs / IDE consoles)
    python main.py --check     validate content and exit
"""
import sys

import content
import ui
from game import Game


def main(argv):
    if "--no-clear" in argv:
        ui.CLEAR_SCREEN = False
    debug = "--debug" in argv

    c = content.load()
    problems = content.validate(c)
    if problems:
        print("Content problems:")
        for p in problems:
            print("  -", p)
        return 1
    if "--check" in argv:
        print("Content OK.")
        return 0

    try:
        while True:
            ui.clear()
            ui.rule("=")
            ui.say("SWAMP MAGIC")
            ui.rule("=")
            ui.say()
            saved = Game.load_player()
            labels = ["New game"] + (["Continue"] if saved else []) + ["Quit"]
            choice = labels[ui.menu(labels)]
            if choice == "Quit":
                return 0
            player = saved if choice == "Continue" else None
            Game(c, player=player, debug=debug).run()
    except ui.QuitGame:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
