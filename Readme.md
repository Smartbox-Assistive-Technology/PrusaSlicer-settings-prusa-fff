# Smartbox PrusaSlicer-settings-prusa-fff

This is a fork of the [Prusaslicer-settings-prusa-fff repo](https://github.com/prusa3d/PrusaSlicer-settings-prusa-fff), updated to include profiles for filaments used by Smartbox Assistive Technology.

[![Fetch Latest PrusaSlicer Config and Release](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml/badge.svg)](https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/actions/workflows/release.yml)


## How it works

The script adds all the `*.add.ini` and `*.rm.ini` files in the [Smartbox](Smartbox) folder to the latest version of the prusa3d/PrusaSlicer-settings-prusa-fff repo, and then creates a new release with the updated files.

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

