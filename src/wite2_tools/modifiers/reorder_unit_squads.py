"""
Unit Squad Reordering Utility
=============================

This module provides functionality to manipulate and reorder ground element
squads within a War in the East 2 (WiTE2) unit data file. It is designed to
modify the internal slot allocation of units by moving specific Ground Elements
to designated indices (0-31) while preserving data integrity for associated
attributes.

Key Features
------------
* **Atomic Operations**: Uses temporary files and atomic replacement to ensure
    the original CSV is not corrupted if an error occurs during processing.
* **Comprehensive Shifting**: When a squad is moved, all associated data
    columns (number, disruption, damage, fatigue, fired state, experience, and
    accumulation) are moved synchronously to maintain data alignment.
* **Memory Efficient**: Utilizes generator-based streaming to process large
    game data files without loading the entire dataset into memory.


CLI Usage
---------
This module can be executed directly from the command line:

    $ python -m wite2_tools.cli mod-reorder-unit [-d DATA_DIR] \\
        target_uid target_wid target_slot

Arguments:
    unit_file_path : The absolute or relative path to the WiTE2
                     _unit CSV file.
    target_uid     : The ID of the unit to modify.
    target_wid     : The ID of the ground element to search for and move.
    target_slot    : The target slot index (0-31) to place the element.

Functions
---------
* `reorder_unit_squads`: The main entry point for file I/O and processing
    logic.
* `reorder_unit_elems`: Helper function that performs the list manipulation
    on the row dictionary.
"""
import os

# Internal package imports
from wite2_tools.constants import (
    MAX_SQUAD_SLOTS,
    MIN_SQUAD_SLOTS,
    UNIT_SQUAD_PREFIXES
)
from wite2_tools.utils import (
    get_logger,
    parse_int
)
from wite2_tools.modifiers.base import process_csv_in_place

# Initialize the logger for this specific module
log = get_logger(__name__)


def reorder_unit_elems(row: dict, source_slot: int, target_slot: int) -> dict:
    """
    Moves elements at 'source_slot' to 'target_slot' and shifts others for
    all 8 associated unit columns.

    Args:
        row (dict): The dictionary representing a single CSV row.
        source_slot (int): The current index of the squad element.
        target_slot (int): The destination index for the squad element.

    Returns:
        dict: The modified row dictionary.
    """""

    for prefix in UNIT_SQUAD_PREFIXES:
        keys = [f"{prefix}{i}" for i in range(MAX_SQUAD_SLOTS)]
        vals = [row[k] for k in keys]
        vals.insert(target_slot, vals.pop(source_slot))
        for i in range(MAX_SQUAD_SLOTS):
            row[keys[i]] = vals[i]

    return row


def reorder_unit_squads(unit_file_path: str,
                        target_uid: int,
                        target_wid: int,
                        target_slot: int) -> int:
    """
    Reorders specific Ground Element squads within a WiTE2 _unit CSV file.

    This function scans a large _unit CSV for a specific target_uid,
    searches its squad slots (sqd 0 through sqd 31) for a target wid, and moves
    that squad to a new slot index using a temporary file stream to maintain
    memory efficiency.

    Args:
        unit_file_path (str): The absolute or relative path to the WiTE2 _unit
                              CSV file.
        target_uid (int): The unique identifier ('id' column) of the UNIT
                           to be modified.
        target_wid (int):  The WID of the Ground Element to be moved.
        target_slot (int): The target slot (0-31) where the element
                           should be relocated.

    Returns:
        int: The total number of rows (OBs) successfully updated. Returns 0 if
             no matches were found or if an error occurred.

    Note:
        - Uses a generator-based streaming approach to handle very large CSV
          files.
        - Employs a temporary file and atomic replacement (`os.replace`) to
          prevent data loss during the write process.
        - Compatible with `csv.reader` (list-based) to safely handle files that
          may contain duplicate column headers.
    """
    if not MIN_SQUAD_SLOTS <= target_slot < MAX_SQUAD_SLOTS:
        log.error("Validation Error: target_slot slot %d is out of bounds "
                  "(0-31).", target_slot)
        return 0

    file_name = os.path.basename(unit_file_path)
    log.info("Reordering squads in '%s' | UNIT ID: %d | WID: %d | To Loc: %d",
             file_name, target_uid, target_wid, target_slot)

    def process_row(row: dict, row_idx: int) -> tuple[dict, bool]:
        uid = parse_int(row.get("id"), 0)
        if target_uid == uid:
            for i in range(MAX_SQUAD_SLOTS):
                current_sqd_col = f"sqd.u{i}"
                if current_sqd_col in row:
                    wid = parse_int(row.get(current_sqd_col), 0)
                    if wid == target_wid:
                        if i != target_slot:
                            row = reorder_unit_elems(row, i, target_slot)
                            log.debug("Row %d: Moved squad from slot %d to %d",
                                      row_idx, i, target_slot)
                            return row, True
                        break
        return row, False

    return process_csv_in_place(unit_file_path, process_row)
