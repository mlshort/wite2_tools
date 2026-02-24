"""
Console Output Formatting Utilities
"""

# Standardized Symbols
BULLET = "  • "  # Standard list item [cite: 571-572]
SUCCESS_MARK = "✅ " # Successful operation completion
ISSUE_MARK = "⚠️ "   # Minor warning or logical anomaly
CRITICAL_MARK = "❌ " # Severe error or referential break [cite: 575]


def format_header(title: str, width: int = 60) -> str:
    """Creates a consistent, centered header block for reports."""
    line = "=" * width
    return f"\n{line}\n {title.upper()}\n{line}"


def format_list_item(content: str) -> str:
    """Returns a string prefixed with the standard bullet."""
    return f"{BULLET}{content}"


def format_error(msg: str) -> str:
    """Returns a string prefixed with the critical error marker."""
    return f"{CRITICAL_MARK}{msg}"


def format_status(msg: str, success: bool = True) -> str:
    """Prefixes a message with a success or warning marker."""
    mark = SUCCESS_MARK if success else ISSUE_MARK
    return f"{mark}{msg}"


def format_critical(msg: str) -> str:
    """Prefixes a message with the critical error marker for data corruption."""
    return f"{CRITICAL_MARK}{msg}"


def format_ref(obj_type: str, obj_id: int, name: str = "") -> str:
    """
    Standardizes references: UID[100], WID[42], or TOE[33].
    Example: UID[100] (1st Panzer)
    """
    prefix = f"{obj_type.upper()}[{obj_id}]"
    return f"{prefix} ({name})" if name else prefix


def format_coords(x: int, y: int) -> str:
    """Standardizes map coordinate output as (X, Y)."""
    return f"({x}, {y})"


def completion_msg(action: str, count: int, file_name: str = "") -> str:
    """
    Standardizes completion messages.
    Example: Success: 5 rows updated in _unit.csv.
    """
    target = f" in {file_name}" if file_name else ""
    return f"{SUCCESS_MARK}{action} complete: {count} matches/rows processed{target}."


def audit_msg(file_name: str, issues: int, item_count: int) -> str:
    """
    Standardizes audit result reporting including the total count of items evaluated.
    Example: ✅ _unit.csv Audit Passed: 0 issues identified (520 units checked).
    """
    mark = SUCCESS_MARK if issues == 0 else ISSUE_MARK
    status = "Passed" if issues == 0 else "Failed"
    return f"{mark}{file_name} Audit {status}: {issues} issues " \
           f"identified ({item_count} items checked)."
