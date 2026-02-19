"""
Module for identifying units with excessive logistical stores in WiTE2 CSV files.

This module scans a War in the East 2 (WiTE2) `_unit` CSV file to locate active
units holding resources far beyond their standard requirements. It evaluates
four specific logistical categories: ammunition, supplies, fuel, and vehicles.

The detection threshold is hardcoded to flag any unit where its current stockpile
is greater than 5 times its calculated need (e.g., `ammo > 5 * aNeed`).

Active units (where `type` != 0) meeting this condition are output to the console
in a formatted table, detailing their ID, Name, Nationality, current amount,
needed amount, and the calculated overage ratio.

Command Line Usage:
    python scan_unit_for_excess.py [--operation {ammo,supplies,fuel,vehicles}]

Arguments:
    --operation: Specifies which resource to scan for.
                 Choices are 'ammo' (default), 'supplies', 'fuel', or 'vehicles'.

Example:
    $ python scan_unit_for_excess.py --operation fuel
    Scans the unit file and prints a table of all units where `fuel` > 5 * `fNeed`.
"""
import os
import argparse
from typing import cast

# Internal package imports
from wite2_tools.constants import EXCESS_RESOURCE_MULTIPLIER
from wite2_tools.paths import CONF_UNIT_FULL_PATH
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.lookups import get_nat_abbr
from wite2_tools.utils.logger import get_logger

# Initialize the log for this specific module
log = get_logger(__name__)


def _scan_excess_resource(unit_file_path: str, resource_col: str, need_col: str, display_name: str) -> int:
    """
    Generic helper to scan for excess logistical stores.
    Logic: If resource > (EXCESS_RESOURCE_MULTIPLIER * need), print row, id, name, nat, resource, and need.
    """
    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    matches_found = 0

    try:
        unit_gen = read_csv_dict_generator(unit_file_path)
        next(unit_gen) # Skip DictReader object

        print(f"\nScanning '{os.path.basename(unit_file_path)}' for excess {display_name.lower()}.")
        # Print Header for the Console Output
        print(f"\n{'Row':<6} | {'ID':<6} | {'Name':<20} | {'Nat':^5} | {display_name:^10} | {need_col:^10} | {'Ratio':<8}")
        print("-" * 85)

        for item in unit_gen:
            # Cast the yielded item to satisfy static type checkers
            row_idx, row = cast(tuple[int, dict], item)

            # 1. Get raw string values
            raw_resource = row.get(resource_col, '0')
            raw_need = row.get(need_col, '0')
            raw_unit_type = row.get('type', '0')

            # 2. Convert to numbers (int) for math comparison
            try:
                resource_val = int(raw_resource)
                need_val = int(raw_need)
                unit_type_val = int(raw_unit_type)
            except ValueError:
                # Skip rows where data isn't a number
                continue

            if unit_type_val == 0:
                continue

            # 3. Apply the Logic: Is resource greater than 5 times need?
            if resource_val > (EXCESS_RESOURCE_MULTIPLIER * need_val):

                # 4. Extract ID, Name, and NAT
                unit_id = int(row.get('id', '0'))
                unit_name = row.get('name', 'Unk')
                unit_nat = row.get('nat', '0')
                unit_country_str = get_nat_abbr(int(unit_nat))

                try:
                    ratio = resource_val / need_val
                except ZeroDivisionError:
                    ratio = float('inf')

                # 5. Print the row
                print(f"{row_idx:<6} | {unit_id:<6} | {unit_name:20.20s} | {unit_country_str:^5} | {resource_val:>10} | {need_val:>10} | {ratio:>8.2f}")
                matches_found += 1

        if matches_found == 0:
            print(f"\nNo rows met the condition ({display_name} > 5 * {need_col}).")
        else:
            print(f"\nScan complete. Found {matches_found} unit(s) with excess {display_name.lower()}.")

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


# --- MAIN EXECUTION ---
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Scans units for excess items and displays listing")
    parser.add_argument("--operation", choices=["ammo", "supplies", "fuel", "vehicles"], default="ammo",
                        help="The operation to perform (default: ammo)")

    args = parser.parse_args()

    # following uses currently configured path value(s)
    if args.operation == "ammo":
        scan_units_for_excess_ammo(CONF_UNIT_FULL_PATH)
    elif args.operation == "supplies":
        scan_units_for_excess_supplies(CONF_UNIT_FULL_PATH)
    elif args.operation == "fuel":
        scan_units_for_excess_fuel(CONF_UNIT_FULL_PATH)
    elif args.operation == "vehicles":
        scan_units_for_excess_vehicles(CONF_UNIT_FULL_PATH)