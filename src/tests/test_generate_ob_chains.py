import csv
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.core.generate_ob_chains import generate_ob_chains

# ==========================================
# FIXTURES (Setup)
# ==========================================


@pytest.fixture(name="mock_workspace")
def mock_workspace(tmp_path) -> tuple[str, str, str]:
    """
    Creates a temporary workspace containing a mock _ob.csv file
    and returns the paths for the input and output files.
    """
    ob_file = tmp_path / "mock_ob.csv"
    csv_out = tmp_path / "chains.csv"
    txt_out = tmp_path / "chains.txt"

    # We are setting up 3 distinct chains here:
    # 1. Normal Chain (Nat 1)
    # 2. Normal Chain (Nat 2)
    # 3. Corrupted Chain with an infinite loop (Nat 1)
    content = (
        "id,name,suffix,type,nat,upgrade\n"
        "10,Panzer Div,41,1,1,20\n"  # Chain 1: 10 -> 20 -> 30
        "20,Panzer Div,42,1,1,30\n"
        "30,Panzer Div,43,1,1,0\n"
        "40,Inf Div,41,4,2,50\n"  # Chain 2: 40 -> 50 (Nat 2)
        "50,Inf Div,42,4,2,0\n"
        "60,Loop Div,A,1,1,70\n"  # Chain 3: 60 -> 70 -> 80 -> Loop(70)
        "70,Loop Div,B,1,1,80\n"
        "80,Loop Div,C,1,1,70\n"  # Circular Reference!
        "0,Skip Me,,0,0,0\n"  # Should be skipped (ID/Type 0)
    )

    ob_file.write_text(content, encoding=ENCODING_TYPE)
    return str(ob_file), str(csv_out), str(txt_out)


# ==========================================
# TEST CASES
# ==========================================


def test_generate_ob_chains_success(mock_workspace):
    """Verifies that all valid chains are traced and counted."""
    ob_file, csv_out, txt_out = mock_workspace

    # Execute with no nationality filter
    num_chains = generate_ob_chains(ob_file, csv_out, txt_out)

    # We expect 3 roots to be found (IDs 10, 40, and 60)
    assert num_chains == 3


def test_generate_ob_chains_nat_filter(mock_workspace):
    """Verifies that the nationality filter correctly isolates chains."""
    ob_file, csv_out, txt_out = mock_workspace

    # Execute with nation_id={2}
    num_chains = generate_ob_chains(ob_file, csv_out, txt_out, nat_codes={2})

    # We expect only 1 root to be found (ID 40)
    assert num_chains == 1

    # Verify the text file only contains Chain 2
    with open(txt_out, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()
        assert "[40] Inf Div 41 -> [50] Inf Div 42" in content
        assert "Panzer" not in content  # Chain 1 should not exist


def test_generate_ob_chains_loop_protection(mock_workspace):
    """
    Verifies that circular references in the game data do not cause
    an infinite while loop, and that the loop is safely documented.
    """
    ob_file, csv_out, txt_out = mock_workspace
    generate_ob_chains(ob_file, csv_out, txt_out)

    # Read the text file output
    with open(txt_out, 'r', encoding=ENCODING_TYPE) as f:
        content = f.read()

        # Verify the loop was caught and appended to the chain string
        assert "70 (LOOP)" in content
        assert "[60] Loop Div A -> [70] Loop Div B -> " \
               "[80] Loop Div C -> 70 (LOOP)" in content


def test_generate_ob_chains_csv_output(mock_workspace):
    """Verifies that the CSV output file is structured correctly."""
    ob_file, csv_out, txt_out = mock_workspace
    generate_ob_chains(ob_file, csv_out, txt_out)

    # Read the generated CSV output
    with open(csv_out, 'r', encoding=ENCODING_TYPE) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 3

        # Verify headers and data for Chain 1
        assert rows
