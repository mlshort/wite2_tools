"""
Core analysis modules for WiTE2 data structures.

Contains logic for tracing TOE (Table of Organization and Equipment)
evolution chains, identifying unreferenced database IDs, and performing
global inventory calculations across the unit database.
"""

__version__ = "0.1.1"
__date__ = "2026-02-19"

from .generate_ob_chains import generate_ob_chains
from .find_unreferenced_ob_ids import find_unreferenced_ob_ids
from .count_global_unit_inventory import count_global_unit_inventory
from .group_units_by_ob import group_units_by_ob

# Accessible via "from wite2_tools.core import *"
__all__ = [
    "generate_ob_chains",
    "find_unreferenced_ob_ids",
    "count_global_unit_inventory",
    "group_units_by_ob"
]
