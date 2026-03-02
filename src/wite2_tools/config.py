from typing import Any, Mapping, Final, Iterable, Union, TypeAlias, Set

ENCODING_TYPE : Final = "ISO-8859-1"
CONFIG_FILE_NAME : Final = "settings.ini"


NatData: TypeAlias = Union[int, str, Iterable[Union[int, str]], None]

def normalize_nat_codes(codes: NatData) -> Set[int]:
    """
    Standardizes nationality input into a set of integers.
    """
    if codes is None:
        return set()
    if isinstance(codes, (int, str)):
        return {int(codes)}
    return {int(c) for c in codes}


def make_hashable(obj: Any) -> Any:
    """
    Recursively converts unhashable types (list, dict, set)
    into hashable equivalents (tuple, frozenset).
    """
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(i) for i in obj)
    elif isinstance(obj, Mapping):
        return tuple((k, make_hashable(v)) for k, v in sorted(obj.items()))
    elif isinstance(obj, set):
        return tuple(make_hashable(i) for i in sorted(obj))
    return obj