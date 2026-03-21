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
from typing import Final

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

GROUND_WPN_PREFIXES: list[str] = ["wpn ", "wpnNum ", "wpnAmmo ",
                                  "wpnRof ", "wpnAcc ", "wpnFace "]

UNIT_SQUAD_PREFIXES: list[str] = ["sqd.u", "sqd.num", "sqd.dis",
                                  "sqd.dam", "sqd.fat", "sqd.fired",
                                  "sqd.exp", "sqd.expAccum"]
GND_ELEMENT_TYPE_DESCRIPTIONS:Final[tuple[str, ...]] = (
        "None",                 # 0
        "Rifle Squad",          # 1
        "Inf-AntiTank",         # 2
        "Cavalry Squad",        # 3
        "Machinegun",           # 4
        "Mortar",               # 5
        "AntiTank Gun",         # 6
        "Mech-Inf Squad",       # 7
        "Md Flak",              # 8
        "Artillery",            # 9
        "Naval Gun",            # 10
        "Armoured Car",         # 11
        "Lt Tank",              # 12
        "Md Tank",              # 13
        "Hvy Tank",             # 14
        "CS Tank",              # 15
        "Motor-Inf Squad",      # 16
        "Flame Tank",           # 17
        "Assault Gun",          # 18
        "Mech-Engr Squad",      # 19
        "Engineer Squad",       # 20
        "SP Artillery",         # 21
        "SP Flak",              # 22
        "HT AT-Gun",            # 23
        "Mech-MG Section",      # 24
        "HT CS-Mortar",         # 25
        "Special Forces",       # 26
        "Marine Commando",      # 27
        "Marine Engineer",      # 28
        "SP AAMG",              # 29
        "AAMG",                 # 30
        "Rocket",               # 31
        "Hvy Artillery",        # 32
        "Lt Flak",              # 33
        "Hvy Flak",             # 34
        "Amphibious Tank",      # 35
        "MSW Tank",             # 36
        "Engineer Tank",        # 37
        "Airborne Squad",       # 38
        "SP Inf-Gun",           # 39
        "SMG Squad",            # 40
        "Carrier-Inf Squad",    # 41
        "Air Landing Section",  # 42
        "Hvy AT Gun",           # 43
        "Lt AT Gun",            # 44
        "Hvy Infantry Gun",     # 45
        "Lt Artillery",         # 46
        "Airborne Tank",        # 47
        "Recon Jeep",           # 48
        "Motorcycle Squad",     # 49
        "Ski Squad",            # 50
        "Security Squad",       # 51
        "Partisan Squad",       # 52
        "Naval Rifle Squad",    # 53
        "Labour Squad",         # 54
        "Md Field Gun",         # 55
        "SP Rocket Launcher",   # 56
        "Lt Armour",            # 57
        "Hvy Mortar",           # 58
        "SP AntiTank Gun",      # 59
        "Tank Destroyer",       # 60
        "Hvy Tank Destroyer",   # 61
        "Infantry Gun",         # 62
        "Infantry Tank",        # 63
        "Cavalry Tank",         # 64
        "Hvy Cavalry Tank",     # 65
        "Hvy Assault Tank",     # 66
        "Lt Tank Destroyer",    # 67
        "CS Cavalry Tank",      # 68
        "CS Infantry Tank",     # 69
        "Lt Armoured Car",      # 70
        "Naval Artillery",      # 71
        "Recon Tank",           # 72
        "Recon Halftrack",      # 73
        "Flamethrower",         # 74
        "Assault Tank",         # 75
        "Foreign Md Tank",      # 76
        "Foreign Lt Tank",      # 77
        "Foreign Flame Tank",   # 78
        "Foreign Lt TD",        # 79
        "Foreign Tank Destroyer", # 80
        "Foreign Assault Gun",  # 81
        "Foreign SP Artillery", # 82
        "Foreign Armoured Car", # 83
        "Unarmored SP Rocket",  # 84
        "HT Mortar",            # 85
        "Super Hvy Artillery",  # 86
        "Chassis",              # 87
        "Mech-Recon",           # 88
        "Lt Infantry",          # 89
        "Hvy SP Artillery",     # 90
        "CS Armored Car",       # 91
        "Hvy Armored Car",      # 92
        "Flame APC",            # 93
        "Troop Ship",           # 94
        "Cargo Ship",           # 95
        "Vehicle Repair",       # 96
        "Supply Dump",          # 97
        "Fuel Dump",            # 98
        "Support",              # 99
        "Air Support",          # 100
        "Manpower",             # 101
        "Hvy Industry",         # 102
        "Oil",                  # 103
        "Fuel",                 # 104
        "Synthetic Fuel",       # 105
        "Resource",             # 106
        "Artillery",            # 107
        "Vehicle",              # 108
        "Railyard",             # 109
        "Port",                 # 110
        "V-Weapons Factory",    # 111
        "V-Weapons Launcher",   # 112
        "U-Boat Factory",       # 113
        "U-Boat Pen",           # 114
        "Assault Squad",        # 115
        "Static AntiTank Gun",  # 116
        "Mech-Cavalry",         # 117
        "MG Section"            # 118
    )



