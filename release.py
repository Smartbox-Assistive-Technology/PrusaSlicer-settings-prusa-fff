#!/usr/bin/env python3
"""
Release script to create a PrusaSlicer offline configuration bundle.

This script creates a zip file that matches the structure of the official
prusa-fff-offline.zip file, containing:
- manifest.json
- vendor_indices.zip (containing PrusaResearch.idx)
- PrusaResearch/ directory with all .ini files and assets
"""

import os
import json
import zipfile
import logging
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_manifest():
    """Create the manifest.json file."""
    manifest = {
        "name": "Prusa FFF Smartbox",
        "description": "Smartbox custom Prusa FFF bundle",
        "visibility": "",
        "id": "prusa-fff",
        "url": "https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff",
        "index_url": "https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/releases/latest/download/vendor_indices.zip",
        "offline_archive_url": "https://github.com/Smartbox-Assistive-Technology/PrusaSlicer-settings-prusa-fff/releases/latest/download/prusa-fff-offline.zip"
    }
    
    with open('build/manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, separators=(',', ':'))
    
    logging.info('Created manifest.json')

def create_vendor_indices():
    """Create the vendor_indices.zip file containing PrusaResearch.idx."""
    # Copy the index file to build directory
    index_source = Path('PrusaResearch/index.idx')
    index_dest = Path('build/PrusaResearch.idx')
    
    if not index_source.exists():
        logging.error(f'Index file {index_source} does not exist')
        sys.exit(1)
    
    # Copy and rename to match expected name
    with open(index_source, 'r', encoding='utf-8') as src:
        content = src.read()
    
    with open(index_dest, 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    # Create the vendor_indices.zip for the offline bundle
    with zipfile.ZipFile('build/vendor_indices_internal.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(index_dest, 'PrusaResearch.idx')
    
    # Create the standalone vendor_indices.zip for direct download
    with zipfile.ZipFile('build/vendor_indices.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(index_dest, 'PrusaResearch.idx')
    
    # Clean up the temporary file
    index_dest.unlink()
    
    logging.info('Created vendor_indices.zip (standalone and internal versions)')

def copy_prusa_research_files():
    """Copy all files from PrusaResearch directory to build/PrusaResearch/, using modified .ini if available."""
    prusa_dir = Path('PrusaResearch')
    build_prusa_dir = Path('build/PrusaResearch')
    
    if not prusa_dir.exists():
        logging.error(f'PrusaResearch directory does not exist')
        sys.exit(1)
    
    # Create build PrusaResearch directory
    build_prusa_dir.mkdir(exist_ok=True)
    
    copied_files = 0
    
    # First, copy all files except .ini files and index.idx
    for file_path in prusa_dir.iterdir():
        if (file_path.is_file() and 
            file_path.name != 'index.idx' and 
            not file_path.name.endswith('.ini')):
            dest_path = build_prusa_dir / file_path.name
            dest_path.write_bytes(file_path.read_bytes())
            copied_files += 1
    
    # Then, copy the modified PrusaResearch.ini from build/ if it exists, 
    # otherwise copy original .ini files
    modified_ini = Path('build/PrusaResearch.ini')
    if modified_ini.exists():
        # Use the modified version and rename it to match the latest version
        import re
        ini_files = [f for f in prusa_dir.glob('*.ini') if re.match(r'\d+\.\d+\.\d+\.ini$', f.name)]
        if ini_files:
            def parse_version(filename):
                match = re.match(r'(\d+)\.(\d+)\.(\d+)', filename.name)
                if match:
                    return tuple(map(int, match.groups()))
                return (0, 0, 0)
            
            latest_ini = max(ini_files, key=lambda x: parse_version(x))
            dest_path = build_prusa_dir / latest_ini.name
            dest_path.write_bytes(modified_ini.read_bytes())
            copied_files += 1
            logging.info(f'Used modified {latest_ini.name} from build/PrusaResearch.ini')
    else:
        # Fallback: copy original .ini files
        for file_path in prusa_dir.glob('*.ini'):
            dest_path = build_prusa_dir / file_path.name
            dest_path.write_bytes(file_path.read_bytes())
            copied_files += 1
    
    logging.info(f'Copied {copied_files} files to build/PrusaResearch/')

def create_offline_archive():
    """Create the final prusa-fff-offline.zip file."""
    build_dir = Path('build')
    
    # Check that all required components exist
    required_files = [
        'build/manifest.json',
        'build/vendor_indices_internal.zip',
        'build/PrusaResearch'
    ]
    
    for required_file in required_files:
        if not Path(required_file).exists():
            logging.error(f'Required component {required_file} does not exist')
            sys.exit(1)
    
    # Create the zip file
    zip_path = 'build/prusa-fff-offline.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add manifest.json
        zf.write('build/manifest.json', 'manifest.json')
        
        # Add vendor_indices.zip (using internal version)
        zf.write('build/vendor_indices_internal.zip', 'vendor_indices.zip')
        
        # Add all PrusaResearch files
        prusa_build_dir = Path('build/PrusaResearch')
        for file_path in prusa_build_dir.iterdir():
            if file_path.is_file():
                arc_name = f'PrusaResearch/{file_path.name}'
                zf.write(file_path, arc_name)
    
    # Get file size for logging
    file_size = Path(zip_path).stat().st_size
    logging.info(f'Created {zip_path} ({file_size:,} bytes)')

def validate_archive():
    """Validate the created archive matches expected structure."""
    zip_path = 'build/prusa-fff-offline.zip'
    
    if not Path(zip_path).exists():
        logging.error(f'Archive {zip_path} does not exist')
        return False
    
    required_entries = {
        'manifest.json',
        'vendor_indices.zip'
    }
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        entries = set(zf.namelist())
        
        # Check required top-level files
        missing_entries = required_entries - entries
        if missing_entries:
            logging.error(f'Missing required entries: {missing_entries}')
            return False
        
        # Check PrusaResearch directory exists
        prusa_entries = [e for e in entries if e.startswith('PrusaResearch/')]
        if not prusa_entries:
            logging.error('No PrusaResearch/ entries found in archive')
            return False
        
        # Validate vendor_indices.zip contains PrusaResearch.idx
        try:
            vendor_zip_data = zf.read('vendor_indices.zip')
            with zipfile.ZipFile(os.path.join(os.path.dirname(__file__), 'temp_vendor.zip'), 'w') as temp_f:
                temp_f.writestr('vendor_indices.zip', vendor_zip_data)
            
            # This is a workaround - create temp file to check contents
            temp_path = Path('temp_vendor_indices.zip')
            temp_path.write_bytes(vendor_zip_data)
            
            with zipfile.ZipFile(temp_path, 'r') as vendor_zf:
                vendor_entries = vendor_zf.namelist()
                if 'PrusaResearch.idx' not in vendor_entries:
                    logging.error('PrusaResearch.idx not found in vendor_indices.zip')
                    temp_path.unlink()
                    return False
            
            temp_path.unlink()
            
        except Exception as e:
            logging.error(f'Error validating vendor_indices.zip: {e}')
            return False
        
        logging.info(f'Archive validation successful: {len(entries)} total entries, {len(prusa_entries)} PrusaResearch files')
        return True

def cleanup_build_artifacts():
    """Clean up intermediate build artifacts, keeping the final outputs."""
    build_dir = Path('build')
    
    # Keep the final outputs for CI
    keep_files = {'prusa-fff-offline.zip', 'vendor_indices.zip', 'PrusaResearch.ini'}
    
    for item in build_dir.iterdir():
        if item.name not in keep_files:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                # Remove directory and all contents
                import shutil
                shutil.rmtree(item)
    
    logging.info('Cleaned up build artifacts (kept ZIP, vendor indices, and INI files)')

def main():
    """Main release process."""
    logging.info('Starting release build process')
    
    # Create build directory
    Path('build').mkdir(exist_ok=True)
    
    try:
        # Create all components
        create_manifest()
        create_vendor_indices()
        copy_prusa_research_files()
        
        # Create final archive
        create_offline_archive()
        
        # Validate the result
        if not validate_archive():
            logging.error('Archive validation failed')
            sys.exit(1)
        
        # Clean up intermediate files
        cleanup_build_artifacts()
        
        logging.info('Release build completed successfully')
        logging.info('Output files:')
        logging.info('  - build/prusa-fff-offline.zip (offline bundle)')
        logging.info('  - build/vendor_indices.zip (vendor indices)')  
        logging.info('  - build/PrusaResearch.ini (standalone configuration)')
        
    except Exception as e:
        logging.error(f'Release build failed: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
