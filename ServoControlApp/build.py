"""
Build script for compiling the application to EXE using PyInstaller
Run this script to create a standalone executable
"""

import subprocess
import sys
import os


def build_exe():
    """Build the executable using PyInstaller"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ServoControlApp",
        "--onefile",
        "--windowed",  # Use --console instead if you want console output
        "--icon", "NONE",  # Add path to .ico file if you have an icon
        "--add-data", "config.json;.",  # Include config file (use : instead of ; on Linux/Mac)
        "--hidden-import", "pymodbus.client",
        "--hidden-import", "pymodbus.exceptions",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtGui",
        "main.py"
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(f"Executable location: {os.path.join(script_dir, 'dist', 'ServoControlApp.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Build failed: {e}")
        return False


def build_with_console():
    """Build the executable with console window for debugging"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ServoControlApp_Debug",
        "--onefile",
        "--console",  # Show console window
        "--add-data", "config.json;.",
        "--hidden-import", "pymodbus.client",
        "--hidden-import", "pymodbus.exceptions",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtGui",
        "main.py"
    ]
    
    print("Building debug executable with console...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Debug build completed successfully!")
        print(f"Executable location: {os.path.join(script_dir, 'dist', 'ServoControlApp_Debug.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stderr: {e.stderr}")
        return False


def build_config_editor():
    """Build the ConfigEditor executable"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # PyInstaller command for ConfigEditor
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "ConfigEditor",
        "--onefile",
        "--windowed",  # Use --console instead if you want console output
        "--icon", "NONE",  # Add path to .ico file if you have an icon
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.filedialog",
        "config_editor.py"
    ]
    
    print("Building ConfigEditor executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("ConfigEditor build completed successfully!")
        print(f"Executable location: {os.path.join(script_dir, 'dist', 'ConfigEditor.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Build failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Servo Control Application")
    parser.add_argument("--debug", action="store_true", help="Build with console for debugging")
    parser.add_argument("--config-editor", action="store_true", help="Build ConfigEditor executable")
    args = parser.parse_args()
    
    if args.config_editor:
        success = build_config_editor()
    elif args.debug:
        success = build_with_console()
    else:
        success = build_exe()
    
    sys.exit(0 if success else 1)
