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
* audit-toe        : Audit units exceeding TOE(OB) limits.

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
from .config import CONFIG_FILE_NAME, ENCODING_TYPE
from .core.exceptions import DataIntegrityError
from .core.find_orphaned_obs import find_orphaned_obs
from .core.generate_ob_chains import generate_ob_chains
from .core.group_units_by_ob import group_units_by_ob
from .core.count_global_unit_inventory import count_global_unit_inventory
from .core.identify_unused_devices import identify_unused_devices
from .core import calc_unit_support
from .auditing import (
    audit_ground_element_csv,
    audit_ob_csv,
    audit_unit_csv,
    audit_unit_ob_excess,
    scan_and_evaluate_unit_files
)
from .modifiers import (
    modify_unit_ground_element,
    modify_unit_squads,
    reorder_unit_squads,
    reorder_ob_squads,
    remove_ground_weapon_gaps
)
from .scanning import (
    scan_ob_for_ground_elem,
    scan_unit_for_ground_elem
)


paths: Dict[str,str] = {}
args = None

# Initialize the log for this specific module
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


def get_config_scenario_name()->str:
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


def save_config(data_dir: str | None = None, scenario: str | None = None)->None:
    """
    Updates settings.ini with new persistent defaults.
    """
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_NAME):
        config.read(CONFIG_FILE_NAME)
    if "Paths" not in config:
        config["Paths"] = {}
    if data_dir:
        config["Paths"]["data_dir"] = data_dir
    if scenario:
        config["Paths"]["scenario_name"] = scenario
    with open(CONFIG_FILE_NAME, "w", encoding=ENCODING_TYPE) as f:
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

    subparsers = base_parser.add_subparsers(dest="command",
                                            required=True,
                                            help="Commands")

    def add_common(p:argparse.ArgumentParser)->None:
        p.add_argument(
            "--nat", dest="nat_codes", type=int, nargs="+", default=[1],
            help="Nationality codes to filter (default: 1)"
        )

    #=========================
    # CONFIG COMMANDS
    #=========================
    p_conf = subparsers.add_parser("config", help="Manage settings.ini")
    p_conf.add_argument("--set-path", help="Set default data directory")
    p_conf.add_argument("--set-scenario", help="Set scenario prefix")

    # Auditing
    subparsers.add_parser("audit-ground", help="Audit _ground.csv")

    p_au = subparsers.add_parser("audit-unit",
                                 help="Audit _unit.csv")
    p_au.add_argument("--active-only", action="store_true", default=True)
    p_au.add_argument("--fix-ghosts", action="store_true")
    p_au.add_argument("--relink-orphans", action="store_true")
    p_au.add_argument("--fallback-hq", type=int, default=0)

    subparsers.add_parser("audit-ob", help="Audit _ob.csv")

    # Analytics
    p_calc = subparsers.add_parser("calc-support",
                                   help="Calculate unit needed support"
    )
    p_calc.add_argument("target_uid", type=int,
                        help="Target Unit ID")

    # --- Auditing ---
    p_toe = subparsers.add_parser("audit-toe",
                                  help="Audit unit TOE excess")
    add_common(p_toe)

    p_audit_devices = subparsers.add_parser("audit-devices",
        help="Identify devices defined in ground elements but never used in Units or OBs."
        )
    add_common(p_audit_devices)

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
    p_excess = subparsers.add_parser("scan-excess",
                                     help="Scan unit resources")
    p_excess.add_argument("--resource", required=True, help="ammo/fuel/etc")
    add_common(p_excess)

    # --- Modifiers ---
    p_reord = subparsers.add_parser("mod-reorder-unit",
                                    help="Move a Ground Element to a new slot"
    )
    p_reord.add_argument("target_uid", type=int)
    p_reord.add_argument("target_wid", type=int)
    p_reord.add_argument("target_slot", type=int)

    p_sunused = subparsers.add_parser("scan-unused",
                                      help="Find unused devs")
    p_sunused.add_argument("device_type", type=int)

    # =========================
    # MODIFIER COMMANDS
    # =========================
    subparsers.add_parser("mod-compact-wpn", help="Compact weapon gaps")

    p_reob = subparsers.add_parser("mod-reorder-ob", help="Move OB squad")
    p_reob.add_argument("target_ob_id", type=int)
    p_reob.add_argument("target_wid", type=int)
    p_reob.add_argument("target_slot", type=int)

    p_repl = subparsers.add_parser("mod-replace-elem",
                                   help="Globally replace a Ground Element WID")
    p_repl.add_argument("old_wid", type=int)
    p_repl.add_argument("new_wid", type=int)

    p_upd = subparsers.add_parser("mod-update-num", help="Update squad count")
    p_upd.add_argument("--ob-id", dest="target_ob_id", type=int, required=True)
    p_upd.add_argument("--wid", dest="target_wid", type=int, required=True)
    p_upd.add_argument("--old", dest="old_num_s", type=int, required=True)
    p_upd.add_argument("--new", dest="new_num_s", type=int, required=True)

    return base_parser

def handle_scan_excess(paths: dict, args: argparse.Namespace) -> None:
    """
    Helper to route excess scanning to the internal implementation.
    Maps human-readable command names to internal resource keys.
    """
    need_map = {'ammo': 'aNeed', 'supplies': 'sNeed',
                'fuel': 'fNeed', 'vehicles': 'vNeed'}
    display_map = {'ammo': 'Ammo', 'supplies': 'Supplies',
                   'fuel': 'Fuel', 'vehicles': 'Vehicles'}

    _scan_excess_resource(paths["unit"],
                          args.resource,
                          need_map[args.resource],
                          display_map[args.resource])



    # Dispatch Map replaces the massive if/elif chain
    # Lambda delayed execution allows for fast startup and lazy imports
    # Dispatch Map (To be expanded)
    # -------------------------------------------------------------------------
COMMAND_MAP: Dict[str, Callable] = {
    "config": lambda a, p: save_config(
        a.set_path,
        a.set_scenario
        ),
    "audit-ground": lambda a, p: audit_ground_element_csv(
        p["ground"]
        ),
    "audit-unit": lambda a, p: audit_unit_csv(
        p["unit"],
        p["ground"],
        a.active_only,
        a.fix_ghosts,
        a.relink_orphans,
        a.fallback_hq
        ),
    "audit-ob": lambda a, p: audit_ob_csv(
        p["ob"],
        p["ground"]
        ),
    "audit-toe": lambda a, p: audit_unit_ob_excess(
        p["unit"],
        p["ob"],
        set(a.nat_codes)
        ),
    "audit-batch": lambda a, p: scan_and_evaluate_unit_files(
        a.data_dir,
        a.active_only,
        a.fix_ghosts
        ),
    "calc-support": lambda a, p: calc_unit_support(
        p["ob"],
        p["unit"],
        p["ground"],
        a.target_uid
        ),
    "gen-inventory": lambda a, p: count_global_unit_inventory(
        p["unit"],
        p["ground"],
        a.nat_codes
        ),
    "gen-orphans": lambda a, p: find_orphaned_obs(
        p["ob"],
        p["unit"],
        a.nat_codes
        ),
    "gen-groups": lambda a, p: group_units_by_ob(
        p["unit"],
        a.active_only,
        a.nat_codes
        ),
    "gen-chains": lambda a, p: generate_ob_chains(
        p["ob"],
        a.csv_out or "",
        a.txt_out or "",
        a.nat_codes
        ),

    "scan-ob": lambda a, p: scan_ob_for_ground_elem(
        p["ob"],
        a.target_wid
        ),
    "scan-unit": lambda a, p: scan_unit_for_ground_elem(
        p["unit"],
        p["ground"],
        p["ob"],
        a.target_wid,
        a.num_squads
        ),
    "scan-excess": lambda a, p: handle_scan_excess(p, a),
    "scan-unused": lambda a, p: identify_unused_devices(
        p["ground"],
        p["aircraft"],
        p["device"],
        a.device_type
        ),

    "mod-compact-wpn": lambda a, p: remove_ground_weapon_gaps(
        p["ground"]
        ),

    "mod-reorder-ob": lambda a, p: reorder_ob_squads(
        p["ob"],
        a.target_ob_id,
        a.target_wid,
        a.target_slot
        ),
    "mod-reorder-unit": lambda a, p: reorder_unit_squads(
        p["unit"],
        a.target_uid,
        a.target_wid,
        a.target_slot
        ),
    "mod-replace-elem": lambda a, p: modify_unit_ground_element(
        p["unit"],
        a.old_wid,
        a.new_wid
        ),
    "mod-update-num": lambda a, p: modify_unit_squads(
        p["unit"],
        a.target_ob_id,
        a.target_wid,
        a.old_num_s,
        a.new_num_s
        )
}

def main() -> None:
    """Main execution loop using a Dispatch Map."""

    parser = setup_parsers()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Path resolution assumed from existing environment context
    paths = resolve_paths(args.data_dir)

    try:
        if args.command in COMMAND_MAP:
            log.info("Executing: %s", args.command)
            COMMAND_MAP[args.command](args, paths)
            log.info("Successfully completed %s", args.command)
    except DataIntegrityError as e:
        log.error("Data Integrity Error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        log.error("Missing CSV file: '%s'", e)
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
