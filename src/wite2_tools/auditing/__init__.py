"""
Verification and validation tools for CSV data integrity.

This sub-package contains validators designed to catch structural
errors, duplicate IDs, and logical inconsistencies within and between
the _ob, _unit, and _ground CSV files.
"""

__version__ = "0.1.1"
__date__ = "2026-02-19"

from .validator import evaluate_ob_consistency, evaluate_unit_consistency
from .audit_ground_element import audit_ground_element_csv
from .batch_evaluator import scan_and_evaluate_unit_files, scan_and_evaluate_ob_files

__all__ = [
    "evaluate_ob_consistency",
    "evaluate_unit_consistency",
    "audit_ground_element_csv",
    "scan_and_evaluate_unit_files",
    "scan_and_evaluate_ob_files"
]
