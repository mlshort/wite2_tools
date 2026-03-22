from pathlib import Path

from wite2_tools.core.find_orphaned_obs import find_orphaned_obs
from wite2_tools.generator import CSVListStream

# 1. Standardized Mock Data for TOE(OB) templates
MOCK_OB_DATA: list[list[str]] = [
    ["id", "name", "suffix", "type", "nat", "upgrade"],
    [ "1",  "Inf Div",  "41",  "1",  "1",  "2"],
    [ "2",  "Inf Div",  "42",  "1",  "1",  "3"],
    [ "3",  "Inf Div",  "43",  "1",  "1",  "0"],
    [ "4",  "Pz Div",  "41",  "1",  "1",  "0"],
    [ "5",  "Sec Div",  "41",  "1",  "1",  "6"],
    [ "6",  "Sec Div",  "42",  "1",  "1",  "0"],
]

# 2. Aligned Mock Unit Data
MOCK_UNIT_DATA: list[list[str]] = [
    [ "id",  "name",  "nat",  "type"],
    [ "1",  "1st Div",  "1",  "1"],    # Valid Ref to OB 1
    [ "2",  "2nd Div",  "1",  "999"],  # INVALID Ref (Orphan)
    [ "3",  "3rd Div",  "2",  "2"]    # Filtered by Nationality
]

def create_mock_stream(data_list: list[list[str]]) -> CSVListStream:
    """
    Helper to simulate the CSVStream object returned by get_csv_list_stream.
    """
    mock_rows = enumerate(data_list[1:], start=1) # Skip header row for iteration
   # fieldnames = list(data_list[0].keys()) if data_list else []
    fieldnames = data_list[0]
    return CSVListStream(header=fieldnames, rows=mock_rows)


def test_find_orphaned_obs_logic(mock_ob_csv: Path, mock_unit_csv: Path) -> None:
    # Use the real files instead of mocking the stream!
    orphans = find_orphaned_obs(str(mock_ob_csv), str(mock_unit_csv), nat_codes={1})
    assert len(orphans) == 5
