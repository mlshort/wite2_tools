"""
Global Unit Inventory Counter
=============================

This module scans the active units in a War in the East 2 (WiTE2) scenario
(`_unit.csv`) to tally the total aggregate count of every Ground Element
(equipment type) currently deployed on the map.

Core Features:
--------------
* Scenario Balancing: Calculates exact counts of equipment
  (e.g., total tanks, artillery) across all active units, explicitly
  ignoring empty or placeholder units (type = 0).
* Nationality Filtering: Can restrict the count to specific nations
  (e.g., Germany and Italy) to analyze faction-specific strength and
  deployment levels.
* Memory Efficiency: Utilizes a generator-based dictionary reader to process
  massive unit files with minimal memory overhead, sorting the final output
  for easy review.

Command Line Usage:
    python -m wite2_tools.cli gen-inventory [-h] [-d DATA_DIR] \
        [--nat-codes CODE [CODE ...]]

Arguments:
    nat_codes (list of int, optional): Filter by nationality codes
                                       (e.g., 1 for Germany, 3 for Italy).

Example:
    $ python -m wite2_tools.cli gen-inventory --nat-codes 1

    Calculates the total equipment inventory for all active German (Nat 1)
    units.
"""
import os
from collections import defaultdict
from typing import Optional, Union, Iterable, cast

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import get_logger
from wite2_tools.utils import get_ground_elem_type_name
from wite2_tools.utils import parse_int
from wite2_tools.utils import format_ref

# Initialize the logger for this specific module
log = get_logger(__name__)


def count_global_unit_inventory(
    unit_file_path: str,
    ground_file_path: str,
    nat_codes: Optional[Union[int, str, Iterable[Union[int, str]]]] = None
) -> dict[int, int]:
    """
    Scans _unit.csv using a generator to count the total number of every
    Ground Element active in the scenario.
    """
    # Key: Ground Element WID (int), Value: Total Count (int)
    inventory: dict[int, int] = defaultdict(int)

    # Standardize nation_id to a set for efficient lookup
    if nat_codes is not None:
        if isinstance(nat_codes, (int, str)):
            nat_filter = {int(nat_codes)}
        else:
            nat_filter = {int(n) for n in nat_codes}
    else:
        nat_filter = None

    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return inventory

    if not os.path.exists(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return inventory

    log.info("Starting global inventory count for: '%s'",
             os.path.basename(unit_file_path))

    # 1. Initialize the generator
    unit_gen = read_csv_dict_generator(unit_file_path)

    # 2. Skip the DictReader object yielded first
    next(unit_gen)

    try:
        # 3. Iterate through the generator items safely
        for item in unit_gen:
            # Cast the yielded item to satisfy static type checkers
            _, row = cast(tuple[int, dict], item)
            uid = parse_int(row.get("id"))
            utype = parse_int(row.get("type"))
            u_nat = parse_int(row.get("nat"))

            if nat_filter is not None and u_nat not in nat_filter:
                continue
            if utype == 0:
                continue

            # Iterate through the MAX_SQUAD_SLOTS potential squad slots (sqd.u0
            # to sqd.u31)
            for i in range(MAX_SQUAD_SLOTS):
                wid = parse_int(row.get(f'sqd.u{i}', 0))
                squad_quantity = parse_int(row.get(f'sqd.num{i}', 0))

                # Check if the slot is occupied (WID is not '0')
                if wid != 0:
                    try:
                        # Default to 0 if the count string is missing or
                        # malformed
                        count = squad_quantity if squad_quantity else 0

                        # Accumulate the total using defaultdict's auto-
                        # initialization
                        inventory[wid] += count
                    except ValueError:
                        log.warning("UID[%d]: Malformed data in slot %d "
                                    "(WID[%d], Num: %d)",
                                    uid, i,
                                    wid, squad_quantity)

        # 4. Log the Final Results
        log.info("--- Inventory Audit Complete ---")
        # Sort by count (descending) to see most prevalent elements first
        sorted_inventory = sorted(inventory.items(), key=lambda x: x[1],
                                  reverse=True)

        for wid, total in sorted_inventory:
            if total > 0:
                ge_name = get_ground_elem_type_name(ground_file_path,
                                                    wid)

                ref = format_ref("WID", wid, ge_name)
                log.info("%s: Total Count = %d",
                         ref, total)

    except StopIteration:
        log.error("The _unit file appears to be empty.")
    except (IOError, OSError) as e:
        log.error("An error occurred reading the file: %s", e)

    return inventory
