"""
Module for locating specific Ground Elements within WiTE2 _unit CSV files.

This module scans a War in the East 2 (WiTE2) `_unit` CSV file to find all
active units that contain a specific Ground Element WID. It iterates
through the squad slots (`sqd.u0` to `sqd.u31`) for active units.

When a match is found, it outputs the result to the console in a formatted
table, displaying the Unit's ID, Name, Type (resolved via a lookup), the
exact squad column where the element was found, and the assigned quantity
(`sqd.num`).

Command Line Usage:
    python -m wite2_tools.cli scan-unit [-h] [-d DATA_DIR] \
        target_wid [num_squads]

Arguments:
    target_wid (int): The WID of the Ground Element to search for across
                      all units.
    target_num_squads (int, optional): Filter by exact number of assigned
                                       squads.

Example:
    $ python -m wite2_tools.cli scan-unit 42

    Scans the unit file and outputs a formatted table of every unit that
    includes Ground Element 42, showing the exact slot it occupies and the
    quantity assigned.

    $ python -m wite2_tools.cli scan-unit 42 10

    Same as above, but only returns matches where exactly 10 of Ground
    Element 42 are assigned.
"""
import os
from typing import cast

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import (
    get_logger,
    get_unit_type_name,
    get_ground_elem_type_name,
    parse_int,
    parse_str
)

log = get_logger(__name__)


def _check_squad_match(
    row: dict,
    ob_full_path: str,
    target_wid: int,
    num_squads_filter: int,
    matches_found: int
) -> int:

    for i in range(MAX_SQUAD_SLOTS):
        sqd_id_col = f"sqd.u{i}"
        sqd_num_col = f"sqd.num{i}"

        wid = parse_int(row.get(sqd_id_col), 0)

        # Check if column exists and matches the target ID
        if sqd_id_col in row and wid == target_wid:

            # Search the row for the new column name and print squad_quantity
            if sqd_num_col in row:
                uname = parse_str(row.get("name"), "Unk")
                squad_quantity = parse_int(row.get(sqd_num_col), 0)
                uid = parse_int(row.get("id"), 0)
                # unit 'type' maps to its TOE(OB) ID
                utype = parse_int(row.get("type"), 0)
                unit_type_name = get_unit_type_name(ob_full_path, utype)

                # Filter by exact quantity if a specific number was provided
                # (-1 means ANY)
                if num_squads_filter != -1:
                    try:
                        if squad_quantity == num_squads_filter:
                            print(f"{uid:>6} | {uname:<15.15s} | "
                                  f"{unit_type_name:<25.25s} | "
                                  f"{sqd_id_col:<6} | "
                                  f"'{sqd_num_col}': {squad_quantity}")
                            matches_found += 1
                    except ValueError:
                        continue
                else:
                    # Print all matches regardless of quantity
                    print(f"{uid:>6} | {uname:<15.15s} | "
                          f"{unit_type_name:<25.25s} | {sqd_id_col:<6} | "
                          f"'{sqd_num_col}': {squad_quantity}")
                    matches_found += 1

    return matches_found


def scan_unit_for_ground_elem(
    unit_file_path: str,
    ground_file_path: str,
    ob_full_path: str,
    target_wid: int,
    target_num_squads: int = -1
) -> int:
    """
    1. Scans a _unit CSV 'sqd.u' columns for ground_elem_id.
    2. If found, finds the corresponding 'sqd.num' column.
    3. If old_num_squads == -1, prints the value of the column.
    4. Otherwise, CHECKS if the value in 'sqd.num' equals 'old_num_squads'.
    """
    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    matches_found = 0

    try:
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip DictReader object

        scan_str = "ANY" if target_num_squads == -1 else str(target_num_squads)
        ground_elem_name = get_ground_elem_type_name(ground_file_path,
                                                     target_wid)

        print(f"\nScanning '{os.path.basename(unit_file_path)}' for "
              f"'{ground_elem_name}' (WID '{target_wid}') where "
              f"quantity == '{scan_str}'")

        # Print Header for the Console Output
        print(f"\n{'ID':^6} | {'Name':<15} | {'Type':<25} | "
              f"{'Squad':<6} | {'Value':<10}")
        print("-" * 80)

        # Iterate through every row
        for item in unit_gen:
            _, row = cast(tuple[int, dict], item)

            # Convert to numbers for math comparison
            utype = parse_int(row.get("type"), 0)
            if utype == 0:
                continue

            # 2. Search columns 'sqd.u0' through 'sqd.u31' for the target ID
            matches_found = _check_squad_match(row, ob_full_path,
                                               target_wid,
                                               target_num_squads,
                                               matches_found)

        if matches_found == 0:
            print("No matches found.")
        else:
            print(f"\nScan complete. Found {matches_found} match(es).")

    except (IOError, OSError, ValueError) as e:
        log.exception("An error occurred during unit scanning: %s", e)

    return matches_found
