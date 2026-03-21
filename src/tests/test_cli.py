"""
Tests for the WiTE2 CLI Dispatcher
==================================
Verifies that subcommands correctly route to the intended worker functions
within the Dispatch Map and handle errors gracefully.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock, ANY

# Internal package imports
from wite2_tools.cli import main, setup_parsers


class TestCLIDispatcher(unittest.TestCase):
    """Verifies command routing and error handling in the refactored CLI."""

    def setUp(self) -> None:
        # We must patch the initialized 'log' variable inside cli.py directly,
        # NOT get_logger(), because log is instantiated at module load time.
        self.patcher_log = patch("wite2_tools.cli.log")
        self.mock_log = self.patcher_log.start()
        self.addCleanup(self.patcher_log.stop)

    @patch("wite2_tools.cli.audit_ground_element_csv")
    def test_dispatch_audit_ground(self, mock_audit: MagicMock) -> None:
        """Verifies 'audit-ground' routes correctly to the auditor."""
        test_args: list[str] = ["cli.py", "audit-ground"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_audit.assert_called_once()

    @patch("wite2_tools.cli.audit_unit_ob_excess")
    def test_dispatch_audit_toe(self, mock_audit: MagicMock) -> None:
        """Verifies that 'audit-toe' routes correctly to the auditor with nat code sets."""
        test_args: list[str] = ["cli.py", "audit-toe", "--nat", "1", "3"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_audit.assert_called_once()

        # Verify nat_codes were cast to a set: {1, 3} as per the COMMAND_MAP lambda
        args, _ = mock_audit.call_args
        target_nat = args[3]
        self.assertEqual(target_nat, {1, 3})

    @patch("wite2_tools.cli.handle_scan_excess")
    def test_dispatch_scan_excess(self, mock_handle_scan: MagicMock) -> None:
        """Verifies 'scan-excess' routes correctly using positional arguments."""
        # 'f' is fuel, '10.0' is the ratio threshold
        test_args: list[str] = ["cli.py", "scan-excess", "f", "10.0"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_handle_scan.assert_called_once()

    @patch("wite2_tools.cli.reorder_unit_squads")
    def test_dispatch_mod_reorder_unit(self, mock_reorder: MagicMock) -> None:
        """Verifies 'mod-reorder-unit' maps the positional arguments accurately."""
        test_args: list[str] = [
            "cli.py", "mod-reorder-unit",
            "100",  # target_uid
            "500",  # target_wid
            "0"     # target_slot
        ]

        with patch.object(sys, "argv", test_args):
            main()

        args, _ = mock_reorder.call_args
        # Validate the numerical arguments were correctly collected and mapped
        self.assertEqual(args[1:], (100, 500, 0))

    @patch("wite2_tools.cli.modify_unit_squads")
    def test_dispatch_mod_update_num(self, mock_modify: MagicMock) -> None:
        """Verifies 'mod-update-num' maps the flagged numerical arguments accurately."""
        test_args: list[str] = [
            "cli.py", "mod-update-num",
            "--ob-id", "50",
            "--wid", "120",
            "--old", "5",
            "--new", "10"
        ]

        with patch.object(sys, "argv", test_args):
            main()

        args, _ = mock_modify.call_args
        # expected passed args: (p["unit"], target_ob_id, target_wid, old_num_s, new_num_s)
        self.assertEqual(args[1:], (50, 120, 5, 10))

    @patch("wite2_tools.cli.sys.exit")
    @patch("wite2_tools.cli.audit_unit_ob_excess")
    def test_main_handles_exception(self, mock_audit: MagicMock, mock_exit: MagicMock) -> None:
        """Verifies global try/except catches and logs errors lazily."""
        # Force the worker function to throw a generic Exception
        mock_audit.side_effect = Exception("Data Corrupt")

        test_args: list[str] = ["cli.py", "audit-toe"]

        with patch.object(sys, "argv", test_args):
            main()

            # Verify the logger's error function was called
            self.mock_log.error.assert_called_with(
                "Critical failure in %s: %s", "audit-toe", ANY, exc_info=True
            )

        # Ensure that it initiates a clean crash via sys.exit(1)
        mock_exit.assert_called_once_with(1)

    def test_parser_nat_defaults(self) -> None:
        """Verifies that the add_common helper applies default nat codes correctly."""
        parser = setup_parsers()
        args = parser.parse_args(["audit-toe"])

        # Should default to a list containing [1]
        self.assertEqual(args.nat_codes, [1])


if __name__ == "__main__":
    unittest.main()
