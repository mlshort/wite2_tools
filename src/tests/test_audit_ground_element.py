import csv

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing import audit_ground_element_csv
from wite2_tools.constants import GroundColumn

# ==========================================
# FIXTURES (Setup)
# ==========================================
@pytest.fixture
def mock_ground_csv(tmp_path):
    """
    Creates a mock ground element CSV that satisfies structural checks
    but contains exactly 4 logical errors.
    """
    csv_file = tmp_path / "mock_ground_audit.csv"

    def create_row(gid, name, gtype, men="10", size="1"):
        # Initialize a row with 25 columns to exceed REQUIRED_STAT_COLS (22)
        row = ["0"] * 25
        row[GroundColumn.ID] = str(gid)
        row[GroundColumn.NAME] = name
        row[GroundColumn.TYPE] = str(gtype)
        row[GroundColumn.MEN] = str(men)   # Index 19
        row[GroundColumn.SIZE] = str(size)  # Index 21
        return row

    header = ["id", "name", "cost", "type", "symbol", "rate", "range", "acc",
              "pen", "load", "ce", "fc", "face", "size_type", "class", "fire",
              "move", "ammo", "fuel", "men", "weight", "size", "trail", "load2",
              "end"]

    with open(csv_file, mode='w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.writer(f)
        writer.writerow(header)

        # Rows 1 & 2: Now valid because MEN and SIZE are > 0
        writer.writerow(create_row(100, "Panzer IV", 30, men="5", size="20"))
        writer.writerow(create_row(101, "Infantry", 1, men="10", size="1"))

        # ISSUE 1: DUPLICATE ID
        writer.writerow(create_row(101, "Infantry Clone", 1))

        # ISSUE 2: MISSING TYPE
        row4 = create_row(102, "Ghost Tank", "")
        row4[GroundColumn.TYPE] = ""
        writer.writerow(row4)

        # ISSUE 3: UNKNOWN TYPE 9999
        writer.writerow(create_row(103, "Future Laser", 9999))

        # ISSUE 4: INVALID TYPE STRING
        writer.writerow(create_row(104, "Bad Data", "INVALID"))

    return str(csv_file)

# ==========================================
# TEST CASES
# ==========================================


def test_audit_ground_element_csv_identifies_issues(mock_ground_csv):
    """
    Verifies that the audit correctly identifies duplicates,
    missing types, unknown types, and malformed data.
    """
    issues = audit_ground_element_csv(mock_ground_csv)

    # Now that the rows are properly padded, the "Insufficient columns"
    # warnings will disappear, and the count should return to 4.
    assert issues == 4


def test_audit_ground_element_csv_file_not_found():
    """
    Verifies safe failure and error handling when the file does not exist.
    """
    issues = audit_ground_element_csv("does_not_exist.csv")

    # The script is designed to return -1 when the path is missing
    assert issues == -1
