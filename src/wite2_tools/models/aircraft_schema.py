"""
_aircraft.csv Mapping Reference:
| Constant       | CSV Header | Index | Notes                                 |
|----------------|------------|-------|---------------------------------------|
| ID             | id         | 0     | Unique Identifier                     |
| NAME           | name       | 1     | Display Name                          |
| MAX_ALT        | maxAlt     | 2     | Maximum Altitude                      |
| NAT            | nat        | 3     | Nationality Code                      |
| MAX_SPEED      | maxSpeed   | 5     | Maximum Speed                         |
| TYPE           | type       | 19    | Aircraft Type Category                |

Note: The Aircraft file contains exactly 322 columns (0-321) covering base
properties, built-in weapon slots (0-9), and 5 external weapon sets
(Loadouts: ws0 through ws4).
"""
from enum import IntEnum
from typing import Any, Final


class AcColumn(IntEnum):
    """
    Aircraft Column indices for WiTE2's _aircraft.csv file (322 Columns).
    """
    # --- Base Properties ---
    ID = 0
    NAME = 1
    MAX_ALT = 2
    NAT = 3
    SYM = 4
    MAX_SPEED = 5

    # The optimum altitude to achieve Max Speed
    MAX_SPEED_ALT = 6

    # Max speed at sea level
    ZERO_ALT_SPEED = 7

    # Max speed at highest altitude
    MAX_ALT_SPEED = 8

    # Cruise Speed
    CRU_SPEED = 9

    # Climb rate in terms of feet per minute
    CLIMB = 10

    # Maximum load in pounds
    MAX_LOAD = 11

    # Endurance in minutes
    ENDURANCE = 12
    RANGE = 13
    YEAR = 14
    MVR = 15
    ARMOR = 16

    # Aircraft damage points are measured against the aircraft
    # durability rating to determine if it is destroyed or just damaged
    DURAB = 17

    MONTH = 18

    # Mapped to AirCraftType
    TYPE = 19

    BLANK = 20
    UPGRADE = 21
    CREW = 22
    SORTIE_AMMO = 23
    SORTIE_FUEL = 24
    BUILD_COST = 25
    POOL = 26

    # Number of frames that are converted each turn
    BUILD_LIMIT = 27
    MAX_IMPORT = 28
    IMPORT_FROM = 29
    LAST_YEAR = 30
    LAST_MONTH = 31

    # Reliability rating ranges from "really good" (lower numbers) to
    # "really bad" (higher numbers). Checked during missions.
    RELIB = 32

    PHOTO = 33
    EXP_RATE = 34
    ENGINE_NUM = 35
    AIR_PROFILE = 36

    # --- Base Weapons ---
    WPN_0, WPN_1, WPN_2, WPN_3, WPN_4 = 37, 38, 39, 40, 41
    WPN_5, WPN_6, WPN_7, WPN_8, WPN_9 = 42, 43, 44, 45, 46

    WPN_NUM_0, WPN_NUM_1, WPN_NUM_2, WPN_NUM_3, WPN_NUM_4 = 47, 48, 49, 50, 51
    WPN_NUM_5, WPN_NUM_6, WPN_NUM_7, WPN_NUM_8, WPN_NUM_9 = 52, 53, 54, 55, 56

    WPN_FACE_0, WPN_FACE_1, WPN_FACE_2, WPN_FACE_3 = 57, 58, 59, 60
    WPN_FACE_4, WPN_FACE_5, WPN_FACE_6, WPN_FACE_7 = 61, 62, 63, 64
    WPN_FACE_8, WPN_FACE_9 = 65, 66

    # --- Weapon Set 0 ---
    WS0_WPN_0, WS0_WPN_NUM_0, WS0_WPN_FACE_0, WS0_WPN_ACC_0 = 67, 68, 69, 70
    WS0_WPN_1, WS0_WPN_NUM_1, WS0_WPN_FACE_1, WS0_WPN_ACC_1 = 71, 72, 73, 74
    WS0_WPN_2, WS0_WPN_NUM_2, WS0_WPN_FACE_2, WS0_WPN_ACC_2 = 75, 76, 77, 78
    WS0_WPN_3, WS0_WPN_NUM_3, WS0_WPN_FACE_3, WS0_WPN_ACC_3 = 79, 80, 81, 82
    WS0_WPN_4, WS0_WPN_NUM_4, WS0_WPN_FACE_4, WS0_WPN_ACC_4 = 83, 84, 85, 86
    WS0_WPN_5, WS0_WPN_NUM_5, WS0_WPN_FACE_5, WS0_WPN_ACC_5 = 87, 88, 89, 90
    WS0_WPN_6, WS0_WPN_NUM_6, WS0_WPN_FACE_6, WS0_WPN_ACC_6 = 91, 92, 93, 94
    WS0_WPN_7, WS0_WPN_NUM_7, WS0_WPN_FACE_7, WS0_WPN_ACC_7 = 95, 96, 97, 98
    WS0_WPN_8, WS0_WPN_NUM_8, WS0_WPN_FACE_8, WS0_WPN_ACC_8 = 99, 100, 101, 102
    WS0_WPN_9, WS0_WPN_NUM_9, WS0_WPN_FACE_9, WS0_WPN_ACC_9 = 103, 104, 105, 106

    WS0_YEAR, WS0_MONTH, WS0_LAST_YEAR, WS0_LAST_MONTH = 107, 108, 109, 110
    WS0_MVR_MOD, WS0_CLIMB_MOD, WS0_SORTIE_AMMO_MOD = 111, 112, 113
    WS0_SORTIE_FUEL_MOD, WS0_END_MOD = 114, 115
    WS0_ALT_MOD, WS0_SPD_MOD = 116, 117

    # --- Weapon Set 1 ---
    WS1_WPN_0, WS1_WPN_NUM_0, WS1_WPN_FACE_0, WS1_WPN_ACC_0 = 118, 119, 120, 121
    WS1_WPN_1, WS1_WPN_NUM_1, WS1_WPN_FACE_1, WS1_WPN_ACC_1 = 122, 123, 124, 125
    WS1_WPN_2, WS1_WPN_NUM_2, WS1_WPN_FACE_2, WS1_WPN_ACC_2 = 126, 127, 128, 129
    WS1_WPN_3, WS1_WPN_NUM_3, WS1_WPN_FACE_3, WS1_WPN_ACC_3 = 130, 131, 132, 133
    WS1_WPN_4, WS1_WPN_NUM_4, WS1_WPN_FACE_4, WS1_WPN_ACC_4 = 134, 135, 136, 137
    WS1_WPN_5, WS1_WPN_NUM_5, WS1_WPN_FACE_5, WS1_WPN_ACC_5 = 138, 139, 140, 141
    WS1_WPN_6, WS1_WPN_NUM_6, WS1_WPN_FACE_6, WS1_WPN_ACC_6 = 142, 143, 144, 145
    WS1_WPN_7, WS1_WPN_NUM_7, WS1_WPN_FACE_7, WS1_WPN_ACC_7 = 146, 147, 148, 149
    WS1_WPN_8, WS1_WPN_NUM_8, WS1_WPN_FACE_8, WS1_WPN_ACC_8 = 150, 151, 152, 153
    WS1_WPN_9, WS1_WPN_NUM_9, WS1_WPN_FACE_9, WS1_WPN_ACC_9 = 154, 155, 156, 157

    WS1_YEAR, WS1_MONTH, WS1_LAST_YEAR, WS1_LAST_MONTH = 158, 159, 160, 161
    WS1_MVR_MOD, WS1_CLIMB_MOD, WS1_SORTIE_AMMO_MOD = 162, 163, 164
    WS1_SORTIE_FUEL_MOD, WS1_END_MOD = 165, 166
    WS1_ALT_MOD, WS1_SPD_MOD = 167, 168

    # --- Weapon Set 2 ---
    WS2_WPN_0, WS2_WPN_NUM_0, WS2_WPN_FACE_0, WS2_WPN_ACC_0 = 169, 170, 171, 172
    WS2_WPN_1, WS2_WPN_NUM_1, WS2_WPN_FACE_1, WS2_WPN_ACC_1 = 173, 174, 175, 176
    WS2_WPN_2, WS2_WPN_NUM_2, WS2_WPN_FACE_2, WS2_WPN_ACC_2 = 177, 178, 179, 180
    WS2_WPN_3, WS2_WPN_NUM_3, WS2_WPN_FACE_3, WS2_WPN_ACC_3 = 181, 182, 183, 184
    WS2_WPN_4, WS2_WPN_NUM_4, WS2_WPN_FACE_4, WS2_WPN_ACC_4 = 185, 186, 187, 188
    WS2_WPN_5, WS2_WPN_NUM_5, WS2_WPN_FACE_5, WS2_WPN_ACC_5 = 189, 190, 191, 192
    WS2_WPN_6, WS2_WPN_NUM_6, WS2_WPN_FACE_6, WS2_WPN_ACC_6 = 193, 194, 195, 196
    WS2_WPN_7, WS2_WPN_NUM_7, WS2_WPN_FACE_7, WS2_WPN_ACC_7 = 197, 198, 199, 200
    WS2_WPN_8, WS2_WPN_NUM_8, WS2_WPN_FACE_8, WS2_WPN_ACC_8 = 201, 202, 203, 204
    WS2_WPN_9, WS2_WPN_NUM_9, WS2_WPN_FACE_9, WS2_WPN_ACC_9 = 205, 206, 207, 208

    WS2_YEAR, WS2_MONTH, WS2_LAST_YEAR, WS2_LAST_MONTH = 209, 210, 211, 212
    WS2_MVR_MOD, WS2_CLIMB_MOD, WS2_SORTIE_AMMO_MOD = 213, 214, 215
    WS2_SORTIE_FUEL_MOD, WS2_END_MOD = 216, 217
    WS2_ALT_MOD, WS2_SPD_MOD = 218, 219

    # --- Weapon Set 3 ---
    WS3_WPN_0, WS3_WPN_NUM_0, WS3_WPN_FACE_0, WS3_WPN_ACC_0 = 220, 221, 222, 223
    WS3_WPN_1, WS3_WPN_NUM_1, WS3_WPN_FACE_1, WS3_WPN_ACC_1 = 224, 225, 226, 227
    WS3_WPN_2, WS3_WPN_NUM_2, WS3_WPN_FACE_2, WS3_WPN_ACC_2 = 228, 229, 230, 231
    WS3_WPN_3, WS3_WPN_NUM_3, WS3_WPN_FACE_3, WS3_WPN_ACC_3 = 232, 233, 234, 235
    WS3_WPN_4, WS3_WPN_NUM_4, WS3_WPN_FACE_4, WS3_WPN_ACC_4 = 236, 237, 238, 239
    WS3_WPN_5, WS3_WPN_NUM_5, WS3_WPN_FACE_5, WS3_WPN_ACC_5 = 240, 241, 242, 243
    WS3_WPN_6, WS3_WPN_NUM_6, WS3_WPN_FACE_6, WS3_WPN_ACC_6 = 244, 245, 246, 247
    WS3_WPN_7, WS3_WPN_NUM_7, WS3_WPN_FACE_7, WS3_WPN_ACC_7 = 248, 249, 250, 251
    WS3_WPN_8, WS3_WPN_NUM_8, WS3_WPN_FACE_8, WS3_WPN_ACC_8 = 252, 253, 254, 255
    WS3_WPN_9, WS3_WPN_NUM_9, WS3_WPN_FACE_9, WS3_WPN_ACC_9 = 256, 257, 258, 259

    WS3_YEAR, WS3_MONTH, WS3_LAST_YEAR, WS3_LAST_MONTH = 260, 261, 262, 263
    WS3_MVR_MOD, WS3_CLIMB_MOD, WS3_SORTIE_AMMO_MOD = 264, 265, 266
    WS3_SORTIE_FUEL_MOD, WS3_END_MOD = 267, 268
    WS3_ALT_MOD, WS3_SPD_MOD = 269, 270

    # --- Weapon Set 4 ---
    WS4_WPN_0, WS4_WPN_NUM_0, WS4_WPN_FACE_0, WS4_WPN_ACC_0 = 271, 272, 273, 274
    WS4_WPN_1, WS4_WPN_NUM_1, WS4_WPN_FACE_1, WS4_WPN_ACC_1 = 275, 276, 277, 278
    WS4_WPN_2, WS4_WPN_NUM_2, WS4_WPN_FACE_2, WS4_WPN_ACC_2 = 279, 280, 281, 282
    WS4_WPN_3, WS4_WPN_NUM_3, WS4_WPN_FACE_3, WS4_WPN_ACC_3 = 283, 284, 285, 286
    WS4_WPN_4, WS4_WPN_NUM_4, WS4_WPN_FACE_4, WS4_WPN_ACC_4 = 287, 288, 289, 290
    WS4_WPN_5, WS4_WPN_NUM_5, WS4_WPN_FACE_5, WS4_WPN_ACC_5 = 291, 292, 293, 294
    WS4_WPN_6, WS4_WPN_NUM_6, WS4_WPN_FACE_6, WS4_WPN_ACC_6 = 295, 296, 297, 298
    WS4_WPN_7, WS4_WPN_NUM_7, WS4_WPN_FACE_7, WS4_WPN_ACC_7 = 299, 300, 301, 302
    WS4_WPN_8, WS4_WPN_NUM_8, WS4_WPN_FACE_8, WS4_WPN_ACC_8 = 303, 304, 305, 306
    WS4_WPN_9, WS4_WPN_NUM_9, WS4_WPN_FACE_9, WS4_WPN_ACC_9 = 307, 308, 309, 310
    WS4_YEAR, WS4_MONTH, WS4_LAST_YEAR, WS4_LAST_MONTH = 311, 312, 313, 314
    WS4_MVR_MOD, WS4_CLIMB_MOD, WS4_SORTIE_AMMO_MOD = 315, 316, 317
    WS4_SORTIE_FUEL_MOD, WS4_END_MOD = 318, 319
    WS4_ALT_MOD, WS4_SPD_MOD = 320, 321


# pylint: disable=too-few-public-methods
class Aircraft:
    """
    A dynamic object representation of a WiTE2 Aircraft.
    """
    # Just type-hint the ones you ACTUALLY use in your code for autocomplete!
    # You don't need to type-hint all 322 columns if you only care about a few.
    ID: int
    NAME: str
    MAX_SPEED: int
    MAX_ALT: int
    ENDURANCE: int
    RANGE: int

    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            try:
                converted_value = int(value)
            except (ValueError, TypeError):
                converted_value = value
            setattr(self, key, converted_value)

    def __getattr__(self, item: str) -> Any:
        normalized_request = item.replace("_", "").replace(".", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").replace(".", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


NUM_COLS : Final[int] = len(AcColumn)
ID_COL : Final[int] = AcColumn.ID


def gen_aircraft_column_names() -> list[str]:
    """
    Generates the 322 headers for a _aircraft.csv file dynamically.
    """

    # 1. Base Properties (Columns 0 to 36)
    cols: list[str] = [
        'id', 'name', 'maxAlt', 'nat', 'sym', 'maxSpeed', 'maxSpeedAlt',
        'zeroAltSpeed', 'maxAltSpeed', 'cruSpeed', 'climb', 'maxLoad',
        'endurance', 'range', 'year', 'mvr', 'armor', 'durab', 'month',
        'type', 'blank', 'upgrade', 'crew', 'sortieAmmo', 'sortieFuel',
        'buildCost', 'pool', 'buildLimit', 'maxImport', 'importFrom',
        'lastYear', 'lastMonth', 'relib', 'photo', 'expRate', 'engineNum',
        'airProfile'
    ]

    # 2. Built-in Weapon Slots (Columns 37 to 66)
    prefixes = ['wpn', 'wpnNum', 'wpnFace']
    for prefix in prefixes:
        for i in range(10):
            cols.append(f"{prefix} {i}")

    # 3. External Weapon Sets (ws0 through ws4) (Columns 67 to 321)
    for ws in range(5):
        # 10 weapon slots per Loadout
        for i in range(10):
            cols.extend([
                f"ws{ws}.wpn {i}",
                f"ws{ws}.wpnNum {i}",
                f"ws{ws}.wpnFace {i}",
                f"ws{ws}.wpnAcc {i}"
            ])
        # 7 Modifiers/Properties per Loadout
        cols.extend([
            f"ws{ws}.year", f"ws{ws}.month", f"ws{ws}.lastYear",
            f"ws{ws}.lastMonth", f"ws{ws}.mvrMod", f"ws{ws}.climbMod",
            f"ws{ws}.sortieAmmoMod", f"ws{ws}.sortieFuelMod",
            f"ws{ws}.endMod", f"ws{ws}.altMod", f"ws{ws}.spdMod"
        ])

    return cols


def gen_default_aircraft_row(aircraft_id: int = 0,
                             name: str = "",
                             nat: int = 0) -> list[str]:
    """
    Generates a default 322-column row for a _aircraft.csv file.

    Args:
        aircraft_id (int): The ID for the Aircraft (Column 0). Defaults to 0.
        name (str): The name of the Aircraft (Column 1). Defaults to empty.
        nat (int): The nationality ID (Column 3). Defaults to 0.

    Returns:
        list[str]: A list containing the ID, Name, 1 zero, Nationality,
        and 318 zeroes.
    """
    # Create the base row: [ID, Name, maxAlt (0), Nat]
    row: list[str] = [str(aircraft_id), name, "0", str(nat)]

    # Append 318 zeroes to fill out the remaining columns
    row.extend(["0"] * 318)

    return row


def gen_default_aircraft_dict(aircraft_id: int = 0,
                              name: str = "",
                              nat: int = 0) -> dict[str, str]:
    """
    Generates a default Aircraft dictionary mapped to schema headers.
    """
    headers = gen_aircraft_column_names()
    default_row_list = gen_default_aircraft_row(aircraft_id, name, nat)

    # Zip the 322 headers together with the 322 default values
    return dict(zip(headers, default_row_list))


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
