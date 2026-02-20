"""
Data manipulation and transformation scripts.

WARNING: These modules perform write operations on the source CSV files.
Includes tools for bulk-updating squad quantities and reordering TOE
elements within the TOE(OB) database.
"""

__version__ = "0.1.1"
__date__ = "2026-02-19"

from .replace_unit_ground_element import replace_unit_ground_element
from .update_unit_num_squads import update_unit_num_squads
from .reorder_unit_squads import reorder_unit_squads
from .reorder_ob_squads import reorder_ob_squads
from .remove_ground_weapon_gaps import remove_ground_weapon_gaps

__all__ = [
    'replace_unit_ground_element',
    'update_unit_num_squads',
    'reorder_unit_squads',
    'reorder_ob_squads',
    'remove_ground_weapon_gaps'
]