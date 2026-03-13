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
from typing import Set, Final
from functools import cache

# Internal package imports
from wite2_tools.models import (
    O_ID_COL, O_TYPE_COL, O_UPGRADE_COL,
    G_ID_COL, G_TYPE_COL,
    U_ID_COL, U_TYPE_COL
)

from wite2_tools.generator import (
    CSVListStream,
    get_csv_list_stream
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import parse_row_int

# Initialize the log for this specific module
log = get_logger(__name__)


@cache
def get_valid_ob_ids(ob_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid TOE(OB) IDs from the _ob CSV.
    The @cache decorator ensures this function only runs once per
    unique file path!
    """
    valid_ob_ids: Set[int] = set()
    file_name = os.path.basename(ob_file_path)
    log.info("Building valid TOE(OB) ID cache from '%s'...", file_name)

    try:
        ob_stream = get_csv_list_stream(ob_file_path)

        for idx, row in ob_stream.rows:

            try:
                ob_id = parse_row_int(row, O_ID_COL)  # 'id' column
                ob_type = parse_row_int(row, O_TYPE_COL)  # 'type' column
                if ob_id != 0 and ob_type != 0:
                    valid_ob_ids.add(ob_id)
            except (ValueError, IndexError):
                log.debug("Skipping malformed row at index %d", idx)
                continue

        log.info("  Cache built with %d valid TOE(OB) IDs.",
                    len(valid_ob_ids))
        return valid_ob_ids

    except FileNotFoundError:
        log.error("_ob csv file not found:'%s'", ob_file_path)
        return set()

    except (OSError, IOError) as e:
        log.exception("File System Error: Could not read %s: %s",
                         ob_file_path, e)
        return set()


@cache
def get_valid_ob_upgrade_ids(ob_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid upgrade IDs from the _ob CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_ob_upgrade_ids: Set[int] = set()
    log.info("Building valid TOE(OB) upgrade ID cache from '%s'...",
                ob_file_path)

    try:
        ob_stream: CSVListStream = get_csv_list_stream(ob_file_path)

        for idx, row in ob_stream.rows:

            try:
                ob_id: int = parse_row_int(row, O_ID_COL)
                # Skip invalid IDs
                if ob_id == 0:
                    continue
                ob_type: int = parse_row_int(row, O_TYPE_COL)
                ob_upgrade: int = parse_row_int(row, O_UPGRADE_COL)

                if ob_type != 0 and ob_upgrade != 0:
                    valid_ob_upgrade_ids.add(ob_upgrade)

            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                log.debug("Skipping malformed row at index %d", idx)
                continue

        log.info("  Cache built with %d valid TOE(OB) upgrade IDs.",
                    len(valid_ob_upgrade_ids))
        return valid_ob_upgrade_ids

    except FileNotFoundError:
        log.error("_ob csv file not found: %s", ob_file_path)
        return set()

    except (OSError, IOError) as e:
        log.exception("File System Error: Could not read %s: %s",
                         ob_file_path, e)
        return set()


@cache
def get_valid_ground_elem_ids(ground_file_path: str) -> Set[int]:
    """
    Builds and returns a set of valid ground element WIDs from the _ground CSV.
    Caches the result to avoid repeated file I/O.
    """
    valid_elem_ids: Set[int] = set()
    file_name: str = os.path.basename(ground_file_path)
    log.info("Building valid ground element ID cache from '%s'...",
                file_name)

    # The minimum number of columns required to process this row
    # pylint: disable=invalid-name
    MIN_REQUIRED_COLS: Final[int] = max(G_ID_COL, G_TYPE_COL) + 1
    try:
        # Use list generator to handle duplicate 'id' column names safely
        gnd_stream: CSVListStream = get_csv_list_stream(ground_file_path)

        for idx, row in gnd_stream.rows:

            # 2. Defensive check: Skip rows that are too short for our indices
            if len(row) < MIN_REQUIRED_COLS:
                # Log only on debug to avoid flooding the console for empty lines
                log.debug("Skipping malformed row %d: insufficient columns.", idx)
                continue

            try:
                # Access by index to avoid duplicate header issues
                wid = parse_row_int(row, G_ID_COL)
                if wid == 0:
                    continue
                ground_type = parse_row_int(row, G_TYPE_COL)
                if ground_type != 0:
                    valid_elem_ids.add(wid)
            except (ValueError, IndexError):
                # Skip malformed rows or empty lines
                log.debug("Skipping malformed row at index %d", idx)
                continue

        log.info("  Cache built with %d valid WIDs.", len(valid_elem_ids))
        return valid_elem_ids

    except FileNotFoundError:
        log.error("_ground.csv file not found:'%s'", ground_file_path)
        return set()

    except (OSError, IOError) as e:
        log.exception("File System Error: Could not read %s: %s",
                         ground_file_path, e)
        return set()

@cache
def get_valid_unit_ids(unit_file_path: str,
                       active_only: bool = False) -> Set[int]:
    """
    Extracts a set of valid unit IDs from a _unit.csv file.

    Args:
        unit_file_path: Path to the _unit.csv file.
        active_only: If True, only returns IDs for units where type != 0.

    Returns:
        A set of valid integer unit IDs.
    """
    valid_ids: Set[int] = set()

    # The minimum number of columns required to process this row
    # pylint: disable=invalid-name
    MIN_REQUIRED_COLS: Final[int] = max(U_ID_COL, U_TYPE_COL) + 1

    try:
        unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

        for idx, row in unit_stream.rows:

            # 2. Defensive check: Skip rows that are too short for our indices
            if len(row) < MIN_REQUIRED_COLS:
                # Log only on debug to avoid flooding the console for empty lines
                log.debug("Skipping malformed row %d: insufficient columns.", idx)
                continue
            try:
                uid: int = parse_row_int(row, U_ID_COL)

                # If filtering by active, skip Type 0 units
                if active_only:
                    utype: int = parse_row_int(row, U_TYPE_COL)
                    if utype == 0:
                        continue

                if uid != 0:
                    valid_ids.add(uid)

            except (ValueError, TypeError) as e:
                # This catches cases where data exists but isn't a valid number
                log.warning("Row %d: Failed to parse ID or Type. Error: %s",
                            idx, e)
                continue

    except IndexError as e:
        # This catches any structural index issues not caught by the length check
        log.exception("Structural Error: Index out of bounds in %s: %s",
                      unit_file_path, e)

    except FileNotFoundError:
        log.error("_ground.csv file not found:'%s'", unit_file_path)

    except (OSError, IOError) as e:
        log.exception("File System Error: Could not read %s: %s",
                         unit_file_path, e)

    return valid_ids
