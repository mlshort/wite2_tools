"""
WiTE2 Data Models and Schemas.

This package centralizes the data structures, object representations, and
column schemas (Enums) used to parse and interact with WiTE2 CSV files.

By defining strict mappings for core game entities (Units, Ground Elements,
Devices, Aircraft, Airgroups, and Orders of Battle), this package provides
a strongly typed interface that eliminates the need for slow, dynamic string
lookups across the project.

It also exports abbreviated column aliases (e.g., `G_ID_COL`, `U_NAME_COL`)
to keep imports and syntax clean in downstream processing scripts.
"""

from .ob_schema import (
    OB, ObColumn,
    gen_ob_column_names,
    gen_default_ob_row,
    ELEM_BASE,
    NUM_BASE,
    NUM_COLS as O_NUM_COLS,
    SQD_SLOTS as O_SQD_SLOTS,
    ID_COL as O_ID_COL, TYPE_COL as O_TYPE_COL,
    NAT_COL as O_NAT_COL,
    NAME_COL as O_NAME_COL, SUFFIX_COL as O_SUFFIX_COL,
    UPGRADE_COL as O_UPGRADE_COL,
    FIRSTYEAR_COL as O_FIRSTYEAR_COL, FIRSTMONTH_COL as O_FIRSTMONTH_COL,
    LASTYEAR_COL as O_LASTYEAR_COL, LASTMONTH_COL as O_LASTMONTH_COL,
    SQD0_COL as O_SQD0_COL, SQD_NUM0_COL as O_SQD_NUM0_COL
)
from .unit_schema import (
    Unit, UnitColumn,
    gen_unit_column_names,
    gen_default_unit_row,
    ATTRS_PER_SQD,
    NUM_COLS as U_NUM_COLS,
    SQD_SLOTS as U_SQD_SLOTS,
    ID_COL as U_ID_COL, TYPE_COL as U_TYPE_COL,
    NAME_COL as U_NAME_COL, NAT_COL as U_NAT_COL,
    TRUCK_COL as U_TRUCK_COL, SUPPORT_COL as U_SUPPORT_COL,
    SPT_NEED_COL as U_SPT_NEED_COL, HQ_SUPPORT_COL as U_HQ_SUPPORT_COL,
    SQD0_COL as U_SQD0_COL, SQD_NUM0_COL as U_SQD_NUM0_COL
)
from .gnd_schema import (
    GndColumn,
    gen_gnd_column_names,
    gen_default_gnd_row,
    NUM_COLS as G_NUM_COLS,
    WPN_SLOTS as G_WPN_SLOTS,
    ID_COL as G_ID_COL, TYPE_COL as G_TYPE_COL,
    NAME_COL as G_NAME_COL, SIZE_COL as G_SIZE_COL, MEN_COL as G_MEN_COL
)
from .dev_schema import (
    DevColumn,
    gen_device_column_names,
    gen_default_device_row,
    NUM_COLS as D_NUM_COLS,
    ID_COL as D_ID_COL, TYPE_COL as D_TYPE_COL,
    NAME_COL as D_NAME_COL, LOAD_COST_COL as D_LOAD_COST_COL
)
from .aircraft_schema import (
    AcColumn,
    gen_aircraft_column_names,
    gen_default_aircraft_row
)
from .airgroup_schema import AirGroupColumn

__all__ = [
    # --- Ground Entities ---
    "GndColumn",
    "gen_gnd_column_names",
    "gen_default_gnd_row",
    "G_NUM_COLS",
    "G_WPN_SLOTS",
    "G_ID_COL",
    "G_TYPE_COL",
    "G_NAME_COL",
    "G_SIZE_COL",
    "G_MEN_COL",

    # --- Unit Entities ---
    "Unit",
    "UnitColumn",
    "gen_unit_column_names",
    "gen_default_unit_row",
    "ATTRS_PER_SQD",
    "U_NUM_COLS",
    "U_SQD_SLOTS",
    "U_ID_COL",
    "U_TYPE_COL",
    "U_NAME_COL",
    "U_NAT_COL",
    "U_TRUCK_COL",
    "U_SUPPORT_COL",
    "U_SPT_NEED_COL",
    "U_HQ_SUPPORT_COL",
    "U_SQD0_COL",
    "U_SQD_NUM0_COL",

    # --- OB (Order of Battle) Entities ---
    "OB",
    "ObColumn",
    "gen_ob_column_names",
    "gen_default_ob_row",
    "ELEM_BASE",
    "NUM_BASE",
    "O_NUM_COLS",
    "O_SQD_SLOTS",
    "O_ID_COL",
    "O_TYPE_COL",
    "O_NAME_COL",
    "O_SUFFIX_COL",
    "O_NAT_COL",
    "O_UPGRADE_COL",
    "O_FIRSTYEAR_COL",
    "O_FIRSTMONTH_COL",
    "O_LASTYEAR_COL",
    "O_LASTMONTH_COL",
    "O_SQD0_COL",
    "O_SQD_NUM0_COL",

    # --- Equipment/Device Entities ---
    "DevColumn",
    "gen_device_column_names",
    "gen_default_device_row",
    "D_NUM_COLS",
    "D_ID_COL",
    "D_TYPE_COL",
    "D_NAME_COL",
    "D_LOAD_COST_COL",

    # --- Aircraft ---
    "AcColumn",
    "gen_aircraft_column_names",
    "gen_default_aircraft_row",
    "AirGroupColumn",
]
