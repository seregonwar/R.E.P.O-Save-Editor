#!/usr/bin/env python3
"""
Build script for R.E.P.O Save Editor using PyInstaller
This script will create an executable with the proper icon and settings
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Ensure PyInstaller is installed
try:
    import PyInstaller
except ImportError:
    print("PyInstaller is not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
# Configuration
APP_NAME = "REPO Save Editor"
APP_VERSION = "1.1.0"
MAIN_SCRIPT = "src/main.py"
ICON_PATH = "src/assets/icons/reposaveeditor.png"

# PyInstaller options
PYINSTALLER_ARGS = [
    "--name={}".format(APP_NAME),
    "--onefile",  # Create a single executable
    "--windowed",  # Don't open a console window
    "--icon={}".format(ICON_PATH),
    "--add-data={}{}{}".format(ICON_PATH, os.pathsep, "assets/icons"),  # Add icon as data file
    "--add-data={}{}{}".format("assets", os.pathsep, "assets"),  # Include assets folder
    "--clean",  # Clean PyInstaller cache
    "--noconfirm",  # Replace output directory without confirmation
    "--hidden-import=PIL._tkinter_finder",  # Fix potential PIL import issues
    MAIN_SCRIPT
]

def build_app():
    """Build the application using PyInstaller"""
    # Ensure assets and icons directories exist
    os.makedirs("assets/icons", exist_ok=True)
    
    # Ensure icon exists
    if not os.path.exists(ICON_PATH):
        print(f"Warning: Icon '{ICON_PATH}' not found! The application will run without an icon.")
    
    # Create the command line
    cmd = [sys.executable, "-m", "PyInstaller"] + PYINSTALLER_ARGS
    
    # Run PyInstaller
    print("Building application...")
    subprocess.run(cmd, check=True)
    
    # Copy additional files to dist folder
    print("Copying additional files...")
    dist_dir = Path("dist")
    
    # Create README.txt in dist folder
    with open(dist_dir / "README.txt", "w") as readme:
        readme.write(f"{APP_NAME} v{APP_VERSION}\n\n")
        readme.write("Created by SeregonWar\n\n")
        readme.write("Support the developer:\n")
        readme.write("- Ko-Fi: https://ko-fi.com/seregon\n")
        readme.write("- PayPal: https://paypal.me/seregonwar\n")
        readme.write("- Twitter: https://x.com/SeregonWar\n")

    with open(dist_dir / "CHANGELOG.txt", "w") as readme:
        readme.write(f"{APP_NAME} v{APP_VERSION}\n\n")
        readme.write("Created by SeregonWar\n\n")
        readme.write("Support the developer:\n")
        readme.write("- Ko-Fi: https://ko-fi.com/seregon\n")
        readme.write("- PayPal: https://paypal.me/seregonwar\n")
        readme.write("- Twitter: https://x.com/SeregonWar\n")
    
    print(f"Build complete! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build_app() 