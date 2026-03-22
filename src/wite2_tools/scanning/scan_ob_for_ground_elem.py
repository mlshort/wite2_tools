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

# Internal package imports
from wite2_tools.generator import get_csv_list_stream, CSVListStream
from wite2_tools.models import (
    ObColumn,
    ObRow,
    O_SQD_SLOTS
)
from wite2_tools.utils import (
    get_logger,
    get_ob_type_code_name,
    format_ref
)
from wite2_tools.utils.parsing import parse_row_int

# Initialize the log for this specific module
log = get_logger(__name__)


def scan_ob_for_ground_elem(
    ob_file_path: str,
    target_wid: int
) -> int:
    """
    1. Scans a _ob CSV 'sqd' columns for ground_elem_id.
    2. If found, finds the corresponding 'sqdNum' column.
    3. Outputs the value.
    """
    if not os.path.isfile(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0

    matches_found = 0

    try:
        ob_stream: CSVListStream = get_csv_list_stream(ob_file_path)

        # Assuming format_ref is just for formatting the target_wid properly
        ref = format_ref("WID", target_wid, "Target")
        print(f"\nScanning '{os.path.basename(ob_file_path)}' for {ref}")

        # Print Header for the Console Output
        print(f"\n{'ID':^6} | {'Name':<20} | {'Type':<9} | "
              f"{'Squad':<7} | {'Value':<10}")
        print("-" * 80)

        # Iterate through every row
        for _, row in ob_stream.rows:
            ob = ObRow(row)

            ob_type = ob.TYPE
            ob_id   = ob.ID

            if ob_id == 0 or ob_type == 0:
                # Skip rows where type or id == 0
                continue

            # 2. Search columns 'sqd 0' through 'sqd 31' for the ground_elem_id
            for i in range(O_SQD_SLOTS):

                # Calculate the physical indices for this specific slot
                wid_idx = ObColumn.SQD_0 + i
                cnt_idx = ObColumn.SQD_NUM_0 + i

                sqd_wid = parse_row_int(row, wid_idx)

                # Check if column matches the target ID
                if sqd_wid == target_wid:
                    ob_name   = ob.NAME
                    ob_suffix = ob.SUFFIX
                    ob_full_name = f"{ob_name} {ob_suffix}"
                    sqd_num = parse_row_int(row, cnt_idx)

                    ob_type_name = get_ob_type_code_name(ob_type)

                    # Reconstruct the column name strings for the console output
                    sqd_id_col = f"sqd {i}"
                    sqd_num_col = f"sqdNum {i}"

                    print(f"{ob_id:>6} | {ob_full_name:<20.20s} | "
                          f"{ob_type_name:<9.9s} | '{sqd_id_col}' | "
                          f"'{sqd_num_col}': {sqd_num}")
                    matches_found += 1

        if matches_found == 0:
            print("No matches found.")
        else:
            print(f"\nScan complete. Found {matches_found} match(es).")

    except (IOError, OSError, ValueError) as e:
        log.exception("An error occurred during OB scanning: %s", e)

    return matches_found