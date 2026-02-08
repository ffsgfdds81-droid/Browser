#!/usr/bin/env python3
"""
Develer Browser AppImage Builder
Creates AppImage with all required libraries and dependencies
"""

import os
import sys
import subprocess
import shutil
import glob
from pathlib import Path

class AppImageBuilder:
    def __init__(self):
        self.app_name = "DevelerBrowser"
        self.version = "1.0.0"
        self.app_dir = Path("DevelerBrowser.AppDir")
        self.appimage_name = f"{self.app_name}-{self.version}-x86_64.AppImage"
        
    def run_command(self, cmd, cwd=None):
        """Run command and handle errors"""
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            print(f"Output: {e.output}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("Checking dependencies...")
        
        # Check Python
        try:
            import PyQt5
            import PyQtWebEngine
            print("✓ PyQt5 found")
        except ImportError as e:
            print(f"✗ PyQt5 not found: {e}")
            return False
            
        # Check appimagetool
        try:
            import appimage_builder
            print("✓ appimage-builder found")
        except ImportError as e:
            print("✗ appimage-builder not found")
            print("Installing appimage-builder...")
            return self.install_appimagetool()
    
    def install_appimagetool(self):
        """Install appimage-builder package"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "appimage-builder"], check=True)
            print("✓ appimage-builder installed")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install appimage-builder")
            return False
    
    def create_appimage_structure(self):
        """Create AppImage directory structure"""
        print("Creating AppImage structure...")
        
        # Clean previous builds
        if self.app_dir.exists():
            shutil.rmtree(self.app_dir)
        
        self.app_dir.mkdir(exist_ok=True)
        
        # Create required directories
        dirs = [
            self.app_dir / "usr" / "bin",
            self.app_dir / "usr" / "lib",
            self.app_dir / "usr" / "share" / "applications",
            self.app_dir / "usr" / "share" / "icons",
            self.app_dir / "usr" / "share" / "metainfo"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✓ AppImage structure created")
        
    def create_desktop_file(self):
        """Create desktop file for AppImage"""
        desktop_content = f"""[Desktop Entry]
Version={self.version}
Type=Application
Name={self.app_name}
Comment=Modern web browser with advanced features
Exec={self.app_name}
Icon={self.app_name.lower()}
Terminal=false
Categories=Network;WebBrowser;
Keywords=web;browser;internet;
StartupWMClass={self.app_name}
"""
        
        desktop_file = self.app_dir / "usr" / "share" / "applications" / f"{self.app_name.lower()}.desktop"
        desktop_file.write_text(desktop_content)
        
        # Copy icon if exists
        icon_sources = ["browser-icon.png", "browser-icon.ico", "browser-icon.svg"]
        for icon_file in icon_sources:
            if Path(icon_file).exists():
                shutil.copy2(icon_file, self.app_dir / "usr" / "share" / "icons" / f"{self.app_name.lower()}.png")
                break
        
        print("✓ Desktop file created")
    
    def create_metainfo(self):
        """Create metainfo file"""
        metainfo_content = f"""[AppImageKit]
Type=2
X-AppImageKit-Arch=x86_64
Name={self.app_name}
Version={self.version}
"""
        
        metainfo_file = self.app_dir / "metainfo"
        metainfo_file.write_text(metainfo_content)
        
        print("✓ Metainfo file created")
    
    def build_appimage(self):
        """Build AppImage using appimage-builder"""
        print(f"Building {self.appimage_name}...")
        
        cmd = [
            "appimage-builder",
            "--appimage",
            "--appdir-extract-and-keep",
            "--binary=",
            f"--directory={self.app_dir}",
            "--desktop-file=",
            str(self.app_dir / "usr" / "share" / "applications" / f"{self.app_name.lower()}.desktop"),
            "--icon=",
            str(self.app_dir / "usr" / "share" / "icons" / f"{self.app_name.lower()}.png") if Path(self.app_dir / "usr" / "share" / "icons" / f"{self.app_name.lower()}.png").exists() else "",
            "--version={self.version}",
            f"--create-desktop-file={self.app_image_name}"
        ]
        
        success = self.run_command(cmd)
        if success:
            print(f"✓ AppImage created: {self.appimage_name}")
            return True
        else:
            print("✗ Failed to create AppImage")
            return False
    
    def copy_sources(self):
        """Copy Python source files"""
        print("Copying source files...")
        
        # Copy main Python files
        python_files = [
            "main.py",
            "browser.py",
            "browser_pro.py", 
            "webnavigator_simple_stable.py",
            "webnavigator_allinone.py"
            "develer_browser_simple.py"
        ]
        
        for py_file in python_files:
            if Path(py_file).exists():
                shutil.copy2(py_file, self.app_dir / "usr" / "bin" / py_file)
                print(f"  ✓ Copied {py_file}")
        
        # Copy modules
        if Path("devtools").exists():
            shutil.copytree("devtools", self.app_dir / "usr" / "bin" / "devtools")
            print("  ✓ Copied devtools module")
        
        if Path("error_page_handler").exists():
            shutil.copytree("error_page_handler", self.app_dir / "usr" / "bin" / "error_page_handler")
            print("  ✓ Copied error_page_handler module")
        
        if Path("local_server").exists():
            shutil.copytree("local_server", self.app_dir / "usr" / "bin" / "local_server")
            print("  ✓ Copied local_server module")
        
        # Copy resources
        resources = ["*.html", "browser-icon.png"]
        for resource in resources:
            for resource_file in glob.glob(resource):
                if resource_file.exists():
                    target_dir = self.app_dir / "usr" / "share"
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(resource_file, target_dir)
        
        if Path("error_pages").exists():
            shutil.copytree("error_pages", self.app_dir / "usr" / "share" / "error_pages")
            
        if Path("data").exists():
            shutil.copytree("data", self.app_dir / "usr" / "share" / "data")
            
        print("✓ Source files copied")
    
    def build_python_executable(self):
        """Build Python executable for Linux"""
        print("Building Python executable for Linux...")
        
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=DevelerBrowser",
            "--icon=browser-icon.png",
            f"--workpath={self.app_dir}/build",
            f"--distpath={self.app_dir}/dist",
            "--add-data=*.html:html",
            "--add-data=error_pages:error_pages",
            "--add-data=data:data",
            "--hidden-import=PyQt5.QtCore",
            "--hidden-import=PyQt5.QtGui",
            "--hidden-import=PyQt5.QtWidgets",
            "--hidden-import=PyQt5.QtWebEngineWidgets",
            "--hidden-import=browser",
            "--hidden-import=devtools",
            "--hidden-import=error_page_handler",
            "--hidden-import=local_server",
            "--exclude-module=tkinter",
            "--exclude-module=matplotlib",
            "--exclude-module=numpy",
            "--exclude-module=scipy",
            "--exclude-module=pandas",
            "--workpath=build_linux",
            "--distpath=dist_linux",
            "main.py"
        ]
        
        # Change to AppImage directory for build
        original_cwd = os.getcwd()
        os.chdir(self.app_dir)
        
        try:
            success = self.run_command(pyinstaller_cmd)
            if success:
                # Find the built executable
                dist_files = list(Path(self.app_dir / "dist").glob("DevelerBrowser"))
                if dist_files:
                    executable_path = dist_files[0]
                    # Move to usr/bin
                    shutil.move(str(executable_path), "usr/bin")
                    print(f"  ✓ Built executable: {executable_path}")
                    return True
                else:
                    print("✗ No executable found in dist directory")
                    return False
            else:
                print("✗ PyInstaller failed")
                return False
        finally:
            os.chdir(original_cwd)
    
    def create_launcher_script(self):
        """Create launcher script for AppImage"""
        launcher_script = f"""#!/bin/bash
# Develer Browser Launcher Script
export APPDIR="$(dirname "$0")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
exec "$APPDIR/usr/bin/DevelerBrowser" "$@"
"""
        
        launcher_file = self.app_dir / "AppRun"
        launcher_file.write_text(launcher_script)
        launcher_file.chmod(0o755)  # Make executable
        print("✓ Launcher script created")
    
    def clean_build(self):
        """Clean build artifacts"""
        for build_dir in [self.app_dir / "build", self.app_dir / "dist"]:
            if Path(build_dir).exists():
                shutil.rmtree(build_dir)
                print(f"  ✓ Cleaned {build_dir}")
    
    def update_build_files(self):
        """Update files in AppDir"""
        # Update AppRun script
        self.create_launcher_script()
        
        # Update desktop file paths
        desktop_file = self.app_dir / "usr" / "share" / "applications" / f"{self.app_name.lower()}.desktop"
        if desktop_file.exists():
            with open(desktop_file, 'r') as f:
                content = f.read()
                # Update Exec path
                content = content.replace(f"Exec={self.app_name}", f"Exec=AppRun")
            with open(desktop_file, 'w') as f:
                f.write(content)
            print("  ✓ Updated desktop file")
    
    def build_complete_appimage(self):
        """Finalize and move AppImage"""
        # Create final AppImage
        final_cmd = [
            "appimage-builder",
            "--appimage",
            "--appdir-extract-and-keep",
            "--no-appstream",
            "--directory=.",
            "--desktop-file=",
            str(self.app_dir / "usr" / "share" / "applications" / f"{self.app_name.lower()}.desktop"),
            "--icon=",
            str(self.app_dir / "usr" / "share" / "icons" / f"{self.app_name.lower()}.png") if (self.app_dir / "usr" / "share" / "icons" / f"{self.app_name.lower()}.png").exists() else "",
            "--version={self.version}",
            f"{self.app_image_name}"
        ]
        
        success = self.run_command(final_cmd)
        if success:
            # Move to parent directory
            if Path(self.app_image_name).exists():
                print(f"✓ AppImage created: {self.app_image_name}")
                size_mb = self.app_image_name.stat().st_size / (1024 * 1024)
                print(f"  Size: {size_mb:.1f} MB")
                return True
        else:
            print("✗ Failed to create AppImage")
            return False
    
    def build(self):
        """Main build process"""
        print("=" * 50)
        print(f"Building {self.app_name} AppImage")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("Cannot build without required dependencies")
            return False
        
        try:
            # Step 1: Create structure
            self.create_appimage_structure()
            
            # Step 2: Copy sources
            self.copy_sources()
            
            # Step 3: Create desktop and metainfo
            self.create_desktop_file()
            self.create_metainfo()
            
            # Step 4: Build Python executable
            if not self.build_python_executable():
                print("Failed to build executable")
                return False
            
            # Step 5: Create launcher
            self.create_launcher_script()
            
            # Step 6: Update files
            self.update_build_files()
            
            # Step 7: Clean build artifacts
            self.clean_build()
            
            # Step 8: Build final AppImage
            if not self.build_complete_appimage():
                print("Failed to create AppImage")
                return False
            
            print("\n" + "=" * 50)
            print(f"{self.app_name} AppImage build completed successfully!")
            print(f"File: {self.app_image_name}")
            print(f"Run with: ./{self.app_image_name}")
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"Build error: {e}")
            return False

def main():
    """Main entry point"""
    print("Develer Browser AppImage Builder")
    print("Creating Linux AppImage with full dependencies...")
    print("This will include all browser modules and resources")
    print()
    
    builder = AppImageBuilder()
    
    if builder.build():
        print("\nBuild successful! You can now run:")
        print(f"./{builder.app_image_name}")
        print("=" * 50)
    else:
        print("Build failed. Check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()