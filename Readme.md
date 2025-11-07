# Smartbox PrusaSlicer-settings-prusa-fff

This is a fork of the [Prusaslicer-settings-prusa-fff repo](https://github.com/prusa3d/PrusaSlicer-settings-prusa-fff), updated to include profiles for filaments used by Smartbox Assistive Technology.

[![Fetch Latest PrusaSlicer Config and Release](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml/badge.svg)](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml)


## How it works

The upstream Prusa configuration is included as a git submodule at `prusa-upstream/`. Three Python scripts work together to build custom configuration bundles:

### Build Scripts

**`version.py`**
- Generates semantic version numbers based on git tags and Prusa base version
- Scans `Smartbox/*.add.ini` and `*.rm.ini` files to detect filament changes
- Creates `index.idx` file with version changelog
- Generates markdown release notes with filament changes and recent commits

**`build.py`**
- Finds latest Prusa .ini file from submodule
- Removes filament profiles specified in `Smartbox/*.rm.ini` files
- Adds custom filament profiles from `Smartbox/*.add.ini` files
- Updates config_version to match generated version
- Copies all upstream .ini files to build directory

**`release.py`**
- Creates manifest.json with repository metadata
- Packages index.idx into vendor_indices.zip
- Copies all PrusaResearch assets (SVGs, STLs, thumbnails)
- Assembles final `prusa-fff-offline.zip` bundle matching prusa structure
- Validates the archive contains all required components

## Making a Release

### Automatic Release (Recommended)

Releases are created automatically by CI when changes are merged to `main`:

1. **Add/modify filament profiles** in the `Smartbox/` folder:
   - Create `filament-name.add.ini` to add a new filament
   - Create `filament-name.rm.ini` to remove an existing filament
2. **Create a PR** with your changes (triggers build workflow for validation)
3. **Merge to main** - this triggers the release workflow which:
   - Builds the configuration bundle
   - Auto-increments version (patch bump from latest tag)
   - Generates release notes with detected filament changes
   - Creates a GitHub release with all bundle files

The version is automatically calculated as `2.X.Y` where X and Y are incremented based on existing tags.

### Manual Build (Testing)

To test locally before creating a PR:

```bash
python version.py   # Generate version and release notes
python build.py     # Build configuration files
python release.py   # Package the release bundle
# Check build/ directory for outputs
```

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

