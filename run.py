#!/usr/bin/env python3
"""
Run script for R.E.P.O Save Editor
This script properly configures paths and starts the application
"""

import sys
import os
import logging
from pathlib import Path

def setup_environment():
    """Set up the environment for the application"""
    # Add the project root directory to PYTHONPATH
    root_dir = Path(__file__).parent.absolute()
    sys.path.append(str(root_dir))
    
    # Ensure assets directory is properly accessible
    os.environ["REPO_SAVE_EDITOR_ROOT"] = str(root_dir)
    
    # Ensure the assets/icons directory exists
    os.makedirs(root_dir / "assets" / "icons", exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        filename=root_dir / "repo_editor.log",
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f"R.E.P.O Save Editor starting from: {root_dir}")
    logging.info(f"Python version: {sys.version}")
    
    return root_dir

if __name__ == "__main__":
    root_dir = setup_environment()
    
    # Import modules after environment setup
    try:
        from src.ui.main_window import main
        main()
    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("Ensure all required dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        logging.exception("Error starting application")
        sys.exit(1) 