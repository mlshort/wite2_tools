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

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers import process_csv_in_place
from wite2_tools.utils import (
    get_logger,
    parse_int
)

# Initialize the log for this specific module
log = get_logger(__name__)


def reorder_ob_elems(row: dict, squad_col: str, squad_num_col: str,
                     source_slot: int, target_slot: int) -> dict:
    """
    Moves elements at 'source_slot' to 'target_slot' and shifts others for
    all associated squad columns.

    Args:
        row (dict): The dictionary representing a single CSV row.
        squad_col (str): The column prefix for the element ID.
        squad_num_col (str): The column prefix for the element quantity.
        source_slot (int): The current index of the squad element.
        target_slot (int): The destination index for the squad element.

    Returns:
        dict: The modified row dictionary.
    """
    squad_keys = [f"{squad_col}{i}" for i in range(MAX_SQUAD_SLOTS)]
    num_keys = [f"{squad_num_col}{i}" for i in range(MAX_SQUAD_SLOTS)]

    squad_vals = [row[k] for k in squad_keys]
    num_vals = [row[k] for k in num_keys]

    squad_vals.insert(target_slot, squad_vals.pop(source_slot))
    num_vals.insert(target_slot, num_vals.pop(source_slot))

    for i in range(MAX_SQUAD_SLOTS):
        row[squad_keys[i]] = squad_vals[i]
        row[num_keys[i]] = num_vals[i]

    return row


def reorder_ob_squads(ob_file_path: str,
                      target_ob_id: int,
                      target_wid: int,
                      target_slot: int) -> int:
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
        int: The total number of rows (OBs) successfully updated.
             Returns 0 if no matches were found or if an error occurred.

    Note:
        - Uses a generator-based streaming approach to handle very large CSV
          files.
        - Employs a temporary file and atomic replacement (`os.replace`) to
          prevent data loss during the write process.
        - Compatible with `csv.reader` (list-based) to safely handle files that
          may contain duplicate column headers.
    """
    if not 0 <= target_slot <= 31:
        log.error("Validation Error: target_slot slot index %d is "
                  "out of bounds (0-31).", target_slot)
        return 0

    log.info("Reordering squads in '%s' | TOE(ID): %d | Target WID: %d |"
             " To Slot Loc: %d",
             ob_file_path, target_ob_id, target_wid, target_slot)

    # Define the specific logic for processing an TOE(OB) row
    def process_row(row: dict, _: int) -> tuple[dict, bool]:
        ob_id = parse_int(row.get("id"), 0)
        if target_ob_id == ob_id:
            for i in range(MAX_SQUAD_SLOTS):
                current_sqd_col = f"sqd {i}"

                if current_sqd_col in row:
                    wid = parse_int(row.get(current_sqd_col), 0)

                    if wid == target_wid:
                        if i != target_slot:
                            row = reorder_ob_elems(row, "sqd ",
                                                   "sqdNum ", i,
                                                   target_slot)
                            log.debug("TOE(OB) ID[%d]: Moved squad from"
                                      " slot %d to %d", ob_id, i, target_slot)
                            return row, True  # Row was modified
                        break
        return row, False  # Row was untouched

    # Execute via the shared wrapper
    return process_csv_in_place(ob_file_path, process_row)
