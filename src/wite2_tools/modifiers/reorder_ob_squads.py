"""
Module for reordering Ground Element squads within WiTE2 Order of Battle
TOE(OB) CSV files.

This module provides functionality to parse a War in the East 2 (WiTE2) `_ob`
CSV file, locate a specific TOE(OB) ID, and modify the internal slot index
(0-31) of a targeted Ground Element. When an element is moved to a new slot
index, the remaining elements are automatically shifted to accommodate the
change.

To maintain data integrity, both the squad ID (`sqd X`) and the corresponding
squad quantity (`sqdNum X`) are shifted in perfect synchronization. The script
utilizes temporary files to ensure memory efficiency and safe atomic file
replacement.

Command Line Usage:
    python -m wite2_tools.cli mod-mod-reorder-ob [-h] [-d DATA_DIR] \
        target_ob_id target_wid target_slot

Arguments:
    target_ob_id (int): The target Order of Battle TOE(OB) ID.
    target_wid (int):  The WID of the Ground Element to be moved.
    source_slot (int): The current slot index (0-31) of the
                       targeted element.
    target_slot (int): The destination slot index (0-31) for the
                       element.

Example:
    $ python -m wite2_tools.cli mod-mod-reorder-ob -d "C:\\My_Mods" 150 42 0

    This scans the _ob.csv located in "C:\\My_Mods" for TOE(OB) ID 150,
    finds Ground Element 42, and moves it to the very first slot (index 0)

"""
import os

# Internal package imports
from wite2_tools.utils import get_logger
from wite2_tools.modifiers.base import process_csv_in_place

# Import ObColumn so we can use its pure integer indices
from wite2_tools.models import (
    ObRow,
    ObColumn,
    O_SQD_SLOTS
)


# Initialize the log for this specific module
log = get_logger(__name__)


def reorder_ob_squads(ob_file_path: str,
                      target_ob_id: int,
                      target_wid: int,
                      target_slot: int) -> tuple[int,int]:
    """
    Reorders specific Ground Element squads within a WiTE2 TOE(OB) (Order of
    Battle) CSV file.

    This function scans a large _ob CSV for a specific TOE(OB) ID, searches its
    squad slots (sqd 0 through sqd 31) for a target Ground Element WID, and
    moves that squad to a new slot index using a temporary file stream to
    maintain memory efficiency.

    Args:
        ob_file_path (str): The absolute or relative path to the WiTE2 _ob CSV
            file.
        target_ob_id (int): The unique identifier ('id' column) of the
            TOE(OB) to be modified.
        target_wid (int): The WID of the Ground Element to be moved.
        target_slot (int): The target slot index (0-31) where the
            element should be relocated.

    Returns:
        tuple[int, int]: A tuple containing (total_rows_processed, total_rows_updated).
            Returns (0, 0) if no matches were found or error occurred.

    Note:
        - Uses a generator-based streaming approach to handle very large CSV
          files.
        - Employs a temporary file and atomic replacement (`os.replace`) to
          prevent data loss during the write process.
        - Compatible with `csv.reader` (list-based) to safely handle files that
          may contain duplicate column headers.
    """

    # Validation
    if not 0 <= target_slot < O_SQD_SLOTS:
        log.error("Validation Error: target_slot index %d is "
                  "out of bounds.", target_slot)
        return 0, 0

    if not os.path.isfile(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0, 0

    log.info("Task Start: Reordering squads in '%s' | TOE(ID): %d | Target WID: %d | To Slot: %d",
             os.path.basename(ob_file_path), target_ob_id, target_wid, target_slot)

    # 1. Define the List-based row processor
    def process_row(row: list[str], row_idx: int) -> tuple[list[str], bool]:
        # Skip header row (row index 0)
        if row_idx == 0:
            return row, False

        ob = ObRow(row)

        try:
            ob_id = ob.ID
        except AttributeError:
            return row, False

        if ob_id == target_ob_id:
            # Grab the exact starting index for the squad block
            sqd_base = ObColumn.SQD_0

            for i in range(O_SQD_SLOTS):
                try:
                    # Direct list access using pure integer offset math
                    wid = int(ob.raw[sqd_base + i])
                except (IndexError, ValueError):
                    continue

                if wid == target_wid:
                    if i != target_slot:
                        # ObRow's method handles shifting elements and updating self.raw
                        ob.reorder_slots(i, target_slot)

                        log.debug("TOE(OB) ID[%d]: Moved squad from slot %d to %d",
                                  ob_id, i, target_slot)
                        # Return the modified underlying list
                        return ob.raw, True
                    break # Found the WID but it's already in the target slot

        return row, False

    # 2. Execute via the shared list-stream wrapper
    processed, updated = process_csv_in_place(ob_file_path, process_row)

    log.info("Task Complete: Rows processed: %d, Rows Modified: %d moving the WID[%d] to "
             "the new slot [%d].",
             processed,
             updated, target_wid, target_slot)

    return processed, updated