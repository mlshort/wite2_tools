"""
Ground Element Weapon Compacting Utility
======================================

This module scans a WiTE2 `_ground.csv` file and consolidates the weapon loadouts.
If a Ground Element has empty weapon slots (e.g., slot 0 is empty, but slot 1 has a weapon),
this script will shift the active weapons "up" to fill the gaps, ensuring they are sequentially
packed starting from slot 0.

It synchronizes all 6 weapon attributes during the shift:
- wpn (ID)
- wpnNum (Quantity)
- wpnAmmo (Ammo)
- wpnRof (Rate of Fire)
- wpnAcc (Accuracy)
- wpnFace (Facing)

Command Line Usage:
    python -m wite2_tools.cli compact-weapons [--ground-file FILE]

Example:
    $ python -m wite2_tools.cli compact-weapons
    Scans the default _ground.csv file and shifts weapons left/up to compact any empty slots.
"""
from typing import Tuple
import os

# Internal package imports
from wite2_tools.constants import GROUND_WPN_PREFIXES, MAX_WPN_SLOTS
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.utils.logger import get_logger

# Initialize the log for this specific module
log = get_logger(__name__)

def remove_ground_weapon_gaps(ground_file_path: str) -> int:
    """
    Scans the _ground CSV file, identifies rows with gaps in their weapon slots,
    and shifts valid weapons left/up to fill those gaps.
    """

    log.info("Task Start: Compacting empty weapon slots in '%s'",
             os.path.basename(ground_file_path))

    def process_row(row: dict, row_idx: int) -> Tuple[dict, bool]:
        valid_weapons = []
        original_wpn_ids = []

        # 1. EXTRACT: Gather all weapons and their associated stats
        for i in range(MAX_WPN_SLOTS):
            wpn_key = f"wpn {i}"
            wpn_id = row.get(wpn_key, "0").strip()
            original_wpn_ids.append(wpn_id)

            # If the slot is NOT empty (0 or blank)
            if wpn_id != "0" and wpn_id != "":
                # Group all stats for this weapon into a dictionary packet
                weapon_data = {p: row.get(f"{p}{i}", "0") for p in GROUND_WPN_PREFIXES}
                valid_weapons.append(weapon_data)

        # 2. CHECK: Did we actually find any gaps?
        # (e.g. valid weapons exist, but aren't packed at the front)
        was_modified = False
        new_wpn_ids = []

        # 3. REWRITE: Write the compacted weapons back starting from index 0
        for i in range(10):
            if i < len(valid_weapons):
                # Apply the valid weapon packet to slot i
                for p in GROUND_WPN_PREFIXES:
                    row[f"{p}{i}"] = valid_weapons[i][p]
                new_wpn_ids.append(valid_weapons[i]["wpn "])
            else:
                # Pad remaining slots at the end with "0"
                for p in GROUND_WPN_PREFIXES:
                    row[f"{p}{i}"] = "0"
                new_wpn_ids.append("0")

        # 4. VERIFY: Compare original layout to new layout
        if original_wpn_ids != new_wpn_ids:
            was_modified = True
            log.debug("Row %d (ID %s): Shifted weapons. Old Layout: %s -> New Layout: %s",
                      row_idx, row.get("id", "0"), original_wpn_ids, new_wpn_ids)

        return row, was_modified

    # Execute via the shared atomic wrapper
    updates = process_csv_in_place(ground_file_path, process_row)

    log.info("Finished. Total Ground Elements compacted: %d", updates)
    print(f"Success! {updates} Ground Elements had their weapon slot compacted.")
    return updates
