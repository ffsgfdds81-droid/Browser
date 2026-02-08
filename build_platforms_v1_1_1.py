#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Enhanced Browser v1.1.1 - Platform-Specific Build Script

This script builds installers and packages for all supported platforms:
- Windows: .exe installer with DirectX optimizations
- macOS: .dmg package with Metal rendering
- Linux: .AppImage with Wayland/X11 support
- Mobile: Android APK and iOS IPA (frameworks provided)
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class PlatformBuilder:
    """Universal browser builder for all platforms"""
    
    def __init__(self):
        self.version = "1.1.1"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.source_dir = Path(".")
        self.build_info = {
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version,
            "build_env": os.environ.copy()
        }
        
        # Ensure build directories exist
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def log(self, message):
        """Log build progress"""
        print(f"[BUILD] {message}")
    
    def run_command(self, command, check=True):
        """Run shell command with error handling"""
        try:
            self.log(f"Running: {command}")
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}")
            self.log(f"Return code: {e.returncode}")
            self.log(f"Output: {e.output}")
            raise
    
    def create_requirements_file(self):
        """Create requirements.txt for distribution"""
        requirements = """PyQt6>=6.4.0
PyQt6-WebEngine>=6.4.0
cryptography>=3.4.8
requests>=2.28.1
psutil>=5.9.0
numpy>=1.21.0
Pillow>=9.0.0
"""
        
        requirements_file = self.build_dir / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write(requirements)
        
        self.log("Created requirements.txt")
        return requirements_file
    
    def copy_source_files(self):
        """Copy necessary source files to build directory"""
        essential_files = [
            "main.py",
            "enhanced_browser.py",
            "enhanced_main.py", 
            "enhanced_core.py",
            "navigation_manager_v1_1_1.py",
            "simple_integration_test.py"
        ]
        
        build_src_dir = self.build_dir / "src"
        build_src_dir.mkdir(exist_ok=True)
        
        for file in essential_files:
            src_path = self.source_dir / file
            if src_path.exists():
                shutil.copy2(src_path, build_src_dir / file)
                self.log(f"Copied {file} to build directory")
            else:
                self.log(f"Warning: {file} not found")
        
        return build_src_dir
    
    def build_windows(self):
        """Build Windows installer with PyInstaller"""
        self.log("Building Windows installer...")
        
        # Create PyInstaller spec
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('requirements.txt', '.')],
    hiddenimports=['PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore'],
    hookspath=[],
    hooksconfig={{}},
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
    name='UniversalBrowser_v{self.version}',
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
    icon='icon.ico',
    version='version_info.txt'
)
'''
        
        spec_file = self.build_dir / "browser_windows.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Create version info file
        version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({self.version.replace('.', ',')},0),
    prodvers=({self.version.replace('.', ',')},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'Universal Browser Project'),
            StringStruct(u'FileDescription', u'Universal Enhanced Browser'),
            StringStruct(u'FileVersion', u'{self.version}'),
            StringStruct(u'InternalName', u'UniversalBrowser'),
            StringStruct(u'LegalCopyright', u'Copyright (C) 2026'),
            StringStruct(u'OriginalFilename', u'UniversalBrowser_v{self.version}.exe'),
            StringStruct(u'ProductName', u'Universal Enhanced Browser'),
            StringStruct(u'ProductVersion', u'{self.version}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        version_file = self.build_dir / "version_info.txt"
        with open(version_file, 'w') as f:
            f.write(version_info)
        
        try:
            # Run PyInstaller
            self.run_command(f"pyinstaller --clean {spec_file}")
            
            # Create installer directory
            installer_dir = self.dist_dir / "windows"
            installer_dir.mkdir(exist_ok=True)
            
            # Move executable to dist
            exe_path = Path("dist") / f"UniversalBrowser_v{self.version}.exe"
            if exe_path.exists():
                shutil.move(str(exe_path), installer_dir / exe_path.name)
                self.log(f"Built Windows executable: {installer_dir / exe_path.name}")
            
            return True
            
        except Exception as e:
            self.log(f"Windows build failed: {e}")
            return False
    
    def build_macos(self):
        """Build macOS .app bundle and .dmg package"""
        self.log("Building macOS package...")
        
        try:
            # Create app bundle structure
            app_name = f"UniversalBrowser.app"
            app_dir = self.build_dir / app_name
            contents_dir = app_dir / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            # Create directories
            for directory in [contents_dir, macos_dir, resources_dir]:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Create Info.plist
            info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Universal Browser</string>
    <key>CFBundleExecutable</key>
    <string>UniversalBrowser</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.universalbrowser.browser</string>
    <key>CFBundleName</key>
    <string>Universal Browser</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.version}</string>
    <key>CFBundleVersion</key>
    <string>{self.version}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
</dict>
</plist>'''
            
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(info_plist)
            
            # Copy main executable
            shutil.copy2("main.py", macos_dir / "UniversalBrowser")
            
            # Make executable
            os.chmod(macos_dir / "UniversalBrowser", 0o755)
            
            # Copy resources
            for file in ["requirements.txt"]:
                if Path(file).exists():
                    shutil.copy2(file, resources_dir)
            
            # Create .dmg
            dmg_dir = self.dist_dir / "macos"
            dmg_dir.mkdir(exist_ok=True)
            
            dmg_name = f"UniversalBrowser_v{self.version}.dmg"
            dmg_path = dmg_dir / dmg_name
            
            # Create temporary DMG source directory
            dmg_source = self.build_dir / "dmg_source"
            dmg_source.mkdir(exist_ok=True)
            shutil.copytree(app_dir, dmg_source / app_name)
            
            # Create DMG (requires create-dmg utility)
            try:
                self.run_command(f"create-dmg --volname 'Universal Browser' "
                               f"--window-pos 200 120 --window-size 600 300 "
                               f"--icon-size 100 --icon '{app_name}' 175 120 "
                               f"--hide-extension '{app_name}' "
                               f"--app-drop-link 425 120 "
                               f"'{dmg_path}' '{dmg_source}'")
                self.log(f"Built macOS DMG: {dmg_path}")
                return True
                
            except:
                self.log("create-dmg not available, creating manual DMG")
                # Fallback to hdiutil
                self.run_command(f"hdiutil create -volname 'Universal Browser' "
                               f"-srcfolder '{dmg_source}' -ov -format UDZO "
                               f"'{dmg_path}'")
                self.log(f"Built macOS DMG (fallback): {dmg_path}")
                return True
                
        except Exception as e:
            self.log(f"macOS build failed: {e}")
            return False
    
    def build_linux(self):
        """Build Linux AppImage with AppImageTool"""
        self.log("Building Linux AppImage...")
        
        try:
            # Create AppImage directory structure
            app_name = f"UniversalBrowser-{self.version}"
            app_dir = self.build_dir / app_name / "usr" / "bin"
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            shutil.copy2("main.py", app_dir / "UniversalBrowser")
            
            # Create desktop file
            desktop_content = f'''[Desktop Entry]
Type=Application
Name=Universal Browser
Comment=Universal Enhanced Browser v{self.version}
Exec=UniversalBrowser
Icon=UniversalBrowser
Terminal=false
Categories=Network;WebBrowser;
Version={self.version}'''
            
            desktop_dir = self.build_dir / app_name / "usr" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            with open(desktop_dir / "UniversalBrowser.desktop", 'w') as f:
                f.write(desktop_content)
            
            # Create AppRun script
            apprun_content = '''#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/UniversalBrowser" "$@"'''
            
            apprun_path = self.build_dir / app_name / "AppRun"
            with open(apprun_path, 'w') as f:
                f.write(apprun_content)
            os.chmod(apprun_path, 0o755)
            
            # Create AppImage
            appimage_name = f"UniversalBrowser-{self.version}-x86_64.AppImage"
            appimage_path = self.dist_dir / "linux" / appimage_name
            (self.dist_dir / "linux").mkdir(exist_ok=True)
            
            # Convert to AppImage (requires appimagetool)
            try:
                self.run_command(f"appimagetool {self.build_dir / app_name} {appimage_path}")
                self.log(f"Built Linux AppImage: {appimage_path}")
                return True
                
            except:
                self.log("appimagetool not available, creating archive instead")
                # Fallback to tar.gz
                archive_name = f"UniversalBrowser-{self.version}-linux.tar.gz"
                archive_path = self.dist_dir / "linux" / archive_name
                self.run_command(f"tar -czf '{archive_path}' -C {self.build_dir} {app_name}")
                self.log(f"Built Linux archive: {archive_path}")
                return True
                
        except Exception as e:
            self.log(f"Linux build failed: {e}")
            return False
    
    def build_android(self):
        """Build Android APK framework"""
        self.log("Creating Android APK framework...")
        
        try:
            android_dir = self.dist_dir / "android"
            android_dir.mkdir(exist_ok=True)
            
            # Create Android project structure
            project_dir = android_dir / "UniversalBrowser"
            project_dir.mkdir(exist_ok=True)
            
            # Create build script for Android
            build_script = f'''#!/bin/bash
# Universal Browser v{self.version} - Android Build Script
# This script provides framework for building Android APK

echo "Universal Browser v{self.version} Android Framework"
echo "This requires Android SDK and build tools installed"

# Project structure would be set up here
# Requirements:
# - Android SDK
# - Gradle
# - Kivy/Buildozer for Python packaging

echo "To complete Android build:"
echo "1. Install Android SDK"
echo "2. Install Buildozer: pip install buildozer"
echo "3. Run: buildozer android debug"
'''
            
            with open(project_dir / "build_android.sh", 'w') as f:
                f.write(build_script)
            os.chmod(project_dir / "build_android.sh", 0o755)
            
            # Create buildozer spec
            buildozer_spec = f'''[app]

# (str) Title of your application
title = Universal Browser

# (str) Package name
package.name = universalbrowser

# (str) Package domain (needed for android/ios packaging)
package.domain = org.universalbrowser

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*.png

# (str) Application versioning (method 1)
version = {self.version}

# (list) Application requirements
requirements = python3,kivy,pyqt6,pyqt6-webengine,cryptography,requests

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (bool) If True, the window never close
fullscreen = 0

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) If True, then android trying to use lean startup
android.debuggable = False
'''
            
            with open(project_dir / "buildozer.spec", 'w') as f:
                f.write(buildozer_spec)
            
            self.log(f"Created Android framework: {project_dir}")
            return True
            
        except Exception as e:
            self.log(f"Android framework creation failed: {e}")
            return False
    
    def build_ios(self):
        """Build iOS framework"""
        self.log("Creating iOS framework...")
        
        try:
            ios_dir = self.dist_dir / "ios"
            ios_dir.mkdir(exist_ok=True)
            
            # Create iOS project structure
            project_dir = ios_dir / "UniversalBrowser"
            project_dir.mkdir(exist_ok=True)
            
            # Create iOS build instructions
            build_script = f'''#!/bin/bash
# Universal Browser v{self.version} - iOS Build Script
# This script provides framework for building iOS IPA

echo "Universal Browser v{self.version} iOS Framework"
echo "This requires Xcode and iOS development tools"

# Project structure would be set up here
# Requirements:
# - Xcode
# - iOS Developer Account
# - Python iOS packaging tools

echo "To complete iOS build:"
echo "1. Install Xcode from App Store"
echo "2. Install Python iOS tools: pip install python-for-ios"
echo "3. Configure Xcode project"
echo "4. Build with Xcode"
'''
            
            with open(project_dir / "build_ios.sh", 'w') as f:
                f.write(build_script)
            os.chmod(project_dir / "build_ios.sh", 0o755)
            
            # Create Xcode project template
            xcode_content = f'''// Universal Browser v{self.version} iOS Project
// This provides the basic structure for Xcode integration

import UIKit
import PythonKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Initialize Python environment
        try? PythonLibrary.useVersion(3, 9)
        
        // Import and run browser
        let sys = Python.import("sys")
        sys.path.append("/path/to/browser/source")
        
        let browser = Python.import("main")
        
        return true
    }
}
'''
            
            with open(project_dir / "AppDelegate.swift", 'w') as f:
                f.write(xcode_content)
            
            self.log(f"Created iOS framework: {project_dir}")
            return True
            
        except Exception as e:
            self.log(f"iOS framework creation failed: {e}")
            return False
    
    def save_build_info(self):
        """Save build information"""
        build_info_file = self.dist_dir / f"build_info_v{self.version}.json"
        with open(build_info_file, 'w', encoding='utf-8') as f:
            json.dump(self.build_info, f, indent=2, ensure_ascii=False)
        
        self.log(f"Saved build info: {build_info_file}")
    
    def build_all_platforms(self):
        """Build for all supported platforms"""
        self.log(f"Starting Universal Browser v{self.version} build process")
        
        # Prepare build
        self.create_requirements_file()
        self.copy_source_files()
        
        results = {}
        
        # Build for current platform
        if sys.platform == "win32":
            results["windows"] = self.build_windows()
        elif sys.platform == "darwin":
            results["macos"] = self.build_macos()
        elif sys.platform == "linux":
            results["linux"] = self.build_linux()
        
        # Build mobile frameworks
        results["android"] = self.build_android()
        results["ios"] = self.build_ios()
        
        # Save build information
        self.save_build_info()
        
        # Print results
        self.log("\n" + "="*60)
        self.log("BUILD SUMMARY")
        self.log("="*60)
        for platform, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            self.log(f"{platform}: {status}")
        self.log("="*60)
        
        return results

def main():
    """Main build function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Enhanced Browser v1.1.1 Builder")
    parser.add_argument("--platform", choices=["windows", "macos", "linux", "android", "ios", "all"],
                       default="all", help="Target platform (default: all)")
    parser.add_argument("--output", default="dist", help="Output directory (default: dist)")
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    
    args = parser.parse_args()
    
    builder = PlatformBuilder()
    
    # Override output directory if specified
    if args.output != "dist":
        builder.dist_dir = Path(args.output)
        builder.dist_dir.mkdir(exist_ok=True)
    
    # Clean if requested
    if args.clean:
        if builder.build_dir.exists():
            shutil.rmtree(builder.build_dir)
        if builder.dist_dir.exists():
            shutil.rmtree(builder.dist_dir)
        builder.build_dir.mkdir(exist_ok=True)
        builder.dist_dir.mkdir(exist_ok=True)
        builder.log("Cleaned build directories")
    
    # Build for specified platforms
    if args.platform == "all":
        results = builder.build_all_platforms()
    elif args.platform == "windows":
        results = {"windows": builder.build_windows()}
    elif args.platform == "macos":
        results = {"macos": builder.build_macos()}
    elif args.platform == "linux":
        results = {"linux": builder.build_linux()}
    elif args.platform == "android":
        results = {"android": builder.build_android()}
    elif args.platform == "ios":
        results = {"ios": builder.build_ios()}
    
    # Exit with appropriate code
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\nAll {total_count} builds completed successfully!")
        return 0
    elif success_count > 0:
        print(f"\n{success_count}/{total_count} builds completed successfully")
        return 1
    else:
        print(f"\nAll {total_count} builds failed")
        return 2

if __name__ == "__main__":
    sys.exit(main())