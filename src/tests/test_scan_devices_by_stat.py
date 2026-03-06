import csv
from pathlib import Path
import pytest
from unittest.mock import patch

from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import DeviceCol
from wite2_tools.scanning.scan_devices_by_stat import scan_devices_by_stat

@pytest.fixture
def mock_device_csv(tmp_path: Path) -> str:
    """
    Creates a mock _device.csv file.
    Note: Since the scanner uses DeviceCol (Enum/Int), the CSV columns
    must align with those integer indexes.
    """
    csv_file = tmp_path / "mock_device.csv"

    # We need to ensure the list is long enough to satisfy the DeviceCol indexes.
    # If DeviceCol.PENETRATION is index 15, the list needs at least 16 elements.
    # To be safe, we'll create a row with 100 empty strings.
    def create_row(dev_id: str, name: str, stat_val: str, stat_idx: int) -> list[str]:
        row = [""] * 100
        row[DeviceCol.ID] = dev_id
        row[DeviceCol.NAME] = name
        row[stat_idx] = stat_val
        return row

    with open(csv_file, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.writer(f)
        # WiTE2 files often have a metadata header row, get_csv_list_stream handles this
        writer.writerow(["WiTE2", "Device", "Data"])

        # Device 1: Meets criteria (150 >= 100)
        writer.writerow(create_row("1", "Pak 40", "150", DeviceCol.PEN))
        # Device 2: Fails criteria (50 < 100)
        writer.writerow(create_row("2", "Pak 36", "50", DeviceCol.PEN))
        # Device 3: Meets criteria exactly (100 >= 100)
        writer.writerow(create_row("3", "KwK 40", "100", DeviceCol.PEN))

    return str(csv_file)

def test_scan_devices_by_stat_finds_matches(mock_device_csv: str) -> None:
    """Tests that devices meeting or exceeding the threshold are returned."""
    results = scan_devices_by_stat(
        device_file_path=mock_device_csv,
        stat_col=DeviceCol.PEN,
        min_value=100
    )

    # We expect Pak 40 and KwK 40
    assert len(results) == 2
    assert results[0]["name"] == "Pak 40"
    assert results[0]["stat_value"] == 150
    assert results[1]["id"] == "3"

def test_scan_devices_by_stat_no_matches(mock_device_csv: str) -> None:
    """Tests that an empty list is returned if no devices meet the threshold."""
    results = scan_devices_by_stat(
        device_file_path=mock_device_csv,
        stat_col=DeviceCol.PEN,
        min_value=999 # Impossible threshold
    )

    assert len(results) == 0

def test_scan_devices_by_stat_file_not_found() -> None:
    """Tests graceful handling of a non-existent file path."""
    # Running against a path we know doesn't exist
    results = scan_devices_by_stat(
        device_file_path="non_existent_file.csv",
        stat_col=DeviceCol.PEN,
        min_value=100
    )

    assert results == []

def test_scan_devices_by_stat_index_error(tmp_path: Path) -> None:
    """Tests handling of malformed rows that are too short for the requested index."""
    bad_csv = tmp_path / "short_row.csv"
    with open(bad_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Header"])
        # This row only has 1 column, indexing DeviceCol.PENETRATION (e.g. 15) will crash
        writer.writerow(["OnlyOneCol"])

    results = scan_devices_by_stat(
        device_file_path=str(bad_csv),
        stat_col=DeviceCol.PEN,
        min_value=10
    )

    # Should catch IndexError and return what it found (nothing)
    assert results == []