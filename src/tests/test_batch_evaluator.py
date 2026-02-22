from unittest.mock import patch
from wite2_tools.auditing.batch_evaluator import scan_and_evaluate_unit_files
from wite2_tools.auditing.batch_evaluator import scan_and_evaluate_ob_files


def test_scan_and_evaluate_logic(tmp_path):
    """
    Verifies that the batch evaluator correctly identifies and
    processes CSVs in a directory.
    """
    # 1. Setup a dummy scenario directory
    scenario_dir = tmp_path / "1941_GC"
    scenario_dir.mkdir()

    # Create dummy files that the scanner will pick up
    (scenario_dir / "scen01_unit.csv").write_text("id,name,type\n1,Alpha,1")
    (scenario_dir / "scen01_ground.csv").write_text("id,name,type\n1,Panzer,1")

    # 2. Mock audit_unit_csv to isolate the batching logic
    with patch('wite2_tools.auditing.batch_evaluator.audit_unit_csv') as mock_val:
        # Mock return value (0 issues found)
        mock_val.return_value = 0

        # Execute the batch scan
        scan_and_evaluate_unit_files(
            target_folder=str(scenario_dir),
            active_only=True,
            fix_ghosts=False
        )

        # 3. Assertions
        # Verify it found the unit/ground pair and called the validator
        mock_val.assert_called_once()

        # Verify the paths passed to the validator were correct
        args, _ = mock_val.call_args
        assert "_unit.csv" in args[0]
        assert "_ground.csv" in args[1]


@patch('wite2_tools.auditing.batch_evaluator.audit_ob_csv')
def test_scan_and_evaluate_ob_logic(mock_ob_val, tmp_path):
    """Verifies the scanner correctly picks up and evaluates OB files."""
    scenario_dir = tmp_path / "OB_Test"
    scenario_dir.mkdir()

    # Create required file pairs
    (scenario_dir / "1941_ob.csv").write_text("id,name,type\n1,Panzer_TOE,1")
    (scenario_dir / "1941_ground.csv").write_text("id,name,type\n1,Panzer,1")

    # FIX: Set the return value to an integer so the >= comparison works
    mock_ob_val.return_value = 0

    scan_and_evaluate_ob_files(str(scenario_dir))

    mock_ob_val.assert_called_once()
