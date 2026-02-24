"""
TOE / Order of Battle Audit Utility
===================================

This module provides functionality to audit War in the East 2 (WiTE2)
`_ob.csv` (Table of Organization and Equipment) files.

It scans the core template database to ensure historical chronology,
upgrade path validity, and equipment slot consistency. Finding and fixing
these issues prevents infinite upgrade loops or "time traveling" units
from breaking the scenario generation process.

Key Validation Logic
--------------------
* Chronological Bounds: Ensures an TOE(OB) does not expire (Last Year/Month)
  before it is historically introduced (First Year/Month).
* Upgrade Path Integrity: Detects upgrade dead-ends (pointing to a non-existent
  TOE(OB) ID) and infinite self-upgrade loops.
* Slot Consistency: Flags negative squad quantities and prevents intra-template
  duplication (assigning the same WID to multiple slots in the same TOE(OB)).
* Referential Integrity: Confirms all assigned equipment exists in
    `_ground.csv`.

Command Line Usage:
    python -m wite2_tools.cli audit-ob [-h] [-d DATA_DIR]
"""
import os

# Internal package imports
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.utils import (
    get_logger,
    parse_int,
    parse_str,
    get_valid_ground_elem_ids
)


log = get_logger(__name__)


def _check_chronology(ob_id: int, ob_name: str, row: dict) -> int:
    """Validates the historical introduction and expiration dates."""
    issues = 0
    f_year = parse_int(row.get('firstYear'), 0)
    f_month = parse_int(row.get('firstMonth'), 0)
    l_year = parse_int(row.get('lastYear'), 0)
    l_month = parse_int(row.get('lastMonth'), 0)

    if f_year == 0:
        log.warning("TOE(OB) ID[%d] (%s): Active but has First Year of 0.",
                    ob_id, ob_name)
        issues += 1

    if l_year > 0:
        if l_year < f_year:
            log.error("TOE(OB) ID[%d] (%s): Expires (%d) before intro "
                      "year (%d).",
                      ob_id, ob_name, l_year, f_year)
            issues += 1
        elif l_year == f_year and l_month < f_month:
            log.error("TOE(OB) ID[%d] (%s): Expires in month %d but introduced "
                      "in month %d of same year.",
                      ob_id, ob_name, l_month, f_month)
            issues += 1

    return issues


def _check_upgrade_path(ob_id: int,
                        ob_name: str,
                        row: dict,
                        valid_ob_ids: set[int]) -> int:
    """Validates the TOE upgrade paths to prevent loops and dead-ends."""
    issues = 0
    upgrade_id = parse_int(row.get('upgrade'), 0)

    if upgrade_id > 0:
        if upgrade_id == ob_id:
            log.error("TOE(OB) ID[%d] (%s): Upgrades into itself "
                      "(Infinite Loop).", ob_id, ob_name)
            issues += 1
        elif upgrade_id not in valid_ob_ids:
            log.error("TOE(OB) ID[%d] (%s): Upgrades to non-existent OB ID[%d].",
                      ob_id, ob_name, upgrade_id)
            issues += 1

    return issues


def _check_squad_slots(ob_id: int,
                       ob_name: str,
                       row: dict,
                       valid_elem_ids: set[int]) -> int:
    """
    Validates all 32 equipment slots for negative quantities, ghosts,
    and WID duplicates.
    """
    issues = 0
    seen_wids_in_row = set()

    for i in range(MAX_SQUAD_SLOTS):
        sqd_id_col = f"sqd.u{i}"
        sqd_num_col = f"sqd.num{i}"

        sqd_id = parse_int(row.get(sqd_id_col), 0)
        qty = parse_int(row.get(sqd_num_col), 0)

        if qty < 0:
            log.error("TOE(OB) ID[%d] (%s): %s has negative quantity (%d).",
                      ob_id, ob_name, sqd_num_col, qty)
            issues += 1

        if sqd_id != 0 and sqd_id not in valid_elem_ids:
            log.error("TOE(OB) ID[%d]: %s has WID[%d] but WID is not found "
                      "in _ground.csv.",
                      ob_id, sqd_id_col, sqd_id)
            issues += 1

        if qty != 0 and sqd_id == 0:
            log.warning("TOE(OB) (ID[%d]): Ghost Squad! %s has quantity %d but %s "
                        "is '0'",
                        ob_id, sqd_num_col, qty, sqd_id_col)
            issues += 1

        # Intra-Template Duplicate Check
        if sqd_id != 0 and qty > 0:
            if sqd_id in seen_wids_in_row:
                log.warning("TOE(OB) ID[%d] (%s): WID[%d] is assigned to "
                            "multiple slots.",
                            ob_id, ob_name, sqd_id)
                issues += 1
            seen_wids_in_row.add(sqd_id)

    return issues


def audit_ob_csv(ob_file_path: str, ground_file_path: str) -> int:
    """
    Performs a deep consistency check on a WiTE2 _ob CSV file.

    Args:
        ob_file_path (str): The absolute or relative path to the _ob.csv file.
        ground_file_path (str): The path to the _ground.csv file for
        referential integrity.

    Returns:
        int: The total number of issues identified. -1 if a critical error
             occurred.
    """
    issues_found = 0
    seen_ob_ids: set[int] = set()
    valid_elem_ids: set[int] = set()
    valid_ob_ids: set[int] = set()

    try:
        ob_file_base_name = os.path.basename(ob_file_path)
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)

        # 1. PRE-PASS: Collect all valid TOE(OB) IDs for upgrade checking
        ob_gen_pre = read_csv_dict_generator(ob_file_path, 2)
        next(ob_gen_pre)  # skip header
        for _, r in ob_gen_pre:
            valid_ob_ids.add(parse_int(r.get("id"), 0))

        # 2. MAIN PASS
        ob_gen = read_csv_dict_generator(ob_file_path, 2)
        reader = next(ob_gen)
        fieldnames = getattr(reader, 'fieldnames', None)
        header_len = len(fieldnames) if fieldnames else 0

        log.info("Checking consistency on: '%s'", ob_file_base_name)

        for _, row in ob_gen:
            ob_id = parse_int(row.get('id'), 0)
            ob_type = parse_int(row.get('type'), 0)
            ob_name = parse_str(row.get('name'), 'Unk')

            # Duplicate ID Check
            if ob_id in seen_ob_ids:
                log.error("TOE(OB) ID[%d]: Duplicate IDs found", ob_id)
                issues_found += 1
            seen_ob_ids.add(ob_id)

            # Row Length Check
            if len(row) != header_len:
                log.error("TOE(OB) ID[%d]: Column count mismatch.", ob_id)
                issues_found += 1

            # Only check active OBs
            if ob_type != 0:
                issues_found += _check_chronology(ob_id, ob_name, row)
                issues_found += _check_upgrade_path(ob_id, ob_name, row,
                                                    valid_ob_ids)

            # Slot & Element Validation
            issues_found += _check_squad_slots(ob_id, ob_name, row,
                                               valid_elem_ids)

        # Output formatting bug fixed here (swapped variables)
        if issues_found == 0:
            log.info("%d OBs Checked - _ob.csv Consistency Check Passed.",
                     len(seen_ob_ids))
        else:
            log.info("%d OBs Checked - _ob.csv Consistency Check Failed: %d "
                     "issues identified.",
                     len(seen_ob_ids), issues_found)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during consistency check: %s", e)
        return -1

    return issues_found