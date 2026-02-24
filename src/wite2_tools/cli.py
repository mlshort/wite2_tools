"""
WiTE2 Utility Command-Line Interface (CLI)
==========================================

A unified command-line tool for modifying, auditing, and analyzing War in the
East 2 (WiTE2) scenario data files. This script acts as the main entry point
for executing targeted modifications, generating analytics, and running audits.

Available Commands:
-------------------
[Auditing]
* audit-ground     : Scans a _ground CSV file to ensure type IDs are valid.
* audit-unit       : Audits _unit.csv data integrity and referential links.
* audit-ob         : Audits _ob.csv referential integrity.
* audit-batch      : Scans a folder for CSV files and runs consistency checks.

[Scanning]
* scan-ob          : Scans TOE(OB)s for a specific Ground Element WID.
* scan-unit        : Scans Units for a specific Ground Element WID.
* scan-excess      : Scans units for excess supplies (ammo, fuel, etc.).

[Modifiers]
* mod-compact-wpn  : Removes empty weapon slots and shifts remaining up.
* mod-reorder-ob   : Moves a Ground Element to a new slot index for an TOE(OB).
* mod-reorder-unit : Moves a Ground Element to a new slot index for a Unit.
* mod-replace-elem : Globally replaces a specific Ground Element WID.
* mod-update-num   : Conditionally updates unit squad counts.

[Generators / Core Analytics]
* gen-inventory    : Counts global unit inventory (with nat filters).
* gen-orphans      : Identifies unreferenced TOE(OB) IDs.
* gen-groups       : Groups active units by their assigned TOE(OB) ID.
* gen-chains       : Generates TOE(OB) upgrade chains to CSV/TXT outputs.

Note: Target file paths are resolved automatically from the provided
      `--data-dir` (or `-d`) argument. It defaults to the current directory.

"""
import argparse
import os
import sys
import configparser

from wite2_tools.auditing import (
    audit_ground_element_csv,
    audit_ob_csv,
    audit_unit_csv,
#    scan_and_evaluate_ob_files,
    scan_and_evaluate_unit_files
)

from wite2_tools.core import (
    group_units_by_ob,
    count_global_unit_inventory,
    identify_unused_devices,
    find_orphaned_ob_ids,
    generate_ob_chains
)

from wite2_tools.modifiers import (
    remove_ground_weapon_gaps,
    modify_unit_ground_element,
    modify_unit_num_squads,
    reorder_ob_squads,
    reorder_unit_squads
)

from wite2_tools.scanning import (
    scan_ob_for_ground_elem,
    scan_unit_for_ground_elem
)

from wite2_tools.scanning.scan_unit_for_excess import _scan_excess_resource

from wite2_tools.utils import get_logger

log = get_logger(__name__)

CONFIG_FILE = "settings.ini"


def get_config_defaults() -> dict[str, str]:
    """
    Reads data_dir and scenario_name from settings.ini.
    Returns a dictionary of defaults.
    """
    config = configparser.ConfigParser()
    defaults = {"data_dir": ".", "scenario_name": ""}
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        # Ensure we check for the section to avoid falling back to defaults
        # when the file exists but the section is missing.
        if config.has_section("Paths"):
            defaults["data_dir"] = config.get("Paths", "data_dir", fallback=".")
            defaults["scenario_name"] = config.get("Paths", "scenario_name", fallback="")
    return defaults

def get_config_scenario_name():
    scen_name = ""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        # Ensure we check for the section to avoid falling back to defaults
        # when the file exists but the section is missing.
        if config.has_section("Paths"):
            scen_name = config.get("Paths", "scenario_name", fallback="")
    return scen_name

def save_config(data_dir: str | None = None, scenario: str | None = None):
    """Encapsulated helper to prevent redundant logic in main()."""
    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)

    if "Paths" not in config:
        config["Paths"] = {}

    if data_dir:
        config["Paths"]["data_dir"] = data_dir

    if scenario:
        config["Paths"]["scenario_name"] = scenario

    with open(CONFIG_FILE, "w") as f:
        config.write(f)


def resolve_paths(data_dir: str) -> dict[str, str]:
    """
    Resolves standard WiTE2 file names from a target directory.

    Args:
        data_dir (str): The directory containing the WiTE2 CSV files.

    Returns:
        dict[str, str]: A dictionary mapping file keys ('unit', 'ob',
                        'ground') to their absolute or relative paths.

    """
    defaults = get_config_defaults()
    scen_name = defaults.get("scenario_name", "")
    return {
        "unit": os.path.join(data_dir, scen_name + "_unit.csv"),
        "ob": os.path.join(data_dir, scen_name + "_ob.csv"),
        "ground": os.path.join(data_dir, scen_name + "_ground.csv"),
        "device": os.path.join(data_dir, scen_name + "_device.csv"),
        "aircraft": os.path.join(data_dir, scen_name + "_aircraft.csv")
    }


def create_parser() -> argparse.ArgumentParser:
    """
    Constructs the CLI argument parser with inherited parent parsers.
    """
    # Load the default path from config for the help text and default value
    defaults = get_config_defaults()
    default_path = defaults.get("data_dir", ".")

    # --- PARENT PARSERS ---
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "-d", "--data-dir", default=default_path,
        help=f"Directory containing the WiTE2 CSV files "
             f"(Current default: {default_path})."
    )
    base_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug logging output."
    )

    nat_parser = argparse.ArgumentParser(add_help=False)
    nat_parser.add_argument(
        "--nat-codes", nargs="+", type=int,
        help="Filter by specific nationality codes (e.g., 1 3)."
    )

    active_parser = argparse.ArgumentParser(add_help=False)
    active_parser.add_argument(
        "--active-only", action="store_true", default=True,
        help="Skip inactive units (type=0)."
    )

    # --- MAIN PARSER ---
    main_parser = argparse.ArgumentParser(
        prog="wite2-tools",
        description="WiTE2 Data Modification and Analysis Toolkit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = main_parser.add_subparsers(dest="command", required=True)

    # NEW CONFIG COMMAND
    config_parser = subparsers.add_parser(
        "config",
        help="Manage global tool settings like default data directory."
    )
    config_parser.add_argument(
        "--set-path", type=str,
        help="Save a new default data directory to settings.ini."
    )
    config_parser.add_argument(
        "--set-scenario", type=str,
        help="Save a new default scenario name to settings.ini."
    )

    # 1. AUDIT COMMANDS
    subparsers.add_parser(
        "audit-ground", parents=[base_parser],
        help="Audit the _ground.csv file for consistency."
    )

    audit_unit = subparsers.add_parser(
        "audit-unit", parents=[base_parser, active_parser],
        help="Audit _unit.csv integrity."
    )
    audit_unit.add_argument(
        "--fix-ghosts", action="store_true",
        help="Automatically zeroes out ghost squads."
    )

# --- NEW ARGUMENTS ---
    audit_unit.add_argument(
        "--relink-orphans", action="store_true",
        help="Automatically reassigns units with inactive/missing HQs."
    )
    audit_unit.add_argument(
        "--fallback-hq", type=int, default=0,
        help="The Unit ID to assign orphaned units to (e.g., OKH/STAVKA)."
    )

    subparsers.add_parser(
        "audit-ob", parents=[base_parser],
        help="Audit _ob.csv referential integrity."
    )

    batch = subparsers.add_parser(
        "audit-batch", parents=[base_parser, active_parser],
        help="Run all audits on a directory."
    )
    batch.add_argument("--fix-ghosts", action="store_true")

    # 2. SCAN COMMANDS
    scan_ob = subparsers.add_parser(
        "scan-ob", parents=[base_parser],
        help="Find all Ground Elements matching a WID in _ob.csv"
    )
    scan_ob.add_argument("target_wid", type=int)

    scan_unit = subparsers.add_parser(
        "scan-unit", parents=[base_parser],
        help="Find all Ground Elements matching a WID in _unit.csv"
    )
    scan_unit.add_argument("target_wid", type=int)
    scan_unit.add_argument("--num-squads", type=int, default=-1)

    scan_ex = subparsers.add_parser(
        "scan-excess", parents=[base_parser],
        help="Find units with excessive logistics"
    )
    scan_ex.add_argument(
        "--operation", default="ammo",
        choices=["ammo", "supplies", "fuel", "vehicles"]
    )

    scan_unused = subparsers.add_parser(
        "scan-unused", parents=[base_parser],
        help="Identify devices of a specific type not used in any Ground Element."
    )
    scan_unused.add_argument(
        "device_type", type=int,
        help="The integer ID of the device type (e.g., 7 for Hvy Gun, 25 for DP Gun)."
    )

    # 3. MODIFIER COMMANDS
    subparsers.add_parser(
        "mod-compact-wpn", parents=[base_parser],
        help="Compact weapon gaps in _ground.csv"
    )

    mod_re_ob = subparsers.add_parser(
        "mod-reorder-ob", parents=[base_parser],
        help="Move a squad to a new slot in _ob.csv"
    )
    mod_re_ob.add_argument("target_ob_id", type=int)
    mod_re_ob.add_argument("target_wid", type=int)
    mod_re_ob.add_argument("target_slot", type=int)

    mod_re_unit = subparsers.add_parser(
        "mod-reorder-unit", parents=[base_parser],
        help="Move a squad to a new slot in _unit.csv"
    )
    mod_re_unit.add_argument("target_uid", type=int)
    mod_re_unit.add_argument("target_wid", type=int)
    mod_re_unit.add_argument("target_slot", type=int)

    mod_rep = subparsers.add_parser(
        "mod-replace-elem", parents=[base_parser],
        help="Globally replace a Ground Element WID"
    )
    mod_rep.add_argument("old_wid_id", type=int)
    mod_rep.add_argument("new_wid_id", type=int)

    mod_num = subparsers.add_parser(
        "mod-update-num", parents=[base_parser],
        help="Conditionally update a unit's squad count"
    )
    mod_num.add_argument("target_ob_id", type=int)
    mod_num.add_argument("target_wid", type=int)
    mod_num.add_argument("old_num_squads", type=int)
    mod_num.add_argument("new_num_squads", type=int)

    # 4. GENERATOR / CORE COMMANDS
    subparsers.add_parser(
        "gen-inventory", parents=[base_parser, nat_parser],
        help="Calculate total global equipment counts"
    )
    subparsers.add_parser(
        "gen-orphans", parents=[base_parser, nat_parser],
        help="Find unreferenced TOE(OB) templates"
    )
    subparsers.add_parser(
        "gen-groups", parents=[base_parser, nat_parser, active_parser],
        help="Group active units by their TOE(OB)"
    )

    gen_chain = subparsers.add_parser(
        "gen-chains", parents=[base_parser, nat_parser],
        help="Generate upgrade chain paths"
    )
    gen_chain.add_argument("--csv-out", default="ob_chains.csv")
    gen_chain.add_argument("--txt-out", default="ob_chains.txt")

    return main_parser


def main():
    """
    Main execution block. Parses arguments, sets up logging, resolves
    file paths, and routes execution to the designated command logic.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Handle Config command before path resolution
    if args.command == "config":
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)

        if "Paths" not in config:
            config["Paths"] = {}

        if args.set_path:
            save_config(args.set_path)
            print(f"Default data directory saved: {args.set_path}")

        if args.set_scenario:
            save_config(None, args.set_scenario)
            print(f"Scenario name saved: {args.set_scenario}")

        if not args.set_path and not args.set_scenario:
            defaults = get_config_defaults()
            print(f"Current default data directory: {defaults['data_dir']}")
            print(f"Current scenario name: {defaults['scenario_name']}")
        sys.exit(0)

    paths = resolve_paths(args.data_dir)

    if args.verbose:
        log.info("Verbose mode enabled.")

    log.info("Using Data Directory: %s", os.path.abspath(args.data_dir))

    try:
        if args.command == "audit-ground":
            audit_ground_element_csv(paths["ground"])

        elif args.command == "audit-unit":
            # Pass the new arguments down to the validator
            audit_unit_csv(
                paths["unit"], paths["ground"],
                args.active_only, args.fix_ghosts,
                args.relink_orphans, args.fallback_hq
            )

        elif args.command == "audit-ob":
            audit_ob_csv(paths["ob"], paths["ground"])

        elif args.command == "audit-batch":
            scan_and_evaluate_unit_files(
                args.data_dir, args.active_only, args.fix_ghosts
            )

        elif args.command == "scan-ob":
            scan_ob_for_ground_elem(paths["ob"], args.target_wid)

        elif args.command == "scan-unit":
            scan_unit_for_ground_elem(
                paths["unit"],
                paths["ob"],
                paths["ground"],
                args.target_wid, args.num_squads
            )
        elif args.command == "scan-unused":
            identify_unused_devices(
                paths["ground"],
                paths["aircraft"],
                paths["device"],
                args.device_type
            )

        elif args.command == "scan-excess":
            need_map = {
                'ammo': 'aNeed', 'supplies': 'sNeed',
                'fuel': 'fNeed', 'vehicles': 'vNeed'
            }
            display_map = {
                'ammo': 'Ammo', 'supplies': 'Supplies',
                'fuel': 'Fuel', 'vehicles': 'Vehicles'
            }
            _scan_excess_resource(
                paths["unit"], args.operation,
                need_map[args.operation], display_map[args.operation]
            )

        elif args.command == "mod-compact-wpn":
            remove_ground_weapon_gaps(paths["ground"])

        elif args.command == "mod-reorder-ob":
            reorder_ob_squads(
                paths["ob"], args.target_ob_id, args.target_wid,
                args.target_slot
            )

        elif args.command == "mod-reorder-unit":
            reorder_unit_squads(
                paths["unit"], args.target_uid,
                args.target_wid, args.target_slot
            )

        elif args.command == "mod-replace-elem":
            modify_unit_ground_element(
                paths["unit"], args.old_wid, args.new_wid
            )

        elif args.command == "mod-update-num":
            modify_unit_num_squads(
                paths["unit"], args.target_ob_id, args.target_wid,
                args.old_num_squads, args.new_num_squads
            )

        elif args.command == "gen-inventory":
            count_global_unit_inventory(
                paths["unit"], paths["ground"], args.nat_codes
            )

        elif args.command == "gen-orphans":
            find_orphaned_ob_ids(paths["ob"], paths["unit"], args.nat_codes)

        elif args.command == "gen-groups":
            group_units_by_ob(paths["unit"], args.active_only, args.nat_codes)

        elif args.command == "gen-chains":
            generate_ob_chains(
                paths["ob"], args.csv_out, args.txt_out, args.nat_codes
            )

    except FileNotFoundError as e:
        log.error("Missing CSV: %s. Check your --data-dir path.", e)
        sys.exit(1)
    except (OSError, ValueError, KeyError, TypeError) as e:
        log.exception("A data processing error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
