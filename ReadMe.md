# wite2_tools

[![Build Status](https://github.com/mlshort/wite2_tools/actions/workflows/python-app.yml/badge.svg)](https://github.com/mlshort/wite2_tools/actions)
[![Pylint](https://github.com/mlshort/wite2_tools/actions/workflows/pylint.yml/badge.svg?event=push)](https://github.com/mlshort/wite2_tools/actions/workflows/pylint.yml)


**Version:** 0.3.1
**Author:** Mark L. Short

A specialized, Python-based toolkit for managing, modifying, and analyzing
Gary Grigsby's *War in the East 2 (WiTE2)* CSV data files.

This package is designed for scenario designers and modders who need to
perform bulk updates, trace complex upgrade chains, and ensure data integrity
across massive game databases without risking file corruption.

---

## 🚀 Core Capabilities

The framework is divided into five main sub-packages based on functionality:

* **Modifiers:** Safely perform bulk data mutations on `_unit`, `_ob`, and
  `_ground` CSVs. Uses an atomic file-replacement wrapper to ensure
  original files are only overwritten if the script completes successfully.
* **Data Generation & Reporting:** Generate scenario insights, map global
  equipment inventories, trace TOE (Table of Organization and Equipment)
  upgrade chains, and identify unreferenced "orphan" templates.
* **Auditing:** Batch evaluate data files for structural integrity, logical
  consistency, and duplicate IDs. Automatically detects "Ghost Squads" and
  out-of-bounds map coordinates to prevent game crashes.
* **Scanners:** High-performance queries to locate specific ground elements,
  units, or excess logistical stores (e.g., ammo, fuel > 5x need) without
  modifying the source files.
* **Utilities:** Memory-efficient CSV streaming generators, robust encoding
  detection (`ISO-8859-1`), centralized logging, and fast ID-to-string lookup
  caching using strongly typed `IntEnum` column mappings.

---

## ⚙️ Configuration & Setup

1. **Clone the repository** to your local workspace.
2. **Install requirements:** Ensure you have `pytest` installed for running
   the test suite, and `chardet` for the encoding detection utility.
   ```cmd
   pip install -r requirements.txt
   ```
3. **Set Game Data Paths:** By default, the toolset expects the standard Steam
   installation path for WiTE2. The toolkit must resolve the location of your
   WiTE2 CSV files (e.g., _unit.csv, _ob.csv, _ground.csv). You can configure
   this in two ways:

   * Option A: CLI Configuration (Recommended): Use the config command to save
   your target directory to a local settings.ini file. This avoids manual code
   changes.

    ```cmd
    python -m wite2_tools.cli config --set-path "C:\Path\To\Your\WiTE2\CSV"
    ```

   * Option B: Manual Path Update: Open src\wite2_tools\paths.py and update the
   GAME_DATA_PATH variable to your specific installation directory.

---
## 💡 Best Practices & Recommendations

**Always Test on Exported Data First!**
Before executing any modifiers against your active game data or live mod files,
it is highly recommended to experiment in a safe environment:

1. Open the **WiTE2 Editor**.
2. Navigate to the **CSV Tab** and export a fresh copy of your scenario's
   data (`_ob.csv`, `_unit.csv`, and `_ground.csv`) files.
3. Copy these exported files into this project's local `\data` subdirectory.
4. Temporarily update your `src\wite2_tools\paths.py` to point to these local
   files (or use the CLI's optional path arguments) to safely test commands,
   verify logic, and review the resulting outputs without risking your
   master game files.

---

## 🛠️ Unified CLI Usage

The package provides a unified Command-Line Interface (`cli.py`) for executing
all tools. Target file paths are resolved automatically via `paths.py`
unless explicitly overridden via optional arguments.

*(Note: Depending on your Windows Python installation, you may need to use `py`
instead of `python` in your Command Prompt or PowerShell).*

Once installed, you can access the toolkit from your terminal via the unified
command-line interface `wite2-tools` (or by running the module directly with
`python -m wite2_tools.cli`).

### 1. Generation Tools (`gen-*`)
Tools for generating reports and cross-referencing data.
* **`gen-orphans`**: Identifies unreferenced (orphaned) TOE(OB) templates and
  finds units pointing to invalid TOE(OB) IDs. Includes full upgrade-chain
  tracing.
  * *Example:* `python -m wite2-tools.cli gen-orphans --nat-codes 1 3`
  (Filters the scan to Germany(1) and Italy(3) nationality codes).
* **`gen-inventory`**: Generates a comprehensive inventory report of elements.
* **`gen-groups`**: Analyzes and maps organizational groups.
* **`gen-chains`**: Maps and validates unit/TOE(OB) upgrade chains.

### 2. Auditing Tools (`audit-*`)
Tools for verifying the integrity of your WiTE2 database files.
* **`audit-ground`**: Scans `_ground.csv` for errors.
* **`audit-unit`**: Scans `_unit.csv` for broken dependencies or invalid stats.
* **`audit-ob`**: Scans `_ob.csv` for malformed templates.
* **`audit-batch`**: Runs a comprehensive audit across multiple target files.

### 3. Modding & Manipulation Tools (`mod-*`)
* **`mod-compact-wpn`**: Compacts weapon data arrays.
* **`mod-reorder-ob`**: Moves a Ground Element to a new slot for a TOE(OB).
* **`mod-reorder-unit`**: Moves a Ground Element to a new slot for a Unit.
* **`mod-replace-elem`**: Batch replaces specific elements within templates.
* **`mod-update-num`**: Updates numerical stats across specified datasets.

### 4. Scanning Tools (`scan-*`)
Tools for quickly finding specific data points or anomalies.
* **`scan-ob`**: Locates all Ground Elements matching a WID within OBs.
* **`scan-unit`**: Locates all Ground Elements matching a WID within Units.
* **`scan-excess`**: Locates units with excessive logistical stores.

### 5. Configuration
* **`config`**: Manage default data directories and settings for the CLI tools.

**CLI Examples:**
```cmd
python -m wite2_tools.cli config
python -m wite2-tools.cli config --set-path "C:\DevProjects\wite2_tools\TestMods"
python -m wite2_tools.cli scan-excess --operation fuel
python -m wite2_tools.cli gen-chains --nat-codes 1 3
```

**Providing Custom Paths in Windows:**
If you provide a custom file path that contains spaces, you **must** wrap it in
double quotes for the Windows command line to read it properly:
```cmd
python -m wite2_tools.cli compact-weapons --ground-file "C:\My WiTE2 Mods\MyCustomMod_ground.csv"
```

---

## 🧪 Testing

This project maintains a robust suite of isolated `pytest` fixtures. To run
the tests and verify logical consistency before executing on your master game
files:

```cmd
pytest src\tests\
```

Test data uses mock CSVs generated in a temporary workspace to ensure your
actual game files remain untouched during development.

---

## 📝 Logs & Exports

All operations automatically generate a timestamped log file
(e.g., `wite2_20260217_1330.log`) in the local `\logs` directory.
Analytical data (like TOE(OB) chains) are saved to the `\exports` directory.
