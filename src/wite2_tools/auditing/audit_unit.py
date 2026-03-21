
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

# Internal package imports
from wite2_tools.generator import CSVListStream, get_csv_list_stream
from wite2_tools.utils import get_logger, parse_row_int
from wite2_tools.utils.formatting import (
    format_ref,
    format_header,
    format_coords,
    format_status,
    audit_msg,
    completion_msg
)
from wite2_tools.models import (
    UnitRow,
    UnitColumn,
    U_SQD_SLOTS,
    U_SQD0_COL,
    U_SQD_NUM0_COL,
    U_ATTRS_PER_SQD
)
from wite2_tools.utils.get_valid_ids import (
    get_valid_ground_elem_ids,
    get_valid_unit_ids
)

from wite2_tools.config import ENCODING_TYPE

from wite2_tools.NatCodes import NatCodes

from wite2_tools.constants import (
    MIN_X,
    MAX_X,
    MIN_Y,
    MAX_Y,
    MAX_GAME_TURNS
)


# Initialize the logger for this specific module
log = get_logger(__name__)


def _check_nat(row: list[str],
               uid: int,
               uname: str) -> int:
    issues = 0

    unit = UnitRow(row)
    u_nat = unit.NAT
    if u_nat not in NatCodes:
        ref = format_ref("UID", uid, uname)
        log.warning("%s: Invalid NAT %s",
                        ref, u_nat)
        issues += 1

    return issues



def _check_coords(row: list[str],
                  uid: int,
                  uname: str) -> int:
    """
    Helper to validate all coordinate sets (x, y, tx, ty, etc.).
    """
    issues = 0
    coord_pairs = [(UnitColumn.X, UnitColumn.Y), (UnitColumn.TX, UnitColumn.TY),
                    (UnitColumn.ATX, UnitColumn.ATY), (UnitColumn.PTX, UnitColumn.PTY)]

    for cx, cy in coord_pairs:
        x = parse_row_int(row, cx, -1)
        y = parse_row_int(row, cy, -1)

        # NEW: Ignore holding/production pool coordinates (0, 0)
        if x == 0 and y == 0:
            continue

        if not (MIN_X <= x <= MAX_X and MIN_Y <= y <= MAX_Y):
            # Uniform Identifier and Coordinate formatting
            ref = format_ref("UID", uid, uname)
            coords = format_coords(x, y)
            log.warning("%s: Invalid coordinates %s",
                        ref, coords)
            issues += 1
    return issues


def _check_squads(
    row: list[str],
    valid_ground_element_ids: set[int],
    unit_ref: str,
    fix_ghosts: bool
) -> tuple[int, int]:
    """Scans all 32 squad slots for invalid element IDs (ghosts)."""
    issues = 0
    fixed = 0

    for i in range(U_SQD_SLOTS):
        sqd_col:int = U_SQD0_COL + (i * U_ATTRS_PER_SQD)
        num_col:int = U_SQD_NUM0_COL + (i * U_ATTRS_PER_SQD)
        wid = parse_row_int(row, sqd_col)
        qty = parse_row_int(row, num_col)

        if qty > 0 and wid not in valid_ground_element_ids:
            issues += 1
            msg = (f"{unit_ref} (Ghost Sqd): Slot {i} contains "
                   f"{qty} elements of invalid WID[{wid}].")

            if fix_ghosts:
                row[sqd_col] = "0"
                row[num_col] = "0"
                fixed += 1
                log.warning("%s %s", format_status("FIXED"), msg)
            else:
                log.warning(msg)

    return issues, fixed


def _check_hq_and_delay(
    row: list[str],
    valid_unit_ids: set[int],
    fallback_hq: int,
    unit_ref: str,
    relink_orphans: bool = False
) -> tuple[int, int]:
    """Validates command chain assignments and associated data."""
    issues = 0
    fixed = 0
    hhq_id = parse_row_int(row, UnitColumn.HHQ)

    if hhq_id not in valid_unit_ids and hhq_id != 0:
        issues += 1
        msg = f"{unit_ref} (Orphan): Assigned to invalid HQ[{hhq_id}]"

        if relink_orphans:
            row[UnitColumn.HHQ] = str(fallback_hq)
            fixed += 1
            log.warning(
                "%s %s -> Relinked to HQ[%d]",
                format_status("FIXED"), msg, fallback_hq
            )
        else:
            log.warning(msg)

    return issues, fixed


# pylint: disable=too-many-branches, too-many-statements, too-many-locals
def audit_unit_csv(
    unit_file_path: str,
    ground_file_path: str,
    active_only: bool = True,
    fix_ghosts: bool = False,
    relink_orphans: bool = False,
    fallback_hq: int = 0
) -> int:
    """
    Evaluates unit data for consistency and optionally applies fixes.
    """
    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    if not os.path.isfile(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return 0

    file_base = os.path.basename(unit_file_path)
    log.info(format_header(f"Task Start: Evaluating Unit file integrity: '{file_base}'"))

    valid_ground_element_ids: set[int] = get_valid_ground_elem_ids(ground_file_path)
    valid_unit_ids: set[int] = get_valid_unit_ids(unit_file_path, active_only)

    issues_found:int = 0
    ghosts_fixed:int = 0
    orphans_fixed:int = 0
    seen_unit_ids:set[int] = set()

    temp_file = None
    if fix_ghosts or relink_orphans:
        file_dir = os.path.dirname(unit_file_path)
        temp_file = NamedTemporaryFile(
            mode='w', newline='', delete=False, dir=file_dir,
            encoding=ENCODING_TYPE, suffix=".csv"
        )

    def _cleanup_temp() -> None:
        if temp_file and os.path.isfile(temp_file.name):
            try:
                temp_file.close()
                os.remove(temp_file.name)
            except OSError:
                pass

    try:
        unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

        writer = None
        if (fix_ghosts or relink_orphans) and temp_file:
            writer = csv.writer(temp_file, lineterminator='\n')
            writer.writerow(unit_stream.header)

        for _, row in unit_stream.rows:
            unit = UnitRow(row)
            uid:int = unit.ID
            uname:str = unit.NAME

            unit_ref: str = format_ref("UID", uid, uname)
            seen_unit_ids.add(uid)

            # --- Validation Helpers ---
            issues_found += _check_nat(row, uid, uname)
            issues_found += _check_coords(row, uid, uname)

            sqd_issues, sqd_fixed = _check_squads(
                row, valid_ground_element_ids, unit_ref, fix_ghosts
            )
            issues_found += sqd_issues
            ghosts_fixed += sqd_fixed

            hq_issues, hq_fixed = _check_hq_and_delay(
                row, valid_unit_ids, fallback_hq, unit_ref, relink_orphans
            )
            issues_found += hq_issues
            orphans_fixed += hq_fixed

            if writer and temp_file:
                writer.writerow(row)

        if (fix_ghosts or relink_orphans) and temp_file:
            temp_file.close()
            if ghosts_fixed > 0 or orphans_fixed > 0:
                log.info(
                    completion_msg(
                        "Repair", ghosts_fixed + orphans_fixed, file_base
                    )
                )
                os.replace(temp_file.name, unit_file_path)
            else:
                log.info("Fix Mode Complete: No issues found to repair.")
                os.remove(temp_file.name)

        if issues_found == 0:
            log.info(
                "%d Units Checked - _unit.csv Consistency Check Passed.",
                len(seen_unit_ids)
            )
            log.info(audit_msg(file_base, issues_found, len(seen_unit_ids)))
        else:
            log.warning(
                "%d Units Checked - Check Failed with %d issues.",
                len(seen_unit_ids), issues_found
            )

    except OSError as e:
        log.error("File access error for '%s'. Details: %s", file_base, e)
        _cleanup_temp()
        return 0
    except ValueError as e:
        log.error("Data conversion failed in '%s'. Details: %s", file_base, e)
        _cleanup_temp()
        return 0
    except KeyError as e:
        log.error("Missing expected dictionary key in '%s': %s", file_base, e)
        _cleanup_temp()
        return 0
    except IndexError as e:
        log.error("Truncated row or missing column in '%s': %s", file_base, e)
        _cleanup_temp()
        return 0
    except TypeError as e:
        log.error("Type error processing '%s'. Details: %s", file_base, e)
        _cleanup_temp()
        return 0
    finally:
        for handler in log.handlers:
            handler.flush()

    return issues_found