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
  `get_csv_dict_stream`, preventing out-of-memory errors when handling
  massive game files.
* Callback-Driven Logic: Accepts a `row_processor` callback function. This
  cleanly separates the file handling boilerplate from the actual data
  mutation logic injected by individual modifier scripts.
"""
import csv
import os
from tempfile import NamedTemporaryFile
from collections.abc import Callable
from typing import cast

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.generator import get_csv_list_stream
from wite2_tools.utils import get_logger

# Initialize the log for this specific module
log = get_logger(__name__)


def process_csv_in_place(file_path: str,
                         row_processor: Callable[[list, int],
                                                 tuple[list, bool]]) -> tuple[int, int]:
    """
    A boilerplate wrapper that safely processes a CSV file in-place using a
    temporary file and a List Stream (more memory efficient).

    Args:
        file_path: The absolute path to the CSV file.
        row_processor: A callback function that takes (row_list, row_index) and
                       returns a tuple of (modified_row_list, was_modified_bool).
    Returns:
        A tuple containing (total_rows_processed, total_rows_updated).
    """
    if not os.path.isfile(file_path):
        log.error("File Error: The file '%s' was not found.", file_path)
        return 0, 0

    processed:int = 0
    updated:int = 0
    # Use NamedTemporaryFile to ensure we don't corrupt the source if the script crashes
    temp_file = NamedTemporaryFile(mode='w', delete=False,
                                   dir=os.path.dirname(file_path),
                                   newline='', encoding=ENCODING_TYPE)

    try:
        stream = get_csv_list_stream(file_path)

        with temp_file as outfile:
            writer = csv.writer(outfile)

            # List streams usually include the header as the first yielded row or
            # through the stream's row generator. We iterate through the stream:
            for item in stream.rows:
                processed += 1

                # Explicitly cast for type checkers: (row_index, row_data_list)
                row_idx, row = cast(tuple[int, list], item)

                # Pass the list to the custom logic callback
                row, was_modified = row_processor(row, row_idx)

                if was_modified:
                    updated += 1

                writer.writerow(row)

        if updated == 0:
            log.warning("Process complete: No matches found or "
                        "no changes made in '%s'.",
                        os.path.basename(file_path))
            os.remove(temp_file.name)
        else:
            log.info("Success: Processing complete. Total rows updated: %d.",
                     updated)
            # Atomic swap of the temp file with the original file
            os.replace(temp_file.name, file_path)

    except (OSError, IOError, ValueError, KeyError, TypeError) as e:
        log.exception("Critical error during file processing: %s", e)
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

    return processed, updated
