#!/usr/bin/env python3
"""
R.E.P.O Save Editor - Script di avvio
"""

import os
import sys
import traceback
from pathlib import Path

# Imposta la directory principale come variabile d'ambiente
root_dir = os.path.dirname(os.path.abspath(__file__))
os.environ["REPO_SAVE_EDITOR_ROOT"] = root_dir

# Aggiungi la directory src al path
sys.path.append(os.path.join(root_dir, "src"))

# Crea le directory necessarie
os.makedirs(os.path.join(root_dir, "backups"), exist_ok=True)
os.makedirs(os.path.join(root_dir, "languages"), exist_ok=True)

try:
    from src.ui.main_window import main
    main()
except Exception as e:
    # Gestisci le eccezioni
    error_message = f"Si è verificato un errore durante l'avvio dell'applicazione:\n{str(e)}\n\n{traceback.format_exc()}"
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Errore", error_message)
    except:
        print(error_message)
    sys.exit(1)
