import csv
import pytest
from wite2_tools.auditing.validator import evaluate_unit_consistency

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture
def mock_ground_csv(tmp_path) -> str:
    content = "id,name,other,type\n105,Panzer IV,x,1\n"
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding="ISO-8859-1")
    return str(file_path)

@pytest.fixture
def mock_corrupted_unit_csv(tmp_path) -> str:
    """Creates a unit file with multiple deliberate errors for the validator to catch."""
    content = (
        "id,name,type,x,y,hhq,hq,sqd.u0,sqd.num0\n"
        "1,Valid Unit,10,50,50,0,0,105,10\n"       # 0 Errors: Perfectly valid
        "1,Duplicate,10,50,50,0,0,105,10\n"        # 1 Error: Duplicate ID '1'
        "3,Bad Coords,10,999,50,0,0,105,10\n"      # 1 Error: X=999 is off map
        "4,Bad Elem,10,50,50,0,0,999,10\n"         # 1 Error: Elem 999 doesn't exist
        "5,Ghost Sqd,10,50,50,0,0,0,50\n"          # 1 Error: Qty 50, but ID is 0
    )
    file_path = tmp_path / "mock_corrupted_unit.csv"
    file_path.write_text(content, encoding="ISO-8859-1")
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

    # We deliberately injected exactly 4 errors into the mock CSV
    assert issues_found == 4


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
    with open(mock_corrupted_unit_csv, 'r', encoding="ISO-8859-1") as f:
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