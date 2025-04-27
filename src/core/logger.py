"""
Modulo di logging per l'applicazione
"""

import logging
from core.logging_config import logger as app_logger

# Esporta il logger configurato
logger = app_logger

# Per facilitare l'utilizzo
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical

def get_logger(name):
    """Ottiene un logger figlio con il nome specificato
    
    Args:
        name: Nome del logger
        
    Returns:
        Logger: Logger figlio
    """
    return logging.getLogger(f"RepoSaveEditor.{name}") 