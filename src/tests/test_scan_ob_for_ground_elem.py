import pytest

# Internal package imports
from wite2_tools.scanning.scan_ob_for_ground_elem import (
    scan_ob_for_ground_elem
)


def test_scan_ob_for_ground_elem_success(mock_ob_csv, capsys):
    """
    Verifies the TOE(OB) scanner finds target ground elements across the 32
    slots.
    Note: mock_ob_csv fixture is provided by conftest.py
    """
    # In conftest.py, ID 500 is placed at "sqd 2" of TOE(OB) ID 10
    matches = scan_ob_for_ground_elem(mock_ob_csv, 500)

    assert matches == 1

    # Verify console output format using pytest's capsys
    captured = capsys.readouterr()
    assert "Found 1 WID match(es)." in captured.out
    assert "'sqd 2'" in captured.out


def test_scan_ob_for_ground_elem_no_matches(mock_ob_csv, capsys):
    """
    Verifies the scanner returns 0 and prints correctly when no match is found.
    """
    matches = scan_ob_for_ground_elem(mock_ob_csv, 9999)

    assert matches == 0
    captured = capsys.readouterr()
    assert "No matches found." in captured.out


def test_scan_ob_for_ground_elem_missing_file():
    """
    Verifies graceful failure when the file doesn't exist.
    """
    matches = scan_ob_for_ground_elem("does_not_exist.csv", 500)
    assert matches == 0
