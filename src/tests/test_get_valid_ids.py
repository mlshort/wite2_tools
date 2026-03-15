from pathlib import Path

# Internal package imports
from wite2_tools.utils.get_valid_ids import (
    get_valid_ob_ids,
    get_valid_ob_upgrade_ids,
    get_valid_ground_elem_ids,
    get_valid_unit_ids
)


# ==========================================
# TEST CASES
# ==========================================
def test_get_valid_ob_ids(mock_ob_csv: Path)->None:
    """
    Verifies parsing of TOE(OB) IDs based on non-zero ID and non-zero type.
    """
    valid_ids = get_valid_ob_ids(mock_ob_csv)

    assert valid_ids == {1, 10, 11, 12, 20, 30, 33, 40, 50, 51, 60, 70, 99}


def test_get_valid_ob_upgrade_ids(mock_ob_csv: Path)->None:
    """
    Verifies extraction of upgrade targets based on non-zero ID, type,
    and upgrade.
    """
    upgrade_ids = get_valid_ob_upgrade_ids(mock_ob_csv)
    assert upgrade_ids == {20, 50, 60}


def test_get_valid_ground_elem_ids(mock_ground_csv: Path)->None:
    """Verifies extraction of Ground Element WIDs."""
    elem_ids = get_valid_ground_elem_ids(mock_ground_csv)
    assert elem_ids == {1, 2, 3, 4, 42,
                        51, 52, 53,
                        100, 105,
                        201, 202, 203, 204, 500}


def test_get_valid_unit_ids(mock_unit_csv: Path)->None:
    """Verifies extraction of Unit IDs."""
    unit_ids = get_valid_unit_ids(mock_unit_csv, True)
    assert unit_ids == {1, 2, 3, 4, 5, 10, 11, 12, 60, 61, 63,
                        100, 101, 102, 103, 104,
                        201, 202, 203, 204, 500, 502}


def test_file_not_found_returns_empty_set()->None:
    """
    Verifies that missing files are handled gracefully and return an empty
    set.
    """
    fake_path = "does_not_exist.csv"

    assert get_valid_ob_ids(fake_path) == set()
    assert get_valid_ob_upgrade_ids(fake_path) == set()
    assert get_valid_ground_elem_ids(fake_path) == set()
    assert get_valid_unit_ids(fake_path) == set()


