import os
from typing import cast

from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils import (
    get_logger,
    parse_int,
    parse_str
)

# Initialize the log for this specific module
log = get_logger(__name__)


def identify_unused_devices(ground_file_path: str,
                            aircraft_file_path: str,
                            device_file_path: str,
                            device_type: int):
    """
    Identifies devices of a specific type that are not present in any ground
    unit or aircraft.
    :param device_type: The integer ID of the device type (e.g.,
    7 for Hvy Gun, 25 for DP Gun)
    """
    devices_of_type = {}

    if not os.path.exists(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return

    if not os.path.exists(aircraft_file_path):
        log.error("Error: The file '%s' was not found.", aircraft_file_path)
        return

    if not os.path.exists(device_file_path):
        log.error("Error: The file '%s' was not found.", device_file_path)
        return

    ground_base_name = os.path.basename(ground_file_path)
    aircraft_base_name = os.path.basename(aircraft_file_path)
    device_base_name = os.path.basename(device_file_path)

    log.info("identify unused devices.\n"
            "  _ground file: '%s'\n"
            "  _aircraft file: '%s'\n"
            "  _device file: '%s'\n"
            " device type: %d",
            ground_base_name,
            aircraft_base_name,
            device_base_name,
            device_type
        )

    # 1. Identify all devices of the specified type from the device file
    try:
        device_gen = read_csv_dict_generator(device_file_path)
        next(device_gen)  # Skip DictReader header

        for item in device_gen:
            # Cast the yielded item to satisfy static type checkers
            _, row = cast(tuple[int, dict], item)
            d_type = parse_int(row.get("type"))
            if d_type == device_type:
                d_name = parse_str(row.get('name', "Unk"))
                d_id = parse_int(row.get('id', 0))
                if d_id:
                    devices_of_type[d_id] = d_name

    except (OSError, IOError, ValueError, KeyError) as e:
        log.exception("identify_unused_devices failed: %s", e)
        return

    if not devices_of_type:
        print(f"No devices of Type {device_type} found in the device file.")
        return

    # 2. Identify all weapon IDs used in the ground and aircraft files (wpn 0 through wpn 9)
    used_weapon_ids = set()
    wpn_cols = [f'wpn {i}' for i in range(10)]

    for file_path in [ground_file_path, aircraft_file_path]:
        try:
            gen = read_csv_dict_generator(file_path)
            next(gen)  # Skip DictReader header

            for item in gen:
                _, row = cast(tuple[int, dict], item)
                for col in wpn_cols:
                    wpn_id = parse_int(row.get(col), 0)
                    # Filter out zero values
                    if wpn_id:
                        used_weapon_ids.add(wpn_id)

        except (OSError, IOError, ValueError, KeyError) as e:
            log.warning("Skipping file %s due to error: %s", file_path, e)

    # 3. Filter for unused devices
    unused_list = []
    for dev_id, dev_name in devices_of_type.items():
        if dev_id not in used_weapon_ids:
            unused_list.append((dev_id, dev_name))

    # 4. Sort and print the results
    unused_list.sort(key=lambda x: int(x[0]))

    print(f"\n--- Unused Type {device_type} Devices (Ground & Air) ---")
    if not unused_list:
        print(f"All Type {device_type} devices are currently in use.")
    else:
        print(f"{'ID':<8} | {'Device Name'}")
        print("-" * 45)
        for dev_id, dev_name in unused_list:
            print(f"{dev_id:<8} | {dev_name}")
        print(f"\nTotal unused devices: {len(unused_list)}"
              f" for Type: {device_type}")
