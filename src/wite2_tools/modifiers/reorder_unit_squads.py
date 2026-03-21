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
from typing import List

# Internal package imports
from wite2_tools.utils import (
    get_logger,
    parse_int
)
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.models import (
    UnitColumn,
    U_SQD_SLOTS,
    U_ID_COL,
    U_SQD0_COL,
    U_ATTRS_PER_SQD
)

# Initialize the logger for this specific module
log = get_logger(__name__)


def reorder_unit_elems(row: List[str],
                       source_slot: int,
                       target_slot: int) -> List[str]:
    """
    Moves elements at 'source_slot' to 'target_slot' using List indices
    mapped from the UnitColumn IntEnum.

    Args:
        row (list): The list representing a single CSV row.
        source_slot (int): The current offset (0-9).
        target_slot (int): The destination offset (0-9).

    Returns:
        list: The modified row list.
    """
    # Define the starting column for each of the 8 associated attribute blocks
    # We use the '0' index member of each block from the IntEnum
    attribute_bases : List[int] = [
        UnitColumn.SQD_U0,
        UnitColumn.SQD_NUM0,
        UnitColumn.SQD_DIS0,
        UnitColumn.SQD_DAM0,
        UnitColumn.SQD_FAT0,
        UnitColumn.SQD_FIRED0,
        UnitColumn.SQD_EXP0,
        UnitColumn.SQD_EXP_ACCUM0
    ]


    # Calculate the exact starting index for both slots
    source_offset = source_slot * U_ATTRS_PER_SQD
    target_offset = target_slot * U_ATTRS_PER_SQD

    for base_enum in attribute_bases:
        # Move the data
        row[base_enum + target_offset] = row[base_enum + source_offset]
        # Clear the old slot
        row[base_enum + source_offset] = "0"

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
    if not 0 <= target_slot < U_SQD_SLOTS:
        log.error("Validation Error: target_slot slot %d is out of bounds "
                  "(0-31).", target_slot)
        return 0

    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return -1

    file_name = os.path.basename(unit_file_path)
    log.info("Reordering squads in '%s' | UNIT ID: %d | WID: %d | To Loc: %d",
             file_name, target_uid, target_wid, target_slot)



    def process_row(row: List[str], row_idx: int) -> tuple[List[str], bool]:
        uid = parse_int(row[U_ID_COL])
        if target_uid == uid:

            for i in range(U_SQD_SLOTS):
                current_sqd_col = U_SQD0_COL + (i * 8)

                if current_sqd_col < len(row):
                    wid = parse_int(row[current_sqd_col])
                    if wid == target_wid:
                        if i != target_slot:
                            row = reorder_unit_elems(row, i, target_slot)
                            log.debug("Row %d: Moved squad from slot %d to %d",
                                      row_idx, i, target_slot)
                            return row, True
                        break
        return row, False

    return process_csv_in_place(unit_file_path, process_row)
