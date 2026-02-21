"""
Module for conditionally updating the number of squads in WiTE2 _unit CSV
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
    python -m wite2_tools.cli update-num [-h] ob_id wid old_num_squads
    new_num_squads

Arguments:
    ob_id (int): Target unit's TOE(OB) ID (Order of Battle ID). wid (int):
    Unit's Element WID containing the squads to change. old_num_squads (int):
    The exact number of existing squads required to trigger the update.
    new_num_squads (int): Number of new squads to set.

Example:
    $ python -m wite2_tools.cli update-num 42 105 10 12 This will scan for
    units with ob_id 42, look for wid 105, and if its current squad count is
    exactly 10, update it to 12.
"""

import os

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.utils.logger import get_logger

# Initialize the logger for this specific module
log = get_logger(__name__)


def update_unit_num_squads(unit_file_path: str, target_ob_id: int, wid: int,
                           old_num_squads: int, new_num_squads: int) -> int:
    """
    1. Scans the _unit CSV file for rows where 'type' == target_ob_id
      (TOE(OD)).
    2. Scans the row for 'sqd.u' == wid (WID).
    3. Finds the corresponding 'sqd.num' column.
    4. CHECKS if the value in 'sqd.num' == 'old_num_squads'.
    5. If it matches, REPLACES it with 'new_num_squads'.
    """

    # Convert all inputs to strings for consistent CSV comparison
    ge_id_str = str(wid)
    old_num_squad_str = str(old_num_squads)
    new_num_squad_str = str(new_num_squads)

    log.info("Starting update on '%s' (Target TOE(ID): %d, WID: %d)",
             os.path.basename(unit_file_path), target_ob_id, wid)

    # Define the specific logic for processing a Unit row
    def process_row(row: dict, _: int) -> tuple[dict, bool]:
        was_modified = False
        unit_id = int(row.get('id') or '0')
        unit_type = int(row.get('type') or '0')  # unit 'type' maps to TOE(OB)

        # 1. Check ob_id
        if unit_type == target_ob_id:
            # 2. Check sqd.u0 through sqd.u31
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col = f"sqd.u{i}"
                sqd_num_col = f"sqd.num{i}"

                # 3. If wid matches
                if row.get(sqd_id_col, "0") == ge_id_str:
                    num_squads_val = row.get(sqd_num_col, "0")

                    # 4. CONDITIONAL CHECK: Does it equal the exact old amount?
                    if num_squads_val == old_num_squad_str:
                        # 5. UPDATE VALUE
                        row[sqd_num_col] = new_num_squad_str
                        was_modified = True
                        log.info("Unit ID %d: Updated WID %s from '%s' to "
                                 "'%s'",
                                 unit_id, sqd_num_col, old_num_squad_str,
                                 new_num_squad_str)
                    else:
                        log.debug("Unit ID %d: WID match at %s, but %s was "
                                  "'%s' (Expected '%s')",
                                  unit_id, sqd_id_col, sqd_num_col,
                                  num_squads_val, old_num_squad_str)

        return row, was_modified

    # Execute via the shared wrapper
    total_updates = process_csv_in_place(unit_file_path, process_row)
    log.info("Finished. Total rows modified: %d", total_updates)
    print(f"Success! {total_updates} row(s) updated.")
    return total_updates
