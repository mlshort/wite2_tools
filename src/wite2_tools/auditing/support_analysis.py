from typing import List, Iterable, Optional, Tuple
from wite2_tools.models.UnitRow import UnitRow

# ... [Include the UnitColumn IntEnum from previous step] ...


def filter_units(
    units: Iterable[UnitRow],
    name_contains: Optional[str] = None,
    at_coords: Optional[Tuple[int, int]] = None,
    min_morale: Optional[int] = None
) -> List[UnitRow]:
    """
    Filters a collection of units based on specific criteria.
    """
    results: List[UnitRow] = list(units)

    if name_contains:
        results = [u for u in results if name_contains.lower() in u.NAME.lower()]

    if at_coords:
        results = [u for u in results if u.X == at_coords[0] and u.Y == at_coords[1]]

    if min_morale is not None:
        results = [u for u in results if u.MORALE >= min_morale]

    return results


def print_undersupported_units(units: Iterable[UnitRow]) -> None:
    """
    Identifies and prints units where SPT_NEED is greater than SUPPORT.
    Displays the deficit for easy prioritization.
    """
    print(f"{'Unit Name':<30} | {'Need':<8} | {'Current':<8} | {'Deficit':<8}")
    print("-" * 60)

    count: int = 0
    for u in units:
        # Checking if the unit needs more support than it currently has
        if u.SPT_NEED > u.SUPPORT:
            deficit: int = u.SPT_NEED - u.SUPPORT
            print(f"{u.NAME:<30} | {u.SPT_NEED:<8} | {u.SUPPORT:<8} | {deficit:<8}")
            count += 1

    print("-" * 60)
    print(f"Total undersupported units found: {count}")


