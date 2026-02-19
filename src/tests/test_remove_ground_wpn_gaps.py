import pytest
import csv
from wite2_tools.modifiers.remove_ground_weapon_gaps import remove_ground_weapon_gaps

@pytest.fixture
def mock_ground_csv(tmp_path) -> str:
    """Generates a mock _ground.csv with intentional gaps in the weapon slots."""
    file_path = tmp_path / "mock_ground_weapons.csv"

    # Core headers
    headers = ["id", "name", "type"]
    prefixes = ["wpn ", "wpnNum ", "wpnAmmo ", "wpnRof ", "wpnAcc ", "wpnFace "]

    for i in range(10):
        for p in prefixes:
            headers.append(f"{p}{i}")

    def create_row(uid, wpn_dict):
        row = {h: "0" for h in headers}
        row.update({"id": uid, "name": "Test Tank", "type": "1"})

        # Apply specific weapon data
        for k, v in wpn_dict.items():
            row[k] = v
        return row

    with open(file_path, 'w', newline='', encoding="ISO-8859-1") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Row 1 (ID 1): Gap at index 0. Weapon is at index 1.
        writer.writerow(create_row("1", {"wpn 1": "500", "wpnNum 1": "2"}))

        # Row 2 (ID 2): Multiple Gaps. Weapons at index 2 and 5.
        writer.writerow(create_row("2", {
            "wpn 2": "100", "wpnNum 2": "1",
            "wpn 5": "200", "wpnNum 5": "4"
        }))

        # Row 3 (ID 3): Perfectly packed. No gaps. Should not be modified.
        writer.writerow(create_row("3", {"wpn 0": "300", "wpnNum 0": "1"}))

    return str(file_path)

def test_remove_ground_weapon_gaps(mock_ground_csv):
    """Verifies that gaps are removed and weapons are shifted left/up."""

    # Execute the modifier
    updates = remove_ground_weapon_gaps(mock_ground_csv)

    # Assert that exactly 2 rows were modified (Rows 1 and 2)
    assert updates == 2

    # Verify the contents were actually shifted
    with open(mock_ground_csv, 'r', encoding="ISO-8859-1") as f:
        rows = list(csv.DictReader(f))

        # Row 1 Verification: Weapon 500 should now be at index 0
        assert rows[0]["wpn 0"] == "500"
        assert rows[0]["wpnNum 0"] == "2"
        assert rows[0]["wpn 1"] == "0"  # Original slot should be empty

        # Row 2 Verification: Weapons 100 and 200 should be at index 0 and