import os
import pytest
from typing import Tuple

from wite2_tools.config import ENCODING_TYPE
from wite2_tools.modifiers.base import process_csv_in_place

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture
def mock_unit_csv(tmp_path) -> str:
    """Uses exact headers from your production _unit.csv."""
    headers = "id,name,type,nat,sqd.u0,sqd.num0\n"
    content = (
        "1,1st Panzer,100,1,105,10\n"
        "2,2nd Panzer,100,1,105,10\n"
        "3,3rd Infantry,200,1,15,10\n"
    )
    file_path = tmp_path / "mock_unit.csv"
    file_path.write_text(headers + content, encoding=ENCODING_TYPE)
    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================

def test_process_csv_successful_modification(mock_unit_csv):
    """Verifies that the wrapper successfully modifies and saves the file."""

    # 1. Define a callback that changes 'sqd.num0' to '99' if 'type' is '100'
    def mock_row_processor(row: dict, _row_idx: int) -> Tuple[dict, bool]:
        if row['type'] == '100':
            row['sqd.num0'] = '99'
            return row, True
        return row, False

    # 2. Execute the wrapper
    updates = process_csv_in_place(mock_unit_csv, mock_row_processor)

    # 3. Assert it counted exactly 2 updates (1st and 2nd Panzer)
    assert updates == 2
    #id,name,type,nat,sqd.u0,sqd.num0\n"
    # 4. Read the file back and assert the data was actually saved
    with open(mock_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()
        assert "1,1st Panzer,100,1,105,99" in content
        assert "2,2nd Panzer,100,1,105,99" in content
        assert "3,3rd Infantry,200,1,15,10" in content # Untouched


def test_process_csv_no_modifications(mock_unit_csv):
    """Verifies that the wrapper cleanly exits if no changes are made."""

    # 1. Define a callback that never modifies anything
    def mock_row_processor(row: dict, _row_idx: int) -> Tuple[dict, bool]:
        return row, False

    # 2. Capture the original modification time of the file
    original_mtime = os.path.getmtime(mock_unit_csv)

    # 3. Execute the wrapper
    updates = process_csv_in_place(mock_unit_csv, mock_row_processor)

    # 4. Assert 0 updates and that the file was never overwritten
    assert updates == 0
    assert os.path.getmtime(mock_unit_csv) == original_mtime


def test_process_csv_atomic_rollback_on_error(mock_unit_csv):
    """
    Ensures that if the script crashes halfway through processing,
    the original file is NOT corrupted or partially overwritten.
    The temporary file should be discarded and the original preserved.
    """
    def mock_row_processor(row: dict, row_idx: int) -> Tuple[dict, bool]:
        if row_idx == 1:
            row['sqd.num0'] = '99'
            return row, True
        if row_idx == 2:
            # This simulates a failure after the first row was "saved" in memory
            raise ValueError("Simulated unexpected crash!")
        return row, False

    # The wrapper gracefully catches the error and returns the updates made prior to the crash.
    process_csv_in_place(mock_unit_csv, mock_row_processor)

    # Verification
    with open(mock_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()
        # The first row change ('99') should NOT be present because the
        # temporary file was discarded upon the crash.
        assert "99" not in content
        assert "10" in content

def test_process_csv_file_not_found():
    """Verifies that the script handles non-existent paths gracefully."""
    def dummy_processor(row: dict, _idx: int) -> Tuple[dict, bool]:
        return row, False

    updates = process_csv_in_place("ghost_file.csv", dummy_processor)
    assert updates == 0

# updated with new mock_unit_csv