# Changelog

## v1.1.0 - 2026-05-23

**Features**:

- Added `status` command
- Added drift detection support
- Added `diff` command
- Added side-by-side diff rendering
- Added colored diff output
- Added short status rendering
- Added structured status report model

**Fixes**:

- Fixed incorrect file existence detection for permission-restricted files (`Path.exists()` was not sufficient)
- Improved file stat handling using `os.stat()` / permission-aware checks in status and diff operations

**UX Improvements**:

- Improved CLI icons and symbols
- Improved human-readable status output
- Added cleaner sync/drift reporting

**Known Limitations**:

- `sudo` handling currently only applies to the `save` command
- Some commands may still show limited metadata for restricted files depending on system permissions

## v1.0.9 - 2025-06-25

**Features**:

- Added `--prune` flag to clean stale tracked files
- Added automatic config cleanup support
- Added entry cleanup support

**Fixes**:

- Fixed dependency-related issues
- Fixed path existence handling in data handler

**Improvements**:

- Improved README documentation
- General code cleanup and refactoring

---

## v1.0.8 - 2025-04-22

**Features**:

- Added improved CLI symbols and status messages
- Added automatic pull support during save/apply operations

**Fixes**:

- Fixed pull operation for local-only branches
- Prevented overwriting existing hooks/config during initialization

---

## v1.0.7 - 2025-04-10

**Features**:

- Added interactive hooks support
- Added `--hooks-timeout` flag for hook execution control

**Fixes**:

- Improved hook error handling
- Improved shell script execution handling

**Documentation**:

- Added profile workflow diagram
- Updated README examples and usage docs

---

## v1.0.6 - 2025-04-06

**Features**:

- Added support for creating empty profiles
- Added profile initialization checkpoints
- Added hook system:
  - pre-apply hooks
  - post-apply hooks
  - hook failure control flags

**Improvements**:

- Added dynamic props support
- Improved importer/exporter cleanup
- Added profile wipe command

**Fixes**:

- Fixed missing templates/packages
- Fixed missing binary handler

---

## v1.0.5 - 2025-04-03

**Features**:

- Added profile import support
- Added profile export support
- Added push support
- Added apply profile functionality

**Improvements**:

- Refactored git handlers and saver logic
- Improved initialization workflow
- Added fetch support for cloud metadata sync

---

## v1.0.4 - 2025-03-26

**Features**:

- Added profile listing
- Added profile switching
- Added profile creation
- Added profile removal

**Improvements**:

- Added handler-based architecture
- Added detailed profile metadata

**Fixes**:

- Fixed local vs archived profile handling
- Fixed repository metadata issues

---

## v1.0.3 - 2025-03-12

**Features**:

- Added initialization workflow
- Added configuration validation
- Added environment-specific templates

**Fixes**:

- Fixed permission handling issues
- Fixed workflow and packaging bugs

**Improvements**:

- Refactored configuration initialization
- Improved logging and typing

---

## v1.0.2 - 2023-01-19

**Initial Public Release**:

- Added first stable `dotctl` implementation
- Added project structure and packaging
- Added initial CLI functionality
