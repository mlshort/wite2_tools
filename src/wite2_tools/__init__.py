"""
wite2_tools: A specialized toolkit for WiTE2 data management.

This package provides a modular framework for auditing, scanning, and
manipulating game CSV data (TOE(OB), Unit, and Ground Elements). It
centralizes configuration, path management, and data generation for
scenario development and modding.
"""
__version__ = "0.5.0"
__author__ = "Mark L. Short"
__date__ = "2026-03-02"

# Import Sub-Packages to expose them at the top level
from . import auditing
from . import core
from . import modifiers
from . import scanning
from . import utils

from . config import (
    ENCODING_TYPE,
    CONFIG_FILE_NAME,
    normalize_nat_codes,
    make_hashable
)
from . constants import (
    MAX_SQUAD_SLOTS,
    MAX_GND_WPN_SLOTS,
    GroundColumn,
    UnitColumn,
    ObColumn,
)
from . paths import (
    CONF_OB_FULL_PATH,
    CONF_UNIT_FULL_PATH,
    CONF_GROUND_FULL_PATH,
)
from .generator import (
    get_csv_list_stream,
    get_csv_dict_stream,
    CSVDictStream,
    CSVListStream
)


__all__ = [
    'auditing',
    'core',
    'modifiers',
    'scanning',
    'utils',
    'ENCODING_TYPE',
    'CONFIG_FILE_NAME',
    'normalize_nat_codes',
    'make_hashable',
    'MAX_SQUAD_SLOTS',
    'MAX_GND_WPN_SLOTS',
    'GroundColumn',
    'UnitColumn',
    'ObColumn',
    'CONF_OB_FULL_PATH',
    'CONF_UNIT_FULL_PATH',
    'CONF_GROUND_FULL_PATH',
    'get_csv_list_stream',
    'get_csv_dict_stream',
    'CSVListStream',
    'CSVDictStream'
]
