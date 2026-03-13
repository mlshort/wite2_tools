import csv
from unittest.mock import patch
from pathlib import Path

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.audit_unit import audit_unit_csv

# ==========================================
# FIXTURES (Setup)
# ==========================================



# ==========================================
# TEST CASES
# ==========================================


def test_coordinate_bounds_validation(tmp_path:Path)->None:
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


def test_referential_integrity_failure(tmp_path:Path)->None:
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


def test_ghost_squad_detection(tmp_path:Path)->None:
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


def test_audit_unit_handles_value_error(tmp_path: Path)-> None:
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


def test_audit_unit_handles_critical_io_error(tmp_path: Path)->None:
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

def test_audit_unit_csv_detects_all_errors(tmp_path: Path,
                                           mock_ground_csv: Path)->None:
    """
    Verifies audit_unit spots duplicates, bad bounds, missing references, and ghosts.
    """
    # 1. ARRANGE: Create the poisoned file locally using raw string for specific audit headers
    content = (
        "id,name,type,x,y,delay,hhq,hq,sqd.u0,sqd.num0,ax,ay,tx,ty,"
        "ptx,pty,awx,awy\n"
        "1,Valid Unit,10,50,50,0,32,0,105,10,38,17,40,14,19,78,32,55\n" # Valid
        "1,Duplicate,10,50,50,0,89,0,105,10,38,17,40,114,129,71,71,2\n" # Duplicate ID
        "3,Bad Coords,10,999,50,251,0,0,105,10,38,17,40,14,19,73,84,25\n" # X=999
        "4,Bad Elem,10,50,50,0,82,0,999,10,38,17,40,134,119,78,26,90\n" # WID 999
        "5,Ghost Sqd,10,50,50,0,0,59,0,50,38,17,40,114,19,28,91,100\n" # Qty 50, ID 0
    )
    poisoned_file = tmp_path / "corrupted_unit.csv"
    poisoned_file.write_text(content, encoding=ENCODING_TYPE)

    # 2. ACT: Note that we pass Path objects directly now
    issues_found = audit_unit_csv(
        str(poisoned_file),
        str(mock_ground_csv),
        active_only=True,
        fix_ghosts=False
    )

    # 3. ASSERT
    assert issues_found == 8

def test_audit_unit_csv_fixes_ghosts(mock_corrupted_unit_csv: Path,
                                     mock_ground_csv: Path) -> None:
    """
    Verifies that fix_ghosts=True successfully mutates the file and zeroes
    out corrupted quantities.
    """

    # Run in FIX mode
    audit_unit_csv(
        str(mock_corrupted_unit_csv),
        str(mock_ground_csv),
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
