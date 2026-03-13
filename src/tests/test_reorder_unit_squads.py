from typing import List
from wite2_tools.models import (
    UnitColumn,
    gen_default_unit_row,
    ATTRS_PER_SQD
)
from wite2_tools.modifiers.reorder_unit_squads import (
    reorder_unit_elems,
    reorder_unit_squads
)

def test_reorder_unit_elems_logic() -> None:
    """Verifies all 8 unit attributes shift in sync using UnitColumn offsets."""

    # 1. Initialize a 'row' as a list (matching get_csv_list_stream output)
    row: List[str] = gen_default_unit_row()

    # Calculate exact offsets for Slot 1 by jumping over 8 columns
    u_idx_1 = UnitColumn.SQD_U0 + (1 * ATTRS_PER_SQD)
    num_idx_1 = UnitColumn.SQD_NUM0 + (1 * ATTRS_PER_SQD)

    row[u_idx_1] = "99"
    row[num_idx_1] = "10"

    # 3. Action: Move from slot 1 to slot 0
    # The function manipulates the list based on these 8-column chunks
    updated = reorder_unit_elems(row, source_slot=1, target_slot=0)

    # 4. Assertions using Schema Offsets for Target (Slot 0)
    u_idx_0 = UnitColumn.SQD_U0 + (0 * ATTRS_PER_SQD)
    num_idx_0 = UnitColumn.SQD_NUM0 + (0 * ATTRS_PER_SQD)

    assert updated[u_idx_0] == "99", f"Expected WID 99 at index {u_idx_0}"
    assert updated[num_idx_0] == "10", f"Expected Qty 10 at index {num_idx_0}"

    # 5. Assertions for Source Cleanup (Slot 1)
    assert updated[u_idx_1] == "0", "Source WID should be vacated"
    assert updated[num_idx_1] == "0", "Source Qty should be vacated"


def test_reorder_unit_squads_integration(mock_unit_csv: str) -> None:
    """Tests the full file-write process using the list-stream logic."""
    # Target ID 42 is at slot 5 in the conftest fixture
    # The internal logic of reorder_unit_squads should now use get_csv_list_stream
    updates: int = reorder_unit_squads(
        mock_unit_csv,
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
