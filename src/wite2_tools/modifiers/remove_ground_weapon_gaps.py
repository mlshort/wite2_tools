"""
Ground Element Weapon Compaction Modifier
=========================================

Scans and processes WiTE2 `_ground.csv` files to identify and eliminate
gaps in weapon slots. It compacts the data by shifting valid weapons
leftwards (towards index 0) to ensure contiguous weapon assignments.

If a Ground Element has empty weapon slots (e.g., slot 0 is empty,
but slot 1 has a weapon), this script will shift the active weapons "up" to
fill the gaps, ensuring they are sequentially packed starting from slot 0.

Changes are applied in-place using the standard atomic replacement wrapper
to guarantee file integrity during the transformation process.
Ground Element Weapon Compacting Utility


It synchronizes all 6 weapon attributes during the shift:
    - wpn (ID)
    - wpnNum (Quantity)
    - wpnAmmo (Ammo)
    - wpnRof (Rate of Fire)
    - wpnAcc (Accuracy)
    - wpnFace (Facing)

Command Line Usage:
    python -m wite2_tools.cli mod-compact-wpn [-d DATA_DIR]

Example:
    $ python -m wite2_tools.cli mod-compact-wpn Scans the default _ground.csv
    file and shifts weapons left/up to compact any empty slots.
"""
from typing import Tuple, List, Any
import os

# Internal package imports
from wite2_tools.utils import get_logger
from wite2_tools.utils import parse_int
from wite2_tools.modifiers.base import process_csv_in_place
from wite2_tools.models import (
    GndColumn,
    G_WPN_SLOTS
)

# Initialize the log for this specific module
log = get_logger(__name__)


def remove_ground_weapon_gaps(ground_file_path: str) -> int:
    """
    Scans the _ground CSV file, identifies rows with gaps in their weapon
    slots, and shifts valid weapons left/up to fill those gaps.

    Args:
        ground_file_path (str): The absolute or relative path to the WiTE2
            _ground CSV file.

    Returns:
        int: The total number of Ground Elements that had their weapon slots
            compacted.
    """
    if not os.path.isfile(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return -1

    log.info("Task Start: Compacting empty weapon slots in '%s'",
             os.path.basename(ground_file_path))

    # Aliasing Enum values to integers for performance and readability
    # Define the 5 attribute blocks associated with Ground Weapons
    # These represent the 'starting' column for each 6-slot block
    # pylint: disable=invalid-name
    WPN_BASES: List[int] = [
        GndColumn.WPN_0,
        GndColumn.WPN_NUM_0,
        GndColumn.WPN_AMMO_0,
        GndColumn.WPN_ROF_0,
        GndColumn.WPN_ACC_0,
        GndColumn.WPN_FACE_0
    ]

    # pylint: disable=invalid-name
    ID_COL: int = GndColumn.ID

    def process_row(row: List[str], row_idx: int) -> Tuple[List[str], bool]:
        # Skip header
        if row_idx == 0:
            return row, False

        valid_packets: List[List[Any]] = []
        original_wpn_ids: List[int] = []

        # 1. EXTRACT: Gather valid weapon "packets"
        # The weapon ID is always the first base in our list
        wpn_id_base: int = WPN_BASES[0]

        for i in range(G_WPN_SLOTS):
            # Direct index access instead of .get()
            wid_val: str = row[wpn_id_base + i]
            wid: int = parse_int(wid_val)
            original_wpn_ids.append(wid)

            if wid != 0:
                # Create a packet: [ID, Num, Facing, Type, Traverse] for slot i
                packet: List[str] = [row[base + i] for base in WPN_BASES]
                valid_packets.append(packet)

        # 2. CHECK: Compare layouts to see if a shift is actually needed
        # Reconstruct what the layout SHOULD look like if compacted
        new_wpn_ids: List[int] = (
            [parse_int(p[0]) for p in valid_packets] +
            [0] * (G_WPN_SLOTS - len(valid_packets))
        )

        if original_wpn_ids == new_wpn_ids:
            return row, False

        # 3. REWRITE: Write valid packets back and zero out the rest
        for i in range(G_WPN_SLOTS):
            if i < len(valid_packets):
                # Unpack the saved packet into the specific slot i across all 5 blocks
                for attr_idx, base in enumerate(WPN_BASES):
                    row[base + i] = valid_packets[i][attr_idx]
            else:
                # No more valid weapons; fill remaining slots with string "0"
                for base in WPN_BASES:
                    row[base + i] = "0"

        # Restore your original debug log using index-based ID lookup
        log.debug("Row %d ID[%s]: Shifted weapons. Old Layout: %s -> New Layout: %s",
                  row_idx, row[ID_COL], original_wpn_ids, new_wpn_ids)

        return row, True

    # 4. EXECUTE & SUMMARY
    # process_csv_in_place is expected to handle the List Stream logic
    updates: int = process_csv_in_place(ground_file_path, process_row)

    log.info("Finished. Total Ground Elements compacted: %d", updates)
    print(f"Success! {updates} Ground Elements had their weapon slots compacted.")

    return updates
