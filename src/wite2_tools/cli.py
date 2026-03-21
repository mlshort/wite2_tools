"""
WiTE2 Utility Command-Line Interface (CLI)
==========================================

A unified command-line tool for modifying, auditing, and analyzing War in the
East 2 (WiTE2) scenario data files. This script acts as the main entry point
for executing targeted modifications, generating analytics, and running audits.

Available Commands:
-------------------
[Configuration]
* config           : Manage settings.ini default paths and scenario prefixes.

[Auditing]
* audit-ob         : Audits _ob.csv referential integrity.
* audit-ground     : Audits _ground.csv to ensure type IDs are valid.
* audit-unit       : Audits _unit.csv data integrity and referential links.
* audit-toe        : Audits _unit.csv exceeding TOE(OB) limits.
* audit-batch      : Scans a folder for CSV files and runs batch consistency checks.

[Scanning]
* scan-ob          : Scans TOE(OB)s for a specific Ground Element WID.
* scan-unit        : Scans Units for a specific Ground Element WID.
* scan-excess      : Scans units for excess supplies (ammo, fuel, etc.).
* scan-unused      : Find unused devices in the ground/aircraft files.

[Modifiers]
* mod-compact-wpn  : Removes empty weapon slots and shifts remaining up.
* mod-reorder-ob   : Moves a Ground Element to a new slot index for an TOE(OB).
* mod-reorder-unit : Moves a Ground Element to a new slot index for a Unit.
* mod-replace-elem : Globally replaces a specific Ground Element WID.
* mod-update-num   : Conditionally updates unit squad counts.

[Generators / Core Analytics]
* calc-support     : Calculate unit support and need.
* gen-inventory    : Counts global unit inventory (with nat filters).
* gen-orphans      : Find units with missing TOE(OB) references.
* gen-groups       : Groups active units by their assigned TOE(OB) ID.
* gen-chains       : Trace TOE(OB) upgrade chains to CSV/TXT outputs.

Note: Target file paths are resolved automatically from the provided
      `--data-dir` (or `-d`) argument. It defaults to the current directory.
"""

import argparse
import configparser
import os
import sys
from collections.abc import Callable

# Project Imports
from wite2_tools.utils import get_logger
from wite2_tools.scanning.scan_unit_for_excess import (
    scan_units_for_excess_ammo,
    scan_units_for_excess_fuel,
    scan_units_for_excess_supplies,
    scan_units_for_excess_vehicles
)
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
    audit_batch
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


# Initialize the log for this specific module
log = get_logger(__name__)


def get_config_defaults() -> dict[str, str]:
    """
    Reads data_dir and scenario_name from settings.ini.
    Returns a dictionary of defaults.
    """
    config = configparser.ConfigParser()
    defaults = {"data_dir": ".", "scenario_name": ""}
    if os.path.isfile(CONFIG_FILE_NAME):
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
    """
    Retrieves the scenario name from the config file.
    """
    scen_name = ""
    config = configparser.ConfigParser()
    if os.path.isfile(CONFIG_FILE_NAME):
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
    if os.path.isfile(CONFIG_FILE_NAME):
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

# pylint: disable=too-many-locals,too-many-statements
def setup_parsers() -> argparse.ArgumentParser:
    """
    Configures the argument parsing for all subcommands.
    """
    # Load the default path from config for the help text and default value
    defaults = get_config_defaults()
    default_path = defaults.get("data_dir", ".")

    # =========================
    # PARENT PARSERS
    # =========================
    base_parser = argparse.ArgumentParser(
        description=__doc__,  # This pulls your nice docstring from the top of the file
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    base_parser.add_argument(
        "-d", "--data-dir", default=default_path,
        help=f"Directory containing the WiTE2 CSV files "
             f"(Current default: {default_path})."
    )

    base_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug logging output."
    )

    subparsers = base_parser.add_subparsers(
        dest="command",
        required=False,
        title="subcommands",
        metavar="<command>" # Cleans up the ugly {config,audit,...} list
    )

    def add_nat_argument(p:argparse.ArgumentParser)->None:
        p.add_argument(
            "--nat", dest="nat_codes", type=int, nargs="+", default=[1],
            help="Nationality codes to filter (default: 1)"
        )

    #=========================
    # CONFIG COMMANDS
    #=========================
    p_conf = subparsers.add_parser("config",
                                   help="Manage settings.ini")
    p_conf.add_argument("--set-path", help="Set default data directory")
    p_conf.add_argument("--set-scenario", help="Set scenario prefix")

    # =========================
    # AUDIT COMMANDS
    # =========================

    # TODO audit-devices is not currently active
    #p_audit_devices = subparsers.add_parser("audit-devices",
    #    help="Identify devices defined in ground elements but never used in Units or OBs.")
    #add_common(p_audit_devices)

    subparsers.add_parser("audit-ob", help="Audit _ob.csv")

    subparsers.add_parser("audit-ground",
                          help="Audit _ground.csv")

    p_au = subparsers.add_parser("audit-unit",
                                 help="Audit _unit.csv")
    p_au.add_argument("--active-only", action="store_true", default=True)
    p_au.add_argument("--fix-ghosts", action="store_true")
    p_au.add_argument("--relink-orphans", action="store_true")
    p_au.add_argument("--fallback-hq", type=int, default=0)

    p_toe = subparsers.add_parser("audit-toe",
                                  help="Audits _unit.csv exceeding TOE(OB) limits")
    add_nat_argument(p_toe)

    p_ab = subparsers.add_parser("audit-batch",
                                 help="Scans a folder for CSV files and runs consistency checks")
    p_ab.add_argument("--active-only", action="store_true", default=True)

    # =========================
    # ANALYTIC COMMANDS
    # =========================
    p_calc = subparsers.add_parser("calc-support",
                                   help="Calculate unit support and need")
    p_calc.add_argument("target_uid", type=int,
                        help="Target Unit ID")


    # =========================
    # GENERATION COMMANDS
    # =========================
    p_inv = subparsers.add_parser("gen-inventory",
                                  help="Counts global unit inventory (with nat filters)")
    add_nat_argument(p_inv)

    p_orphans = subparsers.add_parser("gen-orphans",
                                      help="Find units with missing TOE(OB) references")
    add_nat_argument(p_orphans)

    p_groups = subparsers.add_parser("gen-groups",
                                     help="Group units by their assigned TOE(OB) ID")
    p_groups.add_argument("--active-only", action="store_true")
    add_nat_argument(p_groups)

    p_chains = subparsers.add_parser("gen-chains",
                                     help="Trace the TOE(OB)'s upgrade paths")
    p_chains.add_argument("--csv-out", help="Path for CSV output")
    p_chains.add_argument("--txt-out", help="Path for TXT report")
    add_nat_argument(p_chains)

    # =========================
    # SCANNING COMMANDS
    # =========================
    p_scan_ob = subparsers.add_parser("scan-ob",
                                      help="Scans TOE(OB)s for a specific Ground Element WID")
    p_scan_ob.add_argument("target_wid", type=int, help="Target Ground Element WID")
    add_nat_argument(p_scan_ob)

    p_excess = subparsers.add_parser("scan-excess",
                                     help="Scans units for excess resources")
    p_excess.add_argument("resource",
                          nargs="?",
                          choices=['a','f','s','v'],
                          default='a',
                          help="(a)mmo/(f)uel/(s)upplies or (v)ehicles")
    p_excess.add_argument("ratio",
                          nargs="?",
                          type=float,
                          default=5.0,
                          help="Ratio threshold (default: 5.0)")

    p_sunused = subparsers.add_parser("scan-unused",
                                      help="Find unused devices")
    p_sunused.add_argument("device_type", type=int)
    add_nat_argument(p_sunused)

    # =========================
    # MODIFIER COMMANDS
    # =========================
    p_reord = subparsers.add_parser("mod-reorder-unit",
                                    help="Move's a Unit's Ground Element to a new slot"
    )
    p_reord.add_argument("target_uid", type=int)
    p_reord.add_argument("target_wid", type=int)
    p_reord.add_argument("target_slot", type=int)

    subparsers.add_parser("mod-compact-wpn",
                          help="Compact weapon gaps")

    p_reob = subparsers.add_parser("mod-reorder-ob",
                                   help="Moves a TOE(OB)'s squad to a new slot")
    p_reob.add_argument("target_ob_id", type=int)
    p_reob.add_argument("target_wid", type=int)
    p_reob.add_argument("target_slot", type=int)

    p_repl = subparsers.add_parser("mod-replace-elem",
                                   help="Globally replace a Ground Element WID")
    p_repl.add_argument("old_wid", type=int)
    p_repl.add_argument("new_wid", type=int)

    p_upd = subparsers.add_parser("mod-update-num",
                                  help="Update squad count")
    p_upd.add_argument("--ob-id", dest="target_ob_id", type=int, required=True)
    p_upd.add_argument("--wid", dest="target_wid", type=int, required=True)
    p_upd.add_argument("--old", dest="old_num_s", type=int, required=True)
    p_upd.add_argument("--new", dest="new_num_s", type=int, required=True)

    return base_parser


def handle_scan_excess(p: dict[str, str], a: argparse.Namespace) -> None:
    """
    Routes the scan-excess command to the correct resource scanner.
    """
    resource = a.resource.lower()
    ratio = a.ratio
    unit_path = p["unit"]

    if resource == "a":
        scan_units_for_excess_ammo(unit_path, ratio)
    elif resource == "s":
        scan_units_for_excess_supplies(unit_path, ratio)
    elif resource == "f":
        scan_units_for_excess_fuel(unit_path, ratio)
    elif resource == "v":
        scan_units_for_excess_vehicles(unit_path, ratio)
    else:
        # Fallback if the user types an unsupported resource
        print(f"Error: Unknown resource type '{resource}'."
               "Choose from: (a)mmo, (s)upplies, (f)uel, (v)ehicles.")

# Dispatch Map replaces the massive if/elif chain
# Lambda delayed execution allows for fast startup and lazy imports
# Dispatch Map (To be expanded)
# -------------------------------------------------------------------------
COMMAND_MAP: dict[str, Callable] = {
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
        p["ground"],
        set(a.nat_codes)
        ),
    "audit-batch": lambda a, p: audit_batch(
        a.data_dir,
        a.active_only
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

paths: dict[str,str] = {}
# args = None

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
            log.debug("Executing: %s", args.command)
            COMMAND_MAP[args.command](args, paths)
            log.debug("Successfully completed %s", args.command)

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
