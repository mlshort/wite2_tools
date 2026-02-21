"""
WiTE2 Path Configuration and Management
=======================================

This module centralizes directory and file path management for the
`wite2_tools` package. It dynamically resolves project-relative folders
and provides absolute paths to the external War in the East 2 game data.

Core Features:
--------------
* Workspace Initialization: Automatically locates the project root and
  ensures required local directories (`data/`, `exports/`, `logs/`) exist.
* Game Data Linking: Defines the absolute path to the WiTE2 Steam
  installation directory for direct file interaction.
* Centralized Exports: Exposes standard configuration variables
  (e.g., `CONF_UNIT_FULL_PATH`) used by all other modules, allowing
  developers to easily swap between live game data and local test files.
"""
import os

# ==========================================
# 1. DYNAMIC LOCAL PATHS (Project Relative)
# ==========================================
# Dynamically calculates the root directory of your project

_THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_THIS_FILE_DIR)
PROJECT_ROOT = os.path.dirname(_SRC_DIR)

LOCAL_DATA_PATH = os.path.join(PROJECT_ROOT, "data")
LOCAL_EXPORTS_PATH = os.path.join(PROJECT_ROOT, "exports")
LOCAL_LOG_PATH = os.path.join(PROJECT_ROOT, "logs")

# Auto-create local directories if they don't exist yet
os.makedirs(LOCAL_DATA_PATH, exist_ok=True)
os.makedirs(LOCAL_EXPORTS_PATH, exist_ok=True)
os.makedirs(LOCAL_LOG_PATH, exist_ok=True)


# ==========================================
# 2. EXTERNAL GAME DATA PATH
# ==========================================
# Allows users to set a custom path via environment variables (.env),
# otherwise defaults to the standard Windows Steam installation.
GAME_DATA_PATH = os.getenv(
    "WITE2_DATA_PATH",
    r"C:\Program Files (x86)\Steam\steamapps\common\"Gary Grigsby's War in the East 2\Dat\CSV"
)

# ==========================================
# 3. FILENAMES
# ==========================================
_GC41_OB_FILENAME = "1941 Campaign_ob.csv"
_GC41_UNIT_FILENAME = "1941 Campaign_unit.csv"
_GC41_GROUND_FILENAME = "1941 Campaign_ground.csv"

_GENERIC_OB_FILENAME = "_ob.csv"
_GENERIC_UNIT_FILENAME = "_unit.csv"
_GENERIC_GROUND_FILENAME = "_ground.csv"

# Names used for modded CSV files
# Users are expected to replace these with their own custom scenario filenames
_MOD_OB_FILENAME = "MyCustomMod_ob.csv"
_MOD_UNIT_FILENAME = "MyCustomMod_unit.csv"
_MOD_GROUND_FILENAME = "MyCustomMod_ground.csv"

# ==========================================
# 4. CONSTRUCTED FULL PATHS (Safe Joins)
# ==========================================
_GC41_OB_FULL_PATH = os.path.join(GAME_DATA_PATH, _GC41_OB_FILENAME)
_GC41_UNIT_FULL_PATH = os.path.join(GAME_DATA_PATH, _GC41_UNIT_FILENAME)
_GC41_GROUND_FULL_PATH = os.path.join(GAME_DATA_PATH, _GC41_GROUND_FILENAME)

_OB_FULL_PATH = os.path.join(GAME_DATA_PATH, _MOD_OB_FILENAME)
_UNIT_FULL_PATH = os.path.join(GAME_DATA_PATH, _MOD_UNIT_FILENAME)
_GROUND_FULL_PATH = os.path.join(GAME_DATA_PATH, _MOD_GROUND_FILENAME)

# LOCAL Paths are for testing
_LOCAL_OB_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _MOD_OB_FILENAME)
_LOCAL_UNIT_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _MOD_UNIT_FILENAME)
_LOCAL_GROUND_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _MOD_GROUND_FILENAME)

_LOCAL_GEN_OB_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _GENERIC_OB_FILENAME)
_LOCAL_GEN_UNIT_FULL_PATH = os.path.join(LOCAL_DATA_PATH,
                                         _GENERIC_UNIT_FILENAME)
_LOCAL_GEN_GROUND_FULL_PATH = os.path.join(LOCAL_DATA_PATH,
                                           _GENERIC_GROUND_FILENAME)

_LOCAL_GC41_OB_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _GC41_OB_FILENAME)
_LOCAL_GC41_UNIT_FULL_PATH = os.path.join(LOCAL_DATA_PATH, _GC41_UNIT_FILENAME)
_LOCAL_GC41_GROUND_FULL_PATH = os.path.join(LOCAL_DATA_PATH,
                                            _GC41_GROUND_FILENAME)

# The configured filenames used throughout Wite2_tools
CONF_OB_FULL_PATH = _LOCAL_OB_FULL_PATH
CONF_UNIT_FULL_PATH = _LOCAL_UNIT_FULL_PATH
CONF_GROUND_FULL_PATH = _LOCAL_GROUND_FULL_PATH
