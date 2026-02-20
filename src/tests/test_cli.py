import sys
import argparse
from unittest.mock import patch

import pytest
# Internal package imports
from wite2_tools.cli import str2bool, main

# ==========================================
# 1. str2bool Helper Tests
# ==========================================

def test_str2bool_true_values():
    """Verifies that truthy strings are correctly parsed to True."""
    assert str2bool(True) is True
    assert str2bool('yes') is True
    assert str2bool('true') is True
    assert str2bool('T') is True
    assert str2bool('y') is True
    assert str2bool('1') is True

def test_str2bool_false_values():
    """Verifies that falsy strings are correctly parsed to False."""
    assert str2bool(False) is False
    assert str2bool('no') is False
    assert str2bool('false') is False
    assert str2bool('F') is False
    assert str2bool('n') is False
    assert str2bool('0') is False

def test_str2bool_invalid_values():
    """Verifies that invalid strings raise an ArgumentTypeError."""
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool('maybe')
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool('100')


# ==========================================
# 2. CLI Routing & Parsing Tests
# ==========================================

@patch('wite2_tools.cli.sys.exit')
@patch('wite2_tools.cli.argparse.ArgumentParser.print_help')
def test_main_no_arguments(mock_print_help, mock_exit):
    """Verifies that running the CLI without arguments prints help and exits."""
    test_args = ['cli.py']
    with patch.object(sys, 'argv', test_args):
        main()
        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(1)

@patch('wite2_tools.cli.replace_unit_ground_element')
def test_main_replace_elem(mock_replace):
    """Verifies the 'replace-elem' command routes correctly with arguments."""
    test_args = ['cli.py', 'replace-elem', '105', '999', '--unit-file', 'test_unit.csv']
    with patch.object(sys, 'argv', test_args):
        main()
        mock_replace.assert_called_once_with('test_unit.csv', 105, 999)

@patch('wite2_tools.cli.update_unit_num_squads')
def test_main_update_num(mock_update):
    """Verifies the 'update-num' command parses all positional integers correctly."""
    test_args = ['cli.py', 'update-num', '50', '105', '10', '12', '--unit-file', 'test_unit.csv']
    with patch.object(sys, 'argv', test_args):
        main()
        mock_update.assert_called_once_with('test_unit.csv', 50, 105, 10, 12)

@patch('wite2_tools.cli.evaluate_unit_consistency')
def test_main_audit_unit(mock_evaluate_unit):
    """Verifies the 'audit-unit' command correctly parses boolean flags and paths."""
    mock_evaluate_unit.return_value = 0 # Mock the return value used in the print statement
    test_args = [
        'cli.py', 'audit-unit',
        '--unit-file', 'u.csv',
        '--ground-file', 'g.csv',
        'true', 'false' # active_only=True, fix_ghosts=False
    ]
    with patch.object(sys, 'argv', test_args):
        main()
        mock_evaluate_unit.assert_called_once_with('u.csv', 'g.csv', True, False)

@patch('wite2_tools.cli.scan_units_for_excess_fuel')
def test_main_scan_excess_fuel(mock_scan_fuel):
    """Verifies the 'scan-excess' command properly routes based on the --operation choice."""
    test_args = ['cli.py', 'scan-excess', '--operation', 'fuel', '--unit-file', 'u.csv']
    with patch.object(sys, 'argv', test_args):
        main()
        mock_scan_fuel.assert_called_once_with('u.csv')

@patch('wite2_tools.cli.detect_encoding')
def test_main_detect_encoding(mock_detect):
    """Verifies the 'detect-encoding' utility routes correctly."""
    mock_detect.return_value = "UTF-8"
    test_args = ['cli.py', 'detect-encoding', 'my_mod.csv']
    with patch.object(sys, 'argv', test_args):
        main()
        mock_detect.assert_called_once_with('my_mod.csv')

# ==========================================
# 3. CLI Error Handling Tests
# ==========================================

@patch('wite2_tools.cli.sys.exit')
@patch('wite2_tools.cli.audit_ground_element_csv')
def test_main_handles_exceptions_gracefully(mock_audit, mock_exit, capsys):
    """
    Verifies that if a routed function raises a predictable error (like FileNotFoundError),
    the CLI catches it, prints to stderr, and exits cleanly instead of throwing a stack trace.
    """
    # Force the mock to raise a FileNotFoundError when called
    mock_audit.side_effect = FileNotFoundError("Mocked missing file")

    test_args = ['cli.py', 'audit-ground', '--ground-file', 'missing.csv']
    with patch.object(sys, 'argv', test_args):
        main()

        # Verify it attempted to exit with error code 1
        mock_exit.assert_called_once_with(1)

        # Verify the error was printed to stderr
        captured = capsys.readouterr()
        assert "Error: Mocked missing file" in captured.err
