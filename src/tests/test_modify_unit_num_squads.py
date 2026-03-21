import csv
from pathlib import Path


# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.modifiers import modify_unit_squads
from wite2_tools.models import U_SQD_NUM0_COL


def test_modify_unit_squads_success_and_filters(mock_unit_csv: Path) -> None:
    """
    Verifies that the strict multi-level conditions are applied correctly.
    """

    # Execute: In TOE(OB) 50, if Elem 105 has qty 10, change it to 99
    results = modify_unit_squads(
        str(mock_unit_csv),
        target_ob_id=50,
        target_wid=105,
        old_num_squads=10,
        new_num_squads=99
    )

    # Assert ONLY Row 1 was updated by the script
    assert results == (26, 1)

    with open(mock_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.reader(f))

        # Use your known index from unit_schema
        target_qty_idx = U_SQD_NUM0_COL + (2 * 8)

        # Find the unit by ID (Index 0 is ALWAYS the ID column).
        # We slice rows[1:] to skip the header row, avoiding any BOM weirdness.
        updated_unit = next(r for r in rows[1:] if r[0] == "102")

        assert updated_unit[target_qty_idx] == "99", "Quantity should be updated to 99"
