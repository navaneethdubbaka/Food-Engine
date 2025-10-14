#!/usr/bin/env python3
"""
Build script for creating executable from Sri Vengamamba Food Court
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('database', 'database'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.windows.edge',
        'webview.platforms.winforms',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SriVengamambaFoodCourt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('restaurant_billing.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created")

def main():
    """Main build process"""
    print("🏗️  Building Sri Vengamamba Food Court Executable")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Create spec file
    create_spec_file()
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Kill any running processes that might be using files
    print("🔄 Checking for running processes...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'SriVengamambaFoodCourt.exe'], 
                      capture_output=True, shell=True)
        print("✅ Killed any running SriVengamambaFoodCourt processes")
    except:
        pass
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build directory")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned dist directory")
    
    # Build executable
    if not run_command("pyinstaller restaurant_billing.spec", "Building executable"):
        print("❌ Failed to build executable")
        sys.exit(1)
    
    # Create final distribution folder
    dist_folder = Path("SriVengamambaFoodCourt_Distribution")
    if dist_folder.exists():
        try:
            shutil.rmtree(dist_folder)
        except PermissionError:
            print("⚠️  Warning: Cannot delete existing distribution folder (file may be in use)")
            print("🔄 Renaming existing folder and creating new one...")
            backup_folder = Path("SriVengamambaFoodCourt_Distribution_backup")
            if backup_folder.exists():
                shutil.rmtree(backup_folder)
            dist_folder.rename(backup_folder)
            print(f"✅ Existing folder renamed to: {backup_folder}")
    
    dist_folder.mkdir()
    
    # Copy executable
    exe_path = Path("dist/SriVengamambaFoodCourt.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_folder / "SriVengamambaFoodCourt.exe")
        print("✅ Executable copied to distribution folder")
    else:
        print("❌ Executable not found in dist folder")
        sys.exit(1)
    
    # Copy launcher files
    if os.path.exists('start_app.vbs'):
        shutil.copy2('start_app.vbs', dist_folder / 'start_app.vbs')
        print("✅ VBS launcher copied")
    
    if os.path.exists('start_app.bat'):
        shutil.copy2('start_app.bat', dist_folder / 'start_app.bat')
        print("✅ Batch launcher copied")
    
    # Copy database folder
    if os.path.exists('database'):
        shutil.copytree('database', dist_folder / 'database')
        print("✅ Database folder copied")
    
    # Copy static folder
    if os.path.exists('static'):
        shutil.copytree('static', dist_folder / 'static')
        print("✅ Static folder copied")
    
    # Copy templates folder
    if os.path.exists('templates'):
        shutil.copytree('templates', dist_folder / 'templates')
        print("✅ Templates folder copied")
    
    # Create README for distribution
    readme_content = """# Sri Vengamamba Food Court

## Quick Start

### Option 1: Desktop Application (Recommended)
1. Double-click `SriVengamambaFoodCourt.exe` to start the desktop application
2. The system will open as a standalone desktop window
3. No web browser required - everything runs in the desktop app

### Option 2: Silent Launch
1. Double-click `start_app.vbs` to start the application silently
2. The system will automatically open in your web browser
3. No console window will be shown

### Option 3: Batch Launch
1. Double-click `start_app.bat` to start the application
2. The system will automatically open in your web browser

## Features

- 🧾 Create and print customer bills
- 🍴 Manage menu items with categories
- ⚙️ Configure tax rates and restaurant settings
- 📊 View sales reports and bill history
- 💾 All data stored locally in SQLite database
- 🌐 Bilingual support (English/Telugu)
- 💰 Rupee currency support
- 🖥️ Standalone desktop application (no browser needed)

## First Time Setup

1. Go to Settings to configure your restaurant information
2. Add menu items in the Menu section
3. Start creating bills in the Billing section

## File Structure

- `SriVengamambaFoodCourt.exe` - Main desktop application (recommended)
- `start_app.vbs` - Silent launcher
- `start_app.bat` - Batch launcher
- `database/` - Contains your data (SQLite database)
- `static/` - Images and assets
- `templates/` - Application templates

## Desktop Application Features

- **Standalone Window**: Runs as a native desktop application
- **No Browser Required**: Everything embedded in the desktop window
- **Native Look**: Feels like a regular Windows application
- **Resizable Window**: Adjust the window size as needed
- **Full Functionality**: All features work exactly the same

## Language Support

- Switch between English and Telugu in Settings
- All interface elements support both languages
- Food items remain in English as requested

## Support

This is a standalone application that runs completely offline.
All your data is stored locally and never leaves your computer.

## System Requirements

- Windows 10 or later
- No internet connection required
- No additional software installation needed
- No web browser required for desktop version
"""
    
    with open(dist_folder / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.txt created")
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Distribution folder: {dist_folder.absolute()}")
    print(f"🚀 Executable: {dist_folder / 'SriVengamambaFoodCourt.exe'}")
    print("\nTo distribute:")
    print(f"1. Zip the '{dist_folder}' folder")
    print("2. Share the zip file with users")
    print("3. Users can extract and run SriVengamambaFoodCourt.exe")

if __name__ == "__main__":
    main()
