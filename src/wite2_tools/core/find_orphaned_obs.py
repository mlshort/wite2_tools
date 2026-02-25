"""
Orphaned Order of Battle (TOE(OB)) Identifier
========================================

This module cross-references War in the East 2 (WiTE2) `_ob.csv` and
`_unit.csv` files to identify unreferenced or "orphaned" TOE(OB) templates.

An TOE(OB) is considered an "orphan" if it exists in the TOE(OB) database but
is never actively assigned to a unit on the map, nor is it part of a valid
upgrade chain for an active unit. Conversely, this script also identifies
"invalid references," which occur when an active unit is assigned an TOE(OB) ID
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
    nat_codes: (list of int, optional): Filter by nationality codes.

Example:
    $ python -m wite2_tools.cli find-orphaned_ob_ids --nat-codes 1 3

    Identifies all unreferenced (orphaned) TOE(OB) templates for
    German (1) and Italian (3) factions.

"""
import os
from typing import Dict, Set, Optional, Sequence
from functools import cache

# Internal package imports
from wite2_tools.core.unit import Unit
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import get_logger
from wite2_tools.utils import format_header, format_list_item
from wite2_tools.utils import (
    get_ob_full_name,
    get_ob_suffix
)
from wite2_tools.utils import (
    parse_int,
    parse_str
)

# Initialize the logger for this specific module
log = get_logger(__name__)


def _parse_ob_data(ob_file_path: str, nat_filter: set[int] | None):
    """Parses the OB file and returns structured data for cross-referencing."""
    all_obs = set()
    active_obs = set()
    ob_id_to_name = {}
    ob_id_upgrade = {}

    ob_gen = read_csv_dict_generator(ob_file_path)
    next(ob_gen, None)

    for _, row in ob_gen:
        ob_nat: int = parse_int(row.get('nat'))
        if nat_filter is not None and ob_nat not in nat_filter:
            continue

        ob_id: int = parse_int(row.get('id'))
        if ob_id == 0:
            continue

        all_obs.add(ob_id)
        ob_id_to_name[ob_id] = f"{parse_str(row.get('name'))} {parse_str(row.get('suffix'))}"

        if parse_int(row.get('type')) != 0:
            active_obs.add(ob_id)
            upgrade_id:int = parse_int(row.get('upgrade'))
            if upgrade_id != 0:
                ob_id_upgrade[ob_id] = upgrade_id

    return all_obs, active_obs, ob_id_to_name, ob_id_upgrade


def _trace_unit_references(unit_file_path: str, ob_file_path: str,
                           nat_filter: set[int] | None, ob_id_upgrade: dict[int, int]):
    """Parses unit file and traces the full TOE upgrade chain."""
    obs_ref_by_unit = set()
    ob_to_units: Dict[int, Set[Unit]] = {}

    unit_gen = read_csv_dict_generator(unit_file_path)
    next(unit_gen, None)

    for _, row in unit_gen:
        u_nat: int = parse_int(row.get('nat'))
        if nat_filter is not None and u_nat not in nat_filter:
            continue

        u_id: int = parse_int(row.get('id'))
        u_type: int = parse_int(row.get('type'))

        if u_id != 0 and u_type != 0:
            if u_type not in ob_to_units:
                ob_to_units[u_type] = set()

            u_full_name = f"{parse_str(row.get('name'), 'Unk')} {get_ob_suffix(ob_file_path, u_type)}"
            ob_to_units[u_type].add(Unit(u_id, u_full_name, u_type, u_nat))

            # Trace upgrade chain
            curr = u_type
            while curr != 0:
                if curr in obs_ref_by_unit:
                    break
                obs_ref_by_unit.add(curr)
                curr = ob_id_upgrade.get(curr, 0)

    return obs_ref_by_unit, ob_to_units

def find_orphaned_obs(ob_file_path: str, unit_file_path: str,
                         nat_codes: Optional[int | Sequence[int]] = None) -> Set[int]:
    """Identifies orphaned TOE(OB) IDs and invalid references."""
    if not all(os.path.exists(f) for f in [ob_file_path, unit_file_path]):
        log.error("Required CSV files not found.")
        return set()

    # Standardize nationality filter
    if nat_codes is None:
        nat_filter = None
    else:
        nat_filter = {int(nat_codes)} if isinstance(nat_codes, (int, str)) else {int(n) for n in nat_codes}

    try:
        # 1. Parse OB Data
        all_obs, active_obs, _, ob_id_upgrade = _parse_ob_data(ob_file_path, nat_filter)

        # 2. Parse Unit Data & Trace Upgrades
        obs_ref_by_unit, ob_to_units = _trace_unit_references(
            unit_file_path, ob_file_path, nat_filter, ob_id_upgrade
        )

        # 3. Calculate Differences
        orphaned_ob_ids = active_obs - obs_ref_by_unit
        inv_ref_ob_ids = obs_ref_by_unit - active_obs

        _report_results(orphaned_ob_ids, inv_ref_ob_ids, ob_to_units, ob_file_path)

        log.info("Analysis complete for Nat Filter %s. Found %d orphans.", nat_filter, len(orphaned_ob_ids))
        return orphaned_ob_ids

    except (ValueError, OSError, KeyError) as exc:
        log.exception("Cross-reference failed: %s", exc)
        return set()

def find_orphaned_ob_ids2(ob_file_path: str,
                         unit_file_path: str,
                         nat_codes: int | list[int] | None = None) -> Set[int]:
    """
    Identifies IDs in the _ob CSV file that are never referenced by the 'type'
    or 'upgrade' columns in the _unit CSV file, further filtered by the
    nat_codes provided.
    """
    verbose_orphans: bool = True

    if not os.path.exists(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return set()

    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return set()

    # complete set of TOE(OB) IDs
    all_obs: Set[int] = set()
    # set of valid TOE(OB) IDs
    active_obs: Set[int] = set()
    ob_id_to_name: dict[int, str] = {}
    ob_id_upgrade: dict[int, int] = {}

    # set of TOE(OB) IDs directly referenced by units
    obs_ref_by_unit: Set[int] = set()
    ob_to_units: dict[int, Set[Unit]] = {}

    # Standardize nation_id to a set for efficient lookup
    if nat_codes is not None:
        if isinstance(nat_codes, (int, str)):
            nat_filter = {int(nat_codes)}
        else:
            nat_filter = {int(n) for n in nat_codes}
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
#    - type (int): TOE(OB) type
#    - name (str): TOE(OB) name
#    - upgrade (int): TOE(OB) upgrade
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
            ob_nat: int = parse_int(row.get('nat'))

            if nat_filter is not None and ob_nat not in nat_filter:
                continue

            ob_id: int = parse_int(row.get('id'))
            ob_type: int = parse_int(row.get('type'))
            ob_upgrade: int = parse_int(row.get('upgrade'))
            # Combine ob_name and ob_suffix
            ob_name = parse_str(row.get('name'))
            ob_suffix = parse_str(row.get('suffix'))
            ob_full_name = f"{ob_name} {ob_suffix}"

            if ob_id != 0:
                all_obs.add(ob_id)
                ob_id_to_name[ob_id] = ob_full_name
                # the following are the valid TOE(OB) IDs
                if ob_type != 0:
                    active_obs.add(ob_id)
                    if ob_upgrade != 0:
                        ob_id_upgrade[ob_id] = ob_upgrade

        # 2. Parse the Unit file
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip header
        ref_upgraded_id_count = 0

        for _, row in unit_gen:
            u_nat: int = parse_int(row.get('nat'))

            if nat_filter is not None and u_nat not in nat_filter:
                continue

            uid: int = parse_int(row.get('id'))

            # utype is the FK to ob_id / TOE(OB)
            utype: int = parse_int(row.get('type'))
            uname: str = parse_str(row.get('name'), 'Unk')
            usuffix: str = get_ob_suffix(ob_file_path, utype)
            ufull_name: str = f"{uname} {usuffix}"

            # do we have a valid unit?
            if uid != 0 and utype != 0:
                # if yes, then lets collect its data, if we haven't already
                if utype not in ob_to_units:
                    ob_to_units[utype] = set()
                a_unit = Unit(uid, ufull_name, utype, u_nat)
                # since we have a non-zero unit type, this unit
                # thinks it has an associated TOE(OB)
                # let's go with that for now...
                ob_to_units[utype].add(a_unit)

                obs_ref_by_unit.add(utype)
                current_upgrade = utype
                while current_upgrade in ob_id_upgrade:
                    next_upgrade = ob_id_upgrade[current_upgrade]

                    # If we've already marked this as referenced,
                    # the rest of the chain is also covered
                    if next_upgrade in obs_ref_by_unit:
                        break

                    obs_ref_by_unit.add(next_upgrade)
                    current_upgrade = next_upgrade

                # Trace the full upgrade chain
                current_upgrade = utype
                while current_upgrade in ob_id_upgrade:
                    next_upgrade = ob_id_upgrade[current_upgrade]

                    if next_upgrade in obs_ref_by_unit:
                        break

                    obs_ref_by_unit.add(next_upgrade)
                    ref_upgraded_id_count += 1
                    log.debug(
                        "New Upgrade Ref mapped from '%s': %d -> %d",
                        uname,
                        current_upgrade,
                        next_upgrade
                    )
                    current_upgrade = next_upgrade

        # 3. Find IDs in the TOE(OB) set that are NOT in the Referenced set
        orphaned_ob_ids = active_obs - obs_ref_by_unit
        # 4. Find IDs that are Referenced, but are NOT active or valid
        # The result is the set of Invalid TOE(OB) IDs that are being referenced
        inv_ref_ob_ids = obs_ref_by_unit - active_obs

        # 5. Logging Results
        if orphaned_ob_ids:
            print(format_header("Unused TOE(OB) Report"))
            sorted_orphans = sorted(list(orphaned_ob_ids), key=int)

            print(f"Total Orphaned TOE(OB)s Found: {len(orphaned_ob_ids)}\n")

            # verbose logging ?
            if verbose_orphans:
                for orphan_id in sorted_orphans:
                    ob_full_name = get_ob_full_name(
                        ob_file_path,
                        orphan_id
                    )
                    # Print cleanly to console instead of logging every line
                    print(format_list_item(f"[{orphan_id}] {ob_full_name}"))
            else:
                chunk_size = 20
                for i in range(0, len(sorted_orphans), chunk_size):
                    chunk = sorted_orphans[i:i + chunk_size]
                    chunk_str = ", ".join(map(str, chunk))
                    end_idx = min(i + chunk_size, len(sorted_orphans))
                    print(f"   Orphans [{i + 1} to {end_idx}]: {chunk_str}")

            # Keep a single summary line for the actual log file
            log.warning("Found %d Orphan (Unused) OBs.", len(orphaned_ob_ids))

        num_units_with_inv_ob_ids = 0
        if inv_ref_ob_ids:
            print("\n" + "="*40)
            print(" ORPHAN REPORT: Invalid TOE(OB) IDs being Referenced.")
            print("="*40)

            # Sort the IDs so the output is consistent and easy to read
            for inv_ob_id in sorted(inv_ref_ob_ids):
                units_with_inv_ob_id = ob_to_units.get(inv_ob_id, [])

                if units_with_inv_ob_id:
                    num_units_with_inv_ob_ids += len(units_with_inv_ob_id)
                    print(f"\n❌ Ref to Bad TOE(OB):[{inv_ob_id}]")
                    print(f"   Affected Units: ({len(units_with_inv_ob_id)}):")

                    for orphan_unit in units_with_inv_ob_id:
                        print(f"   • [{orphan_unit.uid}] {orphan_unit.name}")

            # Keep a single summary line for the actual log file
            if num_units_with_inv_ob_ids > 0:
                log.error("CRITICAL: %d Units are using Invalid TOE(OB) IDs.",
                          num_units_with_inv_ob_ids)

        if not orphaned_ob_ids and not inv_ref_ob_ids:
            log.info(
                "Cross-reference perfect: All OBs used and all "
                "Units point to valid OBs."
            )
            print("Success: Data is 100% synchronized.")
        else:
            msg = (
                "Analysis complete: using Nat Filter {%s} \n"
                "   All OBs:                   %d\n"
                "   Valid OBs:                 %d\n"
                "   Orphan OBs (Unused):       %d\n"
                "   Invalid TOE(OB) IDs Referenced: %d\n"
                "   Total Units Affected:      %d"
            )

            # Use 'num_units_with_inv_ob_ids' from the loop above, or
            #  default to 0
            # if the inv_ref_ob_ids block didn't execute
            total_affected = num_units_with_inv_ob_ids if inv_ref_ob_ids else 0

            print(
                msg % (
                    nat_filter,
                    len(all_obs),
                    len(active_obs),
                    len(orphaned_ob_ids),
                    # counts the number of missing templates (IDs)
                    len(inv_ref_ob_ids),
                    total_affected
                )
            )

        return orphaned_ob_ids

    except (ValueError, IOError, KeyError) as e:
        log.exception(
            "An error occurred during cross-reference: %s",
            e
        )
        return set()

def _report_results(orphans: Set[int], invalid: Set[int],
                    unit_map: Dict[int, Set[Unit]], ob_path: str):
    """Handles console output for the orphan report."""
    if orphans:
        print(format_header("Unused TOE(OB) Report"))
        print(f"Total Orphaned TOE(OB)s Found: {len(orphans)}\n")
        for oid in sorted(orphans):
            print(format_list_item(f"[{oid}] {get_ob_full_name(ob_path, oid)}"))

    if invalid:
        print("\n" + "="*40 + "\n ORPHAN REPORT: Invalid TOE(OB) IDs Referenced.\n" + "="*40)
        for iid in sorted(invalid):
            affected = unit_map.get(iid, [])
            if affected:
                print(f"\n❌ Ref to Bad TOE(OB):[{iid}] (Affected Units: {len(affected)})")
                for u in affected:
                    print(f"   • [{u.uid}] {u.name}")


@cache
def _get_cached_orphans(ob_file_path: str, unit_file_path: str,
                        nat_code_tuple: tuple[int, ...]) -> set[int]:
    """
    Private helper: Runs the heavy orphan logic and caches the resulting set.
    """

    log.info("Building Orphan TOE(OB) cache for nat_codes %s...",
             nat_code_tuple)
    return find_orphaned_obs(ob_file_path, unit_file_path,
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
