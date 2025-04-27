"""
Configurazione del sistema di logging per l'applicazione
"""

import os
import logging
from datetime import datetime
from pathlib import Path

# Configurazione logger globale
logger = logging.getLogger("RepoSaveEditor")

def setup_logging(level=logging.INFO, log_to_file=True):
    """Configura il sistema di logging
    
    Args:
        level: Livello di logging
        log_to_file: Se True, salva i log su file
    """
    # Configura il logger principale
    logger.setLevel(level)
    
    # Formatter per i log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler per console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler per file
    if log_to_file:
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f"repo-save-editor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configura anche alcuni moduli standard
    logging.getLogger("PyQt6").setLevel(logging.WARNING)
    
    return logger 