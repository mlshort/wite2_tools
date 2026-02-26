"""
Module for locating specific Ground Elements within WiTE2 Order of Battle
TOE(OB) CSV files.

This module scans a War in the East 2 (WiTE2) `_ob` CSV file to find all
Orders of Battle that contain a specific Ground Element WID. It iterates
through the squad slots (`sqd 0` to `sqd 31`) for active OBs, skipping
rows where the `type` evaluates to 0 or is invalid.

When a match is found, it outputs the result to the console in a formatted
table. This table displays the TOE(OB)'s ID, Name, Type (resolved via a
lookup), the exact squad column where the element was found, and the
assigned quantity from the `sqdNum` column.

Command Line Usage:
    python -m wite2_tools.cli scan-ob [-h] [-d DATA_DIR] \
        target_wid

Arguments:
    target_wid (int): The WID of the Ground Element to search for across
                      all OBs.

Example:
    $ python -m wite2_tools.cli scan-ob 42

    Scans the TOE(OB) file and outputs a formatted table of every TOE(OB)
    that includes Ground Element 42, showing the exact slot it occupies
    and the quantity assigned.
"""
import os
from typing import cast

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import (
    get_logger,
    get_ob_type_code_name,
    parse_int,
    parse_str
)

log = get_logger(__name__)


def scan_ob_for_ground_elem(ob_file_path: str,
                            target_wid: int) -> int:
    """
    1. Scans 'sqd' columns for ground_elem_id (WID).
    2. If found, finds the corresponding 'sqdNum' column.
    3. Prints the value of the column.
    """
    file = os.path.basename(ob_file_path)
    if not os.path.exists(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0

    matches_found = 0

    try:
        ob_gen = read_csv_dict_generator(ob_file_path)
        next(ob_gen)  # Skip DictReader object

        # Convert inputs to strings to ensure they match CSV text format
        ground_element_id_str = str(target_wid)

        print(f"\nScanning '{file}' for any instances of "
              "WID='{ground_element_id_str}'")
        # Print Header for the Console Output
        print(f"\n{'ID':^6} | {'Name':<20} | {'Type':^9} | "
              "{'Squad':<6} | {'Value':<10}")
        print("-" * 80)

        # Iterate through every row using explicit type casting
        for item in ob_gen:
            _, row = cast(tuple[int, dict], item)

            # Convert to numbers for math comparison
            ob_type = parse_int(row.get("type"), 0)
            ob_id = parse_int(row.get("id"), 0)

            if ob_id == 0 or ob_type == 0:
                # Skip rows where type or id == 0
                continue

            # 2. Search columns 'sqd 0' through 'sqd 31' for the ground_elem_id
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col = f"sqd {i}"
                sqd_num_col = f"sqdNum {i}"

                # Check if column exists and matches the target ID
                if sqd_id_col in row:
                    if row[sqd_id_col] == ground_element_id_str:
                        ob_name = parse_str(row.get("name"), "")
                        ob_suffix = parse_str(row.get("suffix"), "")
                        ob_full_name = f"{ob_name} {ob_suffix}"
                        sqd_num = parse_int(row.get(sqd_num_col), 0)

                        ob_type_name = get_ob_type_code_name(ob_type)

                        print(f"{ob_id:>6} | {ob_full_name:<20.20s} | "
                              f"{ob_type_name:<9.9s} | '{sqd_id_col}' | "
                              f"'{sqd_num_col}': {sqd_num}")
                        matches_found += 1

        if matches_found == 0:
            print("No matches found.")
        else:
            print(f"\nScan complete. Found {matches_found} WID match(es).")

    except (FileNotFoundError, ValueError, IOError) as e:
        log.exception("An error occurred during scanning _ob for WIDs: %s", e)

    return matches_found
