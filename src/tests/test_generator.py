import pytest
import csv
from typing import cast
from wite2_tools.generator import read_csv_list_generator, read_csv_dict_generator

@pytest.fixture
def mock_basic_csv(tmp_path) -> str:
    content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6\n"
    file_path = tmp_path / "mock_basic.csv"
    file_path.write_text(content, encoding="ISO-8859-1")
    return str(file_path)

def test_read_csv_list_generator(mock_basic_csv):
    """Verifies list generator yields header first, then enumerated lists."""
    gen = read_csv_list_generator(mock_basic_csv)

    # First yield should be the header list
    header = next(gen)
    assert header == ["col1", "col2", "col3"]

    # Second yield should be (index 1, row list)
    idx1, row1 = cast(tuple[int, list], next(gen))
    assert idx1 == 1
    assert row1 == ["val1", "val2", "val3"]

    # Third yield should be (index 2, row list)
    idx2, row2 = cast(tuple[int, list], next(gen))
    assert idx2 == 2
    assert row2 == ["val4", "val5", "val6"]

def test_read_csv_dict_generator(mock_basic_csv):
    """Verifies dict generator yields DictReader first, then enumerated dicts."""
    gen = read_csv_dict_generator(mock_basic_csv)

    # First yield should be the DictReader object
    reader = next(gen)
    assert isinstance(reader, csv.DictReader)
    assert reader.fieldnames == ["col1", "col2", "col3"]

    # Second yield should be (index 1, row dict)
    idx1, row1 = cast(tuple[int, dict], next(gen))
    assert idx1 == 1
    assert row1 == {"col1": "val1", "col2": "val2", "col3": "val3"}