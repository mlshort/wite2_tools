import csv

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.replace_unit_ground_element import (
    replace_unit_ground_element,
)


@pytest.fixture(name="mock_replace_unit_csv")
def mock_replace_unit_csv(tmp_path):
    """
    Generates a mock _unit.csv to test global Ground Element replacements.
    """
    file_path = tmp_path / "mock_replace_unit.csv"

    headers = ["id", "name", "type", "nat"]
    for i in range(MAX_SQUAD_SLOTS):
        headers.append(f"sqd.u{i}")
        headers.append(f"sqd.num{i}")

    def create_row(uid, elem_slot0, elem_slot31):
        # Initialize all columns to "0"
        row = {h: "0" for h in headers}
        row.update({
            "id": uid,
            "name": "Test Unit",
            "type": "1",
            "nat": "1",
            "sqd.u0": elem_slot0,
            "sqd.u31": elem_slot31,
            "sqd.num0": "10",  # Dummy quantity
            "sqd.num31": "20"  # Dummy quantity
        })
        return row

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        # Row 1: Target 105 at slot 0
        writer.writerow(create_row("1", "105", "0"))

        # Row 2: Target 105 at the very end (slot 31) proving the loop reaches
        # the end
        writer.writerow(create_row("2", "55", "105"))

        # Row 3: Control row (Target 105 not present, should not be updated)
        writer.writerow(create_row("3", "99", "88"))

        # Row 4: Multiple instances of target 105 in the same unit
        writer.writerow(create_row("4", "105", "105"))

        # Row 5: Malformed string data (proves ValueError block prevents
        # crashes)
        writer.writerow(create_row("5", "INVALID", ""))

    return str(file_path)


def test_replace_unit_ground_element_success(mock_replace_unit_csv):
    """
    Verifies that the target Ground Element is replaced globally across
    all valid slots.
    """

    # Execute: Globally replace all instances of Ground Element 105 with 999
    updates = replace_unit_ground_element(
        unit_file_path=mock_replace_unit_csv,
        old_ge_id=105,
        new_ge_id=999
    )

    # Assert exactly 3 rows were updated (Rows 1, 2, and 4)
    assert updates == 3

    with open(mock_replace_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.DictReader(f))

        # Row 1: Slot 0 updated, quantity unchanged
        assert rows[0]["sqd.u0"] == "999"
        assert rows[0]["sqd.num0"] == "10"

        # Row 2: Slot 31 updated successfully
        assert rows[1]["sqd.u0"] == "55"
        assert rows[1]["sqd.u31"] == "999"

        # Row 3: Untouched control row
        assert rows[2]["sqd.u0"] == "99"
        assert rows[2]["sqd.u31"] == "88"

        # Row 4: Both slots updated in the same row
        assert rows[3]["sqd.u0"] == "999"
        assert rows[3]["sqd.u31"] == "999"

        # Row 5: Malformed data ignored cleanly without crashing
        assert rows[4]["sqd.u0"] == "INVALID"
