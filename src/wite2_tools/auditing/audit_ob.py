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
from wite2_tools.generator import CSVListStream, get_csv_list_stream
from wite2_tools.utils import (
    get_logger,
    parse_row_int,
    parse_row_str,
    get_valid_ground_elem_ids,
    format_ref
)
from wite2_tools.models import (
    ObRow,
    O_SQD_SLOTS,
    O_ID_COL,
    O_NAME_COL,
    O_TYPE_COL,
    O_UPGRADE_COL,
    O_SQD0_COL,
    O_SQD_NUM0_COL,
)

# Initialize the log for this specific module
log = get_logger(__name__)


def is_date_invalid(f_yr:int, f_mo:int, l_yr:int, l_mo:int) -> bool:
    if l_yr < f_yr:
        return True
    if l_yr == f_yr and l_mo < f_mo:
        return True
    return False

def _check_chronology(ob_id: int, ob_name: str, row: list[str]) -> int:
    """Validates the historical introduction and expiration dates."""
    issues = 0
    ob = ObRow(row)
    f_year  = ob.FIRST_YEAR #  parse_row_int(row,O_FIRSTYEAR_COL)
    f_month = ob.FIRST_MONTH #parse_row_int(row,O_FIRSTMONTH_COL)
    l_year  = ob.LAST_YEAR #parse_row_int(row,O_LASTYEAR_COL)
    l_month = ob.LAST_MONTH #parse_row_int(row,O_LASTMONTH_COL)

    ref = format_ref("TOE(OB)", ob_id, ob_name)

    if f_year == 0:
        log.warning("%s: Active but has First Year of 0.",
                    ref)
        issues += 1

    if l_year > 0:
        if l_year < f_year:
            log.error("%s: Expires (%d) before intro "
                      "year (%d).",
                      ref, l_year, f_year)
            issues += 1
        elif l_year == f_year and l_month < f_month:
            log.error("%s: Expires in month %d but introduced "
                      "in month %d of same year.",
                      ref, l_month, f_month)
            issues += 1

    return issues


def _check_upgrade_path(ob_id: int,
                        ob_name: str,
                        row: list[str],
                        valid_ob_ids: set[int]) -> int:
    """Validates the TOE upgrade paths to prevent loops and dead-ends."""
    issues = 0
    upgrade_id = parse_row_int(row,O_UPGRADE_COL)

    ref = format_ref("TOE(OB)", ob_id, ob_name)

    if upgrade_id > 0:
        if upgrade_id == ob_id:
            log.error("%s: Upgrades into itself "
                      "(Infinite Loop).", ref)
            issues += 1
        elif upgrade_id not in valid_ob_ids:
            log.error("%s: Upgrades to non-existent OB ID[%d].",
                      ref, upgrade_id)
            issues += 1

    return issues


def _check_squad_slots(ob_id: int,
                       ob_name: str,
                       row: list[str],
                       valid_elem_ids: set[int]) -> int:
    """
    Validates all 32 equipment slots for negative quantities, ghosts,
    and WID duplicates.
    """
    issues = 0
    seen_wids_in_row: set[int] = set()
    ref = format_ref("TOE(OB)", ob_id, ob_name)

    for i in range(O_SQD_SLOTS):
        sqd_id_col = O_SQD0_COL + i
        sqd_num_col = O_SQD_NUM0_COL + i

        sqd_id = parse_row_int(row,sqd_id_col)
        qty = parse_row_int(row,sqd_num_col)

        if qty < 0:
            log.error("%s: %s has negative quantity (%d).",
                      ref, sqd_num_col, qty)
            issues += 1

        if sqd_id != 0 and sqd_id not in valid_elem_ids:
            log.error("%s: %s has WID[%d] but WID is not found "
                      "in _ground.csv.",
                      ref, sqd_id_col, sqd_id)
            issues += 1

        if qty != 0 and sqd_id == 0:
            log.warning("%s: Ghost Squad! %s has quantity %d but %s "
                        "is '0'",
                        ref, sqd_num_col, qty, sqd_id_col)
            issues += 1

        # Intra-Template Duplicate Check
        if sqd_id != 0 and qty > 0:
            if sqd_id in seen_wids_in_row:
                log.warning("%s: WID[%d] is assigned to "
                            "multiple slots.",
                            ref, sqd_id)
                issues += 1
            seen_wids_in_row.add(sqd_id)

    return issues


def _check_for_loops(upgrade_map: dict[int, int],
                     ob_names: dict[int, str]) -> int:
    """
    Traces every upgrade path to ensure it eventually ends at 0.
    Returns the number of loops found.
    """
    issues = 0
    for start_id in upgrade_map:
        visited = set()
        current_id:int = start_id
        path:list[str] = []

        while current_id != 0:
            if current_id in visited:
                # Loop detected!
                path_str = " -> ".join(f"[{i}]" for i in path + [current_id])
                log.error("TOE(OB) Upgrade Loop Detected: %s", path_str)
                issues += 1
                break

            visited.add(current_id)
            path.append(str(current_id))
            # Move to the next ID in the chain, default to 0 (end) if ID is missing
            current_id = upgrade_map.get(current_id, 0)

    return issues


def audit_ob_csv(ob_file_path: str,
                 ground_file_path: str) -> int:
    """
    Performs a deep consistency check on a WiTE2 _ob CSV file.

    Args:
        ob_file_path (str): The absolute or relative path to the _ob.csv file.
        ground_file_path (str): The path to the _ground.csv file for
        referential integrity.

    Returns:
        int: The total number of issues identified.
    """
    issues_found = 0
    upgrade_map: dict[int, int] = {}
    ob_names: dict[int, str] = {}
    seen_ob_ids: set[int] = set()
    valid_elem_ids: set[int] = set()
    valid_ob_ids: set[int] = set()

    if not os.path.isfile(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0

    if not os.path.isfile(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return 0

    try:
        ob_file_base_name: str = os.path.basename(ob_file_path)
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)

        # 1. PRE-PASS: Collect all valid TOE(OB) IDs for upgrade checking
        ob_gen_pre: CSVListStream = get_csv_list_stream(ob_file_path)
        for _, r in ob_gen_pre.rows:
            ob_id = parse_row_int(r, O_ID_COL)
            if ob_id != 0:
                valid_ob_ids.add(ob_id)
                ob_names[ob_id] = parse_row_str(r, O_NAME_COL, "Unk")
                upgrade_map[ob_id] = parse_row_int(r, O_UPGRADE_COL)

        # 2. MAIN PASS
        ob_stream: CSVListStream = get_csv_list_stream(ob_file_path)
        header_len = len(ob_stream.header)

        log.info("Checking consistency on: '%s'", ob_file_base_name)

        for _, row in ob_stream.rows:
            ob_id = parse_row_int(row,O_ID_COL)
            ob_type = parse_row_int(row,O_TYPE_COL)
            ob_name = parse_row_str(row,O_NAME_COL, 'Unk')

            # Duplicate ID Check
            if ob_id in seen_ob_ids:
                log.error("TOE(OB) ID[%d]: Duplicate IDs found", ob_id)
                issues_found += 1
            seen_ob_ids.add(ob_id)

            # Row Length Check
            row_len: int = len(row)
            if row_len != header_len:
                log.error("TOE(OB) ID[%d]: Column count mismatch. %d vs %d",
                          ob_id, header_len, row_len)
                issues_found += 1

            # Only check active OBs
            if ob_type != 0:
                issues_found += _check_chronology(ob_id, ob_name, row)
                issues_found += _check_upgrade_path(ob_id, ob_name, row,
                                                    valid_ob_ids)

            # Slot & Element Validation
            issues_found += _check_squad_slots(ob_id, ob_name, row,
                                               valid_elem_ids)

        # 3. UPGRADE LOOP PASS: Catch multi-level circular references
        issues_found += _check_for_loops(upgrade_map, ob_names)

        # Output formatting bug fixed here (swapped variables)
        if issues_found == 0:
            log.info("%d OBs Checked - _ob.csv Consistency Check Passed.",
                     len(seen_ob_ids))
        else:
            log.info("%d OBs Checked - _ob.csv Consistency Check Failed: %d "
                     "issue(s) identified.",
                     len(seen_ob_ids), issues_found)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during consistency check: %s", e)
        return 0

    return issues_found
