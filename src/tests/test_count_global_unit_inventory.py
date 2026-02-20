import pytest
import csv

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.constants import MAX_SQUAD_SLOTS
from wite2_tools.core.count_global_unit_inventory import count_global_unit_inventory

# ==========================================
# FIXTURES (Setup)
# ==========================================

@pytest.fixture
def mock_ground_csv(tmp_path) -> str:
    """Creates a minimal _ground.csv for lookup name resolution."""
    content = "id,name,other,type\n101,Panzer III,x,1\n102,Infantry Sqd,x,1\n"
    file_path = tmp_path / "mock_ground.csv"
    file_path.write_text(content, encoding=ENCODING_TYPE)
    return str(file_path)

@pytest.fixture
def mock_unit_csv(tmp_path) -> str:
    """Generates a mock file using the exact 32-slot dot notation from _unit.csv."""
    file_path = tmp_path / "mock_unit_inventory.csv"

    # 1. Start with your real core headers
    fieldnames = ["id", "name", "type", "nat", "x", "y", "aNeed", "sNeed"]

    # 2. Add the 32 slots using the dot notation found in your file
    for i in range(MAX_SQUAD_SLOTS):
        fieldnames.append(f"sqd.u{i}")
        fieldnames.append(f"sqd.num{i}")

    def create_row(uid, name, utype, nat, slots):
        row = {"id": uid, "name": name, "type": utype, "nat": nat, "x": "50", "y": "50", "aNeed": "0", "sNeed": "0"}
        for i in range(MAX_SQUAD_SLOTS):
            row[f"sqd.u{i}"] = "0"
            row[f"sqd.num{i}"] = "0"
        row.update(slots)
        return row

    with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Row 1: Valid German Unit (Nat 1), 10x ID 101, 5x ID 102 (Tests loop range and addition)
        writer.writerow(create_row("1", "1st Pz", "1", "1", {
            "sqd.u0": "101", "sqd.num0": "10",
            "sqd.u31": "102", "sqd.num31": "5"
        }))

        # Row 2: Valid Finnish Unit (Nat 2), 20x ID 102 (Tests filtering)
        writer.writerow(create_row("2", "1st Fin", "1", "2", {
            "sqd.u0": "102", "sqd.num0": "20"
        }))

        # Row 3: Malformed Data (Non-integer quantity)
        writer.writerow(create_row("3", "Bad Data", "1", "1", {
            "sqd.u0": "101", "sqd.num0": "INVALID"
        }))

        # Row 4: Inactive Unit (Type 0) - Should be ignored
        writer.writerow(create_row("4", "Ghost", "0", "1", {
            "sqd.u0": "101", "sqd.num0": "500"
        }))

    return str(file_path)

# ==========================================
# TEST CASES
# ==========================================

def test_inventory_total_aggregation(mock_unit_csv, mock_ground_csv):
    """Verifies that items are summed correctly across all active units."""
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv)

    # ID 101: 10 (Unit 1) + 0 (Unit 2) + 0 (Unit 3/bad) + 0 (Unit 4/type0) = 10
    assert inventory[101] == 10

    # ID 102: 5 (Unit 1) + 20 (Unit 2) = 25
    assert inventory[102] == 25

def test_inventory_nationality_filtering(mock_unit_csv, mock_ground_csv):
    """Verifies that the nationality filter isolates counts to specific factions."""
    # Filter for only Nat 2 (Finnish)
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv, nat_code=2)

    # Should only see the 20x 102s from the Finnish unit
    assert inventory[102] == 20
    assert 101 not in inventory or inventory[101] == 0

def test_inventory_multiple_nat_filtering(mock_unit_csv, mock_ground_csv):
    """Verifies that passing a list/set of nat codes works."""
    # Filter for both Germans (1) and Finns (2)
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv, nat_code=[1, 2])

    # Total should be the same as the no-filter test in this setup
    assert inventory[101] == 10
    assert inventory[102] == 25

def test_inventory_robustness_to_malformed_data(mock_unit_csv, mock_ground_csv):
    """Verifies that a 'ValueError' in one slot doesn't stop the whole script."""
    inventory = count_global_unit_inventory(mock_unit_csv, mock_ground_csv)
    # Proves it kept processing after the ValueError on Unit 3
    assert 101 in inventory

def test_inventory_empty_file(tmp_path, mock_ground_csv):
    """Verifies that an empty or header-only file returns an empty dictionary."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("id,name,type,nat\n", encoding=ENCODING_TYPE)

    inventory = count_global_unit_inventory(str(empty_file), mock_ground_csv)
    assert inventory == {}