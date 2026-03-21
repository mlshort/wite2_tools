"""
Unit Ground Element Modifier
========================================
This module provides functionality to parse a War in the East 2 (WiTE2) _unit
CSV file and globally replace all instances of a specific Ground Element WID
with a new ID. It scans through all 32 unit squad slots (`sqd.u0` through
`sqd.u31`) and performs an integer-based comparison to ensure accurate
 replacements.

To maintain data integrity and handle large files efficiently, the script
streams the data using a generator and writes to a temporary file, which
atomically replaces the original file only upon successful completion.

Command Line Usage:
    python -m wite2_tools.cli mod-replace-elem [-h] [-d DATA_DIR] \
        old_wid new_wid

Arguments:
    old_wid (int): The existing Ground Element WID to be replaced.
    new_wid (int): The new Ground Element WID value.
"""
import os

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.utils import get_logger
from wite2_tools.utils import parse_int
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.models import UnitColumn

# Initialize the log for this specific module
log = get_logger(__name__)


def modify_unit_ground_element(unit_file_path: str,
                               old_wid: int,
                               new_wid: int) -> tuple[int,int]:
    """
    Replaces a specific Ground Element WID with a new one across all
    units in a WiTE2 _unit CSV file using integer-based comparison.

    Args:
        unit_file_path (str): The path to the WiTE2 _unit CSV file.
        old_wid (int): The existing Ground Element WID to be replaced.
        new_wid (int): The new Ground Element WID value.

    Returns:
        tuple[int, int]: A tuple containing (total_rows_processed, total_rows_updated).
            Returns (0, 0) if no matches were found or error occurred.

    """

    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0, 0

    log.info("Task Start: Replace WID[%d] with %d in '%s'",
             old_wid, new_wid, os.path.basename(unit_file_path))

    # Define the specific logic for processing a Unit row
    def process_row(row: list[str], _: int) -> tuple[list[str], bool]:
        was_modified = False

        # Check sqd.u0 through sqd.u31
        for i in range(MAX_SQUAD_SLOTS):
            sqd_id_col = UnitColumn.SQD_U0 + (i * 8)

            # BOUNDARY CHECK: Ensure the row is long enough before accessing!
            if sqd_id_col < len(row) :
                wid = parse_int(row[sqd_id_col])

                if wid != 0:
                    try:
                        # Treat values as integers for comparison
                        if wid == old_wid:
                            row[sqd_id_col] = str(new_wid)
                            was_modified = True
                    except ValueError:
                        continue

        return row, was_modified

    # Execute via the shared wrapper
    processed, updated = process_csv_in_place(unit_file_path, process_row)
    log.info("Task Complete: Rows processed: %d, Rows Modified: %d containing the old WID[%d] to "
             "the new WID[%d].",
             processed,
             updated, old_wid, new_wid)

    return processed, updated
