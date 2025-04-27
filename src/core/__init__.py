"""
Funzionalità core per R.E.P.O Save Editor
"""

from core.language import LanguageManager, tr
from core.error_handler import handle_error, REPOError, SaveLoadError, DataError, EncryptionError
from core.backup import BackupManager

# Istanze globali
language_manager = LanguageManager()


backup_manager = BackupManager()

__all__ = [
    'language_manager', 'tr', 'backup_manager',
    'handle_error', 'REPOError', 'SaveLoadError', 
    'DataError', 'EncryptionError'
] 