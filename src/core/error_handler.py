"""Gestione degli errori personalizzati"""

import logging
import traceback
from typing import Optional, Type, Union
from PyQt6.QtWidgets import QMessageBox

# Configurazione del logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='repo_editor.log',
    filemode='a'
)

logger = logging.getLogger('REPOEditor')

class REPOError(Exception):
    """Eccezione base per tutti gli errori dell'applicazione"""
    
    def __init__(self, message: str, details: str = ""):
        self.message = message
        self.details = details
        super().__init__(f"{message}: {details}" if details else message)

class SaveLoadError(REPOError):
    """Errore durante il caricamento/salvataggio"""
    pass

class DataError(REPOError):
    """Errore nei dati del salvataggio"""
    pass

class EncryptionError(REPOError):
    """Errore durante la crittografia/decrittografia"""
    pass

def handle_error(
    error: Union[Exception, Type[REPOError]],
    parent=None,
    show_message: bool = True,
    log_error: bool = True
) -> None:
    """
    Gestisce un errore mostrando un messaggio all'utente e loggando i dettagli
    
    Args:
        error: L'errore da gestire
        parent: Widget padre per il messaggio
        show_message: Se mostrare il messaggio all'utente
        log_error: Se loggare l'errore
    """
    if log_error:
        if isinstance(error, REPOError):
            logger.error(f"{error.message}\n{error.details if error.details else ''}")
        else:
            logger.error(f"Errore non gestito: {str(error)}\n{traceback.format_exc()}")
    
    if show_message:
        if isinstance(error, REPOError):
            message = error.message
            details = error.details
        else:
            message = "Si è verificato un errore imprevisto"
            details = str(error)
            
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Errore")
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
            
        msg_box.exec() 