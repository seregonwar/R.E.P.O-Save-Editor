"""
Configurazione del logging per R.E.P.O Save Editor
"""

import logging
import os
from pathlib import Path
import sys

def setup_logging(level=logging.INFO):
    """
    Configura il sistema di logging.
    
    Args:
        level: Livello di logging (default: INFO)
    """
    # Crea una directory per i log se non esiste
    app_root = os.environ.get("REPO_SAVE_EDITOR_ROOT", Path(__file__).parent.parent.absolute())
    log_dir = Path(app_root) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configura il logger root
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Rimuovi tutti gli handler esistenti
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Crea un formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Aggiungi un handler per il file
    log_file = log_dir / "repo_save_editor.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Aggiungi un handler per la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Aggiungi gli handler al logger root
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 