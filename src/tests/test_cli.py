import pytest
from unittest.mock import MagicMock, patch
import wite2_tools.cli as cli
from wite2_tools.cli import setup_parsers, COMMAND_MAP

@pytest.fixture
def mock_paths()->dict[str,str]:
    """Provides consistent dummy paths for testing."""
    return {
        "unit": "data/unit.csv",
        "ob": "data/ob.csv",
        "ground": "data/ground.csv",
        "aircraft": "data/aircraft.csv",
        "device" : "data/device.csv"
    }

@pytest.fixture
def mock_args()->MagicMock:
    """Simulates the argparse Namespace with all possible CLI arguments."""
    args = MagicMock()
    args.nat_codes = [1]
    args.active_only = True
    args.set_path = "/new/path"
    args.set_scenario = "1941"
    args.csv_out = "out.csv"
    args.txt_out = "out.txt"
    args.target_uid = 100
    args.target_wid = 50
    args.target_slot = 2
    args.old_wid = 50
    args.new_wid = 60
    args.target_ob_id = 500
    args.old_num_s = 5
    args.new_num_s = 10
    args.device_type = 17
    return args

## --- Configuration & Audit Tests ---

@patch("wite2_tools.cli.save_config")
def test_command_config(mock_func, mock_args)->None:
    """Verifies config saves paths and scenario settings."""
    with patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["config"](mock_args, {})
    mock_func.assert_called_once_with(mock_args.set_path, mock_args.set_scenario)

@patch("wite2_tools.cli.audit_unit_ob_excess")
def test_command_audit_toe(mock_func, mock_args, mock_paths):
    """Verifies TOE audit receives unit/ob paths and nat set."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["audit-toe"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["unit"], mock_paths["ob"], {1})

@patch("wite2_tools.cli.identify_unused_devices")
def test_command_audit_devices(mock_func, mock_args, mock_paths):
    """Verifies device audit cross-references all three main files."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["scan-unused"](mock_args, mock_paths)
    mock_func.assert_called_once_with(
        mock_paths["ground"],
        mock_paths["aircraft"],
        mock_paths["device"],
        mock_args.device_type
    )

## --- Generation & Analysis Tests ---

@patch("wite2_tools.cli.find_orphaned_obs")
def test_command_gen_orphans(mock_func, mock_args, mock_paths):
    """Verifies orphaned OB search uses correct paths."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["gen-orphans"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["ob"], mock_paths["unit"], [1])

@patch("wite2_tools.cli.group_units_by_ob")
def test_command_gen_groups(mock_func, mock_args, mock_paths):
    """Verifies unit grouping handles the active_only flag."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["gen-groups"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["unit"], True, [1])

@patch("wite2_tools.cli.generate_ob_chains")
def test_command_gen_chains(mock_func, mock_args, mock_paths):
    """Verifies OB chain generation handles dual output paths."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["gen-chains"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["ob"], "out.csv", "out.txt", [1])

@patch("wite2_tools.cli.handle_scan_excess")
def test_command_scan_excess(mock_func, mock_args, mock_paths):
    """Verifies excess scanning receives full paths and args context."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["scan-excess"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths, mock_args)

## --- Modification Tests ---

@patch("wite2_tools.cli.reorder_unit_squads")
def test_command_mod_reorder(mock_func, mock_args, mock_paths):
    """Verifies squad reordering passes target indices."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["mod-reorder-unit"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["unit"], 100, 50, 2)

@patch("wite2_tools.cli.modify_unit_ground_element")
def test_command_mod_replace(mock_func, mock_args, mock_paths):
    """Verifies element replacement maps old and new weapon IDs."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["mod-replace-elem"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["unit"], 50, 60)

@patch("wite2_tools.cli.modify_unit_squads")
def test_command_mod_update_num(mock_func, mock_args, mock_paths):
    """Verifies squad count updates target the correct OB ID."""
    with patch("wite2_tools.cli.paths", mock_paths), patch("wite2_tools.cli.args", mock_args):
        cli.COMMAND_MAP["mod-update-num"](mock_args, mock_paths)
    mock_func.assert_called_once_with(mock_paths["unit"], 500, 50, 5, 10)