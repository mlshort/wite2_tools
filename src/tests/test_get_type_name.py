import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.utils.get_type_name import (
    _build_ob_lookup,
    _build_ground_elem_lookup,
    get_ob_full_name,
    get_ground_elem_type_name
)

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture(autouse=True, name="clear_caches")
def clear_caches():
    """
    Automatically runs before every test to clear the @cache decorators.
    This ensures that Test A doesn't accidentally use the cached data from Test B!
    """
    _build_ob_lookup.cache_clear()
    _build_ground_elem_lookup.cache_clear()

@pytest.fixture(name="mock_ob_csv")
def mock_ob_csv(tmp_path) -> str:
    """Creates a temporary, miniaturized _ob.csv file for testing."""
    content = (
        "id,name,suffix,type\n"       # Header
        "10,Panzer Div,41,1\n"        # Valid row
        "0,Placeholder,,0\n"          # Should be skipped (ID and Type = 0)
        "11,Infantry Div,42,4\n"      # Valid row
        "invalid,BadRow,,1\n"         # Should be skipped (Invalid ID)
    )
    # Write to a temporary file managed by pytest
    file_path = tmp_path / "mock_ob.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    """Creates a temporary, miniaturized _ground.csv file for testing."""
    content = (
        "id,name,other,type\n"        # Header
        "105,Panzer IV,x,13\n"        # Valid row
        "0,Empty,x,0\n"               # Should be skipped
        "106,Tiger I,x,14\n"          # Valid row
    )
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


# ==========================================
# TEST CASES
# ==========================================

def test_get_ob_full_name_success(mock_ob_csv):
    """Verifies that the TOE(OB) lookup correctly parses and combines strings."""
    assert get_ob_full_name(mock_ob_csv, 10) == "Panzer Div 41"
    assert get_ob_full_name(mock_ob_csv, 11) == "Infantry Div 42"

def test_get_ob_full_name_missing_id(mock_ob_csv):
    """Verifies the fallback logic when an ID is not in the CSV."""
    assert get_ob_full_name(mock_ob_csv, 999) == "Unk (999)"
    assert get_ob_full_name(mock_ob_csv, 0) == "Unk (0)" # 0 was skipped during parse

def test_get_ground_elem_type_name_success(mock_ground_csv):
    """Verifies that the Ground Element lookup correctly parses strings."""
    assert get_ground_elem_type_name(mock_ground_csv, 105) == "Panzer IV"
    assert get_ground_elem_type_name(mock_ground_csv, 106) == "Tiger I"

def test_get_ground_elem_type_name_missing_id(mock_ground_csv):
    """Verifies the fallback logic for Ground Elements."""
    assert get_ground_elem_type_name(mock_ground_csv, 999) == "Unk (999)"

def test_file_not_found_graceful_fail():
    """Verifies the script doesn't crash if the file path is completely invalid."""
    fake_path = "this/does/not/exist.csv"
    assert get_ob_full_name(fake_path, 10) == "Unk (10)"
    assert get_ground_elem_type_name(fake_path, 105) == "Unk (105)"
