
from pathlib import Path
from typing import Callable

# Internal package imports
from wite2_tools.auditing.audit_ob import audit_ob_csv

# ==========================================
# TEST CASES
# ==========================================

def test_audit_ob_handles_key_error(tmp_path: Path,
                                    mock_ground_csv: Path) -> None:
    """
    Targets the KeyError branch by providing a CSV missing required columns.
    """
    unit_csv = tmp_path / "missing_columns.csv"
    # Note: Pass path as string for now if your audit_ob_csv hasn't been updated
    # to Path
    unit_csv.write_text("wrong_header1,wrong_header2\nval1,val2")

    issues = audit_ob_csv(str(unit_csv), str(mock_ground_csv))
    assert issues == -1


def test_clean_ob_passes(make_ob_csv: Callable[..., Path],
                         mock_ground_csv: Path) -> None:
    """A perfectly valid TOE(OB) should return 0 issues."""
    ob_path = make_ob_csv(
        filename="clean_ob.csv",
        rows_data=[
            {
                "id": "100", "name": "Valid Div",
                "firstYear" : "1941", "firstMonth": "6",
                "lastYear" : "1945", "lastMont": "3",
                "squads": [(0, "105", "9"), (1, "42", "3")]
            }
        ]
    )

    issues = audit_ob_csv(str(ob_path), str(mock_ground_csv))
    assert issues == 0


def test_chronological_bounds_error(make_ob_csv: Callable[..., Path],
                                    mock_ground_csv: Path) -> None:
    """
    Should flag if lastYear is before firstYear.
    """
    # Use the refactored factory to create the chronological error
    ob_path = make_ob_csv(
        filename="chrono_error.csv",
        rows_data=[
            {
                "id": "101",
                "name": "Time Traveler",
                "firstYear": "1941",
                "firstMonth": "6",
                "lastYear": "1940",
                "lastMonth": "1"
            }
        ]
    )

    issues = audit_ob_csv(str(ob_path), str(mock_ground_csv))

    # Assert exactly 1 issue was found (1940 is before 1941)
    assert issues == 1


def test_upgrade_loop_detection(make_ob_csv: Callable[..., Path],
                                mock_ground_csv: Path) -> None:
    """
    Should flag a circular upgrade chain involving multiple levels.
    Chain: 100 -> 101 -> 102 -> 103 -> 100 (Loop)
    """
    ob_path = make_ob_csv(
        filename="loop_error.csv",
        rows_data=[
            {"id": "100", "name": "Level 1", "upgrade": "101"},
            {"id": "101", "name": "Level 2", "upgrade": "102"},
            {"id": "102", "name": "Level 3", "upgrade": "103"},
            {"id": "103", "name": "Level 4", "upgrade": "100"}  # Loops back to start
        ]
    )

    # audit_ob_csv should trace the chain and identify the circular reference
    issues = audit_ob_csv(str(ob_path), str(mock_ground_csv))

    # We expect at least 1 issue flagged for the loop
    assert issues >= 1

def test_intra_template_duplicate_element(make_ob_csv: Callable[..., Path],
                                          mock_ground_csv: Path) -> None:
    """Should flag if the same WID is used in multiple slots."""
    ob_path = make_ob_csv(
        filename="dup_wid.csv",
        rows_data=[
            {
                "id": "104", "name": "Dup WID Div",
                "squads": [(0, "105", "9"), (1, "105", "3")] # WID 105 twice
            }
        ]
    )

    issues = audit_ob_csv(str(ob_path), str(mock_ground_csv))
    assert issues == 1


def test_ghost_and_negative_squads(make_ob_csv: Callable[..., Path],
                                   mock_ground_csv: Path) -> None:
    """Should flag negative quantities and ghost squads."""
    ob_path = make_ob_csv(
        filename="ghost_ob.csv",
        rows_data=[
            {"id": "105", "name": "Neg Div", "squads": [(0, "105", "-5")]},
            {"id": "106", "name": "Ghost Div", "squads": [(0, "0", "10")]}
        ]
    )
    issues = audit_ob_csv(str(ob_path), str(mock_ground_csv))
    assert issues == 2
