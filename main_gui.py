"""SWAMP MAGIC - graphical front-end (pygame).

    pip install pygame
    python main_gui.py

The console version (python main.py) still works and shares the same engine.
"""
import sys

try:
    import pygame  # noqa: F401
except ImportError:
    sys.exit("This front-end needs pygame:  pip install pygame")

import content
from gfx.app import main

if __name__ == "__main__":
    problems = content.validate(content.load())
    if problems:
        print("Content problems:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    sys.exit(main(sys.argv[1:]))
