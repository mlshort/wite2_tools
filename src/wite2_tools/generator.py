"""
CSV Generator Utilities
=======================

This module provides generator functions for efficiently reading and iterating
over CSV files. It is designed to handle large datasets by yielding rows
lazily rather than loading the entire file into memory.

The module supports two modes of reading:
1.  **List-based reading**: Returns rows as lists of strings, useful for
    sequential data processing.
2.  **Dictionary-based reading**: Returns rows as dictionaries mapped to
    header names, useful for column-agnostic data access.

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
from typing import Generator, Union, List, Dict
from collections.abc import Iterator
from dataclasses import dataclass

# Internal package imports
from .config import ENCODING_TYPE

@dataclass
class CSVStream:
    fieldnames: list[str]
    rows: Iterator[tuple[int, dict[str, str]]]

def get_csv_dict_stream(filename: str,
                        enum_start: int = 1) -> CSVStream:

    file = open(filename, mode='r', newline='', encoding=ENCODING_TYPE)
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames or []

    def row_gen() -> Iterator[tuple[int, dict[str, str]]]:
        try:
            for index, row in enumerate(reader, start=enum_start):
                yield index, row
        finally:
            file.close()

    return CSVStream(fieldnames=list(fieldnames), rows=row_gen())

def read_csv_list_generator(
    filename: str,
    enum_start: int = 1
) -> Generator[Union[List[str], tuple[int, List[str]]], None, None]:
    """
    Yields the header list first, then index and row lists.
    """
    with open(filename, mode='r', newline='', encoding=ENCODING_TYPE) as file:
        reader = csv.reader(file)

        # Manually extract the first row as the header
        try:
            header: List[str] = next(reader)
        except StopIteration:
            return  # Handle empty file

        # Yield the header list (replaces the DictReader object for fieldnames
        # access)
        yield header

        # Yield rows as lists with their index
        for index, row in enumerate(reader, start=enum_start):
            yield index, row


def read_csv_dict_generator(
    filename: str,
    enum_start: int = 1
) -> Generator[Union[csv.DictReader, tuple[int, Dict[str, str]]], None, None]:
    """
    Yields the DictReader object first, then index, row dictionaries.
    """
    with open(filename, mode='r', newline='', encoding=ENCODING_TYPE) as file:
        reader = csv.DictReader(file)

        # Yield the reader for fieldnames access
        yield reader

        for index, row in enumerate(reader, start=enum_start):
            yield index, row
