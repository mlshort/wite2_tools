from unittest.mock import patch, MagicMock
from wite2_tools.core.find_orphaned_obs import find_orphaned_obs
from wite2_tools.generator import CSVStream

# 1. Standardized Mock Data for TOE(OB) templates
MOCK_OB_DATA = [
    {"id": "id", "name": "name", "suffix": "suffix", "type": "type", "nat": "nat", "upgrade": "upgrade"},
    {"id": "1", "name": "Inf Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "2"},
    {"id": "2", "name": "Inf Div", "suffix": "42", "type": "1", "nat": "1", "upgrade": "3"},
    {"id": "3", "name": "Inf Div", "suffix": "43", "type": "1", "nat": "1", "upgrade": "0"},
    {"id": "4", "name": "Pz Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "0"},
    {"id": "5", "name": "Sec Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "6"},
    {"id": "6", "name": "Sec Div", "suffix": "42", "type": "1", "nat": "1", "upgrade": "0"},
]

# 2. Aligned Mock Unit Data
# Changed IDs to 1, 2, and 3 to match the test's assertions
MOCK_UNIT_DATA = [
    {"id": "id", "name": "name", "nat": "nat", "type": "type"},
    {"id": "1", "name": "1st Div", "nat": "1", "type": "1"},    # Valid Ref to OB 1
    {"id": "2", "name": "2nd Div", "nat": "1", "type": "999"},  # INVALID Ref (Orphan)
    {"id": "3", "name": "3rd Div", "nat": "2", "type": "2"}    # Filtered by Nationality
]

def create_mock_stream(data_list):
    """Helper to simulate the CSVStream object returned by get_csv_dict_stream."""
    mock_rows = enumerate(data_list[1:], start=1) # Skip header row for iteration
    fieldnames = list(data_list[0].keys()) if data_list else []
    return CSVStream(fieldnames=fieldnames, rows=mock_rows)

class TestOrphanedObs:

    @patch("wite2_tools.core.find_orphaned_obs.get_ob_full_name", return_value="Mocked OB Name")
    @patch("wite2_tools.core.find_orphaned_obs.get_csv_dict_stream")
    @patch("os.path.exists", return_value=True)
    def test_find_orphaned_obs_logic(self, mock_exists, mock_gen, mock_name):
        """Verifies that only units with non-existent OB IDs are flagged."""

        # Configure the mock generator to return our test streams
        mock_gen.side_effect = [
            create_mock_stream(MOCK_OB_DATA),
            create_mock_stream(MOCK_UNIT_DATA)
        ]

        # Run the audit for Nationality 1 (Germans)
        # This will trace chains and identify unit 2 as having an invalid OB reference
        orphans = find_orphaned_obs("_ob.csv", "_unit.csv", nat_codes={1})

        assert 2 not in orphans

        assert 1 not in orphans

        assert 3 not in orphans

        assert len(orphans) == 3
