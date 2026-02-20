import os
import pytest

# Internal package imports
from wite2_tools.paths import (
    CONF_UNIT_FULL_PATH,
    CONF_OB_FULL_PATH,
    CONF_GROUND_FULL_PATH
)
from wite2_tools.core.group_units_by_ob import group_units_by_ob
from wite2_tools.core.count_global_unit_inventory import count_global_unit_inventory

# Tell pytest this is a slow integration test
pytestmark = pytest.mark.integration


def test_real_data_paths_exist():
    """Sanity check: Ensure the real data files actually exist where expected."""
    assert os.path.exists(CONF_UNIT_FULL_PATH), f"Missing: {CONF_UNIT_FULL_PATH}"
    assert os.path.exists(CONF_OB_FULL_PATH), f"Missing: {CONF_OB_FULL_PATH}"
    assert os.path.exists(CONF_GROUND_FULL_PATH), f"Missing: {CONF_GROUND_FULL_PATH}"

def test_load_group_units_by_ob_real_data():
    """
    Stress test: Runs the grouping logic against the massive real _unit.csv.
    We just want to prove it doesn't crash and returns a populated dictionary.
    """
    # Clear cache just in case
    group_units_by_ob.cache_clear()

    result = group_units_by_ob(CONF_UNIT_FULL_PATH)

    # Assert that it successfully processed a massive amount of data
    assert len(result) > 0
    assert isinstance(result, dict)

def test_load_global_inventory_real_data():
    """
    Stress test: Runs the inventory counter against the configured game data files.
    """
    inventory = count_global_unit_inventory(CONF_UNIT_FULL_PATH, CONF_GROUND_FULL_PATH)

    # Assert the dictionary populated successfully
    assert len(inventory) > 0
    assert isinstance(inventory, dict)
