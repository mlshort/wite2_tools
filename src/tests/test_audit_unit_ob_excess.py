import csv
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from wite2_tools.config import ENCODING_TYPE
from wite2_tools.auditing.audit_unit_ob_excess import audit_unit_ob_excess
from wite2_tools.constants import MAX_SQUAD_SLOTS

@pytest.fixture
def mock_files(tmp_path: Path) -> tuple[str, str, str]:
    """Generates mock CSV files mapping perfectly to the auditor's expected columns."""
    unit_csv = tmp_path / "mock_unit.csv"
    ob_csv = tmp_path / "mock_ob.csv"
    ground_csv = tmp_path / "mock_ground.csv"

    # 1. Setup Ground File
    ground_headers = ["id", "name", "type", "size", "men"]
    with open(ground_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ground_headers)
        writer.writeheader()
        writer.writerow({"id": "100", "name": "Rifle Squad", "type": "1", "size": "1", "men": "10"})

    # 2. Setup TOE(OB) File (Note: Uses 'sqd X' and 'sqdNum X')
    ob_headers = ["id", "type", "name", "nat", "lastYear", "lastMonth", "upgrade"]
    for i in range(MAX_SQUAD_SLOTS):
        ob_headers.extend([f"sqd {i}", f"sqdNum {i}"])

    with open(ob_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ob_headers)
        writer.writeheader()

        row1 = {"id": "1", "type": "1", "name": "Inf Div", "nat": "1", "upgrade": "0"}
        for i in range(MAX_SQUAD_SLOTS):
            row1[f"sqd {i}"] = "0"
            row1[f"sqdNum {i}"] = "0"

        # Set authorized amount to 10
        row1["sqd 0"] = "100"
        row1["sqdNum 0"] = "10"
        writer.writerow(row1)

    # 3. Setup Unit File (Note: Uses 'sqd.uX' and 'sqd.numX')
    unit_headers = ["id", "name", "type", "nat", "delay", "hq", "hhq"]
    for i in range(MAX_SQUAD_SLOTS):
        unit_headers.extend([f"sqd.u{i}", f"sqd.num{i}"])

    with open(unit_csv, "w", encoding=ENCODING_TYPE, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=unit_headers)
        writer.writeheader()

        def create_unit_row(uid: int, name: str, sqd_qty: int) -> dict[str, str]:
            # 'type': '1' links this unit to OB ID 1
            u_row = {"id": str(uid), "name": name, "type": "1", "nat": "1", "delay": "0", "hq": "0"}
            for i in range(MAX_SQUAD_SLOTS):
                u_row[f"sqd.u{i}"] = "0"
                u_row[f"sqd.num{i}"] = "0"
            u_row["sqd.u0"] = "100"
            u_row["sqd.num0"] = str(sqd_qty)
            return u_row

        # Unit ID 1: 10 / 10 limit (100% -> Under 125% threshold) -> Pass
        writer.writerow(create_unit_row(1, "1st Div", 10))

        # Unit ID 2: 15 / 10 limit (150% -> Over 125% threshold) -> Fail (1 Issue)
        writer.writerow(create_unit_row(2, "2nd Div", 15))

    return str(unit_csv), str(ob_csv), str(ground_csv)

@patch("wite2_tools.auditing.audit_unit_ob_excess.get_ob_suffix")
def test_audit_unit_ob_excess_flags_violations(mock_suffix: MagicMock,
                                               mock_files: tuple[str, str, str]) -> None:
    """Verifies that units exceeding 125% of their OB TOE limits are flagged."""
    unit_path, ob_path, ground_path = mock_files

    # Mock the suffix generator since we aren't testing its logic here
    mock_suffix.return_value = "41a"

    issues: int = audit_unit_ob_excess(
        unit_file_path=unit_path,
        ob_file_path=ob_path,
        gnd_file_path=ground_path,
        target_nat={1}
    )

    # Expect exactly 1 issue (Unit 2)
    assert issues == 1
