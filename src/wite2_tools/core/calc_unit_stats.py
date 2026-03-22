"""
    module still work-in-progress
"""
import os
from typing import Any, TypedDict

# Direct import to bypass __init__ export issues
from wite2_tools.core.GND_ELEMENT_DATA import GND_ELEMENT_DATA
from wite2_tools.generator import (
    CSVListStream,
    get_csv_list_stream
)
from wite2_tools.utils.parsing import parse_row_int, parse_row_str
from wite2_tools.utils import get_ob_suffix, format_ref
from wite2_tools.utils import get_logger
from wite2_tools.models import (
    O_SQD_SLOTS
)
from wite2_tools.models import (
    GndRow,
    G_NAME_COL,
    G_TYPE_COL
)
from wite2_tools.models import (
    UnitRow,
    U_SQD_SLOTS,
    U_NAME_COL,
    U_TYPE_COL,
    U_TRUCK_COL,
    U_SQD0_COL,
    U_SQD_NUM0_COL,
    U_SUPPORT_COL,
    U_SPT_NEED_COL,
    U_HQ_SUPPORT_COL
)
from wite2_tools.models.gnd_schema import (
    GndElementType
)

# Initialize the logger for this specific module
log = get_logger(__name__)

class OBComposition(TypedDict):
    name: str
    qty: int
    subtotal_sup: int

class OBStatsResult(TypedDict):
    id: int
    name: str | None
    total_cv: int
    total_support: int
    details: list[OBComposition]


def _calc_ob_stats_for_row(ob_row: list[str],
                           header: list[str],
                           element_stats: dict[int, dict[str, Any]]
                           )->OBStatsResult:
    """
    Calculates total CV and Support for a single OB template list row.
    Maps ob.csv 'sqd 0-31' to ground.csv 'id'.
    """
    total_cv = 0
    total_support = 0
    composition:list[OBComposition] = []

    id_idx = header.index('id')
    name_idx = header.index('name')

    # Iterate through the 32 equipment slots in the OB file
    # (Leaving this dynamic since we aren't importing ObColumn here yet)
    for i in range(O_SQD_SLOTS):
        gid_key = f'sqd {i}'
        qty_key = f'sqdNum{i}'

        if gid_key in header and qty_key in header:
            gid = parse_row_int(ob_row, header.index(gid_key))
            qty = parse_row_int(ob_row, header.index(qty_key))

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
        "id": parse_row_int(ob_row, id_idx),
        "name": parse_row_str(ob_row, name_idx),
        "total_cv": total_cv,
        "total_support": total_support,
        "details": composition
    }


def _calc_unit_needed_support_for_row(
    unit_row: list[str],
    element_stats: dict[int, dict[str, Any]]
) -> dict[str, Any]:
    """
    Calculates 'Needed Support' for a unit by processing a single CSV list row.
    Strictly uses UnitColumn schema for indexing.
    """
    active_cv: int = 0
    total_needed_sup: int = 0
    breakdown: list[dict[str, Any]] = []
    unit = UnitRow(unit_row)

    # Process 32 equipment slots using strict schema indices
    for i in range(U_SQD_SLOTS):
        wid = parse_row_int(unit_row, U_SQD0_COL + (i * 8))
        qty = parse_row_int(unit_row, U_SQD_NUM0_COL + (i * 8))

        if wid and wid in element_stats and qty > 0:
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
        "unit_id": unit.ID, #parse_row_int(unit_row, U_ID_COL),
        "name": parse_row_str(unit_row, U_NAME_COL, "Unkn"),
        "total_active_cv": active_cv,
        "total_needed_support": total_needed_sup,
        "breakdown": breakdown
    }


# pylint: disable=too-many-statements, too-many-branches, too-many-locals
def calc_unit_support(ob_file_path: str,
                      unit_file_path: str,
                      ground_file_path: str,
                      unit_id: int) -> int:
    """
    Calculates Support and Need for a specific Unit ID from unit.csv.
    """
    calc_unit_spt_need: int = 0
    calc_unit_spt: int = 0
    actual_spt_need: int = 0
    actual_spt: int = 0
    actual_hq_spt: int = 0

    unit_found = False
    ground_info: dict[int, tuple[str, int]] = {}

    if not os.path.isfile(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0

    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    try:
        # 1. Process Ground Elements
        gnd_stream: CSVListStream = get_csv_list_stream(ground_file_path)

        for _, g_row in gnd_stream.rows:
            gnd = GndRow(g_row)
            g_id = gnd.ID
        #    g_id = parse_row_int(g_row, G_ID_COL)
            g_elem_type = parse_row_int(g_row, G_TYPE_COL)

            if g_id == 0 or g_elem_type == 0:
                continue
            ground_info[g_id] = (
                parse_row_str(g_row, G_NAME_COL),
                g_elem_type
            )

        # 2. Process Units
        unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

        # Pre-calculate dynamic squad slot indices safely using Schema Enum
        u_sqd_indices: list[tuple[int, int]] = [
            (U_SQD0_COL + (i * 8), U_SQD_NUM0_COL + (i * 8))
            for i in range(U_SQD_SLOTS)
        ]

        # pylint: disable=invalid-name
        sptNeed_per_truck = 0.5

        for _, row in unit_stream.rows:
            unit = UnitRow(row)
            uid = unit.ID  #parse_row_int(row, U_ID_COL)
            if uid == unit_id:
                unit_found = True

                u_type = parse_row_int(row, U_TYPE_COL)
                u_suffix = get_ob_suffix(ob_file_path, u_type)
                u_name = parse_row_str(row, U_NAME_COL)
                u_full_name = f"{u_name} {u_suffix}"

                ref = format_ref("UID", uid, u_full_name)
                print(f"\n--- Support for {ref} ---")
                print(f"\n{'Slot':^8} | {'Qty':>4} | {'Name':20.20} | "
                      f"{'Type':4} | {'Need(ea)':8} | {'Slot Need':4}")
                print("-" * 75)

                u_vehicles = parse_row_int(row, U_TRUCK_COL)
                actual_spt_need = parse_row_int(row, U_SPT_NEED_COL)
                actual_spt = parse_row_int(row, U_SUPPORT_COL)
                actual_hq_spt = parse_row_int(row, U_HQ_SUPPORT_COL)

                # pylint: disable=C0103
                slot_sptNeed: int = 0

                # Iterate through the pre-calculated equipment slots
                for i, (sqd_u_idx, sqd_num_idx) in enumerate(u_sqd_indices):
                    g_id = parse_row_int(row, sqd_u_idx)
                    g_elem_qty = parse_row_int(row, sqd_num_idx)

                    if g_id != 0 and g_id in ground_info:
                        g_info = ground_info[g_id]
                        g_elem_type = g_info[1]

                        if g_elem_type in GND_ELEMENT_DATA and g_elem_qty > 0:
                            data: tuple[str, int, int, str, int] = GND_ELEMENT_DATA[g_elem_type]

                            if g_elem_type == GndElementType.SUPPORT:
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
                    vehicle_type = GndElementType.VEHICLE
                    print(f"Slot {'-':2}: | {u_vehicles:4} | {'Vehicles':20} | {vehicle_type:4} "
                          f"| {sptNeed_per_truck/10:>8.2f} | {slot_sptNeed:6}")

                    calc_unit_spt_need += slot_sptNeed
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    if not unit_found:
        print(f"Unit ID {unit_id} not found.")
        return calc_unit_spt_need

    print("-" * 75)
    calc_unit_spt += actual_hq_spt
    print(f"{'CALCULATED SUPPORT:':24} {calc_unit_spt:5}"
          f"    {'actual support:':20} {actual_spt:5} (in-game) ")

    print(f"{'CALCULATED SUPPORT NEED:':24} {calc_unit_spt_need:5}"
          f"    {'actual support need:':20} {actual_spt_need:5} (in-game) ")
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
    Calculates total CV and Spt Need for a specific Unit ID from unit.csv.
    """
    total_cv = 0
    total_sup = 0
    unit_found = False

    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return None

    unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

    u_sqd_indices: list[tuple[int, int]] = [
        (U_SQD0_COL + (i * 8), U_SQD_NUM0_COL + (i * 8))
        for i in range(U_SQD_SLOTS)
    ]

    for _, row in unit_stream.rows:
        unit = UnitRow(row)
        uid = unit.ID #parse_row_int(row, U_ID_COL)
        if uid == unit_id:
            unit_found = True
            u_name = parse_row_str(row, U_NAME_COL)
            print(f"--- Stats for Unit: {u_name} (ID: {unit_id}) ---")

            # Iterate through the pre-calculated equipment slots
            for i, (sqd_u_idx, sqd_num_idx) in enumerate(u_sqd_indices):
                ground_id = parse_row_int(row, sqd_u_idx)
                qty = parse_row_int(row, sqd_num_idx)

                if ground_id in GND_ELEMENT_DATA and qty > 0:
                    data = GND_ELEMENT_DATA[ground_id]
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
