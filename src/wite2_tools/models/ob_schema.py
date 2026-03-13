"""
_ob.csv (TOE) Mapping Reference:
| Constant       | CSV Header | Index | Notes                         |
|----------------|------------|-------|-------------------------------|
| ID_COL         | id         | 0     | Unique Identifier             |
| NAME_COL       | name       | 1     | Display Name                  |
| SUFFIX_COL     | suffix     | 2     | Unit Naming Suffix            |
| UPGRADE_COL    | upgrade    | 9     | FK: _ob.csv -> id (Next TOE)  |
| SQD0_COL       | sqd 0      | 15    | FK: _ground.csv -> id         |
| SQD_NUM0_COL   | sqdNum 0   | 47    | Quantity of Ground Element    |

Note: The OB file contains exactly 79 columns (0-78) covering 32 slots.
"""
from enum import IntEnum
from typing import List, Any, Final


class ObColumn(IntEnum):
    """
    TOE(OB) Column indices for WiTE2 _ob.csv files (79 Columns).

    The OB (Order of Battle) schema is divided into three logical zones:
    1. Metadata (0-14): ID, Name, Upgrade logic, and Form Size.
    2. Ground Element Slots (15-46): 32 columns containing Ground IDs.
    3. Quantities (47-78): 32 columns containing the TOE strength for each slot.
    """
    ID = 0
    NAME = 1
    SUFFIX = 2
    NAT = 3
    FIRST_YEAR = 4
    FIRST_MONTH = 5
    LAST_YEAR = 6
    LAST_MONTH = 7
    TYPE = 8
    UPGRADE = 9
    OB_CLASS = 10
    ICON = 11
    DIVIDE_MULTI_ROLE = 12
    MTZ_TYPE = 13
    FORM_SIZE = 14
# --- Squads ---
    SQD_0, SQD_1, SQD_2, SQD_3, SQD_4, SQD_5 = 15, 16, 17, 18, 19, 20
    SQD_6, SQD_7, SQD_8, SQD_9, SQD_10, SQD_11 = 21, 22, 23, 24, 25, 26
    SQD_12, SQD_13, SQD_14, SQD_15, SQD_16, SQD_17 = 27, 28, 29, 30, 31, 32
    SQD_18, SQD_19, SQD_20, SQD_21, SQD_22, SQD_23 = 33, 34, 35, 36, 37, 38
    SQD_24, SQD_25, SQD_26, SQD_27, SQD_28, SQD_29 = 39, 40, 41, 42, 43, 44
    SQD_30, SQD_31 = 45, 46

    # --- Squad Numbers (Quantities) ---
    SQD_NUM_0, SQD_NUM_1, SQD_NUM_2, SQD_NUM_3, SQD_NUM_4 = 47, 48, 49, 50, 51
    SQD_NUM_5, SQD_NUM_6, SQD_NUM_7, SQD_NUM_8, SQD_NUM_9 = 52, 53, 54, 55, 56
    SQD_NUM_10, SQD_NUM_11, SQD_NUM_12, SQD_NUM_13 = 57, 58, 59, 60
    SQD_NUM_14, SQD_NUM_15, SQD_NUM_16, SQD_NUM_17 = 61, 62, 63, 64
    SQD_NUM_18, SQD_NUM_19, SQD_NUM_20, SQD_NUM_21 = 65, 66, 67, 68
    SQD_NUM_22, SQD_NUM_23, SQD_NUM_24, SQD_NUM_25 = 69, 70, 71, 72
    SQD_NUM_26, SQD_NUM_27, SQD_NUM_28, SQD_NUM_29 = 73, 74, 75, 76
    SQD_NUM_30, SQD_NUM_31 = 77, 78


NUM_COLS : Final[int] = len(ObColumn)
SQD_SLOTS : Final[int] = 32

#: The unique ID for this TOE definition.
ID_COL: Final[int]       = ObColumn.ID
NAME_COL : Final[int]    = ObColumn.NAME
SUFFIX_COL : Final[int]  = ObColumn.SUFFIX
NAT_COL : Final[int]     = ObColumn.NAT
TYPE_COL: Final[int]     = ObColumn.TYPE
#: The ID of the TOE this unit will eventually upgrade into.
UPGRADE_COL: Final[int]  = ObColumn.UPGRADE

FIRSTYEAR_COL : Final[int]  = ObColumn.FIRST_YEAR
FIRSTMONTH_COL : Final[int] = ObColumn.FIRST_MONTH
LASTYEAR_COL : Final[int]   = ObColumn.LAST_YEAR
LASTMONTH_COL : Final[int]  = ObColumn.LAST_MONTH

#: Starting index for Ground Element ID slots (Maps to _ground.csv -> id).
ELEM_BASE: Final[int]    = ObColumn.SQD_0
#: Starting index for Quantity slots
NUM_BASE: Final[int]     = ObColumn.SQD_NUM_0
SQD0_COL: Final[int]     = ObColumn.SQD_0
SQD_NUM0_COL: Final[int] = ObColumn.SQD_NUM_0


def gen_ob_column_names() -> List[str]:
    """
    Generates the column name list for OB files dynamically.
    """
    cols: List[str] = [
        "id", "name", "suffix", "nat", "firstYear", "firstMonth",
        "lastYear", "lastMonth", "type", "upgrade", "obClass",
        "icon", "divideMultiRole", "mtzType", "formSize"
    ]

    # Append SQD_0 through SQD_31
    for i in range(SQD_SLOTS):
        cols.append(f"sqd {i}")

    # Append SQD_NUM_0 through SQD_NUM_31
    for i in range(SQD_SLOTS):
        cols.append(f"sqdNum {i}")

    return cols


def gen_default_ob_row(ob_id: int = 0,
                       name: str = "",
                       suffix: str = "") -> List[str]:
    """
    Generates a default 79-column row for an _ob.csv file.

    Args:
        ob_id (int): The ID for the OB (Column 0). Defaults to 0.
        name (str): The name of the OB (Column 1). Defaults to empty.
        suffix (str): The suffix string (Column 2). Defaults to empty.

    Returns:
        List[str]: A list containing the ID, Name, Suffix, and 76 zeroes.
    """
    # Create the base row with the ID, Name, and Suffix
    row: List[str] = [str(ob_id), name, suffix]

    # Append 76 zeroes to fill out the remaining columns
    # (12 remaining base properties + 32 'sqd' slots + 32 'sqdNum' slots)
    row.extend(["0"] * 76)

    return row

# pylint: disable= too-few-public-methods
class OB:
    """
    A dynamic representation of a WiTE2 Order of Battle (TOE).

    This class transforms raw CSV row dictionaries into objects with
    type-hinted attributes. It supports fuzzy attribute lookup (e.g.,
    ob.sqd0 or ob.SQD_0) via __getattr__.
    """
    # Type hints for standard OB fields to keep Pylance happy
    ID: int
    NAME: str
    SUFFIX: str
    NAT: int
    FIRST_YEAR: int
    FIRST_MONTH: int
    LAST_YEAR: int
    LAST_MONTH: int
    TYPE: int
    UPGRADE: int
    OB_CLASS: int
    FORM_SIZE: int

    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            # Attempt to convert to integer for comparisons (like ob.men > 500)
            try:
                converted_value = int(value)
            except (ValueError, TypeError):
                converted_value = value  # Keep as string for names, types, etc.

            setattr(self, key, converted_value)

    def __getattr__(self, item: str) -> Any:
        normalized_request = item.replace("_", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
