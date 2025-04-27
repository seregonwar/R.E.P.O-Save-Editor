"""
Classe per la gestione delle traduzioni
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import locale
import sys

class LanguageManager:
    """Gestisce le traduzioni dell'applicazione"""
    
    def __init__(self):
        self.languages = {}  # Dizionario delle lingue disponibili
        self.current_language = "en-US"  # Lingua predefinita
        self.translations = {}  # Traduzioni correnti
        self.observers = []  # Lista di osservatori per il cambio lingua
        self.load_languages()
        
    def load_languages(self):
        """Carica tutte le lingue disponibili dalla cartella languages"""
        try:
            # Trova il percorso della cartella languages usando diversi metodi
            languages_dir = None
            
            # 1. Controlla la variabile d'ambiente
            if "REPO_SAVE_EDITOR_ROOT" in os.environ:
                root_dir = Path(os.environ["REPO_SAVE_EDITOR_ROOT"])
                languages_dir = root_dir / "languages"
                print(f"DEBUG - Cercando lingue da variabile d'ambiente: {languages_dir}")
            
            # 2. Se siamo in un ambiente PyInstaller
            if not languages_dir or not languages_dir.exists():
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    # Siamo in un eseguibile PyInstaller
                    languages_dir = Path(sys._MEIPASS) / "languages"
                    print(f"DEBUG - Cercando lingue in PyInstaller: {languages_dir}")
            
            # 3. Percorso relativo alla directory del modulo corrente
            if not languages_dir or not languages_dir.exists():
                root_dir = Path(__file__).parent.parent
                languages_dir = root_dir / "languages"
                print(f"DEBUG - Cercando lingue in percorso relativo: {languages_dir}")
            
            # 4. Percorso assoluto basato sulla directory corrente
            if not languages_dir or not languages_dir.exists():
                languages_dir = Path(os.getcwd()) / "languages"
                print(f"DEBUG - Cercando lingue in percorso assoluto: {languages_dir}")
            
            print(f"DEBUG - Percorso finale per le lingue: {languages_dir}")
            
            # Verifica se la cartella esiste
            if not languages_dir.exists():
                print(f"Cartella delle lingue non trovata: {languages_dir}")
                # Crea la cartella se non esiste
                languages_dir.mkdir(parents=True, exist_ok=True)
                
                # Crea la lingua inglese di default
                self.create_default_language()
                return
                
            try:
                # Lista tutti i file nella cartella
                print(f"DEBUG - File nella cartella: {list(languages_dir.glob('*.json'))}")
            except Exception as e:
                print(f"DEBUG - Errore nella listazione dei file: {e}")
                
            # Carica tutti i file JSON nella cartella
            json_files = list(languages_dir.glob("*.json"))
            print(f"DEBUG - Trovati {len(json_files)} file JSON")
            
            for file_path in json_files:
                try:
                    print(f"DEBUG - Caricamento file lingua: {file_path}")
                    with open(file_path, "r", encoding="utf-8") as f:
                        lang_data = json.load(f)
                        
                    # Estrai il codice della lingua dal nome del file
                    lang_code = file_path.stem
                    
                    # Memorizza le informazioni sulla lingua
                    self.languages[lang_code] = {
                        "name": lang_data.get("language", lang_code),
                        "code": lang_code,
                        "author": lang_data.get("author", "Unknown"),
                        "version": lang_data.get("version", "1.0.0"),
                        "translations": lang_data.get("translations", {})
                    }
                    
                    print(f"Lingua caricata: {lang_code} - {self.languages[lang_code]['name']}")
                    
                except Exception as e:
                    print(f"Errore durante il caricamento del file lingua {file_path.name}: {str(e)}")
                    
            # Se non ci sono lingue, crea la lingua predefinita
            if not self.languages:
                print("DEBUG - Nessuna lingua trovata, creo la lingua predefinita")
                self.create_default_language()
                
            # Prova a impostare la lingua del sistema
            try:
                system_locale = locale.getlocale()[0]
                if system_locale:
                    # Converte il formato locale (es. it_IT) in formato lingua (es. it-IT)
                    system_lang = system_locale.replace('_', '-')
                    print(f"DEBUG - Lingua di sistema rilevata: {system_lang}")
                    
                    # Verifica se esiste una lingua corrispondente
                    if system_lang in self.languages:
                        self.current_language = system_lang
                        print(f"DEBUG - Lingua di sistema trovata: {system_lang}")
                    else:
                        # Prova a trovare una corrispondenza parziale (solo la prima parte)
                        lang_prefix = system_lang.split('-')[0]
                        for lang_code in self.languages.keys():
                            if lang_code.startswith(lang_prefix):
                                self.current_language = lang_code
                                print(f"DEBUG - Trovata corrispondenza parziale: {lang_code}")
                                break
            except Exception as e:
                print(f"DEBUG - Errore nel rilevamento della lingua di sistema: {e}")
                
            # Elenco tutte le lingue disponibili
            print(f"DEBUG - Lingue disponibili: {', '.join(self.languages.keys())}")
                
            # Carica la lingua predefinita
            self.set_language(self.current_language)
            
        except Exception as e:
            print(f"Errore durante il caricamento delle lingue: {str(e)}")
            # Crea la lingua predefinita in caso di errore
            self.create_default_language()
            
    def create_default_language(self):
        """Crea il file della lingua predefinita (inglese)"""
        try:
            # Trova il percorso della cartella languages usando diversi metodi
            languages_dir = None
            
            # 1. Controlla la variabile d'ambiente
            if "REPO_SAVE_EDITOR_ROOT" in os.environ:
                root_dir = Path(os.environ["REPO_SAVE_EDITOR_ROOT"])
                languages_dir = root_dir / "languages"
            
            # 2. Se siamo in un ambiente PyInstaller
            if not languages_dir or not languages_dir.exists():
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    # Siamo in un eseguibile PyInstaller
                    languages_dir = Path(sys._MEIPASS) / "languages"
            
            # 3. Percorso relativo alla directory del modulo corrente
            if not languages_dir or not languages_dir.exists():
                root_dir = Path(__file__).parent.parent
                languages_dir = root_dir / "languages"
            
            # 4. Percorso assoluto basato sulla directory corrente
            if not languages_dir or not languages_dir.exists():
                languages_dir = Path(os.getcwd()) / "languages"
            
            # Crea la cartella se non esiste
            languages_dir.mkdir(parents=True, exist_ok=True)
            
            # Crea il file della lingua inglese
            default_lang = {
                "language": "English",
                "code": "en-US",
                "author": "R.E.P.O Save Editor Team",
                "version": "1.0.0",
                "translations": {
                    "general": {
                        "app_title": "R.E.P.O Save Editor",
                        "save": "Save",
                        "cancel": "Cancel",
                        "ok": "OK",
                        "error": "Error",
                        "warning": "Warning",
                        "info": "Information",
                        "success": "Success",
                        "loading": "Loading...",
                        "processing": "Processing...",
                        "ready": "Ready",
                        "exit": "Exit"
                    },
                    "main_window": {
                        "player_tab": "Player",
                        "inventory_tab": "Inventory",
                        "advanced_tab": "Advanced",
                        "settings_tab": "Settings",
                        "file_menu": "File",
                        "edit_menu": "Edit",
                        "help_menu": "Help",
                        "open_action": "Open",
                        "save_action": "Save"
                    }
                }
            }
            
            # Salva il file
            file_path = languages_dir / "en-US.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default_lang, f, indent=4)
                
            # Memorizza la lingua
            self.languages["en-US"] = {
                "name": "English",
                "code": "en-US",
                "author": "R.E.P.O Save Editor Team",
                "version": "1.0.0",
                "translations": default_lang["translations"]
            }
            
            print("Creato file lingua predefinito: en-US.json")
            
        except Exception as e:
            print(f"Errore durante la creazione della lingua predefinita: {str(e)}")
            
    def set_language(self, lang_code: str) -> bool:
        """
        Imposta la lingua corrente
        
        Args:
            lang_code: Codice della lingua da impostare
            
        Returns:
            True se la lingua è stata impostata con successo, False altrimenti
        """
        # Se la lingua richiesta non esiste, usa la lingua predefinita
        if lang_code not in self.languages:
            print(f"Lingua {lang_code} non trovata, uso la lingua predefinita")
            lang_code = "en-US"
            
            # Se anche la lingua predefinita non esiste, crea il file
            if lang_code not in self.languages:
                self.create_default_language()
                
        # Imposta la lingua corrente
        self.current_language = lang_code
        self.translations = self.languages[lang_code]["translations"]
        
        print(f"Lingua impostata: {lang_code} - {self.languages[lang_code]['name']}")
        
        # Notifica gli osservatori del cambio lingua
        try:
            self.notify_observers()
        except Exception as e:
            print(f"Errore durante la notifica degli osservatori del cambio lingua: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    def get_translation(self, key: str, default: str = None) -> str:
        """
        Ottiene una traduzione dalla lingua corrente
        
        Args:
            key: Chiave della traduzione nel formato "sezione.chiave"
            default: Valore predefinito da restituire se la traduzione non esiste
            
        Returns:
            La traduzione o il valore predefinito se non trovata
        """
        try:
            # Dividi la chiave in sezione e chiave
            parts = key.split(".")
            
            # Se la chiave non ha il formato corretto, restituisci il valore predefinito
            if len(parts) < 2:
                return default if default is not None else key
                
            # Estrai la sezione e la chiave
            section = parts[0]
            subkey = ".".join(parts[1:])
            
            # Cerca la traduzione nella sezione
            if section in self.translations:
                # Se la chiave contiene ulteriori punti, naviga nella struttura
                current = self.translations[section]
                for part in parts[1:-1]:
                    if part in current:
                        current = current[part]
                    else:
                        return default if default is not None else key
                        
                # Ottieni la traduzione finale
                final_key = parts[-1]
                if final_key in current:
                    return current[final_key]
                    
            # Se la traduzione non è stata trovata, restituisci il valore predefinito
            return default if default is not None else key
            
        except Exception as e:
            print(f"Errore durante l'ottenimento della traduzione per {key}: {str(e)}")
            return default if default is not None else key
            
    def get_available_languages(self) -> Dict[str, str]:
        """
        Ottiene un dizionario delle lingue disponibili
        
        Returns:
            Dizionario con codice lingua -> nome lingua
        """
        return {code: data["name"] for code, data in self.languages.items()}
        
    def get_language_info(self, lang_code: str) -> Dict[str, Any]:
        """
        Ottiene informazioni su una lingua specifica
        
        Args:
            lang_code: Codice della lingua
            
        Returns:
            Dizionario con informazioni sulla lingua
        """
        if lang_code in self.languages:
            return {
                "name": self.languages[lang_code]["name"],
                "code": lang_code,
                "author": self.languages[lang_code]["author"],
                "version": self.languages[lang_code]["version"]
            }
        return None
        
    def reload_languages(self):
        """Ricarica tutte le lingue dalla cartella languages"""
        self.languages = {}
        self.load_languages()
        
    def get_current_language(self) -> str:
        """
        Ottiene il codice della lingua corrente
        
        Returns:
            Codice della lingua corrente
        """
        return self.current_language
        
    def get_current_language_name(self) -> str:
        """
        Ottiene il nome della lingua corrente
        
        Returns:
            Nome della lingua corrente
        """
        if self.current_language in self.languages:
            return self.languages[self.current_language]["name"]
        return "Unknown"
        
    def add_observer(self, observer):
        """
        Aggiunge un osservatore per il cambio lingua
        
        Args:
            observer: Funzione da chiamare quando la lingua cambia
        """
        if observer not in self.observers:
            self.observers.append(observer)
            
    def remove_observer(self, observer):
        """
        Rimuove un osservatore
        
        Args:
            observer: Osservatore da rimuovere
        """
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observers(self):
        """Notifica tutti gli osservatori del cambio lingua"""
        print(f"Notifica cambio lingua a {len(self.observers)} osservatori...")
        
        for idx, observer in enumerate(self.observers):
            try:
                # Verifica se l'osservatore ha un metodo update_language
                if hasattr(observer, 'update_language'):
                    print(f"[{idx+1}/{len(self.observers)}] Chiamata update_language() per {observer.__class__.__name__}")
                    observer.update_language()
                elif callable(observer):
                    # Mantiene la compatibilità con funzioni osservatori
                    print(f"[{idx+1}/{len(self.observers)}] Chiamata diretta per {observer.__name__}")
                    observer()
                else:
                    print(f"Warning: L'osservatore [{idx+1}/{len(self.observers)}] {observer} non è chiamabile e non ha un metodo update_language")
            except Exception as e:
                print(f"Errore durante la notifica dell'osservatore [{idx+1}/{len(self.observers)}]: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("Notifica cambio lingua completata")

# Istanza globale del gestore delle lingue
language_manager = LanguageManager()

# Funzione di utilità per ottenere una traduzione
def tr(key: str, default: str = None) -> str:
    """
    Ottiene una traduzione dalla lingua corrente
    
    Args:
        key: Chiave della traduzione nel formato "sezione.chiave"
        default: Valore predefinito da restituire se la traduzione non esiste
        
    Returns:
        La traduzione o il valore predefinito se non trovata
    """
    return language_manager.get_translation(key, default)
