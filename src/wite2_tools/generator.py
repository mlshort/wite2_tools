"""
CSV Generator Utilities
=======================

This module provides generator functions for efficiently reading and iterating
over CSV files. It is designed to handle large datasets by yielding rows
lazily rather than loading the entire file into memory.

Configuration
-------------
The module relies on `ENCODING_TYPE` imported from the internal `.config`
package to ensure consistent file encoding handling across the application.

Functions
---------
* `read_csv_list_generator`: Yields the header row, followed by enumerated
    tuples of (index, row_list).
* `read_csv_dict_generator`: Yields the DictReader object
    (for metadata access), followed by enumerated tuples of (index, row_dict).
"""
import csv
from collections.abc import Iterator
from dataclasses import dataclass

# Internal package imports
from .config import ENCODING_TYPE

@dataclass
class CSVListStream:
    """
    A data class representing a streamed CSV file.

    Attributes:
        header (list[str]): The column headers extracted from the first row of the CSV.
        rows (Iterator[tuple[int, list[str]]]): A lazy iterator that yields tuples.
            Each tuple contains the row index and the row data (as a list of strings).
    """
    header: list[str]
    rows: Iterator[tuple[int, list[str]]]


def get_csv_list_stream(filename: str,
                        enum_start: int = 1) -> CSVListStream:
    """
    Opens a CSV file and creates a streamable data structure of its contents.

    This function reads the first row as the header and creates a lazy generator
    for the remaining rows. The file remains open while the generator is consumed
    and is safely closed in a `finally` block once the iterator is exhausted.
    Handles empty files gracefully.

    Args:
        filename (str): The path to the CSV file to open.
        enum_start (int, optional): The starting index for row enumeration.
                                    Defaults to 1.

    Returns:
        CSVListStream: An object containing the header list and the row iterator.
            If the file is completely empty, returns an empty header and an empty
            iterator.

    Raises:
        OSError: If there is a failure opening the file
            (e.g., file not found, permission denied).
    """
    # throws OSError upon failure
    file = open(filename, mode='r', newline='', encoding=ENCODING_TYPE)
    reader = csv.reader(file)
    try:
        header = next(reader) # Error check: handle StopIteration here
    except StopIteration:
        file.close()
        return CSVListStream(header=[], rows=iter([]))

    def row_gen()->Iterator[tuple[int, list[str]]]:
        """
        Generates enumerated rows from the CSV reader and ensures the file is closed.

        Yields:
            tuple[int, list[str]]: The row index and the row contents.
        """
        try:
            for index, row in enumerate(reader, start=enum_start):
                yield index, row
        finally:
            file.close() # Clean up resource

    return CSVListStream(header=header, rows=row_gen())
