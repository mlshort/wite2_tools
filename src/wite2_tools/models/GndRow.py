from collections.abc import Iterator
from typing import Any, Self

from wite2_tools.models.gnd_schema import (
    WPN_SLOTS,
    NUM_COLS,
    GndColumn,
    GndElementType
)


class GndRow:
    """
    A dynamic representation of a WiTE2 Ground Element (GE).

    Instantiates directly from a raw CSV list, mapping indices to attributes
    via GndColumn. Supports fuzzy lookup and efficient weapon slot iteration.
    """
    # Type hints for standard GE fields
    ID: int
    NAME: str
    ID_2: int
    TYPE: int
    NAT: int
    YEAR: int
    RANGE: int
    SPEED: int
    DUR: int
    MEN: int
    UPGRADE: int
    SIZE: int
    _raw: list[str]


    @property
    def raw(self: Self) -> list[str]:
        """
        Returns the underlying raw CSV string list.
        """
        return self._raw


    def __init__(self: Self, row: list[str]) -> None:
        """
        Parses the raw CSV row using GndColumn indices.
        """
        self.load_row(row)


    def load_row(self: Self, row: list[str]) -> None:
        """
        Internal initialization method to safely parse and load a row,
        avoiding unsound __init__ calls.
        """
        super().__setattr__('_raw', row)
        row_len = len(row)

        for col in GndColumn:
            raw_val = row[col] if col < row_len else "0"

            val: Any
            try:
                val = int(raw_val)
            except (ValueError, TypeError):
                val = raw_val

            setattr(self, col.name, val)


    def get_weapons(self: Self) -> Iterator[tuple[int, int]]:
        """
        Yields (device_id, quantity) by calculating offsets from the
        WPN_0 and WPN_NUM_0 base indices.
        """
        # Base indices from GndColumn Enum
        wpn_base = GndColumn.WPN_0      # 32
        num_base = GndColumn.WPN_NUM_0  # 42

        for i in range(WPN_SLOTS): # Ground elements have 10 weapon slots
            try:
                device_id = int(self.raw[wpn_base + i])
                qty = int(self.raw[num_base + i])

                if device_id > 0 and qty > 0:
                    yield device_id, qty
            except (IndexError, ValueError):
                continue


    def set_weapon(self: Self, slot_idx: int, device_id: int, qty: int) -> None:
        """
        Sets the device ID and quantity for a specific weapon slot (0 to WPN_SLOTS - 1).
        Updates both the underlying raw CSV list and the named attributes.
        """
        # Ensure the index is within the allowed 10 weapon slots
        if not 0 <= slot_idx < WPN_SLOTS:
            raise IndexError(f"Weapon slot {slot_idx} is out of range. Must be 0 to {WPN_SLOTS - 1}.")

        # Calculate the exact column indices
        wpn_col_idx = GndColumn.WPN_0 + slot_idx
        num_col_idx = GndColumn.WPN_NUM_0 + slot_idx

        # 1. Update the underlying _raw list
        # (Pad the list with zeroes if it's somehow too short)
        max_idx = max(wpn_col_idx, num_col_idx)
        while len(self.raw) <= max_idx:
            self.raw.append("0")

        self.raw[wpn_col_idx] = str(device_id)
        self.raw[num_col_idx] = str(qty)

        # 2. Update the object attributes (e.g., self.WPN_0)
        # Using f-strings is drastically faster than reverse Enum lookups!
        setattr(self, f"WPN_{slot_idx}", device_id)
        setattr(self, f"WPN_NUM_{slot_idx}", qty)


    def __getattr__(self: Self, item: str) -> Any:
        """
        Fuzzy lookup for attribute access (e.g., gnd.men or gnd.ID).
        """
        normalized_request = item.replace("_", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"GndRow has no attribute '{item}'")


    def __setattr__(self: Self, key: str, value: Any) -> None:
        """
        Intercepts attribute assignments to keep the underlying `_raw` CSV
        list perfectly synchronized with the object properties.
        """
        # Allow internal setup attributes to bypass the CSV synchronization
        if key == '_raw':
            super().__setattr__(key, value)
            return

        normalized_key = key.upper()

        try:
            # Validate that the key exists in our schema
            col_enum = GndColumn[normalized_key]
        except KeyError:
            # If it's a completely unknown property, just set it normally
            super().__setattr__(key, value)
            return

        # 1. Update the actual object attribute
        super().__setattr__(col_enum.name, value)

        # 2. Update the underlying raw list at the correct index
        # Ensure the list is long enough (pad with "0" if necessary)
        while len(self._raw) <= col_enum:
            self._raw.append("0")

        self._raw[col_enum] = str(value)


    @classmethod
    def create_default(cls: type[Self],
                       elem_id: int = 0,
                       name: str = "",
                       g_type: int = GndElementType.RIFLE_SQUAD) -> Self:
        """
        Generates a default 92-column row for a _ground.csv file.

        Args:
            elem_id (int): The ID for the ground element (Column 0). Defaults to 0.
            name (str): The name of the element (Column 1). Defaults to empty.

        Returns:
            list[str]: A list containing the ID, Name, and 90 zeroes.
        """
        # Create the base row with the ID, Name, ID_2 and Type
        row: list[str] = [str(elem_id), name, str(elem_id), str(g_type)]

        # Append 90 zeroes to fill out the remaining 89 columns
        # (Properties, Limits, and the 10x Weapon Slots)
        row.extend(["0"] * (NUM_COLS - 4))

        return cls(row)
