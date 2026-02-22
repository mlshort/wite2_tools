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
from functools import cache
from dataclasses import dataclass

# Internal package imports
from wite2_tools.constants import GroundColumn
from wite2_tools.generator import (
    read_csv_dict_generator,
    read_csv_list_generator,
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import (
    parse_int,
    parse_str
)

# Initialize the log for this specific module
logger = get_logger(__name__)


@dataclass(frozen=True)
class OBName:
    """
    Used when building a full ob name
    """
    full_name: str
    suffix: str  # stores the suffix for later


# ==========================================
# ORDER OF BATTLE TOE(OB) LOOKUP
# ==========================================


@cache
def _build_ob_lookup(ob_file_path: str) -> dict[int, OBName]:
    """
    Private Helper: Scans the _ob CSV, builds the TOE(ID)-to-Name dictionary,
    and caches it.
    The @cache decorator ensures this only runs once per unique file path.
    """
    lookup: dict[int, OBName] = {}

    if not os.path.exists(ob_file_path):
        logger.error("TOE(OB) file not found: %s", ob_file_path)
        return lookup

    try:
        ob_gen = read_csv_dict_generator(ob_file_path)
        next(ob_gen)  # Skip DictReader yield

        for _, row in ob_gen:
            ob_id = parse_int(row.get("id"), 0)
            if ob_id != 0:
                ob_name = parse_str(row.get('name'), '')
                ob_suffix = parse_str(row.get('suffix'), '')
                ob_full_name = f"{ob_name} {ob_suffix}"

                lookup[ob_id] = OBName(
                    full_name=ob_full_name,
                    suffix=ob_suffix
                )

    except (OSError, IOError, ValueError, KeyError) as e:
        logger.error("Error building TOE(OB) lookup: %s", e)

    return lookup


def get_ob_full_name(ob_file_path: str, ob_id_to_find: int) -> str:
    """
    Public API: Resolves an TOE(OB) ID to a full name.
    """
    # 1. Retrieve the cached dictionary
    cached_dict = _build_ob_lookup(ob_file_path)

    # 2. Perform instant O(1) lookup
    result = cached_dict.get(ob_id_to_find)

    if result is not None:
        return result.full_name
    else:
        return f"Unk ({ob_id_to_find})"


def get_unit_type_name(ob_file_path: str, unit_id_to_find: int) -> str:
    """
    A convenience wrapper. In WiTE2, a unit's type name is derived
    from its assigned TOE(OB) name in the _ob.csv file and equates to its
    TOE(OB)'s full name.
    """
    # Simply route this through the TOE(OB) lookup to utilize the same cache
    return get_ob_full_name(ob_file_path, unit_id_to_find)


# ==========================================
# GROUND ELEMENT LOOKUP
# ==========================================


@cache
def _build_ground_elem_lookup(ground_file_path: str) -> dict[int, str]:
    """
    Private Helper: Scans the _ground CSV, builds the ID-to-Name dictionary,
    and caches it.
    The @cache decorator ensures this only runs once per unique file path.
    """
    lookup: dict[int, str] = {}

    if not os.path.exists(ground_file_path):
        logger.error("Ground file not found: %s", ground_file_path)
        return lookup

    try:
        ground_gen = read_csv_list_generator(ground_file_path)
        next(ground_gen)  # Skip Header

        for _, row in ground_gen:
            try:
                g_id = parse_int(row[GroundColumn.ID], 0)
                if g_id != 0:
                    # 'name' column
                    g_name = parse_str(row[GroundColumn.NAME], "")
                    lookup[g_id] = g_name
            except (ValueError, IndexError):
                continue

    except (OSError, IOError) as e:
        logger.error("Error building ground lookup: %s", e)

    return lookup


def get_ground_elem_type_name(ground_file_path: str,
                              ground_id_to_find: int) -> str:
    """
    Public API: Resolves a Ground Element WID to its name.
    """
    # 1. Retrieve the cached dictionary
    cached_dict = _build_ground_elem_lookup(ground_file_path)

    # 2. Perform instant O(1) lookup
    return cached_dict.get(ground_id_to_find, f"Unk ({ground_id_to_find})")
