# Nexus Browser - Build Script

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_icon_placeholder():
    """Создает текстовый файл-заглушку для иконки"""
    icon_path = Path("installer/icon.ico")
    if not icon_path.exists():
        with open(icon_path, "w") as f:
            f.write("# Placeholder for icon.ico\n")
            f.write("# Replace with actual 256x256 icon file\n")
        print("Created icon placeholder")

def create_wizard_images():
    """Создает заглушки для изображений мастера установки"""
    images = {
        "installer/wizard_image.bmp": "# Placeholder for 164x314 wizard image",
        "installer/wizard_small.bmp": "# Placeholder for 55x58 wizard small image",
        "installer/banner.bmp": "# Placeholder for 57x28 banner image"
    }
    
    for img_path, content in images.items():
        path = Path(img_path)
        if not path.exists():
            with open(path, "w") as f:
                f.write(content + "\n")
            print(f"Created {img_path} placeholder")

def create_executable_stub():
    """Создает заглушку для исполняемого файла"""
    exe_path = Path("installer/nexus_browser.exe")
    if not exe_path.exists():
        with open(exe_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# Nexus Browser executable stub\n")
            f.write("# This will be replaced by pyinstaller or similar tool\n")
            f.write("import sys\n")
            f.write("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n")
            f.write("from main import main\n")
            f.write("if __name__ == '__main__':\n")
            f.write("    main()\n")
        print("Created executable stub")

def prepare_installer_files():
    """Подготавливает все файлы для установщика"""
    print("Preparing installer files...")
    
    # Создаем директории
    os.makedirs("installer/output", exist_ok=True)
    
    # Создаем заглушки для изображений
    create_icon_placeholder()
    create_wizard_images()
    create_executable_stub()
    
    print("Installer files prepared successfully!")

def build_installer():
    """Собирает установщик с помощью Inno Setup"""
    print("Building installer...")
    
    try:
        # Проверяем наличие Inno Setup
        result = subprocess.run(['where', 'iscc'], capture_output=True, text=True)
        if result.returncode != 0:
            print("ERROR: Inno Setup not found!")
            print("Please install Inno Setup 6.x from: https://jrsoftware.org/isdl.php")
            return False
            
        # Собираем установщик
        result = subprocess.run(['iscc', 'installer/nexus_browser.iss'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS! Installer created:")
            print("installer/output/nexus_browser_setup_1.0.0.exe")
            return True
        else:
            print("ERROR: Failed to build installer!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def create_portable_package():
    """Создает портативную версию браузера"""
    print("Creating portable package...")
    
    portable_dir = Path("installer/portable/Nexus Browser")
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Копируем основные файлы
    files_to_copy = [
        "main.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, portable_dir / file)
    
    # Копируем папку browser
    if Path("browser").exists():
        shutil.copytree("browser", portable_dir / "browser", dirs_exist_ok=True)
    
    # Создаем запускной файл
    start_script = portable_dir / "Start Nexus Browser.bat"
    with open(start_script, "w") as f:
        f.write("@echo off\n")
        f.write("echo Starting Nexus Browser...\n")
        f.write("python main.py\n")
        f.write("pause\n")
    
    # Создаем README для портативной версии
    portable_readme = portable_dir / "PORTABLE_README.txt"
    with open(portable_readme, "w") as f:
        f.write("Nexus Browser - Portable Version\n")
        f.write("==================================\n\n")
        f.write("This is a portable version of Nexus Browser.\n")
        f.write("No installation required.\n\n")
        f.write("Requirements:\n")
        f.write("- Python 3.8 or higher\n")
        f.write("- Internet connection\n\n")
        f.write("To start:\n")
        f.write("1. Install Python dependencies: python -m pip install -r requirements.txt\n")
        f.write("2. Run: python main.py\n")
        f.write("   Or double-click: 'Start Nexus Browser.bat'\n\n")
        f.write("All data is stored in the 'data' subdirectory.\n")
    
    print("Portable package created in: installer/portable/")

def main():
    """Главная функция сборки"""
    print("========================================")
    print("Nexus Browser Build System")
    print("========================================")
    print()
    
    # Подготавливаем файлы
    prepare_installer_files()
    
    # Создаем портативную версию
    create_portable_package()
    
    # Собираем установщик
    success = build_installer()
    
    if success:
        print()
        print("========================================")
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("========================================")
        print()
        print("Created files:")
        print("- installer/output/nexus_browser_setup_1.0.0.exe")
        print("- installer/portable/Nexus Browser/ (portable version)")
        print()
        print("To test the installer, run:")
        print("installer/output/nexus_browser_setup_1.0.0.exe")
    else:
        print()
        print("========================================")
        print("BUILD FAILED!")
        print("========================================")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()