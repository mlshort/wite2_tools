"""
Core analysis modules for WiTE2 data structures.
Contains logic for tracing TOE (Table of Organization and Equipment)
evolution chains, identifying unreferenced database IDs, and performing
global inventory calculations across the unit database.
"""

__version__ = "0.3.1"
__date__ = "2026-02-22"

from .generate_ob_chains import generate_ob_chains
from .find_orphaned_obs import (
    find_orphaned_obs,
    is_ob_orphaned
)
from .count_global_unit_inventory import count_global_unit_inventory
from .identify_unused_devices import identify_unused_devices
from .group_units_by_ob import group_units_by_ob, Unit

# Accessible via "from wite2_tools.core import *"
__all__ = [
    "generate_ob_chains",
    "find_orphaned_obs",
    "is_ob_orphaned",
    "count_global_unit_inventory",
    "group_units_by_ob",
    "identify_unused_devices",
    "Unit"
]
