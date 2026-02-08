# -*- mode: python ; coding: utf-8 -*-

"""
Develer Browser - Advanced Build Script
Creates executable with all optimizations
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    print("Checking requirements...")
    
    required = [
        'PyInstaller',
        'PyQt5',
        'PyQtWebEngine', 
        'psutil',
        'numpy'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.lower())
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Packages installed successfully!")
    else:
        print("All requirements satisfied!")

def create_spec_file():
    """Create PyInstaller spec file with all optimizations"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_clean.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('*.html', '.'),
        ('*.css', '.'),
        ('*.js', '.'),
        ('*.png', '.'),
        ('*.ico', '.'),
        ('*.jpg', '.'),
        ('*.gif', '.'),
        ('devtools.html', '.'),
        ('settings.html', '.'),
        ('newtab.html', '.'),
        ('history.html', '.'),
        ('error_pages', 'error_pages'),
        ('data', 'data'),
        ('downloads', 'downloads'),
    ],
    hiddenimports=[
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtCore', 
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebChannel',
        'PyQt5.QtNetwork',
        'PyQt5.QtPrintSupport',
        'PyQt5.QtSvg',
        'memory_manager',
        'webgpu_support',
        'optimized_renderer',
        'browser_memory_pool', 
        'performance_monitor',
        'shader_effect_system',
        'devtools',
        'error_page_handler',
        'local_server',
        'browser',
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
    [],
    exclude_binaries=True,
    name='DevelerBrowser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='develer_icon.ico' if os.path.exists('develer_icon.ico') else None,
    version='1.1.1',
    description='Develer Browser - Advanced Optimized Version',
    company='Develer Software',
    product='Develer Browser',
    copyright='Copyright (C) 2024 Develer Software',
    trademarks='Develer Browser is a trademark of Develer Software'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DevelerBrowser',
    debug=False,
    bootloader_ignore_signals=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('DevelerBrowser_advanced.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file: DevelerBrowser_advanced.spec")

def create_icon():
    """Create default icon if not exists"""
    if not os.path.exists('develer_icon.ico'):
        print("Creating default icon...")
        # Create a simple icon using PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Create 256x256 image
            img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw browser-like icon
            draw.rectangle([20, 20, 236, 236], fill=(52, 152, 219), outline=(255, 255, 255, 255), width=4)
            draw.rectangle([40, 40, 216, 216], fill=(255, 255, 255), outline=(0, 100, 200), width=2)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 80)
                text_width = font.getlength("DB")
                text_x = (256 - text_width) // 2
                draw.text((text_x, 90), "DB", fill=(52, 152, 219), font=font)
            except:
                draw.text((80, 90), "DB", fill=(52, 152, 219))
            
            # Save as ICO
            img.save('develer_icon.ico', format='ICO', sizes=[(256, 256)])
            print("Icon created successfully!")
            
        except ImportError:
            print("PIL not available, skipping icon creation...")
        except Exception as e:
            print(f"Icon creation failed: {e}")

def build_executable():
    """Build the executable"""
    print("\nBuilding executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Run PyInstaller
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        '--log-level=INFO',
        'DevelerBrowser_advanced.spec'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("Build completed!")

def create_installer():
    """Create simple installer"""
    dist_dir = Path('dist/DevelerBrowser')
    if not dist_dir.exists():
        print("No build directory found!")
        return
    
    print("\nCreating installer package...")
    
    # Create installer directory
    installer_dir = Path('DevelerBrowser_Installer')
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    installer_dir.mkdir()
    
    # Copy executable and files
    shutil.copytree(dist_dir, installer_dir / 'DevelerBrowser')
    
    # Create installer script
    install_script = '''
@echo off
echo ====================================
echo Develer Browser Installer
echo ====================================
echo.
echo Installing Develer Browser Advanced...
echo.

REM Create program files directory
if not exist "%PROGRAMFILES%\\DevelerBrowser" mkdir "%PROGRAMFILES%\\DevelerBrowser"

REM Copy files
xcopy "DevelerBrowser\\*" "%PROGRAMFILES%\\DevelerBrowser\\" /E /I /Y

REM Create desktop shortcut
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\DevelerBrowser.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\DevelerBrowser\\DevelerBrowser.exe'; $Shortcut.Save()"

REM Create start menu shortcut
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DevelerBrowser" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DevelerBrowser"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\DevelerBrowser\\DevelerBrowser.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\DevelerBrowser\\DevelerBrowser.exe'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo Develer Browser has been installed to:
echo %PROGRAMFILES%\\DevelerBrowser
echo.
echo Shortcuts created on Desktop and Start Menu.
echo.
echo Press any key to exit...
pause >nul
'''
    
    with open(installer_dir / 'install.bat', 'w') as f:
        f.write(install_script)
    
    # Create README
    readme = '''# Develer Browser - Advanced Optimized Version

## Installation:
1. Run install.bat as administrator
2. Follow the installation prompts

## Features:
- Advanced Memory Management
- WebGPU Hardware Acceleration  
- Optimized Rendering Engine
- Browser Component Pooling
- Performance Monitoring
- Advanced Shader Effects

## Requirements:
- Windows 7 or later
- Graphics card with OpenGL/WebGL support
- 4GB RAM (8GB+ recommended)

## Launch:
- Desktop shortcut: "DevelerBrowser"
- Start Menu: Programs → DevelerBrowser
- Direct: C:\\Program Files\\DevelerBrowser\\DevelerBrowser.exe

## Controls:
- F12: DevTools
- Ctrl+T: New Tab
- Ctrl+Shift+C: Element Inspector
- DevTools Menu: Performance Stats, Memory Stats, GPU Stats, Shader Effects
'''
    
    with open(installer_dir / 'README.txt', 'w') as f:
        f.write(readme)
    
    # Create ZIP archive
    import zipfile
    zip_path = Path('DevelerBrowser_Advanced_v1.1.1.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in installer_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(installer_dir)
                zipf.write(file_path, arcname)
    
    print(f"Installer package created: {zip_path}")
    print(f"Package size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

def main():
    """Main build function"""
    print("=" * 60)
    print("Develer Browser - Advanced Build Script")
    print("=" * 60)
    print()
    
    # Check requirements
    check_requirements()
    
    # Create icon
    create_icon()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    build_executable()
    
    # Create installer
    create_installer()
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print("Files created:")
    print("  • dist/DevelerBrowser/ - Executable and dependencies")
    print("  • DevelerBrowser_Advanced_v1.1.1.zip - Installer package")
    print()
    print("To install: Extract ZIP and run install.bat as administrator")
    print("=" * 60)

if __name__ == '__main__':
    main()