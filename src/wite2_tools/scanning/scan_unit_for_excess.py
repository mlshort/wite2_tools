"""
Module for identifying units with excessive logistical stores in WiTE2
CSV files.

This module scans a War in the East 2 (WiTE2) `_unit` CSV file to locate
active units holding resources far beyond their standard requirements. It
evaluates four specific logistical categories: ammunition, supplies, fuel,
and vehicles.

The detection threshold is hardcoded to flag any unit where its current
stockpile is greater than 5 times its calculated need
(e.g., `ammo > 5 * aNeed`).

Active units (where `type` != 0) meeting this condition are output to the
console in a formatted table, detailing their ID, Name, Nationality,
current amount, needed amount, and the calculated overage ratio.

Command Line Usage:
    python -m wite2_tools.cli scan-excess [-h] [-d DATA_DIR] \
        [--operation {ammo,supplies,fuel,vehicles}]

Arguments:
    operation (str): Specifies which resource to scan for. Choices are
                     'ammo' (default), 'supplies', 'fuel', or 'vehicles'.

Example:
    $ python -m wite2_tools.cli scan-excess --operation fuel

    Scans the unit file and prints a table of all units where
    `fuel` > 5 * `fNeed`.
"""
import os
from typing import cast

# Internal package imports
from wite2_tools.constants import EXCESS_RESOURCE_MULTIPLIER
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import (
    get_nat_abbr,
    get_logger,
    parse_int,
    parse_str
)

# Initialize the log for this specific module
log = get_logger(__name__)


def _scan_excess_resource(unit_file_path: str,
                          resource_col: str,
                          need_col: str,
                          display_name: str) -> int:
    """
    Generic helper to scan for excess logistical stores.
    Logic: If resource > (EXCESS_RESOURCE_MULTIPLIER * need),
           print row, id, name, nat, resource, and need.
    """
    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    matches_found = 0

    try:
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen)  # Skip DictReader object

        print(f"\nScanning '{os.path.basename(unit_file_path)}'"
              f" for excess {display_name.lower()}.")
        # Print Header for the Console Output
        print(f"\n{'Row':<6} | {'ID':<6} | {'Name':<20} | {'Nat':^5} |"
              f" {display_name:^10} | {need_col:^10} | {'Ratio':<8}")
        print("-" * 85)

        for item in unit_gen:
            # Cast the yielded item to satisfy static type checkers
            row_idx, row = cast(tuple[int, dict], item)

            # 1. Convert to numbers (int) for math comparison
            resource = parse_int(row.get(resource_col), 0)
            resource_need = parse_int(row.get(need_col), 0)
            utype = parse_int(row.get("type"))

            if utype == 0:
                continue

            # 2. Apply the Logic: Is resource greater than 5 times need?
            if resource > (EXCESS_RESOURCE_MULTIPLIER * resource_need):

                # 3. Extract ID, Name, and NAT
                uid = parse_int(row.get("id"))
                uname = parse_str(row.get('name'), 'Unk')
                u_nat = parse_int(row.get("nat"))
                u_nat_abbr = get_nat_abbr(u_nat)

                try:
                    ratio = resource / resource_need
                except ZeroDivisionError:
                    ratio = float('inf')

                # 4. Print the row
                print(f"{row_idx:<6} | {uid:<6} | {uname:20.20s} |"
                      f" {u_nat_abbr:^5} | {resource:>10} |"
                      f" {resource_need:>10} | {ratio:>8.2f}")
                matches_found += 1

        if matches_found == 0:
            print(f"\nNo rows met the condition ("
                  f"{display_name} > 5 * {need_col}).")
        else:
            print(f"\nScan complete. Found {matches_found} "
                  "unit(s) with excess {display_name.lower()}.")

    except (OSError, ValueError, KeyError) as e:
        log.exception("An error occurred during scanning: %s", e)

    return matches_found


# ==========================================
# PUBLIC API WRAPPERS
# ==========================================


def scan_units_for_excess_ammo(unit_file_path: str) -> int:
    return _scan_excess_resource(unit_file_path, 'ammo', 'aNeed', 'Ammo')


def scan_units_for_excess_supplies(unit_file_path: str) -> int:
    return _scan_excess_resource(unit_file_path, 'sup', 'sNeed', 'Supplies')


def scan_units_for_excess_fuel(unit_file_path: str) -> int:
    return _scan_excess_resource(unit_file_path, 'fuel', 'fNeed', 'Fuel')


def scan_units_for_excess_vehicles(unit_file_path: str) -> int:
    return _scan_excess_resource(unit_file_path, 'truck', 'vNeed', 'Vehicles')
