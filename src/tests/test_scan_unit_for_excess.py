"""Unit tests for the Unit Excess Scanner wrappers."""
from unittest.mock import patch
from wite2_tools.scanning.scan_unit_for_excess import (
    scan_units_for_excess_ammo,
    scan_units_for_excess_supplies,
    scan_units_for_excess_fuel,
    scan_units_for_excess_vehicles
)
from wite2_tools.models import UnitColumn
from wite2_tools.constants import EXCESS_RESOURCE_MULTIPLIER

# Target the internal helper function to isolate the wrapper logic
PATCH_TARGET = "wite2_tools.scanning.scan_unit_for_excess._scan_excess_resource"

class TestScanUnitExcessWrappers:

    @patch(PATCH_TARGET)
    def test_scan_units_for_excess_ammo(self, mock_scan) -> None:
        """Verifies the ammo wrapper routes the correct schema indices."""
        mock_scan.return_value = 2
        result = scan_units_for_excess_ammo("dummy.csv")

        assert result == 2
        mock_scan.assert_called_once_with(
            "dummy.csv",
            UnitColumn.AMMO,
            UnitColumn.A_NEED,
            'Ammo',
            EXCESS_RESOURCE_MULTIPLIER
        )

    @patch(PATCH_TARGET)
    def test_scan_units_for_excess_supplies(self, mock_scan) -> None:
        """Verifies the supplies wrapper handles custom ratios."""
        scan_units_for_excess_supplies("dummy.csv", ratio=3.0)

        mock_scan.assert_called_once_with(
            "dummy.csv",
            UnitColumn.SUP,
            UnitColumn.S_NEED,
            'Supplies',
            3.0
        )

    @patch(PATCH_TARGET)
    def test_scan_units_for_excess_fuel(self, mock_scan) -> None:
        """Verifies the fuel wrapper routes the correct schema indices."""
        scan_units_for_excess_fuel("dummy.csv")
        mock_scan.assert_called_once_with(
            "dummy.csv",
            UnitColumn.FUEL,
            UnitColumn.F_NEED,
            'Fuel',
            EXCESS_RESOURCE_MULTIPLIER
        )

    @patch(PATCH_TARGET)
    def test_scan_units_for_excess_vehicles(self, mock_scan) -> None:
        """Verifies the vehicles wrapper routes the correct schema indices."""
        scan_units_for_excess_vehicles("dummy.csv")
        mock_scan.assert_called_once_with(
            "dummy.csv",
            UnitColumn.TRUCK,
            UnitColumn.V_NEED,
            'Vehicles',
            EXCESS_RESOURCE_MULTIPLIER
        )