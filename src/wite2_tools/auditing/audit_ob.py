
"""
Data Validation and Consistency Checkers
========================================

This module provides robust validation routines to ensure the structural
integrity and logical consistency of War in the East 2 (WiTE2) data files.
It is designed to detect common data corruption issues, manual editing errors,
and referential integrity breaks before they cause runtime crashes in the
game engine.

Key Validation Logic
--------------------
* Referential Integrity: Verifies that all Ground Element WIDs
  referenced in squad slots (0-31) actually exist in the master
  `_ground` file.
* Ghost/Orphan Detection: Scans for "Ghost Squads" (slots with a
  quantity but no valid Element ID) which cause game instability.
* Coordinate Bounds: Ensures unit X/Y coordinates fall within the valid
  game map dimensions (0-378, 0-354).
* Structural Checks: Detects duplicate Primary Key IDs and column count
  mismatches.

Functions
---------
* `audit_ob_csv`: detailed audit of Order of Battle TOE(OB) files.
* `audit_unit_csv`: Detailed audit of Unit placement files,
                including HQ attachment logic and map positioning.

Command Line Usage:
    python -m wite2_tools.cli audit-unit [-h] [-d DATA_DIR] [active_only] \
        [fix_ghosts]

    python -m wite2_tools.cli audit-ob [-h] [-d DATA_DIR]

Arguments:
    active_only (bool, optional): Skips inactive units (type=0) if
                                  True. Defaults to True.
    fix_ghosts (bool, optional): Automatically repairs ghost squads if
                                 True. Defaults to False.

Example:
    $ python -m wite2_tools.cli audit-unit True True

    Scans the default unit file, evaluating only active units, and
    automatically fixes any ghost squads found.

    $ python -m wite2_tools.cli audit-ob

    Scans the default TOE(OB) file for structural and logical errors.
"""

import os

# Internal package imports
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.parsing import (
     parse_int,
     parse_str
)
from wite2_tools.constants import (
    MAX_SQUAD_SLOTS
)
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.get_valid_ids import (
    get_valid_ground_elem_ids,
    get_valid_ob_ids
)

# Initialize the logger for this specific module
log = get_logger(__name__)


def is_greater_than_zero(value) -> bool:
    try:
        return float(value) > 0
    except ValueError:
        # Returns False if the cell is text, empty, or None
        return False


def audit_ob_csv(ob_file_path: str,
                 ground_file_path: str) -> int:
    """
    Performs a deep consistency check on a WiTE2 _ob CSV file.
    """
    issues_found = 0
    seen_ob_ids: set[int] = set()
    valid_elem_ids: set[int] = set()
    valid_ob_ids: set[int] = set()

    try:
        ob_file_base_name = os.path.basename(ob_file_path)
        # get the set of valid ground element ids
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)
        # start=2 accounts for header
        valid_ob_ids = get_valid_ob_ids(ob_file_path)
        ob_gen = read_csv_dict_generator(ob_file_path, 2)
        reader = next(ob_gen)
        headers = reader.fieldnames  # type: ignore

        if headers is None:
            log.error("Could not retrieve headers from '%s'.",
                      ob_file_base_name)
            return issues_found

        # Iterate through every row
        log.info("Checking consistency on: '%s'", ob_file_base_name)

        for _, row in ob_gen:
            # 1. Check for Duplicate IDs (Critical for TOE(OB) stability)
            ob_id = parse_int(row.get('id'), 0)
            ob_type = parse_int(row.get('type'), 0)
            ob_name = parse_str(row.get('name'), "Unk")

            if ob_id in seen_ob_ids:
                log.error("TOE(OB) ID %d: Duplicate IDs found", ob_id)
                issues_found += 1
            else:
                seen_ob_ids.add(ob_id)

            if ob_type != 0:
                # 2. Chronological Validation
                f_year = parse_int(row.get('firstYear'), 0)
                f_month = parse_int(row.get('firstMonth'), 0)
                l_year = parse_int(row.get('lastYear'), 0)
                l_month = parse_int(row.get('lastMonth'), 0)

                if f_year == 0:
                    log.warning("TOE(OB) ID %d (%s): Active but has First"
                                " Year of 0.", ob_id, ob_name)
                    issues_found += 1

                if l_year > 0:
                    if l_year < f_year:
                        log.error("TOE(OB) ID %d (%s): Expires (%d) before "
                                  "intro year (%d).",
                                  ob_id, ob_name, l_year, f_year)
                        issues_found += 1
                    elif l_year == f_year and l_month < f_month:
                        log.error("TOE(OB) ID %d (%s): Expires in month %d "
                                  "but introduced in month %d of same year.",
                                  ob_id, ob_name, l_month, f_month)
                        issues_found += 1

            # 2. Check for Row Length Consistency
            header_len = len(headers) if headers is not None else 0
            if len(row) != header_len:
                log.error("TOE(OB) ID %d: Column count mismatch. "
                          "Expected %d Row(s), found %d Row(s).",
                          ob_id, header_len, len(row))
                issues_found += 1

            # 3. Upgrade Path Validation
            upgrade_id = parse_int(row.get('upgrade'), 0)
            if upgrade_id > 0:
                if upgrade_id == ob_id:
                    log.error("TOE(OB) ID %d (%s): Upgrades into itself "
                              "(Infinite Loop).", ob_id, ob_name)
                    issues_found += 1
                elif upgrade_id not in valid_ob_ids:
                    log.error("TOE(OB) ID %d (%s): Upgrades to "
                              "non-existent OB ID %d.",
                              ob_id, ob_name, upgrade_id)
                    issues_found += 1

            # 3. Logical Squad Check (Ghost Squads)
            seen_wids_in_row = set()
            for i in range(MAX_SQUAD_SLOTS):
                # in the WiTE2 editor, this field is called 'WID'
                sqd_id_col = f"sqd.u{i}"
                sqd_num_col = f"sqd.num{i}"

                sqd_id = parse_int(row.get(sqd_id_col), 0)
                qty = parse_int(row.get(sqd_num_col), 0)

                if qty < 0:
                    log.error("TOE(OB) ID %d (%s): Slot %d has negative "
                              "quantity (%d).", ob_id, ob_name, i, qty)
                    issues_found += 1

                if sqd_id != 0 and sqd_id not in valid_elem_ids:
                    log.error("TOE(OB) (ID %d): Slot %d has WID %d but WID is"
                              " not found in _ground.csv.",
                              ob_id, i, sqd_id)
                    issues_found += 1

                # Inverse: If num > 0, sqd_id_val cannot be '0'
                if qty != 0 and sqd_id == 0:
                    log.warning("OB (ID %d): Ghost Squad! %s has quantity %d"
                                " but %s is '0'",
                                ob_id, sqd_num_col, qty, sqd_id_col)
                    issues_found += 1

                # Intra-Template Duplicate Check
                if sqd_id != 0 and qty > 0:
                    if sqd_id in seen_wids_in_row:
                        log.warning("TOE(OB) ID %d (%s): WID %d is assigned "
                                    "to multiple slots.",
                                    ob_id, ob_name, sqd_id)
                        issues_found += 1
                    seen_wids_in_row.add(sqd_id)

        if issues_found == 0:
            log.info("%d OBs Checked - _ob.csv Consistency Check Passed.",
                     len(seen_ob_ids))
        else:
            log.info("%d OBs Checked - _ob.csv Consistency Check Failed:"
                     "%d issues identified.",
                     issues_found, len(seen_ob_ids))

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Could not complete consistency check: %s", e)
        return -1

    return issues_found


