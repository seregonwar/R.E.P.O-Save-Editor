"""Gestione dei salvataggi del gioco"""

import logging
from pathlib import Path
from typing import Dict, Optional
from .error_handler import SaveLoadError, DataError, EncryptionError
from .encryption import encrypt_data, decrypt_data

logger = logging.getLogger(__name__)

class SaveManager:
    """Gestisce il caricamento e il salvataggio dei dati del gioco"""
    
    def __init__(self):
        self.current_path: Optional[Path] = None
        self.original_data: Optional[Dict] = None
        self.current_data: Optional[Dict] = None
        
    def load_save(self, file_path: Path) -> Dict:
        """Carica un salvataggio dal file"""
        try:
            logger.info(f"Caricamento salvataggio da {file_path}")
            
            if not file_path.exists():
                raise SaveLoadError("File non trovato", f"Il file {file_path} non esiste")
                
            try:
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
            except IOError as e:
                raise SaveLoadError("Errore di lettura file", str(e))
                
            try:
                decrypted_data = decrypt_data(encrypted_data)
            except Exception as e:
                raise EncryptionError("Errore di decrittografia", str(e))
                
            if not isinstance(decrypted_data, dict):
                raise DataError("Dati non validi", "I dati decrittati non sono un dizionario")
                
            self.current_path = file_path
            self.original_data = decrypted_data.copy()
            self.current_data = decrypted_data
            
            logger.info("Salvataggio caricato con successo")
            print(f"Salvataggio caricato con successo da {file_path}")
            return self.current_data
            
        except Exception as e:
            logger.error(f"Errore durante il caricamento: {str(e)}")
            raise
            
    def save_save(self) -> None:
        """Salva i dati nel file corrente"""
        if not self.current_path:
            raise SaveLoadError("Nessun file selezionato", "Selezionare prima un file")
            
        self._save_to_file(self.current_path)
        
    def save_save_as(self, file_path: Path) -> None:
        """Salva i dati in un nuovo file"""
        self._save_to_file(file_path)
        self.current_path = file_path
        
    def _save_to_file(self, file_path: Path) -> None:
        """Salva i dati in un file"""
        try:
            logger.info(f"Salvataggio in {file_path}")
            print(f"Salvataggio in corso nel file: {file_path}")
            
            if not isinstance(self.current_data, dict):
                raise DataError("Dati non validi", "I dati da salvare non sono un dizionario")
                
            try:
                encrypted_data = encrypt_data(self.current_data)
            except Exception as e:
                raise EncryptionError("Errore di crittografia", str(e))
                
            try:
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
            except IOError as e:
                raise SaveLoadError("Errore di scrittura file", str(e))
                
            self.original_data = self.current_data.copy()
            logger.info("Salvataggio completato con successo")
            print("Salvataggio completato con successo. File ES3 creato e salvato.")
            
        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {str(e)}")
            raise
            
    def has_changes(self) -> bool:
        """Verifica se ci sono modifiche non salvate"""
        return self.current_data != self.original_data
        
    def get_data(self) -> Dict:
        """Restituisce i dati correnti"""
        if not self.current_data:
            raise DataError("Nessun dato caricato", "Caricare prima un salvataggio")
        return self.current_data
        
    def set_data(self, data: Dict) -> None:
        """Imposta i nuovi dati"""
        if not isinstance(data, dict):
            raise DataError("Dati non validi", "I dati devono essere un dizionario")
        self.current_data = data
        
    def reset_changes(self) -> None:
        """Annulla le modifiche non salvate"""
        if self.original_data:
            self.current_data = self.original_data.copy()
            
    def get_current_path(self) -> Optional[Path]:
        """Restituisce il percorso del file corrente"""
        return self.current_path 