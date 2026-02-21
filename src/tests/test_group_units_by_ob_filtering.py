import pytest

from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.group_units_by_ob import group_units_by_ob, Unit


@pytest.fixture(autouse=True)
def clear_caches():
    """Ensure the @cache is cleared before every test run."""
    group_units_by_ob.cache_clear()


@pytest.fixture(name="mock_nat_unit_csv")
def mock_nat_unit_csv(tmp_path):
    """Creates a mock _unit.csv with multiple nationalities."""
    content = (
        "id,name,type,nat\n"
        "1,1st Panzer,10,1\n"   # German (Nat 1)
        "2,2nd Panzer,10,1\n"   # German (Nat 1)
        "3,1st Finnish,10,2\n"  # Finnish (Nat 2)
        "4,1st Italian,20,3\n"  # Italian (Nat 3)
        "5,Ghost Unit,0,1\n"    # Inactive (Type 0)
    )
    file_path = tmp_path / "mock_nat_units.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


def test_group_units_with_single_nat_filter(mock_nat_unit_csv):
    """Verifies filtering for a single nationality (Germany)."""
    # Act: Filter for Nat 1
    result = group_units_by_ob(mock_nat_unit_csv, nation_id=1)

    # Assert: Only IDs 1 and 2 should be present
    assert 10 in result
    assert len(result[10]) == 2
    assert all(u.nat == 1 for u in result[10])
    # Italian unit (ID 4) should be excluded
    assert 20 not in result


def test_group_units_with_multiple_nat_filter(mock_nat_unit_csv):
    """Verifies filtering for multiple nationalities (Germany and Italy)."""
    # FIX: Pass a tuple (1, 3) instead of a list [1, 3]
    result = group_units_by_ob(mock_nat_unit_csv, nation_id=(1, 3))

    # Assert: German units (Type 10) and Italian units (Type 20) present
    assert 10 in result
    assert 20 in result
    # Finnish unit (ID 3) should be excluded
    assert not any(u.unit_id == 3 for u in result[10])


def test_group_units_no_filter(mock_nat_unit_csv):
    """Verifies behavior when no nationality filter is applied."""
    # Act: No nation_id
    result = group_units_by_ob(mock_nat_unit_csv)

    # Assert: All active units (IDs 1, 2, 3, 4) should be present
    assert len(result[10]) == 3
    assert len(result[20]) == 1
    # Type 0 (ID 5) should still be skipped by default
    assert 0 not in result
