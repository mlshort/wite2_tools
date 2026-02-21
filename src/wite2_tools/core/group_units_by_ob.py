"""
Unit to TOE(OB) Grouping Utility
===============================

This module parses a War in the East 2 (WiTE2) `_unit.csv` file and
groups all active units by their assigned Order of Battle TOE(OB) ID.
It utilizes a cache to ensure that the grouping operation only
needs to read the massive CSV file once per runtime, returning the
cached dictionary on subsequent calls.

Core Features:
--------------
* Nationality Filtering: Supports isolating groups by specific nationality
  codes (e.g., 1 for Germany, 2 for Finland) to analyze faction-specific
  TOE deployments.
* Formatted Output: Automatically generates a structured console table
  displaying the TOE(OB) ID, Unit ID, resolved Nationality abbreviation,
  and Unit Name.
* Memory Efficiency: Utilizes generator-based streaming to handle
  massive scenario files without high memory overhead.

Command Line Usage:
    python -m wite2_tools.cli group-units [-h] [--unit-file PATH] \
        [--nat-codes CODE [CODE ...]] [active_only]

Arguments:
    unit_file_path (str): The path to the WiTE2 _unit CSV file.
    nat_codes (list of int, optional): Filter by nationality codes.
    active_only (bool, optional): Skips inactive units (type=0) if True.
                                  Defaults to True.

Example:
    $ python -m wite2_tools.cli group-units --nat-codes 1 3

    Groups active German and Italian units by their assigned TOE(OB) ID
    and displays a formatted summary table.
"""

import os
from collections import defaultdict
from typing import cast, Optional, Union, Iterable
from functools import cache

# Internal package imports
from wite2_tools.core.unit import Unit
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.lookups import get_nat_abbr
from wite2_tools.utils.parsing import (
    parse_int,
    parse_str
)

# Initialize the log for this specific module
log = get_logger(__name__)


@cache
def group_units_by_ob(
    unit_file_path: str,
    active_only: bool = True,
    nation_id: Optional[Union[int, str, Iterable[Union[int, str]]]] = None
) -> dict[int, list[Unit]]:
    """
    Groups units by TOE(OB) ID with optional nationality filtering.

    Args:
        unit_file_path (str): The absolute or relative path to the WiTE2 _unit
                CSV file.
        active_only (bool, optional): If True, skips units that have a TOE(OB)
                type of 0. Defaults to True.
        nation_id (int, str, or Iterable, optional): A single nationality code
                or a collection of codes to filter the results. Defaults to
                None.

    Returns:
        dict[int, list[Unit]]: A dictionary mapping the TOE(OB) ID to a list of
                matching Unit objects.
    """
    ob_ids_to_units = defaultdict(list)

    # Standardize nation_id to a set for efficient lookup
    if nation_id is not None:
        if isinstance(nation_id, (int, str)):
            nat_filter = {int(nation_id)}
        else:
            nat_filter = {int(n) for n in nation_id}
    else:
        nat_filter = None

    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return dict(ob_ids_to_units)

    try:
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip DictReader header

        for item in unit_gen:
            _, row = cast(tuple[int, dict], item)

            u_type = parse_int(row.get('type'), 0)
            u_nat = parse_int(row.get('nat'), 0)

            # Apply filters: Activity and Nationality
            if active_only and u_type == 0:
                continue
            if nat_filter is not None and u_nat not in nat_filter:
                continue

            u_id = parse_int(row.get('id'), 0)
            u_name = parse_str(row.get('name'), 'Unk')

            unit = Unit(unit_id=u_id, name=u_name, unit_type=u_type, nat=u_nat)
            ob_ids_to_units[u_type].append(unit)

        print_unit_table(ob_ids_to_units)

    except (OSError, IOError, ValueError, KeyError) as e:
        log.exception("Grouping failed: %s", e)

    return dict(ob_ids_to_units)


def print_unit_table(grouped_data: dict[int, list[Unit]]):
    """
    Prints a formatted table of all units organized by Type
    """
    header = f"{'TOE(OB)':<8} | {'UNIT ID':<8} | {'NAT':<5} | {'UNIT NAME'}"
    separator = "-" * 50

    print(f"\n{separator}")
    print(header)
    print(separator)

    for unit_type in sorted(grouped_data.keys()):
        units = grouped_data[unit_type]
        for unit in sorted(units, key=lambda x: x.unit_id):
            nat_str = get_nat_abbr(unit.nat)  # Resolve Nat code to abbr
            print(f"{unit.unit_type:<8} | {unit.unit_id:<8} | "
                  f"{nat_str:<5} | {unit.name}")
        print(separator)
