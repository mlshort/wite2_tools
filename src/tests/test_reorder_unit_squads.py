from typing import List
from pathlib import Path
from wite2_tools.models import (
    UnitRow,
)
from wite2_tools.modifiers.reorder_unit_squads import (
    reorder_unit_squads
)

def test_reorder_unit_elems_logic() -> None:
    """Verifies all interleaved unit attribute blocks shift in sync using UnitRow."""

    # 1. Setup: Use the new factory method on the class
    unit = UnitRow.create_default(unit_id=1, name="Test Unit")

    # 2. Place Data in Slot 1
    # Our __setattr__ logic ensures these values update the underlying _raw list
    unit.SQD_U0 = 99      # Target slot starts as 99
    unit.SQD_NUM0 = 10

    unit.SQD_U1 = 88      # Source slot starts as 88
    unit.SQD_NUM1 = 5

    # 3. Action: Call the class method we added to UnitRow
    # This moves the 8-column block at index 1 to index 0
    unit.reorder_slots(source_slot=1, target_slot=0)

    # 4. Assertions for Target (Slot 0)
    # The value 88 from slot 1 should now be here
    assert unit.SQD_U0 == 88, f"Expected WID 88 at Slot 0, found {unit.SQD_U0}"
    assert unit.SQD_NUM0 == 5, f"Expected Qty 5 at Slot 0, found {unit.SQD_NUM0}"

    # 5. Assertions for Shifting (Old Slot 0 is now Slot 1)
    # Depending on how your reorder_slots handles the 'insert',
    # the old slot 0 usually shifts to the right.
    assert unit.SQD_U1 == 99, "The old Slot 0 data should have shifted to Slot 1"
    assert unit.SQD_NUM1 == 10, f"Expected Qty 10 at Slot 1, found {unit.SQD_NUM1}"


def test_reorder_unit_squads_integration(mock_unit_csv: Path) -> None:
    """Tests the full file-write process using the list-stream logic."""
    # Target ID 42 is at slot 5 in the conftest fixture
    # The internal logic of reorder_unit_squads should now use get_csv_list_stream
    updates: int = reorder_unit_squads(
        str(mock_unit_csv),
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == 1


def test_reorder_unit_squads_integration_missing_file() -> None:
    """Tests error handling when the file path is invalid."""
    updates: int = reorder_unit_squads(
        "does_not_exist.csv",
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == -1
