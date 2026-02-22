"""
wite2_tools: A specialized toolkit for WiTE2 data management.

This package provides a modular framework for auditing, scanning, and
manipulating game CSV data (TOE(OB), Unit, and Ground Elements). It
centralizes configuration, path management, and data generation for
scenario development and modding.
"""
__version__ = "0.3.0"
__author__ = "Mark L. Short"
__date__ = "2026-02-19"

from .config import ENCODING_TYPE
from .constants import (
    MAX_SQUAD_SLOTS,
    MAX_WPN_SLOTS,
    GroundColumn,
    UnitColumn,
    ObColumn,
)
from .paths import (
    CONF_OB_FULL_PATH,
    CONF_UNIT_FULL_PATH,
    CONF_GROUND_FULL_PATH,
)
from .generator import read_csv_dict_generator, read_csv_list_generator

__all__ = [
    'ENCODING_TYPE',
    'MAX_SQUAD_SLOTS',
    'MAX_WPN_SLOTS',
    'GroundColumn',
    'UnitColumn',
    'ObColumn',
    'CONF_OB_FULL_PATH',
    'CONF_UNIT_FULL_PATH',
    'CONF_GROUND_FULL_PATH',
    'read_csv_dict_generator',
    'read_csv_list_generator'
]
