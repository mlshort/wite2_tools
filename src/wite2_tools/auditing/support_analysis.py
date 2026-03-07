from typing import Dict, List, Union, Iterable, Optional
from collections import namedtuple
from wite2_tools.generator import get_csv_dict_stream
from wite2_tools.models.unit_schema import UnitColumn, Unit

# ... [Include the UnitColumn IntEnum from previous step] ...

# Create a template for the Unit object based on Enum names
# Unit = namedtuple("Unit", [c.name for c in UnitColumn])

def parse_unit_to_object(row: List[str]) -> Unit:
    """
    Parses a CSV row into a NamedTuple for dot-notation access.
    """
    processed_values: List[Union[int, str]] = []
    for col in UnitColumn:
        raw_val = row[col.value]
        try:
            processed_values.append(int(raw_val))
        except (ValueError, TypeError):
            processed_values.append(raw_val)
    return Unit(*processed_values)

def filter_units(
    units: Iterable[Unit],
    name_contains: Optional[str] = None,
    at_coords: Optional[tuple[int, int]] = None,
    min_morale: Optional[int] = None
) -> List[Unit]:
    """
    Filters a collection of units based on specific criteria.
    """
    results: List[Unit] = list(units)

    if name_contains:
        results = [u for u in results if name_contains.lower() in u.NAME.lower()]

    if at_coords:
        results = [u for u in results if u.X == at_coords[0] and u.Y == at_coords[1]]

    if min_morale is not None:
        results = [u for u in results if u.MORALE >= min_morale]

    return results


def print_undersupported_units(units: Iterable[Unit]) -> None:
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

# Example usage:
# print_undersupported_units(all_units)

if __name__ == "__main__":


    # Example path - replace with your actual test file
    path = "data/scenarios/test_unit.csv"

    # Correctly mapping the data to the expected type
    stream = get_csv_dict_stream(path)
    typed_units = [Unit(**row) for _, row in stream.rows]

    print_undersupported_units(typed_units)