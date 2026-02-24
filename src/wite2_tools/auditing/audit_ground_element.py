"""
Ground Element Audit Utility
============================

This module provides functionality to audit War in the East 2 (WiTE2)
`_ground.csv` files. It scans the ground elements database to ensure structural
and logical consistency, identifying issues such as duplicate WIDs, missing or
invalid element types, and malformed size or manpower data.

Note: This module utilizes a list-based generator to handle CSV files that
contain duplicate column headers (e.g., multiple 'id' columns).

Command Line Usage:
    python -m wite2_tools.cli audit-ground [-h] [-d DATA_DIR]

Example:
    $ python -m wite2_tools.cli audit-ground

    Scans the default _ground CSV file to ensure all type IDs are valid
    and logs any logical errors.
"""

import os

# Internal package imports
from wite2_tools.constants import (
    MAX_GROUND_MEN,
    GroundColumn,
    GroundElementType
)

from wite2_tools.generator import read_csv_list_generator
from wite2_tools.utils import (
    get_logger,
    get_ground_elem_class_name,
    parse_int,
    parse_str
)
from wite2_tools.utils.formatting import format_ref, audit_msg

# Initialize the log for this specific module
log = get_logger(__name__)


def _check_ground_type(g_id: int,
                       g_name: str,
                       raw_type: str) -> tuple[int, str]:
    """
    Validates the type ID and returns (issues_found, element_class_name).
    """
    issues = 0
    ref = format_ref("WID", g_id, g_name)

    try:
        ground_type = int(raw_type)
        if ground_type == 0:
            return 0, ""  # Skip inactive

        element_class_name = get_ground_elem_class_name(ground_type)

        if "Unk" in element_class_name:
            log.warning("%s: uses undefined Type %d",
                        ref, ground_type)
            issues += 1
        return issues, element_class_name

    except (ValueError, TypeError):
        log.error("%s: 'type' value '%s' is not a valid integer.",
                  ref, raw_type)
        return 1, ""


def _check_ground_stats(g_id: int,
                        g_name: str,
                        element_class_name: str,
                        row: str | list[str]) -> int:
    """Validates physical size and manpower assignments safely."""
    issues = 0
    ref = format_ref("WID", g_id, g_name)

    try:
        ground_type = parse_int(row[GroundColumn.TYPE], 0)
        ground_size = parse_int(row[GroundColumn.SIZE], 0)
        ground_men = parse_int(row[GroundColumn.MEN], 0)

        elem = GroundElementType(ground_type)
        if elem.is_combat_element:

            if ground_size == 0:
                log.warning("%s: %s has ZERO size",
                            ref, element_class_name)
                issues += 1

            if ground_men == 0:
                log.warning("%s: %s has no men assigned",
                            ref, element_class_name)
                issues += 1

            elif ground_men > MAX_GROUND_MEN:
                log.warning("%s: %s has %d > %d men assigned",
                            ref, element_class_name,
                            ground_men, MAX_GROUND_MEN)
                issues += 1

    except (ValueError, TypeError) as e:
        log.error("%s: Value error in stat parsing: %s", ref, e)
    except IndexError:
        log.error("%s: Row data is severely truncated during stat check.",
                  ref)
        issues += 1

    return issues


def audit_ground_element_csv(ground_file_path: str) -> int:
    """
    Scans a _ground CSV file for consistency and
    logically based on the ground_element_type_lookup.
    """
    if not os.path.exists(ground_file_path):
        log.error("Audit failed: File not found at %s", ground_file_path)
        return -1

    issues_found: int = 0
    seen_ground_ids: set[int] = set()

    # Define the minimum indices required for a safe primary parse
    idx_id = GroundColumn.ID
    idx_name = GroundColumn.NAME
    idx_type = GroundColumn.TYPE
    MIN_REQUIRED_COLS = max(idx_id, idx_name, idx_type) + 1

    try:
        file_name = os.path.basename(ground_file_path)
        log.info("--- Starting Ground Element Audit: '%s' ---", file_name)

        ground_gen = read_csv_list_generator(ground_file_path)
        next(ground_gen)  # Skip Header

        for row_idx, row in ground_gen:
            row_len = len(row)

            # Structural Safety Check
            if row_len < MIN_REQUIRED_COLS:
                log.error("Row %d: Truncated data (Len %d < Req %d).",
                          row_idx, row_len, MIN_REQUIRED_COLS)
                issues_found += 1
                continue

            try:
                g_id = parse_int(row[idx_id], 0)
                g_name = parse_str(row[idx_name], "Unk")
                ref = format_ref("WID", g_id, g_name)

                # 1. Uniqueness Check
                if g_id != 0 and g_id in seen_ground_ids:
                    log.error("%s: Duplicate ID detected", ref)
                    issues_found += 1
                    continue
                seen_ground_ids.add(g_id)

                # 2. Type and Stat Validation
                t_issues, element_class_name = _check_ground_type(
                    g_id, g_name, row[idx_type]
                )
                issues_found += t_issues

                if element_class_name:
                    idx_size = GroundColumn.SIZE
                    idx_men = GroundColumn.MEN
                    REQUIRED_STAT_COLS = max(idx_size, idx_men) + 1

                    if row_len >= REQUIRED_STAT_COLS:
                        issues_found += _check_ground_stats(
                            g_id, g_name, element_class_name, row
                        )
                    else:
                        log.warning("%s: Insufficient columns.", ref)
                        issues_found += 1

            except (IndexError, KeyError, ValueError) as e:
                log.error("Row %d: Failed due to %s",
                          row_idx, type(e).__name__)
                issues_found += 1

        log.info(audit_msg(file_name, issues_found, len(seen_ground_ids)))
        return issues_found

    except (OSError, IOError) as e:
        log.error("System error accessing file: %s", e)
        return -1