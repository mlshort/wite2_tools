from pathlib import Path
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.group_units_by_ob import UnitData
from wite2_tools.core.group_units_by_ob import (
    _group_units_by_ob,
    group_units_by_ob
)

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(autouse=True, name="clear_caches")
def clear_caches() -> None:
    """
    Automatically runs before every test to clear the @cache decorator.
    This guarantees that state does not leak between different tests.
    """
    _group_units_by_ob.cache_clear()


@pytest.fixture(name="mock_corrupted_unit_csv")
def mock_corrupted_unit_csv(tmp_path:Path) -> Path:
    """Creates a mock _unit.csv with a ValueError trap."""
    content = (
        "id,name,type,nat\n"
        "1,1st Panzer,10,1\n"     # Valid
        "2,Bad Unit,INVALID,1\n"  # Corrupt: 'INVALID' fails int() conversion
        "3,3rd Infantry,20,2\n"   # Valid
    )
    file_path = tmp_path / "mock_corrupted_unit.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return file_path

# ==========================================
# TEST CASES
# ==========================================


def test_group_units_by_ob_success(mock_unit_csv: Path)->None:
    """Verifies that units are correctly grouped by TOE(OB) ID into lists."""
    result = group_units_by_ob(str(mock_unit_csv))

    # TOE(OB) 10 should contain two units
    assert result[45] == [UnitData(uid=60, name="1st Panzer",
                               utype=45, nat=1),
                          UnitData(uid=61, name="2nd Panzer",
                               utype=45, nat=1)]

    # TOE(OB) 30 should contain one unit
    assert result[30] == [UnitData(uid=63, name="3rd Infantry",
                               utype=30, nat=2)]


def test_group_units_by_ob_skips_type_zero(mock_unit_csv: Path)->None:
    """Verifies that units with a type of 0 are explicitly ignored."""
    result = group_units_by_ob(str(mock_unit_csv))

    # Type 0 should not be a key in the resulting dictionary at all
    assert 0 not in result


def test_group_units_by_ob_file_not_found()->None:
    """Verifies graceful failure when the provided file does not exist."""
    result = group_units_by_ob("does_not_exist.csv")

    # Should safely return an empty dictionary without throwing a hard
    # exception
    assert not result


def test_group_units_by_ob_aborts_on_malformed_data(mock_corrupted_unit_csv: Path)->None:
    """
    Verifies that the script catches the ValueError on malformed data,
    aborts the loop, and returns the data processed up to that point.
    """
    result = group_units_by_ob(str(mock_corrupted_unit_csv))
    # The 1st Panzer should be captured
    assert 10 in result

    assert result[10] == [UnitData(uid=1, name="1st Panzer",
                               utype=10, nat=1)]

    # The 'Bad Unit' shouldn't be returned
    assert 2 not in result
