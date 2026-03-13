import csv
from pathlib import Path


from wite2_tools.config import ENCODING_TYPE
from wite2_tools.models import DevColumn
from wite2_tools.scanning.scan_devices_by_stat import scan_devices_by_stat


def test_scan_devices_by_stat_finds_matches(mock_device_csv: Path) -> None:
    """Tests that devices meeting or exceeding the threshold are returned."""
    results = scan_devices_by_stat(
        device_file_path=str(mock_device_csv),
        stat_col=DevColumn.PEN,
        min_value=100
    )

    # We expect Pak 40 and KwK 40
    assert len(results) == 2
    assert results[0]["name"] == "Pak 40"
    assert results[0]["stat_value"] == 150
    assert results[1]["id"] == "3"

def test_scan_devices_by_stat_no_matches(mock_device_csv: Path) -> None:
    """Tests that an empty list is returned if no devices meet the threshold."""
    results = scan_devices_by_stat(
        device_file_path=str(mock_device_csv),
        stat_col=DevColumn.PEN,
        min_value=999 # Impossible threshold
    )

    assert len(results) == 0

def test_scan_devices_by_stat_file_not_found() -> None:
    """Tests graceful handling of a non-existent file path."""
    # Running against a path we know doesn't exist
    results = scan_devices_by_stat(
        device_file_path="non_existent_file.csv",
        stat_col=DevColumn.PEN,
        min_value=100
    )

    assert not results

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
        stat_col=DevColumn.PEN,
        min_value=10
    )

    # Should catch IndexError and return what it found (nothing)
    assert not results
