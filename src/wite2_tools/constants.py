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
from enum import IntEnum
from typing import Final, List

MIN_SQUAD_SLOTS: Final[int] = 0
MAX_SQUAD_SLOTS: Final[int] = 32
MAX_GROUND_MEN: Final[int] = 30
MAX_GND_WPN_SLOTS: Final[int] = 10
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


class GrdElementType(IntEnum):
    """
    Mapping for the 'type' column in WiTE2's _ground.csv.
    """
    RIFLE_SQUAD = 1
    INFANTRY_AT = 2
    CAVALRY_SQUAD = 3
    MACHINEGUN = 4
    MORTAR = 5
    AT_GUN = 6
    MECH_INF_SQUAD = 7
    MD_FLAK = 8
    ARTILLERY = 9
    NAVAL_GUN = 10
    ARMOURED_CAR = 11
    LT_TANK = 12
    MD_TANK = 13
    HVY_TANK = 14
    CS_TANK = 15
    MOTOR_INF_SQUAD = 16
    FLAME_TANK = 17
    ASSAULT_GUN = 18
    MECH_ENGR_SQUAD = 19
    ENGINEER_SQUAD = 20
    SP_ARTILLERY = 21
    SP_FLAK = 22
    HT_AT_GUN = 23
    HT_MG_MOR = 24
    HT_CS_MORTAR = 25
    SPECIAL_FORCES = 26
    MARINE_COMMANDO = 27
    AIRBORNE_ENG = 28
    SP_AAMG = 29
    AAMG = 30
    ROCKET = 31
    HVY_ARTILLERY = 32
    LT_FLAK = 33
    HVY_FLAK = 34
    DD_TANK = 35
    MSW_TANK = 36  # Minesweeper Tank
    ENGINEER_TANK = 37
    AIRBORNE_SQUAD = 38
    SP_INF_GUN = 39
    SMG_SQUAD = 40
    BARGE = 41
    AIR_LANDING_SECTION = 42
    HVY_AT_GUN = 43
    LT_AT_GUN = 44
    HVY_INFANTRY_GUN = 45
    LT_ARTILLERY = 46
    AIRBORNE_TANK = 47
    RECON_JEEP = 48
    MOTORCYCLE_SQUAD = 49
    SKI_SQUAD = 50
    SECURITY_SQUAD = 51
    PARTISAN_SQUAD = 52
    NAVAL_RIFLE_SQUAD = 53
    LABOUR_SQUAD = 54
    HQ_TROOPS = 55
    AMMO_TRUCK = 56
    LT_ARMOUR = 57
    HVY_MORTAR = 58
    SP_AT_GUN = 59
    TANK_DESTROYER = 60
    HVY_TANK_DESTROYER = 61
    INFANTRY_GUN = 62
    INFANTRY_TANK = 63
    CAVALRY_TANK = 64
    HVY_CAVALRY_TANK = 65
    HVY_ASSAULT_TANK = 66
    LT_TANK_DESTROYER = 67
    CS_CAVALRY_TANK = 68
    CS_INFANTRY_TANK = 69
    LT_ARMOURED_CAR = 70
    NAVAL_ARTILLERY = 71
    RECON_TANK = 72
    RECON_HALFTRACK = 73
    FLAMETHROWER = 74
    ASSAULT_TANK = 75
    FOREIGN_MD_TANK = 76
    FOREIGN_LT_TANK = 77
    FOREIGN_FLAME_TANK = 78
    FOREIGN_LT_TD = 79
    FOREIGN_TANK_DESTROYER = 80
    FOREIGN_ASSAULT_GUN = 81
    FOREIGN_SP_ARTILLERY = 82
    FOREIGN_ARMOURED_CAR = 83
    FOREIGN_SP_ROCKET = 84  # Unarmored?
    HT_MORTAR = 85  # New to WiTE2
    SUPER_HVY_ARTILLERY = 86  # New to WiTE2
    CHASSIS = 87  # New to WiTE2
    MECH_RECON = 88  # New to WiTE2
    LT_INFANTRY = 89  # New to WiTE2
    HVY_SP_ARTILLERY = 90  # New to WiTE2
    CS_ARMORED_CAR = 91  # New to WiTE2
    HVY_ARMORED_CAR = 92  # New to WiTE2
    FLAME_APC = 93  # New to WiTE2
    TROOP_SHIP = 94
    CARGO_SHIP = 95
    VEHICLE_REPAIR = 96
    SUPPLY_DUMP = 97
    FUEL_DUMP = 98
    SUPPORT = 99
    AIR_SUPPORT = 100  # New to WiTE2
    MANPOWER = 101
    HVY_INDUSTRY = 102
    OIL = 103
    FUEL = 104
    SYNTHETIC_FUEL = 105
    RESOURCE = 106
    ARTILLERY_PRODUCTION = 107
    VEHICLE = 108
    RAIL_YARD = 109
    PORT = 110
    V_WEAPONS_FACTORY = 111
    V_WEAPONS_LAUNCHER = 112
    U_BOAT_FACTORY = 113
    U_BOAT_PEN = 114
    ASSAULT_SQUAD = 115  # New to WiTE2
    STATIC_AT_GUN = 116  # New to WiTE2
    MECH_CAV = 117  # New to WiTE2
    MG_SECTION = 118  # Local Modification

    @property
    def is_armored_infantry_element(self) -> bool:
        armored_infantry_types = {
            GrdElementType.MECH_INF_SQUAD
        }
        return self in armored_infantry_types

    @property
    def is_light_tank_element(self) -> bool:
        _types = {
            GrdElementType.LT_TANK,
            GrdElementType.FOREIGN_LT_TANK,
            GrdElementType.RECON_TANK
        }
        return self in _types

    @property
    def is_medium_tank_element(self) -> bool:
        _types = {
            GrdElementType.MD_TANK,
            GrdElementType.FOREIGN_MD_TANK,
            GrdElementType.FLAME_TANK,
            GrdElementType.INFANTRY_TANK,
            GrdElementType.DD_TANK
        }
        return self in _types

    @property
    def is_heavy_tank_element(self) -> bool:
        _types = {
            GrdElementType.HVY_TANK,
            GrdElementType.HVY_CAVALRY_TANK,
            GrdElementType.HVY_ASSAULT_TANK,
            GrdElementType.CS_TANK,
            GrdElementType.CS_INFANTRY_TANK
        }
        return self in _types

    @property
    def is_combat_element(self) -> bool:
        """
        Determines if this GroundElementType is a combat unit element.
        Returns False for static infrastructure, factories, and resource pools.
        """
        non_combat_types = {
            GrdElementType.NAVAL_GUN,
            GrdElementType.NAVAL_ARTILLERY,
            GrdElementType.CHASSIS,
            GrdElementType.TROOP_SHIP,      # 94
            GrdElementType.CARGO_SHIP,      # 95
            GrdElementType.VEHICLE_REPAIR,  # 96
            GrdElementType.SUPPLY_DUMP,     # 97
            GrdElementType.FUEL_DUMP,       # 98
            GrdElementType.SUPPORT,         # 99
            GrdElementType.AIR_SUPPORT,     # 100
            GrdElementType.MANPOWER,              # 101
            GrdElementType.HVY_INDUSTRY,          # 102
            GrdElementType.OIL,                   # 103
            GrdElementType.FUEL,                  # 104
            GrdElementType.SYNTHETIC_FUEL,        # 105
            GrdElementType.RESOURCE,              # 106
            GrdElementType.ARTILLERY_PRODUCTION,  # 107
            GrdElementType.VEHICLE,               # 108
            GrdElementType.RAIL_YARD,             # 109
            GrdElementType.PORT,                  # 110
            GrdElementType.V_WEAPONS_FACTORY,     # 111
            GrdElementType.V_WEAPONS_LAUNCHER,    # 112
            GrdElementType.U_BOAT_FACTORY,        # 113
            GrdElementType.U_BOAT_PEN             # 114
        }

        return self not in non_combat_types


# pylint: disable=invalid-name
class DeviceType(IntEnum):
    """
    Mapping for the 'type' column in WiTE2's _device.csv.
    """
    AIRCRAFT_CANNON = 0
    MAN_WEAPON = 1
    SQUAD_WEAPON = 2
    HVY_SQUAD_WEAPON = 3
    AA_WEAPON = 4
    LT_GUN = 5
    MD_GUN = 6
    HVY_GUN = 7
    FLAME = 8
    AA_ROCKET = 9
    NAVAL_GUN = 10
    AIR_TO_AIR_ROCKET = 11
    INCENDIARY_BOMB = 12
    GP_BOMB_ROCKET = 13
    FACTORY = 14
    DROP_TANK = 15
    RADAR_DETECTOR = 16
    RADAR_JAMMER = 17
    AIR_NAVIGATION = 18
    AIR_RADAR = 19
    GROUND_RADAR = 20
    ELINT = 21
    BALLOON = 22
    FLAK = 23
    TORPEDO = 24
    DP_GUN = 25
    ASW = 26
    MINE = 27
    CAMERA = 28
    NAVAL_RADAR = 29

    @classmethod
    def get_description(cls, value: int) -> str:
        """Returns the original descriptive string for the type ID."""
        descriptions = {
            0: "Aircraft cannon", 1: "Man weapon", 2: "Squad weapon",
            3: "Hvy squad weapon", 4: "AA weapon", 5: "Lt gun",
            6: "Md gun", 7: "Hvy gun", 8: "Flame", 9: "AA Rocket",
            10: "Naval gun", 11: "Air-to-air rocket", 12: "Incendiary bomb",
            13: "GP bomb/rocket", 14: "Factory", 15: "Drop tank",
            16: "RADAR detector", 17: "RADAR jammer", 18: "Air navigation",
            19: "Air RADAR", 20: "Ground RADAR", 21: "ELINT",
            22: "Balloon", 23: "Flak", 24: "Torpedo", 25: "DP Gun",
            26: "ASW", 27: "Mine", 28: "Camera", 29: "Naval RADAR"
        }
        return descriptions.get(value, "Unknown")



# pylint: disable=invalid-name
class AircraftType(IntEnum):
    """
    Mapping for the 'type' column in _aircraft.csv and
    'airType' in _airgroup.csv.
    """
    FIGHTER = 0
    FIGHTER_BOMBER = 1
    NIGHT_FIGHTER = 2
    TACTICAL_BOMBER = 3
    LEVEL_BOMBER = 4
    RECON = 5
    JET_FIGHTER = 6
    EW = 7
    TRANSPORT = 8
    PATROL = 9
    FLOAT_PLANE = 10
    FLOAT_FIGHTER = 11
    TORPEDO_BOMBER = 12
    AIR_FRAME = 13  # New for WiTE2

