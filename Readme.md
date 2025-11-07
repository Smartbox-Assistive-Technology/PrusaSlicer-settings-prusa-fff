# Smartbox PrusaSlicer-settings-prusa-fff

This is a fork of the [Prusaslicer-settings-prusa-fff repo](https://github.com/prusa3d/PrusaSlicer-settings-prusa-fff), updated to include profiles for filaments used by Smartbox Assistive Technology.

[![Fetch Latest PrusaSlicer Config and Release](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml/badge.svg)](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml)


## How it works

The release process uses 3 Python scripts:

### 1. `version.py` - Version & Release Notes Generation
- Generates semantic versions in format `2.x.x` (incrementing from existing tags)
- Creates `build/index.idx` with version history
- Generates release notes with added/updated/removed filaments and recent commits
- Outputs: `build/version.txt`, `build/release_notes.md`, `build/version_info.json`, `build/index.idx`

### 2. `build.py` - Configuration File Builder
- Finds latest Prusa `.ini` file (e.g., `2.4.1.ini`)
- Strips comments from all content
- **Removes** sections specified in `Smartbox/*.rm.ini` files
- **Adds** custom filaments from `Smartbox/*.add.ini` files (inserted before `[printer:*common*]` section)
- Updates `config_version` to match the new version
- Outputs: `build/PrusaResearch.ini` (modified config) and copies all original Prusa `.ini` files

### 3. `release.py` - Bundle Creation
- Creates `manifest.json` with URLs pointing to Smartbox-Assistive-Technology GitHub
- Creates `vendor_indices.zip` containing `PrusaResearch.idx`
- Copies all files from `build/PrusaResearch/` including the modified `.ini`
- Creates final `prusa-fff-offline.zip` bundle with proper structure
- Validates the bundle structure

### Workflow
1. Run `version.py` → generates version, index, release notes
2. Run `build.py` → builds modified configuration files
3. Run `release.py` → packages everything into distributable bundles

The process customizes Prusa's official configs by removing unwanted filaments and adding Smartbox-specific ones, while maintaining compatibility with PrusaSlicer's configuration system.

## Filament Types

Current filaments:

- **Eono PVB** - Support material for water-soluble supports
- **Eryone PP-CF** - Polypropylene with carbon fiber reinforcement
- **eSUN ePLA-CF** - Enhanced PLA with carbon fiber
- **Overture TPU High-Speed** - Flexible thermoplastic polyurethane optimized for high-speed printing
- **Polymaker PolyDissolve S1** - Water-soluble support material

Past filaments (removed because they're now included in official PrusaSlicer):

- **Elegoo Rapid PLA+**
- **Overture PETG**
- **Overture PLA** - Now included in official PrusaSlicer profiles
- **Sunlu PLA+ 2.0** - Now included in official PrusaSlicer profiles


## Installing profiles

To install these custom profiles in PrusaSlicer:

1. Download the latest `prusa-fff-offline.zip` file from the [releases page](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/releases/latest)
2. Open PrusaSlicer
3. Click on **"Configuration"** → **"Configuration Assistant"**
4. Click **"Next"** until you reach the **"Configuration sources"** tab
5. **Untick** the "Prusa FFF online source" checkbox
6. Click the **"Load"** button and select the downloaded `prusa-fff-offline.zip` file
7. Continue through the Configuration Assistant to complete the setup

The custom Smartbox filament profiles will now be available in your filament selection.

