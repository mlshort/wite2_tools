import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.scanning.scan_unit_for_ground_elem import (
    scan_unit_for_ground_elem
)


@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    """Minimal ground file required for the scanner's name lookups."""
    content = "id,name,other,type\n42,Tiger I,x,1\n"
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


def test_scan_unit_for_ground_elem_any_quantity(mock_unit_csv,
                                                mock_ground_csv,
                                                mock_ob_csv):
    """
    Verifies finding an element regardless of how many squads are assigned.
    Note: mock_unit_csv and mock_ob_csv are provided by conftest.py
    """
    # In conftest.py, ID 42 is at 'sqd.u5' in Unit ID 100 with a
    # quantity of 10.
    matches = scan_unit_for_ground_elem(
        unit_file_path=mock_unit_csv,
        ground_file_path=mock_ground_csv,
        ob_full_path=mock_ob_csv,
        target_wid=42,
        target_num_squads=-1  # -1 means ANY quantity
    )

    assert matches == 1


def test_scan_unit_for_ground_elem_exact_quantity(mock_unit_csv,
                                                  mock_ground_csv,
                                                  mock_ob_csv):
    """Verifies the exact quantity filter logic."""

    # 1. Test with the CORRECT quantity (10)
    matches_correct = scan_unit_for_ground_elem(
        unit_file_path=mock_unit_csv,
        ground_file_path=mock_ground_csv,
        ob_full_path=mock_ob_csv,
        target_wid=42,
        target_num_squads=10
    )
    assert matches_correct == 1

    # 2. Test with the WRONG quantity (99)
    matches_wrong = scan_unit_for_ground_elem(
        unit_file_path=mock_unit_csv,
        ground_file_path=mock_ground_csv,
        ob_full_path=mock_ob_csv,
        target_wid=42,
        target_num_squads=99
    )
    assert matches_wrong == 0  # Found the element, but quantity didn't match
