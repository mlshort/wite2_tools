"""
Type Parsing Utilities
======================

This module provides centralized, safe type-casting functions to handle
the often malformed or empty data found in WiTE2 CSV files.
"""
from typing import Optional


def parse_int(value: Optional[str], default: int = 0) -> int:
    """
    Safely parses a string into an integer.
    Returns the default value if the string is None, empty, or malformed.
    """
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default
