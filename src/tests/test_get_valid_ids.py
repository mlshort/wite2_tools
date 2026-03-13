from pathlib import Path
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.utils.get_valid_ids import (
    get_valid_ob_ids,
    get_valid_ob_upgrade_ids,
    get_valid_ground_elem_ids,
    get_valid_unit_ids
)

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture(autouse=True, name="clear_caches")
def clear_caches()->None:
    """
    Automatically runs before every test to clear the @cache decorators.
    This guarantees that state does not leak between different tests.
    """
    get_valid_ob_ids.cache_clear()
    get_valid_ob_upgrade_ids.cache_clear()
    get_valid_ground_elem_ids.cache_clear()
    get_valid_unit_ids.cache_clear()


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


def test_ground_parser_skips_malformed_rows(tmp_path: Path) -> None:
    """Tests that the parser correctly skips bad IDs, Types, and short rows."""

    # 1. ARRANGE: Write intentionally broken text directly to a file
    content = (
        "id,name,id2,type\n"
        "100,Panzer,x,5\n"   # Valid
        "0,Empty,x,5\n"      # Skip: ID is 0
        "101,Tiger,x,0\n"    # Skip: Type is 0
        "bad,Tank,x,5\n"     # Skip: ValueError (Cannot parse 'bad' to int)
        "102\n"              # Skip: IndexError (Row too short)
    )
    mock_file = tmp_path / "broken_ground.csv"
    mock_file.write_text(content, encoding=ENCODING_TYPE)

    # 2. ACT: Pass this broken file to your parser function
    # parsed_data = your_ground_parsing_function(mock_file)

    # 3. ASSERT: Only ID 100 should have survived!
    # assert len(parsed_data) == 1
    # assert parsed_data[0].id == 100


def test_unit_parser_skips_invalid_data(tmp_path: Path) -> None:
    """Tests that the unit parser correctly skips bad IDs and Types."""
    content = (
        "id,name,type,nat\n"
        "500,1st Div,10,1\n"    # Valid
        "0,Placeholder,10,2\n"  # Skip: ID is 0
        "501,2nd Div,0,1\n"     # Skip: Type is 0
        "502,3rd Div,10,1\n"    # Valid
    )
    mock_file = tmp_path / "broken_unit.csv"
    mock_file.write_text(content, encoding=ENCODING_TYPE)
