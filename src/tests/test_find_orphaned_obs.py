import csv

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.core.find_orphaned_obs import find_orphaned_obs

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(name="mock_ob_csv")
def mock_ob_csv(tmp_path) -> str:
    """
    Creates a mock _ob.csv with various upgrade chains and edge cases.
    """
    content = (
        "id,name,suffix,type,nat,upgrade\n"
        "10,Panzer,41,1,1,20\n"  # Referenced directly. Upgrades to 20.
        "20,Panzer,42,1,1,0\n"  # Not directly referenced, but safe via
                                # upgrade chain.
        "30,Orphan Div,A,1,1,0\n"  # NEVER referenced. Should be an orphan!
        "40,Infantry,41,4,1,50\n"  # Referenced directly. Upgrades to 50.
        "50,Infantry,42,4,1,60\n"  # Upgrades to 60.
        "60,Infantry,43,4,1,0\n"  # Safe via a deep 3-step upgrade chain!
        "70,Italian Div,41,4,3,0\n"  # Different Nationality (Nat 3). Never
                                     # referenced.
        "0,Placeholder,,0,0,0\n"  # Should be ignored.
    )
    file_path = tmp_path / "mock_ob.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


@pytest.fixture(name="mock_unit_csv")
def mock_unit_csv(tmp_path):
    file_path = tmp_path / "mock_unit.csv"

    # 1. Generate full width of _unit.csv headers
    headers = ["id", "name", "type", "nat"]
    for i in range(MAX_SQUAD_SLOTS):
        headers.append(f"sqd.u{i}")
        headers.append(f"sqd.num{i}")

    def create_row(uid: str, name: str, utype: str, nat: str):
        # Initialize all columns to "0"
        row = {h: "0" for h in headers}
        # Overwrite with specific unit data
        row.update({"id": uid, "name": name, "type": utype, "nat": nat})
        return row

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Row 1: References TOE(OB) 10 (which triggers the upgrade chain to 20)
        writer.writerow(create_row("1", "1st Panzer", "10", "1"))

        # Row 2: References TOE(OB) 40 (which triggers the chain to 50 -> 60)
        writer.writerow(create_row("2", "1st Infantry", "40", "1"))

        # Row 3: Invalid reference (proves your script ignores bad data)
        writer.writerow(create_row("3", "Bad Unit", "999", "1"))

    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================


def test_find_unreferenced_ob_ids_success(mock_ob_csv, mock_unit_csv):
    """
    Verifies that the core logic correctly identifies true orphans while safely
    ignoring OBs that exist inside a valid upgrade chain.
    """
    # Execute with no nationality filter
    orphans = find_orphaned_obs(mock_ob_csv, mock_unit_csv)

    # Assertions:
    # 10, 40: Referenced directly by units.
    # 20: Safe (10 -> 20)
    # 50, 60: Safe (40 -> 50 -> 60)
    # 30, 70: Orphans (Never referenced directly or in a chain)
    assert orphans == {30, 70}


def test_find_unreferenced_ob_ids_with_nat_filter(mock_ob_csv, mock_unit_csv):
    """
    Verifies that nationality filtering successfully isolates the orphan check
    to a specific faction.
    """
    # Execute: Filter ONLY for Nationality 1 (Germany)
    orphans_ger = find_orphaned_obs(mock_ob_csv, mock_unit_csv,
                                    nat_codes={1})

    # TOE(OB) 70 is Nat 3, so it shouldn't even be evaluated. Only TOE(OB) 30
    # should remain.
    assert orphans_ger == {30}

    # Execute: Filter ONLY for Nationality 3 (Italy)
    orphans_ita = find_orphaned_obs(mock_ob_csv, mock_unit_csv,
                                    nat_codes={3})

    # TOE(OB) 70 is never referenced by any Nat 3 units, so it is an orphan.
    assert orphans_ita == {70}


def test_find_unreferenced_ob_ids_missing_files():
    """
    Verifies graceful failure if the provided file paths are invalid.
    """
    orphans = find_orphaned_obs("does_not_exist.csv",
                                   "also_missing.csv")

    # Should safely return an empty set without crashing
    assert orphans == set()
