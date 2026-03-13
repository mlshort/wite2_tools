from pathlib import Path
from typing import Callable

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.count_global_unit_inventory import (
    count_global_unit_inventory,
)


# ==========================================
# TEST CASES
# ==========================================


def test_inventory_total_aggregation(
    make_unit_csv: Callable[..., Path],
    make_ground_csv: Callable[..., Path]
) -> None:
    """Verifies items are summed correctly across active units."""
    unit_csv = make_unit_csv(
        filename="agg_unit.csv",
        rows_data=[{"id": "100", "squads": [(0, "101", "10")]}]
    )
    ground_csv = make_ground_csv(
        filename="agg_ground.csv",
        rows_data=[{"id": "101", "weapons": [(0, "999", "1")]}]
    )

    inventory = count_global_unit_inventory(str(unit_csv), str(ground_csv))
    assert inventory[101] == 10


def test_inventory_nationality_filtering(
    make_unit_csv: Callable[..., Path],
    make_ground_csv: Callable[..., Path]
) -> None:
    """Verifies the nationality filter isolates counts to a faction."""
    unit_csv = make_unit_csv(
        filename="nat_unit.csv",
        rows_data=[{"id": "100", "nat": "2", "squads": [(0, "102", "20")]}]
    )
    ground_csv = make_ground_csv(
        filename="nat_ground.csv",
        rows_data=[{"id": "102", "weapons": [(0, "999", "1")]}]
    )

    inventory = count_global_unit_inventory(
        str(unit_csv), str(ground_csv), nat_codes=2
    )
    assert inventory[102] == 20


def test_inventory_multiple_nat_filtering(
    make_unit_csv: Callable[..., Path],
    make_ground_csv: Callable[..., Path]
) -> None:
    """Verifies that passing a list of nat codes works."""
    unit_csv = make_unit_csv(
        filename="multi_unit.csv",
        rows_data=[{"id": "100", "nat": "1", "squads": [(0, "101", "10")]}]
    )
    ground_csv = make_ground_csv(
        filename="multi_ground.csv",
        rows_data=[{"id": "101", "weapons": [(0, "999", "1")]}]
    )

    inventory = count_global_unit_inventory(
        str(unit_csv), str(ground_csv), nat_codes=[1, 2]
    )
    assert inventory[101] == 10


def test_inventory_robustness_to_malformed_data(
    make_unit_csv: Callable[..., Path],
    make_ground_csv: Callable[..., Path]
) -> None:
    """Verifies that a ValueError doesn't stop the whole script."""
    unit_csv = make_unit_csv(
        filename="robust_unit.csv",
        rows_data=[
            {"id": "1", "squads": [(0, "101", "BAD_DATA")]},
            {"id": "2", "squads": [(0, "101", "10")]}
        ]
    )
    ground_csv = make_ground_csv(
        filename="robust_ground.csv",
        rows_data=[{"id": "101", "weapons": [(0, "999", "1")]}]
    )

    inventory = count_global_unit_inventory(str(unit_csv), str(ground_csv))
    assert 101 in inventory



def test_inventory_empty_file(tmp_path: Path,
                              mock_ground_csv: Path)->None:
    """
    Verifies that an empty or header-only file returns an empty dictionary.
    """
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("id,name,type,nat\n", encoding=ENCODING_TYPE)

    inventory = count_global_unit_inventory(str(empty_file),
                                            str(mock_ground_csv))
    assert not inventory
