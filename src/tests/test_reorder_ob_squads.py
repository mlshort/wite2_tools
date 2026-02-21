
# Internal package imports
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.reorder_ob_squads import (
    reorder_ob_elems,
    reorder_ob_squads
)


def test_reorder_ob_elems_logic():
    """Verifies TOE(OB) space-notation headers shift correctly."""
    row = {}
    for i in range(MAX_SQUAD_SLOTS):
        row[f"sqd {i}"] = "0"
        row[f"sqdNum {i}"] = "0"

    row["sqd 2"] = "500"

    # Shift element from slot 2 to slot 0
    updated = reorder_ob_elems(row, "sqd ", "sqdNum ", 2, 0)

    assert updated["sqd 0"] == "500"
    assert updated["sqd 2"] == "0"


def test_reorder_ob_squads_integration(mock_ob_csv):
    """Tests the full file-write process with real space-notation headers."""
    # Target ID 500 is at slot 2 in the conftest fixture
    updates = reorder_ob_squads(mock_ob_csv,
                                target_ob_id=10,
                                target_wid=500,
                                target_slot=0)
    assert updates == 1
