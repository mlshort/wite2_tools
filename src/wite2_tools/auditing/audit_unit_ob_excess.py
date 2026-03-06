import os
from typing import Dict, Set

from wite2_tools.utils import (
    get_logger,
    get_ground_elem_type_name,
    get_ob_suffix
)
from wite2_tools.generator import get_csv_dict_stream
from wite2_tools.utils.parsing import parse_int, parse_str
from wite2_tools.constants import MAX_SQUAD_SLOTS


# Initialize the logger for this specific module
log = get_logger(__name__)


def audit_unit_ob_excess(
    unit_file_path: str,
    ob_file_path: str,
    gnd_file_path: str,
    target_nat: Set[int]
) -> int:
    """
    Compares unit equipment to its assigned OB template.
    Prints elements exceeding 125% of the authorized TOE.
    """
    # 1. Map OB IDs to their authorized composition
    ob_templates: Dict[int, Dict[int, int]] = {}

    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return -1

    if not os.path.exists(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return -1

    ob_stream = get_csv_dict_stream(ob_file_path)

    log.info("Task Start: Evaluating Unit ob excess: '%s' against '%s' for Nat Codes: %s",
             os.path.basename(unit_file_path),
             os.path.basename(ob_file_path),
             target_nat)

    ob_count: int = 0
    unit_count: int = 0
    excess_count: int = 0

    for _, ob_row in ob_stream.rows:
        ob_id = parse_int(ob_row.get('id'))
        if ob_id == 0:
            continue

        ob_count += 1

        composition: Dict[int,int] = {}
        # OBs use 'sqd X' for ID and 'sqdNum X' for Count (0-31)
        for i in range(MAX_SQUAD_SLOTS):
            o_wid = parse_int(ob_row.get(f'sqd {i}'))
            o_cnt = parse_int(ob_row.get(f'sqdNum {i}'))
            if o_wid > 0:
                composition[o_wid] = o_cnt
        ob_templates[ob_id] = composition

    # 2. Process Units and Compare to TOE
    unit_stream = get_csv_dict_stream(unit_file_path)

    header = (
        f"{'UID':<6} | {'Unit Name':<25} | {'WID':<6} | {'Element Name':<25} | "
        f"{'Avail':<6} | {'Auth':<6} | {'% OF TOE'}"
    )
    print(header)
    print("-" * 80)

    for _, u_row in unit_stream.rows:
        u_nat:int = parse_int(u_row.get('nat'), default=-1)
        if u_nat not in target_nat:
            continue

        uid = parse_int(u_row.get('id'))

        if uid == 0:
            continue

        unit_count += 1
        u_name:str = parse_str(u_row.get('name'), 'Unk')
        # print(f"Processing {u_name}")
        # type corresponds to the TOE(OB)
        u_type:int = parse_int(u_row.get('type'))

        if u_type not in ob_templates:
            print(f"Unit {u_name} not found in ob_templates")
            continue

        ob_dict = ob_templates[u_type]
        u_suffix:str = get_ob_suffix(ob_file_path, u_type)
        u_fullname:str = f"{u_name} {u_suffix}"

        # Units use 'sqd X' and 'sqdNum X' (0-31)
        for i in range(MAX_SQUAD_SLOTS):
            u_wid:int = parse_int(u_row.get(f'sqd.u{i}'))
            u_cnt:int = parse_int(u_row.get(f'sqd.num{i}'))

            if u_wid > 0 and u_cnt > 0:
                authorized:int = ob_dict.get(u_wid,0)
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
                # else:
                    # Item is in unit but NOT in the TOE(OB) template
                    # line = (
                    #    f"{uid:<7} | {u_name[:24]:<25} | "
                    #    f"{u_wid:<7} | {w_name[:24]:<25} | {u_cnt:<6} | "
                    #    f"{'0':<6} | {'NON-TOE'}"
                    #)
                    # print(line)

    log.info("Task Complete: %d Units checked against %d TOE(OB)s."
             " %d instances of ground element excess found",
             unit_count,
             ob_count,
             excess_count)

    return excess_count
