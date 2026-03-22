import os

from wite2_tools.utils import (
    get_logger,
    get_ground_elem_type_name,
    get_ob_suffix
)
from wite2_tools.generator import get_csv_list_stream, CSVListStream
from wite2_tools.utils.parsing import parse_row_int

from wite2_tools.models import (
    ObColumn,
    O_SQD_SLOTS,
    UnitColumn,
    UnitRow,
    U_SQD_SLOTS
)

log = get_logger(__name__)

# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def audit_unit_ob_excess(
    unit_file_path: str,
    ob_file_path: str,
    gnd_file_path: str,
    target_nat: set[int]
) -> int:
    """
    Compares unit equipment to its assigned OB template.
    Prints elements exceeding 125% of the authorized TOE.
    """
    if not os.path.isfile(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return 0

    if not os.path.isfile(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return 0

    # --- 1. Map OB IDs to their authorized composition ---
    ob_templates: dict[int, dict[int, int]] = {}
    ob_stream: CSVListStream = get_csv_list_stream(ob_file_path)

    for _, ob_row in ob_stream.rows:
        ob_id: int = parse_row_int(ob_row, ObColumn.ID)
        nat: int = parse_row_int(ob_row, ObColumn.NAT)

        if nat in target_nat:
            if ob_id not in ob_templates:
                ob_templates[ob_id] = {}

            for i in range(O_SQD_SLOTS):
                # The slots are contiguous in the CSV, so we just add 'i'
                # to the starting column index!
                wid_idx = ObColumn.SQD_0 + i
                cnt_idx = ObColumn.SQD_NUM_0 + i

                wid: int = parse_row_int(ob_row, wid_idx)
                cnt: int = parse_row_int(ob_row, cnt_idx)

                if wid > 0 and cnt > 0:
                    ob_templates[ob_id][wid] = ob_templates[ob_id].get(wid, 0) + cnt

    # --- 2. Check Units against the OB templates ---
    excess_count = 0
    unit_stream: CSVListStream = get_csv_list_stream(unit_file_path)

    for _, u_row in unit_stream.rows:
        unit = UnitRow(u_row)
        uid: int = unit.ID #parse_row_int(u_row, UnitColumn.ID)
        u_type: int = unit.TYPE #parse_row_int(u_row, UnitColumn.TYPE)
        u_delay: int = unit.DELAY #parse_row_int(u_row, UnitColumn.DELAY)
        u_name: str = unit.NAME #parse_row_str(u_row, UnitColumn.NAME)

        # Skip delayed units and invalid types
        if u_delay != 0 or u_type == 0:
            continue

        # Fetch the authorized OB dict
        ob_dict = ob_templates.get(u_type)
        if ob_dict is None:
            continue

        u_suffix = get_ob_suffix(ob_file_path, u_type)
        u_fullname = f"{u_name} {u_suffix}"

        for i in range(U_SQD_SLOTS):
            # Apply the exact same contiguous index logic to the Unit schema
            wid_idx = UnitColumn.SQD_U0 + i
            cnt_idx = UnitColumn.SQD_NUM0 + i

            u_wid: int = parse_row_int(u_row, wid_idx)
            u_cnt: int = parse_row_int(u_row, cnt_idx)

            if u_wid > 0 and u_cnt > 0:
                authorized: int = ob_dict.get(u_wid, 0)
                w_name: str = get_ground_elem_type_name(gnd_file_path, u_wid)

                if authorized > 0:
                    pct = (u_cnt / authorized) * 100
                    if pct > 125:
                        line = (
                            f"{uid:<6} | {u_fullname[:24]:<25} | "
                            f"{u_wid:<6} | {w_name[:24]:<25} | {u_cnt:<6} | "
                            f"{authorized:<6} | {pct:>6.1f}%"
                        )
                        excess_count += 1
                        print(line)

    return excess_count
