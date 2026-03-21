# Primary Linkages
# ----------------
# Unit.TYPE   -> Ob.ID       (Which TOE/OB template does this unit use?)
# Ob.SQD_0    -> Gnd.ID      (Which Ground Element is in this slot?)
# Gnd.WPN_0   -> Dev.ID      (Which Device/Weapon is the Ground Element carrying?)

import csv
from pathlib import Path
from typing import Any, Optional
from collections.abc import Callable
import pytest

# Internal package imports
from wite2_tools.config import ENCODING_TYPE
from wite2_tools.models import (
    # Unit Entities
    UnitRow,
    gen_unit_column_names,
    U_ATTRS_PER_SQD, U_SQD_SLOTS,
    U_SQD0_COL, U_SQD_NUM0_COL,
    # OB Entities
    gen_ob_column_names,
    ObColumn, ObRow,
    O_SQD_SLOTS,
    # Ground Entities
    gen_gnd_column_names,
    GndColumn, GndRow,
    G_WPN_SLOTS,
    # Device Entities
    gen_device_column_names,
    DevRow,
    # Aircraft
    gen_aircraft_column_names,
    gen_default_aircraft_row
)

from wite2_tools.utils.get_name import (
    _build_ground_elem_lookup,
    _build_ob_lookup
)
from wite2_tools.core.group_units_by_ob import (
    _group_units_by_ob,
)
from wite2_tools.utils.get_valid_ids import (
    get_valid_ob_ids,
    get_valid_ob_upgrade_ids,
    get_valid_ground_elem_ids,
    get_valid_unit_ids
)


@pytest.fixture(autouse=True, name="clear_caches")
def clear_all_caches()->None:
    """
    Automatically runs before every test to clear the @cache decorators.
    This guarantees that state does not leak between different tests.
    """
    _group_units_by_ob.cache_clear()
    _build_ob_lookup.cache_clear()
    _build_ground_elem_lookup.cache_clear()
    get_valid_ob_ids.cache_clear()
    get_valid_ob_upgrade_ids.cache_clear()
    get_valid_ground_elem_ids.cache_clear()
    get_valid_unit_ids.cache_clear()


# ---------------------------------------------------------
# HELPER FUNCTIONS FOR PADDED ROW GENERATION
# ---------------------------------------------------------

def create_unit_row(
    uid: int,
    name: str,
    utype: int,
    nat: int,
    squads: list[tuple[int, str, str]]
) -> UnitRow:
    """
    Generates a 380-column UnitRow with populated squad slots using direct index access.

    Args:
        uid: Unit ID
        name: Unit Name
        utype: TOE/OB ID
        nat: Nationality
        squads: List of (slot_index, weapon_id, quantity)
    """
    # 1. Create the base object with 380 columns
    unit = UnitRow.create_default(uid, name, utype, nat)

    # 2. Access the underlying list directly
    # Note: We use unit.raw which returns the self.raw list
    for slot_idx, wid, qty in squads:
        if 0 <= slot_idx < U_SQD_SLOTS:
            # Calculate the exact CSV column indices

            squad_col_idx = U_SQD0_COL + (slot_idx * U_ATTRS_PER_SQD)
            num_col_idx = U_SQD_NUM0_COL + (slot_idx * U_ATTRS_PER_SQD)

            unit.raw[squad_col_idx] = str(wid)
            unit.raw[num_col_idx] = str(qty)

    # 3. Synchronize the object attributes
    # Because we modified the 'raw' list directly, we call _load_row
    # to refresh unit.SQD_0, unit.SQD_NUM_0, etc. from the new list values.
    unit.load_row(unit.raw)

    return unit


# pylint: disable=too-many-arguments, too-many-positional-arguments
def create_ob_row(
    ob_id: int,
    name: str,
    suffix: str = "0",
    nat: int = 1,
    first_year: int = 1941,
    first_month: int = 1,
    last_year: int = 1945,
    last_month: int = 12,
    ob_type: int = 0,
    upgrade: int = 0,
    squads: Optional[list[tuple[int, str, str]]] = None
) -> ObRow:
    """
    Generates a populated ObRow object representing a _ob.csv row.
    Matches the schema: Metadata -> 32 sqd slots -> 32 sqdNum slots.
    """
    row: ObRow = ObRow.create_default(ob_id, name, suffix)

    # Clean, Pythonic property assignments!
    row.NAT = nat
    row.FIRST_YEAR = first_year
    row.FIRST_MONTH = first_month
    row.LAST_YEAR = last_year
    row.LAST_MONTH = last_month
    row.TYPE = ob_type
    row.UPGRADE = upgrade

    # Slot Mapping
    if squads:
        for slot_idx, g_id, qty in squads:
            if 0 <= slot_idx < O_SQD_SLOTS:
                # We still use raw here because we are dynamically iterating
                # through the slots using the IntEnum math.
                row.raw[ObColumn.SQD_0 + slot_idx] = str(g_id)
                row.raw[ObColumn.SQD_NUM_0 + slot_idx] = str(qty)
    return row



def create_gnd_row(
    wid: int,
    name: str,
    gtype: int = 1,
    nat: int = 1,
    men: int = 10,
    size: int = 1,
    weapons: list[tuple[int, str, str]] | None = None
) -> GndRow:
    """
    Generates a 92-column _ground.csv row mapping weapons/qtys.
    """
    row: GndRow = GndRow.create_default(wid, name, gtype)

    row.ID_2 = wid
    row.NAT = nat

    # We must ensure MEN and SIZE are populated for your audit scripts
    row.MEN = men
    row.SIZE = size
    if weapons:
        for slot_idx, wep_id, qty in weapons:
            if slot_idx < G_WPN_SLOTS:
                row.raw[GndColumn.WPN_0 + slot_idx] = wep_id
                row.raw[GndColumn.WPN_NUM_0 + slot_idx] = qty

        row.load_row(row.raw)

    return row


def create_dev_row(
    dev_id: int,
    name: str,
    pen: int = 0,
    load: int = 0
) -> DevRow:
    """
    Generates a 25-column _device.csv row based on DevColumn indices.
    """
    row = DevRow.create_default(dev_id, name)
    row.PEN = pen
    row.LOAD_COST = load
    return row


# ---------------------------------------------------------
# FACTORY FIXTURES (For dynamic file generation in tests)
# ---------------------------------------------------------
@pytest.fixture
def make_ob_csv(tmp_path: Path) -> Callable[..., Path]:
    """
    Factory fixture to generate a mock _ob.csv file for testing.
    """
    def _make(filename: str, rows_data: list[dict]) -> Path:
        file_path = tmp_path / filename
        headers: list[str] = gen_ob_column_names()

        with open(file_path, "w", newline="", encoding=ENCODING_TYPE) as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for data in rows_data:
                row = create_ob_row(
                    ob_id=data.get("id") or data.get("ob_id", 0),
                    name=data.get("name",""),
                    suffix=data.get("suffix", ""),
                    nat=data.get("nat", 1),
                    first_year=data.get("firstYear", 1941),
                    first_month=data.get("firstMonth", 1),
                    last_year=data.get("lastYear", 1945),
                    last_month=data.get("lastMonth", 12),
                    ob_type=data.get("type", 1),
                    upgrade=data.get("upgrade", 0),
                    squads=data.get("squads", [])
                )

                writer.writerow(row.raw)

        return file_path
    return _make


@pytest.fixture
def make_unit_csv(tmp_path: Path) -> Callable[..., Path]:
    """
    Factory to generate a custom 380-column _unit.csv file using UnitRow.
    """
    def _make(
        filename: str = "mock_unit.csv",
        rows_data: list[dict[str, Any]] | None = None
    ) -> Path:
        file_path: Path = tmp_path / filename
        headers: list[str] = gen_unit_column_names()

        # Define fields handled by the create_unit_row constructor
        core_fields = {"id", "name", "type", "nat", "squads"}

        with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            if rows_data:
                for data in rows_data:
                    # 1. Create the base UnitRow with core identity and squads
                    unit = create_unit_row(
                        uid=int(data.get("id", 0)),
                        name=str(data.get("name", "Unk")),
                        utype=int(data.get("type", 1)),
                        nat=int(data.get("nat", 1)),
                        squads=data.get("squads", [])
                    )

                    # 2. Apply any other specific attributes (x, y, hhq, etc.)
                    # This allows tests to inject custom values for any column
                    for key, val in data.items():
                        if key not in core_fields:
                            # Use the UnitRow attribute logic to update the raw
                            # list
                            setattr(unit, key, val)

                    # 3. Write the underlying list to the CSV
                    writer.writerow(unit.raw)

        return file_path
    return _make


@pytest.fixture
def make_ground_csv(tmp_path: Path) -> Callable[..., Path]:
    """
    Factory to generate a custom _ground.csv file.
    """
    def _make(
        filename: str = "mock_ground.csv",
        rows_data: list[dict[str, Any]] | None = None
    ) -> Path:
        file_path: Path = tmp_path / filename
        headers = gen_gnd_column_names()

        core_fields = {"id", "name", "type", "nat", "men", "size", "weapons"}

        with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            if rows_data:
                for data in rows_data:
                    gnd = create_gnd_row(
                        wid=int(data.get("id", 0)),
                        name=data.get("name", "Unknown Element"),
                        gtype=int(data.get("type", 1)),
                        nat=int(data.get("nat", 1)),
                        men=int(data.get("men", 10)),
                        size=int(data.get("size", 1)),
                        weapons=data.get("weapons", [])
                    )

                    for key, val in data.items():
                        if key not in core_fields:
                            # Use the UnitRow attribute logic to update the raw
                            # list
                            setattr(gnd, key, val)

                    writer.writerow(gnd.raw)

        return file_path
    return _make


@pytest.fixture
def make_device_csv(tmp_path: Path) -> Callable[..., Path]:
    """
    Factory to generate a custom _device.csv file.
    """
    def _make(
        filename: str = "shared_mock_device.csv",
        rows_data: list[dict[str, Any]] | None = None
    ) -> Path:
        file_path: Path = tmp_path / filename
        headers = gen_device_column_names()

        core_fields = {"id", "name", "pen", "load"}

        with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            if rows_data:
                for data in rows_data:

                    dev = create_dev_row(
                        dev_id=int(data.get("id", 0)),
                        name=data.get("name", "Unknown Device"),
                        pen=int(data.get("pen", 0)),
                        load=int(data.get("load", 0))
                    )

                    for key, val in data.items():
                        if key not in core_fields:
                            # Use the UnitRow attribute logic to update the raw
                            # list
                            setattr(dev, key, val)


                    writer.writerow(dev.raw)
        return file_path
    return _make


@pytest.fixture
def make_aircraft_csv(tmp_path: Path) -> Callable[..., Path]:
    """
    Factory to generate a custom _aircraft.csv file.
    """
    def _make(
        filename: str = "mock_aircraft.csv",
        rows_data: list[dict[str, Any]] | None = None
    ) -> Path:
        file_path: Path = tmp_path / filename
        headers = gen_aircraft_column_names()

        with open(file_path, 'w', newline='', encoding=ENCODING_TYPE) as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            if rows_data:
                for data in rows_data:
                    # Generate the default 322-column row
                    row = gen_default_aircraft_row(
                        aircraft_id=int(data.get("id", 0)),
                        name=data.get("name", "Unknown Aircraft"),
                        nat=int(data.get("nat", 1))
                    )

                    # Dynamically overwrite any specific columns passed in the
                    # dict (e.g., "wpn 0": "101", "maxSpeed": "550")
                    for key, value in data.items():
                        if key not in ["id", "name", "nat"] and key in headers:
                            row[headers.index(key)] = str(value)

                    writer.writerow(row)
        return file_path
    return _make


@pytest.fixture
def mock_corrupted_unit_csv(make_unit_csv: Callable[..., Path])->Path:
    """
    Generates a unit file where a 'Ghost Unit' has quantity (50)
    but an empty equipment ID (0).
    """
    return make_unit_csv(
        filename="corrupted_units.csv",
        rows_data=[
            {
                "id": "1", "name": "Valid Unit", "type": "10", "nat": "1",
                "squads": [(0, "105", "10")]  # Valid: ID 105, Qty 10
            },
            {
                "id": "2", "name": "Filler", "type": "10", "nat": "1"
            },
            {
                "id": "3", "name": "Filler", "type": "10", "nat": "1"
            },
            {
                "id": "4", "name": "Filler", "type": "10", "nat": "1"
            },
            {
                "id": "5", "name": "Ghost Unit", "type": "10", "nat": "1",
                "squads": [(0, "0", "50")]    # Corrupted: ID 0, Qty 50
            },
        ]
    )

@pytest.fixture
def mock_files(
    mock_unit_csv: Path,
    mock_ob_csv: Path,
    mock_ground_csv: Path
) -> tuple[Path, Path, Path]:
    """
    Returns the master triplet of mock files.
    Note: Ensure mock_ob_csv and mock_unit_csv are updated to include
    the 125% threshold test cases.
    """
    return mock_unit_csv, mock_ob_csv, mock_ground_csv

# ---------------------------------------------------------
# SHARED STATIC FIXTURES (The "One Big Fixture" pattern)
# ---------------------------------------------------------

@pytest.fixture(name="mock_unit_csv")
def mock_unit_csv_fixture(make_unit_csv: Callable[..., Path]) -> Path:
    """Master _unit.csv mock with edge cases and decoys."""
    return make_unit_csv(
        filename="shared_mock_unit.csv",
        rows_data=[
# --- Orphan Detection Data ---
            {
                "id": "10", "name": "1st Panzer", "type": "10",
                "nat": "1"
            }, # Uses OB 10
            {
                "id": "11", "name": "1st Infantry", "type": "40",
                "nat": "1"
            }, # Uses OB 40
            {
                "id": "12", "name": "1st Alpine", "type": "70",
                "nat": "3"
            }, # Uses OB 70
# --- Data for Strength Auditing (IDs 1-9) ---
            {
                "id": "1", "name": "1st Div (Pass)", "type": "1", # Links to OB 1
                "nat": "1", "squads": [(0, "100", "10")]           # 10/10 = 100%
            },
            {
                "id": "2", "name": "2nd Div (Fail)", "type": "1", # Links to OB 1
                "nat": "1", "squads": [(0, "100", "15")]           # 15/10 = 150% (>125%)
            },
            {
                "id": "3", "name": "4th Panzer", "type": "10",
                "nat": "1", "squads": [(0, "105", "10"), (1, "106", "5")]
            },
            {
                "id": "4", "name": "10th Panzer", "type": "10",
                "nat": "1", "squads": [(0, "105", "5")]
            },
            {
                "id": "5", "name": "3rd Infantry", "type": "20",
                "nat": "2", "squads": [(0, "106", "10")]
            },
            {
                "id": "0", "name": "Empty Data", "type": "0",
                "nat": "1", "squads": [(0, "105", "100")]
            },
# --- Legacy/Logical Audit Data (IDs 100+) ---
            {
                "id": "100", "name": "1st Panzer", "type": "1",
                "nat": "1", "squads": [(2, "55", "10"), (5, "42", "10")]
            },
            {
                "id": "101", "name": "2nd Panzer", "type": "1",
                "nat": "1", "squads": [(0, "105", "10"), (1, "42", "5")]
            },
            {
                "id": "102", "name": "1st Infantry", "type": "50",
                "nat": "2", "squads": [(2, "105", "10"), (3, "106", "10")]
            },
            {
                "id": "103", "name": "2nd Infantry", "type": "50",
                "nat": "1", "squads": [(0, "999", "50")]
            },
            {
                "id": "104", "name": "Boundary Unit", "type": "99",
                "nat": "1", "squads": [(31, "105", "1")]
            },
            {
                "id": "105", "name": "Ghost Unit", "type": "0",
                "nat": "0", "squads": [(0, "105", "100")]
            },
# --- Nationality Data (IDs 201-205) ---
            {
                "id": "201", "name": "1st Panzer (DE)", "type": "10",
                "nat": "1"
            }, # German
            {
                "id": "202", "name": "2nd Panzer (DE)", "type": "10",
                "nat": "1"
            }, # German
            {
                "id": "203", "name": "1st Finnish", "type": "10",
                "nat": "2"
            },     # Finnish
            {
                "id": "204", "name": "1st Italian", "type": "20",
                "nat": "3"
            },     # Italian
            {
                "id": "205", "name": "Ghost Unit", "type": "0",
                "nat": "1"
            },
# --- Valid ID Parsing Data (IDs 500, 502) ---
            {
                "id": "500", "name": "Validated Div A", "type": "10",
                "nat": "1"
            },
            {
                "id": "502", "name": "Validated Div B", "type": "10",
                "nat": "1"
            },
# Data for test_group_units_by_ob.py
            {
                "id": "60", "name": "1st Panzer", "type": "45",
                "nat": "1"
            },
            {
                "id": "61", "name": "2nd Panzer", "type": "45",
                "nat": "1"
            },
            {
                "id": "63", "name": "3rd Infantry", "type": "30",
                "nat": "2"
            },
            {
                "id": "64", "name": "Ghost Unit", "type": "0",
                "nat": "1"
            },
        ]
    )



@pytest.fixture(name="mock_ob_csv")
def mock_ob_csv_fixture(make_ob_csv: Callable[..., Path]) -> Path:
    """
    Master _ob.csv (TOE) mock updated for orphan detection.
    """
    return make_ob_csv(
        filename="shared_mock_ob.csv",
        rows_data=[
            # --- Orphan Detection Data ---
            {
                "id": "10", "name": "Panzer TOE", "suffix": "41",
                "nat": "1",
                "upgrade": "20"
            },
            {
                "id": "12", "name": "Valid TOE",
                "nat": "1",
                "upgrade": "0"
            },
            {   "id": "20", "name": "Panzer TOE", "suffix": "42",
                "nat": "1",
                "upgrade": "0"
            },
            {
                "id": "30", "name": "Orphan Div TOE", "suffix": "A",
                "nat": "1",
                "upgrade": "0"
            },
            {
                "id": "40", "name": "Infantry TOE", "suffix": "41",
                "nat": "1",
                "upgrade": "50"
            },
            {
                "id": "50", "name": "Infantry Mot TOE", "suffix": "42",
                "nat": "1",
                "upgrade": "60"
            },
            {
                "id": "60", "name": "Infantry TOE", "suffix": "43",
                "nat": "1",
                "upgrade": "0"
            },
            {
                "id": "70", "name": "Italian Div TOE", "suffix": "41",
                "nat": "3",
                "upgrade": "0"
            },
            # --- Existing Logic Data ---
            {
                "id": "1", "name": "Panzer Div TOE",
                "nat": "1",
                "squads": [(0, "55", "10")]
            },
            {
                "id": "51", "name": "Infantry Div TOE",
                "nat": "1",
                "squads": [(0, "105", "10")]
            },
            {
                "id": "33", "name": "Mtn Inf Div TOE",
                "nat": "1",
                "squads": [(0, "100", "10")] # Authorized limit is 10
            },
            {
                "id": "99", "name": "Garrison TOE",
                "nat": "1",
                "squads": [(0, "999", "5")]
            },
            {
                "id": "11", "name": "Reorder Target TOE",
                "nat": "1",
                "squads": [(2, "500", "15")]
            }
        ]
    )


@pytest.fixture(name="mock_ground_csv")
def mock_ground_csv_fixture(make_ground_csv: Callable[..., Path]) -> Path:
    """
    Master _ground.csv mock testing gaps and references.
    """
    return make_ground_csv(
        filename="shared_mock_ground.csv",
        rows_data=[
        # --- NEW: Data for Strength Auditing ---
            {
                "id": "100", "name": "Rifle Squad", "type": "1",
                "nat" : "1",
                "men": "10", "size": "1",
                "weapons": []
            },
            # --- Standard Data ---
            {
                "id": "105", "name": "Panzer IV",
                "weapons": [(0, "10", "1"), (1, "11", "1")]
            },
            {
                "id": "500", "name": "Panther",
                "weapons": [(0, "20", "1"), (1, "21", "1"), (2, "22", "1")]
            },
            # --- Gapped Data (For remove_weapon_gaps tests) ---
            {
                "id": "1", "name": "Gap at Index 0",
                "weapons": [(1, "500", "2")]
            },
            {
                "id": "2", "name": "Multiple Gaps",
                "weapons": [(2, "100", "1"), (5, "200", "4")]
            },
            {
                "id": "3", "name": "Perfectly Packed",
                "weapons": [(0, "300", "1")]
            },
            {
                "id": "4", "name": "Gap at Index 2",
                "weapons": [(0, "10", "20"), (1, "20", "20"), (3, "330", "20")]
            },
            {
                "id": "42", "name": "Tiger I",
                "weapons": [(0, "10", "1"), (5, "11", "1"), (8, "12", "1")]
            },
            {
                "id": "51", "name": "Panzer III", "type": "10",
                "nat": "1",
                "weapons": [(0, "105", "10"), (1, "106", "5")]
            },
            {
                "id": "52", "name": "Stug IIIG", "type": "10",
                "nat": "1",
                "weapons": [(0, "105", "5")]
            },
            {
                "id": "53", "name": "Pioneer", "type": "20",
                "nat": "2",
                "weapons": [(0, "106", "10")]
            },
            {
                "id": "0", "name": "Empty Data", "type": "0",
                "nat": "1",
                "weapons": [(0, "105", "100")]
            },
# --- Data merged from test_count_global_unit_inventory.py ---
            {
                "id": "201", "name": "Panzer III", "type": "1",
                "weapons": []
            },
            {
                "id": "202", "name": "Infantry Sqd", "type": "1",
                "weapons": []
            },
# --- Logical Audit Data (Safe for general parsing) ---
            {
                "id": "203", "name": "Valid Sqd", "type": "1",
                "men": "10",
                "weapons": []
            },
            {
                "id": "204", "name": "Error Sqd", "type": "1",
                "men": "0",
                "weapons": [] # Audit target: Infantry with 0 men
            }
        ]
    )

@pytest.fixture(name="mock_device_csv")
def mock_device_csv_fixture(make_device_csv: Callable[..., Path]) -> Path:
    """
    Master _device.csv mock for general testing.
    """
    return make_device_csv(
        filename="shared_mock_device.csv",
        rows_data=[
            {
                "id": "1", "name": "Pak 40", "pen": "150"
            },
            {
                "id": "2", "name": "Pak 36", "pen": "50"
            },
            {
                "id": "3", "name": "KwK 40", "pen": "100"
            }
        ]
    )


@pytest.fixture(name="mock_aircraft_csv")
def mock_aircraft_csv_fixture(make_aircraft_csv: Callable[..., Path]) -> Path:
    """
    Master _aircraft.csv mock for general testing.
    """
    return make_aircraft_csv(
        filename="shared_mock_aircraft.csv",
        rows_data=[
            {
                "id": "1", "name": "Bf 109G-2", "nat": "1",
                "wpn 0": "101", "wpn 1": "102"
            },
            {
                "id": "2", "name": "Fw 190A-4", "nat": "1",
                "wpn 0": "105"
            },
            {
                "id": "3", "name": "Yak-9", "nat": "2",
                "wpn 0": "200"
            }
        ]
    )