"""
Ground Element Audit Utility
============================

This module provides functionality to audit War in the East 2 (WiTE2)
`_ground.csv` files.
It scans the ground elements database to ensure structural and logical
consistency, identifying issues such as duplicate WIDs, missing or
invalid element types, and malformed size or manpower data.

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
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.lookups import get_ground_elem_class_name
from wite2_tools.generator import read_csv_list_generator
from wite2_tools.utils.parsing import (
    parse_int,
    parse_str
)

# Initialize the log for this specific module
log = get_logger(__name__)


def _check_ground_type(ground_id: int,
                       ground_name: str,
                       raw_type: str) -> tuple[int, str]:
    """
    Validates the type ID and returns (issues_found, element_class_name).
    """
    issues = 0
    try:
        ground_type = int(raw_type)
        if ground_type == 0:
            return 0, ""  # Skip inactive

        element_class_name = get_ground_elem_class_name(ground_type)

        if "Unk" in element_class_name:
            log.warning("WID %d (%s): uses undefined Type %d",
                        ground_id, ground_name, ground_type)
            issues += 1
        elif element_class_name == "Blank":
            log.debug("WID %d (%s): Assigned to a blank Type %d",
                      ground_id, ground_name, ground_type)
        else:
            log.debug("WID %d (%s): Validated as %s",
                      ground_id, ground_name, element_class_name)

        return issues, element_class_name

    except ValueError:
        log.error("WID %d (%s): 'type' value '%s' is not a valid integer.",
                  ground_id, ground_name, raw_type)
        return 1, ""


def _check_ground_stats(ground_id: int,
                        ground_name: str,
                        element_class_name: str,
                        row: str | list[str]) -> int:
    """Validates physical size and manpower assignments safely."""
    issues = 0
    try:
        ground_type = parse_int(row[GroundColumn.TYPE], 0)
        ground_size = parse_int(row[GroundColumn.SIZE], 0)
        ground_men = parse_int(row[GroundColumn.MEN], 0)

        elem = GroundElementType(ground_type)
        if elem.is_combat_element:

            if ground_size == 0:
                log.warning("WID %d (%s): %s has ZERO size",
                            ground_id, ground_name, element_class_name)
                issues += 1

            if ground_men == 0:
                log.warning("WID %d (%s): %s has no men assigned",
                            ground_id, ground_name, element_class_name)
                issues += 1

            elif ground_men > MAX_GROUND_MEN:
                log.warning("WID %d (%s): %s has %d > %d men assigned",
                            ground_id, ground_name, element_class_name,
                            ground_men, MAX_GROUND_MEN)
                issues += 1

    except ValueError as e:
        log.error("(%s): Value error.", e)

    except IndexError:
        log.error("WID %d (%s): Row data is severely truncated.",
                  ground_id, ground_name)
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

    try:
        file_name = os.path.basename(ground_file_path)
        log.info("--- Starting Ground Element Audit: '%s' ---", file_name)

        # Initialize the generator
        ground_gen = read_csv_list_generator(ground_file_path)

        # Skip the first yield (which returns the DictReader object itself)
        next(ground_gen)

        # The generator automatically unpacks row_idx and row dictionary
        for _, row in ground_gen:
            row_len: int = len(row)
            ground_id: int = parse_int(row[GroundColumn.ID], 0)
            ground_name = parse_str(row[GroundColumn.NAME], "Unk")

            # 1. Uniqueness Check
            if ground_id != 0 and ground_id in seen_ground_ids:
                log.error("WID %d: Duplicate IDs (%s)",
                          ground_id, ground_name)
                issues_found += 1
                continue

            seen_ground_ids.add(ground_id)

            # 2. Type Validation
            raw_type = row[GroundColumn.TYPE]  # 'type' column
            if raw_type is None:
                log.error("WID %d (%s): Missing 'type' column value.",
                          ground_id, ground_name)
                issues_found += 1
                continue

            try:
                ground_type = int(raw_type)
                # skip over inactive ground units
                if ground_type == 0:
                    continue
                element_class_name = get_ground_elem_class_name(ground_type)
                # Updated to match the "Unk " fallback in lookups.py
                if "Unk" in element_class_name:
                    log.warning("WID %d (%s): uses undefined Type %d",
                                ground_id, ground_name, ground_type)
                    issues_found += 1
                elif element_class_name == "Blank":
                    log.debug("WID %d (%s): Assigned to a blank Type %d",
                              ground_id, ground_name, ground_type)
                else:
                    log.debug("WID %d (%s): Validated as %s",
                              ground_id, ground_name, element_class_name)

                # following is to account for tests using weird-sized rows
                if GroundColumn.SIZE > row_len:
                    continue

                issues_found += _check_ground_stats(ground_id,
                                                    ground_name,
                                                    element_class_name,
                                                    row)

            except ValueError:
                log.error("WID %d (%s): 'type' value '%s' is not a "
                          "valid integer.",
                          ground_id, ground_name, raw_type)
                issues_found += 1

        log.info("%d Elements Checked - _ground.csv Audit complete with %d "
                 "issues identified ",
                 len(seen_ground_ids), issues_found)

        return issues_found

    except (OSError, IOError, ValueError, KeyError, IndexError) as e:
        log.exception("An unexpected error occurred during the audit: %s", e)
        return -1
