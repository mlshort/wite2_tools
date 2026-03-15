from collections.abc import Iterator
from typing import Any, List, Tuple

from wite2_tools.models.ob_schema import (
    ObColumn,
    NUM_COLS
)


class ObRow:
    """
    A dynamic representation of a WiTE2 Order of Battle (TOE).

    This class transforms raw CSV row dictionaries into objects with
    type-hinted attributes. It supports fuzzy attribute lookup (e.g.,
    ob.sqd0 or ob.SQD_0) via __getattr__.
    """
    # Type hints for standard OB fields to keep Pylance happy
    ID: int
    NAME: str
    SUFFIX: str
    NAT: int
    FIRST_YEAR: int
    FIRST_MONTH: int
    LAST_YEAR: int
    LAST_MONTH: int
    TYPE: int
    UPGRADE: int
    OB_CLASS: int
    FORM_SIZE: int

    def __init__(self, row: List[str]):
        """
        Takes a raw CSV row (list of strings) and parses it using the known
        Enum indices.
        """
        # We must use super().__setattr__ here to bypass our custom __setattr__
        # until the _raw list is actually attached to the object!
        super().__setattr__('_raw', row)

        row_len = len(row)

        for col in ObColumn:
            raw_val = row[col] if col < row_len else "0"

            try:
                val = int(raw_val)
            except (ValueError, TypeError):
                val = raw_val

            # We use super() again to avoid triggering our custom __setattr__ during init
            super().__setattr__(col.name, val)


    def __getattr__(self, item: str) -> Any:
        normalized_request = item.replace("_", "").upper()
        for actual_key, val in self.__dict__.items():
            normalized_key = actual_key.replace("_", "").upper()
            if normalized_key == normalized_request:
                return val
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


    def __setattr__(self, name: str, value: Any) -> None:
        """
        Intercepts attribute assignment to ensure that the underlying CSV _raw
        list is updated simultaneously.
        """
        # 1. Update the normal Python attribute
        super().__setattr__(name, value)

        # 2. Skip internal variables like _raw
        if name.startswith('_'):
            return

        # 3. If this matches an ObColumn, update the raw CSV list!
        try:
            # We look up the exact column index from the enum
            col_enum = ObColumn[name]
            self._raw[col_enum] = str(value)
        except KeyError:
            # If they try to set a variable that isn't a column (like temp_val), just ignore it
            pass


    @classmethod
    def create_default(cls,
                       ob_id: int = 0,
                       name: str = "",
                       suffix: str = "") -> "ObRow":
        """
        Factory method to create a blank ObRow with specified ID/Name.
        Automatically fills all other columns with "0".

        Generates a default 79-column row for an _ob.csv file.

        Args:
        ob_id (int): The ID for the OB (Column 0). Defaults to 0.
        name (str): The name of the OB (Column 1). Defaults to empty.
        suffix (str): The suffix string (Column 2). Defaults to empty.
        """
        # Determine size from the Enum to avoid hardcoding "79"
        total_cols = NUM_COLS

        # Initialize with zeroes
        row = ["0"] * total_cols

        # Set the core identity fields using the Enum indices
        row[ObColumn.ID] = str(ob_id)
        row[ObColumn.NAME] = name
        row[ObColumn.SUFFIX] = suffix

        # Return a fully initialized ObRow object
        return cls(row)


    def get_squads(self) -> Iterator[Tuple[int, int]]:
        """
        Yields (ground_element_id, quantity) by calculating offsets
        directly from the Enum indices.
        """
        # We know exactly where the blocks start
        sqd_start = ObColumn.SQD_0      # Index 15
        num_start = ObColumn.SQD_NUM_0  # Index 47

        for i in range(32):
            try:
                # Direct list access using integer offsets
                ge_id = self._raw[sqd_start + i]
                qty = self._raw[num_start + i]

                # Convert to int only when needed
                ge_id_int = int(ge_id)
                qty_int = int(qty)

                if ge_id_int > 0 and qty_int > 0:
                    yield ge_id_int, qty_int
            except (IndexError, ValueError):
                continue


    @property
    def raw(self) -> List[str]:
        """
        Returns the underlying raw CSV string list.
        """
        return self._raw


    @property
    def is_active(self) -> bool:
        """
        Evaluates if the OB is an active, deployable template in the game engine.
        Returns False for spares, placeholders, and unassigned database slots.
        """
        # Engine null check
        # (Using getattr with a fallback just in case the key is missing)
        if getattr(self, 'ID', 0) == 0:
            return False

        # Core active column checks
        if getattr(self, 'NAT', 0) == 0 or getattr(self, 'TYPE', 0) == 0 or getattr(self, 'FIRST_YEAR', 0) == 0:
            return False

        # Naming convention checks
        name = getattr(self, 'NAME', "").lower()
        suffix = getattr(self, 'SUFFIX', "").lower()

        if "empty" in name or "spare" in name:
            return False
        if "empty" in suffix or "spare" in suffix:
            return False
        return True


    def reorder_slots(self, source_slot: int, target_slot: int) -> None:
        """
        Moves an equipment ID and its corresponding quantity from source_slot
        to target_slot (0-31), shifting other elements accordingly.
        """
        # 1. Bounds check (WiTE2 OBs always have 32 slots)
        if not (0 <= source_slot < 32 and 0 <= target_slot < 32):
            raise IndexError(f"Slot index out of range: {source_slot} -> {target_slot}")

        # 2. Identify the starting offsets for the ID and Quantity blocks
        # Using the Enum directly ensures we don't care where these columns actually are.
        attribute_bases = [
            ObColumn.SQD_0,
            ObColumn.SQD_NUM_0
        ]

        for start_idx in attribute_bases:
            end_idx = start_idx + 32  # The width of the equipment block

            # Extract the relevant 32 columns as a list segment
            segment = self._raw[start_idx:end_idx]

            # Perform the move
            # pop() pulls the value out, insert() wedges it into the new position
            value_to_move = segment.pop(source_slot)
            segment.insert(target_slot, value_to_move)

            # Update the underlying raw list using slice assignment
            self._raw[start_idx:end_idx] = segment

        # 3. CRITICAL: Re-sync the object attributes
        # Since we modified self._raw, we must re-run the parser logic
        # so that ob.SQD_0, ob.SQD_1, etc., reflect the new list order.
        self.__init__(self._raw)
