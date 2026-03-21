"""
Scans active units for excess logistical stores (ammo, supplies, fuel,
vehicles). The detection threshold flags any unit where its current stockpile
is greater than a specified ratio multiplied by its calculated need (e.g.,
`ammo > ratio * aNeed`). The ratio defaults to the EXCESS_RESOURCE_MULTIPLIER
(typically 5.0).

Active units (where `type` != 0) meeting this condition are output to the
console in a formatted table, detailing their ID, Name, Nationality, current
amount, needed amount, and the calculated overage ratio.

Command Line Usage:
    python -m wite2_tools.cli scan-excess [-h] [-d DATA_DIR] \\
        [resource {(a)mmo,(s)upplies,(f)uel,(v)ehicles} [ratio RATIO]

Arguments:
    resource (str): Specifies which resource to scan for.
                    Choices are '(a)mmo', '(s)upplies', '(f)uel',
                    or '(v)ehicles'.  Defaults to (a)mmo.
    ratio (float):  The multiplier used against the base need to determine
                    excess. Defaults to 5.0.

Example:
    $ python -m wite2_tools.cli scan-excess f 3.5
    Scans the unit file and prints a table of all units where `fuel` > 3.5 * `fNeed`.
"""
import os
from typing import cast, Dict

# Internal package imports
from wite2_tools.constants import EXCESS_RESOURCE_MULTIPLIER
from wite2_tools.generator import get_csv_dict_stream
from wite2_tools.utils import (
    get_logger,
    parse_int,
    parse_str
)
from wite2_tools.utils.get_name import get_nat_abbr

# Initialize the log for this specific module
log = get_logger(__name__)


def _scan_excess_resource(unit_file_path: str,
                          resource_col: str,
                          need_col: str,
                          resource_name: str,
                          ratio: float) -> int:
    """
    Generic helper to scan for excess logistical stores.
    Logic: If resource > (EXCESS_RESOURCE_MULTIPLIER * need),
           print row, id, name, nat, resource, and need.
    """
    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return -1

    matches_found:int = 0
    total_resources:int = 0
    # only consider positive ratios
    ratio = abs(ratio)

    try:
        unit_stream = get_csv_dict_stream(unit_file_path)

        print(f"\nScanning '{os.path.basename(unit_file_path)}'"
              f" for excess {resource_name}.")
        # Print Header for the Console Output
        print(f"\n{'ID':<6} | {'Name':<20} | {'Nat':^5} |"
              f" {resource_name:^10} | 'Need':^8 | {'Ratio':^9}")
        print("-" * 85)

        for item in unit_stream.rows:
            # Cast the yielded item to satisfy static type checkers
            _, row = cast(tuple[int, Dict[str,str]], item)

            # 1. Convert to numbers (int) for math comparison
            resource:int = parse_int(row.get(resource_col))
            total_resources += resource
            resource_need:int = parse_int(row.get(need_col))
            # Fallback: If a unit reports 0 need, treat it as 1.
            # This prevents division by zero while still catching
            # zero-need units that are hoarding massive amounts of resources.
            if resource_need == 0:
                resource_need = 1
            u_type:int = parse_int(row.get("type"))
            # only consider valid types
            if u_type == 0:
                continue

            # 2. Apply the Logic: Is resource greater than ratio times need?
            if resource > (ratio * resource_need):
                # 3. Extract ID, Name, and NAT
                uid:int = parse_int(row.get("id"))
                u_name:str = parse_str(row.get('name'), 'Unk')
                u_nat:int = parse_int(row.get("nat"))
                u_nat_abbr:str = get_nat_abbr(u_nat)

                try:
                    actual_ratio = resource / resource_need
                except ZeroDivisionError:
                    actual_ratio = float('inf')

                # 4. Print the row
                print(f"{uid:<6} | {u_name:20.20s} |"
                      f" {u_nat_abbr:^5} | {resource:>10} |"
                      f" {resource_need:>8} | {actual_ratio:>9.2f}")
                matches_found += 1

        if matches_found <= 0:
            print(f"\nNo units met the condition ("
                  f"{resource_name} > {ratio} * {need_col}).")
        else:
            print(f"\n{resource_name} Scan complete.\n"
                  f"Unit(s) with {ratio:.2%} {resource_name}: {matches_found}")
            print(f"Total {resource_name} in all Units: {total_resources:,}\n")

    except (OSError, ValueError, KeyError) as e:
        log.exception("An error occurred during scanning: %s", e)
        return -1

    return matches_found


# ==========================================
# PUBLIC API WRAPPERS
# ==========================================

def scan_units_for_excess_ammo(unit_file_path: str,
                               ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, 'ammo', 'aNeed', 'Ammo', ratio)

def scan_units_for_excess_supplies(unit_file_path: str,
                                   ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, 'sup', 'sNeed', 'Supplies', ratio)

def scan_units_for_excess_fuel(unit_file_path: str,
                               ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, 'fuel', 'fNeed', 'Fuel', ratio)

def scan_units_for_excess_vehicles(unit_file_path: str,
                                   ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, 'truck', 'vNeed', 'Vehicles', ratio)
