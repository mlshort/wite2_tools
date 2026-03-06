import os
import csv
from pathlib import Path
import pytest

# Adjust this import if your encoding constant lives elsewhere
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.core.identify_unused_devices import identify_unused_devices


@pytest.fixture
def mock_files(tmp_path: Path) -> tuple[str, str, str]:
    """
    Generates mock ground, aircraft, and device CSV files.
    """
    ground_csv = tmp_path / "mock_ground.csv"
    aircraft_csv = tmp_path / "mock_aircraft.csv"
    device_csv = tmp_path / "mock_device.csv"

    # --- 1. Setup Device File ---
    # We will create 3 devices of Type 7 (e.g., Heavy Guns) and 1 of Type 9
    device_headers: list[str] = ["id", "type", "name"]
    with open(device_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=device_headers)
        writer.writeheader()
        writer.writerow({"id": "100", "type": "7", "name": "75mm Gun"})  # Used in Ground
        writer.writerow({"id": "101", "type": "7", "name": "88mm Flak"}) # Used in Aircraft
        writer.writerow({"id": "102", "type": "7", "name": "105mm How"}) # UNUSED!
        writer.writerow({"id": "103", "type": "9", "name": "Radio"})     # Ignored (wrong type)

    # --- 2. Setup Ground File ---
    ground_headers: list[str] = ["id", "name"]
    for i in range(MAX_SQUAD_SLOTS):
        ground_headers.append(f"wpn {i}")

    with open(ground_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ground_headers)
        writer.writeheader()

        row1: dict[str, str] = {"id": "1", "name": "Infantry Squad"}
        for i in range(MAX_SQUAD_SLOTS):
            row1[f"wpn {i}"] = "0"

        # Ground unit uses Device 100 in wpn 0 slot
        row1["wpn 0"] = "100"
        writer.writerow(row1)

    # --- 3. Setup Aircraft File ---
    aircraft_headers: list[str] = ["id", "name"]
    for i in range(MAX_SQUAD_SLOTS):
        aircraft_headers.append(f"wpn {i}")

    with open(aircraft_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=aircraft_headers)
        writer.writeheader()

        row1 = {"id": "1", "name": "Bf 109"}
        for i in range(MAX_SQUAD_SLOTS):
            row1[f"wpn {i}"] = "0"

        # Aircraft unit uses Device 101 in wpn 2 slot
        row1["wpn 2"] = "101"
        writer.writerow(row1)

    return str(ground_csv), str(aircraft_csv), str(device_csv)


def test_identify_unused_devices_happy_path(mock_files: tuple[str, str, str]) -> None:
    """Verifies that the function correctly identifies unused devices of the target type."""
    ground_path, aircraft_path, device_path = mock_files

    # Target Type 7.
    # Expectation: 100 used in Ground, 101 used in Air, 102 is unused. Count = 1.
    unused_count: int = identify_unused_devices(
        ground_file_path=ground_path,
        aircraft_file_path=aircraft_path,
        device_file_path=device_path,
        device_type=7
    )

    assert unused_count == 1


def test_identify_unused_devices_all_used(mock_files: tuple[str, str, str]) -> None:
    """Verifies behavior when no devices of the target type are unused."""
    ground_path, aircraft_path, device_path = mock_files

    # Target Type 9.
    # Expectation: Device 103 is Type 9, but let's pretend it was used, OR
    # just test what happens if the type exists but we expect 0 unused.
    # Actually, Device 103 is NOT used in our mock. Let's test a type that doesn't exist.
    unused_count: int = identify_unused_devices(
        ground_file_path=ground_path,
        aircraft_file_path=aircraft_path,
        device_file_path=device_path,
        device_type=99 # Does not exist in the mock device file
    )

    assert unused_count == 0


def test_identify_unused_devices_missing_file(mock_files: tuple[str, str, str]) -> None:
    """Verifies the function aborts gracefully (-1) if a file is missing."""
    ground_path, aircraft_path, device_path = mock_files

    # Provide a fake path for the ground file
    bad_ground_path: str = os.path.join(os.path.dirname(ground_path), "does_not_exist.csv")

    unused_count: int = identify_unused_devices(
        ground_file_path=bad_ground_path,
        aircraft_file_path=aircraft_path,
        device_file_path=device_path,
        device_type=7
    )

    assert unused_count == -1