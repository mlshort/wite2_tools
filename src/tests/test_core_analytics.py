
import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.group_units_by_ob import Unit
from wite2_tools.core.group_units_by_ob import group_units_by_ob
from wite2_tools.core.count_global_unit_inventory import (
    count_global_unit_inventory
)

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(autouse=True, name="clear_caches")
def clear_caches():
    """Clear the group_units_by_ob cache between tests."""
    group_units_by_ob.cache_clear()


@pytest.fixture(name="mock_unit_csv")
def mock_unit_csv(tmp_path) -> str:
    content = (
        "id,name,type,nat,sqd.u0,sqd.num0,sqd.u1,sqd.num1\n"
        "1,1st Panzer,10,1,105,10,106,5\n"  # Nat 1 (Ger), 10x 105s, 5x 106s
        "2,2nd Panzer,10,1,105,5,0,0\n"     # Nat 1 (Ger), 5x 105s
        "3,3rd Infantry,20,2,106,10,0,0\n"  # Nat 2 (Fin), 10x 106s
        "0,Empty Data,0,1,105,100,0,0\n"    # Skip: Type is 0
    )
    file_path = tmp_path / "mock_unit.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    content = "id,name,other,type\n105,Panzer IV,x,1\n106,Tiger I,x,1\n"
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================


def test_group_units_by_ob(mock_unit_csv):
    """
    Verifies that units are correctly grouped by TOE(OB) ID
    and placeholders are skipped.
    """
    result = group_units_by_ob(mock_unit_csv)

    # TOE(OB) 10 should have two units
    assert result[10] == [Unit(unit_id=1, name="1st Panzer",
                               unit_type=10, nat=1),
                          Unit(unit_id=2, name="2nd Panzer",
                               unit_type=10, nat=1)]
    # TOE(OB) 20 should have one unit
    assert result[20] == [Unit(unit_id=3, name="3rd Infantry",
                               unit_type=20, nat=2)]
    # Type 0 should not be in the dictionary
    assert 0 not in result


def test_count_global_unit_inventory_no_filter(mock_unit_csv, mock_ground_csv):
    """
    Verifies that the script accurately sums all equipment across all
    valid units.
    """
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv)

    # ID 105 total: 10 + 5 = 15
    assert inventory[105] == 15
    # ID 106 total: 5 + 10 = 15
    assert inventory[106] == 15
    # Ensure the 100 panzers from the Type 0 row were not counted
    assert inventory[105] != 115


def test_count_global_unit_inventory_with_nat_filter(mock_unit_csv,
                                                     mock_ground_csv):
    """
    Verifies that the nationality filter strictly isolates specific
    factions.
    """
    # Run the count only for Nationality 1
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv,
                                            nation_id={1})

    # ID 105 total for Nat 1: 10 + 5 = 15
    assert inventory[105] == 15
    # ID 106 total for Nat 1: Only the 5 from 1st Panzer
    # (3rd Infantry is Nat 2)
    assert inventory[106] == 5


# reset from default
