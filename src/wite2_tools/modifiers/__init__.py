"""
Data manipulation and transformation scripts.

WARNING: These modules perform write operations on the source CSV files.
Includes tools for bulk-updating squad quantities and reordering TOE
elements within the TOE(OB) database.
"""

__version__ = "0.4.0"
__date__ = "2026-02-26"

from .base import process_csv_in_place
from .modify_unit_ground_element import modify_unit_ground_element
from .modify_unit_num_squads import modify_unit_num_squads
from .reorder_unit_squads import reorder_unit_squads
from .reorder_ob_squads import reorder_ob_squads
from .remove_ground_weapon_gaps import remove_ground_weapon_gaps

__all__ = [
    'process_csv_in_place',
    'modify_unit_ground_element',
    'modify_unit_num_squads',
    'reorder_unit_squads',
    'reorder_ob_squads',
    'remove_ground_weapon_gaps'
]
