"""
Valid ID Caching & Lookup Utility
=================================

This module provides highly efficient, cached retrieval of valid ID sets for
various entities (Units, OBs, Ground Elements) within War in the East 2 (WiTE2)
data.

To optimize performance across bulk auditing and modification scripts, this
module reads the massive CSV files once, extracts the active/valid IDs
(explicitly filtering out empty or zero-type placeholders), and stores them in
global memory. Subsequent calls to these functions perform instant O(1) set
lookups instead of triggering repeated file I/O operations.

Core Features:
--------------
* Memory-Efficient Initialization: Utilizes list-based CSV generators to stream
  data.
* Global Caching: Prevents redundant parsing operations across the toolset.
* Automatic Data Cleaning: Automatically drops invalid or structural
  placeholder rows (e.g., where 'type' or 'id' equals 0).

Main Functions:
---------------
* get_valid_ob_ids          : Returns a set of all valid Order of Battle
                              TOE(OB) IDs.
* get_valid_ob_upgrade_ids  : Returns a set of all valid TOE(OB) upgrade target
                              IDs.
* get_valid_ground_elem_ids : Returns a set of all active Ground Element WIDs.
* get_valid_unit_ids        : Returns a set of all active Unit IDs deployed in
                              the scenario.
"""
import os
from typing import Set
from functools import cache

# Internal package imports
from wite2_tools.constants import (
    GroundColumn,
    ObColumn
)
from wite2_tools.generator import (
    get_csv_list_stream,
    get_csv_dict_stream
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import parse_int

# Initialize the log for this specific module
logger = get_logger(__name__)


@cache
def get_valid_ob_ids(ob_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid TOE(OB) IDs from the _ob CSV.
    The @cache decorator ensures this function only runs once per
    unique file path!
    """
    valid_ob_ids: Set[int] = set()
    file_name = os.path.basename(ob_file_path)
    logger.info("Building valid TOE(OB) ID cache from '%s'...", file_name)

    try:
        ob_stream = get_csv_list_stream(ob_file_path)

        for _, row in ob_stream.rows:
            try:
                ob_id = parse_int(row[ObColumn.ID])  # 'id' column
                ob_type = parse_int(row[ObColumn.TYPE])  # 'type' column
                if ob_id != 0 and ob_type != 0:
                    valid_ob_ids.add(ob_id)
            except (ValueError, IndexError):
                continue

        logger.info("  Cache built with %d valid TOE(OB) IDs.",
                    len(valid_ob_ids))
        return valid_ob_ids

    except FileNotFoundError:
        logger.error("_ob csv file not found:'%s'", ob_file_path)
        return set()


@cache
def get_valid_ob_upgrade_ids(ob_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid upgrade IDs from the _ob CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_ob_upgrade_ids: Set[int] = set()
    logger.info("Building valid TOE(OB) upgrade ID cache from '%s'...",
                ob_file_path)

    try:
        ob_stream = get_csv_list_stream(ob_file_path)

        for _, row in ob_stream.rows:
            try:
                ob_id = parse_int(row[ObColumn.ID])
                if ob_id == 0:
                    continue
                ob_type = parse_int(row[ObColumn.TYPE])
                ob_upgrade = parse_int(row[ObColumn.UPGRADE])

                if ob_type != 0 and ob_upgrade != 0:
                    valid_ob_upgrade_ids.add(ob_upgrade)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                continue

        logger.info("  Cache built with %d valid TOE(OB) upgrade IDs.",
                    len(valid_ob_upgrade_ids))
        return valid_ob_upgrade_ids

    except FileNotFoundError:
        logger.error("_ob csv file not found: %s", ob_file_path)
        return set()


@cache
def get_valid_ground_elem_ids(ground_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid ground element WIDs from the _ground CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_elem_ids: Set[int] = set()
    file_name = os.path.basename(ground_file_path)
    logger.info("Building valid ground element ID cache from '%s'...",
                file_name)

    try:
        # Use list generator to handle duplicate 'id' column names safely
        gnd_stream = get_csv_list_stream(ground_file_path)

        for _, row in gnd_stream.rows:
            try:
                # Access by index to avoid duplicate header issues
                wid = parse_int(row[GroundColumn.ID])
                if wid == 0:
                    continue
                ground_type = parse_int(row[GroundColumn.TYPE])
                if ground_type != 0:
                    valid_elem_ids.add(wid)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                continue

        logger.info("  Cache built with %d valid WIDs.", len(valid_elem_ids))
        return valid_elem_ids

    except FileNotFoundError:
        logger.error("_ground.csv file not found:'%s'", ground_file_path)
        return set()


def get_valid_unit_ids(unit_file_path: str,
                       active_only: bool = False) -> set[int]:
    """
    Extracts a set of valid unit IDs from a _unit.csv file.

    Args:
        unit_file_path: Path to the _unit.csv file.
        active_only: If True, only returns IDs for units where type != 0.

    Returns:
        A set of valid integer unit IDs.
    """
    valid_ids: set[int] = set()

    try:
        # start=2 accounts for WiTE2 headers
        unit_stream = get_csv_dict_stream(unit_file_path, 2)

        for _, row in unit_stream.rows:
            uid = parse_int(row.get("id"))

            # If filtering by active, skip Type 0 units
            if active_only:
                utype = parse_int(row.get("type"))
                if utype == 0:
                    continue

            if uid != 0:
                valid_ids.add(uid)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        logger.exception("Could not retrieve unit IDs from %s: %s",
                         unit_file_path, e)

    return valid_ids
