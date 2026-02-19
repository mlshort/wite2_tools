import csv
import pytest

from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.update_unit_num_squads import update_unit_num_squads

@pytest.fixture
def mock_update_unit_csv(tmp_path):
    """Generates a 4-row truth table to test all conditional updating paths."""
    file_path = tmp_path / "mock_update_unit.csv"

    headers = ["id", "name", "type", "nat"]
    for i in range(MAX_SQUAD_SLOTS):
        headers.append(f"sqd.u{i}")
        headers.append(f"sqd.num{i}")

    def create_row(uid, utype, elem_id, qty):
        # Initialize all columns to "0"
        row = {h: "0" for h in headers}
        # 'type' is the OB ID in unit files
        row.update({
            "id": uid,
            "name": "Test Unit",
            "type": utype,
            "nat": "1",
            "sqd.u0": elem_id,
            "sqd.num0": qty
        })
        return row

    with open(file_path, 'w', newline='', encoding="ISO-8859-1") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Row 1 (Index 0): SUCCESS (Matches OB=50, Elem=105, Qty=10)
        writer.writerow(create_row("1", "50", "105", "10"))

        # Row 2 (Index 1): FAILS (Wrong OB ID - 99 instead of 50)
        writer.writerow(create_row("2", "99", "105", "10"))

        # Row 3 (Index 2): FAILS (Wrong Element ID - 999 instead of 105)
        writer.writerow(create_row("3", "50", "999", "10"))

        # Row 4 (Index 3): FAILS (Wrong Old Qty - 15 instead of 10)
        writer.writerow(create_row("4", "50", "105", "15"))

    return str(file_path)

def test_update_unit_num_squads_success_and_filters(mock_update_unit_csv):
    """Verifies that the strict multi-level conditions are applied correctly."""

    # Execute: In OB 50, if Elem 105 has qty 10, change it to 99
    updates = update_unit_num_squads(
        mock_update_unit_csv,
        target_ob_id=50,
        ge_id=105,
        old_num_squads=10,
        new_num_squads=99
    )

    # Assert ONLY Row 1 was updated by the script
    assert updates == 1

    with open(mock_update_unit_csv, 'r', encoding="ISO-8859-1") as f:
        rows = list(csv.DictReader(f))

        # Assert data integrity using the 4-Row Truth Table
        assert rows[0]["sqd.num0"] == "99" # Successful change
        assert rows[1]["sqd.num0"] == "10" # Blocked by OB check
        assert rows[2]["sqd.num0"] == "10" # Blocked by Elem check
        assert rows[3]["sqd.num0"] == "15" # Blocked by Old Qty check