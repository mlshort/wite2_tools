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

# Internal package imports
from wite2_tools.constants import EXCESS_RESOURCE_MULTIPLIER
from wite2_tools.generator import get_csv_list_stream, CSVListStream
from wite2_tools.models import (
    UnitColumn,
    UnitRow
)
from wite2_tools.utils import get_logger, get_nat_abbr
from wite2_tools.utils.parsing import parse_row_int

# Initialize the log for this specific module
log = get_logger(__name__)


def _scan_excess_resource(
    unit_file_path: str,
    resource_idx: int,
    need_idx: int,
    resource_name: str,
    ratio: float
) -> int:
    """
    Internal helper to scan the _unit.csv file for any active unit whose
    stockpile exceeds (ratio * need). Outputs a formatted table to the
    console and returns the number of matches found.
    """
    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    matches_found = 0
    total_resources = 0

    try:
        unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

        print(f"\nScanning '{os.path.basename(unit_file_path)}' for excess "
              f"{resource_name} (Threshold: > {ratio}x Need)...")

        # Table Header
        print(f"\n{'ID':<6} | {'Name':<20} | {'Nat':^5} | "
              f"{'Current':^10} | {'Needed':^8} | {'% Of Need':^9}")
        print("-" * 85)

        for _, row in unit_stream.rows:
            unit = UnitRow(row)
            u_type = unit.TYPE #parse_row_int(row, UnitColumn.TYPE)
            uid = unit.ID #parse_row_int(row, UnitColumn.ID)

            # Skip non-active or unassigned units
            if u_type == 0 or uid == 0:
                continue

            u_name = unit.NAME #parse_row_str(row, UnitColumn.NAME, "Unk")
            u_nat = unit.NAT #parse_row_int(row, UnitColumn.NAT)

            # Access resource counts safely via physical integer indices
            resource_val = parse_row_int(row, resource_idx)
            need_val = parse_row_int(row, need_idx)

            total_resources += resource_val

            # Determine if this unit breaches the excess threshold
            threshold = ratio * need_val
            if resource_val > threshold:
                pct_str = "N/A"
                if need_val > 0:
                    pct = (resource_val / need_val) * 100
                    pct_str = f"{pct:.1f}%"

                nat_str = get_nat_abbr(u_nat)

                print(f"{uid:>6} | {u_name:<22.22s} | {nat_str:<5.5s} | "
                      f"{resource_val:>9,d} | {need_val:>9,d} | {pct_str:>10s}")
                matches_found += 1

        if matches_found == 0:
            print(f"No active units found meeting the condition ("
                  f"{resource_name} > {ratio} * Need).")
        else:
            print(f"\n{resource_name} Scan complete.\n"
                  f"Unit(s) with {ratio:.2%} {resource_name}: {matches_found}")
            print(f"Total {resource_name} in all Units: {total_resources:,}\n")

    except (OSError, ValueError, IndexError) as e:
        log.exception("An error occurred during scanning: %s", e)
        return 0

    return matches_found


# ==========================================
# PUBLIC API WRAPPERS
# ==========================================

def scan_units_for_excess_ammo(unit_file_path: str,
                               ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, UnitColumn.AMMO,
                                 UnitColumn.A_NEED, 'Ammo', ratio)


def scan_units_for_excess_supplies(unit_file_path: str,
                                   ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, UnitColumn.SUP,
                                  UnitColumn.S_NEED, 'Supplies', ratio)


def scan_units_for_excess_fuel(unit_file_path: str,
                               ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, UnitColumn.FUEL,
                                 UnitColumn.F_NEED, 'Fuel', ratio)


def scan_units_for_excess_vehicles(unit_file_path: str,
                                   ratio: float = EXCESS_RESOURCE_MULTIPLIER) -> int:
    return _scan_excess_resource(unit_file_path, UnitColumn.TRUCK,
                                 UnitColumn.V_NEED, 'Vehicles', ratio)