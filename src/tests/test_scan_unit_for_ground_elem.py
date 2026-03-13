from pathlib import Path

# Internal package imports
from wite2_tools.scanning.scan_unit_for_ground_elem import (
    scan_unit_for_ground_elem
)



def test_scan_unit_for_ground_elem_any_quantity(mock_unit_csv:Path,
                                                mock_ground_csv:Path,
                                                mock_ob_csv:Path) -> None:
    """
    Verifies finding an element regardless of how many squads are assigned.
    Note: mock_unit_csv and mock_ob_csv are provided by conftest.py
    """
    matches = scan_unit_for_ground_elem(
        unit_file_path=str(mock_unit_csv),
        ground_file_path=str(mock_ground_csv),
        ob_full_path=str(mock_ob_csv),
        target_wid=42,
        target_num_squads=-1  # -1 means ANY quantity
    )

    assert matches == 2


def test_scan_unit_for_ground_elem_exact_quantity(mock_unit_csv:Path,
                                                  mock_ground_csv:Path,
                                                  mock_ob_csv:Path) -> None:
    """Verifies the exact quantity filter logic."""

    # 1. Test with the CORRECT quantity (10)
    matches_correct = scan_unit_for_ground_elem(
        unit_file_path=str(mock_unit_csv),
        ground_file_path=str(mock_ground_csv),
        ob_full_path=str(mock_ob_csv),
        target_wid=42,
        target_num_squads=10
    )
    assert matches_correct == 1

    # 2. Test with the WRONG quantity (99)
    matches_wrong = scan_unit_for_ground_elem(
        unit_file_path=str(mock_unit_csv),
        ground_file_path=str(mock_ground_csv),
        ob_full_path=str(mock_ob_csv),
        target_wid=42,
        target_num_squads=99
    )
    assert matches_wrong == 0  # Found the element, but quantity didn't match
