"""All console I/O lives here, so the engine can be tested without a terminal."""
from __future__ import annotations

import os
import textwrap

CLEAR_SCREEN = True
HUD = False        # True when a graphical front-end draws the HUD itself
WIDTH = 76


class QuitGame(Exception):
    """Raised to unwind back to the main menu / exit."""


def clear():
    if CLEAR_SCREEN:
        os.system("cls" if os.name == "nt" else "clear")


def say(text: str = ""):
    print(textwrap.fill(text, WIDTH) if text else "")


def say_lines(lines):
    """Print a block of dialogue / narration, one paragraph per entry."""
    print()
    for line in lines:
        say(line)
        print()


def rule(char: str = "=", n: int = 50):
    print(char * n)


def block(title: str, body: str = ""):
    print()
    rule("-", 40)
    print(f"  {title}")
    if body:
        print(f"    {body}")
    rule("-", 40)
    print()


def ask(prompt: str = "> ") -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        raise QuitGame()


def pause():
    print()
    ask("Press Enter to continue...")


def menu(labels, prompt: str = "> ") -> int:
    """Show a numbered menu, return the chosen 0-based index."""
    for i, label in enumerate(labels, 1):
        print(f"{i}. {label}")
    print()
    while True:
        raw = ask(prompt)
        if raw.isdigit() and 1 <= int(raw) <= len(labels):
            return int(raw) - 1
        say("Invalid choice.")
