import csv

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.audit_ob import audit_ob_csv
from wite2_tools.constants import MAX_SQUAD_SLOTS
import pytest


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
    """
    Creates a unit file with multiple deliberate errors for
    the audit_ob to catch.
    """
    content = (
        "id,name,type,x,y,delay,hhq,hq,sqd.u0,sqd.num0,ax,ay,tx,ty,"
        "ptx,pty,awx,awy\n"
        # 1 Error: Invalid HQ ID
        "1,Valid Unit,10,50,50,0,32,0,105,10,38,17,40,14,19,78,32,55\n"
        # 2 Errors:Duplicate ID '1', Invalid HQ ID
        "1,Duplicate,10,50,50,0,89,0,105,10,38,17,40,114,129,71,71,2\n"
        # 2 Errors: X=999 is off map, Excess Delay
        "3,Bad Coords,10,999,50,251,0,0,105,10,38,17,40,14,19,73,84,25\n"
        # 2 Errors: Elem 999 doesn't exist, Invalid HQ ID
        "4,Bad Elem,10,50,50,0,82,0,999,10,38,17,40,134,119,78,26,90\n"
        # 1 Error: Qty 50, but ID is 0
        "5,Ghost Sqd,10,50,50,0,0,59,0,50,38,17,40,114,19,28,91,100\n"
    )
    file_path = tmp_path / "mock_corrupted_unit.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)


@pytest.fixture
def mock_files(tmp_path):
    """
    A PyTest fixture that sets up mock _ground.csv and _ob.csv files
    in a temporary directory before each test, and yields their paths.
    """
    ground_path = tmp_path / "_ground.csv"
    ob_path = tmp_path / "_ob.csv"

    # Setup Mock Ground Elements (WIDs 1, 2, 3 are valid)
    with open(ground_path, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.writer(f)
        # Add enough dummy headers to reach index 3 (TYPE)
        writer.writerow(["id", "name", "id_2", "type"])
        writer.writerows([
            # id, name, id_2, type (must be > 0)
            [1, "Rifle Squad", 0, 1],
            [2, "MG Squad", 0, 1],
            [3, "81mm Mortar", 0, 2]
        ])

    return ground_path, ob_path
# ==========================================
# TEST CASES
# ==========================================


# Base headers for TOE(OB)
def write_ob_csv(ob_path, rows):
    """Helper function to quickly write TOE(OB) scenarios for tests."""
    ob_headers = [
            "id", "type", "name", "firstYear", "firstMonth",
            "lastYear", "lastMonth", "upgrade"
        ]

    for i in range(MAX_SQUAD_SLOTS):
        ob_headers.extend([f"sqd.u{i}", f"sqd.num{i}"])

    with open(ob_path, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(ob_headers)  # Header row 1

        for row_data in rows:
            # Pad the rest of the row with 0s for unused squad slots
            padded_row = list(row_data) + [0] * (len(ob_headers) -
                                                 len(row_data))
            writer.writerow(padded_row)


# --- TEST CASES ---

def test_audit_ob_handles_key_error(tmp_path):
    """
    Targets the KeyError branch by providing a CSV that is missing
    required columns like 'id' or 'type'.
    """
    unit_csv = tmp_path / "missing_columns.csv"
    # This CSV has headers, but not the 'id' or 'type' headers the
    # audit_ob logic expects.
    unit_csv.write_text("wrong_header1,wrong_header2\nval1,val2")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # When the code tries row.get("id"), it is correctly handled
    # and treated as an 'id' of 0
    issues = audit_ob_csv(str(unit_csv), str(ground_csv))

    assert issues == 0


def test_clean_ob_passes(mock_files):
    """A perfectly valid TOE(OB) should return 0 issues."""
    ground_path, ob_path = mock_files
    write_ob_csv(ob_path, [
            # id, type, name, fY, fM, lY, lM, upgrade, u0, num0, u1, num1
            [100, 1, "Valid Div", 1941, 6, 1945, 1, 0, 1, 9, 2, 3]
        ])

    issues = audit_ob_csv(str(ob_path), str(ground_path))
    assert issues == 0


def test_chronological_bounds_error(mock_files):
    """Should flag if lastYear is before firstYear."""
    ground_path, ob_path = mock_files
    write_ob_csv(ob_path, [
            # Expires in 1940, but introduced in 1941
            [101, 1, "Time Traveler Div", 1941, 6, 1940, 1, 0]
        ])

    issues = audit_ob_csv(str(ob_path), str(ground_path))
    assert issues == 1


def test_upgrade_dead_end_and_loop(mock_files):
    """Should flag upgrades to non-existent IDs and self-upgrades."""
    ground_path, ob_path = mock_files
    write_ob_csv(ob_path, [
            # Upgrades to ID 999 (doesn't exist)
            [102, 1, "Dead End Div", 1941, 6, 1942, 1, 999],
            # Upgrades into itself (infinite loop)
            [103, 1, "Loop Div", 1941, 6, 1942, 1, 103]
        ])

    issues = audit_ob_csv(str(ob_path), str(ground_path))
    assert issues == 2


def test_intra_template_duplicate_element(mock_files):
    """Should flag if the same WID is used in multiple slots."""
    ground_path, ob_path = mock_files
    write_ob_csv(ob_path, [
            # WID 1 is used in Slot 0 AND Slot 1
            [104, 1, "Dup WID Div", 1941, 6, 1945, 1, 0, 1, 9, 1, 3]
        ])

    issues = audit_ob_csv(str(ob_path), str(ground_path))
    assert issues == 1


def test_ghost_and_negative_squads(mock_files):
    """Should flag negative quantities and ghost squads."""
    ground_path, ob_path = mock_files
    write_ob_csv(ob_path, [
            # num0 is negative (-5)
            [105, 1, "Neg Div", 1941, 6, 1945, 1, 0, 1, -5],
            # num0 is 10, but u0 (WID) is 0
            [106, 1, "Ghost Div", 1941, 6, 1945, 1, 0, 0, 10]
        ])
    issues = audit_ob_csv(str(ob_path), str(ground_path))
    assert issues == 2
