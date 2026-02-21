"""
Data Parsing and Sanitization Utilities
=======================================

Provides centralized, exception-safe type-casting functions designed
specifically to handle the malformed, empty, or whitespace-padded data
frequently encountered in War in the East 2 (WiTE2) CSV files.
"""
from typing import Optional


def parse_int(value: Optional[str], default: int = 0) -> int:
    """
    Scans the _ground CSV file, identifies rows with gaps in their weapon
    slots, and shifts valid weapons left/up to fill those gaps.

    Args:
        ground_file_path (str): The absolute or relative path to the WiTE2
                _ground CSV file.

    Returns:
        int: The total number of Ground Elements that had their weapon slots
                compacted.
    """
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
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
