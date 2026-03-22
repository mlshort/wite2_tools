from typing import Any, Self

from wite2_tools.models.unit_schema import (
    gen_unit_column_names,
    UnitColumn,
    ATTRS_PER_SQD as U_ATTRS_PER_SQD,
    SQD_SLOTS as U_SQD_SLOTS,
    SQD_U0_COL as U_SQD0_COL
)


class UnitRow:
    """
    Instantiates directly from a raw CSV list stream, utilizing the UnitColumn
    IntEnum to map indices to class attributes. Supports fuzzy attribute
    lookup (e.g., unit.nat or unit.HHQ) via __getattr__.
    """
    # Type hints for IDE support
    ID: int
    NAME: str
    TYPE: int
    NAT: int
    X: int
    Y: int
    MORALE: int
    HHQ: int
    DELAY: int
    _raw: list[str]

    @property
    def raw(self) -> list[str]:
        return self._raw


    def __init__(self: Self, row: list[str]) -> None:
        """
        Takes a raw CSV row (list of strings) and parses it using the UnitColumn indices.
        """
        self.load_row(row)


    def load_row(self: Self, row: list[str]) -> None:
        # Use super to avoid triggering custom __setattr__ before _raw exists
        super().__setattr__('_raw', row)
        self._refresh_attributes()


    def _refresh_attributes(self: Self)->None:
        """
        Maps the raw list to named attributes.
        """
        row_len = len(self.raw)
        for col in UnitColumn:
            raw_val = self.raw[col.value] if col.value < row_len else "0"

            val: Any
            try:
                val = int(raw_val)
            except (ValueError, TypeError):
                val = raw_val

            # This creates unit.ID, unit.NAME, unit.SQD_0, etc.
            super().__setattr__(col.name, val)


    def __getattr__(self: Self, item: str) -> Any:
        normalized_request = item.replace("_", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


    def __setattr__(self: Self, name: str, value: Any) -> None:
        """
        Ensures that when a class attribute is updated, the underlying
        _raw CSV list is also updated. Supports fuzzy naming.
        """
        super().__setattr__(name, value)

        if name.startswith('_'):
            return

        # Normalize the incoming name (e.g., "sqd 0" -> "SQD0", "x" -> "X")
        normalized_request = name.replace(" ", "").replace("_", "").upper()

        # Find the matching column in the Enum
        for col in UnitColumn:
            normalized_col = col.name.replace("_", "").upper()
            if normalized_col == normalized_request:
                # Update the raw list
                self.raw[col] = str(value)
                return


    @classmethod
    def create_default(cls: type[Self],
                       unit_id: int = 0,
                       name: str = "",
                       unit_type: int = 0,
                       nat: int = 0) -> Self:
        """
        Factory method to create a default 380-column UnitRow.
        """
        # Start with ID, Name, Type, Nat
        row: list[str] = [str(unit_id), name, str(unit_type), str(nat)]

        # Fill the remaining 376 columns with zeroes
        row.extend(["0"] * 376)

        return cls(row)


    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any])->Self:
        # Convert dict to a 380-column list first
        headers = gen_unit_column_names()
        row_list = [str(data.get(h, "0")) for h in headers]
        return cls(row_list)


    def reorder_slots(self: Self, source_slot: int, target_slot: int) -> None:
        """
        Moves an entire squad attribute block (WID, Qty, and other interleaved stats)
        from source_slot to target_slot, shifting other blocks accordingly.
        """
        if not (0 <= source_slot < U_SQD_SLOTS and 0 <= target_slot < U_SQD_SLOTS):
            raise IndexError(f"Slot index out of range: {source_slot} -> {target_slot}")

        # Unit files use interleaved blocks of size ATTRS_PER_SQD (8)
        start_idx = U_SQD0_COL
        stride = U_ATTRS_PER_SQD
        num_slots = U_SQD_SLOTS
        end_of_blocks = start_idx + (num_slots * stride)

        # 1. Extract the section of the list containing all 32 squad blocks
        all_squad_data = self.raw[start_idx:end_of_blocks]

        # 2. Chunk them into a list of 8-element blocks
        blocks = [all_squad_data[i:i + stride] for i in range(0, len(all_squad_data), stride)]

        # 3. Perform the move
        block_to_move = blocks.pop(source_slot)
        blocks.insert(target_slot, block_to_move)

        # 4. Flatten and write back to the raw list
        self.raw[start_idx:end_of_blocks] = [item for sublist in blocks for item in sublist]

        # 5. Re-sync attributes (so unit.SQD_0 matches the new list state)
        self.load_row(self.raw)

