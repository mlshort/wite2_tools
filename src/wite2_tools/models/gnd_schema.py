"""
_ground.csv (Ground Element) Mapping Reference:
| Constant       | CSV Header | Index | Notes                         |
|----------------|------------|-------|-------------------------------|
| ID_COL         | id         | 0     | Unique Identifier             |
| NAME_COL       | name       | 1     | Display Name                  |
| TYPE_COL       | type       | 3     | Element Classification        |
| MEN_COL        | men        | 21    | Crew/Squad size (for Audits)  |
| WPN_0_COL      | wpn 0      | 32    | FK: _device.csv -> id         |
| WPN_NUM_0_COL  | wpnNum 0   | 42    | Quantity of weapon/device     |

Note: Ground elements link up to _ob.csv slots and down to _device.csv weapons.
"""
from enum import IntEnum
from typing import Final, List

class GndColumn(IntEnum):
    """
    Ground Column indices for WiTE2 _ground.csv files (92 Columns).

    The Ground Element schema defines physical characteristics and
    combat capabilities. It is organized into:
    1. Identification (0-5)
    2. Mobility & Protection (6-18): Armor, Speed, and Reliability.
    3. Production (19-31): Build costs, limits, and crew requirements.
    4. Armament Slots (32-71): 10 slots for IDs, Quantities, Ammo, and ROF.
    """
    ID = 0
    NAME = 1
    ID_2 = 2
    TYPE = 3
    SYM = 4
    NAT = 5
    MAX_LOAD = 6
    LOAD_COST = 7
    YEAR = 8
    LAST = 9
    LAST_MONTH = 10
    RANGE = 11  # max effective range
    SPEED = 12  #: speed in miles per hour
    DUR = 13
    SIZE = 14
    RELIB = 15  #: Reliability and Survivabiliy
    """
    The first digit represents the reliability of the AFV when
    moving (if only 1 digit is shown the 1st digit is assumed to be 0).
    The higher the number, the less likely the AFV will become damaged during
    movement.
    The second digit is survivability, and the higher the survivability the less
    likely the AFV will be destroyed in combat during a special survival check as
    opposed to just being damaged.
    """
    ARMOR = 16  #: front armour thickness in millimetres
    SIDE_ARMOR = 17
    TOP_ARMOR = 18
    MONTH = 19
    BUILD_LIMIT = 20
    MEN = 21
    UPGRADE = 22
    FUEL_USE = 23
    SUPPLY_USE = 24
    BUILD_COST = 25
    POOL = 26
    MAX_IMPORT = 27
    IMPORT_FROM = 28
    PHOTO = 29
    EXP_RATE = 30
    SCRAP_AFTER_YEAR = 31
   # --- Weapons ---
    WPN_0, WPN_1, WPN_2, WPN_3, WPN_4 = 32, 33, 34, 35, 36
    WPN_5, WPN_6, WPN_7, WPN_8, WPN_9 = 37, 38, 39, 40, 41

    WPN_NUM_0, WPN_NUM_1, WPN_NUM_2, WPN_NUM_3, WPN_NUM_4 = 42, 43, 44, 45, 46
    WPN_NUM_5, WPN_NUM_6, WPN_NUM_7, WPN_NUM_8, WPN_NUM_9 = 47, 48, 49, 50, 51

    WPN_AMMO_0, WPN_AMMO_1, WPN_AMMO_2, WPN_AMMO_3 = 52, 53, 54, 55
    WPN_AMMO_4, WPN_AMMO_5, WPN_AMMO_6, WPN_AMMO_7 = 56, 57, 58, 59
    WPN_AMMO_8, WPN_AMMO_9 = 60, 61

    WPN_ROF_0 = 62
    """
    Rate of Fire is a negative modifier that is applied to vehicle mounted
    devices to reflect the restrictions of operating the device inside the
    vehicle.
    """
    WPN_ROF_1, WPN_ROF_2, WPN_ROF_3, WPN_ROF_4 = 63, 64, 65, 66
    WPN_ROF_5, WPN_ROF_6, WPN_ROF_7, WPN_ROF_8 = 67, 68, 69, 70
    WPN_ROF_9 = 71

    WPN_ACC_0, WPN_ACC_1, WPN_ACC_2, WPN_ACC_3, WPN_ACC_4 = 72, 73, 74, 75, 76
    WPN_ACC_5, WPN_ACC_6, WPN_ACC_7, WPN_ACC_8, WPN_ACC_9 = 77, 78, 79, 80, 81

    WPN_FACE_0, WPN_FACE_1, WPN_FACE_2, WPN_FACE_3 = 82, 83, 84, 85
    WPN_FACE_4, WPN_FACE_5, WPN_FACE_6, WPN_FACE_7 = 86, 87, 88, 89
    WPN_FACE_8, WPN_FACE_9 = 90, 91

NUM_COLS : Final[int] = len(GndColumn)
WPN_SLOTS : Final[int] = 10
ATTR_PER_WPN : Final[int] = 6
# Aliasing indices to avoid repeated .value calls
#: Unique ID for the ground element.
ID_COL: Final[int]    = GndColumn.ID
NAME_COL: Final[int]  = GndColumn.NAME
TYPE_COL: Final[int]  = GndColumn.TYPE
NAT_COL : Final[int]  = GndColumn.NAT

SIZE_COL: Final[int]  = GndColumn.SIZE
#: The number of men required/present in the element (Critical for Strength Audits).
MEN_COL: Final[int]   = GndColumn.MEN
#: Maps to _device.csv -> id (The primary weapon carried)
WPN0_COL: Final[int]  = GndColumn.WPN_0

def gen_gnd_column_names() -> List[str]:
    """
    Generates the mapping for the GndColumn IntEnum.
    """

    # 1. Base properties (Columns 0 to 31)
    cols: List[str] = [
        'id', 'name', 'id', 'type', 'sym', 'nat', 'maxLoad', 'loadCost',
        'year', 'last', 'lastMonth', 'range', 'speed', 'dur', 'size',
        'relib', 'armor', 'sideArmor', 'topArmor', 'month', 'buildLimit',
        'men', 'upgrade', 'fuelUse', 'supplyUse', 'buildCost', 'pool',
        'maxImport', 'importFrom', 'photo', 'expRate', 'scrapAfterYear'
    ]

    # 2. Dynamically generate the numbered weapon slots (Columns 32 to 91)
    prefixes = ['wpn', 'wpnNum', 'wpnAmmo', 'wpnRof', 'wpnAcc', 'wpnFace']

    for prefix in prefixes:
        # Assuming 10 slots (0 through 9) based on the WiTE2 CSV schema
        for i in range(WPN_SLOTS):
            cols.append(f"{prefix} {i}")

    return cols


def gen_default_gnd_row(elem_id: int = 0,
                        name: str = "") -> List[str]:
    """
    Generates a default 92-column row for a _ground.csv file.

    Args:
        elem_id (int): The ID for the ground element (Column 0). Defaults to 0.
        name (str): The name of the element (Column 1). Defaults to empty.

    Returns:
        List[str]: A list containing the ID, Name, and 90 zeroes.
    """
    # Create the base row with the ID and Name
    row: List[str] = [str(elem_id), name]

    # Append 90 zeroes to fill out the remaining 90 columns
    # (Properties, Limits, and the 10x Weapon Slots)
    row.extend(["0"] * 90)

    return row
