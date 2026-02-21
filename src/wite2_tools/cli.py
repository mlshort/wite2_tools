"""
WiTE2 Utility Command-Line Interface (CLI)
==========================================

A unified command-line tool for modifying, auditing, and analyzing War in the
East 2 (WiTE2) scenario data files. This script acts as the main entry point
for executing targeted modifications, generating analytics, and running audits.

Available Commands:
-------------------
[Modifiers]
* replace-elem    : Swaps a specific Ground Element WID across the unit
                    dataset.
* update-num      : Updates squad counts for a specific GE within a specific
                    TOE(OB).
* reorder-unit    : Moves a Ground Element to a new slot index for a Unit.
* reorder-ob      : Moves a Ground Element to a new slot index for an TOE(OB).
* compact-weapons : Removes empty weapon slots and shifts remaining weapons up.

[Auditing]
* audit-ground    : Scans a _ground CSV file to ensure type IDs are valid.
* batch-eval      : Scans a folder for CSV files and runs consistency checks.

[Core Analytics]
* count-inventory : Counts global unit inventory (with optional nat filters).
* find-orphans    : Identifies unreferenced TOE(OB) IDs.
* check-orphan    : Checks if a specific TOE(OB) ID is orphaned.
* gen-chains      : Generates TOE(OB) upgrade chains to CSV/TXT outputs.
* group-units     : Groups active units by their assigned TOE(OB) ID.

[Scanning]
* scan-ob-elem    : Scans OBs for a specific Ground Element WID.
* scan-unit-elem  : Scans Units for a specific Ground Element WID.
* scan-excess     : Scans units for excess supplies (ammo, fuel, etc.).

[Utilities]
* detect-encoding : Detects the character encoding of a specific file.
* lookup          : Quick identity lookup for an OB, Ground, or Unit ID.

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
from wite2_tools.utils.get_type_name import (
    get_ob_full_name,
    get_ground_elem_type_name
)
from wite2_tools.auditing.validator import (
    evaluate_unit_consistency,
    evaluate_ob_consistency
)

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
    find_orphaned_ob_ids,
    is_ob_orphaned,
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


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    parser = argparse.ArgumentParser(description="WiTE2 Utility CLI - "
                                                 "All-in-One Toolkit")
    subparsers = parser.add_subparsers(dest="command",
                                       help="Available commands")

    # ==========================================
    # MODIFIERS
    # ==========================================
    replace_parser = subparsers.add_parser('replace-elem',
                                           help='Replace Ground Elements '
                                           'in _unit.csv')
    replace_parser.add_argument('old_wid', type=int,
                                help='The WID to search for')
    replace_parser.add_argument('new_wid', type=int,
                                help='The WID to replace it with')
    replace_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    num_parser = subparsers.add_parser('update-num',
                                       help='Update number of squads '
                                       'in _unit.csv')
    num_parser.add_argument("ob_id", type=int, help="Target unit's TOE(OB) ID")
    num_parser.add_argument("wid", type=int,
                            help="Unit's WID containing squads to change")
    num_parser.add_argument("old_num_squads", type=int,
                            help="Number of existing squads")
    num_parser.add_argument("new_num_squads", type=int,
                            help="Number of new squads to set")
    num_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    unit_reorder_parser = subparsers.add_parser('reorder-unit',
                                                help='Reorder squad slots '
                                                'in _unit.csv')
    unit_reorder_parser.add_argument("unit_id", type=int, help="WiTE2 UNIT ID")
    unit_reorder_parser.add_argument("wid", type=int,
                                     help="The WID of the Ground Element to"
                                     " be moved")
    unit_reorder_parser.add_argument("target_slot", type=int,
                                     help="Destination Slot Location (0-31)")
    unit_reorder_parser.add_argument('--unit-file',
                                     default=CONF_UNIT_FULL_PATH)

    ob_reorder_parser = subparsers.add_parser('reorder-ob',
                                              help='Reorder squad slots '
                                              'in _ob.csv')
    ob_reorder_parser.add_argument("ob_num", type=int,
                                   help="Target TOE(OB) ID")
    ob_reorder_parser.add_argument("wid", type=int,
                                   help="The WID specifying the Ground Element"
                                   " to be moved")
    ob_reorder_parser.add_argument("target_slot", type=int, help="Destination"
                                   " Slot Location (0-31)")
    ob_reorder_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)

    compact_parser = subparsers.add_parser('compact-weapons',
                                           help='Removes empty weapon slots '
                                           'in _ground.csv')
    compact_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH)

    # ==========================================
    # AUDITING
    # ==========================================
    audit_gnd_parser = subparsers.add_parser('audit-ground',
                                             help='Scans _ground.csv to'
                                             ' ensure type IDs are valid')
    audit_gnd_parser.add_argument('--ground-file',
                                  default=CONF_GROUND_FULL_PATH,
                                  help="Optional: (default: %(default)s)")

    batch_eval_parser = subparsers.add_parser('batch-eval',
                                              help='Batch runs consistency '
                                              'checks on CSV files')
    batch_eval_parser.add_argument('--target', choices=['all', 'unit', 'ob'],
                                   default='all',
                                   help="Optional: Which files to "
                                   "evaluate (default: %(default)s)")
    batch_eval_parser.add_argument('--data-path', default=LOCAL_DATA_PATH,
                                   help="Optional: (default: %(default)s)")
    batch_eval_parser.add_argument('active_only', type=str2bool, nargs='?',
                                   default=False,
                                   help="Optional: Only evaluate active"
                                   " units (default: %(default)s)")
    batch_eval_parser.add_argument('fix_ghosts', type=str2bool, nargs='?',
                                   default=False,
                                   help="Optional: Fix ghost squads "
                                   "automatically (default: %(default)s)")

    audit_unit_parser = subparsers.add_parser('audit-unit',
                                              help='Runs consistency checks '
                                              'on '
                                              'a single _unit.csv file')
    audit_unit_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH,
                                   help="Optional: (default: %(default)s)")
    audit_unit_parser.add_argument('--ground-file',
                                   default=CONF_GROUND_FULL_PATH,
                                   help="Optional: (default: %(default)s)")
    audit_unit_parser.add_argument('active_only', type=str2bool, nargs='?',
                                   default=True,
                                   help="Optional: Only evaluate active units "
                                   "(default: %(default)s)")
    audit_unit_parser.add_argument('fix_ghosts', type=str2bool, nargs='?',
                                   default=False,
                                   help="Optional: Fix ghost squads "
                                   "automatically (default: %(default)s)")

    audit_ob_parser = subparsers.add_parser('audit-ob',
                                            help='Runs consistency checks on a'
                                            ' single _ob.csv file')
    audit_ob_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                                 help="Optional: (default: %(default)s)")
    audit_ob_parser.add_argument('--ground-file',
                                 default=CONF_GROUND_FULL_PATH,
                                 help="Optional: (default: %(default)s)")

    # ==========================================
    # CORE ANALYTICS
    # ==========================================
    inv_parser = subparsers.add_parser('count-inventory',
                                       help='Counts global unit '
                                       'equipment inventory')
    inv_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH,
                            help="Optional: (default: %(default)s)")
    inv_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH,
                            help="Optional: (default: %(default)s)")
    inv_parser.add_argument('--nat-codes', type=int, nargs='+',
                            help='Optional: Filter by nationality codes '
                            '(e.g., 1, 3)')

    orphan_parser = subparsers.add_parser('find-orphans',
                                          help='Identifies the unreferenced '
                                          'TOE(OB) templates')
    orphan_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                               help="Optional: (default: %(default)s)")
    orphan_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH,
                               help="Optional: (default: %(default)s)")
    orphan_parser.add_argument('--nat-codes', type=int, nargs='+',
                               help='Optional: Filter by nationality codes'
                               ' (e.g., 1, 3)')

    check_orphan_parser = subparsers.add_parser('check-orphan',
                                                help='Checks if a specific '
                                                'TOE(OB) ID is orphaned')
    check_orphan_parser.add_argument('ob_id', type=int,
                                     help='The TOE(OB) ID to check')
    check_orphan_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                                     help="Optional: (default: %(default)s)")
    check_orphan_parser.add_argument('--unit-file',
                                     default=CONF_UNIT_FULL_PATH,
                                     help="Optional: (default: %(default)s)")
    check_orphan_parser.add_argument('--nat-codes', type=int, nargs='+',
                                     help='Optional: Filter by nationality '
                                     'codes (e.g., 1, 3)')

    chains_parser = subparsers.add_parser('gen-chains',
                                          help='Generates chronological '
                                          'TOE(OB) upgrade chains')
    chains_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                               help="Optional: (default: %(default)s)")
    chains_parser.add_argument('--csv-out',
                               default=os.path.join(LOCAL_EXPORTS_PATH,
                                                    "ob_upgrade_chains.csv"))
    chains_parser.add_argument('--txt-out',
                               default=os.path.join(LOCAL_EXPORTS_PATH,
                                                    "ob_upgrade_chains.txt"))
    chains_parser.add_argument('--nat-codes', type=int, nargs='+',
                               help='Optional: Filter by nationality codes '
                               '(e.g., 1, 3)')

    group_parser = subparsers.add_parser('group-units', help='Groups active '
                                         'units by their assigned TOE(OB) ID')
    group_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH,
                              help="Optional: (default: %(default)s)")
    # NEW: Added nationality filter support to the CLI
    group_parser.add_argument('--nat-codes', type=int, nargs='+',
                              help='Optional: Filter by nationality'
                              ' codes (e.g., 1, 3)')
    group_parser.add_argument('active_only', type=str2bool, nargs='?',
                              default=True,
                              help="Optional: Only evaluate active units "
                                   "(default: %(default)s)")

    # ==========================================
    # SCANNING
    # ==========================================
    scan_ob_parser = subparsers.add_parser('scan-ob-elem',
                                           help='Locates a specific Ground '
                                           'Element within all TOE(OB)s')
    scan_ob_parser.add_argument('wid', type=int, help='Ground Element''s '
                                'WID to search for')
    scan_ob_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                                help="Optional: (default: %(default)s)")

    scan_unit_parser = subparsers.add_parser('scan-unit-elem',
                                             help='Locates a specific Ground '
                                             'Element within Units')
    scan_unit_parser.add_argument('wid', type=int, help='Ground Element''s '
                                  'WID to search for')
    scan_unit_parser.add_argument('num_squads', type=int, nargs='?',
                                  default=-1,
                                  help='Filter by exact quantity')
    scan_unit_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)
    scan_unit_parser.add_argument('--ground-file',
                                  default=CONF_GROUND_FULL_PATH)
    scan_unit_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH)

    excess_parser = subparsers.add_parser('scan-excess',
                                          help='Locates units with excessive '
                                          'logistical stores')
    excess_parser.add_argument('--operation',
                               choices=['ammo', 'supplies', 'fuel',
                                        'vehicles'],
                               default='ammo')
    excess_parser.add_argument('--unit-file', default=CONF_UNIT_FULL_PATH)

    # ==========================================
    # UTILITIES
    # ==========================================
    lookup_parser = subparsers.add_parser('lookup',
                                          help='Quick identity lookup for '
                                          'game IDs')
    lookup_parser.add_argument('--type', choices=['ob', 'ground'],
                               required=True, help='The category of the ID')
    lookup_parser.add_argument('--id', type=int, required=True,
                               help='The ID to look up')
    lookup_parser.add_argument('--ob-file', default=CONF_OB_FULL_PATH,
                               help="Optional: (default: %(default)s)")
    lookup_parser.add_argument('--ground-file', default=CONF_GROUND_FULL_PATH,
                               help="Optional: (default: %(default)s)")

    enc_parser = subparsers.add_parser('detect-encoding',
                                       help='Detects the character encoding '
                                       'of a specific file')
    enc_parser.add_argument('file_path', type=str, help='Path to the file to '
                            'check')

    args = parser.parse_args()

    # Handle case where no command is passed
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Routing logic
    try:
        # Modifiers
        if args.command == 'replace-elem':
            replace_unit_ground_element(args.unit_file, args.old_wid,
                                        args.new_wid)
        elif args.command == 'update-num':
            update_unit_num_squads(args.unit_file, args.ob_id, args.wid,
                                   args.old_num_squads, args.new_num_squads)
        elif args.command == 'reorder-unit':
            reorder_unit_squads(args.unit_file, args.unit_id, args.wid,
                                args.target_slot)
        elif args.command == 'reorder-ob':
            reorder_ob_squads(args.ob_file, args.ob_num, args.wid,
                              args.target_slot)
        elif args.command == 'compact-weapons':
            remove_ground_weapon_gaps(args.ground_file)

        # Auditing
        elif args.command == 'audit-ground':
            audit_ground_element_csv(args.ground_file)
        elif args.command == 'batch-eval':
            if args.target in ['all', 'unit']:
                scan_and_evaluate_unit_files(args.data_path, args.active_only,
                                             args.fix_ghosts)
            if args.target in ['all', 'ob']:
                scan_and_evaluate_ob_files(args.data_path)

        # Single-file Auditing
        elif args.command == 'audit-unit':
            issues = evaluate_unit_consistency(args.unit_file,
                                               args.ground_file,
                                               args.active_only,
                                               args.fix_ghosts)
            print(f"Unit audit complete. Found {issues} issues.")
        elif args.command == 'audit-ob':
            issues = evaluate_ob_consistency(args.ob_file, args.ground_file)
            print(f"TOE(OB) audit complete. Found {issues} issues.")

        # Core
        elif args.command == 'count-inventory':
            count_global_unit_inventory(args.unit_file, args.ground_file,
                                        args.nat_codes)
        elif args.command == 'find-orphans':
            find_orphaned_ob_ids(args.ob_file, args.unit_file,
                                 args.nat_codes)
        elif args.command == 'check-orphan':
            is_orphan = is_ob_orphaned(args.ob_file, args.unit_file,
                                       args.ob_id, args.nat_codes)
            status = "an ORPHAN (unused)" if is_orphan else "VALID (ref)"
            print(f"TOE(OB) ID {args.ob_id} is {status}.")
        elif args.command == 'gen-chains':
            generate_ob_chains(args.ob_file, args.csv_out, args.txt_out,
                               args.nat_codes)
        elif args.command == 'group-units':
            group_units_by_ob(args.unit_file, args.active_only, args.nat_codes)

        # Scanning
        elif args.command == 'scan-ob-elem':
            scan_ob_for_ground_elem(args.ob_file, args.wid)
        elif args.command == 'scan-unit-elem':
            scan_unit_for_ground_elem(args.unit_file, args.ground_file,
                                      args.ob_file, args.wid, args.num_squads)
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
            print(f"Detected Encoding for"
                  f"{os.path.basename(args.file_path)}: {encoding}")

        elif args.command == 'lookup':
            name = "Unknown"  # Fallback to prevent UnboundLocalError

            if args.type == 'ob':
                name = get_ob_full_name(args.ob_file, args.id)
            elif args.type == 'ground':
                name = get_ground_elem_type_name(args.ground_file, args.id)

            print(f"[{args.type.upper()}] ID {args.id}: {name}")

    except (FileNotFoundError, ValueError, KeyError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
