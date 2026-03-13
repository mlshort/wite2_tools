"""
Data Parsing and Sanitization Utilities
=======================================

Provides centralized, exception-safe type-casting functions designed
specifically to handle the malformed, empty, or whitespace-padded data
frequently encountered in War in the East 2 (WiTE2) CSV files.
"""
from typing import Optional, List


def parse_int(value: Optional[str], default: int = 0) -> int:
    """
    Safely parses a string into an integer.

    Designed to handle the malformed, empty, or whitespace-padded data
    frequently encountered in War in the East 2 (WiTE2) CSV files.

    Args:
        value (Optional[str]): The string value to parse, typically from a
            CSV cell.
        default (int, optional): The fallback integer to return if the string
            is None, empty, or malformed. Defaults to 0.

    Returns:
        int: The parsed integer, or the default value if a ValueError occurs.
    """
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def parse_row_int(row: List[str], offset: int, default: int = 0) -> int:
    """
    Safely extracts an integer from a CSV row.
    Handles truncated rows and empty cells by returning the default.
    Raises ValueError for malformed strings (like floats or text).
    """
    try:
        val_str = row[offset].strip()

        # Safely handle the most common CSV "blank" scenario
        if not val_str:
            return default

        # If it's a float like "12.5" or text like "abc", this will raise a
        # ValueError and bubble up to the caller.
        return int(val_str)

    except IndexError:
        # The row is truncated (missing columns at the end)
        return default


def parse_str(value: Optional[str], default: str = "") -> str:
    """
    Safely parses a CSV cell into a cleaned string.

    Args:
        value (Optional[str]): The string value to parse.
        default (str, optional): The fallback string to return if the input is
                None. Defaults to "".

    Returns:
        str: A whitespace-stripped version of the input string, or the default
                value if the input is None.
    """
    if value is None:
        return default

    return str(value).strip()


def parse_row_str(row: List[str], offset: int, default: str = "") -> str:
    """
    Safely extracts and cleans a string from a CSV row list.
    Handles truncated rows and empty cells by returning the default value.
    """
    try:
        val_str = row[offset].strip()

        # If the cell was empty or just contained spaces, return the default
        if not val_str:
            return default

        return val_str

    except IndexError:
        # The row is truncated
        return default
