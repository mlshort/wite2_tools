import os
import sys

from unittest.mock import patch

# Internal package imports
from wite2_tools.cli import (
    create_parser,
    resolve_paths,
    get_config_default,
    main
)

from wite2_tools.paths import (
    _MOD_UNIT_FILENAME,
    _MOD_GROUND_FILENAME,
    _MOD_OB_FILENAME
)


@patch("os.path.exists")
@patch("configparser.ConfigParser.read")
@patch("configparser.ConfigParser.get")
def test_get_config_default(mock_get, mock_read, mock_exists):
    """Verifies retrieval of the default path from settings.ini."""
    # Case 1: Config exists
    mock_exists.return_value = True
    mock_get.return_value = "C:/ConfigPath"
    assert get_config_default() == "C:/ConfigPath"

    # Case 2: Config missing
    mock_exists.return_value = False
    assert get_config_default() == "."


def test_parser_config_command():
    """Verifies the new 'config' subcommand parsing."""
    parser = create_parser()
    args = parser.parse_args(["config", "--set-path", "C:/MyMod"])
# ==========================================
# 1. Path Resolution Tests
# ==========================================


def test_resolve_paths():
    """Verifies that paths are correctly joined to the data directory."""
    data_dir = "C:/TestMods"
    paths = resolve_paths(data_dir)

    # Normalize both sides to ensure backslash vs forward slash doesn't
    # break tests
    assert os.path.normpath(paths["unit"]) == os.path.normpath(
        os.path.join(data_dir, _MOD_UNIT_FILENAME))
    assert os.path.normpath(paths["ob"]) == os.path.normpath(
        os.path.join(data_dir, _MOD_OB_FILENAME))


# ==========================================
# 2. CLI Parser Configuration Tests
# ==========================================

@patch('wite2_tools.cli.get_config_default')
def test_create_parser_defaults(mock_config):
    """Verifies the base parser applies defaults correctly."""
    # Force default regardless of local settings.ini
    mock_config.return_value = '.'
    parser = create_parser()
    args = parser.parse_args(['audit-ground'])

    assert args.command == 'audit-ground'
    assert args.data_dir == '.'


# ==========================================
# 3. CLI Routing Tests
# ==========================================

@patch('wite2_tools.cli.audit_ground_element_csv')
def test_main_routing_audit_ground(mock_audit):
    """Verifies 'audit-ground' routes correctly with custom data-dir."""
    test_args = ['cli.py', 'audit-ground', '-d', 'test_dir']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_audit.assert_called_once_with(os.path.join('test_dir',
                                                        _MOD_GROUND_FILENAME))


@patch('wite2_tools.cli._scan_excess_resource')
def test_main_routing_scan_excess(mock_scan):
    """Verifies 'scan-excess' maps the operation correctly."""
    test_args = ['cli.py', 'scan-excess', '--operation', 'fuel', '-d',
                 'test_dir']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_scan.assert_called_once_with(
            os.path.join('test_dir', _MOD_UNIT_FILENAME),
            'fuel', 'fNeed', 'Fuel'
        )


@patch('wite2_tools.cli.reorder_ob_squads')
def test_main_routing_mod_reorder_ob(mock_reorder):
    """Verifies 'mod-reorder-ob' correctly passes positional arguments."""
    test_args = ['cli.py', 'mod-reorder-ob', '150', '42', '5', '-d',
                 'test_dir']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_reorder.assert_called_once_with(
            os.path.join('test_dir', _MOD_OB_FILENAME), 150, 42, 5
        )


@patch('wite2_tools.cli.get_config_default')
@patch('wite2_tools.cli.group_units_by_ob')
def test_main_routing_gen_groups(mock_group, mock_config):
    """Verifies 'gen-groups' correctly handles the nat-codes flag list."""
    mock_config.return_value = '.'
    test_args = ['cli.py', 'gen-groups', '--nat-codes', '1', '3']

    with patch.object(sys, 'argv', test_args):
        main()

        # Capture the actual path used in the call to normalize it
        called_path = mock_group.call_args[0][0]
        assert os.path.normpath(called_path) == \
            os.path.normpath(_MOD_UNIT_FILENAME)
        assert mock_group.call_args[0][1] is True  # active_only
        assert mock_group.call_args[0][2] == [1, 3]  # nat_codes


# ==========================================
# 4. CLI Error Handling Tests
# ==========================================

@patch('wite2_tools.cli.sys.exit')
@patch('wite2_tools.cli.audit_ground_element_csv')
def test_main_handles_file_not_found(mock_audit, mock_exit):
    """
    Verifies that if a routed function raises a FileNotFoundError,
    the CLI catches it and exits with code 1 without a stack trace.
    """
    mock_audit.side_effect = FileNotFoundError("Mocked missing file")
    test_args = ['cli.py', 'audit-ground']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_exit.assert_called_once_with(1)


@patch('wite2_tools.cli.sys.exit')
@patch('wite2_tools.cli.audit_ground_element_csv')
def test_main_handles_data_processing_errors(mock_audit, mock_exit):
    """
    Verifies that standard data errors (ValueError, KeyError, etc.)
    are caught and exit cleanly with code 1.
    """
    mock_audit.side_effect = ValueError("Mocked bad integer")
    test_args = ['cli.py', 'audit-ground']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_exit.assert_called_once_with(1)
