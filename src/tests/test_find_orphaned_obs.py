from pathlib import Path
from typing import Callable

# Internal package imports
from wite2_tools.core.find_orphaned_obs import find_orphaned_obs


# ==========================================
# TEST CASES
# ==========================================


def test_find_unreferenced_ob_ids_success(mock_ob_csv: Path,
                                          mock_unit_csv: Path)->None:
    """
    Verifies that the core logic correctly identifies true orphans while safely
    ignoring OBs that exist inside a valid upgrade chain.
    """
    # Execute with no nationality filter
    orphans = find_orphaned_obs(str(mock_ob_csv), str(mock_unit_csv))

    assert orphans == {11, 12, 33, 51}


def test_find_unreferenced_ob_ids_with_nat_filter(
    make_ob_csv: Callable[..., Path],
    make_unit_csv: Callable[..., Path]
) -> None:
    # Create an Italian TOE (ID 70) and a used TOE (ID 99)
    ob_csv = make_ob_csv(
        filename="orphan_ob.csv",
        rows_data=[
            {"id": "70", "name": "Italian Div", "type": "1", "nat": "3",
             "firstYear" : "1941"},
            {"id": "99", "name": "Used Div", "type": "1", "nat": "3",
             "firstYear": "1941"}
        ]
    )

    # Create an Italian unit (Nat 3) that uses OB 99, leaving OB 70 orphaned.
    unit_csv = make_unit_csv(
        filename="orphan_unit.csv",
        rows_data=[
            {"id": "1", "name": "Ita Unit", "type": "99", "nat": "3",
             "firstUnit" : "1941"}
        ]
    )

    orphans_ita = find_orphaned_obs(
        str(ob_csv), str(unit_csv), nat_codes={3}
    )
    assert orphans_ita == {70}

def test_find_unreferenced_ob_ids_missing_files()->None:
    """
    Verifies graceful failure if the provided file paths are invalid.
    """
    orphans = find_orphaned_obs("does_not_exist.csv",
                                "also_missing.csv")

    # Should safely return an empty set without crashing
    assert orphans == set()
