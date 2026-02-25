import csv
from unittest.mock import patch
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.audit_unit import audit_unit_csv
from wite2_tools.constants import MAX_SQUAD_SLOTS

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
    the audit_unit to catch.
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
def test_coordinate_bounds_validation(tmp_path):
    """
    Targets lines 352-360: Verifies that out-of-bounds coordinates
    are flagged as issues.
    """
    unit_csv = tmp_path / "bad_coords_unit.csv"
    # Unit with X=999 (MAX_X is ~378)
    unit_csv.write_text("id,name,type,x,y,tx,ty,ax,ay,ptx,pty\n"
                        "1,OutBounds,1,999,100,10,10,10,10,10,10")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name,type\n1,Placeholder,1")

    with patch('wite2_tools.auditing.audit_unit.get_valid_ground_elem_ids',
               return_value={1}):
        issues = audit_unit_csv(str(unit_csv), str(ground_csv))
        # Should detect 1 issue for the 'x' coordinate being 999
        assert issues > 0


def test_referential_integrity_failure(tmp_path):
    """
    Targets lines 91-172: Verifies that a squad referencing a
    non-existent WID is flagged.
    """
    unit_csv = tmp_path / "missing_wid_unit.csv"
    # Unit references WID 99 in slot 0, but WID 99 doesn't exist in ground
    unit_csv.write_text("id,name,type,x,y,tx,ty,ax,ay,ptx,pty,sqd.u0,sqd.num0\n"
                        "1,BadWID,1,10,10,10,10,10,10,10,10,99,10")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name,type\n1,ValidElem,1")

    # Mock ground IDs to only include ID 1
    with patch('wite2_tools.auditing.audit_unit.get_valid_ground_elem_ids',
               return_value={1}):
        issues = audit_unit_csv(str(unit_csv), str(ground_csv))
        assert issues > 0


def test_ghost_squad_detection(tmp_path):
    """
    Targets ghost squad logic: Quantity > 0 but WID == 0.
    """
    unit_csv = tmp_path / "ghost_unit.csv"
    # Slot 0 has 10 squads but ID is 0
    unit_csv.write_text("id,name,type,x,y,tx,ty,ax,ay,ptx,pty,sqd.u0,sqd.num0\n"
                        "1,Ghost,1,10,10,10,10,10,10,10,10,0,10")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name,type\n1,ValidElem,1")

    issues = audit_unit_csv(str(unit_csv), str(ground_csv))
    assert issues > 0


def test_audit_unit_handles_value_error(tmp_path):
    """
    Targets the general exception block at the end of
    audit_unit_csv.
    """
    unit_csv = tmp_path / "corrupt.csv"
    # Malformed data to trigger a parsing error
    unit_csv.write_text("id,name\nNOT_AN_INT,Broken")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # it is handled without throwing the exception
    issues = audit_unit_csv(str(unit_csv), str(ground_csv))
    assert issues == 0


def test_audit_unit_handles_critical_io_error(tmp_path):
    """
    Targets the general exception block by providing a non-existent path
    after the initial check, or a file with completely invalid headers.
    """
    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # Providing a directory path where a file is expected usually
    # triggers an OSError/IOError in the CSV reader.
    issues = audit_unit_csv(str(tmp_path), str(ground_csv))

    assert issues == -1


def test_audit_unit_csv_detects_all_errors(mock_corrupted_unit_csv,
                                           mock_ground_csv):
    """
    Verifies the audit_unit successfully spots duplicates,
    bad bounds, missing references, and ghosts.
    """

    issues_found = audit_unit_csv(
        mock_corrupted_unit_csv,
        mock_ground_csv,
        active_only=True,
        fix_ghosts=False
    )

    # We deliberately injected exactly 8 errors into the mock CSV
    assert issues_found == 8


def test_audit_unit_csv_fixes_ghosts(mock_corrupted_unit_csv,
                                     mock_ground_csv):
    """
    Verifies that fix_ghosts=True successfully mutates the file and zeroes
    out corrupted quantities.
    """

    # Run in FIX mode
    audit_unit_csv(
        mock_corrupted_unit_csv,
        mock_ground_csv,
        active_only=True,
        fix_ghosts=True
    )

    # Read the file back to verify Ghost Squad (Unit 5) was fixed
    with open(mock_corrupted_unit_csv, 'r', encoding=ENCODING_TYPE) as f:
        rows = list(csv.DictReader(f))

        # Unit 5 is index 4. The quantity (sqd.num0) should have been forcibly
        # set to "0"
        ghost_unit = rows[4]
        assert ghost_unit["id"] == "5"
        assert ghost_unit["sqd.u0"] == "0"
        assert ghost_unit["sqd.num0"] == "0"  # This was previously "50"

        # Ensure Valid Unit (Index 0) was NOT touched
        valid_unit = rows[0]
        assert valid_unit["sqd.num0"] == "10"
