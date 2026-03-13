import csv
from pathlib import Path
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.modifiers import (
    modify_unit_ground_element,
)
from wite2_tools.models import UnitColumn


def test_modify_unit_ground_element_success(mock_unit_csv: Path) -> None:
    """
    Verifies that the target Ground Element is replaced globally across
    all valid slots.
    """

    # Execute: Globally replace all instances of Ground Element 105 with 999
    updates = modify_unit_ground_element(
        unit_file_path=str(mock_unit_csv),
        old_wid=105,
        new_wid=999
    )

    assert updates == 7

    with open(mock_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.reader(f))

        # Find unit 102 (skip the header row)
        updated_unit = next(r for r in rows[1:] if r[0] == "102")

        # Use your known index from unit_schema
        assert "999" in updated_unit
        assert "105" not in updated_unit

