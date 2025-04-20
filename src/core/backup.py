"""Classe per la gestione dei backup automatici"""

import os
import json
import shutil
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class BackupManager:
    """Gestisce i backup automatici dei salvataggi"""
    
    def __init__(self):
        self.settings = {}
        self.backup_thread = None
        self.stop_backup = threading.Event()
        self.load_settings()
        
    def load_settings(self):
        """Carica le impostazioni di backup dal file settings.json"""
        try:
            # Trova il percorso del file settings.json
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            settings_path = os.path.join(root_dir, "settings.json")
            
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    self.settings = json.load(f)
            else:
                # Impostazioni predefinite
                self.settings = {
                    "auto_backup": True,
                    "backup_path": os.path.join(root_dir, "backups"),
                    "backup_count": 5,
                    "backup_interval": 5  # minuti
                }
                
                # Salva le impostazioni predefinite
                with open(settings_path, "w") as f:
                    json.dump(self.settings, f, indent=4)
                
            # Assicurati che la cartella di backup esista
            if "backup_path" in self.settings:
                os.makedirs(self.settings["backup_path"], exist_ok=True)
                
        except Exception as e:
            print(f"Errore durante il caricamento delle impostazioni di backup: {str(e)}")
            # Impostazioni predefinite in caso di errore
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.settings = {
                "auto_backup": True,
                "backup_path": os.path.join(root_dir, "backups"),
                "backup_count": 5,
                "backup_interval": 5  # minuti
            }
            os.makedirs(self.settings["backup_path"], exist_ok=True)
            
    def create_backup(self, save_path: str) -> Optional[str]:
        """
        Crea un backup del file di salvataggio
        
        Args:
            save_path: Percorso del file di salvataggio
            
        Returns:
            Percorso del file di backup o None in caso di errore
        """
        try:
            # Verifica che il file esista
            if not os.path.exists(save_path):
                print(f"File di salvataggio non trovato: {save_path}")
                return None
                
            # Crea il nome del file di backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = os.path.basename(save_path)
            backup_name = f"{os.path.splitext(save_name)[0]}_{timestamp}{os.path.splitext(save_name)[1]}"
            backup_path = os.path.join(self.settings.get("backup_path", "backups"), backup_name)
            
            # Crea la cartella di backup se non esiste
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Copia il file
            shutil.copy2(save_path, backup_path)
            print(f"Backup creato: {backup_path}")
            
            # Elimina i backup più vecchi se necessario
            self.cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            print(f"Errore durante la creazione del backup: {str(e)}")
            return None
            
    def cleanup_old_backups(self):
        """Elimina i backup più vecchi in base al numero massimo da mantenere"""
        try:
            backup_path = self.settings.get("backup_path", "backups")
            max_backups = self.settings.get("backup_count", 5)
            
            # Ottieni tutti i file di backup
            backup_files = []
            for file in os.listdir(backup_path):
                file_path = os.path.join(backup_path, file)
                if os.path.isfile(file_path) and file.endswith(".es3"):
                    backup_files.append((file_path, os.path.getmtime(file_path)))
                    
            # Ordina per data di modifica (più recente prima)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Elimina i backup in eccesso
            if len(backup_files) > max_backups:
                for file_path, _ in backup_files[max_backups:]:
                    os.remove(file_path)
                    print(f"Backup eliminato: {file_path}")
                    
        except Exception as e:
            print(f"Errore durante la pulizia dei backup: {str(e)}")
            
    def start_auto_backup(self, save_path: str):
        """
        Avvia il thread di backup automatico
        
        Args:
            save_path: Percorso del file di salvataggio
        """
        # Ferma eventuali thread di backup in esecuzione
        self.stop_auto_backup()
        
        # Verifica che il backup automatico sia abilitato
        if not self.settings.get("auto_backup", True):
            print("Backup automatico disabilitato")
            return
            
        # Avvia il thread di backup
        self.stop_backup.clear()
        self.backup_thread = threading.Thread(
            target=self._auto_backup_thread,
            args=(save_path,),
            daemon=True
        )
        self.backup_thread.start()
        print(f"Thread di backup automatico avviato per: {save_path}")
        
    def _auto_backup_thread(self, save_path: str):
        """
        Thread di backup automatico
        
        Args:
            save_path: Percorso del file di salvataggio
        """
        try:
            interval_minutes = self.settings.get("backup_interval", 5)
            interval_seconds = interval_minutes * 60
            
            while not self.stop_backup.is_set():
                # Attendi l'intervallo specificato
                for _ in range(interval_seconds):
                    if self.stop_backup.is_set():
                        break
                    time.sleep(1)
                    
                # Crea il backup
                if not self.stop_backup.is_set():
                    self.create_backup(save_path)
                    
        except Exception as e:
            print(f"Errore nel thread di backup automatico: {str(e)}")
            
    def stop_auto_backup(self):
        """Ferma il thread di backup automatico"""
        if self.backup_thread and self.backup_thread.is_alive():
            self.stop_backup.set()
            self.backup_thread.join(timeout=2)
            print("Thread di backup automatico fermato")
            
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """
        Ottiene la lista dei backup disponibili
        
        Returns:
            Lista di dizionari con informazioni sui backup
        """
        try:
            backup_path = self.settings.get("backup_path", "backups")
            
            # Ottieni tutti i file di backup
            backup_files = []
            for file in os.listdir(backup_path):
                file_path = os.path.join(backup_path, file)
                if os.path.isfile(file_path) and file.endswith(".es3"):
                    # Estrai il timestamp dal nome del file
                    timestamp_str = file.split("_")[-1].split(".")[0]
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        formatted_date = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_date = "Unknown"
                        
                    backup_files.append({
                        "path": file_path,
                        "name": file,
                        "date": formatted_date,
                        "size": os.path.getsize(file_path)
                    })
                    
            # Ordina per data di modifica (più recente prima)
            backup_files.sort(key=lambda x: x["name"], reverse=True)
            
            return backup_files
            
        except Exception as e:
            print(f"Errore durante l'ottenimento della lista dei backup: {str(e)}")
            return []
            
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """
        Ripristina un backup
        
        Args:
            backup_path: Percorso del file di backup
            target_path: Percorso di destinazione
            
        Returns:
            True se il ripristino è avvenuto con successo, False altrimenti
        """
        try:
            # Verifica che il file di backup esista
            if not os.path.exists(backup_path):
                print(f"File di backup non trovato: {backup_path}")
                return False
                
            # Crea un backup del file corrente prima di sovrascriverlo
            if os.path.exists(target_path):
                self.create_backup(target_path)
                
            # Copia il file di backup
            shutil.copy2(backup_path, target_path)
            print(f"Backup ripristinato: {backup_path} -> {target_path}")
            
            return True
            
        except Exception as e:
            print(f"Errore durante il ripristino del backup: {str(e)}")
            return False
            
    def update_settings(self, settings: Dict[str, Any]):
        """
        Aggiorna le impostazioni di backup
        
        Args:
            settings: Nuove impostazioni
        """
        # Aggiorna solo le impostazioni relative al backup
        backup_settings = {
            "auto_backup": settings.get("auto_backup", self.settings.get("auto_backup", True)),
            "backup_path": settings.get("backup_path", self.settings.get("backup_path", "backups")),
            "backup_count": settings.get("backup_count", self.settings.get("backup_count", 5)),
            "backup_interval": settings.get("backup_interval", self.settings.get("backup_interval", 5))
        }
        
        self.settings.update(backup_settings)
        
        # Salva le impostazioni
        try:
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            settings_path = os.path.join(root_dir, "settings.json")
            
            with open(settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Errore durante il salvataggio delle impostazioni: {str(e)}")
        
        # Assicurati che la cartella di backup esista
        os.makedirs(self.settings["backup_path"], exist_ok=True)

# Istanza globale del gestore dei backup
backup_manager = BackupManager()
