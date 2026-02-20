import csv
from typing import Dict

import pytest
# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import MAX_SQUAD_SLOTS


# ==========================================
# UNIT FILE FIXTURES (_unit.csv)
# ==========================================

@pytest.fixture(name="mock_unit_csv")
def mock_unit_csv(tmp_path) -> str:
    """
    Generates a mock _unit.csv using DOT notation (sqd.u0, sqd.num0).
    Initializes all 8 unit attributes across all MAX_SQUAD_SLOTS slots.
    """
    file_path = tmp_path / "mock_unit.csv"
    prefixes = ["sqd.u", "sqd.num", "sqd.dis", "sqd.dam", "sqd.fat", "sqd.fired", "sqd.exp", "sqd.expAccum"]

    # 1. Headers: ID, Name, Type, Nat, plus 256 squad columns (8 prefixes * MAX_SQUAD_SLOTS)
    fieldnames = ["id", "name", "type", "nat", "aNeed", "sNeed"]
    for p in prefixes:
        for i in range(MAX_SQUAD_SLOTS):
            fieldnames.append(f"{p}{i}")

    # 2. Mock Row Generator
    def create_row(uid: str, name: str, utype: str, slots: Dict[str, str]):
        row = {"id": uid, "name": name, "type": utype, "nat": "1", "aNeed": "100", "sNeed": "100"}
        for f in fieldnames:
            if f not in row:
                row[f] = "0"
        row.update(slots)
        return row

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Row 1: Valid unit with target element 42 at slot 5
        writer.writerow(create_row("100", "1st Panzer", "1",
                                   {"sqd.u0": "55", "sqd.u5": "42", "sqd.num5": "10"}))
        # Row 2: Control unit
        writer.writerow(create_row("200", "2nd Panzer", "1", {"sqd.u0": "55"}))

        # Row 1: Valid German Unit (Nat 1), 10x ID 101, 5x ID 102 (Tests loop range and addition)
        writer.writerow(create_row("1", "1st Pz", "1",
                        { "sqd.u0": "101", "sqd.num0": "10", "sqd.u31": "102", "sqd.num31": "5"
        }))

        # Row 2: Valid Finnish Unit (Nat 2), 20x ID 102 (Tests filtering)
        writer.writerow(create_row("2", "1st Fin", "1",
                        { "sqd.u0": "102", "sqd.num0": "20"
        }))

        # Row 3: Malformed Data (Non-integer quantity)
        writer.writerow(create_row("3", "Bad Data", "1", {
            "sqd.u0": "101", "sqd.num0": "INVALID"
        }))

        # Row 4: Inactive Unit (Type 0) - Should be ignored
        writer.writerow(create_row("4", "Ghost", "0", {
            "sqd.u0": "101", "sqd.num0": "500"
        }))

    return str(file_path)


# ==========================================
# TOE(OB) FILE FIXTURES (_ob.csv)
# ==========================================

@pytest.fixture(name="mock_ob_csv")
def mock_ob_csv(tmp_path) -> str:
    """
    Generates a mock _ob.csv using SPACE notation (sqd 0, sqdNum 0).
    Matches the 5-argument signature required by TOE(OB) modifiers.
    """
    file_path = tmp_path / "mock_ob.csv"

    fieldnames = ["id", "name", "suffix", "type", "nat", "upgrade"]
    for i in range(MAX_SQUAD_SLOTS):
        fieldnames.append(f"sqd {i}")
        fieldnames.append(f"sqdNum {i}")

    def create_row(ob_id: str, upgrade: str, slots: Dict[str, str]):
        row = {"id": ob_id, "name": "TOE", "suffix": "41", "type": "1", "nat": "1", "upgrade": upgrade}
        for f in fieldnames:
            if f not in row:
                row[f] = "0"
        row.update(slots)
        return row

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Row 1: Chain (10 -> 20), Target 500 at slot 2
        writer.writerow(create_row("10", "20", {"sqd 0": "55", "sqd 2": "500", "sqdNum 2": "12"}))
        writer.writerow(create_row("20", "0", {"sqd 0": "55"}))
        # Row 3: Orphan
        writer.writerow(create_row("30", "0", {"sqd 0": "99"}))

    return str(file_path)


# ==========================================
# GROUND ELEMENT FIXTURES (_ground.csv)
# ==========================================

@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv(tmp_path) -> str:
    """Creates a minimal _ground.csv for lookup validation."""
    file_path = tmp_path / "mock_ground.csv"
    content = "id,name,other,type\n105,Panzer IV,x,1\n42,Tiger I,x,1\n500,88mm Flak,x,1\n"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)
