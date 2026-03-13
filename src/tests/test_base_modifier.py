from typing import List

# Correct import from models as requested
from wite2_tools.models import (
    gen_default_unit_row,
    ATTRS_PER_SQD,
    U_SQD0_COL
)
from wite2_tools.modifiers.reorder_unit_squads import (
    reorder_unit_elems,
    reorder_unit_squads
)


def test_reorder_unit_elems_logic() -> None:
    """Verifies interleaved unit attribute blocks shift in sync."""

    # 1. Setup
    row: List[str] = gen_default_unit_row()

    # 2. Place Data in Slot 1
    # Slot 1 base = 124 + (1 * 8) = 132
    s1_base = U_SQD0_COL + (1 * ATTRS_PER_SQD)

    row[s1_base + 0] = "99"  # SQD_U1
    row[s1_base + 1] = "10"  # SQD_NUM1

    # 3. Action
    updated: List[str] = reorder_unit_elems(row, source_slot=1, target_slot=0)

    # 4. Assertions for Target (Slot 0)
    s0_base = U_SQD0_COL + (0 * ATTRS_PER_SQD)

    assert updated[s0_base + 0] == "99", f"WID 99 should be at index {s0_base}"
    assert updated[s0_base + 1] == "10", f"Qty 10 should be at index {s0_base + 1}"

    # 6. Assertions for Cleanup (Slot 1)
    assert updated[s1_base + 0] == "0", "Source WID should be reset"
    assert updated[s1_base + 1] == "0", "Source Qty should be reset"


def test_reorder_unit_squads_integration(mock_unit_csv: str) -> None:
    """Tests the full file-write process using list-based stream logic."""
    # This integration test now relies on the underlying modifier
    # using get_csv_list_stream internally.
    updates: int = reorder_unit_squads(
        mock_unit_csv,
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == 1


def test_reorder_unit_squads_integration_missing_file() -> None:
    """Verifies error handling for non-existent files."""
    updates: int = reorder_unit_squads(
        "does_not_exist.csv",
        target_uid=100,
        target_wid=42,
        target_slot=0
    )
    assert updates == -1
