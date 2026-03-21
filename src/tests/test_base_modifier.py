
from wite2_tools.models import (
    UnitRow,
)
from wite2_tools.modifiers.reorder_unit_squads import (
    reorder_unit_squads
)


def test_reorder_unit_elems_logic() -> None:
    """Verifies interleaved unit attribute blocks shift in sync using UnitRow."""

    # 1. Setup: Use the factory method
    unit = UnitRow.create_default(unit_id=1, name="Test Unit", unit_type=1, nat=1)

    # 2. Place Data in Slot 1
    # Because of our custom __setattr__, these assignments automatically
    # update the underlying unit.raw list at the correct indices.
    unit.SQD_U1 = 99
    unit.SQD_NUM1 = 10

    # 3. Action: Call the class method
    unit.reorder_slots(1, 0)

    # 4. Assertions: Check the target (Slot 0)
    # The reorder_slots method refreshed these attributes from the list.
    assert unit.SQD_U0 == 99, "WID 99 should have moved to slot 0"
    assert unit.SQD_NUM0 == 10, "Qty 10 should have moved to slot 0"

    # 5. Assertions for Cleanup (Slot 1)
    # Since we 'popped' the block and 'inserted' it elsewhere,
    # whatever was in slot 2 shifted to slot 1 (which was likely all zeroes).
    assert unit.SQD_U1 == 0, "Source WID (Slot 1) should now be empty/shifted"
    assert unit.SQD_NUM1 == 0, "Source Qty (Slot 1) should now be empty/shifted"



def test_reorder_unit_squads_integration(mock_unit_csv: str) -> None:
    """
    Tests the full file-write process using list-based stream logic.
    """
    # This integration test now relies on the underlying modifier
    # using get_csv_list_stream internally.
    _, updates = reorder_unit_squads(
        mock_unit_csv,
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == 1


def test_reorder_unit_squads_integration_missing_file() -> None:
    """Verifies error handling for non-existent files."""
    _, updates = reorder_unit_squads(
        "does_not_exist.csv",
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == 0
