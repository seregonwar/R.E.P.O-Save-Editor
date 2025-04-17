#!/usr/bin/env python3
"""
Main entry point for R.E.P.O Save Editor
This script properly configures paths and starts the application
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for the application"""
    # Add the project root directory to PYTHONPATH
    root_dir = Path(__file__).parent
    sys.path.append(str(root_dir))
    
    # Ensure assets directory is properly accessible
    os.environ["REPO_SAVE_EDITOR_ROOT"] = str(root_dir)
    
    # Print some debug info
    print(f"R.E.P.O Save Editor starting from: {root_dir}")
    print(f"Python version: {sys.version}")

if __name__ == "__main__":
    setup_environment()
    
    # Import modules after environment setup
    try:
        from src.ui.main_window import main
        main()
    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("Please ensure you have installed all required dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)