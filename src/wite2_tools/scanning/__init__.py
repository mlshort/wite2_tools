"""
Search and query utilities for WiTE2 databases.

Provides optimized scanning functions to locate specific ground
elements, units, or equipment concentrations within the scenario data
without modifying the source files.
"""

__version__ = "0.1.0"
__date__ = "2026-02-19"

from .scan_ob_for_ground_elem import scan_ob_for_ground_elem
from .scan_unit_for_ground_elem import scan_unit_for_ground_elem
from .scan_unit_for_excess import (
    scan_units_for_excess_ammo,
    scan_units_for_excess_fuel,
    scan_units_for_excess_supplies,
    scan_units_for_excess_vehicles
)
__all__ = [
    "scan_ob_for_ground_elem",
    "scan_unit_for_ground_elem",
    "scan_units_for_excess_ammo",
    "scan_units_for_excess_fuel",
    "scan_units_for_excess_supplies",
    "scan_units_for_excess_vehicles"
]