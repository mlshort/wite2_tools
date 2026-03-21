"""
_device.csv Mapping Reference:
| Constant       | CSV Header | Index | Notes                                 |
|----------------|------------|-------|---------------------------------------|
| D_ID_COL       | id         | 0     | Unique Identifier                     |
| D_NAME_COL     | name       | 1     | Display Name                          |
| TYPE_COL       | type       | 2     | Device Type Code                      |
| SYM_COL        | sym        | 3     | Symbol Code                           |
| LOAD_COST_COL  | loadCost   | 4     | Weight in pounds                      |
| PEN_COL        | pen        | 7     | Armor penetration (mm at 100 meters)  |

Note: The Device file contains exactly 25 columns (0-24) covering all combat
statistics and properties for weapons/equipment.
"""
from enum import IntEnum
from typing import Final, List, Dict

# pylint: disable=invalid-name
class DevColumn(IntEnum):
    """
    Device Column indices for WiTE2's _device.csv file (25 Columns).

    The Device schema defines the combat statistics and properties of weapons
    and equipment used by Ground Elements and Aircraft.
    """
    ID = 0
    NAME = 1
    TYPE = 2
    SYM = 3

    # Number of pounds the device weighs
    LOAD_COST = 4

    # No idea how this is used
    RANGE = 5
    EFFECT = 6

    # Penetration: Number of millimetres of armour plate the weapon can
    # penetrate. Appears to be 0-degree (vertical) penetration at 100 meters.
    PEN = 7

    # Accuracy
    ACC = 8

    # Max Ceiling (in feet)
    CEILING = 9
    ANTI_ARMOR = 10
    ANTI_SOFT = 11

    # Not displayed in the Editor
    WARHEAD = 12
    ANTI_AIR = 13

    # Maximum Effective Range (meters for ground units, feet for aircraft)
    RG = 14

    # Rate of Fire (can be negative). A negative value is scaled as RoF
    # of 1 / x minutes, instead of x / 1 minute.
    ROF = 15
    # Rate of Fire (ROF) is not used in the conventional military sense.
    # It indicates how many times a device will be allowed to fire during
    # the combat phase. The higher the number entered the better the ROF.

    # HEAT Pen
    # number of millimetres of armour plate the HEAT weapon can penetrate
    # at (100 meter?) range
    HEAT = 16
    # High Velocity Armor Piercing (HVAP)
    HVAP = 17
    BLAST = 18
    # Not displayed in the Editor
    DUD_RATE = 19
    COUNTER_DEV = 20
    COUNTER_DT = 21
    COUNTER_VAL = 22
    COUNTER_T_VAL = 23
    # Max Effective Ceiling (in feet)
    EFF_CEILING = 24

# 1. Warhead: The Caliber Scale
#
# The warhead value is the primary driver of explosive power and is calculated
# based on the internal volume/caliber of the projectile.
#
#    Linear Scaling for Anti-Tank (AT) Guns: For most standard tank and AT
# guns, the warhead value is almost always roughly Caliber ÷ 15.
# (e.g., 75mm = 4; 88mm = 5; 50mm = 3).
#
#    Artillery & Large Bore: As caliber increases, the scale jumps to reflect
# the non-linear increase in explosive filler. A 150mm howitzer (ID 416) is a
# ssigned an 8, and the massive 600mm Karl-Gerät (ID 441) jumps to 30.
#
#    Small Arms: Machine guns and rifles generally have a warhead of 0,
# indicating they do not rely on chemical energy (explosives) to deal damage.

# 2. Blast: Explosive Radius and Suppression
#
# The blast value correlates strongly with warhead (correlation coefficient of
# 0.30, but nearly 1:1 in behavior for high-caliber weapons) and represents
# the "footprint" of the explosion.
#
#    Formulaic Consistency: For field guns and howitzers, blast is typically
# warhead + 2. (e.g., the 88mm has a warhead of 5 and a blast of 5; the 150mm
# has a warhead of 8 and a blast of 10).
#
#    Rockets vs. Shells: Rockets like the 150mm NbW 41 (ID 430) have a higher
# blast (13) than shells of the same caliber (10), likely to simulate the
# thinner walls of rocket casings which allowed for more explosive filler and
# a larger burst radius at the expense of penetration.

# ---------------------------------------------------------
# CONSTANT ALIASES FOR LEGACY OR CONVENIENCE
# ---------------------------------------------------------
NUM_COLS : Final[int] = len(DevColumn)

ID_COL : Final[int]        = DevColumn.ID
NAME_COL : Final[int]      = DevColumn.NAME
TYPE_COL : Final[int]      = DevColumn.TYPE
LOAD_COST_COL : Final[int] = DevColumn.LOAD_COST
PEN_COL : Final[int]       = DevColumn.PEN



def gen_device_column_names() -> List[str]:
    """
    Generates the 25 headers for a _device.csv file.

    Returns:
        List[str]: A list of column header strings.
    """
    return [
        'id', 'name', 'type', 'sym', 'loadCost', 'range', 'effect', 'pen',
        'acc', 'ceiling', 'antiArmor', 'antiSoft', 'warhead', 'antiAir',
        'rg', 'rof', 'heat', 'hvap', 'blast', 'dudRate', 'counterDev',
        'counterDT', 'counterVal', 'counterTVal', 'effCeiling'
    ]


def gen_default_device_row(device_id: int = 0,
                           name: str = "") -> List[str]:
    """
    Generates a default 25-column row for a _device.csv file.

    Args:
        device_id (int): The ID for the Device (Column 0). Defaults to 0.
        name (str): The name of the Device (Column 1). Defaults to empty.

    Returns:
        List[str]: A list containing the ID, Name, and 23 zeroes.
    """
    row: List[str] = [str(device_id), name]

    # Append 23 zeroes to fill out the remaining combat statistics
    row.extend(["0"] * 23)

    return row


def gen_default_device_dict(device_id: int = 0,
                            name: str = "") -> Dict[str, str]:
    """Generates a default Device dictionary mapped to schema headers."""
    headers = gen_device_column_names()
    default_row_list = gen_default_device_row(device_id, name)

    # Zip the 25 headers together with the 25 default values
    return dict(zip(headers, default_row_list))


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
