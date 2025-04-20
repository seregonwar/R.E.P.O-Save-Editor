"""
Classe per la gestione delle traduzioni
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import locale

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
            # Trova il percorso della cartella languages
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            languages_dir = os.path.join(root_dir, "languages")
            
            # Verifica se la cartella esiste
            if not os.path.exists(languages_dir):
                print(f"Cartella delle lingue non trovata: {languages_dir}")
                # Crea la cartella se non esiste
                os.makedirs(languages_dir, exist_ok=True)
                return
                
            # Carica tutti i file JSON nella cartella
            for file_name in os.listdir(languages_dir):
                if file_name.endswith(".json"):
                    try:
                        file_path = os.path.join(languages_dir, file_name)
                        with open(file_path, "r", encoding="utf-8") as f:
                            lang_data = json.load(f)
                            
                        # Estrai il codice della lingua dal nome del file
                        lang_code = os.path.splitext(file_name)[0]
                        
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
                        print(f"Errore durante il caricamento del file lingua {file_name}: {str(e)}")
                        
            # Se non ci sono lingue, crea la lingua predefinita
            if not self.languages:
                self.create_default_language()
                
            # Prova a impostare la lingua del sistema
            try:
                system_locale = locale.getlocale()[0]
                if system_locale:
                    # Converte il formato locale (es. it_IT) in formato lingua (es. it-IT)
                    system_lang = system_locale.replace('_', '-')
                    
                    # Verifica se esiste una lingua corrispondente
                    if system_lang in self.languages:
                        self.current_language = system_lang
                    else:
                        # Prova a trovare una corrispondenza parziale (solo la prima parte)
                        lang_prefix = system_lang.split('-')[0]
                        for lang_code in self.languages.keys():
                            if lang_code.startswith(lang_prefix):
                                self.current_language = lang_code
                                break
            except:
                pass
                
            # Carica la lingua predefinita
            self.set_language(self.current_language)
            
        except Exception as e:
            print(f"Errore durante il caricamento delle lingue: {str(e)}")
            # Crea la lingua predefinita in caso di errore
            self.create_default_language()
            
    def create_default_language(self):
        """Crea il file della lingua predefinita (inglese)"""
        try:
            # Trova il percorso della cartella languages
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            languages_dir = os.path.join(root_dir, "languages")
            
            # Crea la cartella se non esiste
            os.makedirs(languages_dir, exist_ok=True)
            
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
                        "ready": "Ready"
                    }
                }
            }
            
            # Salva il file
            file_path = os.path.join(languages_dir, "en-US.json")
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
        self.notify_observers()
        
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
        for observer in self.observers:
            try:
                observer()
            except Exception as e:
                print(f"Errore durante la notifica dell'osservatore: {str(e)}")

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
