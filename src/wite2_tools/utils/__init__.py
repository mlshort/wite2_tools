"""
WiTE2 Data Utilities Package
============================

A comprehensive Python toolset designed for modifying, auditing, and
analyzing Gary Grigsby's War in the East 2 (WiTE2) CSV data files.

Core Capabilities:
------------------
* Modifiers: Safely perform bulk updates on _unit and _ob CSVs using
  atomic file replacement (e.g., replacing ground elements, updating
  squad quantities, and reordering squad slots).
* Analyzers: Generate scenario insights including global inventory
  counts, TOE upgrade chains, and identification of unreferenced
  "orphan" TOE(OB) templates.
* Validators: Batch evaluate data files for structural integrity,
  logical consistency, and duplicate IDs to prevent game crashes.
* Utilities: Features memory-efficient CSV streaming generators, robust
  encoding detection, centralized logging, and comprehensive
  ID-to-string lookup caching.
"""

__version__ = "0.1.1"
__date__ = "2026-02-19"

# Expose common configuration so other modules can access it easily
from .logger import get_logger
from .parsing import parse_int
from .lookups import (
    get_nat_abbr,
    get_ob_type_code_name,
    get_device_type_name,
    get_country_name,
    get_hq_type_description,
    get_device_size_description,
    get_device_face_type_name,
    get_ground_elem_class_name,
    get_unit_special_name
)
from .get_type_name import (
    get_ob_full_name,
    get_unit_type_name,
    get_ground_elem_type_name
)
from .get_valid_ids import (
    get_valid_ground_elem_ids,
    get_valid_ob_ids,
    get_valid_ob_upgrade_ids,
    get_valid_unit_ids
)

__all__ = [
    "get_logger",
    "parse_int",
    "get_nat_abbr",
    "get_ob_type_code_name",
    "get_device_type_name",
    "get_country_name",
    "get_ob_full_name",
    "get_unit_type_name",
    "get_ground_elem_type_name",
    "get_ground_elem_class_name",
    "get_hq_type_description",
    "get_device_size_description",
    "get_device_face_type_name",
    "get_ground_elem_class_name",
    "get_unit_special_name",
    "get_valid_ground_elem_ids",
    "get_valid_ob_ids",
    "get_valid_ob_upgrade_ids",
    "get_valid_unit_ids"
]
