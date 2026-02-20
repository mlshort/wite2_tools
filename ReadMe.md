# wite2_tools

[![Build Status](https://github.com/mlshort/wite2_tools/actions/workflows/python-app.yml/badge.svg)](https://github.com/mlshort/wite2_tools/actions)

**Version:** 0.1.1
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
* **Analyzers (Core):** Generate scenario insights, map global equipment
  inventories, trace TOE (Table of Organization and Equipment) upgrade chains,
  and identify unreferenced "orphan" templates.
* **Validators (Auditing):** Batch evaluate data files for structural
  integrity, logical consistency, and duplicate IDs. Automatically
  detects "Ghost Squads" and out-of-bounds map coordinates to prevent game
  crashes.
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
   installation path for WiTE2.
   * Open `src\wite2_tools\paths.py`.
   * Update the `GAME_DATA_PATH` variable if your game is installed on a
     different drive or directory.
   * Set your target filenames (e.g., `_GC41_OB_FILENAME` or
     `_MOD_OB_FILENAME`).

---
## 💡 Best Practices & Recommendations

**Always Test on Exported Data First!**
Before executing any modifiers against your active game data or live mod
files, it is highly recommended to experiment in a safe environment:

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

### 1. Modifiers
* **`replace-elem`**: Replaces a Ground Element WID across the unit dataset.
* **`update-num`**: Updates squad counts for a specific Ground Element WID within a TOE(OB).
* **`reorder-unit`**: Moves a Ground Element to a new slot for a Unit.
* **`reorder-ob`**: Moves a Ground Element to a new slot for a TOE(OB).
* **`compact-weapons`**: Removes empty weapon slots in `_ground.csv`.

### 2. Auditing
* **`audit-ground`**: Scans `_ground.csv` to ensure type IDs are valid.
* **`batch-eval`**: Batch runs consistency checks on CSV folders.
* **`audit-unit`**: Runs consistency checks on a single `_unit.csv`.
* **`audit-ob`**: Runs consistency checks on a single `_ob.csv`.

### 3. Core Analytics
* **`count-inventory`**: Counts global unit equipment inventory.
* **`find-orphans`**: Identifies unreferenced TOE(OB) templates.
* **`gen-chains`**: Generates chronological TOE(OB) upgrade chains.
* **`group-units`**: Groups active units by their assigned TOE(OB) ID.

### 4. Scanning & Utilities
* **`scan-ob-elem`**: Locates a specific Ground Element WID within OBs.
* **`scan-unit-elem`**: Locates a specific Ground Element WID within Units.
* **`scan-excess`**: Locates units with excessive logistical stores.
* **`detect-encoding`**: Detects the character encoding of a specific file.

**CLI Examples:**
```cmd
python -m wite2_tools.cli scan-excess --operation fuel
python -m wite2_tools.cli gen-chains --nat-codes 1 3
```

**Providing Custom Paths in Windows:**
If you provide a custom file path that contains spaces, you **must** wrap it in
double quotes for the Windows command line to read it properly:
```cmd
python -m wite2_tools.cli compact-weapons --ground-file "C:\My WiTE2 Mods\_ground.csv"
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
