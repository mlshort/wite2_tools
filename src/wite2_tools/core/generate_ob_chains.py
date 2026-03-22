"""
Order of Battle TOE(OB) Upgrade Chain Generator
===========================================

This module parses the War in the East 2 (WiTE2) `_ob.csv` file to map and
generate complete chronological upgrade paths (chains) for TOE(OB) templates.

It works by identifying "Root" OBs—templates that are never the destination of
an upgrade—and recursively tracing their 'upgrade' column references until the
end of the war is reached.

Core Features:
--------------
* Full Chain Tracing: Generates easy-to-read strings mapping the entire
  evolution of a unit structure (e.g., `[41] 1941 Inf Div -> [42] 1942 Inf
  Div -> [43] 1943 Inf Div`).
* Nationality Filtering: Can restrict the chain generation to specific nations
  (e.g., Germany) using the `nation_id` parameter.
* Loop Protection: Implements a visited-set safety check to prevent infinite
  loops in the event of circular upgrade references in the game data.
* Dual Export: Outputs the results simultaneously to both a structured CSV
  file and a plaintext file for easy searching.

Main Functions:
---------------
* generate_ob_chains : The primary function that parses the data, traces the
                       chains, and writes the exports to the specified file
                       paths.

Command Line Usage:
    python -m wite2_tools.cli gen-chains [-h] [-d DATA_DIR] \
        [--csv-out PATH] [--txt-out PATH] [--nat-codes CODE [CODE ...]]

Arguments:
    csv_output_path (str): The destination path for the CSV output.
    txt_output_path (str): The destination path for the plaintext output.
    nat_codes (list of int, optional): Filter by nationality codes.

Example:
    $ python -m wite2_tools.cli gen-chains --nat-codes 1

    Generates and exports chronological TOE(OB) upgrade chains strictly
    for the German (Nat 1) faction.
"""
import os
import csv
from typing import Any

from wite2_tools.config import ENCODING_TYPE, NatData, normalize_nat_codes
from wite2_tools.utils import get_logger
from wite2_tools.generator import get_csv_list_stream, CSVListStream
from wite2_tools.models import (
    ObRow
)

log = get_logger(__name__)


def generate_ob_chains(
    ob_csv_path: str,
    csv_output_path: str,
    txt_output_path: str,
    nat_codes: NatData = None
) -> None:
    """
    Parses the _ob.csv file, identifies chronological upgrade sequences
    for units, and writes the mapped chains to both CSV and TXT files.

    Args:
        ob_csv_path (str): The filepath to the source _ob.csv.
        csv_output_path (str): The destination filepath for the CSV export.
        txt_output_path (str): The destination filepath for the TXT export.
        nation_id (int, optional): An integer ID filtering the output to a
                                   specific nationality. Defaults to -1 (All).
    """

    if not os.path.isfile(ob_csv_path):
        log.error("Error: The file '%s' was not found.", ob_csv_path)
        return

    nat_filter = normalize_nat_codes(nat_codes)

    # 1. First Pass: Map the upgrades and identify the targets
    ob_id_to_upgrade_map: dict[int, int] = {}
    ob_id_to_name_map: dict[int, str] = {}
    all_upgrade_targets: set[int] = set()

    ob_stream: CSVListStream = get_csv_list_stream(ob_csv_path)

    for _, row in ob_stream.rows:
        ob = ObRow(row)
        ob_id      = ob.ID
        ob_name    = ob.NAME
        ob_suffix  = ob.SUFFIX
        ob_nat     = ob.NAT
        ob_type    = ob.TYPE
        ob_upgrade = ob.UPGRADE
        full_name = f"{ob_name} {ob_suffix}"
        # Skip invalid or unassigned rows
        if ob_id == 0 or ob_name == "" or ob_type == 0:
            continue

        # Skip rows that don't match the requested Nation ID
        if nat_filter is not None and ob_nat not in nat_filter:
            continue

        # Add this OB to our master tracking dictionaries
        ob_id_to_name_map[ob_id] = full_name

        if ob_upgrade > 0:
            ob_id_to_upgrade_map[ob_id] = ob_upgrade
            all_upgrade_targets.add(ob_upgrade)

    # 2. Identify the "Roots" (OBs that are never upgraded INTO)
    root_obs: list[int] = []
    for ob_id in ob_id_to_upgrade_map:
        if ob_id not in all_upgrade_targets:
            root_obs.append(ob_id)

    log.debug("Found %d roots. Generating chains...", len(root_obs))

    # 3. Trace the paths from each root
    chains_list: list[dict[str, Any]] = []

    for root in root_obs:
        chain: list[int] = []
        curr = root
        visited: set[int] = set()

        # Follow the upgrade path until we hit 0 or a cycle
        while curr > 0:
            if curr in visited:
                log.warning("Cycle detected during OB path generation. Breaking "
                            "chain at TOE(OB) ID[%d]", curr)
                break

            chain.append(curr)
            visited.add(curr)
            curr = ob_id_to_upgrade_map.get(curr, 0)

        if chain:
            # Format the chain string
            chain_str = " -> ".join([
                f"[{cid}] {ob_id_to_name_map.get(cid, 'Unk')}"
                if isinstance(cid, int) else str(cid)
                for cid in chain
            ])
            chains_list.append({
                'root_id': root,
                'length': len(chain),
                'chain_str': chain_str
            })

    # 4. Write the results to the CSV output
    with open(csv_output_path, mode='w', newline='',
              encoding=ENCODING_TYPE) as f:
        writer = csv.writer(f)
        writer.writerow(['Root ID', 'Length', 'Chain'])
        for chain_info in chains_list:
            writer.writerow([chain_info['root_id'],
                             chain_info['length'], chain_info['chain_str']])

    # 5. Write the results to the Text output
    with open(txt_output_path, mode='w', encoding=ENCODING_TYPE) as f:
        for chain_info in chains_list:
            # We know chain_str is a string, so we can safely write it
            # ignoring the Any type hint required for the list of dicts above.
            f.write(f"{chain_info['chain_str']}\n")

    log.info("Success: Saved complete chronological OB mapping chains for "
             "%d roots.", len(chains_list))