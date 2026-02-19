"""
Global Unit Inventory Counter
=============================

This module scans the active units in a War in the East 2 (WiTE2) scenario
(`_unit.csv`) to tally the total aggregate count of every Ground Element
(equipment type) currently deployed on the map.

Core Features:
--------------
* Scenario Balancing: Calculates exact counts of equipment (e.g., total tanks, artillery)
  across all active units, explicitly ignoring empty or placeholder units (type = 0).
* Nationality Filtering: Can restrict the count to specific nations (e.g., Germany and Italy)
  to analyze faction-specific strength and deployment levels.
* Memory Efficiency: Utilizes a generator-based dictionary reader to process massive
  unit files with minimal memory overhead, sorting the final output for easy review.

Main Functions:
---------------
* count_global_unit_inventory : Executes the scan and returns a dictionary mapping
                                Ground Element IDs to their total quantities.
"""
import os
from collections import defaultdict
from typing import Optional, Union, Iterable, cast

# Internal package imports
from wite2_tools.paths import CONF_UNIT_FULL_PATH, CONF_GROUND_FULL_PATH
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.constants import NatCode
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.get_type_name import get_ground_elem_type_name

# Initialize the logger for this specific module
log = get_logger(__name__)

def count_global_unit_inventory(
    unit_file_path: str,
    ground_file_path: str,
    nat_code: Optional[Union[int, str, Iterable[Union[int, str]]]] = None
) -> dict[int, int]:
    """
    Scans _unit.csv using a generator to count the total number of every
    Ground Element active in the scenario.
    """
    # Key: Ground Element ID (int), Value: Total Count (int)
    inventory: dict[int, int] = defaultdict(int)

    # Standardize nat_code to a set for efficient lookup
    if nat_code is not None:
        if isinstance(nat_code, (int, str)):
            nat_filter = {int(nat_code)}
        else:
            nat_filter = {int(n) for n in nat_code}
    else:
        nat_filter = None

    log.info("Starting global inventory count for: '%s'", os.path.basename(unit_file_path))

    # 1. Initialize the generator
    unit_gen = read_csv_dict_generator(unit_file_path)

    # 2. Skip the DictReader object yielded first
    next(unit_gen)

    try:
        # 3. Iterate through the generator items safely
        for item in unit_gen:
            # Cast the yielded item to satisfy static type checkers
            row_idx, row = cast(tuple[int, dict], item)

            unit_type = int(row.get('type','0'))
            unit_nat = int(row.get('nat', '0'))

            if nat_filter is not None and unit_nat not in nat_filter:
                continue
            if unit_type == 0:
                continue

            # Iterate through the MAX_SQUAD_SLOTS potential squad slots (sqd.u0 to sqd.u31)
            for i in range(MAX_SQUAD_SLOTS):
                ground_elem_id_str = row.get(f'sqd.u{i}','0')
                sqd_num_val = row.get(f'sqd.num{i}','0')

                # Check if the slot is occupied (ID is not None, empty, or '0')
                if ground_elem_id_str and ground_elem_id_str != '0':
                    try:
                        ground_elem_id_val = int(ground_elem_id_str)
                        # Default to 0 if the count string is missing or malformed
                        count = int(sqd_num_val) if sqd_num_val else 0

                        # Accumulate the total using defaultdict's auto-initialization
                        inventory[ground_elem_id_val] += count
                    except ValueError:
                        log.warning("Row %s: Malformed data in slot %d (ID: %s, Num: %s)",
                                    row_idx, i, ground_elem_id_str, sqd_num_val)

        # 4. Log the Final Results
        log.info("--- Inventory Audit Complete ---")
        # Sort by count (descending) to see most prevalent elements first
        sorted_inventory = sorted(inventory.items(), key=lambda x: x[1], reverse=True)

        for ground_elem_id_val, total in sorted_inventory:
            if total > 0:
                ground_elem_name_str = get_ground_elem_type_name(ground_file_path, ground_elem_id_val)
                log.info("%s(%d): Total Count = %d", ground_elem_name_str, ground_elem_id_val, total)

    except StopIteration:
        log.error("The _unit file appears to be empty.")
    except (IOError, OSError) as e:
        log.error("An error occurred reading the file: %s", e)

    return inventory

if __name__ == "__main__":
    # Point this to your specific _unit and _ground CSV files
    UNIT_DATA = CONF_UNIT_FULL_PATH
    GROUND_DATA = CONF_GROUND_FULL_PATH

    nat_codes = { NatCode.GER, NatCode.ITA }
    count_global_unit_inventory(UNIT_DATA, GROUND_DATA, nat_codes)
