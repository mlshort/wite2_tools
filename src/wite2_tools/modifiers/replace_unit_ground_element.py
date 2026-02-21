"""
Module for replacing specific Ground Element WIDs across WiTE2 _unit CSV files.
This module uses the base `process_csv_in_place` wrapper to safely perform
atomic file replacements.

This module provides functionality to parse a War in the East 2 (WiTE2) unit
CSV file and globally replace all instances of a specific Ground Element WID
with a new ID. It scans through all 32 unit squad slots (`sqd.u0` through
`sqd.u31`) and performs an integer-based comparison to ensure accurate
 replacements.

To maintain data integrity and handle large files efficiently, the script
streams the data using a generator and writes to a temporary file, which
atomically replaces the original file only upon successful completion.

Command Line Usage:
    python -m wite2_tools.cli replace-elem [-h] old_ge_id new_ge_id

Arguments:
    old_ge_id (int): The existing Ground Element WID to be replaced.
    new_ge_id (int): The new Ground Element WID to insert.

Example:
    $ python -m wite2_tools.cli replace-elem 105 110
    This will scan the unit file and replace every instance of Ground Element
    105 with Ground Element 110 across all squad slots.
"""
import os

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.utils.logger import get_logger

# Initialize the log for this specific module
log = get_logger(__name__)


def replace_unit_ground_element(unit_file_path: str, old_ge_id: int,
                                new_ge_id: int) -> int:
    """
    Replaces a specific Ground Element WID with a new one using integer-based
    comparison.
    """
    log.info("Task Start: Replace GE WID %d with %d in '%s'",
             old_ge_id, new_ge_id, os.path.basename(unit_file_path))

    # Define the specific logic for processing a Unit row
    def process_row(row: dict, _: int) -> tuple[dict, bool]:
        was_modified = False

        # Check sqd.u0 through sqd.u31
        for i in range(MAX_SQUAD_SLOTS):
            sqd_id_col = f"sqd.u{i}"
            ground_elem_id = row.get(sqd_id_col, "0")

            if ground_elem_id:
                try:
                    # Treat values as integers for comparison
                    if int(ground_elem_id) == old_ge_id:
                        row[sqd_id_col] = str(new_ge_id)
                        was_modified = True
                except ValueError:
                    continue

        return row, was_modified

    # Execute via the shared wrapper
    total_updates = process_csv_in_place(unit_file_path, process_row)
    log.info("Task Complete: Modified %d rows containing the old WID %d.",
             total_updates, old_ge_id)
    return total_updates
