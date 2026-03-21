"""
WiTE2 CSV Schema Constants and Enumerations
===========================================
Defines the core structural constants, column indices, and data enumerations
derived from Gary Grigsby's War in the East 2 (WiTE2) CSV database schema.

This module serves as the 'Single Source of Truth' for data offsets, ensuring
that auditing, scanning, and modification tools remain synchronized with
the game engine's legacy file formats.

Key Data Definitions:
---------------------
* Column Indices: Offsets for _unit.csv, _ob.csv, and _ground.csv fields.
* Nationalities: Mapping of country codes to historical combatants.
* Ground Element Classes: Enumeration of weapon types (AFV, Infantry, etc.).
* Device Categories: Classification of sub-components and hardware.

Note:
-----
Many indices in this module are 0-based to align with Python's list indexing,
representing the exact column position in the raw comma-separated data.
"""
from typing import Final, List

MIN_SQUAD_SLOTS: Final[int] = 0
MAX_SQUAD_SLOTS: Final[int] = 32
MAX_GROUND_MEN: Final[int] = 30
# GC41 is configured to run from 22 Jun 1941 till 2 Aug 1945
# which is 216 turns
MAX_GAME_TURNS: Final[int] = 225
EXCESS_RESOURCE_MULTIPLIER: Final[float] = 5.0

# Map Coordinate Limits
MIN_X: Final[int] = 0
MIN_Y: Final[int] = 0
MAX_X: Final[int] = 378
MAX_Y: Final[int] = 354

GROUND_WPN_PREFIXES: List[str] = ["wpn ", "wpnNum ", "wpnAmmo ",
                                  "wpnRof ", "wpnAcc ", "wpnFace "]

UNIT_SQUAD_PREFIXES: List[str] = ["sqd.u", "sqd.num", "sqd.dis",
                                  "sqd.dam", "sqd.fat", "sqd.fired",
                                  "sqd.exp", "sqd.expAccum"]



