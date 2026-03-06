"""
Type Name Resolution Utilities
==============================

This module provides functions to resolve numerical type IDs into
human-readable names by referencing external CSV data files
(specifically TOE(OB) and Ground Element files).
It is primarily used for converting raw data IDs from the WiTE2 context into
descriptive strings for logging or display.

Caching Mechanism
-----------------
To optimize performance and minimize file I/O operations, this module
implements a private-helper caching pattern utilizing `functools.cache`.

The first call to a retrieval function triggers a full read of the
respective CSV file, caching the fully parsed dictionary. All subsequent
lookups query this cached dictionary instantly in O(1) time.

Functions
---------
* `get_ob_full_name`: Resolves an TOE(OB) ID to a full name (combining 'name'
                      and 'suffix').
* `get_unit_type_name`: A wrapper alias for `get_ob_full_name` used for
                        semantic clarity.
* `get_ground_elem_type_name`: Resolves a Ground Element ID to its name.
"""

import os
from typing import Dict
from functools import cache
from dataclasses import dataclass

# Internal package imports
from wite2_tools.constants import GroundColumn
from wite2_tools.generator import (
    get_csv_dict_stream,
    get_csv_list_stream,
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import parse_int, parse_str


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

    if not os.path.exists(ob_file_path):
        log.error("TOE(OB) file not found: %s", ob_file_path)
        return lookup

    try:
        ob_stream = get_csv_dict_stream(ob_file_path)

        for _, row in ob_stream.rows:
            ob_id:int = parse_int(row.get("id"))
            if ob_id != 0:
                ob_name:str = parse_str(row.get('name'), '')
                ob_suffix:str = parse_str(row.get('suffix'), '')

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
    cached_dict = _build_ob_lookup(ob_file_path)

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
    cached_dict = _build_ob_lookup(ob_file_path)

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
    cached_dict = _build_ob_lookup(ob_file_path)

    # 2. Perform instant O(1) lookup
    result = cached_dict.get(ob_id_to_find)

    if result is not None:
        ob_full_name = f"{result.name} {result.suffix}"
        return ob_full_name

    return f"Unk ({ob_id_to_find})"


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

    if not os.path.exists(ground_file_path):
        log.error("Ground file not found: '%s'", ground_file_path)
        return lookup

    try:
        # Use list generator to handle duplicate 'id' column names safely
        gnd_stream = get_csv_list_stream(ground_file_path)

        if gnd_stream.header is None:
            return lookup

        for _, row in gnd_stream.rows:
            try:
                # Ensure GroundColumn values are integers for list indexing
                g_id = parse_int(row[GroundColumn.ID])
                if g_id != 0:
                    # Capture the name based on the specific column index
                    g_name = parse_str(row[GroundColumn.NAME], "")
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
    cached_dict = _build_ground_elem_lookup(ground_file_path)

    # 2. Perform instant O(1) lookup
    return cached_dict.get(wid_to_find, f"Unk ({wid_to_find})")
