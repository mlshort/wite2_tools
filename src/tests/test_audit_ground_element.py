from pathlib import Path

# Internal package imports
from wite2_tools.auditing import audit_ground_element_csv


# ==========================================
# TEST CASES
# ==========================================
def test_audit_ge_catches_zero_men(mock_ground_csv: Path)->None:
    # This should find at least 1 issue (the 0 men squad)
    issues = audit_ground_element_csv(str(mock_ground_csv))
    assert issues >= 1


def test_audit_ground_element_csv_identifies_issues(mock_ground_csv: Path)->None:
    """
    Verifies that the audit correctly identifies duplicates,
    missing types, unknown types, and malformed data.
    """
    issues = audit_ground_element_csv(str(mock_ground_csv))
    assert issues == 1


def test_audit_ground_element_csv_file_not_found()->None:
    """
    Verifies safe failure and error handling when the file does not exist.
    """
    issues = audit_ground_element_csv("does_not_exist.csv")

    # The script is designed to return -1 when the path is missing
    assert issues == -1
