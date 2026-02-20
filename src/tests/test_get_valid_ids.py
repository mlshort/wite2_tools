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
def clear_caches():
    """
    Automatically runs before every test to clear the @cache decorators.
    This guarantees that state does not leak between different tests.
    """
    get_valid_ob_ids.cache_clear()
    get_valid_ob_upgrade_ids.cache_clear()
    get_valid_ground_elem_ids.cache_clear()
    get_valid_unit_ids.cache_clear()

@pytest.fixture(name="mock_ob_csv")
def mock_ob_csv(tmp_path) -> str:
    """
    Creates a temporary _ob.csv.
    Requires at least 10 columns so row[8] (type) and row[9] (upgrade) don't throw IndexError.
    Format: id, c1..c7, type, upgrade
    """
    content = (
        "id,name,suffix,nat,firstYear,firstMonth,lastYear,lastMonth,type,upgrade\n"  # Header
        "10,a,b,c,d,e,f,g,1,20\n"                 # Valid ID (10) and Valid Upgrade (20)
        "0,a,b,c,d,e,f,g,1,21\n"                  # Skip: ID is 0
        "11,a,b,c,d,e,f,g,0,22\n"                 # Skip: Type is 0
        "12,a,b,c,d,e,f,g,1,0\n"                  # Valid ID (12), but Upgrade is 0
        "invalid,a,b,c,d,e,f,g,1,20\n"            # Skip: ID is not an integer (ValueError)
        "13,a\n"                                  # Skip: Not enough columns (IndexError)
    )
    file_path = tmp_path / "mock_ob.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    """
    Creates a temporary _ground.csv.
    Requires at least 4 columns so row[3] (type) doesn't throw IndexError.
    Format: id, name, id2, type
    """
    content = (
        "id,name,id2,type\n"                      # Header
        "100,Panzer,x,5\n"                        # Valid ID (100)
        "0,Empty,x,5\n"                           # Skip: ID is 0
        "101,Tiger,x,0\n"                         # Skip: Type is 0
        "bad,Tank,x,5\n"                          # Skip: ValueError
        "102\n"                                   # Skip: IndexError
    )
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

@pytest.fixture(name="mock_unit_csv")
def mock_unit_csv(tmp_path) -> str:
    """
    Creates a temporary _unit.csv.
    Requires at least 3 columns so row[2] (type) doesn't throw IndexError.
    Format: id, name, type, nat
    """
    content = (
        "id,name,type,nat\n"                      # Header
        "500,1st Div,10,1\n"                      # Valid ID (500)
        "0,Placeholder,10,2\n"                    # Skip: ID is 0
        "501,2nd Div,0,1\n"                       # Skip: Type is 0
        "502,3rd Div,10,1\n"                      # Valid ID (502)
    )
    file_path = tmp_path / "mock_unit.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


# ==========================================
# TEST CASES
# ==========================================

def test_get_valid_ob_ids(mock_ob_csv):
    """Verifies parsing of TOE(OB) IDs based on non-zero ID and non-zero type."""
    valid_ids = get_valid_ob_ids(mock_ob_csv)
    # 10 is valid. 12 is valid (upgrade is 0, but ob_id and type are non-zero)
    assert valid_ids == {10, 12}

def test_get_valid_ob_upgrade_ids(mock_ob_csv):
    """Verifies extraction of upgrade targets based on non-zero ID, type, and upgrade."""
    upgrade_ids = get_valid_ob_upgrade_ids(mock_ob_csv)
    # Only 20 should be captured (from ID 10). ID 0 is skipped, Type 0 is skipped, ID 12 has upgrade 0.
    assert upgrade_ids == {20}

def test_get_valid_ground_elem_ids(mock_ground_csv):
    """Verifies extraction of Ground Element WIDs."""
    elem_ids = get_valid_ground_elem_ids(mock_ground_csv)
    assert elem_ids == {100}

def test_get_valid_unit_ids(mock_unit_csv):
    """Verifies extraction of Unit IDs."""
    unit_ids = get_valid_unit_ids(mock_unit_csv)
    assert unit_ids == {500, 502}

def test_file_not_found_returns_empty_set():
    """Verifies that missing files are handled gracefully and return an empty set."""
    fake_path = "does_not_exist.csv"

    assert get_valid_ob_ids(fake_path) == set()
    assert get_valid_ob_upgrade_ids(fake_path) == set()
    assert get_valid_ground_elem_ids(fake_path) == set()
    assert get_valid_unit_ids(fake_path) == set()

# reset
