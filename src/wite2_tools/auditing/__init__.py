"""
Data Auditing and Integrity Package
===================================
Contains validation logic to ensure Gary Grigsby's War in the East 2 (WiTE2)
CSV files are structurally sound and logically consistent.

Key Capabilities:
-----------------
* CSV Structure Validation: Ensures required column counts and header formats.
* Logical Integrity: Detects "Ghost Squads" (WID 0 with quantity > 0) and orphans.
* Stat Boundary Checks: Validates ground element properties (men, size, types).
* Batch Processing: Automated scanning of multiple target files.
"""

__version__ = "0.5.0"
__date__ = "2026-03-02"

from .audit_unit import audit_unit_csv
from .audit_ob import audit_ob_csv
from .audit_ground_element import audit_ground_element_csv
from .audit_unit_ob_excess import audit_unit_ob_excess
from .batch_evaluator import (
    scan_and_evaluate_unit_files,
    scan_and_evaluate_ob_files,
)
from .support_analysis import print_undersupported_units

__all__ = [
    "audit_ob_csv",
    "audit_unit_csv",
    "audit_ground_element_csv",
    "audit_unit_ob_excess",
    "scan_and_evaluate_unit_files",
    "scan_and_evaluate_ob_files",
    "print_undersupported_units"
]
