import pytest
from unittest.mock import patch, MagicMock
from wite2_tools.core.find_orphaned_obs import find_orphaned_obs

# Added header row as first element to satisfy next(gen)
OB_CSV_DATA = [
    {"id": "id", "name": "name", "suffix": "suffix", "type": "type", "nat": "nat", "upgrade": "upgrade"},
    {"id": "1", "name": "Inf Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "2"},
    {"id": "2", "name": "Inf Div", "suffix": "42", "type": "1", "nat": "1", "upgrade": "3"},
    {"id": "3", "name": "Inf Div", "suffix": "43", "type": "1", "nat": "1", "upgrade": "0"},
    {"id": "4", "name": "Pz Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "0"},
    {"id": "5", "name": "Sec Div", "suffix": "41", "type": "1", "nat": "1", "upgrade": "6"},
    {"id": "6", "name": "Sec Div", "suffix": "42", "type": "1", "nat": "1", "upgrade": "0"},
]

UNIT_CSV_DATA = [
    {"id": "id", "name": "name", "type": "type", "nat": "nat"},
    {"id": "101", "name": "1st Infantry", "type": "1", "nat": "1"},
    {"id": "102", "name": "99th Ghost", "type": "99", "nat": "1"},
]

@patch("wite2_tools.core.find_orphaned_obs.get_ob_suffix", return_value="")
@patch("wite2_tools.core.find_orphaned_obs.read_csv_dict_generator")
@patch("os.path.exists", return_value=True)
def test_upgrade_chain_tracing(mock_exists, mock_gen, mock_suffix):
    """Verifies that units protect their entire upgrade path."""
    mock_gen.side_effect = [
        ((None, row) for row in OB_CSV_DATA),
        ((None, row) for row in UNIT_CSV_DATA)
    ]

    orphans = find_orphaned_obs("_ob.csv", "_unit.csv", nat_codes=1)

    # Now ID 1 is processed, so it should protect 2 and 3
    assert 1 not in orphans
    assert 2 not in orphans
    assert 3 not in orphans
    assert 4 in orphans
    assert 5 in orphans
    assert 6 in orphans
    assert len(orphans) == 3