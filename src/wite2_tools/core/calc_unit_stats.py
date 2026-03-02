"""
    module still work-in-progress
"""
from typing import Dict, Any, List, Union, Tuple, TypedDict
import math


# Direct import to bypass __init__ export issues
from wite2_tools.generator import (
    CSVListStream,
    CSVDictStream,
    get_csv_dict_stream,
    get_csv_list_stream
)
from wite2_tools.utils.parsing import parse_int, parse_str
from wite2_tools.utils import get_ob_suffix, format_ref
from wite2_tools.constants import (
    MAX_SQUAD_SLOTS,
    GroundColumn,
    GroundElementType
)


# WITE2 Ground Element Data (Complete IDs 1-118)
# Format: {ID: {"name": str, "cv": int, "supNeed": int, "targetType": str}}
ELEMENT_DATA = {
    1: ( "Rifle Squad",  3,  4,  "Inf"),
    2: ( "Inf-AntiTank",  1,  1,  "Inf"),
    3: ( "Cavalry Squad",  3,  8,  "Inf"),
    4: ( "Machinegun",  1,  3,  "Inf"),
    5: ( "Mortar",  1,  8,  "Art"),
    6: ( "AntiTank Gun",  1,  6,  "Art"),
    7: ( "Mech-Inf Squad",  8,  9,  "Inf"),
    8: ( "Md Flak",  1,  10,  "Art"),
    9: ( "Artillery",  1,  25,  "Art"),
    10: ( "Naval Gun",  1,  40,  "Art"),
    11: ( "Armoured Car",  4,  6,  "AFV"),
    12: ( "Lt Tank",  7,  12,  "AFV"),
    13: ( "Md Tank",  9,  12,  "AFV"),
    14: ( "Hvy Tank",  9,  12,  "AFV"),
    15: ( "CS Tank",  8,  12,  "AFV"),
    16: ( "Motor-Inf Squad",  3,  4,  "Inf"),
    17: ( "Flame Tank",  9,  12,  "AFV"),
    18: ( "Assault Gun",  8,  12,  "AFV"),
    19: ( "Mech-Engr Squad",  8,  10,  "Inf"),
    20: ( "Engineer Squad",  3,  5,  "Inf"),
    21: ( "SP Artillery",  3,  35,  "AFV"),
    22: ( "SP Flak",  3,  12,  "AFV"),
    23: ( "HT AT-Gun",  3,  10,  "AFV"),
    24: ( "Mech-MG Section",  8,  10,  "Inf"),
    25: ( "HT CS-Mortar",  3,  11,  "AFV"),
    26: ( "Special Forces",  3,  4,  "Inf"),
    27: ( "Marine Commando",  3,  4,  "Inf"),
    28: ( "Airborne Engineer",  3,  5,  "Inf"),
    29: ( "SP AAMG",  1,  4,  "Art"),
    30: ( "AAMG",  1,  4,  "Inf"),
    31: ( "Rocket",  1,  20,  "Art"),
    32: ( "Hvy Artillery",  1,  45,  "Art"),
    33: ( "Lt Flak",  1,  5,  "Art"),
    34: ( "Hvy Flak",  1,  20,  "Art"),
    35: ( "Amphibious Tank",  3,  12,  "AFV"),
    36: ( "MSW Tank",  9,  12,  "AFV"),
    37: ( "Engineer Tank",  9,  12,  "AFV"),
    38: ( "Airborne Squad",  3,  4,  "Inf"),
    39: ( "SP Inf-Gun",  5,  12,  "AFV"),
    40: ( "SMG Squad",  3,  4,  "Inf"),
    41: ( "Carrier-Inf Squad",  3,  10,  "Inf"),
    42: ( "Air Landing Section",  3,  4,  "Inf"),
    43: ( "Hvy AT Gun",  1,  7,  "Art"),
    44: ( "Lt AT Gun",  1,  4,  "Art"),
    45: ( "Hvy Infantry Gun",  1,  9,  "Art"),
    46: ( "Lt Artillery",  1,  15,  "Art"),
    47: ( "Airborne Tank",  7,  12,  "AFV"),
    48: ( "Recon Jeep",  3,  5,  "Inf"),
    49: ( "Motorcycle Squad",  3,  5,  "Inf"),
    50: ( "Ski Squad",  3,  4,  "Inf"),
    51: ( "Security Squad",  3,  4,  "Inf"),
    52: ( "Partisan Squad",  2,  2,  "Inf"),
    53: ( "Naval Rifle Squad",  3,  4,  "Inf"),
    54: ( "Labour Squad",  1,  3,  "Inf"),
    55: ( "Md Field Gun",  1,  35,  "Art"),
    56: ( "SP Rocket Launcher",  3,  25,  "AFV"),
    57: ( "Lt Mortar",  1,  2,  "Inf"),
    58: ( "Hvy Mortar",  1,  12,  "Art"),
    59: ( "SP AntiTank Gun",  7,  12,  "AFV"),
    60: ( "Tank Destroyer",  8,  12,  "AFV"),
    61: ( "Hvy Tank Destroyer",  9,  12,  "AFV"),
    62: ( "Infantry Gun",  1,  7,  "Art"),
    63: ( "Infantry Tank",  9,  12,  "AFV"),
    64: ( "Cavalry Tank",  9,  12,  "AFV"),
    65: ( "Hvy Cavalry Tank",  9,  12,  "AFV"),
    66: ( "Hvy Assault Tank",  8,  12,  "AFV"),
    67: ( "Lt Tank Destroyer",  6,  12,  "AFV"),
    68: ( "CS Cavalry Tank",  8,  12,  "AFV"),
    69: ( "CS Infantry Tank",  9,  12,  "AFV"),
    70: ( "Lt Armoured Car",  2,  6,  "AFV"),
    71: ( "Naval Artillery",  1,  40,  "Art"),
    72: ( "Recon Tank",  7,  12,  "AFV"),
    73: ( "Recon Halftrack",  4,  8,  "AFV"),
    74: ( "Flamethrower",  2,  3,  "Inf"),
    75: ( "Assault Tank",  9,  12,  "AFV"),
    76: ( "Foreign Md Tank",  9,  12,  "AFV"),
    77: ( "Foreign Lt Tank",  7,  12,  "AFV"),
    78: ( "Foreign Flame Tank",  9,  12,  "AFV"),
    79: ( "Foreign Lt TD",  6,  12,  "AFV"),
    80: ( "Foreign Tank Destroyer",  8,  12,  "AFV"),
    81: ( "Foreign Assault Gun",  8,  12,  "AFV"),
    82: ( "Foreign SP Artillery",  3,  35,  "AFV"),
    83: ( "Foreign Armoured Car",  4,  6,  "AFV"),
    84: ( "Unarmored SP Rocket",  1,  20,  "Art"),
    85: ( "HT Mortar",  2,  12,  "AFV"),
    86: ( "Super Hvy Artillery",  1,  45,  "Art"),
    87: ( "Chassis",  0,  0,  "None"),
    88: ( "Mech-Recon",  6,  10,  "Inf"),
    89: ( "Lt Infantry",  3,  4,  "Inf"),
    90: ( "Hvy SP Artillery",  3,  35,  "AFV"),
    91: ( "CS Armored Car",  3,  6,  "AFV"),
    92: ( "Hvy Armored Car",  4,  8,  "AFV"),
    93: ( "Flame APC",  9,  12,  "AFV"),
    94: ( "Troop Ship",  0,  0,  "None"),
    95: ( "Cargo Ship",  0,  0,  "None"),
    96: ( "Vehicle Repair",  0,  0,  "None"),
    97: ( "Supply Dump",  0,  0,  "None"),
    98: ( "Fuel Dump",  0,  0,  "None"),
    99: ( "Support",  1,  0,  "Inf"),
    100: ( "Air Support",  1,  0,  "Inf"),
    101: ( "Manpower",  0,  0,  "None"),
    102: ( "Hvy Industry",  0,  0,  "None"),
    103: ( "Oil",  0,  0,  "None"),
    104: ( "Fuel",  0,  0,  "None"),
    105: ( "Synthetic Fuel",  0,  0,  "None"),
    106: ( "Resource",  0,  0,  "None"),
    107: ( "Artillery",  0,  0,  "None"),
    108: ( "Vehicle",  0,  0,  "None"),
    109: ( "Railyard",  0,  0,  "None"),
    110: ( "Port",  0,  0,  "None"),
    111: ( "V-Weapons Factory",  0,  0,  "None"),
    112: ( "V-Weapons Launcher",  0,  0,  "None"),
    113: ( "U-Boat Factory",  0,  0,  "None"),
    114: ( "U-Boat Pen",  0,  0,  "None"),
    115: ( "Assault Squad",  3,  4,  "Inf"),
    116: ( "Static AntiTank Gun",  1,  6,  "Art"),
    117: ( "Mech-Cavalry",  3,  4,  "Inf"),
    118: ( "MG Section",  4,  6,  "Inf"),
}

class OBComposition(TypedDict):
    name: str
    qty: int
    subtotal_sup: int

class OBStatsResult(TypedDict):
    id: int
    name: str | None
    total_cv: int
    total_support: int
    details: List[OBComposition]

def _calc_ob_stats_for_row(ob_row: Dict[str, str],
                           element_stats: Dict[int, Dict[str, Any]])->OBStatsResult:
    """
    Calculates total CV and Support for a single OB template row.
    Maps ob.csv 'sqd 0-31' to ground.csv 'id'.
    """
    total_cv = 0
    total_support = 0
    composition:List[OBComposition] = []

    # Iterate through the 32 equipment slots in the OB file
    for i in range(MAX_SQUAD_SLOTS):
        gid_key = f'sqd {i}'
        qty_key = f'sqdNum{i}'

        gid = parse_int(ob_row.get(gid_key))
        qty = parse_int(ob_row.get(qty_key))

        if gid and gid in element_stats and qty > 0:
            stats = element_stats[gid]
            total_cv += stats['cv'] * qty
            total_support += stats['sup'] * qty

            composition.append({
                "name": stats['name'],
                "qty": qty,
                "subtotal_sup": stats['sup'] * qty
            })

    return {
        "id": parse_int(ob_row.get('id')),
        "name": parse_str(ob_row.get('name')),
        "total_cv": total_cv,
        "total_support": total_support,
        "details": composition
    }


def _calc_unit_needed_support_for_row(
    unit_row: Dict[str, str],
    element_stats: Dict[int, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculates 'Needed Support' for a unit by processing a single CSV row.
    Maps 'sqd.u0-31' (WID) to element_stats lookup.
    """
    active_cv: int = 0
    total_needed_sup: int = 0
    breakdown: List[Dict[str, Any]] = []

    # Process 32 equipment slots (u0-u31 and n0-n31)
    for i in range(MAX_SQUAD_SLOTS):
        u_key = f'sqd.u{i}'
        n_key = f'sqd.num{i}'

        # Extract WID and Quantity from the row
        wid_val = unit_row.get(u_key)
        qty_val = unit_row.get(n_key, '0')

        # Ensure values exist and map to our stats table
        if wid_val and wid_val.isdigit():
            wid = int(wid_val)
            qty = int(qty_val) if qty_val.isdigit() else 0

            if wid in element_stats and qty > 0:
                stats = element_stats[wid]
                sub_cv = stats['cv'] * qty
                sub_sup = stats['sup'] * qty

                active_cv += sub_cv
                total_needed_sup += sub_sup

                breakdown.append({
                    "element": stats['name'],
                    "qty": qty,
                    "cv": sub_cv,
                    "support_needed": sub_sup
                })

    return {
        "unit_id": unit_row.get('id', 'Unk'),
        "name": unit_row.get('name', 'Unkn'),
        "total_active_cv": active_cv,
        "total_needed_support": total_needed_sup,
        "breakdown": breakdown
    }


def calc_unit_needed_support(ob_file_path: str,
                             unit_file_path: str,
                             ground_file_path: str,
                             unit_id: int) -> int:
    """
    Calculates total CV and supNeed for a specific Unit ID from unit.csv.

    Args:
        csv_path (str): Path to the *_unit.csv file.
        unit_id (int): The unique ID of the unit to calculate.
    """
    calc_unit_spt_need: int = 0
    calc_unit_spt: int = 0
    actual_spt_need: int = 0
    actual_spt: int = 0
    actual_hq_spt: int = 0

    unit_found = False

# Define the variable with type hints before the assignment
    ground_info: Dict[int, Tuple[str, int]] = {}

    try:
       # 1. Process Ground Elements using index-based reader to avoid 'id' collision
        gnd_stream: CSVListStream = get_csv_list_stream(ground_file_path)

        # Find indices manually to be safe
        # id is index 0, name is index 1, type is index 3
        for _, g_row in gnd_stream.rows:
            g_id = parse_int(g_row[GroundColumn.ID])
            g_elem_type = parse_int(g_row[GroundColumn.TYPE])

            if g_id == 0 or g_elem_type == 0:
                continue
            ground_info[g_id] = (
                g_row[GroundColumn.NAME],
                g_elem_type
            )

        unit_stream: CSVDictStream = get_csv_dict_stream(unit_file_path)
        # pylint:disable = C0103
        sptNeed_per_truck = 0.5

        for _, row in unit_stream.rows:
            uid = parse_int(row.get('id'))
            if uid == unit_id:
                unit_found = True

                # you have to get the unit's type to find its ob
                # for its suffix to build the full_name
                u_type = parse_int(row.get('type'))
                u_suffix = get_ob_suffix(ob_file_path, u_type)
                u_name = parse_str(row.get('name'))
                u_full_name = f"{u_name} {u_suffix}"

                ref = format_ref("UID", uid, u_full_name)
                print(f"\n--- Support for {ref} ---")

                        # Print Header for the Console Output
                print(f"\n{'Slot':^8} | {'Qty':>4} | {'Name':20.20} | "
                      f"{'Type':4} | {'Need(ea)':8} | {'Slot Need':4}"
                      )

                print("-" * 75)

                u_vehicles = parse_int(row.get('truck'))
                # these values are read in directly from the _unit.csv
                actual_spt_need = parse_int(row.get('sptNeed'))
                actual_spt = parse_int(row.get('support'))
                actual_hq_spt = parse_int(row.get('hqSupport'))
                # pylint: disable=C0103
                slot_sptNeed: int = 0

                # Iterate through the 32 equipment slots
                for i in range(MAX_SQUAD_SLOTS):
                    g_id = parse_int(row.get(f'sqd.u{i}'))
                    g_elem_qty = parse_int(row.get(f'sqd.num{i}'))

                    if g_id != 0 and g_id in ground_info:
                    # need to get _ground[g_id].type to
                    # reference correct ELEMENT_DATA
                        g_info = ground_info[g_id]
                        g_elem_type = g_info[1]

                        if g_elem_type in ELEMENT_DATA and g_elem_qty > 0:
                            data = ELEMENT_DATA[g_elem_type]

                            if g_elem_type == GroundElementType.SUPPORT:
                               calc_unit_spt += g_elem_qty

                            elem_type_sptNeed = data[2]
                            slot_sptNeed = int(g_elem_qty * elem_type_sptNeed / 10)

                            calc_unit_spt_need += slot_sptNeed

                            print(
                                f"Slot {i:2}: | {g_elem_qty:4} | {data[0]:20} | {g_elem_type:4} "
                                f"| {elem_type_sptNeed/10:>8.2f} | {slot_sptNeed:6}"
                            )

                if u_vehicles > 0:
                    slot_sptNeed = int(u_vehicles * sptNeed_per_truck / 10)
                    vehicle_type = GroundElementType.VEHICLE
                    print(f"Slot {"-":2}: | {u_vehicles:4} | {"Vehicles":20} | {vehicle_type:4} "
                          f"| {sptNeed_per_truck/10:>8.2f} | {slot_sptNeed:6}")

                    calc_unit_spt_need += slot_sptNeed
                break

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e.filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

    if not unit_found:
        print(f"Unit ID {unit_id} not found.")
        return calc_unit_spt_need

    print("-" * 75)
    calc_unit_spt += actual_hq_spt
    print(f"{"CALCULATED SUPPORT:":24} {calc_unit_spt:5}"
          f"    {"actual support:":20} {actual_spt:5} (in-game) "
          )
        #print(f"  Difference: {diff}   Difference(%): {perc_diff:.2%}")

    print(f"{"CALCULATED SUPPORT NEED:":24} {calc_unit_spt_need:5}"
          f"    {"actual support need:":20} {actual_spt_need:5} (in-game) "
          )
        #print(f"  Difference: {diff}   Difference(%): {perc_diff:.2%}")
    print("\n")

    if calc_unit_spt_need > calc_unit_spt:
        print(f"SUPPORT vs NEED: {calc_unit_spt} vs {calc_unit_spt_need}")
        diff = calc_unit_spt_need - calc_unit_spt
        perc_diff: float = diff / calc_unit_spt
        print(f"  Support Deficit: {diff} ({perc_diff:.2%})\n")

    return calc_unit_spt_need

def calc_unit_stats(unit_file_path: str,
                    unit_id: int) -> tuple[int, int] | None:
    """
    Calculates total CV and supNeed for a specific Unit ID from unit.csv.

    Args:
        csv_path (str): Path to the *_unit.csv file.
        unit_id (int): The unique ID of the unit to calculate.
    """
    total_cv = 0
    total_sup = 0
    unit_found = False

    unit_stream: CSVDictStream = get_csv_dict_stream(unit_file_path)

    for _, row in unit_stream.rows:
        uid = parse_int(row.get('id'))
        if uid == unit_id:
            unit_found = True
            print(f"--- Stats for Unit: {row['name']} (ID: {unit_id}) ---")

            # Iterate through the 32 equipment slots
            for i in range(MAX_SQUAD_SLOTS):
                u_id_str = row.get(f'sqd.u{i}')
                qty_str = row.get(f'sqd.num{i}')

                if u_id_str and u_id_str.strip():
                    ground_id = int(u_id_str)
                    qty = int(qty_str) if qty_str else 0

                    if ground_id in ELEMENT_DATA and qty > 0:
                        data = ELEMENT_DATA[ground_id]
                        slot_cv = qty * data[1]
                        slot_sup = qty * data[2]

                        total_cv += slot_cv
                        total_sup += slot_sup

                        print(
                            f"Slot {i:2}: {data[0]:20} | Qty: {qty:4} "
                            f"| CV: {slot_cv:5} | Sup: {slot_sup:5}"
                        )
            break

    if not unit_found:
        print(f"Unit ID {unit_id} not found.")
        return None

    print("-" * 55)
    print(f"TOTAL COMBAT VALUE: {total_cv}")
    print(f"TOTAL SUPPORT NEED: {total_sup}")
    return total_cv, total_sup


# Example usage:
#if __name__ == "__main__":
#    calc_unit_needed_support(OB_FILE, UNIT_FILE, GROUND_FILE, 180)