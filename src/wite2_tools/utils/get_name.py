"""
Type Name Resolution Utilities
==============================

This module provides functions to resolve numerical type IDs into
human-readable names by referencing external CSV data files
It is primarily used for converting raw data IDs from the WiTE2 context into
descriptive strings for logging, reporting or display.

Caching Mechanism
-----------------
To optimize performance and minimize file I/O operations, this module
implements a private-helper caching pattern utilizing `functools.cache`.

The first call to a retrieval function triggers a full read of the
respective CSV file, caching the fully parsed dictionary. All subsequent
lookups query this cached dictionary instantly in O(1) time.

Functions
---------
* `get_ob_name`: Resolves a TOE(OB) ID to its base name.
* `get_ob_suffix`: Resolves a TOE(OB) ID to its suffix.
* `get_ob_full_name`: Resolves a TOE(OB) ID to a full name (combining 'name'
                      and 'suffix').
* `get_unit_type_name`: A wrapper alias for `get_ob_full_name` used for
                        semantic clarity.
* `get_ground_elem_type_name`: Resolves a Ground Element ID to its name via
                               CSV lookup.
* `get_ob_combat_class_name`: Retrieves the description for a specific Combat
                              Class code.
* `get_device_type_name`: Retrieves the description for a specific Device
                          Type code.
* `get_ob_type_code_name`: Retrieves the name for a specific TOE(OB) Type code.
* `get_country_name`: Returns the nation name for a given ID.
* `get_unit_special_name`: Returns the string description for a given WiTE2
                           status code.
* `get_ground_elem_class_name`: Returns the string name for a Ground Element
                                Type WID.
* `get_device_face_type_name`: Retrieves the orientation description for a
                               Device Face code.
"""

import os
from typing import Dict
from functools import cache
from dataclasses import dataclass

# Internal package imports
from wite2_tools.models import (
    G_ID_COL,
    G_NAME_COL,
    O_ID_COL,
    O_NAME_COL,
    O_SUFFIX_COL
)
from wite2_tools.generator import (
    CSVListStream,
    get_csv_list_stream
)


from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import (
    parse_row_int,
    parse_row_str
)
from wite2_tools.utils.lookups import (
    OB_COMBAT_CLASS_LOOKUP,
    OB_TYPE_LOOKUP,
    NATION_LOOKUP,
    UNIT_SPECIAL_LOOKUP,
    DEVICE_TYPE_LOOKUP,
    GROUND_ELEMENT_TYPE_LOOKUP,
    DEVICE_FACE_TYPE_LOOKUP
)


# Initialize the log for this specific module
log = get_logger(__name__)


@dataclass(frozen=True)
class ObName:
    """
    Used when building a full ob name
    """
    name: str
    suffix: str


# ==========================================
# ORDER OF BATTLE TOE(OB) LOOKUP
# ==========================================


@cache
def _build_ob_lookup(ob_file_path: str) -> Dict[int, ObName]:
    """
    Private Helper: Scans the _ob CSV, builds the TOE(ID)-to-Name dictionary,
    and caches it.
    The @cache decorator ensures this only runs once per unique file path.
    """
    lookup: Dict[int, ObName] = {}

    if not os.path.isfile(ob_file_path):
        log.error("TOE(OB) file not found: %s", ob_file_path)
        return lookup

    try:
        ob_stream: CSVListStream = get_csv_list_stream(ob_file_path)

        for _, row in ob_stream.rows:

            ob_id:int = parse_row_int(row, O_ID_COL)
            if ob_id != 0:
                ob_name:str = parse_row_str(row, O_NAME_COL)
                ob_suffix:str = parse_row_str(row, O_SUFFIX_COL)

                lookup[ob_id] = ObName(
                    name=ob_name,
                    suffix=ob_suffix
                )

    except (OSError, IOError, ValueError, KeyError) as e:
        log.error("Error building TOE(OB) lookup: %s", e)

    return lookup



def get_ob_name(ob_file_path: str, ob_id_to_find: int) -> str:
    """
    Public API: Resolves an TOE(OB) ID to a name.
    """
    # 1. Retrieve the cached dictionary
    cached_dict: Dict[int, ObName] = _build_ob_lookup(ob_file_path)

    # 2. Perform instant O(1) lookup
    result = cached_dict.get(ob_id_to_find)

    if result is not None:
        return result.name

    return f"Unk ({ob_id_to_find})"


def get_ob_suffix(ob_file_path: str, ob_id_to_find: int) -> str:
    """
    Public API: Resolves an TOE(OB) ID to its suffix.
    """
    # 1. Retrieve the cached dictionary
    cached_dict: Dict[int, ObName] = _build_ob_lookup(ob_file_path)

    # 2. Perform instant O(1) lookup
    result = cached_dict.get(ob_id_to_find)

    if result is not None:
        return result.suffix

    return f"Unk ({ob_id_to_find})"


def get_ob_full_name(ob_file_path: str, ob_id_to_find: int) -> str:
    """
    Public API: Resolves an TOE(OB) ID to a full name.
    """
    # 1. Retrieve the cached dictionary
    cached_dict: Dict[int, ObName] = _build_ob_lookup(ob_file_path)

    # 2. Perform instant O(1) lookup
    result = cached_dict.get(ob_id_to_find)

    if result is not None:
        ob_full_name = f"{result.name} {result.suffix}"
        return ob_full_name

    return f"Unk ({ob_id_to_find})"


def get_ob_combat_class_name(ob_class_val: int) -> str:
    """
    Retrieves the description for a specific Combat Class code.
    Returns 'Unk ' if the code is not found.
    """
    return OB_COMBAT_CLASS_LOOKUP.get(ob_class_val, f"Unk ({ob_class_val})")


def get_ob_type_code_name(ob_type_code: int) -> str:
    """
    Not to be confused with 'get_ob_type_name', this one
    retrieves the name for a specific TOE(OB) Type code.
    Returns 'Unk ' if the code is not found.
    """
    result = OB_TYPE_LOOKUP.get(ob_type_code,  f"Unk ({ob_type_code})")
    return result


def get_unit_type_name(ob_file_path: str, unit_id_to_find: int) -> str:
    """
    A convenience wrapper. In WiTE2, a unit's type name is derived
    from its assigned TOE(OB)'s name + suffix in the _ob.csv file and equates
    to its TOE(OB)'s full name.
    """
    # Simply route this through the TOE(OB) lookup to utilize the same cache
    return get_ob_full_name(ob_file_path, unit_id_to_find)


# ==========================================
# GROUND ELEMENT LOOKUP
# ==========================================


@cache
def _build_ground_elem_lookup(ground_file_path: str) -> Dict[int, str]:
    """
    Private Helper: Scans the _ground CSV using list-based indexing.
    Cached to ensure O(1) lookups after the first I/O pass.
    """
    lookup: Dict[int, str] = {}

    if not os.path.isfile(ground_file_path):
        log.error("Ground file not found: '%s'", ground_file_path)
        return lookup

    try:
        # Use list generator to handle duplicate 'id' column names safely
        gnd_stream: CSVListStream = get_csv_list_stream(ground_file_path)

        for _, row in gnd_stream.rows:

            try:
                # Ensure GndColumn values are integers for list indexing
                g_id = parse_row_int(row, G_ID_COL)
                if g_id != 0:
                    # Capture the name based on the specific column index
                    g_name = parse_row_str(row, G_NAME_COL)
                    lookup[g_id] = g_name
            except (ValueError, IndexError):
                # ValueError: parse_int failed; IndexError: row is too short
                continue

    except (OSError, IOError) as e:
        log.error("Error building ground lookup: %s", e)

    return lookup


def get_ground_elem_type_name(ground_file_path: str,
                              wid_to_find: int) -> str:
    """
    Public API: Resolves a Ground Element WID to its name via O(1) lookup.
    """
    # 1. Retrieve the cached dictionary
    cached_dict: Dict[int, str] = _build_ground_elem_lookup(ground_file_path)

    # 2. Perform instant O(1) lookup
    return cached_dict.get(wid_to_find, f"Unk ({wid_to_find})")


def get_device_type_name(device_code: int) -> str:
    """
    Retrieves the description for a specific Device Type code.
    Returns 'Unk ' if the code is not found.
    """
    return DEVICE_TYPE_LOOKUP.get(device_code, f"Unk ({device_code})")


def get_country_name(nat_id: int) -> str:
    """
    Returns the nation name for a given ID.
    Defaults to 'Unk ' if ID is not in the list.
    """
    return NATION_LOOKUP.get(nat_id, f"Unk ({nat_id})")


def get_unit_special_name(status_code: int) -> str:
    """
    Returns the string description for a given WiTE2 status code.
    Defaults to 'Unk' if the code is not in the lookup table.
    """
    return UNIT_SPECIAL_LOOKUP.get(status_code, f"Unk ({status_code})")


def get_ground_elem_class_name(type_id: int) -> str:
    """
    Returns the string name for a Ground Element Type WID.
    Handles undefined ranges gracefully.
    """
    return GROUND_ELEMENT_TYPE_LOOKUP.get(type_id, f"Unk ({type_id})")


def get_device_face_type_name(face_code: int) -> str:
    """
    Retrieves the orientation description for a Device Face code.
    Defaults to 'Unk' if the code is outside the 0-12 range.
    """
    return DEVICE_FACE_TYPE_LOOKUP.get(face_code, f"Unk ({face_code})")
