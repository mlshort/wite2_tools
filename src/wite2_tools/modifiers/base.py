"""
CSV In-Place Processing Wrapper
===============================

This module provides the foundational file I/O wrapper used by data
modification scripts within the `wite2_tools` package. It is designed to
abstract away the boilerplate of safely reading, updating, and saving large
War in the East 2 (WiTE2) CSV files.

Core Features:
--------------
* Atomic File Replacement: Safely writes updates to a temporary file first
  using `NamedTemporaryFile`. The original file is only overwritten
  (`os.replace`) if the processing completes successfully and modifications
  were actually made, preventing data corruption. If no changes are made or
  an error occurs, the temporary file is cleanly discarded.
* Memory Efficiency: Streams data row-by-row using the
  `read_csv_dict_generator`, preventing out-of-memory errors when handling
  massive game files.
* Callback-Driven Logic: Accepts a `row_processor` callback function. This
  cleanly separates the file handling boilerplate from the actual data
  mutation logic injected by individual modifier scripts.
"""
import csv
import os
from tempfile import NamedTemporaryFile
from typing import Callable, Tuple, cast

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.generator import read_csv_dict_generator
from wite2_tools.utils.logger import get_logger

log = get_logger(__name__)

def process_csv_in_place(file_path: str,
                         row_processor: Callable[[dict, int], Tuple[dict, bool]]) -> int:
    """
    A boilerplate wrapper that safely processes a CSV file in-place using a temporary file.

    Args:
        file_path: The absolute path to the CSV file.
        row_processor: A callback function that takes (row_dict, row_index) and
                       returns a tuple of (modified_row_dict, was_modified_bool).
    Returns:
        The total number of rows that were modified.
    """
    if not os.path.exists(file_path):
        log.error("File Error: The file '%s' was not found.", file_path)
        return 0

    update_count = 0
    temp_file = NamedTemporaryFile(mode='w', delete=False, dir=os.path.dirname(file_path),
                                   newline='', encoding=ENCODING_TYPE)

    try:
        data_gen = read_csv_dict_generator(file_path)

        # 1. Extract and cast the reader object (first yield)
        reader_item = next(data_gen)
        reader = cast(csv.DictReader, reader_item)

        with temp_file as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames) # type: ignore
            writer.writeheader()

            # 2. Catch the item rather than unpacking it directly in the loop
            for item in data_gen:

                # 3. Explicitly tell the type checker this is now the tuple yield
                row_idx, row = cast(tuple[int, dict], item)

                # Pass the row to the custom logic callback
                row, was_modified = row_processor(row, row_idx)

                if was_modified:
                    update_count += 1

                writer.writerow(row)

        if update_count == 0:
            log.warning("Process complete: No matches found or no changes made in '%s'.", os.path.basename(file_path))
            os.remove(temp_file.name)
        else:
            log.info("Success: Processing complete. Total rows updated: %d.", update_count)
            os.replace(temp_file.name, file_path)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during file processing: %s", e)
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    return update_count
