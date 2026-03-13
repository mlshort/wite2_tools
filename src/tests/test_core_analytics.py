
from pathlib import Path
from typing import Callable
import pytest

# Internal package imports
from wite2_tools.core.group_units_by_ob import UnitData
from wite2_tools.core.group_units_by_ob import (
    _group_units_by_ob,
    group_units_by_ob
)
from wite2_tools.core.count_global_unit_inventory import (
    count_global_unit_inventory
)

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(autouse=True, name="clear_caches")
def clear_caches() -> None:
    """Clear the group_units_by_ob cache between tests."""
    _group_units_by_ob.cache_clear()

# ==========================================
# TEST CASES
# ==========================================


def test_group_units_by_ob(make_unit_csv: Callable[..., Path]) -> None:
    """
    Verifies that units are correctly grouped by TOE(OB)
    and placeholders are skipped.
    """
# 1. Create a custom file with exactly what the test expects
    unit_csv = make_unit_csv(
        filename="group_unit.csv",
        rows_data=[
            {"id": "1", "name": "1st Panzer", "type": "10", "nat": "1"},
            {"id": "2", "name": "2nd Panzer", "type": "10", "nat": "1"},
            {"id": "3", "name": "3rd Infantry", "type": "20", "nat": "2"}
        ]
    )

    result = group_units_by_ob(str(unit_csv))

    # TOE(OB) 10 should have two units
    assert result[10] == [UnitData(uid=1, name="1st Panzer",
                               utype=10, nat=1),
                          UnitData(uid=2, name="2nd Panzer",
                               utype=10, nat=1)]
    # TOE(OB) 20 should have one unit
    assert result[20] == [UnitData(uid=3, name="3rd Infantry",
                               utype=20, nat=2)]
    # Type 0 should not be in the dictionary
    assert 0 not in result


def test_count_global_unit_inventory_no_filter(mock_unit_csv: Path,
                                               mock_ground_csv: Path) -> None:
    """
    Verifies that the script accurately sums all equipment across all
    valid units.
    """
    inventory = count_global_unit_inventory(str(mock_unit_csv),
                                            str(mock_ground_csv))

    assert inventory[105] == 36
    assert inventory[106] == 25
    # Ensure the 100 panzers from the Type 0 row were not counted
    assert inventory[105] != 115


def test_count_global_unit_inventory_with_nat_filter(mock_unit_csv: Path,
                                                     mock_ground_csv: Path) -> None:
    """
    Verifies that the nationality filter strictly isolates specific
    factions.
    """
    # Run the count only for Nationality 1
    inventory = count_global_unit_inventory(str(mock_unit_csv),
                                            str(mock_ground_csv),
                                            nat_codes={1})

    assert inventory[105] == 26
    assert inventory[106] == 5

