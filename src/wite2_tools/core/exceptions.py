"""
Custom Exceptions for WiTE2 Tools
=================================
Centralized error types for data integrity, parsing, and modding logic.
"""
from typing import Optional

class WiTE2Error(Exception):
    """Base class for all exceptions in the wite2_tools package."""


class DataIntegrityError(WiTE2Error):
    """
    Exception raised for errors in the WiTE2 CSV data integrity.

    Attributes:
        message (str): Explanation of the error.
        file_name (str, optional): The CSV file where the error was found.
        row_index (int, optional): The specific line number in the CSV.
    """
    def __init__(self, message: str,
                 file_name: Optional[str] = None,
                 row_index: Optional[int] = None):
        self.message = message
        self.file_name = file_name
        self.row_index = row_index

        # Format a helpful string for logging
        full_msg = message
        if file_name:
            full_msg += f" [File: {file_name}]"
        if row_index is not None:
            full_msg += f" [Row: {row_index}]"

        super().__init__(full_msg)