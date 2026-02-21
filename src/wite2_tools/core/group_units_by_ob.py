"""
Unit to TOE(OB) Grouping Utility
===========================

This module parses a War in the East 2 (WiTE2) `_unit.csv` file and
groups all active units by their assigned Order of Battle TOE(OB) ID.

It utilizes a cache to ensure that the grouping operation only
needs to read the massive CSV file once per runtime, returning the
cached dictionary on subsequent calls.

Command Line Usage:
    python -m wite2_tools.cli group-units [--unit-file FILE]

Example:
    $ python -m wite2_tools.cli group-units
    Groups all active units by their assigned TOE(OB) ID and caches the
    mapping.
"""

import os
from collections import defaultdict
from typing import cast
from functools import cache

# Internal package imports
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger

# Initialize the log for this specific module
log = get_logger(__name__)


@cache
def group_units_by_ob(unit_file_path: str) -> dict[int, list[str]]:
    """
    Groups all active units by their TOE(OB) type ID. Returns a dictionary
    mapping the TOE(OB) ID to a list of unit names.
    """
    # Declare a defaultdict where every new key automatically starts with
    # an empty list []
    # Key: TOE(OB) ID (int), Value: List of Unit Names (list[str])
    ob_ids_to_units: dict[int, list[str]] = defaultdict(list)

    # Check if file exists
    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return ob_ids_to_units

    try:
        log.info("Building Unit to TOE(OB) grouping cache from: '%s'",
                 os.path.basename(unit_file_path))
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip the DictReader object

        for item in unit_gen:
            # Cast the yielded item to satisfy static type checkers
            _, row = cast(tuple[int, dict], item)

            unit_type = int(row.get('type', '0'))
            if unit_type == 0:
                continue

            unit_name = row.get('name', 'Unk').strip()

            # defaultdict creates the list automatically if it's missing
            ob_ids_to_units[unit_type].append(unit_name)

        # Log the summary instead of printing every single row
        log.info("Successfully grouped units into %d unique OBs.",
                 len(ob_ids_to_units))

        # Relegate the granular details to the DEBUG level to prevent console
        # spam
        for unit_type, units in sorted(ob_ids_to_units.items()):
            log.debug("TOE(OB) ID %d is used by %d units: %s...",
                      unit_type, len(units), ', '.join(units[:3]))

    except (OSError, IOError, ValueError, KeyError) as e:
        log.exception("Grouping failed: %s", e)

    return ob_ids_to_units
