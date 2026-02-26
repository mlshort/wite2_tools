import os
from typing import Dict, Set

from wite2_tools.utils import (
    get_logger,
    get_ground_elem_type_name,
    get_ob_suffix
)
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.parsing import parse_int, parse_str
from wite2_tools.paths import LOCAL_DATA_PATH


# Initialize the logger for this specific module
log = get_logger(__name__)


def audit_unit_ob_excess(
    unit_file_path: str,
    ob_file_path: str,
    target_nat: Set[int]
) -> None:
    """
    Compares unit equipment to its assigned OB template.
    Prints elements exceeding 125% of the authorized TOE.
    """
    # 1. Map OB IDs to their authorized composition
    ob_templates: Dict[int, Dict[int, int]] = {}

    if not os.path.exists(unit_file_path):
        log.error("Error: The file '%s' was not found.", unit_file_path)
        return

    if not os.path.exists(ob_file_path):
        log.error("Error: The file '%s' was not found.", ob_file_path)
        return

    ob_gen = read_csv_dict_generator(ob_file_path)
    # Skip DictReader header yield
    next(ob_gen)

    log.info("Task Start: Evaluating Unit ob excess: '%s' against '%s' for Nat Codes: %s",
             os.path.basename(unit_file_path),
             os.path.basename(ob_file_path),
             target_nat)

    ob_count: int = 0
    unit_count: int = 0
    excess_count: int = 0

    for _, row in ob_gen:
        ob_id = parse_int(row.get('id'))
        if ob_id == 0:
            continue

        ob_count += 1

        composition: Dict[int,int] = {}
        # OBs use 'sqd X' for ID and 'sqdNum X' for Count (0-31)
        for i in range(32):
            o_wid = parse_int(row.get(f'sqd {i}'))
            o_cnt = parse_int(row.get(f'sqdNum {i}'))
            if o_wid > 0:
                composition[o_wid] = o_cnt
        ob_templates[ob_id] = composition

    # 2. Process Units and Compare to TOE
    unit_gen = read_csv_dict_generator(unit_file_path)
    next(unit_gen)

    header = (
        f"{'UID':<7} | {'Unit Name':<25} | {'WID':<7} | {'Element Name':<25} | "
        f"{'Avail':<6} | {'Auth':<6} | {'% OF TOE'}"
    )
    print(header)
    print("-" * 80)

    for _, row in unit_gen:
        u_nat = parse_int(row.get('nat'), default=-1)
        if u_nat not in target_nat:
            continue

        uid = parse_int(row.get('id'))

        if uid == 0:
            continue

        unit_count += 1
        u_name = parse_str(row.get('name'), 'Unk')
        # print(f"Processing {u_name}")
        # type corresponds to the TOE(OB)
        u_type = parse_int(row.get('type'))

        if u_type not in ob_templates:
            print(f"Unit {u_name} not found in ob_templates")
            continue

        ob_dict = ob_templates[u_type]
        u_suffix = get_ob_suffix(ob_file_path, u_type)
        u_fullname = f"{u_name} {u_suffix}"

        # Units use 'sqd X' and 'sqdNum X' (0-31)
        for i in range(32):
            u_wid = parse_int(row.get(f'sqd.u{i}'))
            u_cnt = parse_int(row.get(f'sqd.num{i}'))

            if u_wid > 0 and u_cnt > 0:
                authorized = ob_dict.get(u_wid, 0)
                # TODO
                GND_CSV = LOCAL_DATA_PATH + "\\" + "1941 Campaign_ground.csv"
                w_name: str = get_ground_elem_type_name(GND_CSV, u_wid)

                if authorized > 0:
                    pct = (u_cnt / authorized) * 100
                    if pct > 125:
                        line = (
                            f"{uid:<7} | {u_fullname[:24]:<25} | "
                            f"{u_wid:<7} | {w_name[:24]:<25} | {u_cnt:<6} | "
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

    log.info("Task Complete: %d Units checked against %d TOE(OB)s. %d instances of ground element excess found",
             unit_count,
             ob_count,
             excess_count)


if __name__ == "__main__":
    UNIT_CSV = LOCAL_DATA_PATH + "\\" + "1941 Campaign (MG Mod)_unit.csv"
    OB_CSV = LOCAL_DATA_PATH + "\\" + "1941 Campaign (MG Mod)_ob.csv"
    AXIS_NAT = {1}

    audit_unit_ob_excess(UNIT_CSV, OB_CSV, AXIS_NAT)