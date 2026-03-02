"""
CSV Modifiers and Mutation Utilities
====================================
Provides safe, atomic tools for performing bulk modifications to WiTE2 scenario data.

Features:
---------
* Atomic Writing: Uses temporary files to ensure original CSVs are only
  overwritten upon successful script completion.
* Targeted Updates: Modifies specific TOE(OB) templates, unit squad
  assignments, and weapon counts.
* Array Reordering: Logic for shifting ground elements between squad slots
  while maintaining data alignment.
"""

__version__ = "0.5.0"
__date__ = "2026-03-02"

from .base import process_csv_in_place
from .modify_unit_ground_element import modify_unit_ground_element
from .modify_unit_squads import modify_unit_squads
from .reorder_unit_squads import reorder_unit_squads
from .reorder_ob_squads import reorder_ob_squads
from .remove_ground_weapon_gaps import remove_ground_weapon_gaps

__all__ = [
    'process_csv_in_place',
    'modify_unit_ground_element',
    'modify_unit_squads',
    'reorder_unit_squads',
    'reorder_ob_squads',
    'remove_ground_weapon_gaps'
]
