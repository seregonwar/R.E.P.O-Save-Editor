#!/usr/bin/env python3
"""
R.E.P.O Save Editor - Applicazione principale
Autore: Seregon
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from ui.styles import apply_style
from core import language_manager
from utils.logging_config import setup_logging

def main():
    """Funzione principale per l'avvio dell'applicazione"""
    # Configura il logger
    setup_logging()
    
    # Configura la variabile d'ambiente per il percorso dell'applicazione
    os.environ["REPO_SAVE_EDITOR_ROOT"] = str(Path(__file__).parent.absolute())
    
    # Inizializza l'applicazione
    app = QApplication(sys.argv)
    app.setApplicationName("R.E.P.O Save Editor")
    app.setApplicationVersion("3.0.0")
    
    # Applica lo stile
    apply_style(app)
    
    # Imposta l'icona dell'applicazione
    icon_path = Path(__file__).parent / "assets" / "icons" / "reposaveeditor.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
  
    # Crea e mostra la finestra principale
    window = MainWindow()
    window.show()
    
    # Esegui il ciclo degli eventi
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 