import sys
import os
from unittest.mock import patch

# Internal package imports
from wite2_tools.cli import resolve_paths, create_parser, main


# ==========================================
# 1. Path Resolution Tests
# ==========================================

def test_resolve_paths():
    """Verifies that the helper correctly constructs standard file paths."""
    test_dir = "my_mod_folder"
    paths = resolve_paths(test_dir)

    assert paths["unit"] == os.path.join(test_dir, "_unit.csv")
    assert paths["ob"] == os.path.join(test_dir, "_ob.csv")
    assert paths["ground"] == os.path.join(test_dir, "_ground.csv")


# ==========================================
# 2. CLI Parser Configuration Tests
# ==========================================

def test_create_parser_defaults():
    """Verifies the base parser applies defaults correctly."""
    parser = create_parser()
    args = parser.parse_args(['audit-ground'])

    assert args.command == 'audit-ground'
    assert args.data_dir == '.'
    assert args.verbose is False


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
                                                        '_ground.csv'))


@patch('wite2_tools.cli._scan_excess_resource')
def test_main_routing_scan_excess(mock_scan):
    """Verifies 'scan-excess' maps the operation correctly."""
    test_args = ['cli.py', 'scan-excess', '--operation', 'fuel', '-d',
                 'test_dir']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_scan.assert_called_once_with(
            os.path.join('test_dir', '_unit.csv'), 'fuel', 'fNeed', 'Fuel'
        )


@patch('wite2_tools.cli.reorder_ob_squads')
def test_main_routing_mod_reorder_ob(mock_reorder):
    """Verifies 'mod-reorder-ob' correctly passes positional arguments."""
    test_args = ['cli.py', 'mod-reorder-ob', '150', '42', '5', '-d',
                 'test_dir']

    with patch.object(sys, 'argv', test_args):
        main()
        mock_reorder.assert_called_once_with(
            os.path.join('test_dir', '_ob.csv'), 150, 42, 5
        )


@patch('wite2_tools.cli.group_units_by_ob')
def test_main_routing_gen_groups(mock_group):
    """Verifies 'gen-groups' correctly handles the nat-codes flag list."""
    test_args = ['cli.py', 'gen-groups', '--nat-codes', '1', '3']

    with patch.object(sys, 'argv', test_args):
        main()
        # active_only defaults to True
        mock_group.assert_called_once_with(
            os.path.join('.', '_unit.csv'), True, [1, 3]
        )


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
