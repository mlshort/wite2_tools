import pytest
from unittest.mock import patch, MagicMock

# Assuming your module is accessible via this path. Adjust if necessary.
from wite2_tools.utils.get_name import (
    _build_ob_lookup,
    _build_ground_elem_lookup,
    get_ob_name,
    get_ob_suffix,
    get_ob_full_name,
    get_unit_type_name,
    get_ground_elem_type_name,
    get_ob_combat_class_name,
    get_device_type_name,
    get_ob_type_code_name,
    get_country_name,
    get_unit_special_name,
    get_ground_elem_class_name,
    get_device_face_type_name
)
from wite2_tools.models import GndColumn


@pytest.fixture(autouse=True)
def clear_caches():
    """
    Automatically clears the functools.cache for the private helpers
    before each test to ensure tests don't pollute each other's state.
    """
    _build_ob_lookup.cache_clear()
    _build_ground_elem_lookup.cache_clear()
    yield


# ==========================================
# TOE(OB) LOOKUP TESTS
# ==========================================

@patch("wite2_tools.utils.get_name.os.path.exists", return_value=False)
def test_build_ob_lookup_file_not_found(mock_exists):
    """Test that a missing OB file returns an empty dictionary."""
    result = _build_ob_lookup("fake_path.csv")
    assert not result
    mock_exists.assert_called_once_with("fake_path.csv")


@patch("wite2_tools.utils.get_name.os.path.exists", return_value=True)
@patch("wite2_tools.utils.get_name.get_csv_dict_stream")
def test_build_ob_lookup_success(mock_get_csv, mock_exists):
    """Test successful parsing and caching of OB names."""
    # Create a mock stream object
    mock_stream = MagicMock()
    mock_stream.rows = [
        (0, {"id": "1", "name": "Infantry", "suffix": "Div"}),
        (1, {"id": "2", "name": "Armor", "suffix": "Bde"}),
        (2, {"id": "invalid", "name": "Bad", "suffix": "Data"}), # Should be skipped
    ]
    mock_get_csv.return_value = mock_stream

    # Call any of the public APIs to trigger the cache build
    name = get_ob_name("dummy.csv", 1)

    assert name == "Infantry"
    assert get_ob_suffix("dummy.csv", 1) == "Div"
    assert get_ob_full_name("dummy.csv", 1) == "Infantry Div"

    # Test wrapper
    assert get_unit_type_name("dummy.csv", 2) == "Armor Bde"

    # Test missing ID falls back to default "Unk (id)"
    assert get_ob_name("dummy.csv", 999) == "Unk (999)"


# ==========================================
# GROUND ELEMENT LOOKUP TESTS
# ==========================================

@patch("wite2_tools.utils.get_name.os.path.exists", return_value=False)
def test_build_ground_elem_lookup_file_not_found(mock_exists):
    """Test that a missing ground file returns an empty dictionary."""
    result = _build_ground_elem_lookup("fake_ground.csv")
    assert result == {}


@patch("wite2_tools.utils.get_name.os.path.exists", return_value=True)
@patch("wite2_tools.utils.get_name.get_csv_list_stream")
def test_build_ground_elem_lookup_success(mock_get_csv, mock_exists):
    """Test successful parsing and caching of Ground Element names using GndColumn indices."""
    mock_stream = MagicMock()
    mock_stream.header = True

    # Simulate a CSV row list. We just need it to be long enough to have GndColumn.ID and GndColumn.NAME
    # We will dynamically build the list to ensure it's long enough regardless of Enum values
    max_col = max(GndColumn.ID, GndColumn.NAME)

    row_1 = [""] * (max_col + 1)
    row_1[GndColumn.ID] = "100"
    row_1[GndColumn.NAME] = "Panzer IV"

    row_2 = [""] * (max_col + 1)
    row_2[GndColumn.ID] = "101"
    row_2[GndColumn.NAME] = "T-34"

    mock_stream.rows = [
        (0, row_1),
        (1, row_2),
        (2, ["short", "row"]) # Should be skipped via IndexError/ValueError handling
    ]
    mock_get_csv.return_value = mock_stream

    assert get_ground_elem_type_name("dummy_ground.csv", 100) == "Panzer IV"
    assert get_ground_elem_type_name("dummy_ground.csv", 101) == "T-34"
    assert get_ground_elem_type_name("dummy_ground.csv", 999) == "Unk (999)"


# ==========================================
# INTERNAL DICTIONARY LOOKUP TESTS
# ==========================================

# We patch the dictionaries directly in the module where they are used.
@patch.dict("wite2_tools.utils.get_name.OB_COMBAT_CLASS_LOOKUP", {1: "Infantry Class"}, clear=True)
def test_get_ob_combat_class_name():
    assert get_ob_combat_class_name(1) == "Infantry Class"
    assert get_ob_combat_class_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.DEVICE_TYPE_LOOKUP", {5: "Cannon"}, clear=True)
def test_get_device_type_name():
    assert get_device_type_name(5) == "Cannon"
    assert get_device_type_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.OB_TYPE_LOOKUP", {10: "Division"}, clear=True)
def test_get_ob_type_code_name():
    assert get_ob_type_code_name(10) == "Division"
    assert get_ob_type_code_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.NATION_LOOKUP", {1: "Germany", 2: "Soviet Union"}, clear=True)
def test_get_country_name():
    assert get_country_name(1) == "Germany"
    assert get_country_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.UNIT_SPECIAL_LOOKUP", {4: "Motorized"}, clear=True)
def test_get_unit_special_name():
    assert get_unit_special_name(4) == "Motorized"
    assert get_unit_special_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.GROUND_ELEMENT_TYPE_LOOKUP", {20: "Medium Tank"}, clear=True)
def test_get_ground_elem_class_name():
    assert get_ground_elem_class_name(20) == "Medium Tank"
    assert get_ground_elem_class_name(99) == "Unk (99)"

@patch.dict("wite2_tools.utils.get_name.DEVICE_FACE_TYPE_LOOKUP", {0: "Front", 1: "Turret"}, clear=True)
def test_get_device_face_type_name():
    assert get_device_face_type_name(1) == "Turret"
    assert get_device_face_type_name(99) == "Unk (99)"