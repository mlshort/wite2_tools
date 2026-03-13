from typing import List, Callable
from pathlib import Path

# Import the correct schema for OB files
from wite2_tools.models import (
    ELEM_BASE, NUM_BASE,
    gen_default_ob_row,
    gen_ob_column_names,
    ObColumn
)
from wite2_tools.modifiers.reorder_ob_squads import (
    reorder_ob_elems,
    reorder_ob_squads
)

def test_reorder_ob_elems_logic() -> None:
    """Verifies TOE(OB) squad attribute blocks shift correctly using schema offsets."""

    # 1. Setup: Initialize a list representing a CSV row
    row: List[str] = gen_default_ob_row()

    # 2. Setup: Place a Ground Element (WID 500) in Slot 2
    # Access: Base Index + Slot Offset
    row[ELEM_BASE + 2] = "500"
    row[NUM_BASE + 2] = "10" # Adding a quantity for completeness

    # 3. Action: Shift element from slot 2 to slot 0
    # Note: Strings "sqd " and "sqdNum " are no longer required as arguments
    updated: List[str] = reorder_ob_elems(row, source_slot=2, target_slot=0)

    # 4. Assertions: Verify data moved to index 0 of the respective blocks
    assert updated[ELEM_BASE] == "500"
    assert updated[NUM_BASE] == "10"

    # Verify the source slot (2) is now "0"
    assert updated[ELEM_BASE + 2] == "0"


def test_reorder_ob_squads_integration(
    make_ob_csv: Callable[..., Path]
) -> None:
    # Use the expected tuples: (slot_idx, WID, quantity)
    custom_ob_csv = make_ob_csv(
        filename="custom_reorder_ob.csv",
        rows_data=[{
            "id": "10",
            "name": "Test TOE",
            "squads": [(0, "100", "10"), (1, "500", "10")]
        }]
    )

    updates: int = reorder_ob_squads(
        str(custom_ob_csv),
        target_ob_id=10,
        target_wid=500,
        target_slot=0
    )
    assert updates == 1
