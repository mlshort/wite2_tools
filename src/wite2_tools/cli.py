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
* audit-toe        : Audit units exceeding TOE limits.

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
import configparser
import os
import sys
from typing import Dict, Callable

# Project Imports
from wite2_tools.utils import get_logger
from wite2_tools.scanning.scan_unit_for_excess import _scan_excess_resource
from .config import CONFIG_FILE_NAME
from .core.exceptions import DataIntegrityError
from .core.find_orphaned_obs import find_orphaned_obs
from .core.generate_ob_chains import generate_ob_chains
from .core.group_units_by_ob import group_units_by_ob
from .auditing import audit_unit_ob_excess
from .modifiers import (
    modify_unit_ground_element,
    modify_unit_num_squads,
    reorder_unit_squads
)


log = get_logger(__name__)



def get_config_defaults() -> dict[str, str]:
    """
    Reads data_dir and scenario_name from settings.ini.
    Returns a dictionary of defaults.
    """
    config = configparser.ConfigParser()
    defaults = {"data_dir": ".", "scenario_name": ""}
    if os.path.exists(CONFIG_FILE_NAME):
        config.read(CONFIG_FILE_NAME)
        # Ensure we check for the section to avoid falling back to defaults
        # when the file exists but the section is missing.
        if config.has_section("Paths"):
            defaults["data_dir"] = config.get("Paths", "data_dir", fallback=".")
            defaults["scenario_name"] = config.get(
                "Paths", "scenario_name", fallback=""
            )
    return defaults


def get_config_scenario_name():
    """Retrieves the scenario name from the config file."""
    scen_name = ""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_NAME):
        config.read(CONFIG_FILE_NAME)
        # Ensure we check for the section to avoid falling back to defaults
        # when the file exists but the section is missing.
        if config.has_section("Paths"):
            scen_name = config.get("Paths", "scenario_name", fallback="")
    return scen_name


def save_config(data_dir: str | None = None, scenario: str | None = None):
    """Encapsulated helper to prevent redundant logic in main()."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_NAME):
        config.read(CONFIG_FILE_NAME)
    if "Paths" not in config:
        config["Paths"] = {}
    if data_dir:
        config["Paths"]["data_dir"] = data_dir
    if scenario:
        config["Paths"]["scenario_name"] = scenario
    with open(CONFIG_FILE_NAME, "w") as f:
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


def setup_parsers() -> argparse.ArgumentParser:
    """
    Configures the argument parsing for all subcommands.
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

    subparsers = base_parser.add_subparsers(dest="command", help="Commands")

    def add_common(p):
        p.add_argument(
            "--nat", dest="nat_codes", type=int, nargs="+", default=[1],
            help="Nationality codes to filter (default: 1)"
        )

    # --- Config Command ---
    p_conf = subparsers.add_parser("config",
                                   help="Manage settings.ini")
    p_conf.add_argument("--set-path", help="Set the default data directory")
    p_conf.add_argument("--set-scenario", help="Set the scenario prefix")

    # --- Auditing ---
    p_toe = subparsers.add_parser("audit-toe", help="Audit unit TOE excess")
    add_common(p_toe)

    # --- Generation ---
    p_orphans = subparsers.add_parser(
        "gen-orphans", help="Find units with missing OB references"
    )
    add_common(p_orphans)

    p_groups = subparsers.add_parser(
        "gen-groups", help="Group units by their assigned OB ID"
    )
    p_groups.add_argument("--active-only", action="store_true")
    add_common(p_groups)

    p_chains = subparsers.add_parser(
        "gen-chains", help="Trace TOE(OB) upgrade paths"
    )
    p_chains.add_argument("--csv-out", help="Path for CSV output")
    p_chains.add_argument("--txt-out", help="Path for TXT report")
    add_common(p_chains)

    # --- Scanning ---
    p_excess = subparsers.add_parser("scan-excess", help="Scan unit resources")
    p_excess.add_argument("--resource", required=True, help="ammo/fuel/etc")
    add_common(p_excess)

    # --- Modifiers ---
    p_reord = subparsers.add_parser(
        "mod-reorder-unit", help="Move a Ground Element to a new slot"
    )
    p_reord.add_argument("--uid", dest="target_uid", type=int, required=True)
    p_reord.add_argument("--wid", dest="target_wid", type=int, required=True)
    p_reord.add_argument("--slot", dest="target_slot", type=int, required=True)

    p_repl = subparsers.add_parser(
        "mod-replace-elem", help="Globally replace a Ground Element WID"
    )
    p_repl.add_argument("--old-wid", type=int, required=True)
    p_repl.add_argument("--new-wid", type=int, required=True)

    p_upd = subparsers.add_parser(
        "mod-update-num", help="Conditionally update unit squad counts"
    )
    p_upd.add_argument("--ob-id", dest="target_ob_id", type=int, required=True)
    p_upd.add_argument("--wid", dest="target_wid", type=int, required=True)
    p_upd.add_argument("--old", dest="old_num_s", type=int, required=True)
    p_upd.add_argument("--new", dest="new_num_s", type=int, required=True)

    return base_parser

def handle_scan_excess(paths: dict, args: argparse.Namespace) -> None:
    """Helper to map CLI resource names to CSV internal column names."""
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

def main() -> None:
    """Main execution loop using a Dispatch Map."""
    log = get_logger("cli")
    parser = setup_parsers()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Path resolution assumed from existing environment context
    paths = resolve_paths(args.data_dir)

    # Dispatch Map replaces the massive if/elif chain
    # Lambda delayed execution allows for fast startup and lazy imports
    COMMAND_MAP: Dict[str, Callable] = {
        "config": lambda: save_config(args.set_path, args.set_scenario),
        "audit-toe": lambda: audit_unit_ob_excess(
            paths["unit"], paths["ob"], set(args.nat_codes)
        ),
        "gen-orphans": lambda: find_orphaned_obs(
            paths["ob"], paths["unit"], args.nat_codes
        ),
        "gen-groups": lambda: group_units_by_ob(
            paths["unit"], args.active_only, args.nat_codes
        ),
        "gen-chains": lambda: generate_ob_chains(
            paths["ob"], args.csv_out or "", args.txt_out or "", args.nat_codes
        ),
        "scan-excess": lambda: handle_scan_excess(paths, args),
        "mod-reorder-unit": lambda: reorder_unit_squads(
            paths["unit"], args.target_uid, args.target_wid, args.target_slot
        ),
        "mod-replace-elem": lambda: modify_unit_ground_element(
            paths["unit"], args.old_wid, args.new_wid
        ),
        "mod-update-num": lambda: modify_unit_num_squads(
            paths["unit"], args.target_ob_id, args.target_wid,
            args.old_num_s, args.new_num_s
        )
    }

    try:
        if args.command in COMMAND_MAP:
            log.info("Executing: %s", args.command)
            COMMAND_MAP[args.command]()
            log.info("Successfully completed %s", args.command)
    except DataIntegrityError as e:
        log.error("Data Integrity Error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        log.error("MIssing CSV file: '%s'", e)
        sys.exit(1)

    except (OSError, ValueError, KeyError, TypeError) as e:
        log.error("Critical failure in %s: %s", args.command, e, exc_info=True)
        sys.exit(1)

    except Exception as e: # pylint: disable=W0718
        # This block catches any unhandled exceptions from the workers,
        # including the 'Data Corrupt' exception raised by your unit tests.
        log.error("Critical failure in %s: %s", args.command, e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
