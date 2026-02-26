"""
Tests for the WiTE2 CLI Dispatcher
==================================
Verifies that subcommands correctly route to the intended worker functions
within the Dispatch Map and handle errors gracefully.
"""

import sys

import unittest
import unittest.mock
from unittest.mock import patch, ANY

# Internal package imports
from wite2_tools.cli import main, setup_parsers


class TestCLIDispatcher(unittest.TestCase):
    """Verifies command routing and error handling in the refactored CLI."""

    def setUp(self):
        # Common mocks to prevent actual file IO or logging side effects
        self.mock_log = patch("wite2_tools.cli.get_logger").start()
        self.addCleanup(patch.stopall)

    @patch("wite2_tools.cli.audit_unit_ob_excess")
    def test_dispatch_audit_unit_ob_excess(self, mock_audit):
        """Verifies that 'audit-toe' routes correctly to the auditor."""
        test_args = ["cli.py", "audit-toe", "--nat", "1"]

        with patch.object(sys, "argv", test_args):
            main()

        # Verify the auditor was called with expected path/nat logic
        mock_audit.assert_called_once()
        # Verify lazy logging was used (checking the call to log.info)
        self.mock_log.return_value.info.assert_any_call(
            "Executing: %s", "audit-toe"
        )

    @patch("wite2_tools.cli.find_orphaned_obs")
    def test_dispatch_gen_orphans(self, mock_orphans):
        """Verifies that 'gen-orphans' routes correctly."""
        test_args = ["cli.py", "gen-orphans", "--nat", "1", "2"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_orphans.assert_called_once()
        # Check that nat_codes were passed as a list [1, 2]
        args, kwargs = mock_orphans.call_args
        assert 1 in args[2] and 2 in args[2]

    @patch("wite2_tools.cli.modify_unit_num_squads")
    def test_dispatch_mod_update_num(self, mock_update):
        """Verifies complex argument passing for modifiers."""
        test_args = [
            "cli.py", "mod-update-num",
            "--ob-id", "500", "--wid", "10",
            "--old", "5", "--new", "10"
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Capture the actual arguments used in the call
        args, _ = mock_update.call_args
        actual_path = args[0]

        # 1. Verify the path ends with the correct scenario-based filename
        # This handles absolute vs relative path differences
        self.assertTrue(actual_path.endswith("_unit.csv"))

        # 2. Verify the numerical arguments remain exact
        # expected: (path, ob_id, wid, old, new)
        self.assertEqual(args[1:], (500, 10, 5, 10))


    @patch("wite2_tools.cli.sys.exit")
    @patch("wite2_tools.cli.audit_unit_ob_excess")
    def test_main_handles_exception(self, mock_audit, mock_exit):
        """Verifies global try/except catches and logs errors lazily."""
        # Force the mock to raise an error
        mock_audit.side_effect = Exception("Data Corrupt")

        test_args = ["cli.py", "audit-toe"]

        with patch.object(sys, "argv", test_args):
            # main() will catch the Exception and call sys.exit(1)
            main()

            # Verify the logger was called with the lazy % formatting
            self.mock_log.return_value.error.assert_called_with(
                "Critical failure in %s: %s", "audit-toe",
                ANY, exc_info=True
            )

        # This will now pass because main() stayed alive long enough to exit
        mock_exit.assert_called_once_with(1)

    def test_parser_nat_defaults(self):
        """Verifies that the add_common helper applies default nat codes."""
        parser = setup_parsers()
        args = parser.parse_args(["audit-toe"])
        assert args.nat_codes == [1]


if __name__ == "__main__":
    unittest.main()