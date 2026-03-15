from typing import Callable
from pathlib import Path

# Import the correct schema for OB files
from wite2_tools.models import (
    ObRow,
    ObColumn
)
from wite2_tools.generator import get_csv_list_stream

def test_obrow_reorder_slots_logic() -> None:
    """
    Verifies TOE(OB) squad attribute blocks shift correctly using ObRow's internal method.
    """

    # 1. Setup: Initialize a default ObRow
    ob = ObRow.create_default()

    # 2. Setup: Place a Ground Element (WID 500) and quantity (10) in Slot 2
    # We modify the underlying raw list using the Enum offsets to set up the test state
    sqd_base = ObColumn.SQD_0
    num_base = ObColumn.SQD_NUM_0

    ob.raw[sqd_base + 2] = "500"
    ob.raw[num_base + 2] = "10"

    # Re-init to sync the named attributes (e.g., ob.SQD_2) with the raw list we just touched
    ob.__init__(ob.raw)

    # Verify setup worked
    assert ob.SQD_2 == 500
    assert ob.SQD_NUM_2 == 10

    # 3. Action: Shift element from slot 2 to slot 0
    # ObRow method handles popping, inserting, and re-syncing the object
    ob.reorder_slots(source_slot=2, target_slot=0)

    # 4. Assertions: Verify data moved to index 0 and attributes are synced
    assert ob.SQD_0 == 500
    assert ob.SQD_NUM_0 == 10

    # Verify the source slot (2) shifted correctly
    # Since slot 2 moved to 0, the old slot 0 (which was 0) shifted to 1,
    # and the old slot 1 (which was 0) shifted to 2.
    assert ob.SQD_2 == 0
    assert ob.SQD_NUM_2 == 0

def test_obrow_integration_with_csv(
    make_ob_csv: Callable[..., Path]
) -> None:
    """
    Integration test: Verifies that an ObRow can be instantiated from a real CSV file,
    modified using its internal methods, and successfully shift other elements.
    """
    # 1. Setup: Create the mock CSV with our test data
    # Slot 0 has WID 100, Slot 1 has WID 500
    custom_ob_csv = make_ob_csv(
        filename="custom_reorder_ob.csv",
        rows_data=[{
            "id": "10",
            "name": "Test TOE",
            "squads": [(0, "100", "10"), (1, "500", "10")]
        }]
    )

    processed_ob = None

    # 2. Action: Read the CSV and process the target row using ObRow
    # get_csv_list_stream handles file opening, closing, and stripping the header
    stream = get_csv_list_stream(str(custom_ob_csv))

    for _, row in stream.rows:
        ob = ObRow(row)

        # Access ID directly (we can trust it's populated during ObRow __init__)
        try:
            ob_id = ob.ID
        except AttributeError:
            continue

        # Target TOE ID 10
        if ob_id == 10:
            sqd_base = ObColumn.SQD_0

            # Find which slot WID 500 is in using pure integer math
            for i in range(32):
                try:
                    wid = int(ob.raw[sqd_base + i])
                except (IndexError, ValueError):
                    continue

                if wid == 500:
                    ob.reorder_slots(source_slot=i, target_slot=0)
                    processed_ob = ob
                    break

    # 3. Assertions: Verify the ObRow updated correctly
    assert processed_ob is not None, "Target OB was not found or processed in the CSV"

    # 500 should now be in slot 0
    assert processed_ob.SQD_0 == 500
    assert processed_ob.SQD_NUM_0 == 10

    # Because 500 was moved to slot 0, the old WID 100 shifts down to slot 1
    assert processed_ob.SQD_1 == 100
    assert processed_ob.SQD_NUM_1 == 10
