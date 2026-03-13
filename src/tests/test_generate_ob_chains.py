import csv
from pathlib import Path
from typing import Callable
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.generate_ob_chains import generate_ob_chains

# ==========================================
# REFACTORED TEST DATA
# ==========================================

@pytest.fixture(name="ob_chain_setup")
def ob_chain_setup(tmp_path: Path, make_ob_csv: Callable) -> tuple[Path, Path, Path]:
    """
    Creates a temporary workspace using the shared conftest factory.
    Sets up 3 distinct chains:
    1. Normal Chain (Nat 1): 10 -> 20 -> 30
    2. Normal Chain (Nat 2): 40 -> 50
    3. Infinite Loop (Nat 1): 60 -> 70 -> 80 -> 70
    """
    csv_out = tmp_path / "chains.csv"
    txt_out = tmp_path / "chains.txt"

    # Use the factory to ensure proper 79-column padding
    ob_file = make_ob_csv(
        filename="mock_ob_chains.csv",
        rows_data=[
            # Chain 1: 10 -> 20 -> 30
            {"id": "10", "name": "Panzer Div", "suffix": "41", "nat": "1", "upgrade": "20"},
            {"id": "20", "name": "Panzer Div", "suffix": "42", "nat": "1", "upgrade": "30"},
            {"id": "30", "name": "Panzer Div", "suffix": "43", "nat": "1", "upgrade": "0"},

            # Chain 2: 40 -> 50
            {"id": "40", "name": "Inf Div", "suffix": "41", "nat": "2", "upgrade": "50"},
            {"id": "50", "name": "Inf Div", "suffix": "42", "nat": "2", "upgrade": "0"},

            # Chain 3: Infinite Loop (60 -> 70 -> 80 -> 70)
            {"id": "60", "name": "Loop Div A", "suffix": "A", "nat": "1", "upgrade": "70"},
            {"id": "70", "name": "Loop Div B", "suffix": "B", "nat": "1", "upgrade": "80"},
            {"id": "80", "name": "Loop Div C", "suffix": "C", "nat": "1", "upgrade": "70"}
        ]
    )

    return ob_file, csv_out, txt_out

# ==========================================
# TESTS
# ==========================================

def test_generate_ob_chains_logic(ob_chain_setup: tuple[Path, Path, Path]) -> None:
    """Verifies that chains are identified and formatted correctly."""
    ob_file, csv_out, txt_out = ob_chain_setup
    generate_ob_chains(str(ob_file), str(csv_out), str(txt_out))

    with open(txt_out, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()
        # Verify Normal Chain 1
        assert "[10] Panzer Div 41 -> [20] Panzer Div 42 -> [30] Panzer Div 43" in content
        # Verify Normal Chain 2
        assert "[40] Inf Div 41 -> [50] Inf Div 42" in content

def test_generate_ob_chains_infinite_loop(ob_chain_setup: tuple[Path, Path, Path]) -> None:
    """Verifies that the logic catches circular upgrade references."""
    ob_file, csv_out, txt_out = ob_chain_setup
    generate_ob_chains(str(ob_file), str(csv_out), str(txt_out))

    with open(txt_out, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()
        # Verify the loop was caught and documented
        assert "70 (LOOP)" in content
        assert "[60] Loop Div A A -> [70] Loop Div B B -> [80] Loop Div C C -> 70 (LOOP)" in content

def test_generate_ob_chains_csv_output(ob_chain_setup: tuple[Path, Path, Path]) -> None:
    """Verifies that the CSV output file contains the expected number of chains."""
    ob_file, csv_out, txt_out = ob_chain_setup
    generate_ob_chains(str(ob_file), str(csv_out), str(txt_out))

    with open(csv_out, 'r', encoding=ENCODING_TYPE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # Chain 1 starts at 10, Chain 2 at 40, Chain 3 at 60
        assert len(rows) == 3
