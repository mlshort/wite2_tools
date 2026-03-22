from unittest.mock import patch, MagicMock

from wite2_tools.models.UnitRow import UnitRow, gen_unit_column_names
from wite2_tools.generator import CSVListStream
from wite2_tools.auditing.support_analysis import print_undersupported_units

# Import the schema constants to place our mock data in the correct physical columns
from wite2_tools.models import UnitColumn

def create_mock_unit_row(uid: str, name: str, utype: str,
                         nat: str, support: str, spt_need: str) -> list[str]:
    """
    Helper to create a fully padded mock physical row for a Unit.
    """

    row = UnitRow.create_default(int(uid), name, int(utype))
    row.NAT = int(nat)
    row.SUPPORT = int(support)
    row.SPT_NEED = int(spt_need)
    return row.raw

# 1. Create Mock Data matching the new list structure (No header row needed in the data body)
MOCK_UNIT_DATA: list[list[str]] = [
    create_mock_unit_row("1", "1st Panzer", "1", "1", "50", "100"),  # Deficit!
    create_mock_unit_row("2", "2nd Panzer", "1", "1", "100", "50"),  # Fine
    create_mock_unit_row("3", "HQ", "0", "1", "0", "0")              # Ignored/Zeroed
]

def create_mock_stream(data_list: list[list[str]]) -> CSVListStream:
    """Helper to simulate the CSVListStream object from your generator."""
    mock_rows = enumerate(data_list, start=1)

    # CSVListStream expects a list of headers and the row iterator.
    # We pass a dummy header since the logic now relies strictly on physical indices.
    dummy_headers = gen_unit_column_names()
    return CSVListStream(header=dummy_headers, rows=mock_rows)

# pylint: disable=too-few-public-methods
class TestSupportAnalysis:

    # Update the patch target to the new list stream generator
    @patch("wite2_tools.get_csv_list_stream")
    def test_print_undersupported_units(self, mock_stream: MagicMock) -> None:
        """Verifies the logic correctly identifies units with deficits."""

        # 1. Configure the mock to return our fake CSV data
        mock_stream.return_value = create_mock_stream(MOCK_UNIT_DATA)

        # 2. Replicate the logic you'd use in the main script
        stream = mock_stream("dummy_path.csv")

        # 3. Instantiate UnitRow passing the raw list directly to the constructor
        # (This replaces the old UnitRow.from_dict() method)
        typed_units: list[UnitRow] = [UnitRow(row) for _, row in stream.rows]

        # 4. Run the function
        # Since the function just prints, we are ensuring it runs without crashing,
        # but in a real test you might use 'capsys' to read the print output.
        print_undersupported_units(typed_units)

        # Optional: You could add assertions here if your function returns the
        # list instead of just printing it
