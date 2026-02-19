
"""
Data Validation and Consistency Checkers
========================================

This module provides robust validation routines to ensure the structural integrity
and logical consistency of War in the East 2 (WiTE2) data files. It is designed
to detect common data corruption issues, manual editing errors, and referential
integrity breaks before they cause runtime crashes in the game engine.

Key Validation Logic
--------------------
* **Referential Integrity**: Verifies that all Ground Element IDs referenced in
  squad slots (0-31) actually exist in the master `_ground` file.
* **Ghost/Orphan Detection**: Scans for "Ghost Squads" (slots with a quantity
  but no valid Element ID) which are a primary cause of game instability.
* **Coordinate Bounds**: Ensures unit X/Y coordinates fall within the valid
  game map dimensions (0-378, 0-354).
* **Structural Checks**: Detects duplicate Primary Key IDs and column count
  mismatches.

Functions
---------
* `evaluate_ob_consistency`: detailed audit of Order of Battle (OB) files.
* `evaluate_unit_consistency`: Detailed audit of Unit placement files, including
  HQ attachment logic and map positioning.
"""

import csv
import os
from tempfile import NamedTemporaryFile

# Internal package imports
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import (
    MAX_SQUAD_SLOTS,
    MIN_X,
    MAX_X,
    MIN_Y,
    MAX_Y
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.get_valid_ids import get_valid_ground_elem_ids

# Initialize the logger for this specific module
log = get_logger(__name__)

def evaluate_ob_consistency(ob_file_path: str, ground_file_path: str) -> int:
    """
    Performs a deep consistency check on a WiTE2 _ob CSV file.
    """
    issues_found = 0
    seen_ob_ids: set[int] = set()
    valid_elem_ids: set[int] = set()

    try:
        ob_file_base_name = os.path.basename(ob_file_path)
        # get the set of valid ground element ids
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)

        ob_gen = read_csv_dict_generator(ob_file_path, 2)  # start=2 accounts for header
        reader = next(ob_gen)
        headers = reader.fieldnames  # type: ignore

        if headers is None:
            log.error("Could not retrieve headers from '%s'.", ob_file_base_name)
            return issues_found

        # Iterate through every row
        log.info("Checking consistency for: '%s'", ob_file_base_name)

        for _, row in ob_gen:
            # 1. Check for Duplicate IDs (Critical for OB stability)
            ob_id = int(row.get('id', '0'))
            ob_type = int(row.get('type', '0'))
            ob_first_year = int(row.get('firstYear', '0'))

            if ob_id in seen_ob_ids:
                log.error("OB ID %d: Duplicate ID found", ob_id)
                issues_found += 1
            else:
                seen_ob_ids.add(ob_id)

            if ob_type != 0 and ob_first_year == 0:
                log.warning("OB ID %d: Active Type:%d, but has First Year of:%d.",
                            ob_id, ob_type, ob_first_year)
                issues_found += 1

            header_len = len(headers) if headers is not None else 0

            # 2. Check for Row Length Consistency
            if len(row) != header_len:
                log.error("OB ID %d: Column count mismatch. Expected %d, found %d.",
                          ob_id, header_len, len(row))
                issues_found += 1

            # 3. Logical Squad Check (Ghost Squads)
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col = f"sqd.u{i}"  # in the WiTE2 editor, this field is called 'WID'
                sqd_num_col = f"sqd.num{i}"

                sqd_id_val = row.get(sqd_id_col, "0")
                sqd_num_val = row.get(sqd_num_col, "0")

                if sqd_id_val != "0" and int(sqd_id_val) not in valid_elem_ids:
                    log.error("OB (ID %d): Slot %d has Elem ID %s but Elem ID is not found in _ground.csv.",
                              ob_id, i, sqd_id_val)
                    issues_found += 1

                # Inverse: If num > 0, sqd_id_val cannot be '0'
                if sqd_num_val != "0" and sqd_id_val == "0":
                    log.warning("OB (ID %d): Ghost Squad! %s has quantity '%s' but %s is '0'",
                                ob_id, sqd_num_col, sqd_num_val, sqd_id_col)
                    issues_found += 1

        if issues_found == 0:
            log.info("Consistency Check Passed: No structural or logical issues detected.")
        else:
            log.error("Consistency Check Failed: %d issues identified.", issues_found)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Could not complete consistency check: %s", e)
        return -1

    return issues_found


def evaluate_unit_consistency(unit_file_path: str, ground_file_path: str,
                              only_active_units: bool = True, fix_ghosts: bool = False) -> int:
    """
    Validates a WiTE2 _unit CSV file for structural integrity and game-logic errors.

    Args:
        unit_file_path: Path to the unit CSV.
        ground_file_path: Path to the ground element CSV (for ID validation).
        only_active_units: If True, skips units with id="0" or type="0".
        fix_ghosts: If True, automatically zeroes out squad quantities where the ID is 0.
    """
    issues_found = 0
    fixed_count = 0
    seen_unit_ids: set[int] = set()
    valid_elem_ids: set[int] = set()

    # Setup for writing fixed file
    temp_file = None
    writer = None

    try:
        # get the set of valid ground element ids
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)

        unit_gen = read_csv_dict_generator(unit_file_path, 2)  # start=2 accounts for header
        reader = next(unit_gen)

        # Initialize temp file if fix mode is enabled
        if fix_ghosts:
            temp_file = NamedTemporaryFile(mode='w', delete=False, dir=os.path.dirname(unit_file_path),
                                           newline='', encoding=ENCODING_TYPE)
            writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)  # type: ignore
            writer.writeheader()
        unit_file_base_name = os.path.basename(unit_file_path)
        log.info("Evaluating Unit file consistency: '%s' (Fix Mode: %s)", unit_file_base_name, fix_ghosts)

        for _, row in unit_gen:
            unit_id = row.get("id", "0")
            unit_type = row.get("type", "0")

            if only_active_units and (unit_id == "0" or unit_type == "0"):
                if fix_ghosts and writer:
                    writer.writerow(row)
                continue

            unit_name = row.get("name", "Unk")
            row_modified = False

            # 1. Primary Key Uniqueness
            if int(unit_id) in seen_unit_ids:
                log.error("ID %s: Duplicate Unit ID '%s' for '%s'", unit_id, unit_id, unit_name)
                issues_found += 1
            seen_unit_ids.add(int(unit_id))

            # 2. Coordinate Validation
            try:
                x, y = int(row.get('x', -1)), int(row.get('y', -1))
                if not (MIN_X <= x <= MAX_X and MIN_Y <= y <= MAX_Y):
                    log.warning("ID %s (%s): Invalid coordinates (%d, %d)", unit_id, unit_name, x, y)
                    issues_found += 1
            except (ValueError, TypeError):
                log.error("ID %s (%s): Non-numeric coordinates detected.", unit_id, unit_name)
                issues_found += 1

            # 3. Squad ID vs Squad Number Logic
            for i in range(MAX_SQUAD_SLOTS):
                sqd_id_col = f"sqd.u{i}"
                sqd_num_col = f"sqd.num{i}"

                sqd_id_val = row.get(sqd_id_col, "0")
                sqd_num_val = row.get(sqd_num_col, "0")

                # Check for Elem Invalid IDs
                if sqd_id_val != "0" and int(sqd_id_val) not in valid_elem_ids:
                    log.error("ID %s (%s): Slot %d has invalid Elem ID %s.",
                              unit_id, unit_name, i, sqd_id_val)
                    issues_found += 1

                # Check for Ghost Squads (Quantity > 0 but ID == 0)
                if sqd_num_val != "0" and sqd_id_val == "0":
                    log.error("ID %s (%s): Ghost Squad detected in Slot %d (Qty: %s).",
                              unit_id, unit_name, i, sqd_num_val)
                    issues_found += 1

                    if fix_ghosts:
                        log.info(" -> FIXING: Zeroing out %s for Unit %s",
                                 sqd_num_col, unit_id)
                        row[sqd_num_col] = "0"
                        row_modified = True
                        fixed_count += 1

            # 4. Attachment/HQ Check
            if row.get('hhq', '0') == unit_id:
                if row.get('hq', '0') != '1': # highest level HQ
                    log.warning("ID %s (%s): Unit is reporting itself as its own HQ.",
                                unit_id, unit_name)
                    issues_found += 1

            # Write the row (modified or original) to temp file
            if fix_ghosts and writer:
                writer.writerow(row)

        # Finalize and swap files if changes were made
        if fix_ghosts and temp_file:
            temp_file.close()
            if fixed_count > 0:
                log.info("Fix Mode Complete: Repaired %d Ghost Squads. Overwriting original file.",
                         fixed_count)
                os.replace(temp_file.name, unit_file_path)
            else:
                log.info("Fix Mode Complete: No Ghost Squads found to fix.")
                os.remove(temp_file.name)

        if issues_found == 0:
            log.info("Unit Consistency Check Passed.")
        else:
            log.error("Unit Consistency Check Failed with %d issues.", issues_found)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during unit evaluation: %s", e)
        if temp_file and os.path.exists(temp_file.name):
            try:
                temp_file.close()
                os.remove(temp_file.name)
            except OSError:
                pass
        return -1

    return issues_found