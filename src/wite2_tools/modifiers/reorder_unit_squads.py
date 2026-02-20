"""
Unit Squad Reordering Utility
=============================

This module provides functionality to manipulate and reorder ground element
squads within a War in the East 2 (WiTE2) unit data file. It is designed to
modify the internal slot allocation of units by moving specific Ground Elements
to designated indices (0-31) while preserving data integrity for associated attributes.

Key Features
------------
* **Atomic Operations**: Uses temporary files and atomic replacement to ensure
    the original CSV is not corrupted if an error occurs during processing.
* **Comprehensive Shifting**: When a squad is moved, all associated data columns
    (number, disruption, damage, fatigue, fired state, experience, and accumulation)
    are moved synchronously to maintain data alignment.
* **Memory Efficient**: Utilizes generator-based streaming to process large
    game data files without loading the entire dataset into memory.

CLI Usage
---------
This module can be executed directly from the command line:

    $ python -m wite2_tools.cli reorder-unit [target_unit_id] [ge_id] [move_to_index]

Arguments:
    target_unit_id : The ID of the unit to modify.
    ge_id          : The ID of the ground element to search for and move.
    move_to_index  : The target slot index (0-31) to place the element.

Functions
---------
* `reorder_unit_squads`: The main entry point for file I/O and processing logic.
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
from wite2_tools.utils.logger import get_logger
from wite2_tools.modifiers.base import process_csv_in_place

# Initialize the logger for this specific module
log = get_logger(__name__)

def reorder_unit_elems(row: dict, move_from: int, move_to: int) -> dict:
    """
    Moves elements at 'move_from' to 'move_to' and shifts others for all 8 associated unit columns.
    """

    for prefix in UNIT_SQUAD_PREFIXES:
        keys = [f"{prefix}{i}" for i in range(MAX_SQUAD_SLOTS)]
        vals = [row[k] for k in keys]
        vals.insert(move_to, vals.pop(move_from))
        for i in range(MAX_SQUAD_SLOTS):
            row[keys[i]] = vals[i]

    return row


def reorder_unit_squads(unit_file_path: str, target_unit_id: int, ge_id: int, move_to: int) -> int:
    """
    Reorders specific Ground Element squads within a WiTE2 _unit CSV file.

    This function scans a large _unit CSV for a specific target_unit_id, searches its squad
    slots (sqd 0 through sqd 31) for a target ge_id, and moves that squad to a new slot
    index using a temporary file stream to maintain memory efficiency.

    Args:
        unit_file_path (str): The absolute or relative path to the WiTE2 _unit CSV file.
        target_unit_id (int): The unique identifier ('id' column) of the UNIT to be modified.
        ge_id (int): The WID of the Ground Element to be moved.
        move_to (int): The target slot index (0-31) where the element should be relocated.

    Returns:
        int: The total number of rows (OBs) successfully updated. Returns 0 if
             no matches were found or if an error occurred.

    Note:
        - Uses a generator-based streaming approach to handle very large CSV files.
        - Employs a temporary file and atomic replacement (`os.replace`) to prevent
          data loss during the write process.
        - Compatible with `csv.reader` (list-based) to safely handle files that
          may contain duplicate column headers.
    """
    if not (MIN_SQUAD_SLOTS <= move_to < MAX_SQUAD_SLOTS):
        log.error("Validation Error: move_to slot %d is out of bounds (0-31).", move_to)
        return 0

    target_unit_id_str = str(target_unit_id)
    ge_id_str = str(ge_id)
    file_name = os.path.basename(unit_file_path)
    log.info("Reordering squads in '%s' | UNIT ID: %s | GE ID: %s | To Loc: %d",
             file_name, target_unit_id_str, ge_id_str, move_to)

    def process_row(row: dict, row_idx: int) -> tuple[dict, bool]:
        unit_id = row.get("id", "0")
        if target_unit_id_str == str(unit_id):
            for i in range(MAX_SQUAD_SLOTS):
                current_sqd_col = f"sqd.u{i}"
                if current_sqd_col in row and row[current_sqd_col] == ge_id_str:
                    if i != move_to:
                        row = reorder_unit_elems(row, i, move_to)
                        log.debug("Row %d: Moved squad from slot %d to %d", row_idx, i, move_to)
                        return row, True
                    break
        return row, False

    return process_csv_in_place(unit_file_path, process_row)


