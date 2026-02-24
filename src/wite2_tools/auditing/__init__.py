"""
Verification and validation tools for CSV data integrity.

This sub-package contains validators designed to catch structural
errors, duplicate IDs, and logical inconsistencies within and between
the _ob, _unit, and _ground CSV files.
"""

__version__ = "0.3.1"
__date__ = "2026-02-22"

from .audit_unit import audit_unit_csv
from .audit_ob import audit_ob_csv
from .audit_ground_element import audit_ground_element_csv
from .batch_evaluator import (
    scan_and_evaluate_unit_files,
    scan_and_evaluate_ob_files,
)

__all__ = [
    "audit_ob_csv",
    "audit_unit_csv",
    "audit_ground_element_csv",
    "scan_and_evaluate_unit_files",
    "scan_and_evaluate_ob_files"
]
