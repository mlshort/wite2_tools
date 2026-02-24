import csv
from typing import List, Dict, Any

from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import DeviceCol
from wite2_tools.utils import get_logger
from wite2_tools.utils import parse_int

log = get_logger(__name__)


def scan_devices_by_stat(
    device_file_path: str,
    stat_col: DeviceCol,
    min_value: int
) -> List[Dict[str, Any]]:
    """
    Scans _device.csv for items where a specific stat meets or exceeds a
    threshold.
    """
    matches = []

    try:
        with open(device_file_path, mode='r', encoding=ENCODING_TYPE,
                  errors='ignore') as f:
            # Skip the first row (WiTE2 header metadata) if necessary
            reader = csv.reader(f)
            _ = next(reader)

            for row in reader:
                # Use the Enum to safely access the column index
                val = parse_int(row[stat_col], 0)

                if val >= min_value:
                    device_info = {
                        "id": row[DeviceCol.ID],
                        "name": row[DeviceCol.NAME],
                        "stat_value": val
                    }
                    matches.append(device_info)

        log.info("Scan complete. Found %d devices meeting criteria.",
                 len(matches))

    except (OSError, IndexError) as e:
        log.error("Failed to scan device file: %s", e)

    return matches
