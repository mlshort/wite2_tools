"""
WiTE2 Unit Data Structure
=========================

This module defines the core Unit dataclass used across the wite2_tools
package for in-memory representation of War in the East 2 ground units.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    """
    Immutable data structure representing a key WiTE2 Unit.

    Attributes:
        unit_id (int):   The unique identifier of the unit (Primary Key).
        name (str):      The localized or designated name of the unit.
        unit_type (int): The TOE(OB) ID that this unit is currently assigned.
        nat (int):       The nationality code of the unit
            (e.g., 1 for Germany, 12 for SU).

    Note:
        `frozen=True` makes instances of this class hashable and immutable.
        This is required when storing these objects in data structures that
        are managed by the `@cache` decorator to prevent accidental state
        mutation.
    """
    unit_id: int
    name: str
    unit_type: int
    nat: int


# ==========================================
# EXAMPLE USAGE
# ==========================================
if __name__ == "__main__":
    from wite2_tools.utils.lookups import get_nat_abbr

    # Example: Creating a new German Panzer Division
    my_unit = Unit(unit_id=1054, name="1st Panzer Div", unit_type=33, nat=1)

    print(f"Created Unit: {my_unit.name} (ID: {my_unit.unit_id})")
    print(f"Assigned TOE(OB): {my_unit.unit_type}")
    print(f"Nationality: {get_nat_abbr(my_unit.nat)}")

    # Because frozen=True, attempting to change a value will raise a
    # FrozenInstanceError:
    # my_unit.name = "2nd Panzer Div"  # <-- This would crash safely!