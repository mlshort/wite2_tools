from collections.abc import Iterator
from typing import Any, List, Tuple

from wite2_tools.models.gnd_schema import WPN_SLOTS, GndColumn


class GndRow:
    """
    A dynamic representation of a WiTE2 Ground Element (GE).

    Instantiates directly from a raw CSV list, mapping indices to attributes
    via GndColumn. Supports fuzzy lookup and efficient weapon slot iteration.
    """
    # Type hints for standard GE fields
    ID: int
    NAME: str
    TYPE: int
    NAT: int
    MEN: int
    UPGRADE: int
    SPEED: int
    YEAR: int

    def __init__(self, row: List[str]):
        """
        Parses the raw CSV row using GndColumn indices.
        """
        self._raw = row
        row_len = len(row)

        for col in GndColumn:
            raw_val = row[col] if col < row_len else "0"

            try:
                val = int(raw_val)
            except (ValueError, TypeError):
                val = raw_val

            setattr(self, col.name, val)


    @property
    def raw(self) -> List[str]:
        """
        Returns the underlying raw CSV string list.
        """
        return self._raw


    def get_weapons(self) -> Iterator[Tuple[int, int]]:
        """
        Yields (device_id, quantity) by calculating offsets from the
        WPN_0 and WPN_NUM_0 base indices.
        """
        # Base indices from your GndColumn Enum
        wpn_base = GndColumn.WPN_0      # 32
        num_base = GndColumn.WPN_NUM_0  # 42

        for i in range(WPN_SLOTS): # Ground elements have 10 weapon slots
            try:
                device_id = int(self._raw[wpn_base + i])
                qty = int(self._raw[num_base + i])

                if device_id > 0 and qty > 0:
                    yield device_id, qty
            except (IndexError, ValueError):
                continue


    def __getattr__(self, item: str) -> Any:
        """
        Fuzzy lookup for attribute access (e.g., gnd.men or gnd.ID).
        """
        normalized_request = item.replace("_", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"GndRow has no attribute '{item}'")