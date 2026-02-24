
"""
Unit Placement and Integrity Audit Utility
==========================================

This module provides robust validation routines to ensure the structural
and logical consistency of War in the East 2 (WiTE2) `_unit.csv` files.

It is designed to detect common data corruption issues, manual editing errors,
and referential integrity breaks before they cause runtime crashes in the
game engine. It also features automated repair tools to fix broken command
chains and clean up invalid squad data.

Key Validation Logic
--------------------
* Referential Integrity: Verifies that Ground Element WIDs referenced in
  squad slots (0-31) actually exist in the master `_ground` file.
* Ghost Squad Detection: Scans for and optionally fixes slots that have
  a quantity assigned but no valid Element ID (which causes game instability).
* Command Chain Verification: Identifies "orphaned" units assigned to an HQ
  that does not exist or has been deleted, with optional auto-relinking.
* Coordinate Bounds: Ensures unit X/Y coordinates fall within the valid
  game map dimensions (0-378, 0-354), safely ignoring (0,0) for the pool.

Command Line Usage:
    python -m wite2_tools.cli audit-unit [-h] [-d DATA_DIR] [--fix-ghosts] \
        [--relink-orphans] [--fallback-hq HQ_ID]
"""
import csv
import os
from tempfile import NamedTemporaryFile
from typing import Set

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import (
     parse_int,
     parse_str
)
from wite2_tools.constants import (
    MAX_SQUAD_SLOTS,
    MIN_X,
    MAX_X,
    MIN_Y,
    MAX_Y,
    MAX_GAME_TURNS
)
from wite2_tools.utils import get_logger
from wite2_tools.utils import get_valid_ground_elem_ids, get_valid_unit_ids
from wite2_tools.utils import (
    format_ref,
    format_coords,
    audit_msg,
    completion_msg
)

# Initialize the logger for this specific module
log = get_logger(__name__)


def is_greater_than_zero(value) -> bool:
    try:
        return float(value) > 0
    except ValueError:
        # Returns False if the cell is text, empty, or None
        return False


def _check_coords(uid: int, uname: str, row: dict) -> int:
    """Helper to validate all coordinate sets (x, y, tx, ty, etc.)."""
    issues = 0
    coord_pairs = [('x', 'y'), ('tx', 'ty'), ('ax', 'ay'), ('ptx', 'pty')]

    for cx, cy in coord_pairs:
        x = parse_int(row.get(cx), -1)
        y = parse_int(row.get(cy), -1)

        # NEW: Ignore holding/production pool coordinates (0, 0)
        if x == 0 and y == 0:
            continue

        if not (MIN_X <= x <= MAX_X and MIN_Y <= y <= MAX_Y):
            # Uniform Identifier and Coordinate formatting
            ref = format_ref("UID", uid, uname)
            coords = format_coords(x, y)
            log.warning("%s: Invalid %s/%s coordinates %s",
                        ref, cx, cy, coords)
            issues += 1
    return issues


def _check_squads(uid: int,
                  uname: str,
                  row: dict,
                  valid_elem_ids: set,
                  fix_ghosts: bool) -> tuple[int, int]:
    """Helper to validate squad integrity and detect ghost squads."""
    issues = 0
    fixed = 0
    ref = format_ref("UID", uid, uname)

    for i in range(MAX_SQUAD_SLOTS):
        sqd_id_col, sqd_num_col = f"sqd.u{i}", f"sqd.num{i}"
        sqd_id = parse_int(row.get(sqd_id_col), 0)
        qty = parse_int(row.get(sqd_num_col), 0)

        if sqd_id != 0 and sqd_id not in valid_elem_ids:
            log.error("%s: Slot %d has invalid Elem WID[%d].",
                    ref, i, sqd_id)
            issues += 1

        if qty != 0 and sqd_id == 0:
            log.error("%s: Ghost Squad detected in Slot %d (Qty: %d).",
                      ref, i, qty)
            issues += 1
            if fix_ghosts:
                row[sqd_num_col] = "0"
                fixed += 1
    return issues, fixed


def _check_hq_and_delay(uid: int,
                        uname: str,
                        row: dict,
                        valid_active_unit_ids: set,
                        relink_orphans: bool,
                        fallback_hq: int) -> tuple[int, int]:
    """Helper to validate HQ attachment logic and deployment delays."""
    issues = 0
    fixed = 0
    ref: str = format_ref("UID", uid, uname)
    unit_hhq = parse_int(row.get('hhq'), 0)

    if unit_hhq == uid:
        hq_type = parse_int(row.get('hq'), 0)
        if hq_type not in (0, 1):
            log.warning("%s: Self-reporting as HQ with Type(%d).",
                     ref, hq_type)
            issues += 1

    if unit_hhq != 0:
        # NEW: Check if the HQ exists AND is currently active
        if unit_hhq not in valid_active_unit_ids:
            log.error("%s: Unit reports to an invalid or inactive HQ (%d).",
                      ref, unit_hhq)
            issues += 1

            # NEW: Auto-repair orphaned units
            if relink_orphans and fallback_hq > 0:
                log.info(" -> FIXING: Relinking Unit %d to Fallback HQ %d",
                         uid, fallback_hq)
                row['hhq'] = str(fallback_hq)
                fixed += 1

    u_delay = parse_int(row.get("delay"), 0)
    if u_delay > MAX_GAME_TURNS:
        log.warning("%s: Delay(%d) exceeds MAX_GAME_TURNS(%d).",
                    ref, u_delay, MAX_GAME_TURNS)
        issues += 1

    return issues, fixed


def audit_unit_csv(unit_file_path: str,
                   ground_file_path: str,
                   active_only: bool = True,
                   fix_ghosts: bool = False,
                   relink_orphans: bool = False,
                   fallback_hq: int = 0) -> int:
    """
    Validates a WiTE2 _unit CSV file for structural integrity and game-logic
    errors.

    Args:
        unit_file_path: Path to the unit CSV.
        ground_file_path: Path to the ground element CSV (for ID validation).
        active_only: If True, skips units with id="0" or type="0".
        fix_ghosts: If True, automatically zeroes out squad quantities where
                    the ID is 0.
    """
    issues_found: int = 0
    ghosts_fixed: int = 0
    orphans_fixed: int = 0
    seen_unit_ids: Set[int] = set()
    temp_file = None
    file_base = os.path.basename(unit_file_path)

    try:
        log.info("Task Start: Evaluating Unit file integrity: '%s'", file_base)
        # get the set of valid ground element ids
        valid_elem_ids = get_valid_ground_elem_ids(ground_file_path)
        valid_unit_ids = get_valid_unit_ids(unit_file_path, active_only)

        unit_gen = read_csv_dict_generator(unit_file_path, 2)
        reader = next(unit_gen)

        # Initialize temp file if fix mode is enabled
        writer = None
        if fix_ghosts or relink_orphans:
            temp_file = NamedTemporaryFile(mode='w', delete=False,
                                           dir=os.path.dirname(unit_file_path),
                                           newline='', encoding=ENCODING_TYPE)
            header = reader.fieldnames  # type: ignore
            writer = csv.DictWriter(temp_file,
                                    fieldnames=header)  # type: ignore
            writer.writeheader()

        log.info("Evaluating Unit file consistency:'%s' (Active Only:%s) (Fix Mode:%s)",
                 file_base, active_only, (fix_ghosts or relink_orphans))

        for _, row in unit_gen:
            uid = parse_int(row.get("id"), 0)
            utype = parse_int(row.get("type"), 0)

            if active_only and (uid == 0 or utype == 0):
                if writer:
                    writer.writerow(row)
                continue

            uname = parse_str(row.get("name"), "Unk")
            ref = format_ref("UID", uid, uname)

            # 1. Primary Key Uniqueness
            if uid in seen_unit_ids:
                log.error("%s: Duplicate Unit ID for '%s'",
                          ref, uname)
                issues_found += 1
            seen_unit_ids.add(uid)

            # 2. Coordinate Validation
            issues_found += _check_coords(uid, uname, row)

            # 3. Squad and Integrity Checks (Consolidated logic)
            s_issues, s_fixed = _check_squads(uid, uname, row,
                                            valid_elem_ids, fix_ghosts)
            issues_found += s_issues
            ghosts_fixed += s_fixed

            # 4. HQ & Delay Check
            hq_issues, hq_fixed = _check_hq_and_delay(uid, uname, row,
                                                      valid_unit_ids,
                                                      relink_orphans,
                                                      fallback_hq)
            issues_found += hq_issues
            orphans_fixed += hq_fixed

            if writer:
                writer.writerow(row)

        # Finalize and swap files if changes were made
        if (fix_ghosts or relink_orphans) and temp_file:
            temp_file.close()
            if ghosts_fixed > 0 or orphans_fixed > 0:
                log.info(completion_msg("Repair",
                                        ghosts_fixed + orphans_fixed,
                                        file_base))
                os.replace(temp_file.name, unit_file_path)
            else:
                log.info("Fix Mode Complete: No issues found to repair.")
                os.remove(temp_file.name)

        if issues_found == 0:
            log.info("%d Units Checked - _unit.csv Consistency Check Passed.",
                     len(seen_unit_ids))
            # Standardized Audit Summary
            log.info(audit_msg(file_base,
                               issues_found,
                               len(seen_unit_ids)))
        else:
            log.warning("%d Units Checked - _unit.csv Consistency Check Failed with %d issues.",
                        len(seen_unit_ids), issues_found)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during _unit.csv evaluation: %s", e)
        if temp_file and os.path.exists(temp_file.name):
            try:
                temp_file.close()
                os.remove(temp_file.name)
            except OSError:
                pass
        return -1

    return issues_found
