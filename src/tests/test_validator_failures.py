from unittest.mock import patch

from wite2_tools.auditing.validator import evaluate_unit_consistency
from wite2_tools.auditing.validator import evaluate_ob_consistency


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

    with patch('wite2_tools.auditing.validator.get_valid_ground_elem_ids',
               return_value={1}):
        issues = evaluate_unit_consistency(str(unit_csv), str(ground_csv))
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
    with patch('wite2_tools.auditing.validator.get_valid_ground_elem_ids',
               return_value={1}):
        issues = evaluate_unit_consistency(str(unit_csv), str(ground_csv))
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

    issues = evaluate_unit_consistency(str(unit_csv), str(ground_csv))
    assert issues > 0


def test_validator_handles_value_error(tmp_path):
    """
    Targets the general exception block at the end of
    evaluate_unit_consistency.
    """
    unit_csv = tmp_path / "corrupt.csv"
    # Malformed data to trigger a parsing error
    unit_csv.write_text("id,name\nNOT_AN_INT,Broken")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # it is handled without throwing the exception
    issues = evaluate_unit_consistency(str(unit_csv), str(ground_csv))
    assert issues == 0


def test_validator_handles_critical_io_error(tmp_path):
    """
    Targets the general exception block by providing a non-existent path
    after the initial check, or a file with completely invalid headers.
    """
    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # Providing a directory path where a file is expected usually
    # triggers an OSError/IOError in the CSV reader.
    issues = evaluate_unit_consistency(str(tmp_path), str(ground_csv))

    assert issues == -1


def test_validator_handles_key_error(tmp_path):
    """
    Targets the KeyError branch by providing a CSV that is missing
    required columns like 'id' or 'type'.
    """
    unit_csv = tmp_path / "missing_columns.csv"
    # This CSV has headers, but not the 'id' or 'type' headers the
    # validator logic expects.
    unit_csv.write_text("wrong_header1,wrong_header2\nval1,val2")

    ground_csv = tmp_path / "_ground.csv"
    ground_csv.write_text("id,name\n1,Ground")

    # When the code tries row.get("id"), it is correctly handled
    # and treated as an 'id' of 0
    issues = evaluate_ob_consistency(str(unit_csv), str(ground_csv))

    assert issues == 0
