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
* Full Upgrade Chain Tracing: Recursively follows the 'upgrade' column in
  the TOE(OB) data to ensure future targets are not falsely flagged.
* Nationality Filtering: Can isolate the audit to specific nations.
* High-Performance Caching: Provides `is_ob_orphaned` which caches sets in
  memory for O(1) lookups during batch processing.

Main Functions:
---------------
* find_unreferenced_ob_ids : Executes the core parsing and Set Difference
  logic, returning a set of all orphaned TOE(OB) IDs.

* is_ob_orphaned           : A globally cached, O(1) time-complexity
  verification function to check if a specific TOE(OB) ID is currently an
  orphan.

Command Line Usage:
    python -m wite2_tools.cli gen-orphans [-h] [-d DATA_DIR] \
        [--nat-codes CODE [CODE ...]]

Arguments:
    nat_codes:     (list of int, optional): Filter by nationality codes.

Example:
    $ python -m wite2_tools.cli find-orphaned_ob_ids --nat-codes 1 3

    Identifies all unreferenced (orphaned) TOE(OB) templates for
    German (1) and Italian (3) factions.

"""
import os
from functools import cache
from typing import Set

# Internal package imports
from wite2_tools.core.unit import Unit
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.get_type_name import get_ob_full_name
from wite2_tools.utils.parsing import (
    parse_int,
    parse_str
)

# Initialize the logger for this specific module
log = get_logger(__name__)


def find_orphaned_ob_ids(ob_file_path: str, unit_file_path: str,
                         nation_id=None) -> Set[int]:
    """
    Identifies IDs in the _ob CSV file that are never referenced by the 'type'
    or 'upgrade' columns in the _unit CSV file, further filtered by the
    nat_codes provided.
    """
    verbose_orphans: bool = True

    if not os.path.exists(ob_file_path) or not os.path.exists(unit_file_path):
        log.error("File error: One or both of the specified CSV files do not "
                  "exist.")
        return set()

    # complete set of TOE(OB) IDs
    all_ob_ids: Set[int] = set()
    # set of valid TOE(OB) IDs
    valid_ob_ids: Set[int] = set()
    ob_id_to_name: dict[int, str] = {}
    ob_id_upgrade: dict[int, int] = {}

    # set of TOE(OB) IDs directly referenced by units
    ob_ids_ref_by_unit: Set[int] = set()
    ob_ids_to_units: dict[int, list[Unit]] = {}

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
            "Scanning for Orphaned OBs.\n"
            "  TOE(OB) file: '%s'\n"
            "  Unit file: '%s'",
            ob_file_base_name,
            unit_file_base_name
        )

#    DATABASE SCHEMA (CSV-BASED)
#
#    Table: _ob.csv
#    - id (int): Primary Key
#    - type (int): OB type
#    - name (str): OB name
#    - upgrade (int): OB upgrade
#    ....
#
#    Table: _unit.csv
#    - id (int): Primary Key
#    - type (int): _unit.type Foreign Key -> _ob.id
#    - nat (int): Nat Code

        # 1. Parse the TOE(OB) file
        ob_gen = read_csv_dict_generator(ob_file_path)
        next(ob_gen)  # Skip DictReader header yield

        for _, row in ob_gen:
            ob_nation_id: int = parse_int(row.get('nat'), 0)

            if nat_filter is not None and ob_nation_id not in nat_filter:
                continue

            ob_id: int = parse_int(row.get('id'), 0)
            ob_type: int = parse_int(row.get('type'), 0)
            ob_upgrade: int = parse_int(row.get('upgrade'), 0)
            # Combine ob_name and ob_suffix
            ob_name = parse_str(row.get('name'), '')
            ob_suffix = parse_str(row.get('suffix'), '')
            ob_full_name = f"{ob_name} {ob_suffix}"

            if ob_id != 0:
                all_ob_ids.add(ob_id)
                ob_id_to_name[ob_id] = ob_full_name
                # the following are the valid OB IDs
                if ob_type != 0:
                    valid_ob_ids.add(ob_id)
                    if ob_upgrade != 0:
                        ob_id_upgrade[ob_id] = ob_upgrade

        # 2. Parse the Unit file
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip header
        ref_upgraded_id_count = 0

        for _, row in unit_gen:
            unit_nat: int = parse_int(row.get('nat'), 0)

            if nat_filter is not None and unit_nat not in nat_filter:
                continue

            unit_id: int = parse_int(row.get('id'), 0)

            # unit_type is the FK to ob_id / TOE(OB)
            unit_type: int = parse_int(row.get('type'), 0)
            unit_name: str = parse_str(row.get('name'), 'Unk')

            # do we have a valid unit?
            if unit_id != 0 and unit_type != 0:
                # if yes, then lets collect its data, if we haven't already
                if unit_type not in ob_ids_to_units:
                    ob_ids_to_units[unit_type] = []
                a_unit = Unit(unit_id, unit_name, unit_type, unit_nat)
                # since we have a non-zero unit type, this unit
                # thinks it has an associated TOE(OB)
                # let's go with that for now...
                ob_ids_to_units[unit_type].append(a_unit)

                ob_ids_ref_by_unit.add(unit_type)
                current_upgrade = unit_type
                while current_upgrade in ob_id_upgrade:
                    next_upgrade = ob_id_upgrade[current_upgrade]

                    # If we've already marked this as referenced,
                    # the rest of the chain is also covered
                    if next_upgrade in ob_ids_ref_by_unit:
                        break

                    ob_ids_ref_by_unit.add(next_upgrade)
                    current_upgrade = next_upgrade

                # Trace the full upgrade chain
                current_upgrade = unit_type
                while current_upgrade in ob_id_upgrade:
                    next_upgrade = ob_id_upgrade[current_upgrade]

                    if next_upgrade in ob_ids_ref_by_unit:
                        break

                    ob_ids_ref_by_unit.add(next_upgrade)
                    ref_upgraded_id_count += 1
                    log.debug(
                        "New Upgrade Ref mapped from '%s': %d -> %d",
                        unit_name,
                        current_upgrade,
                        next_upgrade
                    )
                    current_upgrade = next_upgrade

        # 3. Find IDs in the TOE(OB) set that are NOT in the Referenced set
        orphaned_ob_ids = valid_ob_ids - ob_ids_ref_by_unit
        # 3. Find IDs that are Referenced, but are NOT valid
        # The result is the set of Invalid OB IDs that are being referenced
        inv_ref_ob_ids = ob_ids_ref_by_unit - valid_ob_ids

        # 4. Logging Results
        if orphaned_ob_ids:
            sorted_orphans = sorted(list(orphaned_ob_ids), key=int)
            log.warning("Found %d Orphan OBs (Unused). Listing below:",
                        len(orphaned_ob_ids))
            # verbose logging ?
            if verbose_orphans:
                for orphan_id in sorted_orphans:
                    ob_full_name = get_ob_full_name(
                        ob_file_path,
                        orphan_id
                    )
                    # listing of Orphaned OBs
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

        if inv_ref_ob_ids:
            print(f"inv_ref_ob_ids {inv_ref_ob_ids}")
            inv_ob_ids = all_ob_ids - valid_ob_ids
            print(f"inv_ob_ids {inv_ob_ids}")
            # print(f"ob_ids_to_unit_dat {ob_ids_to_unit_dat}")
            for inv_ob_id in inv_ref_ob_ids:
                # the following should get the set of units
                # associated with the OB ID
                units_with_inv_ob_id = ob_ids_to_units.get(inv_ob_id)
                print(f" units_with_inv_ob_id {units_with_inv_ob_id}")
                if units_with_inv_ob_id is not None:
                    for orphan_unit in units_with_inv_ob_id:
                        log.error(
                            "Invalid Reference: TOE(OB) ID '%d' does not"
                            " exist! "
                            "Used by unit: %d %s",
                            inv_ob_id,
                            orphan_unit.unit_id,
                            orphan_unit.name)

            print(f"CRITICAL: {len(inv_ref_ob_ids)} units point to "
                  "non-existent "
                  "TOE(OB) IDs. Check logs.")

        if not orphaned_ob_ids and not inv_ref_ob_ids:
            log.info(
                "Cross-reference perfect: All OBs used and all "
                "Units point to valid OBs."
            )
            print("Success: Data is 100% synchronized.")
        else:
            msg = (
                "Analysis complete: For Nats {%s}, there are %d OBs, "
                "%d Orphan OBs and %d invalid refs found."
            )
            print(
                msg % (
                    nat_filter,
                    len(valid_ob_ids),
                    len(orphaned_ob_ids),
                    len(inv_ref_ob_ids)
                )
            )

        return orphaned_ob_ids

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
    return find_orphaned_ob_ids(ob_file_path, unit_file_path,
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
