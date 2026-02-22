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
import csv
import os
from typing import Optional, Union, Iterable, cast

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.parsing import (
    parse_int,
    parse_str
)

# Initialize the log for this specific module
log = get_logger(__name__)


def generate_ob_chains(
    ob_file_path: str,
    csv_output_path: str,
    txt_output_path: str,
    nation_id: Optional[Union[int, str, Iterable[Union[int, str]]]] = None
) -> int:
    """
    Generates TOE(OB) upgrade chains, optionally filtered by a specific
    nationality code.

    :param ob_file_path: Path to the source _ob.csv
    :param csv_output_path: Path to save the CSV results
    :param txt_output_path: Path to save the text results
    :param nation_id: Integer or list of integers representing the 'nat'
                      column value to filter by.
    :return: The total number of chains generated.
    """
    ob_id_to_name_map: dict[int, str] = {}
    ob_id_to_upgrade_map: dict[int, int] = {}
    all_ob_ids: set[int] = set()
    ob_upgrade_ids: set[int] = set()

    # Standardize nation_id to a set for efficient lookup
    if nation_id is not None:
        if isinstance(nation_id, (int, str)):
            nat_filter = {int(nation_id)}
        else:
            nat_filter = {int(n) for n in nation_id}
    else:
        nat_filter = None

    log.info("Starting TOE(OB) Upgrade Chain Generation from '%s'",
             os.path.basename(ob_file_path))

    # 1. Read the input _ob CSV and build mappings
    data_gen = read_csv_dict_generator(ob_file_path)
    next(data_gen)  # Skip DictReader object

    for item in data_gen:
        # Cast the yielded item to satisfy static type checkers
        _, row = cast(tuple[int, dict], item)

        try:
            # Early Exit: Filter by nationality
            ob_nation_id = parse_int(row.get('nat'), 0)
            if nat_filter is not None and ob_nation_id not in nat_filter:
                continue

            ob_type = parse_int(row.get('type'), 0)
            if ob_type == 0:
                continue

            ob_id = parse_int(row.get('id'), 0)
            ob_upgrade_id = parse_int(row.get('upgrade'), 0)

            # Combine ob_name and ob_suffix
            ob_name = parse_str(row.get('name'), '')
            ob_suffix = parse_str(row.get('suffix'), '')
            ob_full_name = f"{ob_name} {ob_suffix}"

            ob_id_to_name_map[ob_id] = ob_full_name
            all_ob_ids.add(ob_id)

            # If an upgrade exists, map it and track it as a 'target'
            if ob_upgrade_id != 0:
                ob_id_to_upgrade_map[ob_id] = ob_upgrade_id
                ob_upgrade_ids.add(ob_upgrade_id)

        except (ValueError, KeyError):
            # Skip rows with invalid IDs or missing columns
            continue

    # 2. Identify Roots (IDs that are not the destination of an upgrade)
    roots: list[int] = sorted(list(all_ob_ids - ob_upgrade_ids))

    # 3. Trace the chains
    chains_list = []
    for root in roots:
        # Filter out empty entries or structural spacers
        if not ob_id_to_name_map.get(root):
            if root not in ob_id_to_upgrade_map:
                continue

        chain = []
        curr = root
        visited: set[int] = set()  # Safety check for infinite loops in data

        while curr != 0 and curr in ob_id_to_name_map:
            if curr in visited:
                chain.append(f"{curr} (LOOP)")
                log.warning("Infinite loop detected in upgrade "
                            "chain at TOE(OB) ID %d", curr)
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
            f.write(str(chain_info['chain_str']) + "\n")

    log.info("Successfully generated %d upgrade chains.", len(chains_list))
    if nation_id:
        log.debug("Filtered by nation_id: %s", nat_filter)

    return len(chains_list)
