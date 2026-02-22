"""
Module for conditionally modifying the number of squads in WiTE2 _unit CSV
files. This module safely handles file updates by writing to a temporary file
first via the `process_csv_in_place` base wrapper.

This module provides functionality to parse a War in the East 2 (WiTE2) _unit
CSV file, locate specific units based on their Order of Battle ID (ob_id), and
modify the squad count for specific Ground Elements within those units. The
update is conditional; it will only replace the squad count if the existing
count matches the specified 'old' value.

The module safely handles file updates by writing to a temporary file first
before replacing the original file, and it includes logging for auditability.

Command Line Usage:
    python -m wite2_tools.cli mod-update-num [-h] target_ob_id target_wid \
        old_num_squads new_num_squads

Arguments:
    target_ob_id (int):   Target unit's TOE(OB) ID (Order of Battle ID).
    target_wid (int):     Unit's Element WID containing the squads to change.
    old_num_squads (int): The exact number of existing squads required to
                          trigger the update.
    new_num_squads (int): Number of new squads to set.

Example:
    $ python -m wite2_tools.cli mod-update-num 42 105 10 12

    This will scan for units with ob_id 42, look for wid 105, and if its
    current squad count is exactly 10, update it to 12.
"""

import os

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import parse_int

# Initialize the logger for this specific module
log = get_logger(__name__)


def modify_unit_num_squads(unit_file_path: str,
                           target_ob_id: int,
                           target_wid: int,
                           old_num_squads: int,
                           new_num_squads: int) -> int:
    """
    Modifies the number of specific Ground Element squads within a WiTE2 _unit
    CSV file.

    Args:
        unit_file_path (str): The path to the WiTE2 _unit CSV file.
        target_uid (int): The identifier ('id' column) of the UNIT to
                modify.
        target_wid (int): The WID of the Ground Element to update.
        old_num_squads (int):
        new_num_squads (int): The new quantity of squads to set.

    Returns:
        int: The total number of rows successfully updated.

    1. Scans the _unit CSV file for rows where 'type' == target_ob_id
      (TOE(OD)).
    2. Scans the row for 'sqd.u' == wid (WID).
    3. Finds the corresponding 'sqd.num' column.
    4. CHECKS if the value in 'sqd.num' == 'old_num_squads'.
    5. If it matches, REPLACES it with 'new_num_squads'.
    """

    log.info("Starting update on '%s' (Target TOE(ID): %d, Target WID: %d)",
             os.path.basename(unit_file_path), target_ob_id, target_wid)

    # Define the specific logic for processing a Unit row
    def process_row(row: dict, _: int) -> tuple[dict, bool]:
        was_modified = False
        uid: int = parse_int(row.get('id'), 0)
        # _unit.'type' maps to _ob.id
        utype: int = parse_int(row.get('type'), 0)

        # 1. Check ob_id
        if utype == target_ob_id:
            # 2. Check sqd.u0 through sqd.u31
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col: str = f"sqd.u{i}"
                sqd_num_col: str = f"sqd.num{i}"

                # 3. If wid matches
                wid: int = parse_int(row.get(sqd_id_col), 0)
                if wid == target_wid:
                    num_squads: int = parse_int(row.get(sqd_num_col), 0)

                    # 4. CONDITIONAL CHECK: Does it equal the exact old amount?
                    if num_squads == old_num_squads:
                        # 5. UPDATE VALUE
                        row[sqd_num_col] = str(new_num_squads)
                        was_modified = True
                        log.info("Unit ID %d: Updated WID %s from %d to %d",
                                 uid, sqd_num_col,
                                 old_num_squads, new_num_squads)
                    else:
                        log.debug("Unit ID %d: WID match at %s, but %s was "
                                  "%d (Expected '%d')",
                                  uid, sqd_id_col, sqd_num_col,
                                  num_squads, old_num_squads)

        return row, was_modified

    # Execute via the shared wrapper
    total_updates = process_csv_in_place(unit_file_path, process_row)
    log.info("Finished. Total rows modified: %d", total_updates)
    print(f"Success! {total_updates} row(s) updated.")
    return total_updates
