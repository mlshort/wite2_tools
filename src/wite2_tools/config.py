from typing import Any, Mapping, Final, Iterable, Union, TypeAlias, Set, Optional

ENCODING_TYPE : Final = "ISO-8859-1"
CONFIG_FILE_NAME : Final = "settings.ini"


NatData: TypeAlias = Union[int, str, Iterable[Union[int, str]], None]


def normalize_nat_codes(codes: NatData) -> Optional[Set[int]]:
    """
    Standardizes nationality input into a set of integers, removing any 0.
    """
    if codes is None:
        return None

    # Handle single integer or string inputs
    if isinstance(codes, (int, str)):
        val = int(codes)
        return {val} if val != 0 else None

    # Handle iterables (lists, sets, etc.), converting to int and filtering out 0
    return {int(c) for c in codes if int(c) != 0}


def make_hashable(obj: Any) -> Any:
    """
    Recursively converts unhashable types (list, dict, set)
    into hashable equivalents (tuple, frozenset).
    """
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(i) for i in obj)
    if isinstance(obj, Mapping):
        return tuple((k, make_hashable(v)) for k, v in sorted(obj.items()))
    if isinstance(obj, set):
        return tuple(make_hashable(i) for i in sorted(obj))
    return obj
