import pytest
from wite2_tools.utils.formatting import (
    format_ref,
    format_coords,
    format_header,
    format_list_item,
    completion_msg,
    audit_msg,
    BULLET,
    SUCCESS_MARK,
    CRITICAL_MARK
)

def test_format_ref():
    """Verifies standardized resource identifiers with and without names."""
    # Test with name
    assert format_ref("UID", 100, "1st Panzer") == "UID[100] (1st Panzer)"
    # Test without name
    assert format_ref("WID", 42) == "WID[42]"
    # Test different object type
    assert format_ref("TOE", 33, "Inf Div") == "TOE[33] (Inf Div)"

def test_format_coords():
    """Verifies that map coordinates are formatted as (X, Y)."""
    assert format_coords(300, 150) == "(300, 150)"
    assert format_coords(0, 0) == "(0, 0)"

def test_format_header():
    """Verifies that headers are uppercase and wrapped in equal signs."""
    header = format_header("audit report")
    assert "AUDIT REPORT" in header
    assert "====================" in header

def test_format_list_item():
    """Verifies standard list item indentation and bullets."""
    assert format_list_item("Item 1") == f"{BULLET}Item 1"

def test_completion_msg():
    """Verifies the standardized success message for modifiers."""
    msg = completion_msg("Repair", 5, "_unit.csv")
    assert SUCCESS_MARK in msg
    assert "Repair complete" in msg
    assert "5 matches/rows processed" in msg
    assert "in _unit.csv" in msg

def test_audit_msg():
    """Verifies audit results for both success and failure states."""
    # Test Success (0 issues)
    success = audit_msg("_ob.csv", 0, 100)
    assert SUCCESS_MARK in success
    assert "Audit Passed" in success
    assert "0 issues identified (100 items checked)" in success

    # Test Failure (n issues)
    failure = audit_msg("_ground.csv", 3, 50)
    assert "⚠️" in failure or "❌" in failure  # Depending on mark logic
    assert "Audit Failed" in failure
    assert "3 issues identified (50 items checked)" in failure