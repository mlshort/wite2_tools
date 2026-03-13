import os

from wite2_tools.generator import get_csv_list_stream
from wite2_tools.utils import (
    get_logger,
    parse_row_int,
    parse_row_str
)
from wite2_tools.models.dev_schema import DevColumn
from wite2_tools.models.gnd_schema import GndColumn
from wite2_tools.models.aircraft_schema import AcColumn

# Initialize the log for this specific module
log = get_logger(__name__)


# pylint: disable=too-many-branches, too-many-locals
def identify_unused_devices(ground_file_path: str,
                            aircraft_file_path: str,
                            device_file_path: str,
                            device_type: int) -> int:
    """
    Identifies devices of a specific type that are not present in any ground
    unit or aircraft.
    :param device_type: The integer ID of the device type (e.g.,
    7 for Hvy Gun, 25 for DP Gun)
    """
    devices_of_type = {}

    if not os.path.isfile(ground_file_path):
        log.error("Error: The file '%s' was not found.", ground_file_path)
        return -1

    if not os.path.isfile(aircraft_file_path):
        log.error("Error: The file '%s' was not found.", aircraft_file_path)
        return -1

    if not os.path.isfile(device_file_path):
        log.error("Error: The file '%s' was not found.", device_file_path)
        return -1

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
        device_gen = get_csv_list_stream(device_file_path)

        for _, row in device_gen.rows:
            d_type = parse_row_int(row, DevColumn.TYPE)

            if d_type == device_type:
                d_name = parse_row_str(row, DevColumn.NAME, default="Unk")
                d_id = parse_row_int(row, DevColumn.ID)
                if d_id:
                    devices_of_type[d_id] = d_name

    except (OSError, IOError, KeyError) as e:
        log.exception("identify_unused_devices failed: %s", e)
        return -1

    if not devices_of_type:
        print(f"No devices of Type {device_type} found in the device file.")
        return 0

    # 2. Identify all weapon IDs used in the ground and aircraft files
    used_weapon_ids = set()

    # Build strict index lists from schemas (WPN_0 through WPN_9)
    gnd_wpn_indices = [getattr(GndColumn, f"WPN_{i}").value for i in range(10)]

    # Aircraft have base weapons and 5 additional Weapon Sets (WS0 to WS4)
    # which must be checked so bombs/drop tanks aren't falsely flagged as unused.
    ac_wpn_indices = [getattr(AcColumn, f"WPN_{i}").value for i in range(10)]
    for ws in range(5):
        ac_wpn_indices.extend([getattr(AcColumn,
                                       f"WS{ws}_WPN_{i}").value for i in range(10)])

    # Map the files to their respective column schemas
    file_mappings = [
        (ground_file_path, gnd_wpn_indices),
        (aircraft_file_path, ac_wpn_indices)
    ]

    for file_path, wpn_indices in file_mappings:
        try:
            gen = get_csv_list_stream(file_path)

            # Iterate through the rows using the exact positional indices
            for _, row in gen.rows:
                for w_idx in wpn_indices:
                    wpn_id = parse_row_int(row, w_idx)
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

    return len(unused_list)
