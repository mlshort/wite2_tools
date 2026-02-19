"""
WiTE2 Utility Command-Line Interface (CLI)
==========================================

A unified command-line tool for modifying, auditing, and analyzing War in the
East 2 (WiTE2) scenario data files. This script acts as the main entry point
for executing targeted modifications, generating analytics, and running audits.

Available Commands:
-------------------
[Modifiers]
* replace-elem    : Swaps a specific Ground Element ID across the unit dataset.
* update-num      : Updates squad counts for a specific GE within a specific OB.
* reorder-unit    : Moves a Ground Element to a new slot index for a Unit.
* reorder-ob      : Moves a Ground Element to a new slot index for an OB.
* compact-weapons : Removes empty weapon slots and shifts remaining weapons up.

[Auditing]
* audit-ground    : Scans a _ground CSV file to ensure type IDs are valid.
* batch-eval      : Scans a folder for CSV files and runs consistency checks.

[Core Analytics]
* count-inventory : Counts global unit inventory (with optional nat filters).
* find-orphans    : Identifies unreferenced OB IDs.
* gen-chains      : Generates OB upgrade chains to CSV/TXT outputs.
* group-units     : Groups active units by their assigned OB ID.

[Scanning]
* scan-ob-elem    : Scans OBs for a specific Ground Element ID.
* scan-unit-elem  : Scans Units for a specific Ground Element ID.
* scan-excess     : Scans units for excess supplies (ammo, fuel, etc.).

Note: Target file paths are resolved automatically via the `paths.py` module
      unless explicitly overridden using the optional arguments.
"""
import argparse
import sys
import os

from wite2_tools.paths import (
    CONF_UNIT_FULL_PATH,
    CONF_OB_FULL_PATH,
    CONF_GROUND_FULL_PATH,
    LOCAL_DATA_PATH,
    LOCAL_EXPORTS_PATH
)

from wite2_tools.utils.det_encoding import detect_encoding
from wite2_tools.auditing.validator import evaluate_unit_consistency, evaluate_ob_consistency

from wite2_tools.modifiers import (
    replace_unit_ground_element,
    update_unit_num_squads,
    reorder_unit_squads,
    reorder_ob_squads,
    remove_ground_weapon_gaps
)

from wite2_tools.auditing import (
    audit_ground_element_csv,
    scan_and_evaluate_unit_files,
    scan_and_evaluate_ob_files
)

from wite2_tools.core import (
    count_global_unit_inventory,
    find_unreferenced_ob_ids,
    generate_ob_chains,
    group_units_by_ob
)

from wite2_tools.scanning import (
    scan_ob_for_ground_elem,
    scan_unit_for_ground_elem,
    scan_units_for_excess_ammo,
    scan_units_for_excess_fuel,
    scan_units_for_excess_supplies,
    scan_units_for_excess_vehicles
)


def main():
    parser = argparse.ArgumentParser(description="WiTE2 Utility CLI - All-in-One Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ==========================================
    # MODIFIERS
    # ==========================================
    replace_parser = subparsers.add_parser('replace-elem', help='Replace Ground Element IDs in _unit.csv')
    replace_parser.add_argument('old_id', type=int, help='The ID to search for')
    replace_parser.add_argument('new_id', type=int, help='The ID to replace it with')
    replace_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    num_parser = subparsers.add_parser('update-num', help='Update number of squads in _unit.csv')
    num_parser.add_argument('new_num', type=int, help='The new number of squads to set')
    num_parser.add_argument("ob_id", type=int, help="Target unit's OB ID")
    num_parser.add_argument("ge_id", type=int, help="Unit's Elem ID containing squads to change")
    num_parser.add_argument("old_num_squads", type=int, help="Number of existing squads")
    num_parser.add_argument("new_num_squads", type=int, help="Number of new squads to set")
    num_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    unit_reorder_parser = subparsers.add_parser('reorder-unit', help='Reorder squad slots in _unit.csv')
    unit_reorder_parser.add_argument("unit_id", type=int, help="WiTE2 UNIT ID")
    unit_reorder_parser.add_argument("ge_id", type=int, help="The WID of the Ground Element to be moved")
    unit_reorder_parser.add_argument("move_to", type=int, help="Destination Location (0-31)")
    unit_reorder_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    ob_reorder_parser = subparsers.add_parser('reorder-ob', help='Reorder squad slots in _ob.csv')
    ob_reorder_parser.add_argument("ob_num", type=int, help="WiTE2 OB ID")
    ob_reorder_parser.add_argument("ge_id", type=int, help="The WID of the Ground Element to be moved")
    ob_reorder_parser.add_argument("move_to", type=int, help="Destination Location (0-31)")
    ob_reorder_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)

    compact_parser = subparsers.add_parser('compact-weapons', help='Removes empty weapon slots in _ground.csv')
    compact_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)

    # ==========================================
    # AUDITING
    # ==========================================
    audit_gnd_parser = subparsers.add_parser('audit-ground',
                                             help='Scans _ground.csv to ensure type IDs are valid')
    audit_gnd_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)

    batch_eval_parser = subparsers.add_parser('batch-eval',
                                              help='Batch runs consistency checks on CSV files')
    batch_eval_parser.add_argument('--data-path', default=LOCAL_DATA_PATH)
    batch_eval_parser.add_argument('--active-only', action='store_true',
                                   help='Only evaluate active units')
    batch_eval_parser.add_argument('--fix-ghosts', action='store_true',
                                   help='Fix ghost squads automatically')

    audit_unit_parser = subparsers.add_parser('audit-unit', help='Runs consistency checks on a single _unit.csv file')
    audit_unit_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)
    audit_unit_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)
    audit_unit_parser.add_argument('--active-only', action='store_true', help='Only evaluate active units')
    audit_unit_parser.add_argument('--fix-ghosts', action='store_true', help='Fix ghost squads automatically')

    audit_ob_parser = subparsers.add_parser('audit-ob', help='Runs consistency checks on a single _ob.csv file')
    audit_ob_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)
    audit_ob_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)

    # ==========================================
    # CORE ANALYTICS
    # ==========================================
    inv_parser = subparsers.add_parser('count-inventory',
                                       help='Counts global unit equipment inventory')
    inv_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)
    inv_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)
    inv_parser.add_argument('--nat-codes', type=int, nargs='+',
                            help='Optional: Filter by nationality codes')

    orphan_parser = subparsers.add_parser('find-orphans', help='Identifies unreferenced OB templates')
    orphan_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)
    orphan_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)
    orphan_parser.add_argument('--nat-codes', type=int, nargs='+', help='Optional: Filter by nationality codes')

    chains_parser = subparsers.add_parser('gen-chains', help='Generates chronological OB upgrade chains')
    chains_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)
    chains_parser.add_argument('--csv-out', default=os.path.join(LOCAL_EXPORTS_PATH, "ob_upgrade_chains.csv"))
    chains_parser.add_argument('--txt-out', default=os.path.join(LOCAL_EXPORTS_PATH, "ob_upgrade_chains.txt"))
    chains_parser.add_argument('--nat-codes', type=int, nargs='+', help='Optional: Filter by nationality codes')

    group_parser = subparsers.add_parser('group-units', help='Groups active units by their assigned OB ID')
    group_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    # ==========================================
    # SCANNING
    # ==========================================
    scan_ob_parser = subparsers.add_parser('scan-ob-elem', help='Locates a specific Ground Element within OBs')
    scan_ob_parser.add_argument('ge_id', type=int, help='Ground Element ID to search for')
    scan_ob_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)

    scan_unit_parser = subparsers.add_parser('scan-unit-elem',
                                             help='Locates a specific Ground Element within Units')
    scan_unit_parser.add_argument('ge_id', type=int, help='Ground Element ID to search for')
    scan_unit_parser.add_argument('num_squads', type=int, nargs='?', default=-1,
                                  help='Filter by exact quantity')
    scan_unit_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)
    scan_unit_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)
    scan_unit_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)

    excess_parser = subparsers.add_parser('scan-excess', help='Locates units with excessive logistical stores')
    excess_parser.add_argument('--operation', choices=['ammo', 'supplies', 'fuel', 'vehicles'],
                               default='ammo')
    excess_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    # ==========================================
    # UTILITIES
    # ==========================================
    enc_parser = subparsers.add_parser('detect-encoding', help='Detects the character encoding of a specific file')
    enc_parser.add_argument('file_path', type=str, help='Path to the file to check')

    args = parser.parse_args()

    # Handle case where no command is passed
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Routing logic
    try:
        # Modifiers
        if args.command == 'replace-elem':
            replace_unit_ground_element(args.unit_file, args.old_id, args.new_id)
        elif args.command == 'update-num':
            update_unit_num_squads(args.unit_file, args.ob_id, args.ge_id,
                                   args.old_num_squads, args.new_num_squads)
        elif args.command == 'reorder-unit':
            reorder_unit_squads(args.unit_file, args.unit_id, args.ge_id, args.move_to)
        elif args.command == 'reorder-ob':
            reorder_ob_squads(args.ob_file, args.ob_num, args.ge_id, args.move_to)
        elif args.command == 'compact-weapons':
            remove_ground_weapon_gaps(args.ground_file)

        # Auditing
        elif args.command == 'audit-ground':
            audit_ground_element_csv(args.ground_file)
        elif args.command == 'batch-eval':
            scan_and_evaluate_unit_files(args.data_path, args.active_only, args.fix_ghosts)
            scan_and_evaluate_ob_files(args.data_path)

        # Single-file Auditing
        elif args.command == 'audit-unit':
            issues = evaluate_unit_consistency(args.unit_file, args.ground_file, args.active_only, args.fix_ghosts)
            print(f"Unit audit complete. Found {issues} issues.")
        elif args.command == 'audit-ob':
            issues = evaluate_ob_consistency(args.ob_file, args.ground_file)
            print(f"OB audit complete. Found {issues} issues.")

        # Core
        elif args.command == 'count-inventory':
            count_global_unit_inventory(args.unit_file, args.ground_file, args.nat_codes)
        elif args.command == 'find-orphans':
            find_unreferenced_ob_ids(args.ob_file, args.unit_file, args.nat_codes)
        elif args.command == 'gen-chains':
            generate_ob_chains(args.ob_file, args.csv_out, args.txt_out, args.nat_codes)
        elif args.command == 'group-units':
            group_units_by_ob(args.unit_file)

        # Scanning
        elif args.command == 'scan-ob-elem':
            scan_ob_for_ground_elem(args.ob_file, args.ge_id)
        elif args.command == 'scan-unit-elem':
            scan_unit_for_ground_elem(args.unit_file, args.ground_file, args.ob_file, args.ge_id, args.num_squads)
        elif args.command == 'scan-excess':
            if args.operation == 'ammo':
                scan_units_for_excess_ammo(args.unit_file)
            elif args.operation == 'supplies':
                scan_units_for_excess_supplies(args.unit_file)
            elif args.operation == 'fuel':
                scan_units_for_excess_fuel(args.unit_file)
            elif args.operation == 'vehicles':
                scan_units_for_excess_vehicles(args.unit_file)
        # Utilities
        elif args.command == 'detect-encoding':
            encoding = detect_encoding(args.file_path)
            print(f"Detected Encoding for {os.path.basename(args.file_path)}: {encoding}")


    except (FileNotFoundError, ValueError, KeyError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()