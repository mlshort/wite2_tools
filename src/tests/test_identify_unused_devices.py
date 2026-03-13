from pathlib import Path
from typing import Callable, Tuple
import pytest

from wite2_tools.models import (
    gen_default_device_row,
    gen_device_column_names,
    DevColumn
)

from wite2_tools.core.identify_unused_devices import identify_unused_devices


@pytest.fixture
def mock_files(make_ground_csv: Callable[..., Path],
               make_aircraft_csv: Callable[..., Path],
               make_device_csv: Callable[..., Path]) -> Tuple[Path, Path, Path]:

    # Helper to force the Type into the correct column index
    headers = gen_device_column_names()
    def _make_dev(d_id: int, name: str, d_type: int) -> dict:
        row = gen_default_device_row(d_id, name)
        row[DevColumn.TYPE] = str(d_type)
        return dict(zip(headers, row))

    device_csv = make_device_csv(
        filename="mock_device_unused.csv",
        rows_data=[
            _make_dev(100, "75mm Gun", 7),
            _make_dev(101, "88mm Flak", 7),
            _make_dev(102, "105mm Howitzer", 7),
            _make_dev(103, "150mm Howitzer", 9),
            _make_dev(104, "Unused Gun A", 7),
            _make_dev(105, "Unused Gun B", 7),
        ]
    )
    # --- 2. Setup Ground File ---
    ground_csv = make_ground_csv(
        filename="mock_ground_unused.csv",
        rows_data=[
            # Ground element using device 100 in slot 0
            # (Using your conftest 'weapons' tuple parser: slot, wpn_id, quantity)
            {"id": "1", "name": "Infantry Squad", "weapons": [(0, "100", "1")]}
        ]
    )

    # --- 3. Setup Aircraft File ---
    aircraft_csv = make_aircraft_csv(
        filename="mock_aircraft_unused.csv",
        rows_data=[
            # Aircraft using device 101 in weapon slot 0
            {"id": "10", "name": "Bf 109", "wpn 0": "101"}
        ]
    )

    return ground_csv, aircraft_csv, device_csv


def test_identify_unused_devices_finds_unused(tmp_path: Path,
                                              make_ground_csv: Callable[..., Path],
                                              make_aircraft_csv: Callable[..., Path]) -> None:
    # 1. Bulletproof Device CSV creation
    device_csv = tmp_path / "mock_device.csv"
    device_csv.write_text("id,name,type\n100,75mm Gun,7\n101,88mm Flak,7\n102,105mm Howitzer,7\n103,150mm Howitzer,9\n104,Unused Gun A,7\n105,Unused Gun B,7", encoding="utf-8")

    # 2. Factory creation for the others
    ground_csv = make_ground_csv(rows_data=[{"id": "1", "weapons": [(0, "100", "1")]}])
    aircraft_csv = make_aircraft_csv(rows_data=[{"id": "10", "wpn 0": "101"}])

    unused_count = identify_unused_devices(str(ground_csv),
                                           str(aircraft_csv),
                                           str(device_csv), 7)

    # 102, 104, 105
    assert unused_count == 3


def test_identify_unused_devices_all_used(mock_files: Tuple[Path, Path, Path]) -> None:
    """Verifies behavior when no devices of the target type are unused."""
    ground_path, aircraft_path, device_path = mock_files

    unused_count: int = identify_unused_devices(
        ground_file_path=str(ground_path),
        aircraft_file_path=str(aircraft_path),
        device_file_path=str(device_path),
        device_type=99 # Does not exist in the mock device file
    )

    assert unused_count == 0


def test_identify_unused_devices_missing_file(mock_files: Tuple[Path, Path, Path],
                                              tmp_path: Path) -> None:
    """Verifies the function aborts gracefully (-1) if a file is missing."""
    _, aircraft_path, device_path = mock_files

    # Provide a fake path for the ground file
    bad_ground_path = tmp_path / "does_not_exist.csv"

    unused_count: int = identify_unused_devices(
        ground_file_path=str(bad_ground_path),
        aircraft_file_path=str(aircraft_path),
        device_file_path=str(device_path),
        device_type=7
    )

    assert unused_count == -1
