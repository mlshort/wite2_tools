from enum import IntEnum
from typing import Dict, List, Any

from wite2_tools.constants import MAX_SQUAD_SLOTS

def _generate_ob_columns() -> Dict[str, int]:
    """Generates the column dictionary for OB files dynamically."""
    cols: List[str] = [
        "ID", "NAME", "SUFFIX", "NAT", "FIRST_YEAR", "FIRST_MONTH",
        "LAST_YEAR", "LAST_MONTH", "TYPE", "UPGRADE", "OB_CLASS",
        "ICON", "DIVIDE_MULTI_ROLE", "MTZ_TYPE", "FORM_SIZE"
    ]

    # Append SQD_0 through SQD_31
    for i in range(MAX_SQUAD_SLOTS):
        cols.append(f"SQD_{i}")

    # Append SQD_NUM_0 through SQD_NUM_31
    for i in range(MAX_SQUAD_SLOTS):
        cols.append(f"SQD_NUM_{i}")

    return {name: i for i, name in enumerate(cols)}

# Expose the Enum just like we did for Unit
# ObColumn = IntEnum("ObColumn", _generate_ob_columns())

class ObColumn(IntEnum):
    """
    TOE(OB) Column indexes for WiTE2's _ob.csv files
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


class OB:
    """
    A dynamic object representation of a WiTE2 Order of Battle (OB).
    Automatically converts CSV string numbers into integers for math/logic.
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