"""
Character Encoding Detection Utility
====================================

This utility safely scans a file to detect its character encoding (e.g.,
ISO-8859-1, UTF-8). This is particularly useful when dealing with modded or
older WiTE2 CSV files to prevent parsing errors.

Command Line Usage:
    python -m wite2_tools.cli detect-encoding file_path

Example:
    $ python -m wite2_tools.cli detect-encoding "C:\\My Mods\\_ground.csv"
    Detects Encoding for _ground.csv: ISO-8859-1
"""
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']
