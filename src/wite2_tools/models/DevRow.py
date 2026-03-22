from typing import Any, Self

from wite2_tools.models.dev_schema import (
    DevColumn,
    DeviceType,
    gen_device_column_names
)


class DevRow:
    """
    A dynamic representation of a WiTE2 Device.

    This class transforms raw CSV row lists into objects with
    type-hinted attributes. It supports fuzzy attribute lookup (e.g.,
    dev.loadCost, dev.LOAD_COST, dev.name) via __getattr__.
    """
    # Type hints for standard Device fields to keep Pylance/MyPy happy
    ID: int
    NAME: str
    TYPE: int
    SYM: int
    LOAD_COST: int
    RANGE: int
    EFFECT: int
    PEN: int
    ACC: int
    ANTI_ARMOR: int
    _raw: list[str]

    @property
    def raw(self:Self) -> list[str]:
        """
        Returns the underlying raw CSV string list.
        """
        return self._raw


    def __init__(self: Self, row: list[str]) -> None:
        """
        Takes a raw CSV row (list of strings) and parses it using the known
        Enum indices from DevColumn.
        """
        self._load_row(row)


    def _load_row(self: Self, row: list[str]) -> None:
        """
        Internal initialization method to safely parse and load a row,
        avoiding unsound __init__ calls.
        """
        # We must use super().__setattr__ here to bypass our custom __setattr__
        # until the _raw list is actually attached to the object!
        super().__setattr__('_raw', row)

        row_len = len(row)

        for col in DevColumn:
            raw_val = row[col] if col < row_len else "0"

            val: Any
            try:
                val = int(raw_val)
            except (ValueError, TypeError):
                val = raw_val

            setattr(self, col.name, val)


    def __getattr__(self: Self, item: str) -> Any:
        """
        Fuzzy lookup for attribute access (e.g., dev.name or dev.NAME).
        """
        normalized_request = item.upper()

        try:
            # Check if the requested attribute matches a DevColumn enum name
            col_enum = DevColumn[normalized_request]
            return super().__getattribute__(col_enum.name)
        except KeyError:
            pass # Fall through to default AttributeError

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


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
            col_enum = DevColumn[normalized_key]
        except KeyError:
            # If it's a completely unknown property, just set it normally
            super().__setattr__(key, value)
            return

        # 1. Update the actual object attribute
        super().__setattr__(col_enum.name, value)

        # 2. Update the underlying raw list at the correct index
        # Ensure the list is long enough (pad with "0" if necessary)
        while len(self.raw) <= col_enum.value:
            self.raw.append("0")

        self.raw[col_enum.value] = str(value)


    @classmethod
    def create_default(cls: type[Self],
                       d_id: int = 0,
                       name: str = "",
                       d_type: int = DeviceType.MAN_WEAPON) -> Self:
        """
        Generates a default 25-column row for a _device.csv file.

        Args:
            device_id (int): The ID for the Device (Column 0). Defaults to 0.
            name (str): The name of the Device (Column 1). Defaults to empty.

        Returns:
            list[str]: A list containing the ID, Name, and 23 zeroes.
        """
        row: list[str] = [str(d_id), name, str(d_type)]

        # Append 23 zeroes to fill out the remaining combat statistics
        row.extend(["0"] * 22)

        return cls(row)


def gen_default_device_dict(d_id: int = 0,
                            name: str = "") -> dict[str, str]:
    """
    Generates a default Device dictionary mapped to schema headers.
    """
    headers = gen_device_column_names()
    default_row_list = DevRow.create_default(d_id, name).raw

    # Zip the 25 headers together with the 25 default values
    return dict(zip(headers, default_row_list))