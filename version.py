#!/usr/bin/env python3
"""
Version generation for Smartbox PrusaSlicer configurations.
Generates semantic versions and release notes based on git history and Smartbox filaments.
"""

import subprocess
import sys
import json
import re
from datetime import datetime
from pathlib import Path

def get_git_info():
    """Get git information for versioning."""
    try:
        # Get current commit hash
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                             text=True).strip()
        
        # Get commit count
        commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], 
                                              text=True).strip()
        
        # Check if we're on a tag
        try:
            current_tag = subprocess.check_output(['git', 'describe', '--exact-match', '--tags'], 
                                                 text=True, stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            current_tag = None
        
        # Get latest tag for version bumping
        try:
            latest_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], 
                                                text=True, stderr=subprocess.DEVNULL).strip()
        except subprocess.CalledProcessError:
            latest_tag = "v9.2.0"  # Default starting version
        
        return {
            'commit_hash': commit_hash,
            'commit_count': commit_count,
            'current_tag': current_tag,
            'latest_tag': latest_tag
        }
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return None

def parse_version(version_str):
    """Parse a version string like 'v9.3.0' into (9, 3, 0)."""
    # Remove 'v' prefix if present
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    try:
        parts = version_str.split('.')
        return tuple(int(p) for p in parts[:3])
    except (ValueError, IndexError):
        return (9, 2, 0)  # Default fallback

def generate_version(git_info=None, prusa_base_version=None):
    """Generate the next version number based on existing tags and Prusa version."""
    if not git_info:
        git_info = get_git_info()
    
    # If we're on a tag, check if it follows our 2.x.x pattern
    if git_info and git_info['current_tag']:
        tag_version = git_info['current_tag'].lstrip('v')
        if tag_version.startswith('2.') and len(tag_version.split('.')) == 3:
            return tag_version
    
    # Get all existing 2.x.x tags to find the highest version
    try:
        all_tags = subprocess.check_output(['git', 'tag', '-l'], text=True).strip().split('\n')
        smartbox_tags = []
        
        for tag in all_tags:
            clean_tag = tag.lstrip('v')
            if re.match(r'^2\.\d+\.\d+$', clean_tag):
                try:
                    parts = clean_tag.split('.')
                    version_tuple = (int(parts[0]), int(parts[1]), int(parts[2]))
                    smartbox_tags.append(version_tuple)
                except (ValueError, IndexError):
                    continue
        
        if smartbox_tags:
            # Get the highest existing version and increment patch
            latest_version = max(smartbox_tags)
            major, minor, patch = latest_version
            return f"{major}.{minor}.{patch + 1}"
    
    except subprocess.CalledProcessError:
        pass
    
    # Fallback: base on Prusa version if no existing tags found
    if not prusa_base_version:
        prusa_base_version = get_prusa_base_version()
    
    prusa_parts = prusa_base_version.split('.')
    if len(prusa_parts) >= 3:
        # Simple version: major=2, minor=prusa_minor+1, patch=0
        major = "2"
        minor = str(int(prusa_parts[1]) + 1)
        return f"{major}.{minor}.0"
    else:
        return "2.4.0"

def get_smartbox_filaments():
    """Get list of current Smartbox filaments from add/rm files."""
    smartbox_dir = Path('Smartbox')
    added_filaments = set()
    removed_filaments = set()
    replaced_filaments = set()
    
    # Process .add.ini files
    for add_file in smartbox_dir.glob('*.add.ini'):
        with open(add_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract primary filament names (not variants with @)
        filament_matches = re.findall(r'^\[filament:([^\]@]+)\]', content, re.MULTILINE)
        for match in filament_matches:
            filament_name = match.strip()
            if filament_name:  # Only add non-empty names
                added_filaments.add(filament_name)
    
    # Process .rm.ini files  
    for rm_file in smartbox_dir.glob('*.rm.ini'):
        with open(rm_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract filament names that are being removed/replaced
        filament_matches = re.findall(r'^\[filament:([^\]@]+)\]', content, re.MULTILINE)
        for match in filament_matches:
            filament_name = match.strip()
            if filament_name:
                removed_filaments.add(filament_name)
                
                # If we're removing something that we're also adding, it's a replacement
                if filament_name in added_filaments:
                    replaced_filaments.add(filament_name)
                    added_filaments.remove(filament_name)
                    removed_filaments.remove(filament_name)
    
    return {
        'added': sorted(list(added_filaments)),
        'removed': sorted(list(removed_filaments)),
        'replaced': sorted(list(replaced_filaments))
    }

def get_prusa_base_version():
    """Get the base Prusa configuration version we're extending."""
    # Find the highest numbered .ini file
    prusa_dir = Path('PrusaResearch')
    ini_files = list(prusa_dir.glob('*.ini'))
    
    # Parse version numbers and find the latest
    versions = []
    for ini_file in ini_files:
        try:
            # Extract version from filename like "2.3.0.ini"
            version_str = ini_file.stem
            # Only include stable versions (no alpha/beta)
            if re.match(r'^\d+\.\d+\.\d+$', version_str):
                versions.append(version_str)
        except:
            continue
    
    if versions:
        # Sort versions properly (not just alphabetically)
        def version_key(v):
            return tuple(int(x) for x in v.split('.'))
        
        return sorted(versions, key=version_key)[-1]
    
    return "2.3.0"  # Fallback

def generate_index_idx(version, filaments, prusa_base_version):
    """Generate the index.idx file content."""
    lines = []
    
    # Add minimum slicer version
    lines.append("min_slic3r_version = 2.8.1")
    
    # Generate filament summary for the version entry
    filament_parts = []
    if filaments['added']:
        filament_parts.append(f"Added: {', '.join(filaments['added'])}")
    if filaments['replaced']:
        filament_parts.append(f"Updated: {', '.join(filaments['replaced'])}")
    if filaments['removed']:
        filament_parts.append(f"Removed: {', '.join(filaments['removed'])}")
    
    filament_summary = ". ".join(filament_parts) if filament_parts else "No filament changes"
    
    # Add our custom version entry
    lines.append(f"{version} Smartbox custom configuration bundle based on Prusa {prusa_base_version}. {filament_summary}.")
    
    # Read existing index.idx and add all other entries (except our custom ones)
    index_file = Path('PrusaResearch/index.idx')
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
        
        # Skip lines that start with our version pattern (9.x.x)
        for line in existing_lines:
            line = line.strip()
            if line and not line.startswith('min_slic3r_version') and not re.match(r'^9\.\d+\.\d+', line):
                lines.append(line)
    
    return '\n'.join(lines) + '\n'

def get_last_commits(count=5):
    """Get recent commit messages for release notes."""
    try:
        # Get last few commits with format: hash|date|message
        cmd = ['git', 'log', f'-{count}', '--pretty=format:%h|%ci|%s']
        output = subprocess.check_output(cmd, text=True).strip()
        
        commits = []
        for line in output.split('\n'):
            if '|' in line:
                hash_part, date_part, message = line.split('|', 2)
                commits.append({
                    'hash': hash_part,
                    'date': date_part.split()[0],  # Just the date part
                    'message': message
                })
        
        return commits
    except subprocess.CalledProcessError:
        return []

def generate_release_notes(version, filaments, prusa_base_version, recent_commits):
    """Generate release notes based on current state."""
    notes = []
    notes.append(f"# Smartbox PrusaSlicer Configuration Bundle v{version}")
    notes.append("")
    notes.append("This release contains custom filament profiles for Smartbox Assistive Technology,")
    notes.append(f"based on Prusa Research configuration bundle v{prusa_base_version}.")
    notes.append("")
    
    # Filaments section with categorization
    has_filaments = any(filaments.values())
    if has_filaments:
        notes.append("## 🧵 Filament Changes")
        notes.append("")
        
        if filaments['added']:
            notes.append("### ✅ Added Filaments")
            for filament in filaments['added']:
                notes.append(f"- **{filament}**")
            notes.append("")
            
        if filaments['replaced']:
            notes.append("### 🔄 Updated Filaments")
            for filament in filaments['replaced']:
                notes.append(f"- **{filament}** (improved profile)")
            notes.append("")
            
        if filaments['removed']:
            notes.append("### ❌ Removed Filaments")
            for filament in filaments['removed']:
                notes.append(f"- **{filament}**")
            notes.append("")
    
    # All current filaments for quick reference
    all_filaments = filaments['added'] + filaments['replaced']
    if all_filaments:
        notes.append("### 📋 All Smartbox Filaments")
        for filament in sorted(all_filaments):
            notes.append(f"- **{filament}**")
        notes.append("")
    
    # Recent changes section
    if recent_commits:
        notes.append("## 📝 Recent Changes")
        notes.append("")
        for commit in recent_commits[:3]:  # Show last 3 commits
            notes.append(f"- {commit['message']} ({commit['hash']})")
        notes.append("")
    
    # Installation section
    notes.append("## 📦 Installation")
    notes.append("")
    notes.append("### Using Configuration Assistant (Recommended)")
    notes.append("1. Download `prusa-fff-offline.zip` from this release")
    notes.append("2. Open PrusaSlicer")
    notes.append("3. Go to **Configuration** → **Configuration Assistant**")
    notes.append("4. Click **Next** until you reach **Configuration sources**")
    notes.append("5. **Untick** the Prusa FFF online source")
    notes.append("6. Click **Load** and select the downloaded zip file")
    notes.append("7. Complete the setup")
    notes.append("")
    
    notes.append("### Manual Installation")
    notes.append("- Download `PrusaResearch.ini` and replace the file in your PrusaSlicer vendor folder")
    notes.append("")
    
    notes.append("## 🔧 Technical Details")
    notes.append("")
    notes.append(f"- **Base Version**: Prusa {prusa_base_version}")
    notes.append(f"- **Minimum PrusaSlicer**: 2.8.1")
    notes.append(f"- **Bundle Version**: {version}")
    notes.append("")
    notes.append("---")
    notes.append("*Generated automatically by Smartbox CI*")
    
    return '\n'.join(notes)

def main():
    """Main function to generate version and release notes."""
    git_info = get_git_info()
    prusa_base_version = get_prusa_base_version()
    version = generate_version(git_info, prusa_base_version)
    filaments = get_smartbox_filaments()
    recent_commits = get_last_commits()
    
    # Generate index.idx content
    index_content = generate_index_idx(version, filaments, prusa_base_version)
    
    # Generate release notes
    release_notes = generate_release_notes(version, filaments, prusa_base_version, recent_commits)
    
    # Output results
    result = {
        'version': version,
        'release_notes': release_notes,
        'filaments': filaments,
        'prusa_base_version': prusa_base_version,
        'git_info': git_info
    }
    
    # Save to files for CI to use
    Path('build').mkdir(exist_ok=True)
    
    with open('build/version.txt', 'w') as f:
        f.write(version)
    
    with open('build/release_notes.md', 'w') as f:
        f.write(release_notes)
    
    with open('build/version_info.json', 'w') as f:
        json.dump(result, f, indent=2)
        
    # Save the generated index.idx
    with open('build/index.idx', 'w') as f:
        f.write(index_content)
    
    # Summary for display
    all_filaments = filaments['added'] + filaments['replaced']
    
    print(f"Generated version: {version}")
    print(f"Based on Prusa: {prusa_base_version}")
    print()
    
    # Display filament changes in requested format
    print("Filaments added:")
    if filaments['added']:
        for filament in filaments['added']:
            print(f"  - {filament}")
    else:
        print("  none")
    
    print("Filaments replaced:")
    if filaments['replaced']:
        for filament in filaments['replaced']:
            print(f"  - {filament}")
    else:
        print("  none")
    
    print("Filaments removed:")
    if filaments['removed']:
        for filament in filaments['removed']:
            print(f"  - {filament}")
    else:
        print("  none")
    
    return result

if __name__ == '__main__':
    main()
