"""
Module for reordering Ground Element squads within WiTE2 Order of Battle (OB) CSV files.

This module provides functionality to parse a War in the East 2 (WiTE2) `_ob` CSV file,
locate a specific OB ID, and modify the internal slot index (0-31) of a targeted
Ground Element. When an element is moved to a new slot index, the remaining elements are automatically
shifted to accommodate the change.

To maintain data integrity, both the squad ID (`sqd X`) and the corresponding squad quantity
(`sqdNum X`) are shifted in perfect synchronization. The script utilizes temporary files to
ensure memory efficiency and safe atomic file replacement.

Command Line Usage:
    python reorder_ob_squads.py [-h] target_ob_id ge_id move_to

Arguments:
    target_ob_id (int): The target Order of Battle (OB) ID.
    ge_id (int): The ID of the Ground Element to be moved.
    move_to (int): The destination slot index (0-31) for the targeted element.

Example:
    $ python reorder_ob_squads.py 150 42 0
    This scans for OB ID 150, finds Ground Element 42 within its squad slots,
    and moves it to the very first slot (index 0), shifting other elements down.
"""

import argparse
from wite2_tools.paths import CONF_OB_FULL_PATH
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.utils.logger import get_logger
from wite2_tools.modifiers.base import process_csv_in_place

log = get_logger(__name__)

def reorder_ob_elems(row: dict, squad_col: str, squad_num_col: str, move_from: int, move_to: int) -> dict:
    """
    Reorders values for two sets of numbered columns.
    """
    squad_keys = [f"{squad_col}{i}" for i in range(MAX_SQUAD_SLOTS)]
    num_keys = [f"{squad_num_col}{i}" for i in range(MAX_SQUAD_SLOTS)]

    squad_vals = [row[k] for k in squad_keys]
    num_vals = [row[k] for k in num_keys]

    squad_vals.insert(move_to, squad_vals.pop(move_from))
    num_vals.insert(move_to, num_vals.pop(move_from))

    for i in range(MAX_SQUAD_SLOTS):
        row[squad_keys[i]] = squad_vals[i]
        row[num_keys[i]] = num_vals[i]

    return row

def reorder_ob_squads(ob_file_path: str, target_ob_id: int, ge_id: int, move_to: int) -> int:
    """
    Reorders specific Ground Element squads within a WiTE2 OB (Order of Battle) CSV file.

    This function scans a large _ob CSV for a specific OB ID, searches its squad slots
    (sqd 0 through sqd 31) for a target Ground Element ID, and moves that squad
    to a new slot index using a temporary file stream to maintain memory efficiency.

    Args:
        ob_file_path (str): The absolute to the WiTE2 _ob CSV file.
        target_ob_id (int): The unique identifier ('id' column) of the OB to be modified.
        ge_id (int): The ID of the Ground Element to be moved.
        move_to (int): The target slot index (0-31) where the element should be relocated.

    Returns:
        int: The total number of rows (OBs) successfully updated.
             Returns 0 if no matches were found or if an error occurred.

    Note:
        - Uses a generator-based streaming approach to handle very large CSV files.
        - Employs a temporary file and atomic replacement (`os.replace`) to prevent
          data loss during the write process.
        - Compatible with `csv.reader` (list-based) to safely handle files that
          may contain duplicate column headers.
    """
    if not (0 <= move_to <= 31):
        log.error("Validation Error: move_to index %d is out of bounds (0-31).", move_to)
        return 0

    ge_id_str = str(ge_id)
    log.info("Reordering squads in '%s' | ob_id: %d | Target ID: %s | To Loc: %d",
             ob_file_path, target_ob_id, ge_id_str, move_to)

    # Define the specific logic for processing an OB row
    def process_row(row: dict, row_idx: int) -> tuple[dict, bool]:
        ob_id = int(row.get("id", "0"))
        if target_ob_id == ob_id:
            for i in range(MAX_SQUAD_SLOTS):
                current_sqd_col = f"sqd {i}"
                if current_sqd_col in row and row[current_sqd_col] == ge_id_str:
                    if i != move_to:
                        row = reorder_ob_elems(row, "sqd ", "sqdNum ", i, move_to)
                        log.debug("Row %d: Moved squad from index %d to %d", row_idx, i, move_to)
                        return row, True  # Row was modified
                    break
        return row, False # Row was untouched

    # Execute via the shared wrapper
    return process_csv_in_place(ob_file_path, process_row)


# --- MAIN EXECUTION ---
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reorders the OB elements by performing a move and shift-down of the squad elements")
    parser.add_argument("ob_id", type=int, help="WiTE2 OB ID")
    parser.add_argument("ge_id", type=int, help="The WID of the Ground Element to be moved")
    parser.add_argument("move_to", type=int, help="Destination Location (0-31) of where to move the target element")

    args = parser.parse_args()

# the following uses the currently configured path values.
    reorder_ob_squads(CONF_OB_FULL_PATH, args.ob_id, args.ge_id, args.move_to)
