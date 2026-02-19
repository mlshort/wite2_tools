import pytest
from wite2_tools.core.group_units_by_ob import group_units_by_ob

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture(autouse=True)
def clear_caches():
    """
    Automatically runs before every test to clear the @cache decorator.
    This guarantees that state does not leak between different tests.
    """
    group_units_by_ob.cache_clear()

@pytest.fixture
def mock_unit_csv(tmp_path) -> str:
    """Creates a mock _unit.csv file for testing the grouping logic."""
    content = (
        "id,name,type,nat\n"
        "1,1st Panzer,10,1\n"       # Valid: Group under OB 10
        "2,2nd Panzer,10,1\n"       # Valid: Group under OB 10 (Testing lists)
        "3,3rd Infantry,20,2\n"     # Valid: Group under OB 20
        "0,Placeholder,0,1\n"       # Skip: Both ID and Type are 0
        "4,Ghost Unit,0,1\n"        # Skip: Type is 0
    )
    file_path = tmp_path / "mock_unit.csv"
    file_path.write_text(content, encoding="ISO-8859-1")
    return str(file_path)

@pytest.fixture
def mock_corrupted_unit_csv(tmp_path) -> str:
    """Creates a mock _unit.csv with a ValueError trap."""
    content = (
        "id,name,type,nat\n"
        "1,1st Panzer,10,1\n"       # Valid
        "2,Bad Unit,INVALID,1\n"    # Corrupt: 'INVALID' fails int() conversion
        "3,3rd Infantry,20,2\n"     # Valid, but won't be reached due to crash
    )
    file_path = tmp_path / "mock_corrupted_unit.csv"
    file_path.write_text(content, encoding="ISO-8859-1")
    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================

def test_group_units_by_ob_success(mock_unit_csv):
    """Verifies that units are correctly grouped by OB ID into lists."""
    result = group_units_by_ob(mock_unit_csv)

    # OB 10 should contain two units
    assert result[10] == ["1st Panzer", "2nd Panzer"]

    # OB 20 should contain one unit
    assert result[20] == ["3rd Infantry"]

def test_group_units_by_ob_skips_type_zero(mock_unit_csv):
    """Verifies that units with a type of 0 are explicitly ignored."""
    result = group_units_by_ob(mock_unit_csv)

    # Type 0 should not be a key in the resulting dictionary at all
    assert 0 not in result

def test_group_units_by_ob_file_not_found():
    """Verifies graceful failure when the provided file does not exist."""
    result = group_units_by_ob("does_not_exist.csv")

    # Should safely return an empty dictionary without throwing a hard exception
    assert result == {}

def test_group_units_by_ob_aborts_on_malformed_data(mock_corrupted_unit_csv):
    """
    Verifies that the script catches the ValueError on malformed data,
    aborts the loop, and returns the data processed up to that point.
    """
    result = group_units_by_ob(mock_corrupted_unit_csv)

    # The 1st Panzer should be captured before the crash
    assert 10 in result
    assert result[10] == ["1st Panzer"]

    # The 3rd Infantry shouldn't be reached because 'INVALID' broke the loop
    assert 20 not in result