"""
Batch Evaluation Utility
========================

This module provides batch evaluation capabilities for War in the East 2
(WiTE2) scenario directories. It scans a target folder for `_unit`, `_ob`,
and `_ground` CSV files, automatically running comprehensive structural and
logical consistency checks across the entire dataset to identify errors,
fix ghost squads, and prevent runtime game crashes.

Command Line Usage:
    python -m wite2_tools.cli audit-batch [-h] [--data-path PATH] \
        [active_only] [fix_ghosts]

Arguments:
    target_folder (str): The directory path containing the WiTE2 CSV
                         files to be evaluated.
    active_only (bool):  If True, evaluates only active units.
                         Defaults to False.
    fix_ghosts (bool):   If True, automatically zeroes out ghost squads.
                         Defaults to False.

Example:
    $ python -m wite2_tools.cli audit-batch --data-path "C:\\My Mods" \
        True False

    Scans all _unit and _ob CSV files in the specified folder for
    consistency, checking only active units.
"""

import os

# Internal package imports
from wite2_tools.auditing.audit_unit import audit_unit_csv
from wite2_tools.auditing.audit_ob import audit_ob_csv
from wite2_tools.utils.logger import get_logger

# Initialize the logger for this specific module
log = get_logger(__name__)


def scan_and_evaluate_unit_files(target_folder: str, active_only: bool,
                                 fix_ghosts: bool):
    """
    Scans a folder for CSV files containing '_unit','_ground' and runs
    consistency checks.
    """
    if not os.path.exists(target_folder) or not os.path.isdir(target_folder):
        log.error("Scan failed: The directory '%s' does not exist.",
                  target_folder)
        return

    log.info("--- Starting Batch Unit File Evaluation in: '%s' ---",
             target_folder)

    # Get all CSV files in the directory
    all_files = os.listdir(target_folder)
    csv_files = [f for f in all_files if f.lower().endswith('.csv')]

    # Filter by name and build absolute paths
    unit_files = [os.path.join(target_folder, f)
                  for f in csv_files if "_unit" in f.lower()]
    ground_files = [os.path.join(target_folder, f)
                    for f in csv_files if "_ground" in f.lower()]

    if not unit_files:
        log.warning("No files found containing the '_unit' substring.")
        return

    if not ground_files:
        log.warning("No files found containing the '_ground' substring.")
        return

    total_issues = 0
    files_processed = 0

    for unit_file, ground_file in zip(unit_files, ground_files):
        unit_file_name = os.path.basename(unit_file)
        log.info("Processing:'%s'", unit_file_name)

        issues = audit_unit_csv(unit_file, ground_file,
                                active_only, fix_ghosts)

        if issues >= 0:
            files_processed += 1
            total_issues += issues
        else:
            log.error("Failed to process '%s' due to an internal error.",
                      unit_file_name)

    log.info("--- Batch Complete ---")
    log.info("Files Processed: %d", files_processed)
    log.info("Total Logical/Structural Issues Found: %d", total_issues)

    print(f"\nScan complete. {files_processed} unit files checked."
          f" {total_issues} issues found.")
    print("Check the latest log in your /logs folder for specific "
          "row details.")


def scan_and_evaluate_ob_files(target_folder: str):
    """
    Scans a folder for CSV files containing '_ob','_ground' and runs
    consistency checks.
    """
    if not os.path.exists(target_folder) or not os.path.isdir(target_folder):
        log.error("Scan failed: The directory '%s' does not exist.",
                  target_folder)
        return

    log.info("--- Starting Batch TOE(OB) Evaluation in:'%s' ---",
             target_folder)

    # Get all CSV files in the directory
    all_files = os.listdir(target_folder)
    csv_files = [f for f in all_files if f.lower().endswith('.csv')]

    # Filter by name and build absolute paths
    ob_files = [os.path.join(target_folder, f)
                for f in csv_files if "_ob" in f.lower()]
    ground_files = [os.path.join(target_folder, f)
                    for f in csv_files if "_ground" in f.lower()]

    if not ob_files:
        log.warning("No files found containing the '_ob' substring.")
        return

    if not ground_files:
        log.warning("No files found containing the '_ground' substring.")
        return

    total_issues = 0
    files_processed = 0

    for ob_file, ground_file in zip(ob_files, ground_files):
        ob_file_name = os.path.basename(ob_file)
        log.info("Processing:'%s'", ob_file_name)

        issues = audit_ob_csv(ob_file, ground_file)
        files_processed += 1

        if issues >= 0:
            total_issues += issues
        else:
            log.error("Failed to process '%s' due to an internal error.",
                      ob_file_name)

    log.info("--- Batch Complete ---")
    log.info("Files Processed: %d", files_processed)
    log.info("Total Logical/Structural Issues Found: %d", total_issues)

    print(f"\nScan complete. {files_processed} ob files checked. "
          f"{total_issues} issues found.")
    print("Check the latest log in your /logs folder for specific "
          "row details.")
