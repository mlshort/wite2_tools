"""
Module for locating specific Ground Elements within WiTE2 Order of Battle (OB) CSV files.

This module scans a War in the East 2 (WiTE2) `_ob` CSV file to find all Orders of Battle that
contain a specific Ground Element ID. It iterates through the squad slots (`sqd 0` to `sqd 31`)
for active OBs, skipping rows where the `type` evaluates to 0 or is invalid.

When a match is found, it outputs the result to the console in a formatted table. This table
displays the OB's ID, Name, Type (resolved via a lookup), the exact squad column where the
element was found, and the assigned quantity from the `sqdNum` column.

Command Line Usage:
    python scan_ob_for_ground_elem.py [-h] ge_id

Arguments:
    ge_id (int): The ID of the Ground Element to search for across all OBs.

Example:
    $ python scan_ob_for_ground_elem.py 42
    Scans the OB file and outputs a formatted table of every OB that includes
    Ground Element 42, showing the exact slot it occupies and the quantity assigned.
"""
import os
from typing import cast

# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.lookups import get_ob_type_code_name
from wite2_tools.utils.logger import get_logger

log = get_logger(__name__)


def scan_ob_for_ground_elem(ob_file_path: str, ground_elem_id: int) -> int:
    """
    1. Scans 'sqd' columns for ground_elem_id.
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
        next(ob_gen) # Skip DictReader object

        # Convert inputs to strings to ensure they match CSV text format
        ground_elem_id_str = str(ground_elem_id)

        print(f"\nScanning '{file}' for ge_id='{ground_elem_id_str}'")
        # Print Header for the Console Output
        print(f"\n{'ID':^6} | {'Name':<20} | {'Type':^9} | {'Squad':<6} | {'Value':<10}")
        print("-" * 80)

        # Iterate through every row using explicit type casting
        for item in ob_gen:
            _, row = cast(tuple[int, dict], item)

            raw_ob_type = row.get("type", "0")
            raw_ob_id = row.get("id", "0")

            # Convert to numbers for math comparison
            try:
                ob_type = int(raw_ob_type)
                ob_id = int(raw_ob_id)
            except ValueError:
                # Skip rows where data isn't a number
                continue

            if ob_id == 0 or ob_type == 0:
                # Skip rows where type or id == 0
                continue

            # 2. Search columns 'sqd 0' through 'sqd 31' for the ground_elem_id
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col = f"sqd {i}".strip()
                sqd_num_col = f"sqdNum {i}".strip()

                # Check if column exists and matches the target ID
                if sqd_id_col in row and row[sqd_id_col] == ground_elem_id_str:
                    ob_name = row.get("name", "").strip()
                    ob_suffix = row.get("suffix", "").strip()
                    ob_full_name = f"{ob_name} {ob_suffix}"
                    sqd_num = row.get(sqd_num_col, "0")

                    ob_type_name = get_ob_type_code_name(ob_type)

                    print(f"{ob_id:>6} | {ob_full_name:<20.20s} | {ob_type_name:<9.9s} | '{sqd_id_col}' | '{sqd_num_col}': {sqd_num}")
                    matches_found += 1

        if matches_found == 0:
            print("No matches found.")
        else:
            print(f"\nScan complete. Found {matches_found} match(es).")

    except (FileNotFoundError, ValueError, IOError) as e:
        log.exception("An error occurred during OB scanning: %s", e)

    return matches_found
