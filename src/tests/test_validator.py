import csv

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.validator import evaluate_unit_consistency

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    content = "id,name,other,type\n105,Panzer IV,x,1\n"
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

@pytest.fixture(name="mock_corrupted_unit_csv")
def mock_corrupted_unit_csv(tmp_path) -> str:
    """Creates a unit file with multiple deliberate errors for the validator to catch."""
    content = (
        "id,name,type,x,y,delay,hhq,hq,sqd.u0,sqd.num0,ax,ay,tx,ty,ptx,pty\n"
        "1,Valid Unit,10,50,50,0,32,0,105,10,38,17,40,14,19,78\n"         # 1 Error: Invalid HQ ID
        "1,Duplicate,10,50,50,0,89,0,105,10,38,17,40,114,129,71\n"        # 2 Errors:Duplicate ID '1', Invalid HQ ID
        "3,Bad Coords,10,999,50,251,0,0,105,10,38,17,40,14,19,73\n"       # 2 Errors: X=999 is off map, Excess Delay
        "4,Bad Elem,10,50,50,0,82,0,999,10,38,17,40,134,119,78\n"         # 2 Errors: Elem 999 doesn't exist, Invalid HQ ID
        "5,Ghost Sqd,10,50,50,0,0,59,0,50,38,17,40,114,19,28\n"           # 1 Error: Qty 50, but ID is 0
    )
    file_path = tmp_path / "mock_corrupted_unit.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================

def test_evaluate_unit_consistency_detects_all_errors(mock_corrupted_unit_csv, mock_ground_csv):
    """Verifies the validator successfully spots duplicates, bad bounds, missing references, and ghosts."""

    issues_found = evaluate_unit_consistency(
        mock_corrupted_unit_csv,
        mock_ground_csv,
        active_only=True,
        fix_ghosts=False
    )

    # We deliberately injected exactly 8 errors into the mock CSV
    assert issues_found == 8


def test_evaluate_unit_consistency_fixes_ghosts(mock_corrupted_unit_csv, mock_ground_csv):
    """Verifies that fix_ghosts=True successfully mutates the file and zeroes out corrupted quantities."""

    # Run in FIX mode
    evaluate_unit_consistency(
        mock_corrupted_unit_csv,
        mock_ground_csv,
        active_only=True,
        fix_ghosts=True
    )

    # Read the file back to verify Ghost Squad (Unit 5) was fixed
    with open(mock_corrupted_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.DictReader(f))

        # Unit 5 is index 4. The quantity (sqd.num0) should have been forcibly set to "0"
        ghost_unit = rows[4]
        assert ghost_unit["id"] == "5"
        assert ghost_unit["sqd.u0"] == "0"
        assert ghost_unit["sqd.num0"] == "0"  # This was previously "50"

        # Ensure Valid Unit (Index 0) was NOT touched
        valid_unit = rows[0]
        assert valid_unit["sqd.num0"] == "10"

# reset
