from typing import Any, Generator
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


# Adjust imports based on the actual functions in your file
from wite2_tools.utils.get_name import (
    get_ground_elem_type_name,
    _build_ground_elem_lookup,
    get_device_type_name,
    get_country_name,
    get_unit_special_name
)


@pytest.fixture(autouse=True)
def reset_caches() -> Generator[None, Any, None]:
    """
    Automatically runs before and after every test to clear the functools
    caches. This guarantees no test contaminates the results of another by
    leaving parsed CSV data in memory.
    """
    # Clear the cache for the ground element builder
    # (Add your other builders here like _build_ob_lookup.cache_clear() if they exist)
    if hasattr(_build_ground_elem_lookup, "cache_clear"):
        _build_ground_elem_lookup.cache_clear()

    yield  # Let the test run

    if hasattr(_build_ground_elem_lookup, "cache_clear"):
        _build_ground_elem_lookup.cache_clear()


# ---------------------------------------------------------
# Tests for Static Dictionary Lookups
# ---------------------------------------------------------

def test_get_country_name_fallback() -> None:
    """Verifies static dict lookup falls back to 'Unk (ID)' if missing."""
    assert get_country_name(9999) == "Unk (9999)"


def test_get_device_type_name_fallback() -> None:
    assert get_device_type_name(9999) == "Unk (9999)"


def test_get_unit_special_name_fallback() -> None:
    assert get_unit_special_name(9999) == "Unk (9999)"


# ---------------------------------------------------------
# Tests for CSV File Lookups (with functools.cache)
# ---------------------------------------------------------

def test_get_ground_elem_type_name_success_and_caching(tmp_path: Path) -> None:
    """Verifies it reads the CSV, caches the dict, and fetches the name."""
    # 1. Create a REAL temporary CSV file
    test_csv = tmp_path / "dummy_ground.csv"
    test_csv.write_text("id,name\n10,Panzer IV\n20,Tiger I", encoding="utf-8")

    # 2. First call (Ensure your arguments match your signature! Usually filepath is first)
    result_1 = get_ground_elem_type_name(str(test_csv), 10)
    assert result_1 == "Panzer IV"

    # 3. DELETE the file!
    test_csv.unlink()

    # 4. Second call hits the cache. If cache failed, it would crash reading the deleted file.
    result_2 = get_ground_elem_type_name(str(test_csv), 20)
    assert result_2 == "Tiger I"



def test_get_ground_elem_type_name_file_not_found() -> None:
    """Verifies behavior when the target CSV file does not exist."""
    result = get_ground_elem_type_name("missing_ground.csv", 10)

    assert result == "Unk (10)"



@patch("wite2_tools.utils.get_name.os.path.exists", return_value=True)
@patch("wite2_tools.utils.get_name.get_csv_list_stream")
def test_get_ground_elem_type_name_id_not_in_file(mock_get_csv: MagicMock,
                                                  mock_exists: MagicMock) -> None:
    """Verifies it handles a valid file that doesn't contain the requested ID."""
    mock_stream = MagicMock()
    mock_stream.rows = [
        (0, ["id", "name"]),
        (1, ["1", "Only Unit"])
    ]
    mock_get_csv.return_value = mock_stream

    result = get_ground_elem_type_name("dummy_ground.csv", 99)

    assert result == "Unk (99)"