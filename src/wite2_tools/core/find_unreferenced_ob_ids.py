"""
Orphaned Order of Battle (OB) Identifier
========================================

This module cross-references War in the East 2 (WiTE2) `_ob.csv` and
`_unit.csv` files to identify unreferenced or "orphaned" TOE(OB) templates.

An TOE(OB) is considered an "orphan" if it exists in the TOE(OB) database but
is never actively assigned to a unit on the map, nor is it part of a valid
upgrade chain for an active unit. Conversely, this script also identifies
"invalid references," which occur when an active unit is assigned an OB ID
that does not exist in the database.

Core Features:
--------------
* Full Upgrade Chain Tracing: Recursively follows the 'upgrade' column in the
  TOE(OB) data to ensure future upgrade targets are not falsely flagged as
  orphans.
* Nationality Filtering: Can isolate the audit to specific nations (e.g.,
  Germany, Italy).
* High-Performance Caching: Provides the `is_ob_orphaned` function, which
  caches the calculated sets in memory. This allows other scripts to query
  thousands of TOE(OB) IDs instantly without re-parsing the large CSV files.

Main Functions:
---------------
* find_unreferenced_ob_ids : Executes the core parsing and Set Difference
  logic, returning a set of all orphaned TOE(OB) IDs.
* is_ob_orphaned           : A globally cached, O(1) time-complexity
  verification function
                             to check if a specific TOE(OB) ID is currently an
                             orphan.

Command Line Usage:
    python -m wite2_tools.cli find-orphans [--ob-file FILE] [--unit-file FILE]
    [--nat-codes NAT_CODES [NAT_CODES ...]]

Example:
    $ python -m wite2_tools.cli find-orphans --nat-codes 1 3 Identifies all
    unreferenced (orphaned) TOE(OB) templates for German (1) and Italian (3)
    factions.
"""
import os
from functools import cache
from typing import Set

# Internal package imports
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.get_type_name import get_ob_full_name
from wite2_tools.utils.parsing import parse_int

# Initialize the logger for this specific module
log = get_logger(__name__)


def find_unreferenced_ob_ids(ob_file_path: str, unit_file_path: str,
                             nation_id=None) -> Set[int]:
    """
    Identifies IDs in the _ob CSV file that are never referenced by the 'type'
    or 'upgrade' columns in the _unit CSV file, further filtered by the
    nat_codes provided.
    """
    detailed_orphans = True

    if not os.path.exists(ob_file_path) or not os.path.exists(unit_file_path):
        log.error("File error: One or both of the specified CSV files do not "
                  "exist.")
        return set()

    # complete set of TOE(OB) IDs
    ob_ids: Set[int] = set()
    ob_id_to_name: dict[int, str] = {}
    ob_id_upgrade: dict[int, int] = {}

    # set of TOE(OB) IDs directly referenced by units
    ref_by_unit_ob_ids: Set[int] = set()
    ob_ids_to_unit_names: dict[int, list[str]] = {}

    # Standardize nation_id to a set for efficient lookup
    if nation_id is not None:
        if isinstance(nation_id, (int, str)):
            nat_filter = {int(nation_id)}
        else:
            nat_filter = {int(n) for n in nation_id}
    else:
        nat_filter = None

    try:
        # Extract filenames for logging
        ob_file_base_name = os.path.basename(ob_file_path)
        unit_file_base_name = os.path.basename(unit_file_path)
        log.info(
            "Scanning for orphan OBs.\n"
            "  TOE(OB) file: '%s'\n"
            "  Unit file: '%s'",
            ob_file_base_name,
            unit_file_base_name
        )

        # 1. Parse the TOE(OB) file
        ob_gen = read_csv_dict_generator(ob_file_path)
        next(ob_gen)  # Skip DictReader header yield

        for _, row in ob_gen:
            ob_nation_id = parse_int(row.get('nat'))

            if nat_filter is not None and ob_nation_id not in nat_filter:
                continue

            ob_id = int(row.get('id') or '0')
            ob_type = int(row.get('type') or '0')
            ob_upgrade = int(row.get('upgrade') or '0')
            # Combine ob_name and ob_suffix
            ob_name = row.get('name', '').strip()
            ob_suffix = row.get('suffix', '').strip()
            ob_full_name = f"{ob_name} {ob_suffix}"

            if ob_id != 0 and (ob_type != 0):
                ob_ids.add(ob_id)
                ob_id_to_name[ob_id] = ob_full_name
                if ob_upgrade != 0:
                    ob_id_upgrade[ob_id] = ob_upgrade

        # 2. Parse the Unit file
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip header
        ref_upgraded_id_count = 0

        for _, row in unit_gen:
            unit_nation_id = parse_int(row.get('nat'))

            if nat_filter is not None and unit_nation_id not in nat_filter:
                continue

            unit_id = int(row.get('id') or '0')
            unit_type = int(row.get('type') or '0')  # 'type' maps to TOE(OB)
            unit_nameid = row.get('name', 'Unk') + f"({unit_id})"

            if unit_type != 0:
                if unit_type not in ob_ids_to_unit_names:
                    ob_ids_to_unit_names[unit_type] = []
                ob_ids_to_unit_names[unit_type].append(unit_nameid)
                ref_by_unit_ob_ids.add(unit_type)

                # Trace the full upgrade chain
                current_upgrade = unit_type
                while current_upgrade in ob_id_upgrade:
                    next_upgrade = ob_id_upgrade[current_upgrade]

                    if next_upgrade in ref_by_unit_ob_ids:
                        break

                    ref_by_unit_ob_ids.add(next_upgrade)
                    ref_upgraded_id_count += 1
                    log.debug(
                        "New Upgrade Ref mapped from '%s': %d -> %d",
                        unit_nameid,
                        current_upgrade,
                        next_upgrade
                    )
                    current_upgrade = next_upgrade

        # 3. Find IDs in TOE(OB) set that are NOT in the Referenced set
        orphans = ob_ids - ref_by_unit_ob_ids
        invalids = ref_by_unit_ob_ids - ob_ids

        # 4. Logging Results
        if orphans:
            sorted_orphans = sorted(list(orphans), key=int)
            log.warning("Found %d Orphan OBs (Unused). Listing below:",
                        len(orphans))

            if detailed_orphans:
                for orphan_id in sorted_orphans:
                    ob_full_name = get_ob_full_name(
                        ob_file_path,
                        orphan_id
                    )
                    log.warning(
                        " TOE(OB) (%d) '%s'",
                        orphan_id,
                        ob_full_name
                    )
            else:
                chunk_size = 20
                for i in range(0, len(sorted_orphans), chunk_size):
                    chunk = sorted_orphans[i:i + chunk_size]
                    chunk_str = ", ".join(map(str, chunk))
                    end_idx = min(i + chunk_size, len(sorted_orphans))
                    log.warning(
                        "  Orphans [%d to %d]: %s",
                        i + 1,
                        end_idx,
                        chunk_str
                    )

        if invalids:
            for inv_id in invalids:
                # Safely get affected units without KeyError
                default_msg = ["Unknown (Added via Upgrade Chain)"]
                affected_units = ob_ids_to_unit_names.get(
                    inv_id,
                    default_msg
                )
                log.error(
                    "Invalid Reference: TOE(OB) ID '%d' does not exist! "
                    "Used by units: %s",
                    inv_id,
                    affected_units
                )

            print(f"CRITICAL: {len(invalids)} units point to non-existent "
                  "TOE(OB) IDs. Check logs.")

        if not orphans and not invalids:
            log.info(
                "Cross-reference perfect: All OBs used and all "
                "Units point to valid OBs."
            )
            print("Success: Data is 100% synchronized.")
        else:
            msg = (
                "Analysis complete: For Nats %s, there are %d OBs, "
                "%d Orphan OBs and %d invalid refs found."
            )
            print(
                msg % (
                    nat_filter,
                    len(ob_ids),
                    len(orphans),
                    len(invalids)
                )
            )

        return orphans

    except (ValueError, IOError, KeyError) as e:
        log.exception(
            "An error occurred during cross-reference: %s",
            e
        )
        return set()


@cache
def _get_cached_orphans(ob_file_path: str, unit_file_path: str,
                        nat_code_tuple: tuple) -> set[int]:
    """
    Private helper: Runs the heavy orphan logic and caches the resulting set.
    """

    log.info("Building Orphan TOE(OB) cache for nat_codes %s...",
             nat_code_tuple)
    return find_unreferenced_ob_ids(ob_file_path, unit_file_path,
                                    nat_code_tuple)


def is_ob_orphaned(ob_file_path: str,
                   unit_file_path: str,
                   ob_id_to_check: int,
                   nation_id=None) -> bool:
    """
    Public function: Converts arguments to hashables and queries the cached
    set.
    """

    # 1. Convert the unhashable list/set into a hashable tuple
    nat_tuple: tuple[int, ...]

    if nation_id is None:
        nat_tuple = ()
    elif isinstance(nation_id, (int, str)):
        nat_tuple = (int(nation_id),)
    else:
        nat_tuple = tuple(sorted(int(n) for n in nation_id))

    # 2. Retrieve the cached set (only calculates once per unique file/nat
    # combination)
    orphan_set = _get_cached_orphans(ob_file_path, unit_file_path, nat_tuple)

    # 3. Perform O(1) lookup
    return ob_id_to_check in orphan_set
