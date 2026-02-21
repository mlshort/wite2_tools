import csv

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.audit_ground_element import audit_ground_element_csv

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    """Generates a mock _ground.csv with various logical edge cases."""
    file_path = tmp_path / "mock_ground_audit.csv"

    # Based on the script: ID is row[0], name is row[1], and type is row[3]
    headers = ["id", "name", "unknown2", "type", "unknown4"]

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        # Note: audit_ground_element_csv uses a list generator, not DictReader,
        # so we write standard lists instead of dictionaries.
        writer = csv.writer(f)
        writer.writerow(headers)

        # Row 1: Valid Ground Element
        # Type 13 = Md Tank
        writer.writerow(["100", "Panzer IV", "x", "13", "x"])

        # Row 2: Valid Ground Element
        # Type 1 = Rifle Squad
        writer.writerow(["101", "Infantry", "x", "1", "x"])

        # Row 3: Duplicate ID (101) -> Error
        writer.writerow(["101", "Infantry Clone", "x", "1", "x"])

        # Row 4: Missing/Empty Type -> ValueError
        writer.writerow(["102", "Ghost Tank", "x", "", "x"])

        # Row 5: Unknown Type (e.g. 9999) -> Warning (counted as issue)
        writer.writerow(["103", "Future Laser", "x", "9999", "x"])

        # Row 6: Non-Integer Type -> ValueError
        writer.writerow(["104", "Bad Data", "x", "INVALID", "x"])

        # Row 7: Valid Reserved/Blank (e.g., 0)
        writer.writerow(["105", "Placeholder", "x", "0", "x"])

    return str(file_path)


# ==========================================
# TEST CASES
# ==========================================


def test_audit_ground_element_csv_identifies_issues(mock_ground_csv):
    """
    Verifies that the audit correctly identifies duplicates,
    missing types, unknown types, and malformed data.
    """
    issues = audit_ground_element_csv(mock_ground_csv)

    # Expected Issues Identified (4 total):
    # 1. Row 3: Duplicate ID 101 triggers a uniqueness violation.
    # 2. Row 4: Empty string `""` fails `int()` conversion, causing a
    # ValueError.
    # 3. Row 5: Type 9999 triggers the "Unk Type" warning from lookups.py.
    # 4. Row 6: "INVALID" string fails `int()` conversion, causing a
    # ValueError.

    assert issues == 4


def test_audit_ground_element_csv_file_not_found():
    """
    Verifies safe failure and error handling when the file does not exist.
    """
    issues = audit_ground_element_csv("does_not_exist.csv")

    # The script is designed to return -1 when the path is missing
    assert issues == -1
