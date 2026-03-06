"""
WiTE2 Device Stat Scanner
=========================

Provides utilities for querying the War in the East 2 `_device.csv` database.
This module allows users to efficiently filter and extract equipment data
based on specific statistical thresholds (e.g., armor penetration, reliability,
load cost) utilizing column enumerations for safe data extraction.

Functions:
    scan_devices_by_stat: Scans the device database and returns a list of
                          devices that meet or exceed a specified minimum value.
"""
from typing import List, Dict, Any

from wite2_tools.generator import get_csv_list_stream
from wite2_tools.constants import DeviceCol
from wite2_tools.utils import get_logger
from wite2_tools.utils import parse_int

# Initialize the log for this specific module
log = get_logger(__name__)


def scan_devices_by_stat(
    device_file_path: str,
    stat_col: DeviceCol,
    min_value: int
) -> List[Dict[str, Any]]:
    """
    Scans the device database for items where a specific stat meets or exceeds
    a threshold.

    Args:
        device_file_path: Path to the _device.csv file.
        stat_col: The DeviceCol enum representing the column to check.
        min_value: The minimum integer value required to include the device.

    Returns:
        A list of dictionaries containing the ID, Name, and the stat value of matches.
    """
    matches: List[Dict[str, Any]] = []

    try:
        dev_stream = get_csv_list_stream(device_file_path)

        for _, row in dev_stream.rows:
            # Use the Enum to safely access the column index

            val = parse_int(row[stat_col])

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
