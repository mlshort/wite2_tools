import csv
from pathlib import Path

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.modifiers import (
    remove_ground_weapon_gaps,
)
from wite2_tools.models import GndColumn



def test_remove_ground_weapon_gaps(mock_ground_csv: Path) -> None:
    """Verifies that gaps are removed and weapons are shifted left/up."""

    # Execute the modifier
    results = remove_ground_weapon_gaps(str(mock_ground_csv))

    assert results == (16, 4)

    # Verify the contents were actually shifted
    with open(mock_ground_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.reader(f))

       # Row 4 is Ground Element 1001 (Gap Target A)
        assert rows[4][GndColumn.WPN_0] == "100"
        assert rows[4][GndColumn.WPN_1] == "200"
        assert rows[4][GndColumn.WPN_2] == "0"
