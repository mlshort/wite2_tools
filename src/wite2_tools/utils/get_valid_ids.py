"""
Valid ID Caching & Lookup Utility
=================================

This module provides highly efficient, cached retrieval of valid ID sets for
various entities (Units, OBs, Ground Elements) within War in the East 2 (WiTE2) data.

To optimize performance across bulk auditing and modification scripts, this module
reads the massive CSV files once, extracts the active/valid IDs (explicitly filtering
out empty or zero-type placeholders), and stores them in global memory. Subsequent
calls to these functions perform instant O(1) set lookups instead of triggering
repeated file I/O operations.

Core Features:
--------------
* Memory-Efficient Initialization: Utilizes list-based CSV generators to stream data.
* Global Caching: Prevents redundant parsing operations across the toolset.
* Automatic Data Cleaning: Automatically drops invalid or structural placeholder rows
  (e.g., where 'type' or 'id' equals 0).

Main Functions:
---------------
* get_valid_ob_ids          : Returns a set of all valid Order of Battle TOE(OB) IDs.
* get_valid_ob_upgrade_ids  : Returns a set of all valid TOE(OB) upgrade target IDs.
* get_valid_ground_elem_ids : Returns a set of all active Ground Element WIDs.
* get_valid_unit_ids        : Returns a set of all active Unit IDs deployed in the scenario.
"""
import os
from typing import Set
from functools import cache

# Internal package imports
from wite2_tools.constants import (
    GroundColumn,
    OBColumn,
    UnitColumn
)
from wite2_tools.generator import read_csv_list_generator
from wite2_tools.utils.logger import get_logger

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
        data_gen = read_csv_list_generator(ob_file_path)
        next(data_gen) # Skip header

        for _, row in data_gen:
            try:
                ob_id = int(row[OBColumn.ID]) # 'id' column
                ob_type = int(row[OBColumn.TYPE]) # 'type' column
                if ob_id != 0 and ob_type != 0:
                    valid_ob_ids.add(ob_id)
            except (ValueError, IndexError):
                continue

        logger.info("Cache built with %d valid TOE(OB) IDs.", len(valid_ob_ids))
        return valid_ob_ids

    except FileNotFoundError:
        logger.error("TOE(OB) file not found:'%s'", ob_file_path)
        return set()

@cache
def get_valid_ob_upgrade_ids(ob_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid upgrade IDs from the _ob CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_ob_upgrade_ids: Set[int] = set()
    logger.info("Building valid TOE(OB) upgrade ID cache from '%s'...", ob_file_path)

    try:
        data_gen = read_csv_list_generator(ob_file_path)
        # Skip header
        next(data_gen)

        for _, row in data_gen:
            try:
                ob_id = int(row[OBColumn.ID]) # 'id' column
                if ob_id == 0:
                    continue
                ob_type = int(row[OBColumn.TYPE])   # 'type' column
                ob_upgrade = int(row[OBColumn.UPGRADE]) # 'upgrade' column

                if ob_type != 0 and ob_upgrade != 0:
                    valid_ob_upgrade_ids.add(ob_upgrade)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                continue

        logger.info("Cache built with %d valid TOE(OB) upgrade IDs.", len(valid_ob_upgrade_ids))
        return valid_ob_upgrade_ids

    except FileNotFoundError:
        logger.error("TOE(OB) file not found: %s", ob_file_path)
        return set()



@cache
def get_valid_ground_elem_ids(ground_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid ground element WIDs from the _ground CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_elem_ids: Set[int] = set()
    file_name = os.path.basename(ground_file_path)
    logger.info("Building valid ground element ID cache from '%s'...", file_name)

    try:
        ground_gen = read_csv_list_generator(ground_file_path)
        # Skip header
        next(ground_gen)

        for _, row in ground_gen:
            try:
                # Access by index to avoid duplicate header issues
                ground_elem_id = int(row[GroundColumn.ID])   # 1st 'id' column
                if ground_elem_id == 0:
                    continue
                ground_type = int(row[GroundColumn.TYPE])   # 'type' column
                if ground_type != 0:
                    valid_elem_ids.add(ground_elem_id)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                continue

        logger.info("Cache built with %d valid WIDs.", len(valid_elem_ids))
        return valid_elem_ids

    except FileNotFoundError:
        logger.error("Ground element file not found:'%s'", ground_file_path)
        return set()

@cache
def get_valid_unit_ids(unit_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid unit IDs from the _unit CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_unit_ids: Set[int] = set()
    file_name = os.path.basename(unit_file_path)
    logger.info("Building valid Unit ID cache from '%s'...", file_name)

    try:
        unit_gen = read_csv_list_generator(unit_file_path)
        # Skip header
        next(unit_gen)

        for _, row in unit_gen:
            try:
                # Access by index to avoid duplicate header issues
                unit_id = int(row[UnitColumn.ID])   #  'id' column
                unit_type = int(row[UnitColumn.TYPE])   # 'type' column
                if unit_id == 0:
                    continue

                if unit_type != 0:
                    valid_unit_ids.add(unit_id)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                continue

        logger.info("Cache built with %d valid Unit IDs.", len(valid_unit_ids))
        return valid_unit_ids

    except FileNotFoundError:
        logger.error("Unit file not found: %s", unit_file_path)
        return set()
