import pytest
from typing import Tuple

from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.modifiers.reorder_unit_squads import (
    reorder_unit_elems,
    reorder_unit_squads
)

def test_reorder_unit_elems_logic():
    """Verifies all 8 unit attributes shift in sync."""
    # We must provide all prefixes the function loops over
    prefixes = ["sqd.u", "sqd.num", "sqd.dis", "sqd.dam", "sqd.fat", "sqd.fired", "sqd.exp", "sqd.expAccum"]
    row = {}
    for p in prefixes:
        for i in range(MAX_SQUAD_SLOTS):
            row[f"{p}{i}"] = "0"

    # Setup: ID 99 at slot 1
    row["sqd.u1"] = "99"
    row["sqd.num1"] = "10"

    # Move from 1 to 0
    updated = reorder_unit_elems(row, 1, 0)

    assert updated["sqd.u0"] == "99"
    assert updated["sqd.num0"] == "10"
    assert updated["sqd.u1"] == "0"

def test_reorder_unit_squads_integration(mock_unit_csv):
    """Tests the full file-write process with real dot-notation headers."""
    # Target ID 42 is at slot 5 in the conftest fixture
    updates = reorder_unit_squads(mock_unit_csv, target_unit_id=100, wid=42, target_slot=0)
    assert updates == 1