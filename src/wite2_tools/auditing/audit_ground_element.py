import os

# Internal package imports
from wite2_tools.constants import MAX_GROUND_MEN, GND_COL
from wite2_tools.utils.logger import get_logger
from wite2_tools.utils.lookups import get_ground_elem_class_name
from wite2_tools.generator import read_csv_list_generator

# Initialize the log for this specific module
log = get_logger(__name__)


def audit_ground_element_csv(ground_file_path: str) -> int:
    """
    Scans a _ground CSV file to ensure 'type' IDs are valid and
    logical based on the ground_element_type_lookup.
    """
    if not os.path.exists(ground_file_path):
        log.error("Audit failed: File not found at %s", ground_file_path)
        return -1

    issues_found : int = 0

    seen_ground_ids: set[int] = set()

    try:
        file_name = os.path.basename(ground_file_path)
        log.info("--- Starting Ground Element Audit: '%s' ---", file_name)

        # Initialize the generator
        ground_gen = read_csv_list_generator(ground_file_path)

        # Skip the first yield (which returns the DictReader object itself)
        next(ground_gen)

        # The generator automatically unpacks row_idx and row dictionary
        for _, row in ground_gen:
            row_len : int = len(row)
            ground_id = int(row[GND_COL.ID] or '0') # 1st 'id' column
            ground_name = row[GND_COL.NAME] # 'name' column

            # 1. Uniqueness Check
            if ground_id != 0 and ground_id in seen_ground_ids:
                log.error("ID %d: Duplicate Ground Element ID (%s)",
                          ground_id, ground_name)
                issues_found += 1
            else:
                seen_ground_ids.add(ground_id)

            # 2. Type Validation
            raw_type = row[GND_COL.TYPE] # 'type' column
            if raw_type is None:
                log.error("ID %d (%s): Missing 'type' column value.", ground_id, ground_name)
                issues_found += 1
                continue

            try:
                ground_type_int = int(raw_type)
                if ground_type_int == 0:
                    continue
                element_class_name = get_ground_elem_class_name(ground_type_int)
                # Updated to match the "Unk " fallback in lookups.py
                if "Unk" in element_class_name:
                    log.warning("ID %d (%s): uses undefined Type %d",
                                ground_id, ground_name, ground_type_int)
                    issues_found += 1
                elif element_class_name == "Blank":
                    log.debug("ID %d (%s): Assigned to reserved/blank Type %d",
                              ground_id, ground_name, ground_type_int)
                else:
                    log.debug("ID %d (%s): Validated as %s",
                              ground_id, ground_name, element_class_name)

                # following is to account for tests using weird-sized rows
                if GND_COL.SIZE > row_len:
                    continue
                ground_size = int(row[GND_COL.SIZE] or '0') # 'size' column
                if ground_size == 0:
                    log.warning("ID %d (%s): %s has ZERO size",
                                ground_id, ground_name, element_class_name)
                    issues_found += 1

                ground_men = int(row[GND_COL.MEN] or '0') # 'men' column
                if ground_men == 0:
                    log.warning("ID %d (%s): %s has no men assigned",
                                ground_id, ground_name, element_class_name)
                    issues_found += 1

                elif ground_men > MAX_GROUND_MEN:
                    log.warning("ID %d (%s): %s has %d > %d men assigned",
                                ground_id, ground_name, element_class_name, ground_men, MAX_GROUND_MEN)
                    issues_found += 1

            except ValueError:
                log.error("ID %d (%s): 'type' value '%s' is not a valid integer.",
                          ground_id, ground_name, raw_type)
                issues_found += 1

        log.info("--- Audit Complete: %d issues identified ---", issues_found)
        return issues_found

    except (OSError, IOError, ValueError, KeyError, IndexError) as e:
        log.exception("An unexpected error occurred during the audit: %s", e)
        return -1


